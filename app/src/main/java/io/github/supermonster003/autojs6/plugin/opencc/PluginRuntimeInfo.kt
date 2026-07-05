package io.github.supermonster003.autojs6.plugin.opencc

import android.content.Context
import android.os.Build
import org.autojs.plugin.common.api.PluginCapabilityKeys
import org.autojs.plugin.common.api.PluginInfo
import org.autojs.plugin.opencc.api.OpenccPluginIds

internal fun Context.pluginInfo(name: String, description: String): PluginInfo {
    val appContext = applicationContext
    val packageInfo = appContext.packageManager.getPackageInfo(appContext.packageName, 0)
    return PluginInfo().apply {
        this.name = name
        this.description = description
        author = appContext.stringResource("plugin_author", "SuperMonster003")
        id = appContext.stringResource("plugin_id", OpenccPluginIds.ID)
        engine = appContext.stringResource("plugin_engine", OpenccPluginIds.ENGINE)
        variant = appContext.stringResource("plugin_variant", OpenccPluginIds.VARIANT_DEFAULT)
        versionName = packageInfo.versionName ?: ""
        versionCode = packageInfo.versionCodeCompat()
        versionDate = appContext.stringResource("plugin_version_date", "")
        supportedAbis = emptyArray()
        capabilities = android.os.Bundle().apply {
            putInt(PluginCapabilityKeys.REQUIRES_HOST_VERSION, 3923)
        }
    }
}

private fun Context.stringResource(name: String, fallback: String): String {
    val id = resources.getIdentifier(name, "string", packageName)
    return if (id != 0) resources.getString(id) else fallback
}

private fun android.content.pm.PackageInfo.versionCodeCompat(): Long {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) return longVersionCode
    @Suppress("DEPRECATION")
    return versionCode.toLong()
}
