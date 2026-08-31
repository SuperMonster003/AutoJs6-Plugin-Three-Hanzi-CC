package io.github.supermonster003.autojs6.plugin.opencc.nativebridge;

/**
 * Stable conversion names shared with the opencc-api contract.
 *
 * <p>The enum order is intentionally identical to OpenccConversionTypes.ALL.
 */
public enum OpenccConversionType {
    HK2S("hk2s.json"),
    HK2T("hk2t.json"),
    JP2T("jp2t.json"),
    S2HK("s2hk.json"),
    S2T("s2t.json"),
    S2TW("s2tw.json"),
    S2TWP("s2twp.json"),
    T2HK("t2hk.json"),
    T2S("t2s.json"),
    T2TW("t2tw.json"),
    T2JP("t2jp.json"),
    TW2S("tw2s.json"),
    TW2T("tw2t.json"),
    TW2SP("tw2sp.json");

    private final String configFile;

    OpenccConversionType(String configFile) {
        this.configFile = configFile;
    }

    public String configFile() {
        return configFile;
    }
}
