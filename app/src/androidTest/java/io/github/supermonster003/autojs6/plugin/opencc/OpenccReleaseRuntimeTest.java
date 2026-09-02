package io.github.supermonster003.autojs6.plugin.opencc;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import android.app.Activity;
import android.app.Instrumentation;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.os.Build;
import android.os.Bundle;
import android.os.IBinder;
import android.os.Parcel;
import android.os.SystemClock;
import android.view.View;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;

import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;

import org.junit.Test;
import org.junit.runner.RunWith;

import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.FutureTask;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Java-only probe used to drive an installed minified release with the separately signed
 * instrumentation APK. Keeping this class free of Kotlin runtime references avoids assuming that R8
 * retains test-only Kotlin helpers in the release target.
 */
@RunWith(AndroidJUnit4.class)
public final class OpenccReleaseRuntimeTest {

    private static final String ARG_EXPECTED_VERSION_NAME = "opencc_expected_version_name";
    private static final String ARG_EXPECTED_VERSION_CODE = "opencc_expected_version_code";
    private static final String PLUGIN_ACTION = "org.autojs.plugin.OPENCC";
    private static final String PLUGIN_CATEGORY = "opencc";
    private static final String PLUGIN_PERMISSION = "org.autojs.permission.PLUGIN";
    private static final String BINDER_DESCRIPTOR = "org.autojs.plugin.opencc.api.IOpenccPlugin";
    private static final int TRANSACTION_CONVERT = IBinder.FIRST_CALL_TRANSACTION + 1;
    private static final String SOURCE = "汉字软件 😀 𠀀";
    private static final String RESULT = "漢字軟件 😀 𠀀";
    private static final long TIMEOUT_MILLIS = 60_000L;

    private final Instrumentation instrumentation = InstrumentationRegistry.getInstrumentation();
    private final Context context = instrumentation.getTargetContext();

    @Test
    public void minifiedReleaseRetainsStandaloneAndBinderRuntime() throws Exception {
        Bundle arguments = InstrumentationRegistry.getArguments();
        String expectedVersionName = arguments.getString(ARG_EXPECTED_VERSION_NAME, "").trim();
        String expectedVersionCodeText = arguments.getString(ARG_EXPECTED_VERSION_CODE, "").trim();
        assertFalse("Expected version name argument is required", expectedVersionName.isEmpty());
        assertFalse("Expected version code argument is required", expectedVersionCodeText.isEmpty());
        long expectedVersionCode = Long.parseLong(expectedVersionCodeText);

        PackageManager packageManager = context.getPackageManager();
        PackageInfo packageInfo = packageManager.getPackageInfo(context.getPackageName(),
            PackageManager.GET_PERMISSIONS);
        assertEquals(expectedVersionName, packageInfo.versionName);
        assertEquals(expectedVersionCode, versionCode(packageInfo));
        assertEquals(0, packageInfo.applicationInfo.flags & ApplicationInfo.FLAG_DEBUGGABLE);
        assertEquals(
            Collections.singletonList(PLUGIN_PERMISSION),
            packageInfo.requestedPermissions == null
                ? Collections.emptyList()
                : java.util.Arrays.asList(packageInfo.requestedPermissions)
        );
        assertNotEquals(
            PackageManager.PERMISSION_GRANTED,
            packageManager.checkPermission(android.Manifest.permission.INTERNET, context.getPackageName())
        );

        Activity activity = launchStandalone(packageManager);
        try {
            assertStandaloneConversion(activity);
            assertBinderConversion(packageManager);
        } finally {
            onMain(() -> {
                if (!activity.isFinishing() && !activity.isDestroyed()) {
                    activity.finish();
                }
                return null;
            });
            instrumentation.waitForIdleSync();
        }
    }

    private Activity launchStandalone(PackageManager packageManager) {
        Intent launcher = packageManager.getLaunchIntentForPackage(context.getPackageName());
        assertNotNull("Release APK has no Launcher activity", launcher);
        List<ResolveInfo> launchers = packageManager.queryIntentActivities(launcher, 0);
        assertEquals("Release APK must expose exactly one Launcher", 1, launchers.size());
        assertTrue(
            "Unexpected Launcher class: " + launchers.get(0).activityInfo.name,
            launchers.get(0).activityInfo.name.endsWith(".OpenccActivity")
        );
        launcher.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        Activity activity = instrumentation.startActivitySync(launcher);
        assertNotNull(activity);
        assertEquals(context.getPackageName(), activity.getPackageName());
        return activity;
    }

    private void assertStandaloneConversion(Activity activity) throws Exception {
        EditText source = activity.findViewById(resourceId("source_text"));
        Spinner types = activity.findViewById(resourceId("conversion_type"));
        TextView result = activity.findViewById(resourceId("result_text"));
        View convert = activity.findViewById(resourceId("convert_button"));
        assertNotNull(source);
        assertNotNull(types);
        assertNotNull(result);
        assertNotNull(convert);

        onMain(() -> {
            source.setText(SOURCE);
            types.setSelection(0);
            assertTrue("Release conversion action must be enabled", convert.isEnabled());
            assertTrue("Release conversion action did not accept the click", convert.performClick());
            return null;
        });
        awaitText(result, RESULT);
        assertEquals(SOURCE, onMain(() -> source.getText().toString()));
    }

    private void assertBinderConversion(PackageManager packageManager) throws Exception {
        Intent discovery = new Intent(PLUGIN_ACTION)
            .addCategory(PLUGIN_CATEGORY)
            .setPackage(context.getPackageName());
        List<ResolveInfo> matches = packageManager.queryIntentServices(discovery, 0);
        assertEquals("Release APK must expose exactly one OpenCC plugin service", 1, matches.size());
        ResolveInfo match = matches.get(0);
        assertEquals(PLUGIN_PERMISSION, match.serviceInfo.permission);
        Intent explicit = new Intent(discovery).setComponent(
            new ComponentName(match.serviceInfo.packageName, match.serviceInfo.name)
        );

        CountDownLatch connected = new CountDownLatch(1);
        AtomicReference<IBinder> binderReference = new AtomicReference<>();
        ServiceConnection connection = new ServiceConnection() {
            @Override
            public void onServiceConnected(ComponentName name, IBinder service) {
                binderReference.set(service);
                connected.countDown();
            }

            @Override
            public void onServiceDisconnected(ComponentName name) {
                // No-op: the assertion completes before unbinding.
            }

            @Override
            public void onNullBinding(ComponentName name) {
                connected.countDown();
            }

            @Override
            public void onBindingDied(ComponentName name) {
                connected.countDown();
            }
        };

        assertTrue("Release plugin service refused binding", context.bindService(
            explicit,
            connection,
            Context.BIND_AUTO_CREATE
        ));
        try {
            assertTrue("Timed out binding the release plugin service",
                connected.await(20, TimeUnit.SECONDS));
            IBinder binder = binderReference.get();
            assertNotNull("Release plugin service returned a null Binder", binder);
            assertEquals(BINDER_DESCRIPTOR, binder.getInterfaceDescriptor());
            assertEquals(RESULT, rawConvert(binder, SOURCE, "S2T"));
        } finally {
            context.unbindService(connection);
        }
    }

    private static String rawConvert(IBinder binder, String text, String conversionType) throws Exception {
        Parcel data = Parcel.obtain();
        Parcel reply = Parcel.obtain();
        try {
            data.writeInterfaceToken(BINDER_DESCRIPTOR);
            data.writeString(text);
            data.writeString(conversionType);
            assertTrue("Legacy convert transaction 2 was not handled",
                binder.transact(TRANSACTION_CONVERT, data, reply, 0));
            reply.readException();
            return reply.readString();
        } finally {
            reply.recycle();
            data.recycle();
        }
    }

    private void awaitText(TextView view, String expected) throws Exception {
        long deadline = SystemClock.elapsedRealtime() + TIMEOUT_MILLIS;
        String actual = "";
        while (SystemClock.elapsedRealtime() < deadline) {
            instrumentation.waitForIdleSync();
            actual = onMain(() -> view.getText().toString());
            if (expected.equals(actual)) {
                return;
            }
            SystemClock.sleep(50L);
        }
        assertEquals("Timed out waiting for release Launcher conversion", expected, actual);
    }

    private int resourceId(String name) {
        int id = context.getResources().getIdentifier(name, "id", context.getPackageName());
        assertNotEquals("Missing release resource id/" + name, 0, id);
        return id;
    }

    private <T> T onMain(Callable<T> callable) throws Exception {
        FutureTask<T> task = new FutureTask<>(callable);
        instrumentation.runOnMainSync(task);
        return task.get(5, TimeUnit.SECONDS);
    }

    @SuppressWarnings("deprecation")
    private static long versionCode(PackageInfo packageInfo) {
        return Build.VERSION.SDK_INT >= Build.VERSION_CODES.P
            ? packageInfo.getLongVersionCode()
            : packageInfo.versionCode;
    }
}
