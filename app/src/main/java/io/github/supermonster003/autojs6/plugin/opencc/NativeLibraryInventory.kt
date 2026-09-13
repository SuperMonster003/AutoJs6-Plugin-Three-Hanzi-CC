package io.github.supermonster003.autojs6.plugin.opencc

import android.content.Context
import android.os.Build
import java.io.File
import java.util.zip.ZipFile

internal object NativeLibraryInventory {

    private const val NATIVE_LIBRARY_FILE_NAME = "libopencc_jni.so"

    private val supportedAbis = listOf(
        "arm64-v8a",
        "armeabi-v7a",
        "x86",
        "x86_64",
    )

    fun supportedAbis(context: Context): Array<String> {
        val applicationInfo = context.applicationInfo
        return supportedAbisFromApks(
            apkPaths = (listOfNotNull(applicationInfo.sourceDir) + applicationInfo.splitSourceDirs.orEmpty())
                .map(::File),
            extractedLibrary = applicationInfo.nativeLibraryDir?.let { File(it, NATIVE_LIBRARY_FILE_NAME) },
            is64Bit = android.os.Process.is64Bit(),
            supported32BitAbis = Build.SUPPORTED_32_BIT_ABIS.toList(),
            supported64BitAbis = Build.SUPPORTED_64_BIT_ABIS.toList(),
        )
    }

    fun supportedAbisFromApks(
        apkPaths: Iterable<File>,
        extractedLibrary: File?,
        is64Bit: Boolean,
        supported32BitAbis: List<String>,
        supported64BitAbis: List<String>,
    ): Array<String> {
        val entries = buildSet {
            apkPaths.forEach { path ->
                runCatching {
                    ZipFile(path).use { zip ->
                        val enumeration = zip.entries()
                        while (enumeration.hasMoreElements()) {
                            add(enumeration.nextElement().name)
                        }
                    }
                }
            }
        }
        val packagedAbis = supportedAbis(entries)
        if (packagedAbis.isNotEmpty()) return packagedAbis

        val loadedAbi = processSupportedAbis(
            is64Bit = is64Bit,
            supported32BitAbis = supported32BitAbis,
            supported64BitAbis = supported64BitAbis,
        ).firstOrNull { it in supportedAbis }
            .takeIf { extractedLibrary?.isFile == true }
        return listOfNotNull(loadedAbi).toTypedArray()
    }

    fun supportedAbis(entryNames: Iterable<String>): Array<String> {
        val entries = entryNames.toHashSet()
        return supportedAbis.filter { abi ->
            "lib/$abi/$NATIVE_LIBRARY_FILE_NAME" in entries
        }.toTypedArray()
    }

    fun processSupportedAbis(
        is64Bit: Boolean,
        supported32BitAbis: List<String>,
        supported64BitAbis: List<String>,
    ): List<String> = if (is64Bit) supported64BitAbis else supported32BitAbis
}
