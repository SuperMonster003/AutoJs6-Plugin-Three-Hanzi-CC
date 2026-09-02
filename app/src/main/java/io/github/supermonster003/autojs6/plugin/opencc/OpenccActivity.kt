package io.github.supermonster003.autojs6.plugin.opencc

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Intent
import android.os.Bundle
import android.text.BidiFormatter
import android.text.Editable
import android.text.TextWatcher
import android.view.KeyEvent
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.Spinner
import android.widget.TextView
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccConversionType
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.Future

/** Launcher entry point for the standalone, fully offline OpenCC experience. */
class OpenccActivity : Activity() {

    private val coordinator by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
        OpenccConversionCoordinator.get(applicationContext)
    }
    private val conversionTypes = OpenccConversionType.values()
    private val conversionExecutor: ExecutorService = Executors.newSingleThreadExecutor { command ->
        Thread(command, "opencc-ui-conversion").apply { isDaemon = true }
    }

    private lateinit var sourceText: EditText
    private lateinit var conversionType: Spinner
    private lateinit var pasteButton: Button
    private lateinit var clearButton: Button
    private lateinit var convertButton: Button
    private lateinit var cancelButton: Button
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
            conversionType.setSelection(DEFAULT_TYPE_INDEX)
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
            }

            override fun onNothingSelected(parent: AdapterView<*>?) = Unit
        }

        pasteButton.setOnClickListener { pastePlainText() }
        clearButton.setOnClickListener { clearText() }
        convertButton.setOnClickListener { startConversion() }
        cancelButton.setOnClickListener { cancelConversion(announce = true) }
        copyButton.setOnClickListener { copyResult() }
        swapButton.setOnClickListener { swapText() }
        shareButton.setOnClickListener { shareResult() }
        updateActionAvailability()
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
        cancelConversion(announce = false)
        conversionExecutor.shutdownNow()
        super.onDestroy()
    }

    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        if (event.action == KeyEvent.ACTION_DOWN && event.keyCode == KeyEvent.KEYCODE_ENTER && event.isCtrlPressed) {
            if (activeConversion == null && convertButton.isEnabled) startConversion()
            return true
        }
        if (event.action == KeyEvent.ACTION_DOWN && event.keyCode == KeyEvent.KEYCODE_ESCAPE) {
            if (cancelConversion(announce = true)) return true
        }
        return super.dispatchKeyEvent(event)
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

    @Suppress("DEPRECATION")
    private fun applySystemBarInsets(root: View) {
        val initialLeft = root.paddingLeft
        val initialTop = root.paddingTop
        val initialRight = root.paddingRight
        val initialBottom = root.paddingBottom
        root.setOnApplyWindowInsetsListener { view, insets ->
            view.setPadding(
                initialLeft + insets.systemWindowInsetLeft,
                initialTop + insets.systemWindowInsetTop,
                initialRight + insets.systemWindowInsetRight,
                initialBottom + insets.systemWindowInsetBottom,
            )
            insets
        }
        root.requestApplyInsets()
    }

    private companion object {
        const val MIME_TYPE_PLAIN_TEXT = "text/plain"
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
