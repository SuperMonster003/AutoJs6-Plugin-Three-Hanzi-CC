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
import org.autojs.plugin.common.api.PluginCapabilityKeys
import org.autojs.plugin.opencc.api.IOpenccPlugin
import org.autojs.plugin.opencc.api.OpenccConversionTypes
import org.autojs.plugin.opencc.api.OpenccPluginActions
import org.autojs.plugin.opencc.api.OpenccPluginIds
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test
import org.junit.runner.RunWith
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

@RunWith(AndroidJUnit4::class)
class OpenccPluginServiceTest {

    private val context = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun discoveryBindingMetadataAndAllConversionTypesRoundTrip() {
        withBoundPlugin { plugin ->
            assertRuntimeInfo(plugin)

            val smokeInput = "汉字漢字软件軟體里面裏面"
            for (conversionType in CONVERSION_TYPES) {
                val result = plugin.convert(smokeInput, conversionType)
                assertTrue("$conversionType returned an empty result", result.isNotEmpty())
            }

            assertEquals("漢字", plugin.convert("汉字", OpenccConversionTypes.S2T))
            assertEquals("汉字", plugin.convert("漢字", OpenccConversionTypes.T2S))

            try {
                plugin.convert("汉字", "NOT_A_CONVERSION")
                fail("Unknown conversion type must be rejected")
            } catch (error: IllegalArgumentException) {
                assertTrue(
                    "Unexpected unknown-type message: ${error.message}",
                    error.message.orEmpty().contains("NOT_A_CONVERSION"),
                )
            }
        }
    }

    private fun assertRuntimeInfo(plugin: IOpenccPlugin) {
        val info = plugin.info
        val packageInfo = context.packageManager.getPackageInfo(context.packageName, 0)

        assertEquals("OpenCC", info.name)
        assertTrue(info.description?.isNotBlank() == true)
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
        val CONVERSION_TYPES = listOf(
            OpenccConversionTypes.HK2S,
            OpenccConversionTypes.HK2T,
            OpenccConversionTypes.JP2T,
            OpenccConversionTypes.S2HK,
            OpenccConversionTypes.S2T,
            OpenccConversionTypes.S2TW,
            OpenccConversionTypes.S2TWP,
            OpenccConversionTypes.T2HK,
            OpenccConversionTypes.T2S,
            OpenccConversionTypes.T2TW,
            OpenccConversionTypes.T2JP,
            OpenccConversionTypes.TW2S,
            OpenccConversionTypes.TW2T,
            OpenccConversionTypes.TW2SP,
        )
    }
}
