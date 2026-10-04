package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.appcompat.app.AlertDialog
import com.google.android.material.snackbar.Snackbar
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.ui.materialDialog
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.ui.showSnackbar
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.TimeUnit
import kotlin.math.max

internal data class AppRelease(
    val tag: String,
    val name: String,
    val notes: String,
    val pageUrl: String,
)

internal object UpdateVersionPolicy {
    private val VERSION_PATTERN =
        Regex("^[vV]?([0-9]+(?:\\.[0-9]+)*)(?:-([0-9A-Za-z.-]+))?(?:\\+[0-9A-Za-z.-]+)?$")

    fun isNewer(candidateTag: String, installedVersion: String): Boolean {
        val candidate = parse(candidateTag) ?: return false
        val installed = parse(installedVersion) ?: return false
        val length = max(candidate.numbers.size, installed.numbers.size)
        for (index in 0 until length) {
            val left = candidate.numbers.getOrElse(index) { 0 }
            val right = installed.numbers.getOrElse(index) { 0 }
            if (left != right) return left > right
        }
        // Same numeric version: a full release supersedes its own pre-releases.
        return when {
            candidate.preRelease == installed.preRelease -> false
            candidate.preRelease == null -> true
            installed.preRelease == null -> false
            else -> comparePreRelease(candidate.preRelease, installed.preRelease) > 0
        }
    }

    private data class ParsedVersion(val numbers: List<Int>, val preRelease: String?)

    private fun comparePreRelease(candidate: String, installed: String): Int {
        val left = candidate.split('.')
        val right = installed.split('.')
        for (index in 0 until minOf(left.size, right.size)) {
            val candidatePart = left[index]
            val installedPart = right[index]
            if (candidatePart == installedPart) continue
            val candidateNumeric = candidatePart.all(Char::isDigit)
            val installedNumeric = installedPart.all(Char::isDigit)
            return when {
                candidateNumeric && installedNumeric -> {
                    // Length comparison also supports numeric identifiers larger than Long.
                    val byLength = candidatePart.length.compareTo(installedPart.length)
                    if (byLength != 0) byLength else candidatePart.compareTo(installedPart)
                }
                candidateNumeric -> -1
                installedNumeric -> 1
                else -> candidatePart.compareTo(installedPart)
            }
        }
        return left.size.compareTo(right.size)
    }

    private fun parse(value: String): ParsedVersion? {
        val match = VERSION_PATTERN.matchEntire(value.trim()) ?: return null
        val numbers = match.groupValues[1]
            .split('.')
            .map { part -> part.toIntOrNull() ?: return null }
        val preRelease = match.groups[2]?.value
        if (preRelease != null && preRelease.split('.').any { identifier ->
                identifier.isEmpty() ||
                    (identifier.length > 1 && identifier.all(Char::isDigit) && identifier.startsWith('0'))
            }) return null
        return ParsedVersion(numbers, preRelease)
    }
}

internal class AppUpdateSettingsStore(context: Context) {
    private val preferences = context.applicationContext.getSharedPreferences(
        PREFERENCES_NAME,
        Context.MODE_PRIVATE,
    )

    var automaticChecksEnabled: Boolean
        get() = preferences.getBoolean(KEY_AUTOMATIC_CHECKS, true)
        set(value) {
            preferences.edit().putBoolean(KEY_AUTOMATIC_CHECKS, value).apply()
        }

    fun ignoredTags(): Set<String> =
        preferences.getStringSet(KEY_IGNORED_TAGS, emptySet()).orEmpty().toSet()

    fun ignore(tag: String) {
        preferences.edit().putStringSet(KEY_IGNORED_TAGS, ignoredTags() + tag).apply()
    }

    fun stopIgnoring(tags: Collection<String>) {
        preferences.edit().putStringSet(KEY_IGNORED_TAGS, ignoredTags() - tags.toSet()).apply()
    }

    fun shouldCheckAutomatically(now: Long = System.currentTimeMillis()): Boolean {
        if (!automaticChecksEnabled) return false
        val lastAttempt = preferences.getLong(KEY_LAST_AUTOMATIC_ATTEMPT, 0L)
        return lastAttempt <= 0L || now - lastAttempt >= AUTOMATIC_CHECK_INTERVAL_MILLIS
    }

    fun recordAutomaticAttempt(now: Long = System.currentTimeMillis()) {
        preferences.edit().putLong(KEY_LAST_AUTOMATIC_ATTEMPT, now).apply()
    }

    private companion object {
        const val PREFERENCES_NAME = "app-update-settings"
        const val KEY_AUTOMATIC_CHECKS = "automatic-checks"
        const val KEY_IGNORED_TAGS = "ignored-tags"
        const val KEY_LAST_AUTOMATIC_ATTEMPT = "last-automatic-attempt"
        const val AUTOMATIC_CHECK_INTERVAL_MILLIS = 12L * 60L * 60L * 1000L
    }
}

/** One cancellable release request; cancelling from any thread aborts the in-flight transfer. */
internal class UpdateCall {
    @Volatile
    private var cancelled = false

    @Volatile
    internal var connection: HttpURLConnection? = null

    fun cancel() {
        cancelled = true
        runCatching { connection?.disconnect() }
    }

    fun isCanceled(): Boolean = cancelled
}

/**
 * Queries the newest GitHub release over plain [HttpURLConnection]: 15s/20s/30s
 * connect/read/overall timeouts, no redirects, and a 256 KiB response cap. The callback always
 * fires exactly once, on the request thread; cancellation surfaces as a failure result.
 */
internal class AppUpdateChecker(
    private val latestReleaseUrl: String = LATEST_RELEASE_URL,
) {
    fun check(callback: (Result<AppRelease>) -> Unit): UpdateCall {
        val call = UpdateCall()
        Thread({ callback(runCatching { fetchRelease(call) }) }, "opencc-update-check").apply {
            isDaemon = true
            start()
        }
        return call
    }

    private fun fetchRelease(call: UpdateCall): AppRelease {
        val deadline = System.nanoTime() + TimeUnit.MILLISECONDS.toNanos(CALL_TIMEOUT_MILLIS)
        val connection = URL(latestReleaseUrl).openConnection() as HttpURLConnection
        call.connection = connection
        try {
            if (call.isCanceled()) throw IOException("Update check cancelled")
            connection.connectTimeout = CONNECT_TIMEOUT_MILLIS
            connection.readTimeout = READ_TIMEOUT_MILLIS
            connection.instanceFollowRedirects = false
            connection.requestMethod = "GET"
            connection.setRequestProperty("Accept", "application/vnd.github+json")
            connection.setRequestProperty("User-Agent", USER_AGENT)
            val status = connection.responseCode
            require(status in 200..299) { "Unexpected release response: HTTP $status" }
            require(connection.contentLengthLong <= MAXIMUM_RESPONSE_BYTES) {
                "Release response too large"
            }
            val body = connection.inputStream.use { stream -> readCapped(stream, deadline) }
            return decodeRelease(body)
        } finally {
            call.connection = null
            connection.disconnect()
        }
    }

    private fun readCapped(stream: InputStream, deadlineNanos: Long): String {
        val output = ByteArrayOutputStream()
        val buffer = ByteArray(8 * 1024)
        while (true) {
            // Read timeouts only bound one stalled read; a trickling stream needs a deadline.
            if (System.nanoTime() >= deadlineNanos) throw IOException("Update check timed out")
            val read = stream.read(buffer)
            if (read < 0) break
            output.write(buffer, 0, read)
            require(output.size() <= MAXIMUM_RESPONSE_BYTES) { "Release response too large" }
        }
        return output.toString(Charsets.UTF_8.name())
    }

    private fun decodeRelease(body: String): AppRelease {
        val json = JSONObject(body)
        val tag = json.optString("tag_name").trim()
        require(TAG_PATTERN.matches(tag)) { "Unexpected release tag" }
        return AppRelease(
            tag = tag,
            name = json.optString("name").trim().ifEmpty { tag },
            notes = json.optString("body").take(MAXIMUM_NOTES_LENGTH),
            pageUrl = "$RELEASES_PAGE_URL/tag/$tag",
        )
    }

    companion object {
        const val LATEST_RELEASE_URL =
            "https://api.github.com/repos/SuperMonster003/AutoJs6-Plugin-Three-Hanzi-CC/releases/latest"
        const val RELEASES_PAGE_URL =
            "https://github.com/SuperMonster003/AutoJs6-Plugin-Three-Hanzi-CC/releases"
        private const val USER_AGENT = "AutoJs6-Plugin-Three-Hanzi-CC-update-checker"
        private const val CONNECT_TIMEOUT_MILLIS = 15_000
        private const val READ_TIMEOUT_MILLIS = 20_000
        private const val CALL_TIMEOUT_MILLIS = 30_000L
        private const val MAXIMUM_RESPONSE_BYTES = 256L * 1024L
        private const val MAXIMUM_NOTES_LENGTH = 6_000
        private val TAG_PATTERN = Regex("^[0-9A-Za-z._-]{1,100}$")
    }
}

/**
 * Drives manual and automatic update checks for one Activity: at most one request in flight,
 * a cancellable progress dialog for manual checks, and quiet failures for automatic ones.
 */
internal class AppUpdateController(
    private val activity: ConfiguredActivity,
    private val store: AppUpdateSettingsStore,
    private val checker: AppUpdateChecker = AppUpdateChecker(),
) {
    private var activeCall: UpdateCall? = null
    private var progressDialog: AlertDialog? = null

    fun checkManually() = check(manual = true)

    fun checkAutomaticallyIfDue() {
        if (!store.shouldCheckAutomatically() || activeCall != null) return
        // Record before requesting so repeated failures cannot turn into a retry storm.
        store.recordAutomaticAttempt()
        check(manual = false)
    }

    fun cancel() {
        activeCall?.cancel()
        activeCall = null
        progressDialog?.dismiss()
        progressDialog = null
    }

    private fun check(manual: Boolean) {
        if (activeCall != null) return
        if (manual) {
            progressDialog = activity.materialDialog()
                .setTitle(R.string.standalone_update_checking)
                .setMessage(R.string.standalone_update_checking_summary)
                .setNegativeButton(android.R.string.cancel) { _, _ -> activeCall?.cancel() }
                .setOnCancelListener { activeCall?.cancel() }
                .show()
                .also(activity::tintDialogButtons)
        }
        activeCall = checker.check { result ->
            activity.runOnUiThread {
                val wasCancelled = activeCall?.isCanceled() == true
                activeCall = null
                progressDialog?.dismiss()
                progressDialog = null
                if (activity.isFinishing || activity.isDestroyed) return@runOnUiThread
                result.fold(
                    onSuccess = { release -> handleRelease(release, manual) },
                    onFailure = {
                        if (manual && !wasCancelled) {
                            activity.showSnackbar(
                                activity.findViewById(android.R.id.content),
                                activity.getString(R.string.standalone_update_check_failed),
                                Snackbar.LENGTH_LONG,
                            )
                        }
                    },
                )
            }
        }
    }

    private fun handleRelease(release: AppRelease, manual: Boolean) {
        val installedVersion = runCatching {
            activity.packageManager.getPackageInfo(activity.packageName, 0).versionName
        }.getOrNull().orEmpty()
        if (!UpdateVersionPolicy.isNewer(release.tag, installedVersion)) {
            if (manual) {
                activity.materialDialog()
                    .setTitle(R.string.standalone_update_up_to_date)
                    .setMessage(
                        activity.getString(
                            R.string.standalone_update_current_version,
                            installedVersion,
                        ),
                    )
                    .setPositiveButton(android.R.string.ok, null)
                    .show()
                    .also(activity::tintDialogButtons)
            }
            return
        }
        if (!manual && release.tag in store.ignoredTags()) return
        val message = buildString {
            append(activity.getString(R.string.standalone_update_available_summary, release.tag))
            if (release.notes.isNotBlank()) {
                append("\n\n")
                append(release.notes.trim())
            }
        }
        activity.materialDialog()
            .setTitle(release.name)
            .setMessage(message)
            .setNegativeButton(R.string.standalone_update_later, null)
            .setNeutralButton(R.string.standalone_update_ignore) { _, _ ->
                store.ignore(release.tag)
                activity.showSnackbar(
                    activity.findViewById(android.R.id.content),
                    activity.getString(R.string.standalone_update_ignored),
                )
            }
            .setPositiveButton(R.string.standalone_update_view_release) { _, _ ->
                openRelease(release.pageUrl)
            }
            .show()
            .also(activity::tintDialogButtons)
    }

    private fun openRelease(pageUrl: String) {
        runCatching {
            activity.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(pageUrl)))
        }.onFailure {
            activity.showSnackbar(
                activity.findViewById(android.R.id.content),
                activity.getString(R.string.standalone_update_open_failed),
                Snackbar.LENGTH_LONG,
            )
        }
    }
}
