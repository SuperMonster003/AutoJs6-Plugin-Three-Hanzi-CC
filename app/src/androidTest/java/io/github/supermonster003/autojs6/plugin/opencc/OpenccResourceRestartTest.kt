package io.github.supermonster003.autojs6.plugin.opencc

import android.content.ComponentName
import android.content.Intent
import android.os.Bundle
import android.os.Parcel
import android.os.Process
import android.util.Base64
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
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

    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val context = instrumentation.targetContext

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
        val editorState = captureEditorState()
        assertEquals(EXPECTED_EDITOR_STATE, editorState)
        val portableState = Bundle().also(editorState::writeTo)
        assertTrue(
            "Unable to persist OpenCC restart evidence",
            preferences().edit()
                .putLong(KEY_PROCESS_ID, Process.myPid().toLong())
                .putLong(KEY_LAST_MODIFIED, archive.lastModified())
                .putLong(KEY_LENGTH, archive.length())
                .putString(KEY_SHA256, sha256(archive))
                .putString(KEY_EDITOR_STATE, encodeBundle(portableState))
                .commit(),
        )
    }

    private fun verifyRestartEvidence() {
        val preferences = preferences()
        val previousProcess = preferences.getLong(KEY_PROCESS_ID, -1L)
        val previousModified = preferences.getLong(KEY_LAST_MODIFIED, -1L)
        val previousLength = preferences.getLong(KEY_LENGTH, -1L)
        val previousDigest = preferences.getString(KEY_SHA256, null)
        val encodedEditorState = preferences.getString(KEY_EDITOR_STATE, null)
        assertTrue("Restart preparation evidence is missing", previousProcess > 0L && previousModified > 0L)
        assertNotEquals("Instrumentation did not restart the app process", previousProcess, Process.myPid().toLong())
        val restoredEditorState = OpenccEditorState.fromBundle(
            decodeBundle(requireNotNull(encodedEditorState) { "Restart editor-state evidence is missing" }),
            OpenccConversionType.values().indices,
            OpenccConversionType.S2T.ordinal,
        )
        assertEquals(
            "The Activity editor state did not survive Bundle serialization across a real process restart",
            EXPECTED_EDITOR_STATE,
            restoredEditorState,
        )

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

    private fun captureEditorState(): OpenccEditorState {
        val intent = Intent(Intent.ACTION_MAIN)
            .addCategory(Intent.CATEGORY_LAUNCHER)
            .setComponent(ComponentName(context, OpenccActivity::class.java))
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
        val activity = instrumentation.startActivitySync(intent) as OpenccActivity
        val state = Bundle()
        instrumentation.runOnMainSync {
            activity.findViewById<EditText>(R.id.source_text).setText(EXPECTED_EDITOR_STATE.source)
            activity.findViewById<TextView>(R.id.result_text).text = EXPECTED_EDITOR_STATE.result
            activity.findViewById<Spinner>(R.id.conversion_type)
                .setSelection(EXPECTED_EDITOR_STATE.typeIndex)
            instrumentation.callActivityOnSaveInstanceState(activity, state)
            activity.finish()
        }
        instrumentation.waitForIdleSync()
        return requireNotNull(
            OpenccEditorState.fromBundle(
                state,
                OpenccConversionType.values().indices,
                OpenccConversionType.S2T.ordinal,
            ),
        )
    }

    private fun encodeBundle(bundle: Bundle): String {
        val parcel = Parcel.obtain()
        return try {
            parcel.writeBundle(bundle)
            Base64.encodeToString(parcel.marshall(), Base64.NO_WRAP)
        } finally {
            parcel.recycle()
        }
    }

    private fun decodeBundle(encoded: String): Bundle {
        val parcel = Parcel.obtain()
        return try {
            val bytes = Base64.decode(encoded, Base64.DEFAULT)
            parcel.unmarshall(bytes, 0, bytes.size)
            parcel.setDataPosition(0)
            requireNotNull(parcel.readBundle(OpenccEditorState::class.java.classLoader))
        } finally {
            parcel.recycle()
        }
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
        const val KEY_EDITOR_STATE = "editor_state"
        val EXPECTED_EDITOR_STATE = OpenccEditorState(
            source = "进程重建来源 😀 𠀀 مرحبا",
            result = "進程重建結果 😀 𠀀 مرحبا",
            typeIndex = OpenccConversionType.TW2SP.ordinal,
        )
    }
}
