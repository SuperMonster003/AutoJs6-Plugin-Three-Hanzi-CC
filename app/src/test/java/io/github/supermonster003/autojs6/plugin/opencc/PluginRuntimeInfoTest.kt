package io.github.supermonster003.autojs6.plugin.opencc

import org.autojs.plugin.opencc.api.OpenccPluginIds
import org.autojs.plugin.opencc.api.OpenccConversionTypes
import org.autojs.plugin.opencc.api.OpenccPluginContract
import org.junit.Assert.assertEquals
import org.junit.Test

class PluginRuntimeInfoTest {

    @Test
    fun runtimeFieldsPreservePackageMetadataAndCompatibilityContract() {
        val fields = pluginRuntimeFields(
            name = "OpenCC",
            description = "OpenCC test description",
            author = "SuperMonster003",
            id = OpenccPluginIds.ID,
            engine = OpenccPluginIds.ENGINE,
            variant = OpenccPluginIds.VARIANT_DEFAULT,
            versionName = "1.1.0",
            versionCode = 18,
            versionDate = "Aug 31, 2026",
        )

        assertEquals("OpenCC", fields.name)
        assertEquals("OpenCC test description", fields.description)
        assertEquals("@raw/plugin_instruction", fields.instruction)
        assertEquals("SuperMonster003", fields.author)
        assertEquals(OpenccPluginIds.ID, fields.id)
        assertEquals(OpenccPluginIds.ENGINE, fields.engine)
        assertEquals(OpenccPluginIds.VARIANT_DEFAULT, fields.variant)
        assertEquals("1.1.0", fields.versionName)
        assertEquals(18, fields.versionCode)
        assertEquals("Aug 31, 2026", fields.versionDate)
        assertEquals(
            listOf("arm64-v8a", "armeabi-v7a", "x86_64", "x86"),
            fields.supportedAbis,
        )
        assertEquals(3923, fields.requiredHostVersion)
        assertEquals(OpenccPluginContract.VERSION_CURRENT, fields.contractVersion)
        assertEquals(OpenccConversionTypes.ALL, fields.supportedConversionTypes)
    }
}
