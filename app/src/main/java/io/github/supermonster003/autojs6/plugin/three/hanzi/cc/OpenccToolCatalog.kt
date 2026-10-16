package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

/**
 * The catalog this plugin returns from `IPluginToolProvider.getCatalog` (AutoJs6 plugin tool contract v1): the short
 * name `opencc` and one read-only tool, `convert`, which AutoJs6 lists as `opencc_convert` for MCP Server, agents and
 * the `plugins.tools` script API. Descriptions are English because they reach model context as written.
 */
internal object OpenccToolCatalog {

    const val SHORT_NAME = "opencc"
    const val TOOL_CONVERT = "convert"
    const val TIMEOUT_MS = 10_000
    const val MAX_CONCURRENCY = 4

    private const val DESCRIPTION = "Converts Chinese text between Simplified, Traditional, Hong Kong, Taiwan and " +
        "Japanese Shinjitai character forms with OpenCC, offline on the phone. It changes character forms, and with " +
        "the twi / p configs also Taiwan vocabulary (for example software, internet); it does not translate between " +
        "languages. Pick config as <from>2<to>: s2t (Simplified to Traditional, the default), t2s, s2tw / s2hk " +
        "(Simplified to Taiwan / Hong Kong standard characters), s2twi (= s2twp, also Taiwan vocabulary), tw2s / hk2s, " +
        "twi2s (= tw2sp), t2tw / t2hk / tw2t / hk2t (OpenCC Traditional to and from regional standards), t2jp / jp2t " +
        "(Traditional to and from Japanese Shinjitai), and chains such as s2jp, hk2tw, tw2hk or jp2s."

    private const val CONFIG_DESCRIPTION = "The conversion, named <from>2<to> with s (Simplified), t (Traditional, " +
        "OpenCC standard), hk (Hong Kong), tw (Taiwan), twi (Taiwan with Taiwan vocabulary) and jp (Japanese Shinjitai). " +
        "Default s2t."

    val json: String by lazy {
        val tool = linkedMapOf(
            "name" to TOOL_CONVERT,
            "title" to "Convert Chinese text (OpenCC)",
            "description" to DESCRIPTION,
            "inputSchema" to linkedMapOf(
                "type" to "object",
                "properties" to linkedMapOf(
                    "text" to linkedMapOf(
                        "type" to "string",
                        "description" to "The text to convert, at most ${OpenccToolConfigs.MAX_TEXT_LENGTH} characters.",
                        "maxLength" to OpenccToolConfigs.MAX_TEXT_LENGTH,
                    ),
                    "config" to linkedMapOf(
                        "type" to "string",
                        "description" to CONFIG_DESCRIPTION,
                        "enum" to OpenccToolConfigs.names,
                        "default" to OpenccToolConfigs.DEFAULT,
                    ),
                ),
                "required" to listOf("text"),
                "additionalProperties" to false,
            ),
            "outputSchema" to linkedMapOf(
                "type" to "object",
                "properties" to linkedMapOf(
                    "text" to linkedMapOf("type" to "string", "description" to "The converted text."),
                    "config" to linkedMapOf("type" to "string", "description" to "The config that was applied."),
                ),
                "required" to listOf("text", "config"),
                "additionalProperties" to false,
            ),
            "risk" to "readonly",
            "timeoutMs" to TIMEOUT_MS,
            "maxConcurrency" to MAX_CONCURRENCY,
        )
        encode(linkedMapOf("shortName" to SHORT_NAME, "tools" to listOf(tool)))
    }

    /** A minimal JSON encoder for the catalog's maps, lists, strings, numbers and booleans. */
    internal fun encode(value: Any?): String = when (value) {
        null -> "null"
        is String -> quote(value)
        is Number, is Boolean -> value.toString()
        is Map<*, *> -> value.entries.joinToString(",", "{", "}") { (key, item) -> quote(key.toString()) + ":" + encode(item) }
        is Iterable<*> -> value.joinToString(",", "[", "]") { encode(it) }
        else -> throw IllegalArgumentException("unsupported catalog value ${value::class.java.name}")
    }

    private fun quote(text: String): String = buildString(text.length + 2) {
        append('"')
        for (char in text) {
            when {
                char == '"' -> append("\\\"")
                char == '\\' -> append("\\\\")
                char == '\n' -> append("\\n")
                char == '\r' -> append("\\r")
                char == '\t' -> append("\\t")
                char < ' ' -> append(String.format("\\u%04x", char.code))
                else -> append(char)
            }
        }
        append('"')
    }
}
