package io.github.supermonster003.autojs6.plugin.opencc

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.IBinder
import android.os.SystemClock
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccUpstream
import org.autojs.plugin.opencc.api.IOpenccPlugin
import org.autojs.plugin.opencc.api.OpenccConversionTypes
import org.autojs.plugin.opencc.api.OpenccPluginActions
import org.autojs.plugin.opencc.api.OpenccPluginIds
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.io.RandomAccessFile
import java.security.MessageDigest
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

/**
 * Invoked in two fresh processes to prove that both public entry points stay lazy and install
 * only the pinned resource embedded in the APK. The standalone phase also starts from a damaged
 * same-size archive so the first UI conversion exercises recovery rather than a happy-path copy.
 */
@RunWith(AndroidJUnit4::class)
class OpenccEntryResourceTest {

    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val context = instrumentation.targetContext

    @Test
    fun firstEntryConversionUsesOnlyTheVerifiedEmbeddedResource() {
        when (InstrumentationRegistry.getArguments().getString(PHASE_ARGUMENT)) {
            PHASE_STANDALONE -> verifyStandaloneFirstConversion()
            PHASE_BINDER -> verifyBinderFirstConversion()
            else -> error("Pass -e $PHASE_ARGUMENT {$PHASE_STANDALONE|$PHASE_BINDER}")
        }
    }

    private fun verifyStandaloneFirstConversion() {
        resetVersionDirectory()
        val archive = resourceArchive()
        assertFalse("Resource must be absent before standalone launch", archive.exists())

        val activity = launchActivity()
        try {
            instrumentation.waitForIdleSync()
            assertFalse("Opening the standalone UI must not install resources", archive.exists())

            val embeddedSize = installCorruptedEmbeddedAsset(archive)
            assertEquals(embeddedSize, archive.length())
            assertTrue(
                "The test fixture did not corrupt the embedded resource copy",
                sha256(archive) != OpenccUpstream.resourceSha256(),
            )

            val source = activity.findViewById<EditText>(R.id.source_text)
            val convert = activity.findViewById<Button>(R.id.convert_button)
            val result = activity.findViewById<TextView>(R.id.result_text)
            instrumentation.runOnMainSync {
                source.setText(SMOKE_INPUT)
                check(convert.performClick()) { "Standalone conversion click was not accepted" }
            }
            await("standalone conversion and resource recovery") {
                readText(result) == SMOKE_OUTPUT &&
                    archive.isFile &&
                    archive.length() == embeddedSize &&
                    sha256(archive) == OpenccUpstream.resourceSha256()
            }
            assertVersionDirectoryInventory()
        } finally {
            instrumentation.runOnMainSync { activity.finish() }
            instrumentation.waitForIdleSync()
        }

        // The next instrumentation invocation runs in a different app process and must exercise
        // the Binder-first missing-resource path independently.
        resetVersionDirectory()
    }

    private fun verifyBinderFirstConversion() {
        val archive = resourceArchive()
        assertFalse("Resource must be absent before first Binder binding", archive.exists())
        withBoundPlugin { plugin ->
            plugin.info
            assertEquals(OpenccConversionTypes.ALL, plugin.supportedConversionTypes)
            assertFalse("Binding and capability discovery must not install resources", archive.exists())

            assertEquals(SMOKE_OUTPUT, plugin.convert(SMOKE_INPUT, OpenccConversionTypes.S2T))
            assertTrue("First Binder conversion did not install the pinned resource", archive.isFile)
            assertEquals(OpenccUpstream.resourceSha256(), sha256(archive))
            assertEquals(embeddedAssetSize(), archive.length())
            assertVersionDirectoryInventory()
        }
    }

    private fun launchActivity(): OpenccActivity {
        val intent = Intent(Intent.ACTION_MAIN)
            .addCategory(Intent.CATEGORY_LAUNCHER)
            .setComponent(ComponentName(context, OpenccActivity::class.java))
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
        return instrumentation.startActivitySync(intent) as OpenccActivity
    }

    private fun installCorruptedEmbeddedAsset(archive: File): Long {
        val directory = requireNotNull(archive.parentFile)
        assertTrue("Unable to create the versioned OpenCC test directory", directory.mkdirs())
        context.assets.open("opencc/${OpenccUpstream.resourceAsset()}").use { input ->
            archive.outputStream().buffered().use { output -> input.copyTo(output) }
        }
        val originalSize = archive.length()
        RandomAccessFile(archive, "rw").use { file ->
            val firstByte = file.read()
            check(firstByte >= 0) { "Embedded OpenCC resource is empty" }
            file.seek(0)
            file.write(firstByte xor 0xff)
        }
        check(archive.setLastModified(archive.lastModified() + 2_000L)) {
            "Unable to update the corrupted resource timestamp"
        }
        return originalSize
    }

    private fun embeddedAssetSize(): Long {
        return context.assets.open("opencc/${OpenccUpstream.resourceAsset()}").use { input ->
            var size = 0L
            val buffer = ByteArray(32 * 1024)
            while (true) {
                val count = input.read(buffer)
                if (count < 0) break
                size += count
            }
            size
        }
    }

    private fun assertVersionDirectoryInventory() {
        assertEquals(
            "The resource installer must leave exactly one final archive and no temporary files",
            listOf(OpenccUpstream.resourceAsset()),
            versionDirectory().listFiles().orEmpty().map { it.name }.sorted(),
        )
    }

    private fun resetVersionDirectory() {
        val directory = versionDirectory()
        if (!directory.exists()) return
        directory.listFiles().orEmpty().forEach { child ->
            check(child.isFile) { "Unexpected nested path in versioned OpenCC directory: $child" }
            check(child.delete()) { "Unable to delete test resource file: $child" }
        }
        check(directory.delete()) { "Unable to delete versioned OpenCC test directory: $directory" }
    }

    private fun versionDirectory(): File = File(
        context.noBackupFilesDir,
        "opencc/${OpenccUpstream.version()}-${OpenccUpstream.commit().take(12)}",
    )

    private fun resourceArchive(): File = File(versionDirectory(), OpenccUpstream.resourceAsset())

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

    private fun readText(view: TextView): String {
        val text = AtomicReference<String>()
        instrumentation.runOnMainSync { text.set(view.text.toString()) }
        return text.get()
    }

    private fun await(description: String, predicate: () -> Boolean) {
        val deadline = SystemClock.elapsedRealtime() + TIMEOUT_MILLIS
        while (SystemClock.elapsedRealtime() < deadline) {
            instrumentation.waitForIdleSync()
            if (predicate()) return
            SystemClock.sleep(POLL_INTERVAL_MILLIS)
        }
        throw AssertionError("Timed out waiting for $description")
    }

    private fun withBoundPlugin(block: (IOpenccPlugin) -> Unit) {
        val discoveryIntent = Intent(OpenccPluginActions.OPENCC)
            .addCategory(OpenccPluginIds.ID)
            .setPackage(context.packageName)
        @Suppress("DEPRECATION")
        val matches = context.packageManager.queryIntentServices(discoveryIntent, 0)
        assertEquals("OpenCC discovery must resolve exactly one service", 1, matches.size)
        val info = matches.single().serviceInfo
        val explicitIntent = Intent(discoveryIntent).setComponent(ComponentName(info.packageName, info.name))
        val connected = CountDownLatch(1)
        val binder = AtomicReference<IBinder?>()
        val connection = object : ServiceConnection {
            override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
                binder.set(service)
                connected.countDown()
            }

            override fun onServiceDisconnected(name: ComponentName?) = Unit
            override fun onNullBinding(name: ComponentName?) = connected.countDown()
            override fun onBindingDied(name: ComponentName?) = connected.countDown()
        }
        assertTrue(
            "Unable to bind the discovered OpenCC service",
            context.bindService(explicitIntent, connection, Context.BIND_AUTO_CREATE),
        )
        try {
            assertTrue("Timed out binding the OpenCC service", connected.await(15, TimeUnit.SECONDS))
            val rawBinder = binder.get()
            assertNotNull("OpenCC service returned a null Binder", rawBinder)
            block(remoteOpenccPlugin(rawBinder!!))
        } finally {
            context.unbindService(connection)
        }
    }

    private companion object {
        const val PHASE_ARGUMENT = "opencc_entry_resource_phase"
        const val PHASE_STANDALONE = "standalone"
        const val PHASE_BINDER = "binder"
        const val SMOKE_INPUT = "汉字软件 😀 𠀀"
        const val SMOKE_OUTPUT = "漢字軟件 😀 𠀀"
        const val TIMEOUT_MILLIS = 60_000L
        const val POLL_INTERVAL_MILLIS = 50L
    }
}
