package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType
import org.autojs.plugin.opencc.api.OpenccConversionTypes
import org.autojs.plugin.tool.api.PluginToolLimits
import org.autojs.plugin.tool.api.PluginToolNames
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.Locale

class OpenccToolCatalogTest {

    @Test
    fun configsMatchTheThirtyTwoNamesOfTheHostOpenccModule() {
        val names = OpenccToolConfigs.names
        assertEquals(32, names.size)
        assertEquals(OpenccConversionTypes.ALL.map { it.lowercase(Locale.ROOT) }, names.take(14))
        // The aliases and chains of AutoJs6's OpenccConversionPlan, in its order.
        assertEquals(
            listOf(
                "s2twi", "twi2s", "s2jp", "t2twi", "hk2tw", "hk2twi", "hk2jp", "tw2hk", "tw2twi", "tw2jp",
                "twi2t", "twi2hk", "twi2tw", "twi2jp", "jp2s", "jp2hk", "jp2tw", "jp2twi",
            ),
            names.drop(14),
        )
        assertEquals(listOf(OpenccConversionType.S2TWP), OpenccToolConfigs.chains.getValue("s2twi"))
        assertEquals(
            listOf(OpenccConversionType.JP2T, OpenccConversionType.T2S, OpenccConversionType.S2TWP),
            OpenccToolConfigs.chains.getValue("jp2twi"),
        )
        OpenccConversionType.entries.forEach { type ->
            assertEquals(listOf(type), OpenccToolConfigs.chains.getValue(type.name.lowercase(Locale.ROOT)))
        }
        // Every chain starts where its name starts and ends where its name ends.
        val forms = mapOf("s" to "s", "sp" to "s", "t" to "t", "hk" to "hk", "tw" to "tw", "twi" to "tw", "twp" to "tw", "jp" to "jp")
        OpenccToolConfigs.chains.filterKeys { it !in setOf("s2twi", "twi2s") }.forEach { (name, chain) ->
            val (from, to) = name.split("2")
            val first = chain.first().name.lowercase(Locale.ROOT).split("2")
            val last = chain.last().name.lowercase(Locale.ROOT).split("2")
            assertEquals(name, forms.getValue(from), forms.getValue(first[0]))
            assertEquals(name, forms.getValue(to), forms.getValue(last[1]))
        }
    }

    @Test
    fun planDefaultsChecksTheConfigAndCountsCharacters() {
        assertEquals(listOf(OpenccConversionType.S2T), OpenccToolConfigs.plan("汉字", null))
        assertEquals(listOf(OpenccConversionType.S2T, OpenccConversionType.T2JP), OpenccToolConfigs.plan("", "s2jp"))
        val unknown = assertThrows(IllegalArgumentException::class.java) { OpenccToolConfigs.plan("汉字", "S2T") }
        assertTrue(unknown.message, unknown.message!!.startsWith("unknown config \"S2T\"; use one of hk2s, hk2t"))
        // A character outside the BMP counts once although it takes two UTF-16 units.
        val supplementary = String(Character.toChars(0x20000))
        OpenccToolConfigs.plan(supplementary.repeat(OpenccToolConfigs.MAX_TEXT_LENGTH), "t2s")
        val tooLong = assertThrows(IllegalArgumentException::class.java) {
            OpenccToolConfigs.plan("字".repeat(OpenccToolConfigs.MAX_TEXT_LENGTH + 1), "s2t")
        }
        assertEquals("text has 16385 characters; at most 16384 are allowed", tooLong.message)
    }

    @Test
    fun catalogFollowsTheContractLimits() {
        val json = OpenccToolCatalog.json
        assertTrue(PluginToolNames.isValidShortName(OpenccToolCatalog.SHORT_NAME))
        assertFalse(PluginToolNames.isReservedShortName(OpenccToolCatalog.SHORT_NAME))
        assertTrue(PluginToolNames.isValidToolName(OpenccToolCatalog.TOOL_CONVERT))
        assertEquals("opencc_convert", PluginToolNames.fullName(OpenccToolCatalog.SHORT_NAME, OpenccToolCatalog.TOOL_CONVERT))
        assertTrue(json.toByteArray(Charsets.UTF_8).size < PluginToolLimits.MAX_CATALOG_BYTES)
        assertTrue(json.startsWith("{\"shortName\":\"opencc\",\"tools\":[{\"name\":\"convert\",\"title\":\"Convert Chinese text (OpenCC)\","))
        assertTrue(json.contains("\"enum\":" + OpenccToolCatalog.encode(OpenccToolConfigs.names) + ",\"default\":\"s2t\""))
        assertTrue(json.contains("\"maxLength\":16384"))
        assertTrue(json.contains("\"required\":[\"text\"],\"additionalProperties\":false"))
        assertTrue(json.endsWith("\"risk\":\"readonly\",\"timeoutMs\":10000,\"maxConcurrency\":4}]}"))
        val description = Regex("\"description\":\"(.*?)\",\"inputSchema\"").find(json)!!.groupValues[1]
        assertTrue(description.length in 1..PluginToolLimits.MAX_DESCRIPTION_CHARS)
        assertTrue(description.all { it.code in 0x20..0x7e })
        assertEquals(json.count { it == '{' }, json.count { it == '}' })
        assertEquals(json.count { it == '[' }, json.count { it == ']' })
    }

    @Test
    fun encoderEscapesStrings() {
        assertEquals("{\"a\":[1,true,null,\"q\\\"b\\\\n\\n\\u0001\"]}", OpenccToolCatalog.encode(mapOf("a" to listOf(1, true, null, "q\"b\\n\n\u0001"))))
    }
}
