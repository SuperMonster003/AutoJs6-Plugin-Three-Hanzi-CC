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
        assertEquals("1.4.2", fields.openccVersion)
        assertEquals("025f371dc76b598d77384fbdab90c937471844d8", fields.openccCommit)
        assertEquals(
            "9ea0d303219b34d014d5c116677b5d325043beafb2c8a62ee889ca67f4d054a5",
            fields.openccResourceSha256,
        )
    }
}
