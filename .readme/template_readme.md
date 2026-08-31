<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="{{ repo_url }}/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="{{ repo_url }}/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="{{ icon_alt }}" border="0" width="128" />
    </picture>
  </p>

  <p>{{ text_plugin_synopsis }}</p>

  <p>
    <a href="{{ repo_url }}/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/{{ repo_slug }}?label=Release"/></a>
    <a href="{{ repo_url }}/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/{{ repo_slug }}?color=A24232&label=Issues"/></a>
    <a href="{{ license_url }}"><img alt="GitHub License" src="https://img.shields.io/github/license/{{ repo_slug }}?color=534BAE&label=License"/></a>
  </p>
</div>

******

### {{ h3_languages_with_ascii }}

******

{{ p_languages_all_supported_for_readme }}:

{{ placeholder_ul_languages_all_supported }}

******

### {{ h3_introduction }}

******

{{ p_introduction_what }}

{{ p_introduction_how }}

******

### {{ h3_features }}

******

{{ placeholder_features }}

******

### {{ h3_screenshots }}

******

{{ p_screenshots_intro }}

<table>
  <tr>
    <td align="center">
      <img src="{{ repo_url }}/blob/master/docs/images/screenshots/plugin-center-enabled.png?raw=true"
           alt="{{ screenshot_plugin_center_caption }}" width="360" />
      <br />
      <sub>{{ screenshot_plugin_center_caption }}</sub>
    </td>
  </tr>
</table>

******

### {{ h3_usage }}

******

{{ placeholder_usage_steps }}

> {{ p_usage_note }}

******

### {{ h3_quick_start }}

******

{{ p_quick_start_intro }}:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.t2jp("圖書館"));      // => 図書館
```

{{ p_quick_start_convert }}:

```javascript
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
console.log(opencc("汉字转换", "s2t"));         // => 漢字轉換
```

{{ p_quick_start_note }}

******

### {{ h3_conversion_types }}

******

{{ p_conversion_types_intro }}:

| {{ th_type_code }} | {{ th_type_direction }} |
|---|---|
| `S2T` | {{ td_type_s2t }} |
| `T2S` | {{ td_type_t2s }} |
| `S2TW` | {{ td_type_s2tw }} |
| `TW2S` | {{ td_type_tw2s }} |
| `S2TWP` | {{ td_type_s2twp }} |
| `TW2SP` | {{ td_type_tw2sp }} |
| `S2HK` | {{ td_type_s2hk }} |
| `HK2S` | {{ td_type_hk2s }} |
| `T2TW` | {{ td_type_t2tw }} |
| `TW2T` | {{ td_type_tw2t }} |
| `T2HK` | {{ td_type_t2hk }} |
| `HK2T` | {{ td_type_hk2t }} |
| `T2JP` | {{ td_type_t2jp }} |
| `JP2T` | {{ td_type_jp2t }} |

{{ p_conversion_types_phrase_note }}

{{ p_conversion_types_jp_note }}

******

### {{ h3_script_methods }}

******

{{ p_methods_intro }}

{{ p_methods_core }}:

```text
s2t   t2s   s2tw  tw2s  s2twp  tw2sp  s2hk
hk2s  t2tw  tw2t  t2hk  hk2t   t2jp   jp2t
```

{{ p_methods_alias }}

{{ p_methods_composed }}:

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

{{ p_methods_composed_note }}

******

### {{ h3_choose_apk }}

******

{{ p_choose_apk_intro }}:

| {{ th_apk_variant }} | {{ th_apk_target }} |
|---|---|
| `arm64-v8a` | {{ td_abi_arm64 }} |
| `armeabi-v7a` | {{ td_abi_arm32 }} |
| `x86_64` | {{ td_abi_x86_64 }} |
| `x86` | {{ td_abi_x86 }} |
| `universal` | {{ td_abi_universal }} |

{{ p_choose_apk_note }}

******

### {{ h3_self_check }}

******

{{ p_self_check_intro }}:

```javascript
console.log(opencc.s2t("汉字转换"));
```

{{ p_self_check_result }}

******

### {{ h3_faq }}

******

{{ placeholder_faq }}

******

### {{ h3_security }}

******

{{ p_security_intro }}

{{ placeholder_security_points }}

{{ p_security_permission }}

******

### {{ h3_plugin_interface }}

******

{{ p_plugin_interface }}:

```text
application id: {{ plugin_application_id }}
plugin id: {{ plugin_id }}
engine: {{ plugin_engine }}
variant: {{ plugin_variant }}
service action: {{ plugin_service_action }}
service category: {{ plugin_service_category }}
aidl interface: {{ plugin_aidl_interface }}
aidl contract version: {{ plugin_contract_version }}
aidl methods: getInfo(), convert(text, conversionType), getSupportedConversionTypes(), convertBatch(texts, conversionType), convertChain(text, conversionTypes)
batch/chain limits: {{ max_batch_size }} texts / {{ max_chain_length }} stages
minimum host build: {{ required_host_version_code }} ({{ required_host_version_name }})
conversion library: {{ opencc_library_coordinates }}
```

{{ p_contract_service }}

{{ p_abi_reporting }}

******

### {{ h3_roadmap }}

******

{{ p_roadmap }}

- [{{ text_link_roadmap }}]({{ roadmap_url }})

******

### {{ h3_release_history }}

******

{{ placeholder_latest_release_history }}

##### {{ h5_for_more_release_history }}

* {{ placeholder_read_more_in_changelog_md }}

******

### {{ h3_build }}

******

{{ p_build_intro }}

{{ p_build_debug }}:

```powershell
.\gradlew.bat :app:assembleDebug
```

{{ p_build_test }}:

```powershell
.\gradlew.bat :app:testDebugUnitTest :app:assembleDebugAndroidTest
```

{{ p_build_release }}:

```powershell
.\gradlew.bat :app:assembleRelease
```

{{ p_build_digest }}:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

{{ p_build_release_bundle }}:

```powershell
py scripts\release\prepare_release.py
```

{{ p_build_docs_check }}:

```powershell
py .python\generate_markdown.py --check
```

{{ p_build_requirements }}

******

### {{ h3_resource_layout }}

******

```text
.readme/common.json
.readme/lang_*.json
.readme/template_readme.md
.readme/template_plugin_instruction.md
.changelog/lang_*.json
.changelog/template_changelog.md
.python/generate_markdown.py
docs/images/screenshots/README.md
docs/images/screenshots/plugin-center-enabled.png
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

{{ p_resource_layout }}

******

### {{ h3_license }}

******

{{ p_license }}

******

### {{ h3_links }}

******

- {{ text_link_autojs6_opencc_docs }}: {{ docs_opencc_url }}
- {{ text_link_autojs6 }}: {{ autojs6_url }}
- {{ text_link_opencc_official }}: {{ opencc_official_url }}
- {{ text_link_android_opencc }}: {{ android_opencc_url }}
