package io.github.supermonster003.autojs6.plugin.opencc.nativebridge;

import android.content.Context;

import java.io.Closeable;
import java.io.File;
import java.io.IOException;
import java.util.Objects;

/** Thread-safe JVM facade for the pinned official OpenCC engine. */
public final class OpenccNativeEngine implements Closeable {
    private final Context applicationContext;
    private boolean closed;

    static {
        System.loadLibrary("opencc_jni");
    }

    public OpenccNativeEngine(Context context) {
        Context appContext = Objects.requireNonNull(context, "context").getApplicationContext();
        applicationContext = appContext != null ? appContext : context;
    }

    public synchronized String convert(String text, OpenccConversionType conversionType) {
        ensureOpen();
        Objects.requireNonNull(text, "text");
        Objects.requireNonNull(conversionType, "conversionType");

        final File resourceArchive;
        try {
            resourceArchive = OpenccResourceInstaller.ensureInstalled(applicationContext);
        } catch (IOException error) {
            throw new IllegalStateException("Unable to prepare OpenCC " + OpenccUpstream.version() + " resources", error);
        }
        return nativeConvert(text, conversionType.configFile(), resourceArchive.getAbsolutePath());
    }

    @Override
    public synchronized void close() {
        if (closed) {
            return;
        }
        nativeClearCache();
        closed = true;
    }

    private void ensureOpen() {
        if (closed) {
            throw new IllegalStateException("OpenCC engine is closed");
        }
    }

    private static native String nativeConvert(String text, String configFile, String resourceArchivePath);

    private static native void nativeClearCache();
}
