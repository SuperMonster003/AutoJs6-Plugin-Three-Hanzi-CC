package io.github.supermonster003.autojs6.plugin.opencc.nativebridge;

import android.content.Context;
import android.content.res.AssetManager;
import android.os.Process;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Locale;

/** Installs the official resource ZIP as one versioned, hash-verified file. */
final class OpenccResourceInstaller {
    private static final Object INSTALL_LOCK = new Object();
    private static volatile File installedArchive;
    private static volatile long installedArchiveLastModified;

    private OpenccResourceInstaller() {
        throw new AssertionError("No instances");
    }

    static File ensureInstalled(Context context) throws IOException {
        File cached = installedArchive;
        if (isUnchangedCachedArchive(cached)) {
            return cached;
        }

        synchronized (INSTALL_LOCK) {
            cached = installedArchive;
            if (isUnchangedCachedArchive(cached)) {
                return cached;
            }

            File versionDirectory = new File(
                    new File(context.getNoBackupFilesDir(), "opencc"),
                    BuildConfig.OPENCC_VERSION + "-" + BuildConfig.OPENCC_COMMIT.substring(0, 12)
            );
            ensureDirectory(versionDirectory);

            File target = new File(versionDirectory, BuildConfig.OPENCC_RESOURCE_ASSET);
            if (isExpectedArchive(target)) {
                rememberInstalledArchive(target);
                return target;
            }
            if (target.exists() && !target.delete()) {
                throw new IOException("Unable to remove invalid OpenCC resource archive: " + target);
            }

            File temporary = new File(
                    versionDirectory,
                    BuildConfig.OPENCC_RESOURCE_ASSET
                            + ".tmp-"
                            + Process.myPid()
                            + "-"
                            + Integer.toHexString(System.identityHashCode(Thread.currentThread()))
            );
            if (temporary.exists() && !temporary.delete()) {
                throw new IOException("Unable to remove stale OpenCC temporary archive: " + temporary);
            }

            try {
                copyAndVerify(context.getAssets(), temporary);
                if (!temporary.renameTo(target)) {
                    if (!isExpectedArchive(target)) {
                        throw new IOException("Unable to atomically install OpenCC resource archive: " + target);
                    }
                }
            } finally {
                if (temporary.exists()) {
                    // Best effort: a failed installation is retried after removing this file next time.
                    // File.deleteOnExit() is deliberately avoided because Android processes are long-lived.
                    //noinspection ResultOfMethodCallIgnored
                    temporary.delete();
                }
            }

            if (!isExpectedArchive(target)) {
                throw new IOException("Installed OpenCC resource archive failed verification: " + target);
            }
            rememberInstalledArchive(target);
            return target;
        }
    }

    private static boolean isUnchangedCachedArchive(File archive) {
        return archive != null
                && archive.isFile()
                && archive.length() == BuildConfig.OPENCC_RESOURCE_SIZE
                && archive.lastModified() == installedArchiveLastModified;
    }

    private static void rememberInstalledArchive(File archive) {
        installedArchiveLastModified = archive.lastModified();
        installedArchive = archive;
    }

    private static void ensureDirectory(File directory) throws IOException {
        if (directory.isDirectory()) {
            return;
        }
        if (directory.exists() || !directory.mkdirs()) {
            throw new IOException("Unable to create OpenCC resource directory: " + directory);
        }
    }

    private static boolean isExpectedArchive(File archive) throws IOException {
        return archive.isFile()
                && archive.length() == BuildConfig.OPENCC_RESOURCE_SIZE
                && BuildConfig.OPENCC_RESOURCE_SHA256.equals(sha256(archive));
    }

    private static void copyAndVerify(AssetManager assets, File target) throws IOException {
        MessageDigest digest = newSha256();
        long copied = 0L;
        try (
                InputStream input = new BufferedInputStream(
                        assets.open(BuildConfig.OPENCC_RESOURCE_ASSET_PATH, AssetManager.ACCESS_STREAMING)
                );
                FileOutputStream output = new FileOutputStream(target)
        ) {
            byte[] buffer = new byte[32 * 1024];
            int read;
            while ((read = input.read(buffer)) != -1) {
                output.write(buffer, 0, read);
                digest.update(buffer, 0, read);
                copied += read;
            }
            output.getFD().sync();
        }

        String actualDigest = toHex(digest.digest());
        if (copied != BuildConfig.OPENCC_RESOURCE_SIZE
                || !BuildConfig.OPENCC_RESOURCE_SHA256.equals(actualDigest)) {
            throw new IOException(
                    String.format(
                            Locale.ROOT,
                            "OpenCC resource asset mismatch: expected %d bytes/%s, found %d bytes/%s",
                            BuildConfig.OPENCC_RESOURCE_SIZE,
                            BuildConfig.OPENCC_RESOURCE_SHA256,
                            copied,
                            actualDigest
                    )
            );
        }
    }

    private static String sha256(File file) throws IOException {
        MessageDigest digest = newSha256();
        try (InputStream input = new BufferedInputStream(new FileInputStream(file))) {
            byte[] buffer = new byte[32 * 1024];
            int read;
            while ((read = input.read(buffer)) != -1) {
                digest.update(buffer, 0, read);
            }
        }
        return toHex(digest.digest());
    }

    private static MessageDigest newSha256() {
        try {
            return MessageDigest.getInstance("SHA-256");
        } catch (NoSuchAlgorithmException error) {
            throw new AssertionError("SHA-256 is unavailable", error);
        }
    }

    private static String toHex(byte[] digest) {
        StringBuilder output = new StringBuilder(digest.length * 2);
        for (byte value : digest) {
            output.append(Character.forDigit((value >>> 4) & 0x0f, 16));
            output.append(Character.forDigit(value & 0x0f, 16));
        }
        return output.toString();
    }
}
