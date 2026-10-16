package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

import android.os.Binder
import android.os.IBinder
import android.os.IInterface
import android.os.Parcel
import org.autojs.plugin.opencc.api.IOpenccPlugin
import org.autojs.plugin.tool.api.IPluginToolProvider

/** Forces the generated AIDL Proxy/Parcel path even though instrumentation shares the app process. */
internal fun remoteOpenccPlugin(target: IBinder): IOpenccPlugin {
    return IOpenccPlugin.Stub.asInterface(RemoteOnlyBinder(target))
}

/** The same Proxy/Parcel path for the plugin tool provider. */
internal fun remotePluginToolProvider(target: IBinder): IPluginToolProvider {
    return IPluginToolProvider.Stub.asInterface(RemoteOnlyBinder(target))
}

private class RemoteOnlyBinder(
    private val target: IBinder,
) : Binder() {
    override fun queryLocalInterface(descriptor: String): IInterface? = null

    override fun onTransact(code: Int, data: Parcel, reply: Parcel?, flags: Int): Boolean {
        return target.transact(code, data, reply, flags)
    }
}
