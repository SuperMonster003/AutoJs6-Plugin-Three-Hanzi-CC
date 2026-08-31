package io.github.supermonster003.autojs6.plugin.opencc

import com.zqc.opencc.android.lib.ConversionType
import org.autojs.plugin.opencc.api.OpenccConversionTypes
import org.junit.Assert.assertEquals
import org.junit.Test

class ConversionTypeContractTest {

    @Test
    fun apiConstantsAndConversionEngineExposeTheSameFourteenTypes() {
        val apiTypes = OpenccConversionTypes.ALL
        val engineTypes = ConversionType.entries.map { it.name }

        assertEquals(14, apiTypes.size)
        assertEquals(14, engineTypes.size)
        assertEquals(apiTypes, engineTypes)
    }
}
