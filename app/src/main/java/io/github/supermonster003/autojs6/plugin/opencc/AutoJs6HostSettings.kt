package io.github.supermonster003.autojs6.plugin.opencc

import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build

/**
 * AutoJs6's versioned, read-only official-plugin settings contract, inlined because the bundled
 * `common-plugin-api` artifact of this plugin predates the contract's publication. Keys and values
 * mirror `org.autojs.plugin.common.api.AutoJs6HostSettingsContract` verbatim.
 */
internal object AutoJs6HostSettingsContract {
    const val HOST_PACKAGE_NAME = "org.autojs.autojs6"
    const val CONTENT_URI = "content://org.autojs.autojs6.plugin.settings"
    const val METHOD_GET_SETTINGS = "getSettings"
    const val PROTOCOL_VERSION = 1
    const val KEY_PROTOCOL_VERSION = "protocolVersion"
    const val KEY_HOST_PACKAGE_NAME = "hostPackageName"
    const val KEY_HOST_VERSION_CODE = "hostVersionCode"
    const val KEY_HOST_VERSION_NAME = "hostVersionName"
    const val KEY_THEME_COLOR_PRIMARY = "themeColorPrimary"
    const val KEY_THEME_COLOR_PRIMARY_DARK = "themeColorPrimaryDark"
    const val KEY_THEME_COLOR_ACCENT = "themeColorAccent"
    const val KEY_DARK_MODE_POLICY = "darkModePolicy"
    const val KEY_DARK_MODE_ACTIVE = "darkModeActive"
    const val KEY_LANGUAGE_TAG = "languageTag"
    const val KEY_RESOLVED_LANGUAGE_TAG = "resolvedLanguageTag"
}

internal enum class AutoJs6HostAvailability {
    AVAILABLE,
    NOT_INSTALLED,
    DISABLED,
    CONTRACT_UNAVAILABLE,
}

internal enum class AutoJs6DarkModePolicy {
    FOLLOW_SYSTEM,
    LIGHT,
    DARK,
}

internal data class AutoJs6HostSettingsSnapshot(
    val hostVersionCode: Long,
    val hostVersionName: String,
    val themeColorPrimary: Int,
    val themeColorPrimaryDark: Int,
    val themeColorAccent: Int,
    val darkModePolicy: AutoJs6DarkModePolicy,
    val darkModeActive: Boolean,
    val languageTag: String,
    val resolvedLanguageTag: String,
)

internal data class AutoJs6HostSettingsResult(
    val availability: AutoJs6HostAvailability,
    val snapshot: AutoJs6HostSettingsSnapshot? = null,
) {
    init {
        require((availability == AutoJs6HostAvailability.AVAILABLE) == (snapshot != null))
    }

    val selectable: Boolean
        get() = availability == AutoJs6HostAvailability.AVAILABLE

    val definitiveAbsence: Boolean
        get() = availability == AutoJs6HostAvailability.NOT_INSTALLED ||
            availability == AutoJs6HostAvailability.DISABLED
}

/** Client for AutoJs6's versioned, read-only official-plugin settings contract. */
internal object AutoJs6HostSettingsClient {
    private val settingsUri = Uri.parse(AutoJs6HostSettingsContract.CONTENT_URI)

    fun query(context: Context): AutoJs6HostSettingsResult {
        val installed = inspectHostPackage(context)
        if (installed != AutoJs6HostAvailability.AVAILABLE) {
            return AutoJs6HostSettingsResult(installed)
        }
        val bundle = runCatching {
            context.contentResolver.call(
                settingsUri,
                AutoJs6HostSettingsContract.METHOD_GET_SETTINGS,
                null,
                null,
            )
        }.getOrNull() ?: return AutoJs6HostSettingsResult(
            AutoJs6HostAvailability.CONTRACT_UNAVAILABLE,
        )
        val snapshot = runCatching {
            require(
                bundle.getInt(AutoJs6HostSettingsContract.KEY_PROTOCOL_VERSION, 0) ==
                    AutoJs6HostSettingsContract.PROTOCOL_VERSION,
            )
            require(
                bundle.getString(AutoJs6HostSettingsContract.KEY_HOST_PACKAGE_NAME) ==
                    AutoJs6HostSettingsContract.HOST_PACKAGE_NAME,
            )
            require(bundle.containsKey(AutoJs6HostSettingsContract.KEY_THEME_COLOR_PRIMARY))
            require(bundle.containsKey(AutoJs6HostSettingsContract.KEY_THEME_COLOR_PRIMARY_DARK))
            require(bundle.containsKey(AutoJs6HostSettingsContract.KEY_THEME_COLOR_ACCENT))
            AutoJs6HostSettingsSnapshot(
                hostVersionCode = bundle.getLong(
                    AutoJs6HostSettingsContract.KEY_HOST_VERSION_CODE,
                    0L,
                ),
                hostVersionName = bundle.getString(
                    AutoJs6HostSettingsContract.KEY_HOST_VERSION_NAME,
                ).orEmpty(),
                themeColorPrimary = bundle.getInt(
                    AutoJs6HostSettingsContract.KEY_THEME_COLOR_PRIMARY,
                ),
                themeColorPrimaryDark = bundle.getInt(
                    AutoJs6HostSettingsContract.KEY_THEME_COLOR_PRIMARY_DARK,
                ),
                themeColorAccent = bundle.getInt(
                    AutoJs6HostSettingsContract.KEY_THEME_COLOR_ACCENT,
                ),
                darkModePolicy = AutoJs6DarkModePolicy.valueOf(
                    bundle.getString(AutoJs6HostSettingsContract.KEY_DARK_MODE_POLICY).orEmpty(),
                ),
                darkModeActive = bundle.getBoolean(
                    AutoJs6HostSettingsContract.KEY_DARK_MODE_ACTIVE,
                ),
                languageTag = bundle.getString(
                    AutoJs6HostSettingsContract.KEY_LANGUAGE_TAG,
                ).orEmpty(),
                resolvedLanguageTag = bundle.getString(
                    AutoJs6HostSettingsContract.KEY_RESOLVED_LANGUAGE_TAG,
                ).orEmpty(),
            )
        }.getOrNull() ?: return AutoJs6HostSettingsResult(
            AutoJs6HostAvailability.CONTRACT_UNAVAILABLE,
        )
        return AutoJs6HostSettingsResult(AutoJs6HostAvailability.AVAILABLE, snapshot)
    }

    private fun inspectHostPackage(context: Context): AutoJs6HostAvailability {
        val packageManager = context.packageManager
        val applicationInfo = runCatching {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                packageManager.getApplicationInfo(
                    AutoJs6HostSettingsContract.HOST_PACKAGE_NAME,
                    PackageManager.ApplicationInfoFlags.of(
                        PackageManager.MATCH_DISABLED_COMPONENTS.toLong(),
                    ),
                )
            } else {
                @Suppress("DEPRECATION")
                packageManager.getApplicationInfo(
                    AutoJs6HostSettingsContract.HOST_PACKAGE_NAME,
                    PackageManager.MATCH_DISABLED_COMPONENTS,
                )
            }
        }.getOrNull() ?: return AutoJs6HostAvailability.NOT_INSTALLED
        val enabled = when (
            packageManager.getApplicationEnabledSetting(
                AutoJs6HostSettingsContract.HOST_PACKAGE_NAME,
            )
        ) {
            PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
            PackageManager.COMPONENT_ENABLED_STATE_DISABLED_UNTIL_USED,
            PackageManager.COMPONENT_ENABLED_STATE_DISABLED_USER,
            -> false
            PackageManager.COMPONENT_ENABLED_STATE_ENABLED -> true
            else -> applicationInfo.enabled
        }
        return if (enabled) AutoJs6HostAvailability.AVAILABLE else AutoJs6HostAvailability.DISABLED
    }
}
