package io.github.supermonster003.autojs6.plugin.opencc

import android.content.Context

/**
 * Main-screen UI preferences. Deliberately separate from [ApplicationSettingsStore]: these values
 * must not bump the settings revision, which would recreate resumed activities for no visible
 * change.
 */
internal class OpenccUiPreferences(context: Context) {
    private val preferences = context.applicationContext.getSharedPreferences(
        PREFERENCES_NAME,
        Context.MODE_PRIVATE,
    )

    var rememberConversionType: Boolean
        get() = preferences.getBoolean(KEY_REMEMBER_CONVERSION_TYPE, true)
        set(value) {
            preferences.edit().putBoolean(KEY_REMEMBER_CONVERSION_TYPE, value).apply()
        }

    /** Spinner position of the most recently chosen conversion type, or -1 when never set. */
    var lastConversionTypeIndex: Int
        get() = preferences.getInt(KEY_LAST_CONVERSION_TYPE_INDEX, -1)
        set(value) {
            preferences.edit().putInt(KEY_LAST_CONVERSION_TYPE_INDEX, value).apply()
        }

    private companion object {
        const val PREFERENCES_NAME = "opencc-ui-settings"
        const val KEY_REMEMBER_CONVERSION_TYPE = "remember-conversion-type"
        const val KEY_LAST_CONVERSION_TYPE_INDEX = "last-conversion-type-index"
    }
}
