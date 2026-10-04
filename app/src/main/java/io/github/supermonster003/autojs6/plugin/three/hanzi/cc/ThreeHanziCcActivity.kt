package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

import android.content.ActivityNotFoundException
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Intent
import android.content.res.ColorStateList
import android.os.Bundle
import android.text.BidiFormatter
import android.text.Editable
import android.text.TextWatcher
import android.view.KeyEvent
import android.view.Menu
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.ImageButton
import android.widget.PopupMenu
import android.widget.ProgressBar
import android.widget.Spinner
import android.widget.TextView
import com.google.android.material.button.MaterialButton
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.ui.Ui
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.ui.accentRipple
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.ui.accentTone
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.ui.applySystemBarInsets
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.ui.roundedFill
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.Future

/** Launcher entry point for the standalone, fully offline OpenCC experience. */
class ThreeHanziCcActivity : ConfiguredActivity() {

    private val coordinator by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
        OpenccConversionCoordinator.get(applicationContext)
    }
    private val conversionTypes = OpenccConversionType.values()
    private val conversionExecutor: ExecutorService = Executors.newSingleThreadExecutor { command ->
        Thread(command, "opencc-ui-conversion").apply { isDaemon = true }
    }
    private val uiPreferences by lazy { OpenccUiPreferences(this) }
    private val updateController by lazy { AppUpdateController(this, AppUpdateSettingsStore(this)) }

    private lateinit var sourceText: EditText
    private lateinit var conversionType: Spinner
    private lateinit var pasteButton: Button
    private lateinit var clearButton: Button
    private lateinit var convertButton: Button
    private lateinit var cancelButton: Button
    private lateinit var invertButton: Button
    private lateinit var overflowButton: ImageButton
    private lateinit var progress: ProgressBar
    private lateinit var resultText: TextView
    private lateinit var copyButton: Button
    private lateinit var swapButton: Button
    private lateinit var shareButton: Button
    private lateinit var statusText: TextView
    private var activeConversion: Future<*>? = null
    private var requestGeneration = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_opencc)

        val root = findViewById<View>(R.id.standalone_root)
        sourceText = findViewById(R.id.source_text)
        conversionType = findViewById(R.id.conversion_type)
        pasteButton = findViewById(R.id.paste_button)
        clearButton = findViewById(R.id.clear_button)
        convertButton = findViewById(R.id.convert_button)
        cancelButton = findViewById(R.id.cancel_button)
        invertButton = findViewById(R.id.invert_type_button)
        overflowButton = findViewById(R.id.overflow_menu_button)
        progress = findViewById(R.id.conversion_progress)
        resultText = findViewById(R.id.result_text)
        copyButton = findViewById(R.id.copy_button)
        swapButton = findViewById(R.id.swap_button)
        shareButton = findViewById(R.id.share_button)
        statusText = findViewById(R.id.conversion_status)

        applySystemBarInsets(root)
        conversionType.adapter = ArrayAdapter(
            this,
            R.layout.opencc_spinner_item,
            R.id.opencc_spinner_text,
            conversionTypes.map(::conversionTypeLabel),
        ).apply {
            setDropDownViewResource(R.layout.opencc_spinner_dropdown_item)
        }

        val identity = coordinator.runtimeIdentity
        findViewById<TextView>(R.id.runtime_identity).text = getString(
            R.string.standalone_runtime_identity,
            identity.version,
            identity.commit.take(12),
            identity.resourceSha256.take(12),
        )

        val restoredState = OpenccEditorState.fromBundle(
            savedInstanceState,
            conversionTypes.indices,
            DEFAULT_TYPE_INDEX,
        )
        if (restoredState != null) {
            sourceText.setText(restoredState.source)
            resultText.text = restoredState.result
            conversionType.setSelection(restoredState.typeIndex)
        } else {
            conversionType.setSelection(initialConversionTypeIndex())
        }

        sourceText.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(
                text: CharSequence?,
                start: Int,
                count: Int,
                after: Int,
            ) = Unit

            override fun onTextChanged(
                text: CharSequence?,
                start: Int,
                before: Int,
                count: Int,
            ) = Unit

            override fun afterTextChanged(text: Editable?) {
                if (activeConversion != null) cancelConversion(announce = true)
                updateActionAvailability()
            }
        })
        conversionType.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(
                parent: AdapterView<*>?,
                view: View?,
                position: Int,
                id: Long,
            ) {
                if (activeConversion != null) cancelConversion(announce = true)
                if (uiPreferences.rememberConversionType && position in conversionTypes.indices) {
                    uiPreferences.lastConversionTypeIndex = position
                }
            }

            override fun onNothingSelected(parent: AdapterView<*>?) = Unit
        }

        pasteButton.setOnClickListener { pastePlainText() }
        clearButton.setOnClickListener { clearText() }
        convertButton.setOnClickListener { startConversion() }
        cancelButton.setOnClickListener { cancelConversion(announce = true) }
        invertButton.setOnClickListener { invertConversionType() }
        overflowButton.setOnClickListener { showOverflowMenu(it) }
        copyButton.setOnClickListener { copyResult() }
        swapButton.setOnClickListener { swapText() }
        shareButton.setOnClickListener { shareResult() }

        applyPageStyling(root)
        updateActionAvailability()
        window.decorView.post { updateController.checkAutomaticallyIfDue() }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        OpenccEditorState(
            source = sourceText.text.toString(),
            result = resultText.text.toString(),
            typeIndex = conversionType.selectedItemPosition,
        ).writeTo(outState)
        super.onSaveInstanceState(outState)
    }

    override fun onDestroy() {
        updateController.cancel()
        cancelConversion(announce = false)
        conversionExecutor.shutdownNow()
        super.onDestroy()
    }

    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        if (event.keyCode == KeyEvent.KEYCODE_ENTER && event.isCtrlPressed) {
            if (event.action == KeyEvent.ACTION_DOWN && activeConversion == null && convertButton.isEnabled) {
                startConversion()
            }
            return true
        }
        if (event.action == KeyEvent.ACTION_DOWN && event.keyCode == KeyEvent.KEYCODE_ESCAPE) {
            if (cancelConversion(announce = true)) return true
        }
        return super.dispatchKeyEvent(event)
    }

    private fun applyPageStyling(root: View) {
        applyThemeToControls(root)
        val palette = appPalette

        findViewById<TextView>(R.id.standalone_title).apply {
            setTextColor(palette.primaryText)
            typeface = Ui.mediumTypeface
            textSize = Ui.TEXT_DISPLAY
        }
        findViewById<TextView>(R.id.standalone_subtitle).apply {
            setTextColor(palette.secondaryText)
            textSize = Ui.TEXT_BODY
            setLineSpacing(0f, Ui.LINE_SPACING_BODY)
        }
        listOf(R.id.source_text_label, R.id.conversion_type_label, R.id.result_text_label).forEach { labelId ->
            findViewById<TextView>(labelId).apply {
                setTextColor(palette.secondaryText)
                typeface = Ui.mediumTypeface
                textSize = Ui.TEXT_SECTION
                letterSpacing = 0.05f
            }
        }
        statusText.setTextColor(palette.secondaryText)
        statusText.textSize = Ui.TEXT_BODY
        findViewById<TextView>(R.id.runtime_identity).apply {
            setTextColor(AppColorPolicy.withAlpha(palette.secondaryText, 0xCC))
            textSize = Ui.TEXT_CAPTION
        }

        styleEditorSurface(sourceText)
        styleEditorSurface(resultText)
        listOf<TextView>(sourceText, resultText).forEach { editor ->
            editor.setTextColor(palette.primaryText)
            editor.setHintTextColor(AppColorPolicy.withAlpha(palette.secondaryText, 0xA6))
        }

        conversionType.backgroundTintList = ColorStateList.valueOf(palette.secondaryText)
        conversionType.setPopupBackgroundDrawable(
            roundedFill(palette.surface, Ui.RADIUS_CONTROL, palette.outline),
        )

        overflowButton.imageTintList = ColorStateList.valueOf(palette.secondaryText)

        styleFilledButton(convertButton)
        listOf(pasteButton, clearButton, cancelButton, copyButton, swapButton, shareButton)
            .forEach(::styleTonalButton)
        styleTextButton(invertButton)
    }

    private fun styleEditorSurface(editor: TextView) {
        fun refresh() {
            editor.background = roundedFill(
                appPalette.surface,
                Ui.RADIUS_CARD,
                if (editor.isFocused) appPalette.accent else appPalette.outline,
            )
            editor.backgroundTintList = null
        }
        refresh()
        editor.setOnFocusChangeListener { _, _ -> refresh() }
    }

    private fun styleFilledButton(button: Button) {
        val palette = appPalette
        styleActionButton(
            button,
            fill = enabledStateColors(palette.primary, AppColorPolicy.withAlpha(palette.secondaryText, 0x1F)),
            text = enabledStateColors(palette.onPrimary, AppColorPolicy.withAlpha(palette.secondaryText, 0x99)),
            rippleColor = accentRipple(palette.onPrimary),
        )
    }

    private fun styleTonalButton(button: Button) {
        val palette = appPalette
        styleActionButton(
            button,
            fill = enabledStateColors(accentTone(palette.accent), AppColorPolicy.withAlpha(palette.secondaryText, 0x14)),
            text = enabledStateColors(palette.accent, AppColorPolicy.withAlpha(palette.secondaryText, 0x77)),
            rippleColor = accentRipple(palette.accent),
        )
    }

    private fun styleTextButton(button: Button) {
        val palette = appPalette
        styleActionButton(
            button,
            fill = ColorStateList.valueOf(0x00000000),
            text = enabledStateColors(palette.accent, AppColorPolicy.withAlpha(palette.secondaryText, 0x77)),
            rippleColor = accentRipple(palette.accent),
        )
    }

    private fun styleActionButton(button: Button, fill: ColorStateList, text: ColorStateList, rippleColor: Int) {
        button.setTextColor(text)
        button.typeface = Ui.mediumTypeface
        button.textSize = Ui.TEXT_BODY
        button.backgroundTintList = fill
        if (button is MaterialButton) {
            button.cornerRadius = uiDp(Ui.RADIUS_CONTROL)
            button.rippleColor = ColorStateList.valueOf(rippleColor)
            button.strokeWidth = 0
        }
    }

    private fun enabledStateColors(enabled: Int, disabled: Int) = ColorStateList(
        arrayOf(intArrayOf(-android.R.attr.state_enabled), intArrayOf()),
        intArrayOf(disabled, enabled),
    )

    private fun initialConversionTypeIndex(): Int {
        if (!uiPreferences.rememberConversionType) return DEFAULT_TYPE_INDEX
        return uiPreferences.lastConversionTypeIndex.takeIf { it in conversionTypes.indices } ?: DEFAULT_TYPE_INDEX
    }

    private fun invertConversionType() {
        cancelConversion(announce = false)
        val currentIndex = conversionType.selectedItemPosition
            .takeIf { it in conversionTypes.indices }
            ?: DEFAULT_TYPE_INDEX
        val inverted = inverseConversionType(conversionTypes[currentIndex])
        conversionType.setSelection(conversionTypes.indexOf(inverted))
    }

    private fun inverseConversionType(type: OpenccConversionType): OpenccConversionType = when (type) {
        OpenccConversionType.S2T -> OpenccConversionType.T2S
        OpenccConversionType.T2S -> OpenccConversionType.S2T
        OpenccConversionType.S2TW -> OpenccConversionType.TW2S
        OpenccConversionType.TW2S -> OpenccConversionType.S2TW
        OpenccConversionType.S2TWP -> OpenccConversionType.TW2SP
        OpenccConversionType.TW2SP -> OpenccConversionType.S2TWP
        OpenccConversionType.S2HK -> OpenccConversionType.HK2S
        OpenccConversionType.HK2S -> OpenccConversionType.S2HK
        OpenccConversionType.T2TW -> OpenccConversionType.TW2T
        OpenccConversionType.TW2T -> OpenccConversionType.T2TW
        OpenccConversionType.T2HK -> OpenccConversionType.HK2T
        OpenccConversionType.HK2T -> OpenccConversionType.T2HK
        OpenccConversionType.T2JP -> OpenccConversionType.JP2T
        OpenccConversionType.JP2T -> OpenccConversionType.T2JP
    }

    private fun showOverflowMenu(anchor: View) {
        PopupMenu(this, anchor).apply {
            menu.add(Menu.NONE, MENU_ITEM_SETTINGS, Menu.NONE, R.string.standalone_menu_settings)
            setOnMenuItemClickListener { item ->
                when (item.itemId) {
                    MENU_ITEM_SETTINGS -> {
                        startActivity(Intent(this@ThreeHanziCcActivity, AppSettingsActivity::class.java))
                        true
                    }
                    else -> false
                }
            }
            show()
        }
    }

    private fun startConversion() {
        if (activeConversion != null) return

        val source = sourceText.text.toString()
        if (source.isEmpty()) {
            statusText.setText(R.string.standalone_status_no_source)
            return
        }
        val typeIndex = conversionType.selectedItemPosition
            .takeIf { it in conversionTypes.indices }
            ?: DEFAULT_TYPE_INDEX
        val type = conversionTypes[typeIndex]
        val generation = ++requestGeneration

        setConverting(true)
        activeConversion = conversionExecutor.submit {
            val outcome: Result<String> = try {
                Result.success(coordinator.convert(source, type))
            } catch (error: Exception) {
                Result.failure(error)
            }
            runOnUiThread {
                if (isDestroyed || generation != requestGeneration) return@runOnUiThread
                activeConversion = null
                outcome.fold(
                    onSuccess = { converted ->
                        resultText.text = converted
                        statusText.setText(R.string.standalone_status_complete)
                    },
                    onFailure = { error ->
                        statusText.text = getString(
                            R.string.standalone_status_failed,
                            error.message ?: getString(R.string.standalone_error_unknown),
                        )
                    },
                )
                setConverting(false)
            }
        }
    }

    private fun cancelConversion(announce: Boolean): Boolean {
        val conversion = activeConversion ?: return false
        requestGeneration += 1
        activeConversion = null
        conversion.cancel(true)
        setConverting(false)
        if (announce) statusText.setText(R.string.standalone_status_canceled)
        return true
    }

    private fun pastePlainText() {
        cancelConversion(announce = false)
        val clipboard = getSystemService(ClipboardManager::class.java)
        val clip = clipboard.primaryClip
        val text = clip
            ?.takeIf { it.itemCount > 0 }
            ?.getItemAt(0)
            ?.text
        if (text == null) {
            statusText.setText(R.string.standalone_status_clipboard_has_no_text)
            return
        }
        sourceText.setText(text)
        sourceText.setSelection(sourceText.text.length)
        statusText.setText(R.string.standalone_status_pasted)
    }

    private fun clearText() {
        cancelConversion(announce = false)
        sourceText.text.clear()
        resultText.text = ""
        statusText.setText(R.string.standalone_status_cleared)
        updateActionAvailability()
    }

    private fun copyResult() {
        val result = resultText.text.toString()
        if (result.isEmpty()) return
        val clipboard = getSystemService(ClipboardManager::class.java)
        clipboard.setPrimaryClip(
            ClipData.newPlainText(getString(R.string.standalone_result_label), result),
        )
        statusText.setText(R.string.standalone_status_copied)
    }

    private fun swapText() {
        cancelConversion(announce = false)
        val source = sourceText.text.toString()
        val result = resultText.text.toString()
        sourceText.setText(result)
        sourceText.setSelection(sourceText.text.length)
        resultText.text = source
        statusText.setText(R.string.standalone_status_swapped)
        updateActionAvailability()
    }

    private fun shareResult() {
        val result = resultText.text.toString()
        if (result.isEmpty()) return
        try {
            startActivity(createShareChooserIntent(result))
            statusText.setText(R.string.standalone_status_share_opened)
        } catch (_: ActivityNotFoundException) {
            statusText.setText(R.string.standalone_status_share_unavailable)
        }
    }

    internal fun createShareChooserIntent(text: String): Intent {
        val sendIntent = Intent(Intent.ACTION_SEND)
            .setType(MIME_TYPE_PLAIN_TEXT)
            .putExtra(Intent.EXTRA_TEXT, text)
        return Intent.createChooser(sendIntent, getString(R.string.standalone_share_chooser_title))
    }

    private fun setConverting(converting: Boolean) {
        convertButton.isEnabled = !converting
        cancelButton.visibility = if (converting) View.VISIBLE else View.GONE
        progress.visibility = if (converting) View.VISIBLE else View.GONE
        if (converting) statusText.setText(R.string.standalone_status_converting)
        updateActionAvailability()
    }

    private fun updateActionAvailability() {
        val hasSource = sourceText.text.isNotEmpty()
        val hasResult = resultText.text.isNotEmpty()
        clearButton.isEnabled = hasSource || hasResult || activeConversion != null
        copyButton.isEnabled = hasResult
        swapButton.isEnabled = hasSource || hasResult
        shareButton.isEnabled = hasResult
    }

    private fun conversionTypeLabel(type: OpenccConversionType): String {
        val (sourceResource, resultResource) = when (type) {
            OpenccConversionType.HK2S ->
                R.string.standalone_script_hong_kong_traditional to
                    R.string.standalone_script_simplified_chinese
            OpenccConversionType.HK2T ->
                R.string.standalone_script_hong_kong_traditional to
                    R.string.standalone_script_traditional_chinese
            OpenccConversionType.JP2T ->
                R.string.standalone_script_japanese_shinjitai to
                    R.string.standalone_script_traditional_old_forms
            OpenccConversionType.S2HK ->
                R.string.standalone_script_simplified_chinese to
                    R.string.standalone_script_hong_kong_traditional
            OpenccConversionType.S2T ->
                R.string.standalone_script_simplified_chinese to
                    R.string.standalone_script_traditional_chinese
            OpenccConversionType.S2TW, OpenccConversionType.S2TWP ->
                R.string.standalone_script_simplified_chinese to
                    R.string.standalone_script_taiwan_traditional
            OpenccConversionType.T2HK ->
                R.string.standalone_script_traditional_chinese to
                    R.string.standalone_script_hong_kong_traditional
            OpenccConversionType.T2S ->
                R.string.standalone_script_traditional_chinese to
                    R.string.standalone_script_simplified_chinese
            OpenccConversionType.T2TW ->
                R.string.standalone_script_traditional_chinese to
                    R.string.standalone_script_taiwan_traditional
            OpenccConversionType.T2JP ->
                R.string.standalone_script_traditional_old_forms to
                    R.string.standalone_script_japanese_shinjitai
            OpenccConversionType.TW2S, OpenccConversionType.TW2SP ->
                R.string.standalone_script_taiwan_traditional to
                    R.string.standalone_script_simplified_chinese
            OpenccConversionType.TW2T ->
                R.string.standalone_script_taiwan_traditional to
                    R.string.standalone_script_traditional_chinese
        }
        val bidi = BidiFormatter.getInstance()
        val source = bidi.unicodeWrap(getString(sourceResource))
        val result = bidi.unicodeWrap(getString(resultResource))
        val code = bidi.unicodeWrap(type.name)
        val terminologyResource = when (type) {
            OpenccConversionType.S2TWP -> R.string.standalone_terminology_taiwan
            OpenccConversionType.TW2SP -> R.string.standalone_terminology_mainland
            else -> null
        }
        return if (terminologyResource == null) {
            getString(R.string.standalone_conversion_direction, source, result, code)
        } else {
            getString(
                R.string.standalone_conversion_direction_with_terminology,
                source,
                result,
                bidi.unicodeWrap(getString(terminologyResource)),
                code,
            )
        }
    }

    private companion object {
        const val MIME_TYPE_PLAIN_TEXT = "text/plain"
        const val MENU_ITEM_SETTINGS = 1
        val DEFAULT_TYPE_INDEX = OpenccConversionType.values().indexOf(OpenccConversionType.S2T)
    }
}

/** Minimal editor state that Android may serialize when recreating the Activity in a new process. */
internal data class OpenccEditorState(
    val source: String,
    val result: String,
    val typeIndex: Int,
) {
    fun writeTo(bundle: Bundle) {
        bundle.putString(STATE_SOURCE, source)
        bundle.putString(STATE_RESULT, result)
        bundle.putInt(STATE_TYPE_INDEX, typeIndex)
    }

    companion object {
        private const val STATE_SOURCE = "opencc.source"
        private const val STATE_RESULT = "opencc.result"
        private const val STATE_TYPE_INDEX = "opencc.type.index"

        fun fromBundle(bundle: Bundle?, validTypeIndices: IntRange, defaultTypeIndex: Int): OpenccEditorState? {
            if (bundle == null) return null
            return OpenccEditorState(
                source = bundle.getString(STATE_SOURCE).orEmpty(),
                result = bundle.getString(STATE_RESULT).orEmpty(),
                typeIndex = bundle.getInt(STATE_TYPE_INDEX, defaultTypeIndex).coerceIn(validTypeIndices),
            )
        }
    }
}
