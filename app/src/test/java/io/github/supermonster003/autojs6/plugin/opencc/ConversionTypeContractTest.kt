package io.github.supermonster003.autojs6.plugin.opencc

import com.zqc.opencc.android.lib.ConversionType as LegacyConversionType
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccConversionType
import org.autojs.plugin.opencc.api.OpenccConversionTypes
import org.junit.Assert.assertEquals
import org.junit.Test

class ConversionTypeContractTest {

    @Test
    fun apiConstantsOfficialEngineAndMigrationBaselineExposeTheSameFourteenTypes() {
        val apiTypes = OpenccConversionTypes.ALL
        val engineTypes = OpenccConversionType.entries.map { it.name }
        val legacyTypes = LegacyConversionType.entries.map { it.name }

        assertEquals(14, apiTypes.size)
        assertEquals(14, engineTypes.size)
        assertEquals(apiTypes, engineTypes)
        assertEquals(apiTypes, legacyTypes)
    }
}
