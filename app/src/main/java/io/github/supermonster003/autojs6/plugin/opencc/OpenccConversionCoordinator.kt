package io.github.supermonster003.autojs6.plugin.opencc

import android.content.Context
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccConversionType
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccNativeEngine
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccUpstream
import org.autojs.plugin.opencc.api.OpenccConversionTypes
import org.autojs.plugin.opencc.api.OpenccPluginContract
import java.util.Locale

/**
 * Process-scoped application layer shared by the Launcher UI and the Binder service.
 *
 * The native engine is initialized only by the first conversion. It intentionally lives for
 * the process lifetime so destroying one Android component cannot invalidate a conversion or
 * converter cache still in use by another entry point.
 */
internal class OpenccConversionCoordinator private constructor(context: Context) {

    private val applicationContext = context.applicationContext ?: context
    private val conversionLock = Any()
    private val engine by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
        OpenccNativeEngine(applicationContext)
    }

    val supportedConversionTypes: List<String>
        get() = OpenccConversionTypes.ALL

    val runtimeIdentity: OpenccRuntimeIdentity
        get() = OpenccRuntimeIdentity(
            version = OpenccUpstream.version(),
            commit = OpenccUpstream.commit(),
            resourceSha256 = OpenccUpstream.resourceSha256(),
        )

    fun convert(text: String?, conversionType: String?): String {
        return convert(text.orEmpty(), requireConversionType(conversionType))
    }

    fun convert(text: String, conversionType: OpenccConversionType): String {
        return synchronized(conversionLock) {
            engine.convert(text, conversionType)
        }
    }

    fun convertBatch(
        texts: List<String?>?,
        conversionType: String?,
    ): MutableList<String> {
        val sourceTexts = texts.orEmpty()
        require(sourceTexts.size <= OpenccPluginContract.MAX_BATCH_SIZE) {
            "Conversion batch exceeds ${OpenccPluginContract.MAX_BATCH_SIZE} items"
        }
        val type = requireConversionType(conversionType)
        return synchronized(conversionLock) {
            sourceTexts.mapTo(mutableListOf()) { text ->
                engine.convert(text.orEmpty(), type)
            }
        }
    }

    fun convertChain(
        text: String?,
        conversionTypes: List<String?>?,
    ): String {
        val typeNames = conversionTypes.orEmpty()
        require(typeNames.size <= OpenccPluginContract.MAX_CHAIN_LENGTH) {
            "Conversion chain exceeds ${OpenccPluginContract.MAX_CHAIN_LENGTH} stages"
        }
        val types = typeNames.map(::requireConversionType)
        return synchronized(conversionLock) {
            types.fold(text.orEmpty()) { converted, type ->
                engine.convert(converted, type)
            }
        }
    }

    private fun requireConversionType(conversionType: String?): OpenccConversionType {
        val typeName = conversionType.orEmpty().trim().uppercase(Locale.US)
        return runCatching { OpenccConversionType.valueOf(typeName) }
            .getOrElse {
                throw IllegalArgumentException(
                    applicationContext.getString(
                        R.string.error_unsupported_conversion_type,
                        conversionType,
                    ),
                    it,
                )
            }
    }

    internal companion object {
        @Volatile
        private var instance: OpenccConversionCoordinator? = null

        fun get(context: Context): OpenccConversionCoordinator {
            return instance ?: synchronized(this) {
                instance ?: OpenccConversionCoordinator(context).also { instance = it }
            }
        }
    }
}

internal data class OpenccRuntimeIdentity(
    val version: String,
    val commit: String,
    val resourceSha256: String,
)
