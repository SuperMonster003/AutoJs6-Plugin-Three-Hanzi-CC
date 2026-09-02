package io.github.supermonster003.autojs6.plugin.opencc

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.content.pm.ActivityInfo
import android.content.pm.PackageManager
import android.os.IBinder
import android.os.Parcel
import android.os.Parcelable
import android.os.SystemClock
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccConversionType
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccUpstream
import org.autojs.plugin.common.api.PluginInfo
import org.autojs.plugin.opencc.api.IOpenccPlugin
import org.autojs.plugin.opencc.api.OpenccConversionTypes
import org.autojs.plugin.opencc.api.OpenccPluginActions
import org.autojs.plugin.opencc.api.OpenccPluginIds
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertSame
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

@RunWith(AndroidJUnit4::class)
class OpenccDualEntryTest {

    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val context = instrumentation.targetContext

    @Test
    fun launcherAndBinderUseTheSameOfficialBackend() {
        assertManifestBoundaries()

        val launcherIntent = Intent(Intent.ACTION_MAIN)
            .addCategory(Intent.CATEGORY_LAUNCHER)
            .setPackage(context.packageName)
            .setComponent(ComponentName(context, OpenccActivity::class.java))
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
        val activity = instrumentation.startActivitySync(launcherIntent) as OpenccActivity
        try {
            assertSame(
                "Launcher and service-facing calls must resolve one process coordinator",
                OpenccConversionCoordinator.get(context),
                OpenccConversionCoordinator.get(activity),
            )

            val input = activity.findViewById<EditText>(R.id.source_text)
            val types = activity.findViewById<Spinner>(R.id.conversion_type)
            val convert = activity.findViewById<Button>(R.id.convert_button)
            val result = activity.findViewById<TextView>(R.id.result_text)
            val runtimeIdentity = activity.findViewById<TextView>(R.id.runtime_identity)

            instrumentation.runOnMainSync {
                input.setText(SMOKE_INPUT)
                types.setSelection(OpenccConversionType.values().indexOf(OpenccConversionType.S2T))
                convert.performClick()
            }
            awaitText(result, SMOKE_OUTPUT)

            val uiIdentity = readText(runtimeIdentity)
            assertTrue(uiIdentity.contains(OpenccUpstream.version()))
            assertTrue(uiIdentity.contains(OpenccUpstream.commit().take(12)))
            assertTrue(uiIdentity.contains(OpenccUpstream.resourceSha256().take(12)))

            withBoundPlugin { plugin, rawBinder ->
                assertLegacyV1Transactions(rawBinder)
                assertEquals(SMOKE_OUTPUT, plugin.convert(SMOKE_INPUT, OpenccConversionTypes.S2T))
                val capabilities = requireNotNull(plugin.info.capabilities)
                assertEquals(
                    OpenccUpstream.version(),
                    capabilities.getString(OpenccEngineCapabilityKeys.VERSION),
                )
                assertEquals(
                    OpenccUpstream.commit(),
                    capabilities.getString(OpenccEngineCapabilityKeys.COMMIT),
                )
                assertEquals(
                    OpenccUpstream.resourceSha256(),
                    capabilities.getString(OpenccEngineCapabilityKeys.RESOURCE_SHA256),
                )
            }
        } finally {
            instrumentation.runOnMainSync { activity.finish() }
            instrumentation.waitForIdleSync()
        }
    }

    @Suppress("DEPRECATION")
    private fun assertManifestBoundaries() {
        val packageManager = context.packageManager
        val packageInfo = packageManager.getPackageInfo(
            context.packageName,
            PackageManager.GET_ACTIVITIES or
                PackageManager.GET_SERVICES or
                PackageManager.GET_RECEIVERS or
                PackageManager.GET_PROVIDERS or
                PackageManager.GET_PERMISSIONS,
        )
        assertEquals(
            "The final APK must request only the existing AutoJs6 plugin permission",
            setOf(PLUGIN_PERMISSION),
            packageInfo.requestedPermissions.orEmpty().toSet(),
        )
        assertEquals(
            "The final APK activity inventory changed",
            setOf(OpenccActivity::class.java.name, WakeActivity::class.java.name),
            packageInfo.activities.orEmpty().map { it.name }.toSet(),
        )
        assertEquals(
            "The final APK service inventory changed",
            setOf(OpenccPluginService::class.java.name),
            packageInfo.services.orEmpty().map { it.name }.toSet(),
        )
        assertTrue("The APK must not declare broadcast receivers", packageInfo.receivers.orEmpty().isEmpty())
        assertTrue("The APK must not declare content providers", packageInfo.providers.orEmpty().isEmpty())

        val launcherIntent = Intent(Intent.ACTION_MAIN)
            .addCategory(Intent.CATEGORY_LAUNCHER)
            .setPackage(context.packageName)
        val launcherMatches = packageManager.queryIntentActivities(launcherIntent, 0)
        assertEquals("The APK must expose exactly one desktop entry", 1, launcherMatches.size)
        val activityInfo = launcherMatches.single().activityInfo
        assertEquals(OpenccActivity::class.java.name, activityInfo.name)
        assertTrue("The Launcher activity must be exported", activityInfo.exported)
        assertNull("Desktop launch must not require the AutoJs6 plugin permission", activityInfo.permission)
        assertEquals("Launcher must use the ordinary app task affinity", context.packageName, activityInfo.taskAffinity)
        assertEquals("Launcher must retain the standard launch mode", ActivityInfo.LAUNCH_MULTIPLE, activityInfo.launchMode)
        assertEquals(
            "Launcher must not create document tasks",
            ActivityInfo.DOCUMENT_LAUNCH_NONE,
            activityInfo.documentLaunchMode,
        )
        val forbiddenLauncherFlags = ActivityInfo.FLAG_ALLOW_TASK_REPARENTING or
            ActivityInfo.FLAG_EXCLUDE_FROM_RECENTS or
            ActivityInfo.FLAG_FINISH_ON_TASK_LAUNCH or
            ActivityInfo.FLAG_NO_HISTORY
        assertEquals(
            "Launcher must remain in its ordinary visible task without reparenting",
            0,
            activityInfo.flags and forbiddenLauncherFlags,
        )

        val shareMatches = packageManager.queryIntentActivities(
            Intent(Intent.ACTION_SEND)
                .setType("text/plain")
                .addCategory(Intent.CATEGORY_DEFAULT)
                .setPackage(context.packageName),
            PackageManager.MATCH_DEFAULT_ONLY,
        )
        assertTrue("The standalone Activity must not receive implicit shared text", shareMatches.isEmpty())
        val viewMatches = packageManager.queryIntentActivities(
            Intent(Intent.ACTION_VIEW)
                .setData(android.net.Uri.parse("content://untrusted.example/document/1"))
                .addCategory(Intent.CATEGORY_DEFAULT)
                .setPackage(context.packageName),
            PackageManager.MATCH_DEFAULT_ONLY,
        )
        assertTrue("The standalone Activity must not receive external paths or URIs", viewMatches.isEmpty())

        val serviceInfo = packageManager.getServiceInfo(
            ComponentName(context, OpenccPluginService::class.java),
            0,
        )
        assertTrue("The plugin service must remain exported for AutoJs6", serviceInfo.exported)
        assertEquals(PLUGIN_PERMISSION, serviceInfo.permission)

        val wakeInfo = packageManager.getActivityInfo(
            ComponentName(context, WakeActivity::class.java),
            0,
        )
        assertTrue("The wake activity must remain exported for AutoJs6", wakeInfo.exported)
        assertEquals(PLUGIN_PERMISSION, wakeInfo.permission)
        val wakeMatches = packageManager.queryIntentActivities(
            Intent(WAKE_ACTION)
                .addCategory(Intent.CATEGORY_DEFAULT)
                .setPackage(context.packageName),
            0,
        )
        assertEquals("The wake protocol must resolve exactly one protected Activity", 1, wakeMatches.size)
        assertEquals(WakeActivity::class.java.name, wakeMatches.single().activityInfo.name)

        assertEquals(
            "Backups must remain disabled",
            0,
            packageInfo.applicationInfo!!.flags and android.content.pm.ApplicationInfo.FLAG_ALLOW_BACKUP,
        )
        assertEquals(
            "Cleartext traffic must remain disabled",
            0,
            packageInfo.applicationInfo!!.flags and android.content.pm.ApplicationInfo.FLAG_USES_CLEARTEXT_TRAFFIC,
        )
        assertFalse(
            "The standalone APK must remain offline",
            packageManager.checkPermission(android.Manifest.permission.INTERNET, context.packageName) ==
                PackageManager.PERMISSION_GRANTED,
        )
    }

    private fun assertLegacyV1Transactions(rawBinder: IBinder) {
        assertEquals(IOpenccPlugin.DESCRIPTOR, rawBinder.interfaceDescriptor)

        val infoData = Parcel.obtain()
        val infoReply = Parcel.obtain()
        try {
            infoData.writeInterfaceToken(IOpenccPlugin.DESCRIPTOR)
            assertTrue(
                "Legacy getInfo transaction 1 was not handled",
                rawBinder.transact(LEGACY_GET_INFO_TRANSACTION, infoData, infoReply, 0),
            )
            infoReply.readException()
            @Suppress("UNCHECKED_CAST")
            val creator = PluginInfo::class.java.getField("CREATOR").get(null) as Parcelable.Creator<PluginInfo>
            val info = if (infoReply.readInt() != 0) {
                creator.createFromParcel(infoReply)
            } else {
                null
            }
            assertNotNull("Legacy getInfo transaction returned null", info)
            assertEquals(OpenccPluginIds.ID, info?.id)
            assertEquals(OpenccPluginIds.VARIANT_DEFAULT, info?.variant)
        } finally {
            infoReply.recycle()
            infoData.recycle()
        }

        val convertData = Parcel.obtain()
        val convertReply = Parcel.obtain()
        try {
            convertData.writeInterfaceToken(IOpenccPlugin.DESCRIPTOR)
            convertData.writeString(SMOKE_INPUT)
            convertData.writeString(OpenccConversionTypes.S2T)
            assertTrue(
                "Legacy convert transaction 2 was not handled",
                rawBinder.transact(LEGACY_CONVERT_TRANSACTION, convertData, convertReply, 0),
            )
            convertReply.readException()
            assertEquals(SMOKE_OUTPUT, convertReply.readString())
        } finally {
            convertReply.recycle()
            convertData.recycle()
        }
    }

    private fun awaitText(view: TextView, expected: String) {
        val deadline = SystemClock.elapsedRealtime() + CONVERSION_TIMEOUT_MILLIS
        var actual = ""
        while (SystemClock.elapsedRealtime() < deadline) {
            instrumentation.waitForIdleSync()
            actual = readText(view)
            if (actual == expected) return
            SystemClock.sleep(POLL_INTERVAL_MILLIS)
        }
        assertEquals("Timed out waiting for the Launcher conversion", expected, actual)
    }

    private fun readText(view: TextView): String {
        val value = AtomicReference<String>()
        instrumentation.runOnMainSync { value.set(view.text.toString()) }
        return value.get()
    }

    private fun withBoundPlugin(block: (IOpenccPlugin, IBinder) -> Unit) {
        val discoveryIntent = Intent(OpenccPluginActions.OPENCC)
            .addCategory(OpenccPluginIds.ID)
            .setPackage(context.packageName)
        @Suppress("DEPRECATION")
        val matches = context.packageManager.queryIntentServices(discoveryIntent, 0)
        assertEquals("OpenCC discovery must still resolve exactly one service", 1, matches.size)

        val serviceInfo = matches.single().serviceInfo
        val explicitIntent = Intent(discoveryIntent).setComponent(
            ComponentName(serviceInfo.packageName, serviceInfo.name),
        )
        val latch = CountDownLatch(1)
        val binder = AtomicReference<IBinder?>()
        val connection = object : ServiceConnection {
            override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
                binder.set(service)
                latch.countDown()
            }

            override fun onServiceDisconnected(name: ComponentName?) = Unit

            override fun onNullBinding(name: ComponentName?) = latch.countDown()

            override fun onBindingDied(name: ComponentName?) = latch.countDown()
        }

        assertTrue(
            "Unable to bind the discovered OpenCC service",
            context.bindService(explicitIntent, connection, Context.BIND_AUTO_CREATE),
        )
        try {
            assertTrue("Timed out binding the OpenCC service", latch.await(15, TimeUnit.SECONDS))
            val rawBinder = binder.get()
            assertNotNull("OpenCC service returned a null Binder", rawBinder)
            block(remoteOpenccPlugin(rawBinder!!), rawBinder)
        } finally {
            context.unbindService(connection)
        }
    }

    private companion object {
        const val PLUGIN_PERMISSION = "org.autojs.permission.PLUGIN"
        const val WAKE_ACTION = "org.autojs.plugin.action.WAKE"
        const val LEGACY_GET_INFO_TRANSACTION = 1
        const val LEGACY_CONVERT_TRANSACTION = 2
        const val SMOKE_INPUT = "汉字软件 😀 𠀀"
        const val SMOKE_OUTPUT = "漢字軟件 😀 𠀀"
        const val CONVERSION_TIMEOUT_MILLIS = 30_000L
        const val POLL_INTERVAL_MILLIS = 50L
    }
}
