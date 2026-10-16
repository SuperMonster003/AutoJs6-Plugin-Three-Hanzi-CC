package io.github.supermonster003.autojs6.plugin.three.hanzi.cc

import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.HK2S
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.HK2T
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.JP2T
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.S2HK
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.S2T
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.S2TW
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.S2TWP
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.T2HK
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.T2JP
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.T2S
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.T2TW
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.TW2S
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.TW2SP
import io.github.supermonster003.autojs6.plugin.three.hanzi.cc.nativebridge.OpenccConversionType.TW2T
import java.util.Locale

/**
 * The `config` values of the `opencc_convert` tool: the same 32 names the AutoJs6 `opencc` script module accepts
 * (its `OpenccConversionPlan`), so a tool call and a script call mean the same conversion. 14 names are the native
 * OpenCC configurations, `s2twi` / `twi2s` are aliases, and 16 names chain native configurations in order.
 */
internal object OpenccToolConfigs {

    const val DEFAULT = "s2t"

    /** At most this many characters (code points) per call; 16384 three-byte characters stay within the 64 KiB argument limit. */
    const val MAX_TEXT_LENGTH = 16384

    val chains: Map<String, List<OpenccConversionType>> = linkedMapOf<String, List<OpenccConversionType>>().apply {
        OpenccConversionType.entries.forEach { put(it.name.lowercase(Locale.ROOT), listOf(it)) }
        put("s2twi", listOf(S2TWP))
        put("twi2s", listOf(TW2SP))
        put("s2jp", listOf(S2T, T2JP))
        put("t2twi", listOf(T2S, S2TWP))
        put("hk2tw", listOf(HK2T, T2TW))
        put("hk2twi", listOf(HK2S, S2TWP))
        put("hk2jp", listOf(HK2T, T2JP))
        put("tw2hk", listOf(TW2T, T2HK))
        put("tw2twi", listOf(TW2S, S2TWP))
        put("tw2jp", listOf(TW2T, T2JP))
        put("twi2t", listOf(TW2SP, S2T))
        put("twi2hk", listOf(TW2SP, S2HK))
        put("twi2tw", listOf(TW2SP, S2TW))
        put("twi2jp", listOf(TW2SP, S2T, T2JP))
        put("jp2s", listOf(JP2T, T2S))
        put("jp2hk", listOf(JP2T, T2HK))
        put("jp2tw", listOf(JP2T, T2TW))
        put("jp2twi", listOf(JP2T, T2S, S2TWP))
    }

    val names: List<String> get() = chains.keys.toList()

    /**
     * Checks one call and returns the native configurations to apply; throws [IllegalArgumentException] with the reason.
     * The host has already checked the arguments against the tool's schema, so this only guards direct callers.
     */
    fun plan(text: String, config: String?): List<OpenccConversionType> {
        val name = config ?: DEFAULT
        val chain = requireNotNull(chains[name]) { "unknown config \"$name\"; use one of ${names.joinToString(", ")}" }
        val length = text.codePointCount(0, text.length)
        require(length <= MAX_TEXT_LENGTH) { "text has $length characters; at most $MAX_TEXT_LENGTH are allowed" }
        return chain
    }
}
