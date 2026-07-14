package io.github.supermonster003.autojs6.plugin.opencc

import android.app.Service
import android.content.Intent
import android.os.IBinder
import com.zqc.opencc.android.lib.ChineseConverter
import com.zqc.opencc.android.lib.ConversionType
import org.autojs.plugin.common.api.PluginInfo
import org.autojs.plugin.opencc.api.IOpenccPlugin
import java.util.Locale

class OpenccPluginService : Service() {

    override fun onBind(intent: Intent?): IBinder = binder

    private val binder = object : IOpenccPlugin.Stub() {
        override fun getInfo(): PluginInfo {
            return pluginInfo(
                name = "OpenCC",
                description = "OpenCC conversion provider.",
            )
        }

        override fun convert(text: String?, conversionType: String?): String {
            val typeName = conversionType.orEmpty().trim().uppercase(Locale.US)
            val type = runCatching { ConversionType.valueOf(typeName) }
                .getOrElse { throw IllegalArgumentException("Unsupported OpenCC conversion type: $conversionType", it) }
            return ChineseConverter.convert(text.orEmpty(), type, this@OpenccPluginService)
        }
    }
}
