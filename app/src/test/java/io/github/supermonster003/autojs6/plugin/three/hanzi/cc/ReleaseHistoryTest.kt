package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.FileNotFoundException
import java.util.Locale

class ReleaseHistoryTest {
    private fun first(tag: String) = ReleaseHistoryAssetPolicy.candidatesFor(Locale.forLanguageTag(tag)).first()

    @Test fun mapsChineseLocalesAndFallsBackToEnglish() {
        assertEquals("doc/CHANGELOG-zh-Hant-HK.md", first("zh-HK"))
        assertEquals("doc/CHANGELOG-zh-Hant-HK.md", first("zh-Hant-MO"))
        assertEquals("doc/CHANGELOG-zh-Hant-TW.md", first("zh-TW"))
        assertEquals("doc/CHANGELOG-zh-Hant-TW.md", first("zh-Hant"))
        assertEquals("doc/CHANGELOG-zh-Hans.md", first("zh-Hans-CN"))
        assertEquals("doc/CHANGELOG-zh-Hans.md", first("zh-Hans-HK"))
        assertEquals(listOf("doc/CHANGELOG-ar.md", "doc/CHANGELOG-en.md"), ReleaseHistoryAssetPolicy.candidatesFor(Locale.forLanguageTag("ar-EG")))
        assertEquals(listOf("doc/CHANGELOG-en.md"), ReleaseHistoryAssetPolicy.candidatesFor(Locale.forLanguageTag("de-DE")))
        assertEquals(listOf("doc/CHANGELOG-en.md"), ReleaseHistoryAssetPolicy.candidatesFor(Locale.ENGLISH))
    }

    /** A missing, blank or unparsable localized changelog falls back to English; nothing usable gives the empty state. */
    @Test fun skipsMissingBlankOrUnparsableLocalizedAssetsAndReportsCompleteFailure() {
        val candidates = ReleaseHistoryAssetPolicy.candidatesFor(Locale.FRANCE)
        val english = "# v1.0.0\n\n###### 2026/10/04\n\n* `Feature` English note\n"
        fun load(french: String?) = loadReleaseHistory(candidates) { path ->
            when {
                path.endsWith("-en.md") -> english
                french == null -> throw FileNotFoundException(path)
                else -> french
            }
        }
        assertEquals("English note", load(null).entries.single().items.single().text)
        assertEquals("doc/CHANGELOG-en.md", load(null).asset)
        assertEquals("English note", load(" ").entries.single().items.single().text)
        assertEquals("English note", load("### Historique\n").entries.single().items.single().text)
        assertEquals("Note", load("# v1.0.0\n\n* `Nouveauté` Note\n").entries.single().items.single().text)
        assertEquals("doc/CHANGELOG-fr.md", load("# v1.0.0\n\n* `Nouveauté` Note\n").asset)
        val blank = loadReleaseHistory(candidates) { " " }
        assertTrue(blank.entries.isEmpty())
        assertNull(blank.asset)
        assertTrue(loadReleaseHistory(candidates) { throw FileNotFoundException(it) }.entries.isEmpty())
    }

    /** Arabic items stay right to left; an Arabic interface that falls back to English reads it left to right. */
    @Test fun theDirectionFollowsTheAssetThatWasRead() {
        val candidates = ReleaseHistoryAssetPolicy.candidatesFor(Locale.forLanguageTag("ar"))
        val release = "# v1.0.0\n\n* `ميزة` README\n"
        assertTrue(loadReleaseHistory(candidates) { release }.isRightToLeft)
        val fallback = loadReleaseHistory(candidates) { path ->
            if (path.endsWith("-ar.md")) throw FileNotFoundException(path) else release
        }
        assertFalse(fallback.isRightToLeft)
        assertFalse(loadReleaseHistory(candidates) { " " }.isRightToLeft)
    }

    @Test fun parsesTheDoubleHashHeadingToo() {
        val entries = ReleaseHistoryParser.parse("## v1.0.0\n\n* `Feature` Note\n")
        assertEquals("v1.0.0", entries.single().version)
        assertEquals(1, entries.single().items.size)
    }

    /** The page names each category once and lists its items beneath; the collapsed summary counts them. */
    @Test fun groupsItemsByCategoryInTheOrderTheyFirstAppear() {
        val entry = ReleaseHistoryParser.parse(
            "# v1.2.0\n\n* `Hint` A\n* `Feature` B\n* `Feature` C\n* `Fix` D\n* `Feature` E\n* Untagged F\n",
        ).single()
        assertEquals(
            listOf("Hint" to listOf("A"), "Feature" to listOf("B", "C", "E"), "Fix" to listOf("D"), null to listOf("Untagged F")),
            entry.groups.map { it.tag to it.items },
        )
        assertEquals(listOf("Hint" to 1, "Feature" to 3, "Fix" to 1), entry.categoryCounts)
    }

    @Test fun ignoresSectionTitlesThatAreNotVersions() {
        assertTrue(ReleaseHistoryParser.parse("### Release History\n\n* `Feature` Orphan\n").isEmpty())
        assertTrue(ReleaseHistoryParser.parse("# Release History\n\n* `Feature` Orphan\n").isEmpty())
    }
}
