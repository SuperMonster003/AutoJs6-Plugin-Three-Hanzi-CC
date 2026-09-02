package io.github.supermonster003.autojs6.plugin.opencc

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.ActivityInfo
import android.content.res.Configuration
import android.app.Activity
import android.app.Application
import android.os.Bundle
import android.os.Build
import android.os.SystemClock
import android.text.BidiFormatter
import android.view.ContextThemeWrapper
import android.view.KeyEvent
import android.view.LayoutInflater
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.ScrollView
import android.widget.Spinner
import android.widget.TextView
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.util.Locale
import java.util.concurrent.Callable
import java.util.concurrent.CountDownLatch
import java.util.concurrent.FutureTask
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference
import kotlin.math.roundToInt

@RunWith(AndroidJUnit4::class)
class OpenccAccessibilityLayoutTest {

    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val context = instrumentation.targetContext

    @Test
    fun standaloneUiHasStableSemanticsKeyboardFlowAndResponsiveLayouts() {
        var activity = launchActivity()
        try {
            assertRequestedRuntimeConfiguration(activity)
            assertAccessibilitySemanticsAndFocusOrder(activity)
            assertHardwareKeyboardConversion(activity)
            assertIndependentLongTextScrolling(activity)
            assertSyntheticPhoneAndTabletConfigurations()
            assertDayAndNightResourcesDiffer()
            activity = assertOrientationChangesPreserveEditorState(activity)
        } finally {
            onMain {
                if (!activity.isFinishing && !activity.isDestroyed) activity.finish()
            }
            instrumentation.waitForIdleSync()
        }
    }

    private fun assertRequestedRuntimeConfiguration(activity: OpenccActivity) {
        val arguments = InstrumentationRegistry.getArguments()
        if (arguments.getString(ARG_EXPECT_RTL).toBoolean()) {
            assertEquals(View.LAYOUT_DIRECTION_RTL, activity.resources.configuration.layoutDirection)
            assertEquals(ARABIC_SOURCE_LABEL, activity.getString(R.string.standalone_source_label))
            assertTrue(BidiFormatter.getInstance(true).isRtl(activity.getString(R.string.standalone_subtitle)))
        }
        if (arguments.getString(ARG_EXPECT_LARGE_FONT).toBoolean()) {
            assertTrue(
                "Expected a system font scale of at least $LARGE_FONT_SCALE",
                activity.resources.configuration.fontScale >= LARGE_FONT_SCALE,
            )
        }
        if (arguments.getString(ARG_EXPECT_NIGHT).toBoolean()) {
            assertEquals(
                Configuration.UI_MODE_NIGHT_YES,
                activity.resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK,
            )
        }
    }

    private fun assertAccessibilitySemanticsAndFocusOrder(activity: OpenccActivity) {
        val title = activity.findViewById<TextView>(R.id.standalone_title)
        val sourceLabel = activity.findViewById<TextView>(R.id.source_text_label)
        val source = activity.findViewById<EditText>(R.id.source_text)
        val paste = activity.findViewById<Button>(R.id.paste_button)
        val clear = activity.findViewById<Button>(R.id.clear_button)
        val typeLabel = activity.findViewById<TextView>(R.id.conversion_type_label)
        val types = activity.findViewById<Spinner>(R.id.conversion_type)
        val convert = activity.findViewById<Button>(R.id.convert_button)
        val cancel = activity.findViewById<Button>(R.id.cancel_button)
        val progress = activity.findViewById<ProgressBar>(R.id.conversion_progress)
        val status = activity.findViewById<TextView>(R.id.conversion_status)
        val resultLabel = activity.findViewById<TextView>(R.id.result_text_label)
        val result = activity.findViewById<TextView>(R.id.result_text)
        val copy = activity.findViewById<Button>(R.id.copy_button)
        val swap = activity.findViewById<Button>(R.id.swap_button)
        val share = activity.findViewById<Button>(R.id.share_button)

        assertEquals(source.id, sourceLabel.labelFor)
        assertEquals(types.id, typeLabel.labelFor)
        assertEquals(result.id, resultLabel.labelFor)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            assertTrue("The screen title must be exposed as an accessibility heading", title.isAccessibilityHeading)
        }
        assertEquals(View.ACCESSIBILITY_LIVE_REGION_POLITE, status.accessibilityLiveRegion)
        assertFalse("Progress semantics must describe the active operation", progress.contentDescription.isNullOrBlank())
        assertTrue("Converted text must remain selectable", result.isTextSelectable)
        assertTrue(source.isVerticalScrollBarEnabled)
        assertTrue(result.isVerticalScrollBarEnabled)
        assertTrue(source.isNestedScrollingEnabled)
        assertTrue(result.isNestedScrollingEnabled)

        assertEquals(paste.id, source.nextFocusForwardId)
        assertEquals(clear.id, paste.nextFocusForwardId)
        assertEquals(types.id, clear.nextFocusForwardId)
        assertEquals(convert.id, types.nextFocusForwardId)
        assertEquals(convert.id, cancel.nextFocusForwardId)
        assertEquals(result.id, convert.nextFocusForwardId)
        assertEquals(copy.id, result.nextFocusForwardId)
        assertEquals(swap.id, copy.nextFocusForwardId)
        assertEquals(share.id, swap.nextFocusForwardId)
        assertEquals(source.id, share.nextFocusForwardId)

        val minimumTouchPixels = (MINIMUM_TOUCH_TARGET_DP * activity.resources.displayMetrics.density).roundToInt()
        listOf(paste, clear, types, convert, cancel, copy, swap, share).forEach { view ->
            assertTrue(
                "${activity.resources.getResourceEntryName(view.id)} is shorter than 48dp: ${view.height}px",
                view.height >= minimumTouchPixels || view.visibility == View.GONE,
            )
        }
    }

    private fun assertHardwareKeyboardConversion(activity: OpenccActivity) {
        val source = activity.findViewById<EditText>(R.id.source_text)
        val result = activity.findViewById<TextView>(R.id.result_text)
        val status = activity.findViewById<TextView>(R.id.conversion_status)
        onMain {
            source.requestFocus()
            source.setText(KEYBOARD_INPUT)
            source.setSelection(source.text.length)
        }
        val now = SystemClock.uptimeMillis()
        instrumentation.sendKeySync(
            KeyEvent(now, now, KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_ENTER, 0, KeyEvent.META_CTRL_ON),
        )
        instrumentation.sendKeySync(
            KeyEvent(now, SystemClock.uptimeMillis(), KeyEvent.ACTION_UP, KeyEvent.KEYCODE_ENTER, 0, KeyEvent.META_CTRL_ON),
        )
        await("Ctrl+Enter conversion") {
            readText(result) == KEYBOARD_OUTPUT &&
                readText(status) == activity.getString(R.string.standalone_status_complete)
        }
        assertEquals("Ctrl+Enter must not insert a newline", KEYBOARD_INPUT, readText(source))
    }

    private fun assertIndependentLongTextScrolling(activity: OpenccActivity) {
        val root = activity.findViewById<ScrollView>(R.id.standalone_root)
        val source = activity.findViewById<EditText>(R.id.source_text)
        val result = activity.findViewById<TextView>(R.id.result_text)
        val longText = LONG_TEXT_LINE.repeat(LONG_TEXT_REPETITIONS)
        onMain {
            source.setText(longText)
            source.setSelection(7, 21)
            result.text = longText
        }
        instrumentation.waitForIdleSync()

        assertEquals(7, source.selectionStart)
        assertEquals(21, source.selectionEnd)
        assertTrue("Long source text must scroll inside its editor", source.canScrollVertically(1))
        assertTrue("Long converted text must scroll inside its result view", result.canScrollVertically(1))
        assertTrue("The complete page must remain vertically scrollable", root.canScrollVertically(1))
        assertTrue(source.height <= activity.resources.getDimensionPixelSize(R.dimen.opencc_editor_max_height))
        assertTrue(result.height <= activity.resources.getDimensionPixelSize(R.dimen.opencc_editor_max_height))
    }

    private fun assertSyntheticPhoneAndTabletConfigurations() {
        val phone = measureLayout(
            widthDp = 320,
            heightDp = 480,
            smallestWidthDp = 320,
            fontScale = SYNTHETIC_FONT_SCALE,
            locale = Locale.forLanguageTag("ar"),
            night = true,
        )
        assertEquals(View.LAYOUT_DIRECTION_RTL, phone.layoutDirection)
        assertResponsiveChildren(phone)

        val tablet = measureLayout(
            widthDp = 960,
            heightDp = 600,
            smallestWidthDp = 600,
            fontScale = 1.3f,
            locale = Locale.ENGLISH,
            night = false,
        )
        assertEquals(View.LAYOUT_DIRECTION_LTR, tablet.layoutDirection)
        assertResponsiveChildren(tablet)

        val splitScreen = measureLayout(
            widthDp = 360,
            heightDp = 360,
            smallestWidthDp = 360,
            fontScale = SYNTHETIC_FONT_SCALE,
            locale = Locale.ENGLISH,
            night = false,
        )
        assertResponsiveChildren(splitScreen)

        val phonePadding = configurationContext(320, 480, 320, 1f, Locale.ENGLISH, false)
            .resources.getDimensionPixelSize(R.dimen.opencc_page_horizontal_padding)
        val tabletPadding = configurationContext(960, 600, 600, 1f, Locale.ENGLISH, false)
            .resources.getDimensionPixelSize(R.dimen.opencc_page_horizontal_padding)
        assertTrue("Tablet resources must provide a wider readable page gutter", tabletPadding > phonePadding)
    }

    private fun assertResponsiveChildren(root: ScrollView) {
        onMain {
            val source = root.findViewById<EditText>(R.id.source_text)
            val result = root.findViewById<TextView>(R.id.result_text)
            val types = root.findViewById<Spinner>(R.id.conversion_type)
            val longText = LONG_TEXT_LINE.repeat(LONG_TEXT_REPETITIONS)
            source.setText(longText)
            result.text = longText
            measureAndLayout(root, root.measuredWidth, root.measuredHeight)

            assertTrue(source.width > 0 && result.width > 0 && types.width > 0)
            assertTrue(source.height <= source.maxHeight)
            assertTrue(result.height <= result.maxHeight)
            assertTrue(source.canScrollVertically(1))
            assertTrue(result.canScrollVertically(1))

            val selected = types.selectedView as TextView
            assertTrue("Responsive spinner labels must lay out at least one line", selected.lineCount >= 1)
            for (line in 0 until selected.lineCount) {
                assertEquals("Responsive spinner labels must not be ellipsized", 0, selected.layout.getEllipsisCount(line))
            }
            listOf(
                R.id.paste_button,
                R.id.clear_button,
                R.id.convert_button,
                R.id.copy_button,
                R.id.swap_button,
                R.id.share_button,
            ).forEach { id ->
                val button = root.findViewById<Button>(id)
                assertTrue("Button ${button.text} has no measurable content", button.width > 0 && button.height > 0)
                for (line in 0 until button.lineCount) {
                    assertEquals("Button ${button.text} is ellipsized", 0, button.layout.getEllipsisCount(line))
                }
            }
        }
    }

    private fun measureLayout(
        widthDp: Int,
        heightDp: Int,
        smallestWidthDp: Int,
        fontScale: Float,
        locale: Locale,
        night: Boolean,
    ): ScrollView = onMain {
        val configured = configurationContext(widthDp, heightDp, smallestWidthDp, fontScale, locale, night)
        val themed = ContextThemeWrapper(configured, R.style.Theme_Opencc)
        val root = LayoutInflater.from(themed).inflate(R.layout.activity_opencc, null) as ScrollView
        root.layoutDirection = configured.resources.configuration.layoutDirection
        root.findViewById<Spinner>(R.id.conversion_type).adapter = ArrayAdapter(
            themed,
            R.layout.opencc_spinner_item,
            R.id.opencc_spinner_text,
            listOf(
                configured.getString(
                    R.string.standalone_conversion_direction_with_terminology,
                    configured.getString(R.string.standalone_script_simplified_chinese),
                    configured.getString(R.string.standalone_script_taiwan_traditional),
                    configured.getString(R.string.standalone_terminology_taiwan),
                    "S2TWP",
                ),
            ),
        ).apply {
            setDropDownViewResource(R.layout.opencc_spinner_dropdown_item)
        }
        val density = configured.resources.displayMetrics.density
        measureAndLayout(
            root,
            (widthDp * density).roundToInt(),
            (heightDp * density).roundToInt(),
        )
        root
    }

    private fun measureAndLayout(root: View, width: Int, height: Int) {
        root.measure(
            View.MeasureSpec.makeMeasureSpec(width, View.MeasureSpec.EXACTLY),
            View.MeasureSpec.makeMeasureSpec(height, View.MeasureSpec.EXACTLY),
        )
        root.layout(0, 0, root.measuredWidth, root.measuredHeight)
    }

    private fun configurationContext(
        widthDp: Int,
        heightDp: Int,
        smallestWidthDp: Int,
        fontScale: Float,
        locale: Locale,
        night: Boolean,
    ): Context {
        val configuration = Configuration(context.resources.configuration).apply {
            setLocale(locale)
            setLayoutDirection(locale)
            this.fontScale = fontScale
            screenWidthDp = widthDp
            screenHeightDp = heightDp
            smallestScreenWidthDp = smallestWidthDp
            orientation = if (widthDp > heightDp) {
                Configuration.ORIENTATION_LANDSCAPE
            } else {
                Configuration.ORIENTATION_PORTRAIT
            }
            uiMode = (uiMode and Configuration.UI_MODE_NIGHT_MASK.inv()) or if (night) {
                Configuration.UI_MODE_NIGHT_YES
            } else {
                Configuration.UI_MODE_NIGHT_NO
            }
        }
        return context.createConfigurationContext(configuration)
    }

    private fun assertDayAndNightResourcesDiffer() {
        val day = configurationContext(360, 640, 360, 1f, Locale.ENGLISH, false)
        val night = configurationContext(360, 640, 360, 1f, Locale.ENGLISH, true)
        assertNotEquals(
            day.getColor(R.color.opencc_window_background),
            night.getColor(R.color.opencc_window_background),
        )
        assertNotEquals(day.getColor(R.color.opencc_system_bar), night.getColor(R.color.opencc_system_bar))
    }

    private fun assertOrientationChangesPreserveEditorState(activity: OpenccActivity): OpenccActivity {
        onMain {
            activity.findViewById<EditText>(R.id.source_text).setText(ROTATION_SOURCE)
            activity.findViewById<TextView>(R.id.result_text).text = ROTATION_RESULT
            activity.findViewById<Spinner>(R.id.conversion_type).setSelection(ROTATION_TYPE_INDEX)
        }
        val originalOrientation = activity.resources.configuration.orientation
        val (oppositeRequest, oppositeOrientation) = if (originalOrientation == Configuration.ORIENTATION_LANDSCAPE) {
            ActivityInfo.SCREEN_ORIENTATION_PORTRAIT to Configuration.ORIENTATION_PORTRAIT
        } else {
            ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE to Configuration.ORIENTATION_LANDSCAPE
        }
        var recreated = requestOrientation(
            activity,
            oppositeRequest,
            oppositeOrientation,
        )
        assertRestoredRotationState(recreated)
        val restoreRequest = if (originalOrientation == Configuration.ORIENTATION_LANDSCAPE) {
            ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
        } else {
            ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
        }
        recreated = requestOrientation(
            recreated,
            restoreRequest,
            originalOrientation,
        )
        assertRestoredRotationState(recreated)
        return recreated
    }

    private fun requestOrientation(
        activity: OpenccActivity,
        requestedOrientation: Int,
        expectedOrientation: Int,
    ): OpenccActivity {
        val replacement = AtomicReference<OpenccActivity?>()
        val created = CountDownLatch(1)
        val callbacks = object : Application.ActivityLifecycleCallbacks {
            override fun onActivityCreated(candidate: Activity, state: Bundle?) {
                if (candidate is OpenccActivity && candidate !== activity) {
                    replacement.compareAndSet(null, candidate)
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
            onMain { activity.requestedOrientation = requestedOrientation }
            assertTrue("Timed out waiting for the requested orientation", created.await(20, TimeUnit.SECONDS))
            instrumentation.waitForIdleSync()
            return requireNotNull(replacement.get()).also { candidate ->
                assertEquals(expectedOrientation, candidate.resources.configuration.orientation)
            }
        } finally {
            activity.application.unregisterActivityLifecycleCallbacks(callbacks)
        }
    }

    private fun assertRestoredRotationState(activity: OpenccActivity) {
        assertEquals(ROTATION_SOURCE, readText(activity.findViewById(R.id.source_text)))
        assertEquals(ROTATION_RESULT, readText(activity.findViewById(R.id.result_text)))
        assertEquals(
            ROTATION_TYPE_INDEX,
            onMain { activity.findViewById<Spinner>(R.id.conversion_type).selectedItemPosition },
        )
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
        const val ARG_EXPECT_RTL = "opencc_expect_rtl"
        const val ARG_EXPECT_LARGE_FONT = "opencc_expect_large_font"
        const val ARG_EXPECT_NIGHT = "opencc_expect_night"
        const val ARABIC_SOURCE_LABEL = "النص المصدر"
        const val KEYBOARD_INPUT = "汉字软件 😀 𠀀"
        const val KEYBOARD_OUTPUT = "漢字軟件 😀 𠀀"
        const val LONG_TEXT_LINE = "汉字漢字 OpenCC 😀 𠀀 مرحبا\n"
        const val LONG_TEXT_REPETITIONS = 256
        const val ROTATION_SOURCE = "旋转与分屏 😀 𠀀 مرحبا"
        const val ROTATION_RESULT = "旋轉與分屏 😀 𠀀 مرحبا"
        const val ROTATION_TYPE_INDEX = 4
        const val MINIMUM_TOUCH_TARGET_DP = 48
        const val LARGE_FONT_SCALE = 1.5f
        const val SYNTHETIC_FONT_SCALE = 2f
        const val TIMEOUT_MILLIS = 60_000L
        const val POLL_INTERVAL_MILLIS = 50L
    }
}
