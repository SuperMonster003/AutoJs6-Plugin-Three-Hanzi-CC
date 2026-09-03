package io.github.supermonster003.autojs6.plugin.opencc

import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccUpstream
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
            versionName = "1.2.0",
            versionCode = 19,
            versionDate = "Sep 1, 2026",
        )

        assertEquals("OpenCC", fields.name)
        assertEquals("OpenCC test description", fields.description)
        assertEquals("@raw/plugin_instruction", fields.instruction)
        assertEquals("SuperMonster003", fields.author)
        assertEquals(OpenccPluginIds.ID, fields.id)
        assertEquals(OpenccPluginIds.ENGINE, fields.engine)
        assertEquals(OpenccPluginIds.VARIANT_DEFAULT, fields.variant)
        assertEquals("1.2.0", fields.versionName)
        assertEquals(19, fields.versionCode)
        assertEquals("Sep 1, 2026", fields.versionDate)
        assertEquals(
            listOf("arm64-v8a", "armeabi-v7a", "x86_64", "x86"),
            fields.supportedAbis,
        )
        assertEquals(3923, fields.requiredHostVersion)
        assertEquals(OpenccPluginContract.VERSION_CURRENT, fields.contractVersion)
        assertEquals(OpenccConversionTypes.ALL, fields.supportedConversionTypes)
        val controlledAcceptance = OpenccUpstream.isControlledAcceptance()
        val expectedVersion = if (controlledAcceptance) "999.4.2" else "1.4.2"
        val expectedTag = if (controlledAcceptance) "controlled-ver.999.4.2" else "ver.1.4.2"
        val expectedCommit = if (controlledAcceptance) {
            "b8bf091a83e7b318945352a8298127ecd0158643"
        } else {
            "025f371dc76b598d77384fbdab90c937471844d8"
        }
        val expectedResourceSha256 = if (controlledAcceptance) {
            "dbcd3cf917e960db3562e663f4baf3fcadc21d2b38102937fa266b4b2cdc809e"
        } else {
            "9ea0d303219b34d014d5c116677b5d325043beafb2c8a62ee889ca67f4d054a5"
        }
        assertEquals(expectedVersion, fields.openccVersion)
        assertEquals(expectedTag, OpenccUpstream.tag())
        assertEquals(expectedCommit, fields.openccCommit)
        assertEquals(
            expectedResourceSha256,
            fields.openccResourceSha256,
        )
    }
}
