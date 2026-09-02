package io.github.supermonster003.autojs6.plugin.opencc

import android.content.ComponentName
import android.content.Intent
import android.graphics.Bitmap
import android.os.Environment
import android.os.SystemClock
import android.widget.EditText
import android.widget.ScrollView
import android.widget.Spinner
import android.widget.TextView
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccConversionType
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.Callable
import java.util.concurrent.FutureTask
import java.util.concurrent.TimeUnit

/** Explicitly invoked fixture for reproducible, unedited documentation screenshots. */
@RunWith(AndroidJUnit4::class)
class OpenccDocumentationScreenshotTest {

    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val context = instrumentation.targetContext

    @Test
    fun capturePopulatedStandaloneScreen() {
        val requestedName = InstrumentationRegistry.getArguments().getString(ARG_FILE_NAME).orEmpty()
        require(FILE_NAME_PATTERN.matches(requestedName)) {
            "Pass -e $ARG_FILE_NAME a safe .png file name"
        }

        val activity = launchActivity()
        try {
            val source = activity.findViewById<EditText>(R.id.source_text)
            val types = activity.findViewById<Spinner>(R.id.conversion_type)
            val result = activity.findViewById<TextView>(R.id.result_text)
            val status = activity.findViewById<TextView>(R.id.conversion_status)
            onMain {
                source.setText(SCREENSHOT_SOURCE)
                source.setSelection(source.text.length)
                source.clearFocus()
                types.setSelection(OpenccConversionType.S2T.ordinal)
                activity.findViewById<TextView>(R.id.convert_button).performClick()
            }
            await("converted screenshot content") {
                readText(result) == SCREENSHOT_RESULT &&
                    readText(status) == activity.getString(R.string.standalone_status_complete)
            }
            onMain {
                activity.findViewById<ScrollView>(R.id.standalone_root).scrollTo(0, 0)
                activity.window.decorView.requestFocus()
            }
            instrumentation.waitForIdleSync()
            SystemClock.sleep(500)

            val outputDirectory = requireNotNull(
                context.getExternalFilesDir(Environment.DIRECTORY_PICTURES),
            ).resolve("opencc-docs")
            assertTrue(outputDirectory.mkdirs() || outputDirectory.isDirectory)
            val output = File(outputDirectory, requestedName)
            val screenshot = requireNotNull(instrumentation.uiAutomation.takeScreenshot())
            FileOutputStream(output).use { stream ->
                assertTrue(screenshot.compress(Bitmap.CompressFormat.PNG, 100, stream))
            }
            screenshot.recycle()
            println("OPENCC_DOCUMENTATION_SCREENSHOT=${output.absolutePath}")
            assertTrue(output.isFile && output.length() > 0L)
        } finally {
            onMain {
                if (!activity.isFinishing && !activity.isDestroyed) activity.finish()
            }
            instrumentation.waitForIdleSync()
        }
    }

    private fun launchActivity(): OpenccActivity {
        val intent = Intent(Intent.ACTION_MAIN)
            .addCategory(Intent.CATEGORY_LAUNCHER)
            .setComponent(ComponentName(context, OpenccActivity::class.java))
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
        return instrumentation.startActivitySync(intent) as OpenccActivity
    }

    private fun readText(view: TextView): String = onMain { view.text.toString() }

    private fun await(description: String, predicate: () -> Boolean) {
        val deadline = SystemClock.elapsedRealtime() + TIMEOUT_MILLIS
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

    private companion object {
        const val ARG_FILE_NAME = "opencc_screenshot_file"
        val FILE_NAME_PATTERN = Regex("[a-z0-9][a-z0-9-]{0,63}\\.png")
        const val SCREENSHOT_SOURCE = "汉字转换\n软件, 鼠标和内存\n离线 OpenCC 😀"
        const val SCREENSHOT_RESULT = "漢字轉換\n軟件, 鼠標和內存\n離線 OpenCC 😀"
        const val TIMEOUT_MILLIS = 60_000L
        const val POLL_INTERVAL_MILLIS = 50L
    }
}
