<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>중국어 텍스트 변환용 OpenCC 플러그인</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-OpenCC?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-OpenCC?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/commit/ac15c8492f78b0bb9c06f2b1e9b70d7ba87be81f"><img alt="Created" src="https://img.shields.io/date/1784032100?color=2e7d32&label=Created"/></a>
    <br>
    <a href="https://developer.android.com/studio/archive"><img alt="Android Studio" src="https://img.shields.io/badge/Android%20Studio-2023.3+-B64FC8"/></a>
    <a href="https://www.jetbrains.com/idea/download/other.html"><img alt="IntelliJ IDEA" src="https://img.shields.io/badge/IntelliJ%20IDEA-2023.3+-EE4677"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-OpenCC?color=534BAE&label=License"/></a>
  </p>
</div>

******

### 언어 (Languages)

******

현재 README.md는 다음 언어를 지원합니다:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ja.md)
- 한국어 [ko] # 현재
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ar.md)

******

### 소개

******

AutoJs6 OpenCC 플러그인은 AutoJs6에 OpenCC 기반 중국어 텍스트 변환 기능을 제공합니다. 간체 중국어, 번체 중국어, 홍콩 번체, 대만 번체, 일본어 신자체 관련 변환을 지원합니다.

******

### 기능

******

- 플러그인 ID가 `opencc`인 `opencc` 플러그인 서비스를 제공합니다.
- `opencc.convert(text, type)` 및 `opencc.s2t(text)` / `opencc.t2s(text)` 같은 AutoJs6 API를 지원합니다.
- 플러그인 메타데이터, 사용 설명, README, CHANGELOG는 스페인어, 프랑스어, 러시아어, 아랍어, 일본어, 한국어, 영어, 간체 중국어, 홍콩 번체, 대만 번체로 현지화되어 있습니다.
- `com.github.brooklet:android-opencc`를 기반으로 합니다.

******

### 사용 예시

******

```js
let text = "汉字转换";
let converted = opencc.convert(text, "S2T");
console.log(converted);
```

단축 메서드도 사용할 수 있습니다:

```js
console.log(opencc.s2t("汉字转换"));
console.log(opencc.t2s("漢字轉換"));
```

******

### 변환 유형

******

일반적인 OpenCC 변환 유형에는 다음이 포함됩니다:

```text
S2T, S2TW, S2TWP, S2HK,
T2S, T2TW, T2HK, T2JP,
TW2S, TW2T, TW2SP,
HK2S, HK2T,
JP2T
```

AutoJs6는 `s2jp`, `hk2tw`, `tw2hk`, `jp2s` 같은 조합 단축 메서드도 제공합니다.

******

### 릴리스 기록

******

# v1.0.1

###### 2026/07/14

* `개선` `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` 및 `universal` APK를 포함한 ABI 분할 APK 빌드를 추가
* `개선` 호스트가 호환 가능한 변형을 식별할 수 있도록 플러그인 런타임 정보에 지원 ABI 메타데이터를 추가
* `개선` 릴리스 APK 파일 이름에 버전, ABI 변형 및 CRC32 다이제스트를 포함하도록 변경

# v1.0.0

###### 2026/07/14

* `기능` 플러그인 ID `opencc`, 엔진 `opencc`인 OpenCC 플러그인 서비스를 추가
* `기능` `org.autojs.plugin.OPENCC`를 통한 호스트 검색 및 호출을 추가
* `기능` 일반적인 OpenCC 변환 유형 `S2T`, `S2TW`, `S2TWP`, `S2HK`, `T2S`, `T2TW`, `T2HK`, `T2JP`, `TW2S`, `TW2T`, `TW2SP`, `HK2S`, `HK2T`, `JP2T`를 지원
* `기능` 스페인어, 프랑스어, 러시아어, 아랍어, 일본어, 한국어, 영어, 간체 중국어, 홍콩 번체, 대만 번체에 대한 플러그인 메타데이터와 사용 설명을 추가
* `기능` 사용 예시, 빌드 설명, 관련 링크가 포함된 중국어/영어 이중 언어 README를 추가

##### 더 많은 릴리스 기록

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.changelog/CHANGELOG-ko.md)

******

### 빌드

******

```powershell
.\gradlew.bat :app:assembleDebug
```

Release 빌드:

```powershell
.\gradlew.bat :app:assembleRelease
```

빌드 매개변수는 `version.properties`에서 가져옵니다. 현재 최소 SDK는 24이고 대상 SDK는 36입니다.

******

### 리소스 구조

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml`에는 현지화된 플러그인 설명과 오류 메시지가 포함됩니다. `plugin_instruction.md`에는 호스트에서 표시하는 사용 설명이 포함됩니다. README와 CHANGELOG는 `.python/generate_markdown.py`가 JSON 소스에서 생성합니다.

******

### 링크

******

- AutoJs6 OpenCC 문서: https://docs.autojs6.com/#/opencc
- OpenCC 공식 프로젝트: https://github.com/BYVoid/OpenCC
- Android OpenCC 프로젝트: https://github.com/qichuan/android-opencc
