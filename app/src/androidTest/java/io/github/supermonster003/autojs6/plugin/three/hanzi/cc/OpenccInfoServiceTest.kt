package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.IBinder
import androidx.test.platform.app.InstrumentationRegistry
import org.autojs.plugin.common.api.IPluginInfoProvider
import org.junit.Assert.*
import org.junit.Test
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

class OpenccInfoServiceTest {
    @Test fun protectedCommonInfoEntryReturnsInstalledMetadata() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val intent = Intent("org.autojs.plugin.INFO").addCategory("opencc").setPackage(context.packageName)
        val matches = context.packageManager.queryIntentServices(intent, 0)
        assertEquals(1, matches.size)
        val entry = matches.single().serviceInfo
        assertEquals(ThreeHanziCcInfoService::class.java.name, entry.name)
        assertEquals("org.autojs.permission.PLUGIN", entry.permission)
        assertTrue(entry.exported)
        val ready = CountDownLatch(1)
        val service = AtomicReference<IBinder>()
        val connection = object : ServiceConnection {
            override fun onServiceConnected(name: ComponentName?, binder: IBinder?) { service.set(binder); ready.countDown() }
            override fun onServiceDisconnected(name: ComponentName?) = Unit
        }
        assertTrue(context.bindService(Intent(intent).setComponent(ComponentName(context.packageName, entry.name)), connection, Context.BIND_AUTO_CREATE))
        try {
            assertTrue(ready.await(10, TimeUnit.SECONDS))
            val binder = requireNotNull(service.get())
            assertEquals(IPluginInfoProvider::class.java.name, binder.interfaceDescriptor)
            val info = IPluginInfoProvider.Stub.asInterface(binder).info
            assertEquals("opencc", info.id)
            assertEquals("opencc", info.engine)
            assertEquals(context.packageManager.getPackageInfo(context.packageName, 0).versionName, info.versionName)
        } finally { context.unbindService(connection) }
    }
}
