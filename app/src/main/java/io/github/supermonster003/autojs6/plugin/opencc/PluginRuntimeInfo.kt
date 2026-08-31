package io.github.supermonster003.autojs6.plugin.opencc

import android.content.Context
import android.os.Build
import org.autojs.plugin.common.api.PluginCapabilityKeys
import org.autojs.plugin.common.api.PluginInfo
import org.autojs.plugin.opencc.api.OpenccPluginIds

internal const val REQUIRED_HOST_VERSION = 3923

internal val SUPPORTED_ABIS = listOf(
    "arm64-v8a",
    "armeabi-v7a",
    "x86_64",
    "x86",
)

internal data class PluginRuntimeFields(
    val name: String,
    val description: String,
    val author: String,
    val id: String,
    val engine: String,
    val variant: String,
    val versionName: String,
    val versionCode: Long,
    val versionDate: String,
    val supportedAbis: List<String>,
    val requiredHostVersion: Int,
)

internal fun pluginRuntimeFields(
    name: String,
    description: String,
    author: String,
    id: String,
    engine: String,
    variant: String,
    versionName: String,
    versionCode: Long,
    versionDate: String,
): PluginRuntimeFields = PluginRuntimeFields(
    name = name,
    description = description,
    author = author,
    id = id,
    engine = engine,
    variant = variant,
    versionName = versionName,
    versionCode = versionCode,
    versionDate = versionDate,
    supportedAbis = SUPPORTED_ABIS,
    requiredHostVersion = REQUIRED_HOST_VERSION,
)

internal fun Context.pluginInfo(name: String, description: String): PluginInfo {
    val appContext = applicationContext
    val packageInfo = appContext.packageManager.getPackageInfo(appContext.packageName, 0)
    val fields = pluginRuntimeFields(
        name = name,
        description = description,
        author = appContext.stringResource("plugin_author", "SuperMonster003"),
        id = appContext.stringResource("plugin_id", OpenccPluginIds.ID),
        engine = appContext.stringResource("plugin_engine", OpenccPluginIds.ENGINE),
        variant = appContext.stringResource("plugin_variant", OpenccPluginIds.VARIANT_DEFAULT),
        versionName = packageInfo.versionName ?: "",
        versionCode = packageInfo.versionCodeCompat(),
        versionDate = appContext.stringResource("plugin_version_date", ""),
    )
    return PluginInfo().apply {
        this.name = fields.name
        this.description = fields.description
        author = fields.author
        id = fields.id
        engine = fields.engine
        variant = fields.variant
        versionName = fields.versionName
        versionCode = fields.versionCode
        versionDate = fields.versionDate
        supportedAbis = fields.supportedAbis.toTypedArray()
        capabilities = android.os.Bundle().apply {
            putInt(PluginCapabilityKeys.REQUIRES_HOST_VERSION, fields.requiredHostVersion)
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
