package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

import android.app.Service
import android.content.Intent
import android.os.IBinder
import org.autojs.plugin.common.api.IPluginInfoProvider

/** Common metadata entry for host discovery and appearance access; keeps conversion lazy. */
class ThreeHanziCcInfoService : Service() {
    private val binder = object : IPluginInfoProvider.Stub() {
        override fun getInfo() = pluginInfo(
            name = getString(R.string.app_name),
            description = getString(R.string.plugin_description),
        )
    }

    override fun onBind(intent: Intent?): IBinder = binder
}
