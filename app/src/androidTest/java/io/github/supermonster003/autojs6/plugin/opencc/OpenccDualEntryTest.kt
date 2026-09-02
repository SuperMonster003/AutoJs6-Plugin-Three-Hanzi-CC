package io.github.supermonster003.autojs6.plugin.opencc

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.content.pm.PackageManager
import android.os.IBinder
import android.os.SystemClock
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccConversionType
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccUpstream
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

            withBoundPlugin { plugin ->
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
        val launcherIntent = Intent(Intent.ACTION_MAIN)
            .addCategory(Intent.CATEGORY_LAUNCHER)
            .setPackage(context.packageName)
        val launcherMatches = packageManager.queryIntentActivities(launcherIntent, 0)
        assertEquals("The APK must expose exactly one desktop entry", 1, launcherMatches.size)
        val activityInfo = launcherMatches.single().activityInfo
        assertEquals(OpenccActivity::class.java.name, activityInfo.name)
        assertTrue("The Launcher activity must be exported", activityInfo.exported)
        assertNull("Desktop launch must not require the AutoJs6 plugin permission", activityInfo.permission)

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
        assertFalse(
            "The standalone APK must remain offline",
            packageManager.checkPermission(android.Manifest.permission.INTERNET, context.packageName) ==
                PackageManager.PERMISSION_GRANTED,
        )
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

    private fun withBoundPlugin(block: (IOpenccPlugin) -> Unit) {
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
            block(IOpenccPlugin.Stub.asInterface(rawBinder))
        } finally {
            context.unbindService(connection)
        }
    }

    private companion object {
        const val PLUGIN_PERMISSION = "org.autojs.permission.PLUGIN"
        const val SMOKE_INPUT = "汉字软件 😀 𠀀"
        const val SMOKE_OUTPUT = "漢字軟件 😀 𠀀"
        const val CONVERSION_TIMEOUT_MILLIS = 30_000L
        const val POLL_INTERVAL_MILLIS = 50L
    }
}
