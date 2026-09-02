package io.github.supermonster003.autojs6.plugin.opencc;

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

import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.FutureTask;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Platform-only probe used to drive an installed minified release with the separately signed
 * instrumentation APK. It deliberately avoids AndroidX, JUnit, and Kotlin at runtime so the test
 * process does not assume that R8 retains classes needed only by the normal debug test runner.
 */
public final class OpenccReleaseProbeInstrumentation extends Instrumentation {

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

    private Bundle arguments;
    private Context context;

    @Override
    public void onCreate(Bundle arguments) {
        super.onCreate(arguments);
        this.arguments = arguments == null ? Bundle.EMPTY : new Bundle(arguments);
        start();
    }

    @Override
    public void onStart() {
        Bundle result = new Bundle();
        try {
            context = getTargetContext();
            String expectedVersionName = requiredArgument(ARG_EXPECTED_VERSION_NAME);
            long expectedVersionCode = Long.parseLong(requiredArgument(ARG_EXPECTED_VERSION_CODE));
            runProbe(expectedVersionName, expectedVersionCode);
            result.putString(
                "stream",
                "\nRELEASE_RUNTIME_OK version=" + expectedVersionName
                    + " versionCode=" + expectedVersionCode + "\n"
            );
            finish(Activity.RESULT_OK, result);
        } catch (Throwable throwable) {
            StringWriter stack = new StringWriter();
            throwable.printStackTrace(new PrintWriter(stack));
            result.putString("shortMsg", throwable.toString());
            result.putString("stream", "\nRELEASE_RUNTIME_FAILED\n" + stack + "\n");
            finish(Activity.RESULT_CANCELED, result);
        }
    }

    private void runProbe(String expectedVersionName, long expectedVersionCode) throws Exception {
        PackageManager packageManager = context.getPackageManager();
        PackageInfo packageInfo = packageManager.getPackageInfo(
            context.getPackageName(),
            PackageManager.GET_PERMISSIONS
        );
        requireEquals(expectedVersionName, packageInfo.versionName, "Unexpected release versionName");
        requireEquals(expectedVersionCode, versionCode(packageInfo), "Unexpected release versionCode");
        require(
            (packageInfo.applicationInfo.flags & ApplicationInfo.FLAG_DEBUGGABLE) == 0,
            "Release target is debuggable"
        );
        requireEquals(
            Collections.singletonList(PLUGIN_PERMISSION),
            packageInfo.requestedPermissions == null
                ? Collections.emptyList()
                : Arrays.asList(packageInfo.requestedPermissions),
            "Unexpected requested permissions"
        );
        require(
            packageManager.checkPermission(
                android.Manifest.permission.INTERNET,
                context.getPackageName()
            ) != PackageManager.PERMISSION_GRANTED,
            "Release target unexpectedly has INTERNET"
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
            waitForIdleSync();
        }
    }

    private Activity launchStandalone(PackageManager packageManager) {
        Intent launcher = packageManager.getLaunchIntentForPackage(context.getPackageName());
        require(launcher != null, "Release APK has no Launcher activity");
        List<ResolveInfo> launchers = packageManager.queryIntentActivities(launcher, 0);
        requireEquals(1, launchers.size(), "Release APK must expose exactly one Launcher");
        require(
            launchers.get(0).activityInfo.name.endsWith(".OpenccActivity"),
            "Unexpected Launcher class: " + launchers.get(0).activityInfo.name
        );
        launcher.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        Activity activity = startActivitySync(launcher);
        require(activity != null, "Could not launch OpenccActivity");
        requireEquals(context.getPackageName(), activity.getPackageName(), "Unexpected activity package");
        return activity;
    }

    private void assertStandaloneConversion(Activity activity) throws Exception {
        EditText source = activity.findViewById(resourceId("source_text"));
        Spinner types = activity.findViewById(resourceId("conversion_type"));
        TextView converted = activity.findViewById(resourceId("result_text"));
        View convert = activity.findViewById(resourceId("convert_button"));
        require(source != null, "Missing source editor");
        require(types != null, "Missing conversion type selector");
        require(converted != null, "Missing result view");
        require(convert != null, "Missing conversion action");

        onMain(() -> {
            source.setText(SOURCE);
            types.setSelection(0);
            require(convert.isEnabled(), "Release conversion action must be enabled");
            require(convert.performClick(), "Release conversion action did not accept the click");
            return null;
        });
        awaitText(converted, RESULT);
        requireEquals(SOURCE, onMain(() -> source.getText().toString()), "Source text was mutated");
    }

    private void assertBinderConversion(PackageManager packageManager) throws Exception {
        Intent discovery = new Intent(PLUGIN_ACTION)
            .addCategory(PLUGIN_CATEGORY)
            .setPackage(context.getPackageName());
        List<ResolveInfo> matches = packageManager.queryIntentServices(discovery, 0);
        requireEquals(1, matches.size(), "Release APK must expose exactly one OpenCC plugin service");
        ResolveInfo match = matches.get(0);
        requireEquals(PLUGIN_PERMISSION, match.serviceInfo.permission, "Unexpected service permission");
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

        require(
            context.bindService(explicit, connection, Context.BIND_AUTO_CREATE),
            "Release plugin service refused binding"
        );
        try {
            require(connected.await(20, TimeUnit.SECONDS), "Timed out binding the release plugin service");
            IBinder binder = binderReference.get();
            require(binder != null, "Release plugin service returned a null Binder");
            requireEquals(BINDER_DESCRIPTOR, binder.getInterfaceDescriptor(), "Unexpected Binder descriptor");
            requireEquals(RESULT, rawConvert(binder, SOURCE, "S2T"), "Unexpected Binder conversion");
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
            require(
                binder.transact(TRANSACTION_CONVERT, data, reply, 0),
                "Legacy convert transaction 2 was not handled"
            );
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
            waitForIdleSync();
            actual = onMain(() -> view.getText().toString());
            if (expected.equals(actual)) {
                return;
            }
            SystemClock.sleep(50L);
        }
        requireEquals(expected, actual, "Timed out waiting for release Launcher conversion");
    }

    private int resourceId(String name) {
        int id = context.getResources().getIdentifier(name, "id", context.getPackageName());
        require(id != 0, "Missing release resource id/" + name);
        return id;
    }

    private String requiredArgument(String name) {
        String value = arguments.getString(name, "").trim();
        require(!value.isEmpty(), "Required instrumentation argument is missing: " + name);
        return value;
    }

    private <T> T onMain(Callable<T> callable) throws Exception {
        FutureTask<T> task = new FutureTask<>(callable);
        runOnMainSync(task);
        return task.get(5, TimeUnit.SECONDS);
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    private static void requireEquals(Object expected, Object actual, String message) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new AssertionError(message + ": expected=" + expected + ", actual=" + actual);
        }
    }

    private static void requireEquals(long expected, long actual, String message) {
        if (expected != actual) {
            throw new AssertionError(message + ": expected=" + expected + ", actual=" + actual);
        }
    }

    @SuppressWarnings("deprecation")
    private static long versionCode(PackageInfo packageInfo) {
        return Build.VERSION.SDK_INT >= Build.VERSION_CODES.P
            ? packageInfo.getLongVersionCode()
            : packageInfo.versionCode;
    }
}
