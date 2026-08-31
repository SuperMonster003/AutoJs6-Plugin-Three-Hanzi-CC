package io.github.supermonster003.autojs6.plugin.opencc

import com.zqc.opencc.android.lib.ConversionType
import org.autojs.plugin.opencc.api.OpenccConversionTypes
import org.junit.Assert.assertEquals
import org.junit.Test

class ConversionTypeContractTest {

    @Test
    fun apiConstantsAndConversionEngineExposeTheSameFourteenTypes() {
        val apiTypes = setOf(
            OpenccConversionTypes.HK2S,
            OpenccConversionTypes.HK2T,
            OpenccConversionTypes.JP2T,
            OpenccConversionTypes.S2HK,
            OpenccConversionTypes.S2T,
            OpenccConversionTypes.S2TW,
            OpenccConversionTypes.S2TWP,
            OpenccConversionTypes.T2HK,
            OpenccConversionTypes.T2S,
            OpenccConversionTypes.T2TW,
            OpenccConversionTypes.T2JP,
            OpenccConversionTypes.TW2S,
            OpenccConversionTypes.TW2T,
            OpenccConversionTypes.TW2SP,
        )
        val engineTypes = ConversionType.entries.mapTo(mutableSetOf()) { it.name }

        assertEquals(14, apiTypes.size)
        assertEquals(14, engineTypes.size)
        assertEquals(apiTypes, engineTypes)
    }
}
