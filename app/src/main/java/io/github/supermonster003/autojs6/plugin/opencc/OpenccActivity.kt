package io.github.supermonster003.autojs6.plugin.opencc

import android.app.Activity
import android.os.Bundle
import android.view.View
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

/** Desktop entry point for the standalone, fully offline OpenCC experience. */
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
    private lateinit var convertButton: Button
    private lateinit var progress: ProgressBar
    private lateinit var resultText: TextView
    private lateinit var statusText: TextView
    private var activeConversion: Future<*>? = null
    private var requestGeneration = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_opencc)

        val root = findViewById<View>(R.id.standalone_root)
        sourceText = findViewById(R.id.source_text)
        conversionType = findViewById(R.id.conversion_type)
        convertButton = findViewById(R.id.convert_button)
        progress = findViewById(R.id.conversion_progress)
        resultText = findViewById(R.id.result_text)
        statusText = findViewById(R.id.conversion_status)

        applySystemBarInsets(root)
        conversionType.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_item,
            conversionTypes.map { it.name },
        ).apply {
            setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        }

        val identity = coordinator.runtimeIdentity
        findViewById<TextView>(R.id.runtime_identity).text = getString(
            R.string.standalone_runtime_identity,
            identity.version,
            identity.commit.take(12),
            identity.resourceSha256.take(12),
        )

        if (savedInstanceState != null) {
            sourceText.setText(savedInstanceState.getString(STATE_SOURCE).orEmpty())
            resultText.text = savedInstanceState.getString(STATE_RESULT).orEmpty()
            conversionType.setSelection(
                savedInstanceState.getInt(STATE_TYPE_INDEX, DEFAULT_TYPE_INDEX)
                    .coerceIn(conversionTypes.indices),
            )
        } else {
            conversionType.setSelection(DEFAULT_TYPE_INDEX)
        }

        convertButton.setOnClickListener { startConversion() }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        outState.putString(STATE_SOURCE, sourceText.text.toString())
        outState.putString(STATE_RESULT, resultText.text.toString())
        outState.putInt(STATE_TYPE_INDEX, conversionType.selectedItemPosition)
        super.onSaveInstanceState(outState)
    }

    override fun onDestroy() {
        requestGeneration += 1
        activeConversion?.cancel(true)
        conversionExecutor.shutdownNow()
        super.onDestroy()
    }

    private fun startConversion() {
        val source = sourceText.text.toString()
        val type = conversionTypes[conversionType.selectedItemPosition]
        val generation = ++requestGeneration

        activeConversion?.cancel(false)
        setConverting(true)
        activeConversion = conversionExecutor.submit {
            val outcome = runCatching { coordinator.convert(source, type) }
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

    private fun setConverting(converting: Boolean) {
        convertButton.isEnabled = !converting
        progress.visibility = if (converting) View.VISIBLE else View.GONE
        if (converting) statusText.setText(R.string.standalone_status_converting)
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
        const val STATE_SOURCE = "opencc.source"
        const val STATE_RESULT = "opencc.result"
        const val STATE_TYPE_INDEX = "opencc.type.index"
        val DEFAULT_TYPE_INDEX = OpenccConversionType.values().indexOf(OpenccConversionType.S2T)
    }
}
