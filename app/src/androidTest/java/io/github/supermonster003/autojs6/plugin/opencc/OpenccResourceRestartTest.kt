package io.github.supermonster003.autojs6.plugin.opencc

import android.os.Process
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccConversionType
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccNativeEngine
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccUpstream
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.security.MessageDigest

/** Two-phase test invoked by verify_binder_round_trip.sh in separate app processes. */
@RunWith(AndroidJUnit4::class)
class OpenccResourceRestartTest {

    private val context = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun verifiedArchiveIsReusedAcrossARealProcessRestart() {
        when (InstrumentationRegistry.getArguments().getString(PHASE_ARGUMENT)) {
            PHASE_PREPARE -> prepareRestartEvidence()
            PHASE_VERIFY -> verifyRestartEvidence()
            else -> error("Pass -e $PHASE_ARGUMENT {$PHASE_PREPARE|$PHASE_VERIFY}")
        }
    }

    private fun prepareRestartEvidence() {
        OpenccNativeEngine(context).use { engine ->
            assertEquals("漢字", engine.convert("汉字", OpenccConversionType.S2T))
        }
        val archive = resourceArchive()
        assertEquals(OpenccUpstream.resourceSha256(), sha256(archive))
        assertTrue(
            "Unable to persist OpenCC restart evidence",
            preferences().edit()
                .putLong(KEY_PROCESS_ID, Process.myPid().toLong())
                .putLong(KEY_LAST_MODIFIED, archive.lastModified())
                .putLong(KEY_LENGTH, archive.length())
                .putString(KEY_SHA256, sha256(archive))
                .commit(),
        )
    }

    private fun verifyRestartEvidence() {
        val preferences = preferences()
        val previousProcess = preferences.getLong(KEY_PROCESS_ID, -1L)
        val previousModified = preferences.getLong(KEY_LAST_MODIFIED, -1L)
        val previousLength = preferences.getLong(KEY_LENGTH, -1L)
        val previousDigest = preferences.getString(KEY_SHA256, null)
        assertTrue("Restart preparation evidence is missing", previousProcess > 0L && previousModified > 0L)
        assertNotEquals("Instrumentation did not restart the app process", previousProcess, Process.myPid().toLong())

        val archive = resourceArchive()
        assertTrue("Pinned OpenCC archive is missing after restart", archive.isFile)
        assertEquals(previousModified, archive.lastModified())
        assertEquals(previousLength, archive.length())
        assertEquals(previousDigest, sha256(archive))

        OpenccNativeEngine(context).use { engine ->
            assertEquals("汉字", engine.convert("漢字", OpenccConversionType.T2S))
        }
        assertEquals("Verified archive was unexpectedly rewritten", previousModified, archive.lastModified())
        assertEquals(OpenccUpstream.resourceSha256(), sha256(archive))
        assertTrue("Unable to clear OpenCC restart evidence", preferences.edit().clear().commit())
    }

    private fun resourceArchive(): File = File(
        File(
            context.noBackupFilesDir,
            "opencc/${OpenccUpstream.version()}-${OpenccUpstream.commit().take(12)}",
        ),
        OpenccUpstream.resourceAsset(),
    )

    private fun preferences() = context.getSharedPreferences(PREFERENCES_NAME, 0)

    private fun sha256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().buffered().use { input ->
            val buffer = ByteArray(32 * 1024)
            while (true) {
                val count = input.read(buffer)
                if (count < 0) break
                digest.update(buffer, 0, count)
            }
        }
        return digest.digest().joinToString("") { byte -> "%02x".format(byte) }
    }

    private companion object {
        const val PHASE_ARGUMENT = "opencc_resource_restart_phase"
        const val PHASE_PREPARE = "prepare"
        const val PHASE_VERIFY = "verify"
        const val PREFERENCES_NAME = "opencc_resource_restart_test"
        const val KEY_PROCESS_ID = "process_id"
        const val KEY_LAST_MODIFIED = "last_modified"
        const val KEY_LENGTH = "length"
        const val KEY_SHA256 = "sha256"
    }
}
