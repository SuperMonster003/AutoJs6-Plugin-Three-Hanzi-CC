package io.github.supermonster003.autojs6.plugin.opencc

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class UpdateVersionPolicyTest {
    @Test
    fun comparesNumericReleasePartsWithoutStringOrdering() {
        assertTrue(UpdateVersionPolicy.isNewer("v1.10.0", "1.9.9"))
        assertFalse(UpdateVersionPolicy.isNewer("v1.9.9", "1.10.0"))
        assertTrue(UpdateVersionPolicy.isNewer("v2.0.0", "1.99.99"))
    }

    @Test
    fun stableReleaseSupersedesOnlyItsOwnPrereleaseOrOlderNumbers() {
        assertTrue(UpdateVersionPolicy.isNewer("v1.4.0", "1.4.0-rc.10"))
        assertFalse(UpdateVersionPolicy.isNewer("v1.4.0-rc.10", "1.4.0"))
        assertFalse(UpdateVersionPolicy.isNewer("v1.3.9", "1.4.0-rc.1"))
    }

    @Test
    fun comparesNumericPrereleaseIdentifiersNumerically() {
        assertTrue(UpdateVersionPolicy.isNewer("v1.4.0-rc.10", "1.4.0-rc.2"))
        assertFalse(UpdateVersionPolicy.isNewer("v1.4.0-rc.2", "1.4.0-rc.10"))
        assertTrue(UpdateVersionPolicy.isNewer("v1.4.0-rc.999999999999999999999", "1.4.0-rc.20"))
    }

    @Test
    fun ordersPrereleaseIdentifiersAndPrefixesBySemanticPrecedence() {
        val versions = listOf("alpha", "alpha.1", "alpha.beta", "beta", "beta.2", "beta.11", "rc.1")
        versions.zipWithNext().forEach { (older, newer) ->
            assertTrue(UpdateVersionPolicy.isNewer("1.4.0-$newer", "1.4.0-$older"))
            assertFalse(UpdateVersionPolicy.isNewer("1.4.0-$older", "1.4.0-$newer"))
        }
    }

    @Test
    fun ignoresBuildMetadataAndEqualTrailingZeroParts() {
        assertFalse(UpdateVersionPolicy.isNewer("v1.4.0+new", "1.4.0+old"))
        assertFalse(UpdateVersionPolicy.isNewer("1.4.0", "1.4"))
        assertFalse(UpdateVersionPolicy.isNewer("1.4.0-rc.1+new", "1.4.0-rc.1+old"))
    }

    @Test
    fun rejectsInvalidOrAmbiguousVersions() {
        listOf("", "latest", "1.4.0-rc..1", "1.4.0-rc.01", "1.4.0-", "2147483648.0.0").forEach { invalid ->
            assertFalse(UpdateVersionPolicy.isNewer(invalid, "1.3.0"))
            assertFalse(UpdateVersionPolicy.isNewer("1.4.0", invalid))
        }
    }
}
