package io.github.supermonster003.autojs6.plugin.opencc.nativebridge;

/** Reproducible upstream identity embedded into the generated library BuildConfig. */
public final class OpenccUpstream {
    private OpenccUpstream() {
        throw new AssertionError("No instances");
    }

    public static String version() {
        return BuildConfig.OPENCC_VERSION;
    }

    public static String tag() {
        return BuildConfig.OPENCC_TAG;
    }

    public static String commit() {
        return BuildConfig.OPENCC_COMMIT;
    }

    public static String resourceAsset() {
        return BuildConfig.OPENCC_RESOURCE_ASSET;
    }

    public static String resourceSha256() {
        return BuildConfig.OPENCC_RESOURCE_SHA256;
    }
}
