OpenCC 플러그인 (OpenCC Plugin)은 [OpenCC](https://github.com/BYVoid/OpenCC) 기반의 중국어 텍스트 변환 기능을 AutoJs6에 제공합니다. 이 플러그인을 설치하면 AutoJs6 스크립트의 전역 객체 `opencc`를 바로 사용할 수 있으며, 간체자, 번체자, 홍콩 번체자, 대만 정체자, 일본어 신자체 간의 변환이 코드 한 줄로 끝납니다. 모듈을 가져올 필요도 네트워크 연결도 필요하지 않습니다.

이 릴리스에는 공식 OpenCC 1.4.2와 같은 릴리스에 고정된 사전이 포함됩니다. 모든 처리는 계속 완전히 오프라인으로 이루어지며 네이티브 패키지는 16 KB 메모리 페이지를 사용하는 Android 기기를 지원합니다.

### 빠른 시작

설치 후 아래 스크립트를 바로 실행할 수 있습니다. 주석은 기대 출력입니다:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
```

### 변환 유형

`convert` 메서드와 동명의 단축 메서드는 아래 14가지 OpenCC 표준 변환 유형을 지원합니다. 유형 이름에서 S는 간체자, T는 번체자 (OpenCC 표준), HK는 홍콩 번체자, TW는 대만 정체자, JP는 일본어 신자체를 의미합니다:

```text
S2T   T2S   S2TW  TW2S  S2TWP  TW2SP  S2HK
HK2S  T2TW  TW2T  T2HK  HK2T   T2JP   JP2T
```

`P` 접미사가 붙은 유형은 글자 단위 변환에 더해 어휘 치환도 수행하여 현지 표현 습관에 더 맞는 결과를 만듭니다; `P`가 없는 유형은 자형만 변환하고 어휘는 건드리지 않습니다.

### 빠른 자체 점검

플러그인이 설치되고 플러그인 센터에서 활성화된 것을 확인했다면, 아래 한 줄 스크립트로 엔드투엔드 검증을 할 수 있습니다:

```javascript
console.log(opencc.s2t("汉字转换"));
```

`漢字轉換`이 출력되면 플러그인 연동이 완전히 동작하는 것입니다. 스크립트가 오류를 내면 메시지에 따라 처리하세요: 플러그인 누락이라고 표시되면 이 플러그인을 설치하고, 비활성화 또는 미승인이라고 표시되면 플러그인 센터에서 해당 스위치를 켜고, 더 새로운 호스트가 필요하다고 표시되면 AutoJs6를 업데이트합니다.

메서드 목록과 변환 유형의 전체 레퍼런스는 [AutoJs6 OpenCC 문서](https://docs.autojs6.com/#/opencc)와 [프로젝트 README](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC)를 참고하세요.
