package io.github.supermonster003.autojs6.plugin.opencc

import android.app.Service
import android.content.Intent
import android.os.IBinder
import org.autojs.plugin.common.api.PluginInfo
import org.autojs.plugin.opencc.api.IOpenccPlugin

class OpenccPluginService : Service() {

    private val coordinator by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
        OpenccConversionCoordinator.get(applicationContext)
    }

    override fun onBind(intent: Intent?): IBinder = binder

    private val binder = object : IOpenccPlugin.Stub() {
        override fun getInfo(): PluginInfo {
            return pluginInfo(
                name = getString(R.string.app_name),
                description = getString(R.string.plugin_description),
            )
        }

        override fun convert(text: String?, conversionType: String?): String {
            return coordinator.convert(text, conversionType)
        }

        override fun getSupportedConversionTypes(): MutableList<String> {
            return coordinator.supportedConversionTypes.toMutableList()
        }

        override fun convertBatch(
            texts: MutableList<String>?,
            conversionType: String?,
        ): MutableList<String> {
            return coordinator.convertBatch(texts, conversionType)
        }

        override fun convertChain(
            text: String?,
            conversionTypes: MutableList<String>?,
        ): String {
            return coordinator.convertChain(text, conversionTypes)
        }
    }
}
