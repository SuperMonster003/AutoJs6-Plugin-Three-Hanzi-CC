package io.github.supermonster003.autojs6.plugin.opencc

import android.app.Activity
import android.app.Application
import android.app.Instrumentation
import android.content.ClipData
import android.content.ClipboardManager
import android.content.ComponentName
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.os.SystemClock
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccConversionType
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test
import org.junit.runner.RunWith
import java.util.concurrent.Callable
import java.util.concurrent.CountDownLatch
import java.util.concurrent.FutureTask
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

@RunWith(AndroidJUnit4::class)
class OpenccStandaloneUiTest {

    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val context = instrumentation.targetContext

    @Test
    fun allStandaloneActionsRemainExplicitCancellableAndRestorable() {
        var activity = launchActivity()
        val clipboard = activity.getSystemService(ClipboardManager::class.java)
        val previousClip = clipboard.primaryClip
        try {
            var views = views(activity)
            assertFriendlyConversionLabels(views)
            assertEmptyInputIsSafe(activity, views)
            assertAllConversionTypes(activity, views)
            assertLongUnicodeAndRtlText(activity, views)
            assertCancellationAndDuplicateClick(activity, views)
            assertExplicitClipboardActions(activity, views, clipboard)
            assertSwapKeepsConversionType(activity, views)
            assertExplicitShareAction(activity, views)

            activity = assertStateRestoredAfterRecreation(activity, views)
            views = views(activity)
            assertEquals(RESTORED_SOURCE, readText(views.source))
            assertEquals(RESTORED_RESULT, readText(views.result))
            assertEquals(RESTORED_TYPE.ordinal, selectedPosition(views.types))
        } finally {
            restoreClipboard(clipboard, previousClip)
            onMain {
                if (!activity.isFinishing && !activity.isDestroyed) activity.finish()
            }
            instrumentation.waitForIdleSync()
        }
    }

    private fun assertFriendlyConversionLabels(views: Views) {
        val labels = onMain {
            (0 until views.types.adapter.count).map { index ->
                views.types.adapter.getItem(index).toString()
            }
        }
        assertEquals(OpenccConversionType.values().size, labels.size)
        assertEquals("Every conversion label must be distinct", labels.size, labels.toSet().size)
        OpenccConversionType.values().forEachIndexed { index, type ->
            assertTrue("$type label must retain its stable code: ${labels[index]}", labels[index].contains(type.name))
            assertNotEquals("$type must have a user-facing name", type.name, labels[index])
        }

        assertNotEquals(labels[OpenccConversionType.S2TW.ordinal], labels[OpenccConversionType.S2TWP.ordinal])
        assertNotEquals(labels[OpenccConversionType.TW2S.ordinal], labels[OpenccConversionType.TW2SP.ordinal])
        assertTrue(
            labels[OpenccConversionType.T2JP.ordinal].contains(
                context.getString(R.string.standalone_script_japanese_shinjitai),
            ),
        )
    }

    private fun assertEmptyInputIsSafe(activity: OpenccActivity, views: Views) {
        onMain {
            views.source.setText("")
            views.convert.performClick()
        }
        assertEquals(context.getString(R.string.standalone_status_no_source), readText(views.status))
        assertEquals("", readText(views.result))
        assertEquals(View.GONE, visibility(views.cancel))
        assertTrue(isEnabled(views.convert))
        assertFalse(activity.isFinishing)
    }

    private fun assertAllConversionTypes(activity: OpenccActivity, views: Views) {
        assertEquals(OpenccConversionType.values().toSet(), SMOKE_OUTPUTS.keys)
        for (type in OpenccConversionType.values()) {
            convert(activity, views, SMOKE_INPUT, type, SMOKE_OUTPUTS.getValue(type))
        }
    }

    private fun assertLongUnicodeAndRtlText(activity: OpenccActivity, views: Views) {
        val input = "汉A😀𠀀 مرحبا ".repeat(2048)
        val expected = "漢A😀𠀀 مرحبا ".repeat(2048)
        convert(activity, views, input, OpenccConversionType.S2T, expected)
    }

    private fun assertCancellationAndDuplicateClick(activity: OpenccActivity, views: Views) {
        val stableResult = readText(views.result)
        selectType(views, OpenccConversionType.S2T)
        val duplicateWasEnabled = onMain {
            views.source.setText("汉字软件 😀 𠀀 ".repeat(8192))
            check(views.convert.performClick()) { "Initial conversion click was not accepted" }
            val wasEnabled = views.convert.isEnabled
            views.convert.performClick()
            assertEquals(View.VISIBLE, views.cancel.visibility)
            assertEquals(View.VISIBLE, activity.findViewById<View>(R.id.conversion_progress).visibility)
            check(views.cancel.performClick()) { "Cancel click was not accepted" }
            wasEnabled
        }
        assertFalse("A repeated conversion click must be disabled", duplicateWasEnabled)
        assertEquals(context.getString(R.string.standalone_status_canceled), readText(views.status))
        assertEquals(stableResult, readText(views.result))
        assertEquals(View.GONE, visibility(views.cancel))

        // A subsequent request cannot be overwritten by a late result from the canceled request.
        convert(activity, views, "汉字", OpenccConversionType.S2T, "漢字")
        SystemClock.sleep(250)
        instrumentation.waitForIdleSync()
        assertEquals("漢字", readText(views.result))
    }

    private fun assertExplicitClipboardActions(
        activity: OpenccActivity,
        views: Views,
        clipboard: ClipboardManager,
    ) {
        val unchangedSource = "Do not read the clipboard automatically"
        onMain { views.source.setText(unchangedSource) }
        clipboard.setPrimaryClip(ClipData.newPlainText("OpenCC UI test", CLIPBOARD_SOURCE))
        instrumentation.waitForIdleSync()
        assertEquals(
            "Setting the clipboard must not change the source until Paste is clicked",
            unchangedSource,
            readText(views.source),
        )

        onMain { views.paste.performClick() }
        assertEquals(CLIPBOARD_SOURCE, readText(views.source))
        assertEquals(context.getString(R.string.standalone_status_pasted), readText(views.status))

        onMain { views.clear.performClick() }
        assertEquals("", readText(views.source))
        assertEquals("", readText(views.result))
        assertEquals(context.getString(R.string.standalone_status_cleared), readText(views.status))

        convert(activity, views, "软件", OpenccConversionType.S2T, "軟件")
        onMain { views.copy.performClick() }
        assertEquals("軟件", clipboard.primaryClip?.getItemAt(0)?.text?.toString())
        assertEquals(context.getString(R.string.standalone_status_copied), readText(views.status))
    }

    private fun assertSwapKeepsConversionType(activity: OpenccActivity, views: Views) {
        selectType(views, OpenccConversionType.S2TWP)
        val selectedBeforeSwap = selectedPosition(views.types)
        assertEquals("软件", readText(views.source))
        assertEquals("軟件", readText(views.result))

        onMain { views.swap.performClick() }
        assertEquals("軟件", readText(views.source))
        assertEquals("软件", readText(views.result))
        assertEquals(selectedBeforeSwap, selectedPosition(views.types))
        assertEquals(context.getString(R.string.standalone_status_swapped), readText(views.status))
        assertFalse(activity.isFinishing)
    }

    private fun assertExplicitShareAction(activity: OpenccActivity, views: Views) {
        val monitor = ShareIntentMonitor()
        instrumentation.addMonitor(monitor)
        try {
            onMain { views.share.performClick() }
            assertTrue("Share chooser was not started", monitor.started.await(5, TimeUnit.SECONDS))
            val chooser = requireNotNull(monitor.intent.get()) { "Share chooser intent is missing" }
            assertEquals(Intent.ACTION_CHOOSER, chooser.action)
            val sendIntent = requireNotNull(chooser.shareTarget()) { "Share target intent is missing" }
            assertEquals(Intent.ACTION_SEND, sendIntent.action)
            assertEquals("text/plain", sendIntent.type)
            assertEquals("软件", sendIntent.getStringExtra(Intent.EXTRA_TEXT))
            assertEquals(
                context.getString(R.string.standalone_status_share_opened),
                readText(views.status),
            )
            assertFalse(activity.isFinishing)
        } finally {
            instrumentation.removeMonitor(monitor)
        }
    }

    private fun assertStateRestoredAfterRecreation(
        activity: OpenccActivity,
        views: Views,
    ): OpenccActivity {
        selectType(views, RESTORED_TYPE)
        onMain {
            views.source.setText(RESTORED_SOURCE)
            views.result.text = RESTORED_RESULT
        }

        val recreated = AtomicReference<OpenccActivity?>()
        val created = CountDownLatch(1)
        val callbacks = object : Application.ActivityLifecycleCallbacks {
            override fun onActivityCreated(candidate: Activity, state: Bundle?) {
                if (candidate is OpenccActivity && candidate !== activity) {
                    recreated.compareAndSet(null, candidate)
                    created.countDown()
                }
            }

            override fun onActivityStarted(activity: Activity) = Unit
            override fun onActivityResumed(activity: Activity) = Unit
            override fun onActivityPaused(activity: Activity) = Unit
            override fun onActivityStopped(activity: Activity) = Unit
            override fun onActivitySaveInstanceState(activity: Activity, state: Bundle) = Unit
            override fun onActivityDestroyed(activity: Activity) = Unit
        }
        activity.application.registerActivityLifecycleCallbacks(callbacks)
        try {
            onMain { activity.recreate() }
            assertTrue("Timed out recreating the standalone Activity", created.await(15, TimeUnit.SECONDS))
            instrumentation.waitForIdleSync()
            return requireNotNull(recreated.get())
        } finally {
            activity.application.unregisterActivityLifecycleCallbacks(callbacks)
        }
    }

    private fun convert(
        activity: OpenccActivity,
        views: Views,
        input: String,
        type: OpenccConversionType,
        expected: String,
    ) {
        selectType(views, type)
        onMain {
            views.source.setText(input)
            check(views.convert.performClick()) { "Convert click was not accepted for $type" }
        }
        val completedText = activity.getString(R.string.standalone_status_complete)
        await("$type conversion result") {
            readText(views.result) == expected &&
                readText(views.status) == completedText &&
                isEnabled(views.convert)
        }
    }

    private fun selectType(views: Views, type: OpenccConversionType) {
        onMain { views.types.setSelection(type.ordinal) }
        instrumentation.waitForIdleSync()
        assertEquals(type.ordinal, selectedPosition(views.types))
    }

    private fun launchActivity(): OpenccActivity {
        val intent = Intent(Intent.ACTION_MAIN)
            .addCategory(Intent.CATEGORY_LAUNCHER)
            .setComponent(ComponentName(context, OpenccActivity::class.java))
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
        return instrumentation.startActivitySync(intent) as OpenccActivity
    }

    private fun views(activity: OpenccActivity) = Views(
        source = activity.findViewById(R.id.source_text),
        types = activity.findViewById(R.id.conversion_type),
        paste = activity.findViewById(R.id.paste_button),
        clear = activity.findViewById(R.id.clear_button),
        convert = activity.findViewById(R.id.convert_button),
        cancel = activity.findViewById(R.id.cancel_button),
        result = activity.findViewById(R.id.result_text),
        copy = activity.findViewById(R.id.copy_button),
        swap = activity.findViewById(R.id.swap_button),
        share = activity.findViewById(R.id.share_button),
        status = activity.findViewById(R.id.conversion_status),
    )

    private fun readText(view: TextView): String = onMain { view.text.toString() }

    private fun selectedPosition(spinner: Spinner): Int = onMain { spinner.selectedItemPosition }

    private fun visibility(view: View): Int = onMain { view.visibility }

    private fun isEnabled(view: View): Boolean = onMain { view.isEnabled }

    private fun await(description: String, predicate: () -> Boolean) {
        val deadline = SystemClock.elapsedRealtime() + CONVERSION_TIMEOUT_MILLIS
        while (SystemClock.elapsedRealtime() < deadline) {
            if (predicate()) return
            SystemClock.sleep(POLL_INTERVAL_MILLIS)
        }
        fail("Timed out waiting for $description")
    }

    private fun <T> onMain(block: () -> T): T {
        val task = FutureTask(Callable { block() })
        instrumentation.runOnMainSync(task)
        return task.get(5, TimeUnit.SECONDS)
    }

    private fun restoreClipboard(clipboard: ClipboardManager, previousClip: ClipData?) {
        if (previousClip != null) {
            clipboard.setPrimaryClip(previousClip)
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            clipboard.clearPrimaryClip()
        } else {
            clipboard.setPrimaryClip(ClipData.newPlainText("", ""))
        }
    }

    @Suppress("DEPRECATION")
    private fun Intent.shareTarget(): Intent? {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            getParcelableExtra(Intent.EXTRA_INTENT, Intent::class.java)
        } else {
            getParcelableExtra(Intent.EXTRA_INTENT)
        }
    }

    private class ShareIntentMonitor : Instrumentation.ActivityMonitor() {
        val started = CountDownLatch(1)
        val intent = AtomicReference<Intent?>()

        override fun onStartActivity(candidate: Intent): Instrumentation.ActivityResult? {
            if (candidate.action != Intent.ACTION_CHOOSER) return null
            intent.compareAndSet(null, Intent(candidate))
            started.countDown()
            return Instrumentation.ActivityResult(Activity.RESULT_CANCELED, null)
        }
    }

    private data class Views(
        val source: EditText,
        val types: Spinner,
        val paste: Button,
        val clear: Button,
        val convert: Button,
        val cancel: Button,
        val result: TextView,
        val copy: Button,
        val swap: Button,
        val share: Button,
        val status: TextView,
    )

    private companion object {
        const val SMOKE_INPUT = "汉字漢字软件軟體里面裏面"
        const val CLIPBOARD_SOURCE = "粘贴文本 😀 𠀀"
        const val RESTORED_SOURCE = "重建来源 😀 𠀀 مرحبا"
        const val RESTORED_RESULT = "重建結果 😀 𠀀 مرحبا"
        val RESTORED_TYPE = OpenccConversionType.TW2SP
        const val CONVERSION_TIMEOUT_MILLIS = 60_000L
        const val POLL_INTERVAL_MILLIS = 50L

        val SMOKE_OUTPUTS = mapOf(
            OpenccConversionType.HK2S to "汉字汉字软件软体里面里面",
            OpenccConversionType.HK2T to "汉字漢字软件軟體里面裏面",
            OpenccConversionType.JP2T to "汉字漢字软件軟體里面裏面",
            OpenccConversionType.S2HK to "漢字漢字軟件軟體裏面裏面",
            OpenccConversionType.S2T to "漢字漢字軟件軟體裏面裏面",
            OpenccConversionType.S2TW to "漢字漢字軟件軟體裡面裡面",
            OpenccConversionType.S2TWP to "漢字漢字軟體軟體裡面裡面",
            OpenccConversionType.T2HK to "汉字漢字软件軟體里面裏面",
            OpenccConversionType.T2S to "汉字汉字软件软体里面里面",
            OpenccConversionType.T2TW to "汉字漢字软件軟體里面裡面",
            OpenccConversionType.T2JP to "汉字漢字软件軟体里面裏面",
            OpenccConversionType.TW2S to "汉字汉字软件软体里面里面",
            OpenccConversionType.TW2T to "汉字漢字软件軟體里面裏面",
            OpenccConversionType.TW2SP to "汉字汉字软件软件里面里面",
        )
    }
}
