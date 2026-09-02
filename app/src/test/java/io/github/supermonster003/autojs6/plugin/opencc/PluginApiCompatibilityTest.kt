package io.github.supermonster003.autojs6.plugin.opencc

import org.autojs.plugin.common.api.PluginInfo
import org.autojs.plugin.opencc.api.IOpenccPlugin
import org.autojs.plugin.opencc.api.OpenccPluginContract
import org.autojs.plugin.opencc.api.OpenccPluginIds
import org.junit.Assert.assertEquals
import org.junit.Test

class PluginApiCompatibilityTest {

    @Test
    fun aidlMethodsAndTransactionNumbersPreserveTheV1V2Contract() {
        val signatures = IOpenccPlugin::class.java.declaredMethods.associate { method ->
            method.name to MethodSignature(
                returnType = method.returnType.name,
                parameterTypes = method.parameterTypes.map { it.name },
            )
        }
        assertEquals(
            mapOf(
                "getInfo" to MethodSignature(PluginInfo::class.java.name, emptyList()),
                "convert" to MethodSignature(
                    String::class.java.name,
                    listOf(String::class.java.name, String::class.java.name),
                ),
                "getSupportedConversionTypes" to MethodSignature("java.util.List", emptyList()),
                "convertBatch" to MethodSignature(
                    "java.util.List",
                    listOf("java.util.List", String::class.java.name),
                ),
                "convertChain" to MethodSignature(
                    String::class.java.name,
                    listOf(String::class.java.name, "java.util.List"),
                ),
            ),
            signatures,
        )

        val transactions = IOpenccPlugin.Stub::class.java.declaredFields
            .filter { it.name.startsWith("TRANSACTION_") }
            .associate { field ->
                field.isAccessible = true
                field.name.removePrefix("TRANSACTION_") to field.getInt(null)
            }
        assertEquals(
            mapOf(
                "getInfo" to 1,
                "convert" to 2,
                "getSupportedConversionTypes" to 3,
                "convertBatch" to 4,
                "convertChain" to 5,
            ),
            transactions,
        )
        assertEquals(1, OpenccPluginContract.VERSION_LEGACY)
        assertEquals(2, OpenccPluginContract.VERSION_EXTENDED_CONVERSIONS)
        assertEquals(2, OpenccPluginContract.VERSION_CURRENT)
        assertEquals("opencc", OpenccPluginIds.ID)
        assertEquals("opencc", OpenccPluginIds.ENGINE)
        assertEquals("default", OpenccPluginIds.VARIANT_DEFAULT)
    }

    private data class MethodSignature(
        val returnType: String,
        val parameterTypes: List<String>,
    )
}
