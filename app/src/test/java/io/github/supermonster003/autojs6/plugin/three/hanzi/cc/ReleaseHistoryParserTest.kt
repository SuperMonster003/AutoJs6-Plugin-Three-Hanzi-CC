package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.util.Locale

class ReleaseHistoryParserTest {
    @Test
    fun inlineCodeMarkersAreDroppedFromTheText() {
        val markdown = """
            # v1.0.0

            ###### 2026/07/14

            * `Feature` Plugin ID and engine set to `opencc`
            * `Feature` Types: `S2T`/`S2TW`/`JP2T`
            * `Hint` `复盘` -> `復盤`, plain text stays
        """.trimIndent()

        val entries = ReleaseHistoryParser.parse(markdown)

        assertEquals(1, entries.size)
        assertEquals("v1.0.0", entries[0].version)
        assertEquals("2026/07/14", entries[0].date)
        assertEquals(
            listOf(
                ReleaseHistoryItem("Feature", "Plugin ID and engine set to opencc"),
                ReleaseHistoryItem("Feature", "Types: S2T/S2TW/JP2T"),
                ReleaseHistoryItem("Hint", "复盘 -> 復盤, plain text stays"),
            ),
            entries[0].items,
        )
    }

    @Test
    fun everyBundledChangelogParsesWithoutInlineCodeMarkers() {
        val docs = listOf(File("src/main/assets/doc"), File("app/src/main/assets/doc")).first { it.isDirectory }
        val versionName = docs.resolve("../../../../../version.properties").readLines()
            .first { it.startsWith("VERSION_NAME=") }.substringAfter('=').trim()
        val locales = listOf("ar", "en", "es", "fr", "ja", "ko", "ru", "zh-Hans", "zh-HK", "zh-TW")
            .map(Locale::forLanguageTag)

        for (asset in locales.map(ReleaseHistoryAssetPolicy::assetFor).distinct()) {
            val markdown = docs.resolve(asset).readText()
            val lines = markdown.lines().map(String::trim)
            val entries = ReleaseHistoryParser.parse(markdown)

            assertEquals(asset, lines.count { it.startsWith("# ") }, entries.size)
            assertEquals(asset, "v$versionName", entries.first().version)
            assertTrue(asset, entries.all { it.date != null && it.items.isNotEmpty() && it.items.all { item -> item.tag != null } })
            assertEquals(asset, lines.count { it.startsWith("* ") }, entries.sumOf { it.items.size })
            assertFalse(asset, entries.any { entry -> entry.items.any { '`' in it.text } })
        }
    }
}
