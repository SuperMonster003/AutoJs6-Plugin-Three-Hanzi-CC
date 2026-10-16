package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.Bundle
import android.os.IBinder
import android.os.ParcelFileDescriptor
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType
import org.autojs.plugin.tool.api.IPluginToolCallback
import org.autojs.plugin.tool.api.IPluginToolProvider
import org.autojs.plugin.tool.api.PluginToolAcceptKeys
import org.autojs.plugin.tool.api.PluginToolCancelKeys
import org.autojs.plugin.tool.api.PluginToolCapabilityKeys
import org.autojs.plugin.tool.api.PluginToolCatalogKeys
import org.autojs.plugin.tool.api.PluginToolContract
import org.autojs.plugin.tool.api.PluginToolErrorCodes
import org.autojs.plugin.tool.api.PluginToolInvokeKeys
import org.autojs.plugin.tool.api.PluginToolResultKeys
import org.autojs.plugin.tool.api.PluginToolValues
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.util.UUID
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

/**
 * The plugin tool provider (AutoJs6 plugin tool contract v1) over the generated AIDL Proxy/Parcel path: discovery,
 * capability, catalog, conversions with native, alias and chained configs, and the refusals for bad requests.
 */
@RunWith(AndroidJUnit4::class)
class ThreeHanziCcToolServiceTest {

    private val context = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun discoveryCapabilityAndCatalog() {
        withBoundProvider { provider ->
            assertEquals(1, provider.info.capabilities?.getInt(PluginToolCapabilityKeys.CONTRACT_VERSION))

            val catalog = provider.getCatalog(Bundle().apply {
                putInt(PluginToolCatalogKeys.CONTRACT_VERSION, PluginToolContract.CONTRACT_VERSION)
            })
            assertEquals(PluginToolContract.CONTRACT_VERSION, catalog.getInt(PluginToolCatalogKeys.CONTRACT_VERSION))
            val json = JSONObject(catalog.getString(PluginToolCatalogKeys.CATALOG_JSON)!!)
            assertEquals("opencc", json.getString("shortName"))
            val tools = json.getJSONArray("tools")
            assertEquals(1, tools.length())
            val tool = tools.getJSONObject(0)
            assertEquals("convert", tool.getString("name"))
            assertEquals("readonly", tool.getString("risk"))
            val config = tool.getJSONObject("inputSchema").getJSONObject("properties").getJSONObject("config")
            assertEquals(32, config.getJSONArray("enum").length())
            assertEquals("s2t", config.getString("default"))
        }
    }

    @Test
    fun conversionsReturnTheTextAndTheConfig() {
        withBoundProvider { provider ->
            val defaulted = call(provider, JSONObject().put("text", SMOKE_INPUT))
            assertEquals("漢字漢字軟件軟體裏面裏面", defaulted.text)
            assertEquals(JSONObject().put("text", defaulted.text).put("config", "s2t").toString(), defaulted.resultJson)

            assertEquals("漢字漢字軟體軟體裡面裡面", call(provider, JSONObject().put("text", SMOKE_INPUT).put("config", "s2twi")).text)
            val chained = call(provider, JSONObject().put("text", SMOKE_INPUT).put("config", "s2jp"))
            val expected = OpenccConversionCoordinator.get(context).convertSteps(SMOKE_INPUT, listOf(OpenccConversionType.S2T, OpenccConversionType.T2JP))
            assertEquals(expected, chained.text)
            assertEquals("s2jp", JSONObject(chained.resultJson).getString("config"))
            assertEquals("", call(provider, JSONObject().put("text", "").put("config", "t2s")).text)
        }
    }

    @Test
    fun badRequestsAreRefusedWithTheirCodes() {
        withBoundProvider { provider ->
            assertRefused(provider, PluginToolErrorCodes.UNKNOWN_TOOL, "no tool \"translate\"", tool = "translate")
            assertRefused(provider, PluginToolErrorCodes.INVALID_ARGUMENTS, "unknown config \"S2T\"", JSONObject().put("text", "汉字").put("config", "S2T"))
            assertRefused(provider, PluginToolErrorCodes.INVALID_ARGUMENTS, "text must be a string", JSONObject().put("config", "s2t"))
            assertRefused(
                provider, PluginToolErrorCodes.INVALID_ARGUMENTS, "at most 16384 are allowed",
                JSONObject().put("text", "字".repeat(OpenccToolConfigs.MAX_TEXT_LENGTH + 1)),
            )
            assertRefused(provider, PluginToolErrorCodes.UNSUPPORTED_CONTRACT_VERSION, "version 99", JSONObject().put("text", "汉字"), version = 99)
            // A cancel for a call that already ended or never existed is harmless.
            provider.cancel(Bundle().apply {
                putString(PluginToolCancelKeys.INVOCATION_ID, "never-ran")
                putString(PluginToolCancelKeys.REASON, PluginToolValues.CANCEL_REASON_CALLER)
            })
            assertEquals("漢字", call(provider, JSONObject().put("text", "汉字")).text)
        }
    }

    private class Answer(val text: String?, val resultJson: String)

    private fun call(provider: IPluginToolProvider, arguments: JSONObject): Answer {
        val done = CountDownLatch(1)
        val result = AtomicReference<Bundle?>()
        val failure = AtomicReference<Bundle?>()
        val callback = object : IPluginToolCallback.Stub() {
            override fun onProgress(progress: Bundle?) = Unit

            override fun onResult(bundle: Bundle?, outputs: Array<out ParcelFileDescriptor>?) {
                result.set(bundle)
                done.countDown()
            }

            override fun onError(error: Bundle?) {
                failure.set(error)
                done.countDown()
            }
        }
        val accepted = provider.invoke(request("convert", arguments), emptyArray(), callback)
        assertTrue(accepted.getString(PluginToolAcceptKeys.ERROR_MESSAGE), accepted.getBoolean(PluginToolAcceptKeys.ACCEPTED))
        assertTrue("the tool did not answer", done.await(15, TimeUnit.SECONDS))
        failure.get()?.let { throw AssertionError("the tool failed: ${it.keySet().associateWith { key -> it.get(key) }}") }
        val bundle = assertNotNullAndGet(result.get())
        assertEquals("[]", bundle.getString(PluginToolResultKeys.OUTPUTS_JSON))
        return Answer(bundle.getString(PluginToolResultKeys.TEXT), bundle.getString(PluginToolResultKeys.RESULT_JSON)!!)
    }

    private fun assertRefused(
        provider: IPluginToolProvider,
        code: String,
        message: String,
        arguments: JSONObject = JSONObject(),
        tool: String = "convert",
        version: Int = PluginToolContract.CONTRACT_VERSION,
    ) {
        val callback = object : IPluginToolCallback.Stub() {
            override fun onProgress(progress: Bundle?) = Unit
            override fun onResult(bundle: Bundle?, outputs: Array<out ParcelFileDescriptor>?) = throw AssertionError("a refused call answered")
            override fun onError(error: Bundle?) = throw AssertionError("a refused call answered")
        }
        val answer = provider.invoke(request(tool, arguments, version), emptyArray(), callback)
        assertFalse(answer.getBoolean(PluginToolAcceptKeys.ACCEPTED))
        assertEquals(code, answer.getString(PluginToolAcceptKeys.ERROR_CODE))
        val text = answer.getString(PluginToolAcceptKeys.ERROR_MESSAGE).orEmpty()
        assertTrue(text, text.contains(message))
    }

    private fun request(tool: String, arguments: JSONObject, version: Int = PluginToolContract.CONTRACT_VERSION) = Bundle().apply {
        putInt(PluginToolInvokeKeys.CONTRACT_VERSION, version)
        putString(PluginToolInvokeKeys.INVOCATION_ID, UUID.randomUUID().toString())
        putString(PluginToolInvokeKeys.TOOL, tool)
        putString(PluginToolInvokeKeys.ARGUMENTS_JSON, arguments.toString())
        putString(PluginToolInvokeKeys.INPUTS_JSON, "[]")
        putString(PluginToolInvokeKeys.OUTPUTS_JSON, "[]")
        putLong(PluginToolInvokeKeys.TIMEOUT_MS, 10_000L)
        putString(PluginToolInvokeKeys.CONSUMER, PluginToolValues.CONSUMER_SCRIPT)
    }

    private fun <T> assertNotNullAndGet(value: T?): T {
        assertNotNull(value)
        return value!!
    }

    private fun withBoundProvider(block: (IPluginToolProvider) -> Unit) {
        val discoveryIntent = Intent(PluginToolContract.SERVICE_ACTION).setPackage(context.packageName)
        @Suppress("DEPRECATION")
        val matches = context.packageManager.queryIntentServices(discoveryIntent, 0)
        assertEquals("the tool provider discovery must resolve exactly one service", 1, matches.size)
        val serviceInfo = matches.single().serviceInfo
        assertEquals("${context.packageName}.ThreeHanziCcToolService", serviceInfo.name)
        assertEquals("org.autojs.permission.PLUGIN", serviceInfo.permission)

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
        }
        val explicitIntent = Intent(discoveryIntent).setComponent(ComponentName(serviceInfo.packageName, serviceInfo.name))
        assertTrue("unable to bind the tool provider", context.bindService(explicitIntent, connection, Context.BIND_AUTO_CREATE))
        try {
            assertTrue("timed out binding the tool provider", latch.await(15, TimeUnit.SECONDS))
            block(remotePluginToolProvider(assertNotNullAndGet(binder.get())))
        } finally {
            context.unbindService(connection)
        }
    }

    private companion object {
        const val SMOKE_INPUT = "汉字漢字软件軟體里面裏面"
    }
}
