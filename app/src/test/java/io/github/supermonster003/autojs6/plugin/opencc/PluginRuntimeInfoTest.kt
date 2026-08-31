package io.github.supermonster003.autojs6.plugin.opencc

import org.autojs.plugin.opencc.api.OpenccPluginIds
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
            versionName = "1.0.2",
            versionCode = 17,
            versionDate = "Aug 31, 2026",
        )

        assertEquals("OpenCC", fields.name)
        assertEquals("OpenCC test description", fields.description)
        assertEquals("SuperMonster003", fields.author)
        assertEquals(OpenccPluginIds.ID, fields.id)
        assertEquals(OpenccPluginIds.ENGINE, fields.engine)
        assertEquals(OpenccPluginIds.VARIANT_DEFAULT, fields.variant)
        assertEquals("1.0.2", fields.versionName)
        assertEquals(17, fields.versionCode)
        assertEquals("Aug 31, 2026", fields.versionDate)
        assertEquals(
            listOf("arm64-v8a", "armeabi-v7a", "x86_64", "x86"),
            fields.supportedAbis,
        )
        assertEquals(3923, fields.requiredHostVersion)
    }
}
