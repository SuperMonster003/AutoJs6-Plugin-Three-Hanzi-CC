package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

class NativeLibraryInventoryTest {

    @get:Rule
    val temporaryFolder = TemporaryFolder()

    private fun apk(name: String, vararg entries: String): File {
        val file = temporaryFolder.newFile(name)
        ZipOutputStream(file.outputStream()).use { zip ->
            entries.forEach { entry ->
                zip.putNextEntry(ZipEntry(entry))
                zip.write(byteArrayOf(0x01))
                zip.closeEntry()
            }
        }
        return file
    }

    private fun supportedAbisFromApks(
        apkPaths: Iterable<File>,
        extractedLibrary: File? = null,
        is64Bit: Boolean = true,
        supported32BitAbis: List<String> = listOf("armeabi-v7a", "x86"),
        supported64BitAbis: List<String> = listOf("arm64-v8a", "x86_64"),
    ) = NativeLibraryInventory.supportedAbisFromApks(
        apkPaths,
        extractedLibrary,
        is64Bit,
        supported32BitAbis,
        supported64BitAbis,
    )

    @Test
    fun `reports only packaged MediaInfo ABIs in canonical order`() {
        val entries = listOf(
            "lib/x86_64/libopencc_jni.so",
            "lib/arm64-v8a/libopencc_jni.so",
            "lib/x86_64/libc++_shared.so",
            "classes.dex",
        )

        assertArrayEquals(
            arrayOf("arm64-v8a", "x86_64"),
            NativeLibraryInventory.supportedAbis(entries),
        )
    }

    @Test
    fun `ignores wrong library names and unsupported ABIs`() {
        val entries = listOf(
            "lib/arm64-v8a/libmediainfo_wrong.so",
            "lib/riscv64/libopencc_jni.so",
        )

        assertArrayEquals(emptyArray<String>(), NativeLibraryInventory.supportedAbis(entries))
    }

    @Test
    fun `reports all four ABIs from a universal APK`() {
        val universal = apk(
            "universal.apk",
            "lib/x86_64/libopencc_jni.so",
            "lib/armeabi-v7a/libopencc_jni.so",
            "lib/arm64-v8a/libopencc_jni.so",
            "lib/x86/libopencc_jni.so",
        )

        assertArrayEquals(
            arrayOf("arm64-v8a", "armeabi-v7a", "x86", "x86_64"),
            supportedAbisFromApks(listOf(universal)),
        )
    }

    @Test
    fun `reports one ABI from a single architecture APK`() {
        val singleArchitecture = apk("arm64.apk", "lib/arm64-v8a/libopencc_jni.so")

        assertArrayEquals(arrayOf("arm64-v8a"), supportedAbisFromApks(listOf(singleArchitecture)))
    }

    @Test
    fun `combines native libraries found across base and split APKs`() {
        val base = apk("base.apk", "classes.dex")
        val arm64Split = apk("split-arm64.apk", "lib/arm64-v8a/libopencc_jni.so")
        val x86Split = apk("split-x86.apk", "lib/x86/libopencc_jni.so")

        assertArrayEquals(
            arrayOf("arm64-v8a", "x86"),
            supportedAbisFromApks(listOf(base, x86Split, arm64Split)),
        )
    }

    @Test
    fun `continues scanning after missing and corrupt APK paths`() {
        val missing = File(temporaryFolder.root, "missing.apk")
        val corrupt = temporaryFolder.newFile("corrupt.apk").apply { writeText("not a zip") }
        val validSplit = apk("valid-split.apk", "lib/x86_64/libopencc_jni.so")

        assertArrayEquals(
            arrayOf("x86_64"),
            supportedAbisFromApks(listOf(missing, corrupt, validSplit)),
        )
    }

    @Test
    fun `reports no ABI when packages and extracted directory contain no MediaInfo runtime`() {
        val base = apk("base-without-native.apk", "classes.dex")

        assertArrayEquals(emptyArray<String>(), supportedAbisFromApks(listOf(base)))
    }

    @Test
    fun `falls back to extracted library ABI when APK paths cannot be read`() {
        val extractedLibrary = temporaryFolder.newFile("libopencc_jni.so")

        assertArrayEquals(
            arrayOf("armeabi-v7a"),
            supportedAbisFromApks(
                apkPaths = listOf(File(temporaryFolder.root, "missing.apk")),
                extractedLibrary = extractedLibrary,
                is64Bit = false,
            ),
        )
        assertArrayEquals(
            arrayOf("arm64-v8a"),
            supportedAbisFromApks(
                apkPaths = emptyList(),
                extractedLibrary = extractedLibrary,
                is64Bit = true,
                supported64BitAbis = listOf("riscv64", "arm64-v8a"),
            ),
        )
    }

    @Test
    fun `fallback ABI follows current process bitness`() {
        val supported32BitAbis = listOf("armeabi-v7a", "x86")
        val supported64BitAbis = listOf("arm64-v8a", "x86_64")

        assertEquals(
            supported32BitAbis,
            NativeLibraryInventory.processSupportedAbis(false, supported32BitAbis, supported64BitAbis),
        )
        assertEquals(
            supported64BitAbis,
            NativeLibraryInventory.processSupportedAbis(true, supported32BitAbis, supported64BitAbis),
        )
    }
}
