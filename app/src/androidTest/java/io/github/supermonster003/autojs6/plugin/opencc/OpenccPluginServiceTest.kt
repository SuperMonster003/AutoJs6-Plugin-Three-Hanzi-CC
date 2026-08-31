package io.github.supermonster003.autojs6.plugin.opencc

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.content.pm.PackageInfo
import android.os.Build
import android.os.IBinder
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.zqc.opencc.android.lib.ChineseConverter as LegacyChineseConverter
import com.zqc.opencc.android.lib.ConversionType as LegacyConversionType
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccConversionType
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccNativeEngine
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccUpstream
import org.autojs.plugin.common.api.PluginCapabilityKeys
import org.autojs.plugin.opencc.api.IOpenccPlugin
import org.autojs.plugin.opencc.api.OpenccConversionTypes
import org.autojs.plugin.opencc.api.OpenccPluginCapabilityKeys
import org.autojs.plugin.opencc.api.OpenccPluginContract
import org.autojs.plugin.opencc.api.OpenccPluginActions
import org.autojs.plugin.opencc.api.OpenccPluginIds
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.io.RandomAccessFile
import java.security.MessageDigest
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

@RunWith(AndroidJUnit4::class)
class OpenccPluginServiceTest {

    private val context = InstrumentationRegistry.getInstrumentation().targetContext
    private val testContext = InstrumentationRegistry.getInstrumentation().context
    private val legacyEngineContext: Context by lazy(::prepareLegacyEngineResources)

    @Test
    fun discoveryBindingMetadataAndAllConversionTypesRoundTrip() {
        withBoundPlugin { plugin ->
            assertRuntimeInfo(plugin)

            val smokeInput = "汉字漢字软件軟體里面裏面"
            for (conversionType in CONVERSION_TYPES) {
                val result = plugin.convert(smokeInput, conversionType)
                assertTrue("$conversionType returned an empty result", result.isNotEmpty())
                assertEquals(
                    "Unexpected unreviewed difference from the migration baseline for $conversionType",
                    LegacyChineseConverter.convert(
                        smokeInput,
                        LegacyConversionType.valueOf(conversionType),
                        legacyEngineContext,
                    ),
                    result,
                )
            }

            assertEquals("", plugin.convert("", OpenccConversionTypes.S2T))
            assertEquals("漢字", plugin.convert("汉字", OpenccConversionTypes.S2T))
            assertEquals("汉字", plugin.convert("漢字", OpenccConversionTypes.T2S))
            assertEquals(
                "OpenCC 😀 𠀀",
                plugin.convert("OpenCC 😀 𠀀", OpenccConversionTypes.S2T),
            )
            assertEquals(
                "漢A😀𠀀".repeat(4096),
                plugin.convert("汉A😀𠀀".repeat(4096), OpenccConversionTypes.S2T),
            )

            assertReviewedUpstreamDifferences(plugin)
            assertConcurrentConversions(plugin)

            assertEquals(OpenccConversionTypes.ALL, plugin.supportedConversionTypes)
            val batchInput = listOf("汉字", "软件")
            assertEquals(
                batchInput.map { plugin.convert(it, OpenccConversionTypes.S2T) },
                plugin.convertBatch(
                    batchInput.toMutableList(),
                    OpenccConversionTypes.S2T,
                ),
            )
            assertTrue(
                plugin.convertBatch(mutableListOf(), OpenccConversionTypes.S2T).isEmpty(),
            )

            val chainTypes = mutableListOf(
                OpenccConversionTypes.S2T,
                OpenccConversionTypes.T2JP,
            )
            val sequential = chainTypes.fold("鼠标软件") { text, conversionType ->
                plugin.convert(text, conversionType)
            }
            assertEquals(sequential, plugin.convertChain("鼠标软件", chainTypes))
            assertEquals("identity", plugin.convertChain("identity", mutableListOf()))

            try {
                plugin.convert("汉字", "NOT_A_CONVERSION")
                fail("Unknown conversion type must be rejected")
            } catch (error: IllegalArgumentException) {
                assertTrue(
                    "Unexpected unknown-type message: ${error.message}",
                    error.message.orEmpty().contains("NOT_A_CONVERSION"),
                )
            }

            try {
                plugin.convertBatch(
                    MutableList(OpenccPluginContract.MAX_BATCH_SIZE + 1) { "汉" },
                    OpenccConversionTypes.S2T,
                )
                fail("Oversized conversion batch must be rejected")
            } catch (error: IllegalArgumentException) {
                assertTrue(error.message.orEmpty().contains("1024"))
            }

            try {
                plugin.convertChain(
                    "汉字",
                    MutableList(OpenccPluginContract.MAX_CHAIN_LENGTH + 1) {
                        OpenccConversionTypes.S2T
                    },
                )
                fail("Oversized conversion chain must be rejected")
            } catch (error: IllegalArgumentException) {
                assertTrue(error.message.orEmpty().contains("32"))
            }
        }
        assertResourceRecoveryAndReuse()
    }

    /**
     * OpenCC 1.4.2 intentionally fixes these legacy dictionary outputs. Keeping the
     * old and new expected values together makes every accepted behavior change explicit.
     */
    private fun assertReviewedUpstreamDifferences(plugin: IOpenccPlugin) {
        val reviewedCases = listOf(
            ReviewedDifference(OpenccConversionTypes.S2T, "托着", "託着", "托着", "托/託 candidate order"),
            ReviewedDifference(OpenccConversionTypes.S2T, "复盘", "覆盤", "復盤", "explicit phrase correction"),
            ReviewedDifference(OpenccConversionTypes.S2T, "内卷", "內卷", "內捲", "regional character correction"),
            ReviewedDifference(OpenccConversionTypes.S2T, "谷神谷神星", "穀神穀神星", "谷神穀神星", "classical-context exception"),
            ReviewedDifference(OpenccConversionTypes.T2S, "乾斷食乾紅", "乾断食乾红", "干断食干红", "issue-specific phrases"),
            ReviewedDifference(OpenccConversionTypes.TW2S, "什么怎么这么", "什幺怎幺这幺", "什么怎么这么", "么/幺 destructive-conversion fix"),
            ReviewedDifference(OpenccConversionTypes.S2TWP, "内存条", "記憶體條", "記憶體模組", "Taiwan terminology"),
            ReviewedDifference(OpenccConversionTypes.S2TWP, "数字人文", "數字人文", "數位人文", "Taiwan terminology"),
            ReviewedDifference(OpenccConversionTypes.S2TWP, "互联网络", "網際網路絡", "網際網路", "greedy-match correction"),
            ReviewedDifference(OpenccConversionTypes.S2TWP, "快闪存储器", "快快閃記憶體儲器", "快閃記憶體", "greedy-match correction"),
            ReviewedDifference(OpenccConversionTypes.S2TWP, "老挝人民民主共和国", "寮國人民民主共和國", "寮人民民主共和國", "official Taiwan name"),
        )
        for (case in reviewedCases) {
            assertEquals(
                "Legacy baseline drifted for ${case.conversionType}/${case.input} (${case.reason})",
                case.legacyOutput,
                LegacyChineseConverter.convert(
                    case.input,
                    LegacyConversionType.valueOf(case.conversionType),
                    legacyEngineContext,
                ),
            )
            assertEquals(
                "Official OpenCC 1.4.2 output drifted for " +
                    "${case.conversionType}/${case.input} (${case.reason})",
                case.officialOutput,
                plugin.convert(case.input, case.conversionType),
            )
        }
    }

    /**
     * The legacy wrapper assumes its assets and files directory belong to the same APK.
     * Instrumentation assets live in the test APK while its process/files belong to the
     * target APK, so the migration fixture prepares the old data explicitly.
     */
    private fun prepareLegacyEngineResources(): Context {
        val targetDirectory = File(context.filesDir, "openccdata")
        check(targetDirectory.isDirectory || targetDirectory.mkdirs()) {
            "Unable to create legacy OpenCC test directory: $targetDirectory"
        }
        val entries = requireNotNull(testContext.assets.list("openccdata")) {
            "Legacy OpenCC test assets are unavailable"
        }
        check(entries.isNotEmpty()) { "Legacy OpenCC test assets are empty" }
        for (entry in entries) {
            check('/' !in entry && '\\' !in entry && entry !in setOf(".", "..")) {
                "Unsafe legacy OpenCC test asset name: $entry"
            }
            testContext.assets.open("openccdata/$entry").use { input ->
                File(targetDirectory, entry).outputStream().use(input::copyTo)
            }
        }
        check(File(targetDirectory, "zFinished2").isFile) {
            "Legacy OpenCC completion marker was not installed"
        }
        return context
    }

    private fun assertConcurrentConversions(plugin: IOpenccPlugin) {
        val executor = Executors.newFixedThreadPool(8)
        try {
            val results = (0 until 64).map { index ->
                executor.submit<String> {
                    plugin.convert("$index 汉字 😀", OpenccConversionTypes.S2T)
                }
            }
            results.forEachIndexed { index, result ->
                assertEquals("$index 漢字 😀", result.get(30, TimeUnit.SECONDS))
            }
        } finally {
            executor.shutdownNow()
            assertTrue("Conversion executor did not stop", executor.awaitTermination(5, TimeUnit.SECONDS))
        }
    }

    private fun assertResourceRecoveryAndReuse() {
        val archive = File(
            File(
                context.noBackupFilesDir,
                "opencc/${OpenccUpstream.version()}-${OpenccUpstream.commit().take(12)}",
            ),
            OpenccUpstream.resourceAsset(),
        )

        OpenccNativeEngine(context).use { engine ->
            assertEquals("漢字", engine.convert("汉字", OpenccConversionType.S2T))
        }
        assertEquals(OpenccUpstream.resourceSha256(), sha256(archive))

        val previousModified = archive.lastModified()
        RandomAccessFile(archive, "rw").use { file ->
            val firstByte = file.read()
            check(firstByte >= 0) { "Pinned OpenCC resource archive is empty" }
            file.seek(0)
            file.write(firstByte xor 0xff)
        }
        check(archive.setLastModified(previousModified + 2_000L)) {
            "Unable to update the corrupted OpenCC resource timestamp"
        }
        assertTrue("Test corruption did not change the resource digest", sha256(archive) != OpenccUpstream.resourceSha256())

        OpenccNativeEngine(context).use { engine ->
            assertEquals("漢字", engine.convert("汉字", OpenccConversionType.S2T))
        }
        assertEquals(OpenccUpstream.resourceSha256(), sha256(archive))

        val verifiedModified = archive.lastModified()
        OpenccNativeEngine(context).use { engine ->
            assertEquals("汉字", engine.convert("漢字", OpenccConversionType.T2S))
        }
        assertEquals("An unchanged verified resource must be reused", verifiedModified, archive.lastModified())
    }

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

    private fun assertRuntimeInfo(plugin: IOpenccPlugin) {
        val info = plugin.info
        val packageInfo = context.packageManager.getPackageInfo(context.packageName, 0)

        assertEquals("OpenCC", info.name)
        assertTrue(info.description?.isNotBlank() == true)
        assertEquals("@raw/plugin_instruction", info.instruction)
        assertEquals("SuperMonster003", info.author)
        assertEquals(OpenccPluginIds.ID, info.id)
        assertEquals(OpenccPluginIds.ENGINE, info.engine)
        assertEquals(OpenccPluginIds.VARIANT_DEFAULT, info.variant)
        assertEquals(packageInfo.versionName.orEmpty(), info.versionName)
        assertEquals(packageInfo.versionCodeCompat(), info.versionCode)
        assertTrue(info.versionDate?.isNotBlank() == true)
        assertEquals(
            setOf("arm64-v8a", "armeabi-v7a", "x86_64", "x86"),
            info.supportedAbis.orEmpty().toSet(),
        )

        val processAbis = if (android.os.Process.is64Bit()) {
            Build.SUPPORTED_64_BIT_ABIS
        } else {
            Build.SUPPORTED_32_BIT_ABIS
        }
        val expectedProcessAbi = processAbis.first { it in info.supportedAbis.orEmpty() }
        assertTrue(expectedProcessAbi in info.supportedAbis.orEmpty())

        val capabilities = requireNotNull(info.capabilities) { "Plugin capabilities are missing" }
        assertEquals(3923, capabilities.getInt(PluginCapabilityKeys.REQUIRES_HOST_VERSION))
        assertEquals(
            OpenccPluginContract.VERSION_CURRENT,
            capabilities.getInt(OpenccPluginCapabilityKeys.CONTRACT_VERSION),
        )
        assertEquals(
            OpenccConversionTypes.ALL,
            capabilities.getStringArrayList(OpenccPluginCapabilityKeys.SUPPORTED_CONVERSION_TYPES),
        )
        assertEquals("1.4.2", capabilities.getString(OpenccEngineCapabilityKeys.VERSION))
        assertEquals(
            "025f371dc76b598d77384fbdab90c937471844d8",
            capabilities.getString(OpenccEngineCapabilityKeys.COMMIT),
        )
        assertEquals(
            "9ea0d303219b34d014d5c116677b5d325043beafb2c8a62ee889ca67f4d054a5",
            capabilities.getString(OpenccEngineCapabilityKeys.RESOURCE_SHA256),
        )
    }

    private fun withBoundPlugin(block: (IOpenccPlugin) -> Unit) {
        val discoveryIntent = Intent(OpenccPluginActions.OPENCC)
            .addCategory(OpenccPluginIds.ID)
            .setPackage(context.packageName)
        @Suppress("DEPRECATION")
        val matches = context.packageManager.queryIntentServices(discoveryIntent, 0)
        assertEquals("OpenCC discovery must resolve exactly one service", 1, matches.size)

        val serviceInfo = matches.single().serviceInfo
        val explicitIntent = Intent(discoveryIntent).setComponent(
            ComponentName(serviceInfo.packageName, serviceInfo.name),
        )
        val latch = CountDownLatch(1)
        val binder = AtomicReference<IBinder?>()
        val connection = object : ServiceConnection {
            override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
                binder.set(service)
                latch.countDown()
            }

            override fun onServiceDisconnected(name: ComponentName?) = Unit

            override fun onNullBinding(name: ComponentName?) {
                latch.countDown()
            }

            override fun onBindingDied(name: ComponentName?) {
                latch.countDown()
            }
        }

        assertTrue(
            "Unable to bind the discovered OpenCC service",
            context.bindService(explicitIntent, connection, Context.BIND_AUTO_CREATE),
        )
        try {
            assertTrue("Timed out binding the OpenCC service", latch.await(15, TimeUnit.SECONDS))
            val rawBinder = binder.get()
            assertNotNull("OpenCC service returned a null Binder", rawBinder)
            block(IOpenccPlugin.Stub.asInterface(rawBinder))
        } finally {
            context.unbindService(connection)
        }
    }

    private fun PackageInfo.versionCodeCompat(): Long {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) return longVersionCode
        @Suppress("DEPRECATION")
        return versionCode.toLong()
    }

    private companion object {
        val CONVERSION_TYPES = OpenccConversionTypes.ALL
    }

    private data class ReviewedDifference(
        val conversionType: String,
        val input: String,
        val legacyOutput: String,
        val officialOutput: String,
        val reason: String,
    )
}
