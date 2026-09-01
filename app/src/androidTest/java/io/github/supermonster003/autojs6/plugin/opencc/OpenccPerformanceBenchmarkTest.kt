package io.github.supermonster003.autojs6.plugin.opencc

import android.content.Context
import android.os.Build
import android.os.Bundle
import android.os.Debug
import android.os.Process
import android.os.SystemClock
import android.system.Os
import android.system.OsConstants
import android.util.Log
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccConversionType
import io.github.supermonster003.autojs6.plugin.opencc.nativebridge.OpenccNativeEngine
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.Closeable
import java.io.File
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.locks.LockSupport
import kotlin.math.max

/**
 * Opt-in device benchmark for the pinned official backend.
 *
 * The host runner invokes the first-load and steady-state phases in different app
 * processes. Running the regular instrumentation suite without benchmark arguments
 * skips this class so timing noise can never make the correctness suite flaky.
 */
@RunWith(AndroidJUnit4::class)
class OpenccPerformanceBenchmarkTest {

    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val context = instrumentation.targetContext

    @Test
    fun measureSelectedEngineAndPhase() {
        val arguments = InstrumentationRegistry.getArguments()
        val engineName = arguments.getString(ARGUMENT_ENGINE)
        val phase = arguments.getString(ARGUMENT_PHASE)
        assumeTrue(
            "Pass -e $ARGUMENT_ENGINE official and " +
                "-e $ARGUMENT_PHASE {first-load|steady-state}",
            engineName != null && phase != null,
        )

        require(engineName in ENGINES) { "Unsupported benchmark engine: $engineName" }
        require(phase in PHASES) { "Unsupported benchmark phase: $phase" }

        val result = when (phase) {
            PHASE_FIRST_LOAD -> measureFirstLoad(requireNotNull(engineName))
            PHASE_STEADY_STATE -> measureSteadyState(requireNotNull(engineName))
            else -> error("Unreachable benchmark phase: $phase")
        }
        emitResult(result)
    }

    private fun measureFirstLoad(engineName: String): JSONObject {
        deleteEngineResources(engineName)
        assertTrue("Benchmark resources were not reset for $engineName", !resourceMarker(engineName).exists())
        stabilizeManagedHeap()

        val before = MemorySnapshot.capture()
        val startedAt = SystemClock.elapsedRealtimeNanos()
        val converter = createConverter(engineName)
        val output = converter.convert(BENCHMARK_TEXT)
        val elapsedNanos = SystemClock.elapsedRealtimeNanos() - startedAt
        val after = MemorySnapshot.capture()
        try {
            assertExpectedOutput(output)
            assertTrue("$engineName did not install its benchmark resources", resourceMarker(engineName).exists())
            return baseResult(engineName, PHASE_FIRST_LOAD)
                .put("first_load_ns", elapsedNanos)
                .put("resource_bytes", resourceBytes(engineName))
                .put("output_utf16_units", output.length)
                .put("memory_before", before.toJson())
                .put("memory_after", after.toJson())
                .put("pss_delta_kb", after.totalPssKb - before.totalPssKb)
        } finally {
            converter.close()
        }
    }

    private fun measureSteadyState(engineName: String): JSONObject {
        assertTrue(
            "Run the first-load phase before steady-state for $engineName",
            resourceMarker(engineName).exists(),
        )
        stabilizeManagedHeap()

        val memoryBefore = MemorySnapshot.capture()
        val coldStartedAt = SystemClock.elapsedRealtimeNanos()
        val converter = createConverter(engineName)
        val coldOutput = converter.convert(BENCHMARK_TEXT)
        val coldNanos = SystemClock.elapsedRealtimeNanos() - coldStartedAt
        assertExpectedOutput(coldOutput)
        val memoryAfterCold = MemorySnapshot.capture()

        try {
            repeat(WARMUP_ITERATIONS) {
                assertExpectedOutput(converter.convert(BENCHMARK_TEXT))
            }

            val warmDurations = LongArray(WARM_ITERATIONS)
            repeat(WARM_ITERATIONS) { index ->
                val startedAt = SystemClock.elapsedRealtimeNanos()
                val output = converter.convert(BENCHMARK_TEXT)
                warmDurations[index] = SystemClock.elapsedRealtimeNanos() - startedAt
                assertExpectedOutput(output)
            }

            val batchInput = List(BATCH_SIZE) { index ->
                "$index $BATCH_SEGMENT"
            }
            var batchOutputUnits = 0L
            val batchStartedAt = SystemClock.elapsedRealtimeNanos()
            for (text in batchInput) {
                batchOutputUnits += converter.convert(text).length
            }
            val batchNanos = SystemClock.elapsedRealtimeNanos() - batchStartedAt
            assertTrue("$engineName batch output was empty", batchOutputUnits > 0L)

            stabilizeManagedHeap()
            val memoryBeforeWorkload = MemorySnapshot.capture()
            val sampler = PeakMemorySampler(
                listOf(memoryBefore, memoryAfterCold, memoryBeforeWorkload),
            )
            sampler.use {
                repeat(MEMORY_LONG_TEXT_ITERATIONS) {
                    assertEquals(
                        MEMORY_BENCHMARK_EXPECTED_TEXT,
                        converter.convert(MEMORY_BENCHMARK_TEXT),
                    )
                }
                for (text in batchInput) {
                    assertTrue(converter.convert(text).isNotEmpty())
                }
            }
            val memoryAfterWorkload = MemorySnapshot.capture()
            sampler.include(memoryAfterWorkload)

            return baseResult(engineName, PHASE_STEADY_STATE)
                .put("cold_conversion_ns", coldNanos)
                .put("warmup_iterations", WARMUP_ITERATIONS)
                .put("warm_iterations", WARM_ITERATIONS)
                .put("warm_min_ns", warmDurations.minOrNull())
                .put("warm_median_ns", percentile(warmDurations, 50))
                .put("warm_p95_ns", percentile(warmDurations, 95))
                .put("warm_max_ns", warmDurations.maxOrNull())
                .put("warm_total_ns", warmDurations.sum())
                .put("batch_size", BATCH_SIZE)
                .put("batch_input_utf16_units", batchInput.sumOf(String::length))
                .put("batch_output_utf16_units", batchOutputUnits)
                .put("batch_total_ns", batchNanos)
                .put("memory_before", memoryBefore.toJson())
                .put("memory_after_cold", memoryAfterCold.toJson())
                .put("memory_before_workload", memoryBeforeWorkload.toJson())
                .put("memory_after_workload", memoryAfterWorkload.toJson())
                .put("memory_peak", sampler.peak().toJson())
                .put("peak_pss_delta_kb", sampler.peak().totalPssKb - memoryBefore.totalPssKb)
        } finally {
            converter.close()
        }
    }

    private fun createConverter(engineName: String): BenchmarkConverter {
        return when (engineName) {
            ENGINE_OFFICIAL -> OfficialConverter(context)
            else -> error("Unsupported benchmark engine: $engineName")
        }
    }

    private fun deleteEngineResources(engineName: String) {
        val directory = resourceDirectory(engineName)
        if (!directory.exists()) return
        check(directory.deleteRecursively()) { "Unable to reset benchmark resources: $directory" }
    }

    private fun resourceDirectory(engineName: String): File {
        return when (engineName) {
            ENGINE_OFFICIAL -> File(context.noBackupFilesDir, "opencc")
            else -> error("Unsupported benchmark engine: $engineName")
        }
    }

    private fun resourceMarker(engineName: String): File {
        return when (engineName) {
            ENGINE_OFFICIAL -> resourceDirectory(engineName)
            else -> error("Unsupported benchmark engine: $engineName")
        }
    }

    private fun resourceBytes(engineName: String): Long {
        val directory = resourceDirectory(engineName)
        return directory.walkTopDown().filter(File::isFile).sumOf(File::length)
    }

    private fun assertExpectedOutput(output: String) {
        assertEquals(BENCHMARK_EXPECTED_TEXT, output)
    }

    private fun baseResult(engineName: String, phase: String): JSONObject {
        return JSONObject()
            .put("schema_version", RESULT_SCHEMA_VERSION)
            .put("engine", engineName)
            .put("phase", phase)
            .put("pid", Process.myPid())
            .put("sdk_int", Build.VERSION.SDK_INT)
            .put("android_release", Build.VERSION.RELEASE)
            .put("model", Build.MODEL)
            .put("fingerprint", Build.FINGERPRINT)
            .put("process_is_64_bit", Process.is64Bit())
            .put("supported_abis", JSONArray(Build.SUPPORTED_ABIS.asList()))
            .put("page_size_bytes", Os.sysconf(OsConstants._SC_PAGESIZE))
            .put("input_utf16_units", BENCHMARK_TEXT.length)
            .put("input_code_points", BENCHMARK_TEXT.codePointCount(0, BENCHMARK_TEXT.length))
    }

    private fun emitResult(result: JSONObject) {
        val message = "$RESULT_PREFIX$result"
        instrumentation.sendStatus(
            STATUS_BENCHMARK_RESULT,
            Bundle().apply { putString("stream", "$message\n") },
        )
        Log.i(LOG_TAG, message)
    }

    private fun stabilizeManagedHeap() {
        repeat(2) {
            Runtime.getRuntime().gc()
            System.runFinalization()
        }
        SystemClock.sleep(50L)
    }

    private fun percentile(values: LongArray, percentile: Int): Long {
        require(values.isNotEmpty())
        require(percentile in 0..100)
        val sorted = values.sortedArray()
        val index = ((sorted.lastIndex.toLong() * percentile) / 100L).toInt()
        return sorted[index]
    }

    private interface BenchmarkConverter : Closeable {
        fun convert(text: String): String
    }

    private class OfficialConverter(context: Context) : BenchmarkConverter {
        private val engine = OpenccNativeEngine(context)

        override fun convert(text: String): String {
            return engine.convert(text, OpenccConversionType.S2T)
        }

        override fun close() = engine.close()
    }

    private data class MemorySnapshot(
        val totalPssKb: Long,
        val totalPrivateDirtyKb: Long,
        val nativeHeapBytes: Long,
        val javaHeapBytes: Long,
    ) {
        fun toJson(): JSONObject {
            return JSONObject()
                .put("total_pss_kb", totalPssKb)
                .put("total_private_dirty_kb", totalPrivateDirtyKb)
                .put("native_heap_bytes", nativeHeapBytes)
                .put("java_heap_bytes", javaHeapBytes)
        }

        companion object {
            fun capture(): MemorySnapshot {
                val memoryInfo = Debug.MemoryInfo()
                Debug.getMemoryInfo(memoryInfo)
                val runtime = Runtime.getRuntime()
                return MemorySnapshot(
                    totalPssKb = memoryInfo.totalPss.toLong(),
                    totalPrivateDirtyKb = memoryInfo.totalPrivateDirty.toLong(),
                    nativeHeapBytes = Debug.getNativeHeapAllocatedSize(),
                    javaHeapBytes = runtime.totalMemory() - runtime.freeMemory(),
                )
            }
        }
    }

    private class PeakMemorySampler(initial: List<MemorySnapshot>) : Closeable {
        private val running = AtomicBoolean(true)
        private val totalPssKb = AtomicLong(initial.maxOf(MemorySnapshot::totalPssKb))
        private val totalPrivateDirtyKb = AtomicLong(initial.maxOf(MemorySnapshot::totalPrivateDirtyKb))
        private val nativeHeapBytes = AtomicLong(initial.maxOf(MemorySnapshot::nativeHeapBytes))
        private val javaHeapBytes = AtomicLong(initial.maxOf(MemorySnapshot::javaHeapBytes))
        private val thread = Thread({ sampleUntilStopped() }, "opencc-memory-sampler").apply {
            priority = Thread.NORM_PRIORITY - 1
            start()
        }

        fun include(snapshot: MemorySnapshot) {
            totalPssKb.accumulateAndGet(snapshot.totalPssKb, ::max)
            totalPrivateDirtyKb.accumulateAndGet(snapshot.totalPrivateDirtyKb, ::max)
            nativeHeapBytes.accumulateAndGet(snapshot.nativeHeapBytes, ::max)
            javaHeapBytes.accumulateAndGet(snapshot.javaHeapBytes, ::max)
        }

        fun peak(): MemorySnapshot {
            return MemorySnapshot(
                totalPssKb = totalPssKb.get(),
                totalPrivateDirtyKb = totalPrivateDirtyKb.get(),
                nativeHeapBytes = nativeHeapBytes.get(),
                javaHeapBytes = javaHeapBytes.get(),
            )
        }

        override fun close() {
            running.set(false)
            thread.join(SAMPLER_JOIN_TIMEOUT_MILLIS)
            check(!thread.isAlive) { "OpenCC memory sampler did not stop" }
        }

        private fun sampleUntilStopped() {
            while (running.get()) {
                include(MemorySnapshot.capture())
                LockSupport.parkNanos(SAMPLER_INTERVAL_NANOS)
            }
        }
    }

    private companion object {
        const val ARGUMENT_ENGINE = "opencc_benchmark_engine"
        const val ARGUMENT_PHASE = "opencc_benchmark_phase"
        const val ENGINE_OFFICIAL = "official"
        const val PHASE_FIRST_LOAD = "first-load"
        const val PHASE_STEADY_STATE = "steady-state"
        const val RESULT_PREFIX = "OPENCC_BENCHMARK_JSON="
        const val RESULT_SCHEMA_VERSION = 1
        const val STATUS_BENCHMARK_RESULT = 2
        const val LOG_TAG = "OpenccM4Benchmark"
        const val WARMUP_ITERATIONS = 20
        const val WARM_ITERATIONS = 200
        const val BATCH_SIZE = 1024
        const val MEMORY_LONG_TEXT_ITERATIONS = 12
        const val SAMPLER_INTERVAL_NANOS = 2_000_000L
        const val SAMPLER_JOIN_TIMEOUT_MILLIS = 5_000L
        const val BENCHMARK_SENTENCE = "汉字转换软件开发网络连接数据处理，鼠标点击后显示里面的内容。OpenCC 😀 𠀀。"
        val BENCHMARK_TEXT = BENCHMARK_SENTENCE.repeat(32)
        val BENCHMARK_EXPECTED_TEXT = "漢字轉換軟件開發網絡連接數據處理，鼠標點擊後顯示裏面的內容。OpenCC 😀 𠀀。".repeat(32)
        val MEMORY_BENCHMARK_TEXT = BENCHMARK_TEXT.repeat(8)
        val MEMORY_BENCHMARK_EXPECTED_TEXT = BENCHMARK_EXPECTED_TEXT.repeat(8)
        val BATCH_SEGMENT = "汉字转换软件网络数据 OpenCC 😀 𠀀"
        val ENGINES = setOf(ENGINE_OFFICIAL)
        val PHASES = setOf(PHASE_FIRST_LOAD, PHASE_STEADY_STATE)
    }
}
