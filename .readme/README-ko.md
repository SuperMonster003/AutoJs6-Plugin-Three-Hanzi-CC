<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>단독 및 AutoJs6에서 쓰는 오프라인 OpenCC 중국어 변환기</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-OpenCC?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-OpenCC?color=A24232&label=Issues"/></a>
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

OpenCC는 한 번 설치한 APK에서 [OpenCC](https://github.com/BYVoid/OpenCC) 기반 중국어 텍스트 변환을 두 가지 방식으로 제공합니다. 완전 오프라인 Android 앱으로 직접 실행하거나, 같은 APK를 AutoJs6 플러그인으로 인식시켜 스크립트의 전역 객체 `opencc`를 사용합니다. 두 경로 모두 간체자, 번체자, 홍콩/대만 자형, 일본어 신자체를 지원합니다.

독립 편집기와 권한으로 보호된 AutoJs6 Binder 서비스는 하나의 공식 OpenCC 엔진, 동일하게 고정된 사전, 캐시, 변환 유형, 오류 모델을 공유합니다. 독립 앱은 AutoJs6가 필요 없고, 플러그인 모드는 기존 스크립트 API를 유지하면서 변환 엔진을 호스트와 독립적으로 업데이트할 수 있습니다.

******

### 주요 기능

******

- 하나의 APK, 두 가지 사용법: 런처 아이콘에서 AutoJs6 없이 화면 변환을 하거나, 같은 설치를 AutoJs6의 `opencc` 스크립트 API로 사용할 수 있습니다.
- 14가지 표준 변환: OpenCC의 간체자-번체자 변환, 홍콩/대만 지역 자형 변환, 일본어 신자체 변환을 포괄하며, 대만 상용 어휘 변환 (`软件`과 `軟體`의 상호 변환 등)도 지원합니다.
- 33개 스크립트 메서드: 범용 `opencc.convert(text, type)` 외에 각 변환 유형과 동명의 단축 메서드가 있으며, `s2jp`, `tw2hk` 등 18개의 별칭 및 조합 메서드도 제공합니다.
- 완전 오프라인: 변환은 플러그인에 내장된 사전을 통해 기기 안에서 완결됩니다. 플러그인은 네트워크 권한을 요구하지 않으며 어떤 데이터도 수집하지 않습니다.
- 필요한 만큼만 선택하는 패키지: 4종의 단일 아키텍처 버전과 모든 아키텍처를 포함한 `universal` 버전을 제공하여, 기기에 맞는 패키지만 설치해 용량을 줄일 수 있습니다.
- 다국어 지원: 독립 UI, 플러그인 정보, 사용 설명, README, 변경 기록이 10개 언어를 포괄합니다.
- 공유 백엔드: 편집기와 가벼운 플러그인 서비스가 동일한 검증 리소스와 네이티브 엔진을 재사용하며, 유휴 플러그인 연결은 자동 해제됩니다.

******

### 화면 스크린샷

******

보정하지 않은 Android 실행 화면으로 라이트 테마의 독립 편집기, 글자 크기 170%의 아랍어 RTL 다크 레이아웃, 기존 AutoJs6 플러그인 센터 항목을 보여 줍니다.

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-phone-light.png?raw=true"
           alt="라이트 테마의 독립 오프라인 변환" width="280" />
      <br />
      <sub>라이트 테마의 독립 오프라인 변환</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-rtl-large-dark.png?raw=true"
           alt="다크 테마, 글자 크기 170%의 아랍어 RTL 레이아웃" width="280" />
      <br />
      <sub>다크 테마, 글자 크기 170%의 아랍어 RTL 레이아웃</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/plugin-center-enabled.png?raw=true"
           alt="플러그인 센터에서 인식되고 활성화된 OpenCC 1.0.2" width="280" />
      <br />
      <sub>플러그인 센터에서 인식되고 활성화된 OpenCC 1.0.2</sub>
    </td>
  </tr>
</table>

******

### 사용 방법

******

1. [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) 또는 AutoJs6 플러그인 센터에서 APK 하나를 내려받아 설치합니다. 기기 ABI와 맞는 패키지를 선택하고, 모르면 `universal` 또는 아래의 `설치 패키지 선택 방법`을 참고하세요.
2. 독립 사용 시 런처에서 `OpenCC`를 열고 텍스트를 입력하거나 명시적으로 붙여 넣은 뒤 14개 유형 중 하나를 골라 `변환`을 누릅니다. AutoJs6나 플러그인 권한 부여가 필요 없습니다.
3. 플러그인 사용 시 AutoJs6를 내부 빌드 3923 (6.7.1 Alpha4) 이상으로 업데이트합니다. 릴리스 6.8.0 이상은 요건을 충족합니다.
4. AutoJs6 플러그인 센터에서 `OpenCC`가 인식되고 활성화되었는지 확인합니다. 공식 패키지는 서명 검증을 자동 통과하므로 수동 승인이 필요 없습니다.
5. 스크립트에서 전역 객체 `opencc`를 직접 사용합니다. 예: `opencc.s2t("汉字")`; require, import, 호스트 재시작이 필요 없습니다.

> 두 모드 모두 Android 7.0 (API 24) 이상을 지원합니다. AutoJs6 최소 빌드 요건은 플러그인 스크립트에만 적용되며 독립 앱은 호스트에 의존하지 않습니다. 스크립트에서 누락 또는 버전 안내가 나오면 `자주 묻는 질문`을 참고하세요.

******

### 빠른 시작

******

설치 후 아래 스크립트를 바로 실행할 수 있습니다. 주석은 기대 출력입니다:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.t2jp("圖書館"));      // => 図書館
```

단축 메서드는 범용 메서드 `opencc.convert(text, type)`와 동일합니다; `opencc` 객체 자체도 함수로 호출할 수 있으며, 변환 유형 이름은 대소문자를 구분하지 않습니다:

```javascript
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
console.log(opencc("汉字转换", "s2t"));         // => 漢字轉換
```

모든 메서드는 변환된 문자열을 동기적으로 반환합니다. 변환은 로컬 사전에서 이루어지며 네트워크 요청이 전혀 발생하지 않습니다.

******

### 변환 유형

******

`convert` 메서드와 동명의 단축 메서드는 아래 14가지 OpenCC 표준 변환 유형을 지원합니다. 유형 이름에서 S는 간체자, T는 번체자 (OpenCC 표준), HK는 홍콩 번체자, TW는 대만 정체자, JP는 일본어 신자체를 의미합니다:

| 유형 | 변환 방향 |
|---|---|
| `S2T` | 간체자에서 번체자로 |
| `T2S` | 번체자에서 간체자로 |
| `S2TW` | 간체자에서 대만 정체자로 |
| `TW2S` | 대만 정체자에서 간체자로 |
| `S2TWP` | 간체자에서 대만 정체자로, 대만 상용 어휘로의 치환도 수행 (`内存`이 `記憶體`가 되는 등) |
| `TW2SP` | 대만 정체자에서 간체자로, 대륙 상용 어휘로의 치환도 수행 (`滑鼠`가 `鼠标`가 되는 등) |
| `S2HK` | 간체자에서 홍콩 번체자로 |
| `HK2S` | 홍콩 번체자에서 간체자로 |
| `T2TW` | 번체자에서 대만 정체자로 |
| `TW2T` | 대만 정체자에서 번체자로 |
| `T2HK` | 번체자에서 홍콩 번체자로 |
| `HK2T` | 홍콩 번체자에서 번체자로 |
| `T2JP` | 번체자 (구자체)에서 일본어 신자체로 |
| `JP2T` | 일본어 신자체에서 번체자 (구자체)로 |

`P` 접미사가 붙은 유형은 글자 단위 변환에 더해 어휘 치환도 수행하여 현지 표현 습관에 더 맞는 결과를 만듭니다; `P`가 없는 유형은 자형만 변환하고 어휘는 건드리지 않습니다.

`T2JP`와 `JP2T`는 번체자 구자체와 일본어 신자체 (Shinjitai) 사이를 변환합니다. 예를 들어 `圖書館`과 `図書館` 같은 한자 자형 차이를 다루는 것이며, 중국어와 일본어 간의 번역이 아닙니다.

******

### 스크립트 메서드

******

호스트 측 전역 객체 `opencc`는 총 33개의 메서드를 제공합니다: 범용 메서드 `convert`, 14개의 핵심 단축 메서드, 그리고 18개의 별칭 및 조합 메서드입니다. `convert(text, type)`의 `type` 인수는 32개 변환 이름 전부 (핵심과 조합 모두)를 대소문자 구분 없이 받아들입니다; 알 수 없는 유형을 전달하면 `Unknown OpenCC conversion type` 오류가 발생합니다.

14개의 핵심 단축 메서드는 위 표의 변환 유형과 일대일로 대응하며, 호출 한 번이 플러그인 변환 한 번을 수행합니다:

```text
s2t   t2s   s2tw  tw2s  s2twp  tw2sp  s2hk
hk2s  t2tw  tw2t  t2hk  hk2t   t2jp   jp2t
```

`s2twi`와 `twi2s`는 각각 `s2twp`와 `tw2sp`의 별칭이며 (`twi`는 Taiwan idiom, 즉 대만 상용 어휘를 의미합니다), 동작은 완전히 같습니다.

나머지 16개의 조합 메서드는 여러 핵심 변환을 순서대로 연결한 것으로, 직통 사전이 없는 변환 방향을 포괄합니다:

```text
s2jp   = s2t  + t2jp          jp2s   = jp2t + t2s
hk2tw  = hk2t + t2tw          tw2hk  = tw2t + t2hk
hk2jp  = hk2t + t2jp          tw2jp  = tw2t + t2jp
t2twi  = t2s  + s2twi         twi2t  = twi2s + s2t
hk2twi = hk2s + s2twi         twi2hk = twi2s + s2hk
tw2twi = tw2s + s2twi         twi2tw = twi2s + s2tw
jp2hk  = jp2t + t2hk          jp2tw  = jp2t + t2tw
twi2jp = twi2s + s2t + t2jp   jp2twi = jp2t + t2s + s2twi
```

확장 계약을 지원하는 새 호스트는 전체 조합 체인을 한 번의 플러그인 호출로 보냅니다. 예를 들어 `twi2jp`의 3개 변환 단계에는 Binder 왕복이 1회만 필요합니다; 이전 호스트는 각 단계를 계속 호출하며 이 플러그인과 호환됩니다.

******

### 설치 패키지 선택 방법

******

각 릴리스에는 5개의 APK가 포함되며, 차이는 내장된 OpenCC 네이티브 라이브러리의 프로세서 아키텍처 (ABI)뿐입니다:

| 패키지 | 대상 |
|---|---|
| `arm64-v8a` | 최근 Android 스마트폰과 태블릿의 대다수 (64비트 ARM). 최우선 선택지 |
| `armeabi-v7a` | 다소 오래된 32비트 ARM 기기 |
| `x86_64` | 64비트 x86 에뮬레이터와 소수의 x86 기기 |
| `x86` | 32비트 x86 에뮬레이터와 소수의 x86 기기 |
| `universal` | 4개 아키텍처를 모두 내장하여 용량이 가장 크지만, 모든 기기에서 동작하므로 고민될 때 확실한 선택지 |

기기 아키텍처와 맞지 않는 단일 아키텍처 버전을 잘못 설치하면 플러그인이 변환 서비스를 제공할 수 없습니다. `universal` 버전으로 교체하면 해결됩니다.

******

### 빠른 자체 점검

******

플러그인이 설치되고 플러그인 센터에서 활성화된 것을 확인했다면, 아래 한 줄 스크립트로 엔드투엔드 검증을 할 수 있습니다:

```javascript
console.log(opencc.s2t("汉字转换"));
```

`漢字轉換`이 출력되면 플러그인 연동이 완전히 동작하는 것입니다. 스크립트가 오류를 내면 메시지에 따라 처리하세요: 플러그인 누락이라고 표시되면 이 플러그인을 설치하고, 비활성화 또는 미승인이라고 표시되면 플러그인 센터에서 해당 스위치를 켜고, 더 새로운 호스트가 필요하다고 표시되면 AutoJs6를 업데이트합니다.

******

### 자주 묻는 질문

******

#### 플러그인이 활성화되었는지 어떻게 확인하나요?

AutoJs6 플러그인 센터를 열어 `OpenCC` 플러그인이 표시되고 활성화되어 있으면 호스트가 인식한 것입니다; 이어서 위의 `빠른 자체 점검` 스크립트를 실행하여 `漢字轉換`이 출력되면 정상 동작하는 것입니다.

#### AutoJs6를 설치하지 않고 OpenCC를 사용할 수 있나요?

예. 런처의 `OpenCC` 아이콘을 열어 오프라인 편집기에서 변환할 수 있습니다. AutoJs6는 스크립트가 전역 객체 `opencc`로 플러그인을 호출할 때만 필요하며, 두 모드는 같은 APK에 들어 있습니다.

#### 스크립트에서 `"OpenCC plugin"에 필요한 플러그인이 없습니다`라고 표시되면?

AutoJs6가 기기에서 이 플러그인을 찾지 못했다는 뜻입니다. 플러그인을 설치한 뒤 스크립트를 다시 실행하세요. AutoJs6 재시작은 필요 없습니다; 이미 설치했는데도 안내가 사라지지 않으면 시스템이나 보안 앱이 플러그인을 제거하지 않았는지, 플러그인 센터의 활성화 및 승인 상태가 정상인지 확인하세요.

#### `s2tw`와 `s2twp` (`s2twi`)의 차이는?

`s2tw`는 자형만 변환하고 (`软`이 `軟`이 되는 등) 어휘는 건드리지 않습니다; `s2twp`는 여기에 더해 대륙 어휘를 대만 상용 어휘로 치환합니다 (`软件`이 `軟體`로, `鼠标`가 `滑鼠`로 되는 등). `s2twi`는 그 별칭입니다. 대만 독자를 위한 정식 텍스트에는 보통 `s2twp`를, 자형 통일만 필요하면 `s2tw`를 선택합니다.

#### Node.js 엔진 스크립트에서 `opencc`를 쓸 수 없는 이유는?

`opencc`는 현재 Rhino (AutoJs6의 기본 JavaScript 엔진) 전용 전역 객체이며, Node.js 런타임에는 대응 구현이 아직 없습니다. 관련 지원 계획은 [ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)를 참고하세요.

#### 변환에 네트워크 연결이 필요한가요? 긴 텍스트는 느려지지 않나요?

네트워크는 필요 없습니다. 모든 변환은 플러그인에 내장된 OpenCC 사전으로 로컬에서 이루어집니다. 메서드 호출 한 번이 프로세스 간 통신 한 왕복에 해당하며, 다소 긴 텍스트도 보통 한 왕복으로 변환됩니다; 고빈도 반복 호출에서는 조합 메서드의 다중 왕복을 피하기 위해 핵심 유형 사용을 권장합니다.

#### 플러그인은 어떤 권한을 요구하나요? 데이터는 안전한가요?

플러그인은 AutoJs6와의 통신에 쓰이는 플러그인 권한만 선언하며, 네트워크나 저장소 같은 민감한 시스템 권한은 전혀 요구하지 않습니다; 서비스 자체도 같은 권한으로 보호되어 다른 앱에서는 호출할 수 없습니다. 변환 대상 텍스트는 기기 메모리 안에서만 처리되며 저장되거나 업로드되지 않습니다.

******

### 권한 및 보안

******

독립 앱과 AutoJs6 플러그인 항목은 분리되고 명확한 경계를 가집니다:

- 최소 권한: 매니페스트는 연동용 `org.autojs.permission.PLUGIN`만 선언하며 네트워크, 저장소, 카메라 같은 민감한 권한이 없습니다. 독립 사용자는 플러그인 권한을 부여하지 않습니다.
- 명시적 편집 동작: Launcher는 공유 텍스트나 URI를 받지 않고, `붙여넣기`를 누른 뒤에만 클립보드를 읽으며, `공유`를 누른 뒤에만 시스템 공유 창을 엽니다.
- 보호된 서비스: AutoJs6처럼 권한을 가진 호스트만 바인딩하고 호출할 수 있습니다. AutoJs6는 패키지 서명도 검증하며 다른 앱은 서비스를 호출할 수 없습니다.
- 로컬 처리: 두 진입점 모두 내장 사전으로 완전 오프라인 변환합니다. 입력과 결과는 로그, 영구 저장, 백업, 업로드, 수집되지 않습니다.

플러그인은 공식 [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) 페이지 또는 AutoJs6 플러그인 센터에서만 받으세요. 출처를 알 수 없는 패키지는 버전 번호가 같아 보여도 호스트 검증을 통과하지 못하거나 위험을 포함할 수 있습니다.

******

### 플러그인 인터페이스

******

아래 정보는 AutoJs6 호스트 및 플러그인 개발자를 위한 것입니다. 호스트는 이 식별자들로 플러그인을 발견하고 호환성 협상을 수행합니다:

```text
application id: io.github.supermonster003.autojs6.plugin.opencc
plugin id: opencc
engine: opencc
variant: default
service action: org.autojs.plugin.OPENCC
service category: opencc
aidl interface: org.autojs.plugin.opencc.api.IOpenccPlugin
aidl contract version: 2
aidl methods: getInfo(), convert(text, conversionType), getSupportedConversionTypes(), convertBatch(texts, conversionType), convertChain(text, conversionTypes)
batch/chain limits: 1024 texts / 32 stages
minimum host build: 3923 (6.7.1 Alpha4)
conversion backend: OpenCC 1.4.2 (ver.1.4.2)
OpenCC source commit: 025f371dc76b598d77384fbdab90c937471844d8
OpenCC resources SHA-256: 9ea0d303219b34d014d5c116677b5d325043beafb2c8a62ee889ca67f4d054a5
```

`OpenccPluginService`는 `org.autojs.plugin.OPENCC` 액션 (카테고리 `opencc`)에 opencc-api의 `org.autojs.plugin.opencc.api.IOpenccPlugin`로 응답합니다. 계약 버전 2는 기존 `getInfo()`와 `convert(text, conversionType)` 뒤에 유형 검색, 일괄 변환, 체인 변환을 추가하고 `PluginInfo.capabilities`를 통해 버전과 지원 유형을 알립니다; 이전 호스트는 기존 메서드와 트랜잭션 번호를 계속 사용합니다. 호스트가 플러그인 프로세스를 깨우기 위한 `WakeActivity`도 제공합니다.

플러그인은 커밋 `025f371dc76b598d77384fbdab90c937471844d8`에 고정된 공식 OpenCC `ver.1.4.2`와 같은 릴리스의 리소스를 직접 빌드합니다. 각 ABI에는 정적으로 링크되고 16 KB에 정렬된 `libopencc_jni.so` 하나만 포함되며 변환은 항상 완전히 오프라인으로 이루어집니다.

******

### 개발 로드맵

******

플러그인의 기능 계획과 진행 상황은 체크 가능한 목록 형태로 ROADMAP.md에서 관리됩니다. 마일스톤별로 정리되고 수용 기준이 붙어 있으며, 문서와 릴리스 경험, 엔지니어링과 지속적 통합, 변환 기능 강화, 런타임 진화 등의 방향을 포괄합니다. 체크되지 않은 항목은 계획상의 의향이며 현재 버전의 기능이 아닙니다. Issues에서의 토론을 환영합니다.

- [ROADMAP.md 보기](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### 릴리스 기록

******

#### v1.2.0

_2026/09/01_

- `힌트` OpenCC 1.4.2 사전 업데이트로 `复盘` -> `復盤`, `内卷` -> `內捲`, `什么怎么这么` 유지, `内存条` -> `記憶體模組` 등 일부 결과가 의도적으로 달라집니다. 전체 검토 목록은 마이그레이션 보고서에 기록했습니다
- `개선` 공식 OpenCC 1.4.2와 같은 릴리스의 사전을 ABI별 정적 링크 JNI 라이브러리 하나로 직접 빌드하고 모든 변환을 완전히 오프라인으로 유지
- `개선` NDK 28.2, 16 KB ELF 및 ZIP 정렬, 실제 16 KB 에뮬레이터 Binder 검증으로 16 KB 페이지 크기 기기 지원
- `개선` 고정된 리소스 ZIP을 크기 및 SHA-256 검증과 함께 원자적으로 설치하고 손상 자동 복구, Unicode 안전 JNI 변환, 핫 패스 변환기 캐시 구현
- `의존성` 유지 관리가 중단된 `com.github.brooklet:android-opencc:1.2.2` 래퍼를 제거하고 공식 OpenCC `ver.1.4.2`를 커밋 `025f371dc76b598d77384fbdab90c937471844d8`에 고정
- `의존성` 포함된 OpenCC, Marisa Trie, Darts Clone, RapidJSON의 출처와 라이선스를 `THIRD_PARTY_NOTICES.md`에 문서화

#### v1.1.0

_2026/09/01_

- `기능` OpenCC 플러그인 계약을 버전 2로 업그레이드하고 `getSupportedConversionTypes()`를 추가하여 새 호스트가 플러그인이 실제 지원하는 14개 변환 유형을 동적으로 검색할 수 있습니다
- `기능` `convertBatch(texts, conversionType)`를 추가하여 한 번의 Binder 왕복으로 최대 1024개 텍스트를 변환하며 이전 호스트의 항목별 호출 경로도 유지합니다
- `기능` `convertChain(text, conversionTypes)`를 추가하여 한 번의 호출로 최대 32개 단계를 순서대로 실행하며 새 호스트의 조합 메서드는 최대 3회이던 Binder 왕복이 1회로 줄어듭니다
- `개선` `PluginInfo.instruction`으로 호출자 언어에 맞는 플러그인 설명을 제공하고 capabilities를 통해 계약 버전과 지원 변환 유형을 보고합니다
- `개선` 기존 AIDL 메서드와 트랜잭션 번호를 유지하고 확장 호출, 이전 계약 폴백, 크기 제한, 오류 경로를 단위 테스트와 실제 Binder 테스트로 검증합니다
- `개선` README 레이아웃과 Gradle 플랫폼 버전 관리 방식을 통일

#### v1.0.2

_2026/08/31_

- `힌트` 이 버전은 문서와 빌드 과정만 개선합니다. OpenCC 변환 동작과 14가지 핵심 변환 유형은 변경되지 않습니다
- `개선` 10개 언어의 README를 재구성하고 설치 단계, 패키지 선택 안내, 빠른 자체 점검, 33개 스크립트 메서드 전체 목록, FAQ, 권한 및 보안 설명을 추가했습니다
- `개선` 플러그인 센터 사용 설명을 README 및 CHANGELOG와 같은 다국어 JSON 소스에서 생성하여 모든 Android 문서 산출물을 단일 소스로 동기화했습니다
- `개선` 문서 검증을 강화하고 GitHub Actions에 통합하여 언어 간 구조 불일치, 생성 파일 드리프트, 고아 산출물, 버전 불일치, 남은 자리표시자를 자동으로 감지합니다
- `개선` ROADMAP.md를 추가하여 문서, 엔지니어링, 변환 기능, 런타임 발전 계획을 검증 가능한 마일스톤 목록으로 공개했습니다
- `개선` Gradle 구성을 `org.autojs.build.platform-versions` 1.4.1로 이전하고 foojay로 JDK를 자동 해석하여 빌드 환경을 단순화하고 표준화했습니다

##### 더 많은 릴리스 기록

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/assets/doc/CHANGELOG-ko.md)

******

### 빌드 및 검증

******

이 섹션은 소스에서 플러그인을 빌드하려는 개발자를 위한 것입니다; 일반 사용자는 Releases 페이지의 빌드된 APK를 그대로 설치하면 충분합니다.

debug APK 빌드:

```powershell
.\gradlew.bat :app:assembleDebug
```

JVM 단위 테스트를 실행하고 instrumentation 테스트 APK 빌드:

```powershell
.\gradlew.bat :app:testDebugUnitTest :app:assembleDebugAndroidTest
```

release APK 빌드:

```powershell
.\gradlew.bat :app:assembleRelease
```

릴리스 산출물을 수집하고 파일 이름에 버전, ABI, CRC32 체크섬을 부가:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

release APK를 빌드하고 체크섬과 릴리스 노트 준비:

```powershell
py scripts\release\prepare_release.py
```

다국어 문서 소스와 생성물이 동기화되어 있는지 검증 (CI에서도 실행됩니다):

```powershell
py .python\generate_markdown.py --check
```

빌드에는 JDK 17 이상과 Android SDK 36이 필요합니다; Gradle과 각 플러그인의 버전은 `version.properties`와 `io.github.supermonster003.autojs6-platform-versions`로 일원 관리됩니다.

******

### 현지화 및 문서 생성

******

```text
.readme/common.json
.readme/android_strings.json
.readme/lang_*.json
.readme/template_readme.md
.readme/template_plugin_instruction.md
.changelog/lang_*.json
.changelog/template_changelog.md
.python/generate_markdown.py
docs/images/screenshots/README.md
docs/images/screenshots/plugin-center-enabled.png
docs/images/screenshots/standalone-phone-light.png
docs/images/screenshots/standalone-rtl-large-dark.png
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`.readme/android_strings.json`은 독립 UI와 서비스 오류 문구의 단일 소스이고, 언어 JSON은 README와 플러그인 센터 문구를 제공합니다. `.readme/`와 `.changelog/`의 JSON을 편집한 뒤 `py .python/generate_markdown.py`를 다시 실행하며, 생성된 `strings.xml`, `plugin_instruction.md`, README, 변경 기록은 손으로 편집하지 않습니다. `--check`는 생성물 47개를 검증합니다.

******

### 라이선스

******

프로젝트 코드는 [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE)으로 라이선스됩니다. 중국어 변환은 [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0)를 직접 사용하며 포함된 OpenCC, Marisa Trie, Darts Clone, RapidJSON의 출처와 라이선스는 [서드 파티 고지](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md)에 정리되어 있습니다.

******

### 링크

******

- AutoJs6 OpenCC 문서: https://docs.autojs6.com/#/opencc
- AutoJs6 프로젝트: https://github.com/SuperMonster003/AutoJs6
- OpenCC 공식 프로젝트: https://github.com/BYVoid/OpenCC
- 서드 파티 고지: https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md
