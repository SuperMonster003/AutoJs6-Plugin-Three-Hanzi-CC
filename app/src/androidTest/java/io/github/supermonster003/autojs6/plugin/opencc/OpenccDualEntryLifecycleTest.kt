package io.github.supermonster003.autojs6.plugin.opencc

import android.app.Activity
import android.app.Application
import android.content.ClipData
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.net.Uri
import android.os.Bundle
import android.os.IBinder
import android.os.ParcelFileDescriptor
import android.os.SystemClock
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccConversionType
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccNativeEngine
import org.autojs.plugin.opencc.api.IOpenccPlugin
import org.autojs.plugin.opencc.api.OpenccConversionTypes
import org.autojs.plugin.opencc.api.OpenccPluginActions
import org.autojs.plugin.opencc.api.OpenccPluginIds
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertSame
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.util.concurrent.Callable
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.Future
import java.util.concurrent.FutureTask
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicReference

@RunWith(AndroidJUnit4::class)
class OpenccDualEntryLifecycleTest {

    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val context = instrumentation.targetContext

    @Test
    fun uiAndBinderStayIsolatedAcrossConcurrencyBackgroundAndComponentRestart() {
        var activity = launchActivityWithUntrustedPayload()
        var binding: BoundPlugin? = null
        try {
            var views = views(activity)
            assertEquals("Launcher must ignore incoming text extras", "", readText(views.source))
            assertEquals("Launcher must ignore incoming URI/ClipData payloads", "", readText(views.result))

            binding = bindPlugin()
            assertTrue("Bound-only plugin service is missing from ActivityManager", isPluginServiceRunning())
            assertSame(
                "Both entry points must retain the process-scoped coordinator",
                OpenccConversionCoordinator.get(context),
                OpenccConversionCoordinator.get(activity),
            )

            assertConcurrentUiBinderAndCacheClear(activity, views, binding.plugin)
            assertBackgroundRoundTripKeepsEditorState(activity, views, binding.plugin)

            binding.close()
            binding = null
            await("bound-only service destruction") { !isPluginServiceRunning() }
            convertUi(activity, views, "汉字软件 😀", OpenccConversionType.S2T, "漢字軟件 😀")

            onMain { activity.finish() }
            instrumentation.waitForIdleSync()
            activity = launchActivity()
            views = views(activity)
            convertUi(activity, views, "漢字軟件", OpenccConversionType.T2S, "汉字软件")

            binding = bindPlugin()
            assertEquals(
                "UI-selected T2S state must not alter Binder's explicit S2T behavior",
                "漢字軟件",
                binding.plugin.convert("汉字软件", OpenccConversionTypes.S2T),
            )
            convertUi(activity, views, "汉字软件", OpenccConversionType.S2T, "漢字軟件")
            assertEquals(
                "Alternating back to Binder must retain the requested conversion type",
                "汉字软件",
                binding.plugin.convert("漢字軟件", OpenccConversionTypes.T2S),
            )
        } finally {
            binding?.close()
            onMain {
                if (!activity.isFinishing && !activity.isDestroyed) activity.finish()
            }
            instrumentation.waitForIdleSync()
        }
    }

    private fun assertConcurrentUiBinderAndCacheClear(
        activity: OpenccActivity,
        views: Views,
        plugin: IOpenccPlugin,
    ) {
        val uiInput = "汉A😀𠀀 ".repeat(4096)
        val uiOutput = "漢A😀𠀀 ".repeat(4096)
        selectType(views, OpenccConversionType.S2T)
        onMain {
            views.source.setText(uiInput)
            check(views.convert.performClick()) { "Concurrent UI conversion click was not accepted" }
            assertFalse("UI conversion button must debounce an active request", views.convert.isEnabled)
            assertEquals(View.VISIBLE, views.cancel.visibility)
        }

        val start = CountDownLatch(1)
        val executor = Executors.newFixedThreadPool(CONCURRENT_THREADS)
        val operations = mutableListOf<ExpectedFuture>()
        try {
            repeat(BINDER_CONVERSION_COUNT) { index ->
                val simplified = "$index 汉字软件 😀 𠀀"
                val expected = "$index 漢字軟件 😀 𠀀"
                operations += ExpectedFuture(
                    expected,
                    executor.submit<String> {
                        check(start.await(15, TimeUnit.SECONDS)) { "Concurrent start gate timed out" }
                        plugin.convert(simplified, OpenccConversionTypes.S2T)
                    },
                )
                if (index % CACHE_CLEAR_INTERVAL == 0) {
                    operations += ExpectedFuture(
                        "cache-$index 汉字",
                        executor.submit<String> {
                            check(start.await(15, TimeUnit.SECONDS)) { "Cache-clear start gate timed out" }
                            OpenccNativeEngine(context).use { engine ->
                                "cache-$index " + engine.convert("漢字", OpenccConversionType.T2S)
                            }
                        },
                    )
                }
            }
            start.countDown()
            val deadline = SystemClock.elapsedRealtime() + CONCURRENT_TIMEOUT_MILLIS
            operations.forEachIndexed { index, operation ->
                val remaining = (deadline - SystemClock.elapsedRealtime()).coerceAtLeast(1L)
                assertEquals(
                    "Concurrent UI/Binder/cache operation $index returned the wrong type or text",
                    operation.expected,
                    operation.future.get(remaining, TimeUnit.MILLISECONDS),
                )
            }
            await("concurrent standalone conversion") {
                readText(views.status) == activity.getString(R.string.standalone_status_complete)
            }
            assertEquals(uiOutput, readText(views.result))
            assertTrue(isEnabled(views.convert))
            assertEquals(View.GONE, visibility(views.cancel))

            // A temporary engine closes by clearing the process-wide native converter cache.
            // The long-lived coordinator must transparently recreate it on the next call.
            assertEquals("漢字", plugin.convert("汉字", OpenccConversionTypes.S2T))
            convertUi(activity, views, "软件", OpenccConversionType.S2T, "軟件")
        } finally {
            start.countDown()
            executor.shutdownNow()
            assertTrue("Concurrent conversion executor did not stop", executor.awaitTermination(10, TimeUnit.SECONDS))
        }
    }

    private fun assertBackgroundRoundTripKeepsEditorState(
        activity: OpenccActivity,
        views: Views,
        plugin: IOpenccPlugin,
    ) {
        convertUi(activity, views, BACKGROUND_SOURCE, BACKGROUND_TYPE, BACKGROUND_RESULT)
        val stopped = CountDownLatch(1)
        val resumed = CountDownLatch(1)
        val backgroundObserved = AtomicBoolean(false)
        val unexpectedActivities = AtomicInteger(0)
        val callbacks = object : Application.ActivityLifecycleCallbacks {
            override fun onActivityCreated(candidate: Activity, state: Bundle?) {
                if (candidate is OpenccActivity && candidate !== activity) unexpectedActivities.incrementAndGet()
            }

            override fun onActivityStarted(activity: Activity) = Unit

            override fun onActivityResumed(candidate: Activity) {
                if (candidate === activity && backgroundObserved.get()) resumed.countDown()
            }

            override fun onActivityPaused(activity: Activity) = Unit

            override fun onActivityStopped(candidate: Activity) {
                if (candidate === activity) {
                    backgroundObserved.set(true)
                    stopped.countDown()
                }
            }

            override fun onActivitySaveInstanceState(activity: Activity, state: Bundle) = Unit
            override fun onActivityDestroyed(activity: Activity) = Unit
        }
        activity.application.registerActivityLifecycleCallbacks(callbacks)
        try {
            assertTrue("Unable to move the standalone task to background", onMain { activity.moveTaskToBack(true) })
            assertTrue("Standalone Activity did not reach stopped state", stopped.await(15, TimeUnit.SECONDS))
            assertEquals(
                "Binder must remain usable while the standalone task is in background",
                "漢字軟件",
                plugin.convert("汉字软件", OpenccConversionTypes.S2T),
            )

            val component = ComponentName(context, OpenccActivity::class.java).flattenToShortString()
            val startOutput = runShellCommand(
                "am start --activity-reorder-to-front --activity-single-top " +
                    "-a ${Intent.ACTION_MAIN} -c ${Intent.CATEGORY_LAUNCHER} -n $component",
            )
            assertFalse("Shell failed to return the standalone task to foreground: $startOutput", "Error:" in startOutput)
            assertTrue("Standalone Activity did not resume from background", resumed.await(15, TimeUnit.SECONDS))
            instrumentation.waitForIdleSync()
            assertEquals("Relaunching from Launcher must reuse the existing task", 0, unexpectedActivities.get())
            assertEquals(BACKGROUND_SOURCE, readText(views.source))
            assertEquals(BACKGROUND_RESULT, readText(views.result))
            assertEquals(BACKGROUND_TYPE.ordinal, selectedPosition(views.types))
        } finally {
            activity.application.unregisterActivityLifecycleCallbacks(callbacks)
        }
    }

    private fun launchActivityWithUntrustedPayload(): OpenccActivity {
        return launchActivity(
            Intent(Intent.ACTION_MAIN)
                .addCategory(Intent.CATEGORY_LAUNCHER)
                .setData(Uri.parse("content://untrusted.example/private/document"))
                .putExtra(Intent.EXTRA_TEXT, "untrusted external text")
                .apply {
                    clipData = ClipData.newPlainText("untrusted", "untrusted clip text")
                },
        )
    }

    private fun launchActivity(intent: Intent = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)): OpenccActivity {
        intent.setComponent(ComponentName(context, OpenccActivity::class.java))
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
        return instrumentation.startActivitySync(intent) as OpenccActivity
    }

    private fun views(activity: OpenccActivity) = Views(
        source = activity.findViewById(R.id.source_text),
        types = activity.findViewById(R.id.conversion_type),
        convert = activity.findViewById(R.id.convert_button),
        cancel = activity.findViewById(R.id.cancel_button),
        result = activity.findViewById(R.id.result_text),
        status = activity.findViewById(R.id.conversion_status),
    )

    private fun convertUi(
        activity: OpenccActivity,
        views: Views,
        source: String,
        type: OpenccConversionType,
        expected: String,
    ) {
        selectType(views, type)
        onMain {
            views.source.setText(source)
            check(views.convert.performClick()) { "UI conversion click was not accepted for $type" }
        }
        await("UI conversion for $type") {
            readText(views.result) == expected &&
                readText(views.status) == activity.getString(R.string.standalone_status_complete) &&
                isEnabled(views.convert)
        }
    }

    private fun selectType(views: Views, type: OpenccConversionType) {
        onMain { views.types.setSelection(type.ordinal) }
        instrumentation.waitForIdleSync()
        assertEquals(type.ordinal, selectedPosition(views.types))
    }

    private fun bindPlugin(): BoundPlugin {
        val discoveryIntent = Intent(OpenccPluginActions.OPENCC)
            .addCategory(OpenccPluginIds.ID)
            .setPackage(context.packageName)
        @Suppress("DEPRECATION")
        val matches = context.packageManager.queryIntentServices(discoveryIntent, 0)
        assertEquals("OpenCC discovery must resolve exactly one service", 1, matches.size)
        val serviceInfo = matches.single().serviceInfo
        val explicitIntent = Intent(discoveryIntent).setComponent(
            ComponentName(serviceInfo.packageName, serviceInfo.name),
        )
        val connected = CountDownLatch(1)
        val binder = AtomicReference<IBinder?>()
        val connection = object : ServiceConnection {
            override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
                binder.set(service)
                connected.countDown()
            }

            override fun onServiceDisconnected(name: ComponentName?) = Unit
            override fun onNullBinding(name: ComponentName?) = connected.countDown()
            override fun onBindingDied(name: ComponentName?) = connected.countDown()
        }
        assertTrue(
            "Unable to bind the discovered OpenCC service",
            context.bindService(explicitIntent, connection, Context.BIND_AUTO_CREATE),
        )
        assertTrue("Timed out binding the OpenCC service", connected.await(15, TimeUnit.SECONDS))
        val rawBinder = binder.get()
        assertNotNull("OpenCC service returned a null Binder", rawBinder)
        return BoundPlugin(connection, remoteOpenccPlugin(rawBinder!!))
    }

    private fun isPluginServiceRunning(): Boolean {
        val component = ComponentName(context, OpenccPluginService::class.java).flattenToShortString()
        val output = runShellCommand("dumpsys activity services $component")
        return "ServiceRecord{" in output && component in output
    }

    private fun runShellCommand(command: String): String {
        val descriptor = instrumentation.uiAutomation.executeShellCommand(
            command,
        )
        return ParcelFileDescriptor.AutoCloseInputStream(descriptor)
            .bufferedReader()
            .use { it.readText() }
    }

    private fun readText(view: TextView): String = onMain { view.text.toString() }
    private fun selectedPosition(view: Spinner): Int = onMain { view.selectedItemPosition }
    private fun isEnabled(view: View): Boolean = onMain { view.isEnabled }
    private fun visibility(view: View): Int = onMain { view.visibility }

    private fun await(description: String, predicate: () -> Boolean) {
        val deadline = SystemClock.elapsedRealtime() + UI_TIMEOUT_MILLIS
        while (SystemClock.elapsedRealtime() < deadline) {
            if (predicate()) return
            SystemClock.sleep(POLL_INTERVAL_MILLIS)
        }
        throw AssertionError("Timed out waiting for $description")
    }

    private fun <T> onMain(block: () -> T): T {
        val task = FutureTask(Callable { block() })
        instrumentation.runOnMainSync(task)
        return task.get(5, TimeUnit.SECONDS)
    }

    private inner class BoundPlugin(
        private val connection: ServiceConnection,
        val plugin: IOpenccPlugin,
    ) {
        private var closed = false

        fun close() {
            if (closed) return
            closed = true
            context.unbindService(connection)
        }
    }

    private data class ExpectedFuture(
        val expected: String,
        val future: Future<String>,
    )

    private data class Views(
        val source: EditText,
        val types: Spinner,
        val convert: Button,
        val cancel: Button,
        val result: TextView,
        val status: TextView,
    )

    private companion object {
        const val BINDER_CONVERSION_COUNT = 64
        const val CACHE_CLEAR_INTERVAL = 4
        const val CONCURRENT_THREADS = 10
        const val CONCURRENT_TIMEOUT_MILLIS = 120_000L
        const val UI_TIMEOUT_MILLIS = 60_000L
        const val POLL_INTERVAL_MILLIS = 50L
        const val BACKGROUND_SOURCE = "汉字软件 😀 𠀀 مرحبا"
        const val BACKGROUND_RESULT = "漢字軟件 😀 𠀀 مرحبا"
        val BACKGROUND_TYPE = OpenccConversionType.S2T
    }
}
