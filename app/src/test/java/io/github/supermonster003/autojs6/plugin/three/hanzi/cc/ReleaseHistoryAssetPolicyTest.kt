package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.util.Locale

class ReleaseHistoryAssetPolicyTest {
    private val locales = listOf("ar", "en", "es", "fr", "ja", "ko", "ru", "zh-Hans", "zh-HK", "zh-TW")
        .map(Locale::forLanguageTag)

    @Test
    fun onlyTheArabicChangelogIsRightToLeft() {
        assertTrue(ReleaseHistoryAssetPolicy.isRightToLeft(ReleaseHistoryAssetPolicy.assetFor(Locale.forLanguageTag("ar-EG"))))
        assertTrue(ReleaseHistoryAssetPolicy.isRightToLeft(ReleaseHistoryAssetPolicy.assetFor(Locale.forLanguageTag("ar"))))
        locales.filterNot { it.language == "ar" }.forEach { locale ->
            assertFalse(locale.toLanguageTag(), ReleaseHistoryAssetPolicy.isRightToLeft(ReleaseHistoryAssetPolicy.assetFor(locale)))
        }
        // A right-to-left system language without its own changelog reads the English one left to right.
        assertEquals("CHANGELOG-en.md", ReleaseHistoryAssetPolicy.assetFor(Locale.forLanguageTag("he-IL")))
        assertFalse(ReleaseHistoryAssetPolicy.isRightToLeft("CHANGELOG-en.md"))
    }

    @Test
    fun everyBundledChangelogDirectionMatchesItsScript() {
        val docs = listOf(File("src/main/assets/doc"), File("app/src/main/assets/doc")).first { it.isDirectory }
        for (asset in locales.map(ReleaseHistoryAssetPolicy::assetFor).distinct()) {
            var rightToLeft = 0
            var leftToRight = 0
            docs.resolve(asset).readLines().filter { it.trim().startsWith("* ") }.forEach { line ->
                line.forEach { char ->
                    when (Character.getDirectionality(char)) {
                        Character.DIRECTIONALITY_RIGHT_TO_LEFT,
                        Character.DIRECTIONALITY_RIGHT_TO_LEFT_ARABIC -> rightToLeft++
                        Character.DIRECTIONALITY_LEFT_TO_RIGHT -> leftToRight++
                    }
                }
            }
            assertTrue(asset, rightToLeft + leftToRight > 0)
            assertEquals(asset, rightToLeft > leftToRight, ReleaseHistoryAssetPolicy.isRightToLeft(asset))
        }
    }
}
