package io.github.supermonster003.autojs6.plugin.opencc

import android.app.Service
import android.content.Intent
import android.os.IBinder
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccConversionType
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccNativeEngine
import org.autojs.plugin.common.api.PluginInfo
import org.autojs.plugin.opencc.api.IOpenccPlugin
import org.autojs.plugin.opencc.api.OpenccConversionTypes
import org.autojs.plugin.opencc.api.OpenccPluginContract
import java.util.Locale

class OpenccPluginService : Service() {

    private val conversionLock = Any()
    private val engineDelegate = lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
        OpenccNativeEngine(applicationContext)
    }
    private val engine by engineDelegate

    override fun onBind(intent: Intent?): IBinder = binder

    override fun onDestroy() {
        if (engineDelegate.isInitialized()) {
            synchronized(conversionLock) {
                engine.close()
            }
        }
        super.onDestroy()
    }

    private val binder = object : IOpenccPlugin.Stub() {
        override fun getInfo(): PluginInfo {
            return pluginInfo(
                name = getString(R.string.app_name),
                description = getString(R.string.plugin_description),
            )
        }

        override fun convert(text: String?, conversionType: String?): String {
            val type = requireConversionType(conversionType)
            return synchronized(conversionLock) {
                convert(text.orEmpty(), type)
            }
        }

        override fun getSupportedConversionTypes(): MutableList<String> {
            return OpenccConversionTypes.ALL.toMutableList()
        }

        override fun convertBatch(
            texts: MutableList<String>?,
            conversionType: String?,
        ): MutableList<String> {
            val sourceTexts = texts.orEmpty()
            require(sourceTexts.size <= OpenccPluginContract.MAX_BATCH_SIZE) {
                "Conversion batch exceeds ${OpenccPluginContract.MAX_BATCH_SIZE} items"
            }
            val type = requireConversionType(conversionType)
            return synchronized(conversionLock) {
                sourceTexts.mapTo(mutableListOf()) { text ->
                    convert(text.orEmpty(), type)
                }
            }
        }

        override fun convertChain(
            text: String?,
            conversionTypes: MutableList<String>?,
        ): String {
            val typeNames = conversionTypes.orEmpty()
            require(typeNames.size <= OpenccPluginContract.MAX_CHAIN_LENGTH) {
                "Conversion chain exceeds ${OpenccPluginContract.MAX_CHAIN_LENGTH} stages"
            }
            val types = typeNames.map(::requireConversionType)
            return synchronized(conversionLock) {
                types.fold(text.orEmpty()) { converted, type ->
                    convert(converted, type)
                }
            }
        }
    }

    private fun requireConversionType(conversionType: String?): OpenccConversionType {
        val typeName = conversionType.orEmpty().trim().uppercase(Locale.US)
        return runCatching { OpenccConversionType.valueOf(typeName) }
            .getOrElse {
                throw IllegalArgumentException(
                    getString(R.string.error_unsupported_conversion_type, conversionType),
                    it,
                )
            }
    }

    private fun convert(text: String, conversionType: OpenccConversionType): String {
        return engine.convert(text, conversionType)
    }
}
