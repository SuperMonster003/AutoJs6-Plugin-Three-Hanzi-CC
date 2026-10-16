package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

import android.app.Service
import android.content.Intent
import android.os.Bundle
import android.os.IBinder
import android.os.ParcelFileDescriptor
import android.os.RemoteException
import org.autojs.plugin.common.api.PluginInfo
import org.autojs.plugin.tool.api.IPluginToolCallback
import org.autojs.plugin.tool.api.IPluginToolProvider
import org.autojs.plugin.tool.api.PluginToolAcceptKeys
import org.autojs.plugin.tool.api.PluginToolCancelKeys
import org.autojs.plugin.tool.api.PluginToolCatalogKeys
import org.autojs.plugin.tool.api.PluginToolContract
import org.autojs.plugin.tool.api.PluginToolErrorCodes
import org.autojs.plugin.tool.api.PluginToolErrorKeys
import org.autojs.plugin.tool.api.PluginToolInvokeKeys
import org.autojs.plugin.tool.api.PluginToolResultKeys
import org.json.JSONObject
import java.util.Collections
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.RejectedExecutionException

/**
 * Provider of the AutoJs6 plugin tool contract v1 (action `org.autojs.plugin.TOOL_PROVIDER`): AutoJs6 reads the
 * [OpenccToolCatalog] and forwards `opencc_convert` calls here from MCP Server, agents and `plugins.tools`. Calls run
 * one at a time on a worker thread through the same [OpenccConversionCoordinator] as the OpenCC family service, so
 * the four concurrent calls the catalog allows queue here instead of failing as busy.
 */
class ThreeHanziCcToolService : Service() {

    private val coordinator by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
        OpenccConversionCoordinator.get(applicationContext)
    }

    private val worker: ExecutorService = Executors.newSingleThreadExecutor { runnable ->
        Thread(runnable, "opencc-tool").apply { isDaemon = true }
    }

    /** Invocation ids cancelled before their call started; bounded because cancels may arrive after a call ended. */
    private val cancelled: MutableSet<String> = Collections.synchronizedSet(
        Collections.newSetFromMap(object : LinkedHashMap<String, Boolean>() {
            override fun removeEldestEntry(eldest: MutableMap.MutableEntry<String, Boolean>?) = size > MAX_REMEMBERED_CANCELS
        }),
    )

    override fun onBind(intent: Intent?): IBinder = binder

    override fun onDestroy() {
        worker.shutdownNow()
        super.onDestroy()
    }

    private val binder = object : IPluginToolProvider.Stub() {

        override fun getInfo(): PluginInfo = pluginInfo(
            name = getString(R.string.app_name),
            description = getString(R.string.plugin_description),
        )

        override fun getCatalog(request: Bundle?): Bundle = Bundle().apply {
            putInt(PluginToolCatalogKeys.CONTRACT_VERSION, PluginToolContract.CONTRACT_VERSION)
            putString(PluginToolCatalogKeys.CATALOG_JSON, OpenccToolCatalog.json)
        }

        override fun invoke(request: Bundle?, inputs: Array<out ParcelFileDescriptor>?, callback: IPluginToolCallback?): Bundle {
            // The catalog declares no image or file parameters; close anything that arrives anyway.
            inputs?.forEach { runCatching { it.close() } }
            val invocationId = request?.getString(PluginToolInvokeKeys.INVOCATION_ID)
            if (request == null || callback == null || invocationId == null) {
                return refuse(PluginToolErrorCodes.FAILED, "the request is incomplete")
            }
            val version = request.getInt(PluginToolInvokeKeys.CONTRACT_VERSION)
            if (!PluginToolContract.supportsContractVersion(version)) {
                return refuse(PluginToolErrorCodes.UNSUPPORTED_CONTRACT_VERSION, "plugin tool contract version $version is not supported")
            }
            val tool = request.getString(PluginToolInvokeKeys.TOOL)
            if (tool != OpenccToolCatalog.TOOL_CONVERT) {
                return refuse(PluginToolErrorCodes.UNKNOWN_TOOL, "no tool \"$tool\"")
            }
            val (text, config) = try {
                val arguments = JSONObject(request.getString(PluginToolInvokeKeys.ARGUMENTS_JSON) ?: "{}")
                val text = arguments.opt("text") as? String ?: throw IllegalArgumentException("text must be a string")
                val config = if (arguments.isNull("config")) OpenccToolConfigs.DEFAULT else arguments.opt("config") as? String
                    ?: throw IllegalArgumentException("config must be a string")
                text to config
            } catch (e: Exception) {
                return refuse(PluginToolErrorCodes.INVALID_ARGUMENTS, e.message ?: e.toString())
            }
            val chain = try {
                OpenccToolConfigs.plan(text, config)
            } catch (e: IllegalArgumentException) {
                return refuse(PluginToolErrorCodes.INVALID_ARGUMENTS, e.message ?: e.toString())
            }
            try {
                worker.execute {
                    if (cancelled.remove(invocationId)) {
                        deliver { callback.onError(error(invocationId, PluginToolErrorCodes.CANCELLED, "cancelled before the conversion started")) }
                        return@execute
                    }
                    val converted = try {
                        coordinator.convertSteps(text, chain)
                    } catch (t: Throwable) {
                        deliver { callback.onError(error(invocationId, PluginToolErrorCodes.FAILED, "OpenCC conversion failed: ${t.message ?: t}")) }
                        return@execute
                    }
                    deliver {
                        callback.onResult(Bundle().apply {
                            putString(PluginToolResultKeys.INVOCATION_ID, invocationId)
                            putString(PluginToolResultKeys.RESULT_JSON, JSONObject().put("text", converted).put("config", config).toString())
                            putString(PluginToolResultKeys.TEXT, converted)
                            putString(PluginToolResultKeys.OUTPUTS_JSON, "[]")
                        }, emptyArray())
                    }
                }
            } catch (_: RejectedExecutionException) {
                return refuse(PluginToolErrorCodes.NOT_READY, "the OpenCC tool service is shutting down")
            }
            return Bundle().apply { putBoolean(PluginToolAcceptKeys.ACCEPTED, true) }
        }

        override fun cancel(request: Bundle?) {
            // A conversion takes milliseconds and cannot be interrupted; only calls still queued are dropped.
            request?.getString(PluginToolCancelKeys.INVOCATION_ID)?.let(cancelled::add)
        }
    }

    /** The host may be gone by the time a result is ready; there is nobody left to tell. */
    private inline fun deliver(block: () -> Unit) {
        try {
            block()
        } catch (_: RemoteException) {
        }
    }

    private fun refuse(code: String, message: String) = Bundle().apply {
        putBoolean(PluginToolAcceptKeys.ACCEPTED, false)
        putString(PluginToolAcceptKeys.ERROR_CODE, code)
        putString(PluginToolAcceptKeys.ERROR_MESSAGE, message)
    }

    private fun error(invocationId: String, code: String, message: String) = Bundle().apply {
        putString(PluginToolErrorKeys.INVOCATION_ID, invocationId)
        putString(PluginToolErrorKeys.CODE, code)
        putString(PluginToolErrorKeys.MESSAGE, message)
    }

    private companion object {
        const val MAX_REMEMBERED_CANCELS = 64
    }
}
