<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>Conversor chino OpenCC sin conexión, independiente y compatible con AutoJs6</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-OpenCC?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-OpenCC?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-OpenCC?color=534BAE&label=License"/></a>
  </p>
</div>

******

### Idiomas (Languages)

******

El README.md actual admite los siguientes idiomas:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-fr.md)
- Español [es] # actual
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ar.md)

******

### Introducción

******

OpenCC reúne en una sola instalación dos formas de usar la conversión de texto chino basada en [OpenCC](https://github.com/BYVoid/OpenCC). Inicie directamente la aplicación Android totalmente sin conexión, o deje que AutoJs6 reconozca el mismo APK como complemento y use el objeto global `opencc` en los scripts. Ambas rutas cubren chino simplificado, tradicional, variantes de Hong Kong y Taiwán, y shinjitai japonés.

El editor independiente y el servicio Binder de AutoJs6 protegido por permiso comparten un único motor OpenCC oficial, los mismos diccionarios fijados, caché, tipos de conversión y modelo de errores. La aplicación no requiere AutoJs6; el modo complemento conserva la API de scripts existente y permite actualizar el motor con independencia del host.

******

### Funciones destacadas

******

- Un APK, dos usos: abra el icono del lanzador para convertir texto visualmente sin AutoJs6, o use la misma instalación mediante la API de scripts `opencc` de AutoJs6.
- 14 conversiones estándar: cubre la conversión entre simplificado y tradicional de OpenCC, las variantes de Hong Kong y Taiwán y el shinjitai japonés, incluida la conversión al vocabulario habitual de Taiwán (como el intercambio entre `软件` y `軟體`).
- 33 métodos de script: además del método general `opencc.convert(text, type)`, cada tipo de conversión tiene un método abreviado con el mismo nombre, más 18 métodos de alias y métodos compuestos como `s2jp` y `tw2hk`.
- La conversión usa diccionarios locales y nunca sube el texto. La aplicación solicita Internet para consultar actualizaciones en GitHub. Las consultas automáticas están activadas por defecto, como máximo cada 12 horas, también con datos medidos; pueden desactivarse en Ajustes.
- Paquetes a medida: 4 paquetes de una sola ABI y un paquete `universal` con todas las ABI, de modo que cada dispositivo instala solo lo que necesita.
- Multilingüe: la interfaz independiente, los metadatos, las instrucciones, el README y el changelog cubren 10 idiomas.
- Un backend compartido: el editor y el servicio ligero reutilizan los mismos recursos verificados y el mismo motor nativo; las conexiones inactivas del complemento se liberan automáticamente.

******

### Captura de pantalla

******

Estas capturas Android sin retoques muestran el editor independiente en modo claro, el diseño árabe RTL con fuente al 170% en modo oscuro y la entrada existente del centro de complementos AutoJs6.

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-phone-light.png?raw=true"
           alt="Conversión independiente sin conexión con tema claro" width="280" />
      <br />
      <sub>Conversión independiente sin conexión con tema claro</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-rtl-large-dark.png?raw=true"
           alt="Diseño árabe RTL al 170% con tema oscuro" width="280" />
      <br />
      <sub>Diseño árabe RTL al 170% con tema oscuro</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/plugin-center-enabled.png?raw=true"
           alt="OpenCC 1.0.2 reconocido y activado en el centro de complementos" width="280" />
      <br />
      <sub>OpenCC 1.0.2 reconocido y activado en el centro de complementos</sub>
    </td>
  </tr>
</table>

******

### Cómo se usa

******

1. Descargue e instale un APK desde [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) o el centro de complementos AutoJs6. Elija el paquete que coincida con la ABI del dispositivo; si duda, elija `universal` o consulte `Cómo elegir un paquete`.
2. Para uso independiente, abra `OpenCC` desde el lanzador, escriba o pegue texto de forma explícita, elija uno de los 14 tipos y pulse `Convertir`. No se requiere AutoJs6 ni conceder un permiso de complemento.
3. Para usarlo como complemento, actualice AutoJs6 a la compilación interna 3923 (6.7.1 Alpha4) o superior; la versión 6.8.0 y posteriores cumplen el requisito.
4. Abra el centro de complementos AutoJs6 y confirme que `OpenCC` está reconocido y habilitado. Los paquetes oficiales superan automáticamente la verificación de firma, sin autorización manual.
5. Use directamente el objeto global `opencc` en los scripts, por ejemplo `opencc.s2t("汉字")`; no se necesita require, import ni reiniciar el host.

> Ambos modos admiten Android 7.0 (API 24) o superior. La compilación mínima de AutoJs6 solo se aplica a los scripts del complemento; la aplicación independiente no depende de un host. Si un script informa de un complemento ausente o un host antiguo, consulte las `Preguntas frecuentes`.

******

### Inicio rápido

******

Tras la instalación, el siguiente script se ejecuta tal cual; los comentarios muestran la salida esperada:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.t2jp("圖書館"));      // => 図書館
```

Los métodos abreviados son equivalentes al método general `opencc.convert(text, type)`; el propio objeto `opencc` también puede llamarse como una función, y los nombres de los tipos de conversión no distinguen mayúsculas de minúsculas:

```javascript
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
console.log(opencc("汉字转换", "s2t"));         // => 漢字轉換
```

Todos los métodos devuelven de forma síncrona la cadena convertida; la conversión se realiza sobre los diccionarios locales y nunca genera solicitudes de red.

******

### Tipos de conversión

******

El método `convert` y los métodos abreviados del mismo nombre admiten los siguientes 14 tipos de conversión estándar de OpenCC, donde S designa el chino simplificado, T el chino tradicional (estándar de OpenCC), HK el chino tradicional de Hong Kong, TW el chino tradicional de Taiwán y JP el shinjitai japonés:

| Tipo | Dirección |
|---|---|
| `S2T` | De simplificado a tradicional |
| `T2S` | De tradicional a simplificado |
| `S2TW` | De simplificado a tradicional de Taiwán |
| `TW2S` | De tradicional de Taiwán a simplificado |
| `S2TWP` | De simplificado a tradicional de Taiwán, con vocabulario habitual de Taiwán (por ejemplo, `内存` se convierte en `記憶體`) |
| `TW2SP` | De tradicional de Taiwán a simplificado, con vocabulario habitual de China continental (por ejemplo, `滑鼠` se convierte en `鼠标`) |
| `S2HK` | De simplificado a tradicional de Hong Kong |
| `HK2S` | De tradicional de Hong Kong a simplificado |
| `T2TW` | De tradicional a tradicional de Taiwán |
| `TW2T` | De tradicional de Taiwán a tradicional |
| `T2HK` | De tradicional a tradicional de Hong Kong |
| `HK2T` | De tradicional de Hong Kong a tradicional |
| `T2JP` | De tradicional (kyujitai) a shinjitai japonés |
| `JP2T` | De shinjitai japonés a tradicional (kyujitai) |

Los tipos con sufijo `P` realizan además una sustitución de vocabulario sobre la conversión de caracteres, de modo que el resultado suena natural para los lectores locales; los tipos sin `P` solo convierten las formas de los caracteres, sin tocar el vocabulario.

`T2JP` y `JP2T` convierten entre las formas tradicionales kyujitai y el shinjitai japonés, por ejemplo `圖書館` y `図書館`; tratan diferencias en la forma de los caracteres y no son una traducción entre chino y japonés.

******

### Métodos de script

******

El objeto global `opencc` del lado del host expone 33 métodos en total: el método general `convert`, 14 métodos abreviados básicos y 18 métodos de alias y métodos compuestos. El argumento `type` de `convert(text, type)` acepta los 32 nombres de conversión (tanto básicos como compuestos) sin distinguir mayúsculas de minúsculas; pasar un tipo desconocido lanza un error `Unknown OpenCC conversion type`.

Los 14 métodos abreviados básicos se corresponden uno a uno con los tipos de conversión de la tabla anterior; cada llamada realiza una conversión en el complemento:

```text
s2t   t2s   s2tw  tw2s  s2twp  tw2sp  s2hk
hk2s  t2tw  tw2t  t2hk  hk2t   t2jp   jp2t
```

`s2twi` y `twi2s` son alias de `s2twp` y `tw2sp` respectivamente (`twi` significa Taiwan idiom, es decir, vocabulario habitual de Taiwán) y se comportan de forma idéntica.

Los 16 métodos compuestos restantes encadenan varias conversiones básicas en orden y cubren las direcciones que no tienen diccionario directo:

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

Un host reciente que admita el contrato ampliado envía toda la cadena compuesta en una sola llamada al complemento; las 3 etapas de `twi2jp`, por ejemplo, requieren solo 1 ida y vuelta de Binder. Los hosts antiguos siguen llamando a cada etapa y permanecen compatibles con este complemento.

******

### Cómo elegir un paquete

******

Cada versión publicada incluye 5 APK que solo se diferencian en las arquitecturas de procesador (ABI) de la biblioteca nativa de OpenCC que incorporan:

| Paquete | Recomendado para |
|---|---|
| `arm64-v8a` | La gran mayoría de los teléfonos y tabletas Android modernos (ARM de 64 bits); la primera opción |
| `armeabi-v7a` | Dispositivos ARM de 32 bits más antiguos |
| `x86_64` | Emuladores x86 de 64 bits y unos pocos dispositivos x86 |
| `x86` | Emuladores x86 de 32 bits y unos pocos dispositivos x86 |
| `universal` | Incorpora las 4 arquitecturas y es el más grande; funciona en cualquier dispositivo y es la opción segura en caso de duda |

Si por error se instaló un paquete de una sola ABI que no corresponde a la arquitectura del dispositivo, el complemento no puede ofrecer la conversión; instalar el paquete `universal` lo resuelve.

******

### Autocomprobación rápida

******

Después de confirmar que el complemento está instalado y habilitado en el centro de complementos, ejecute este script de una sola línea para una verificación de extremo a extremo:

```javascript
console.log(opencc.s2t("汉字转换"));
```

Una salida de `漢字轉換` significa que toda la cadena del complemento funciona. Si el script falla, siga el mensaje de error: instale este complemento cuando indique que falta el complemento, active el interruptor correspondiente en el centro de complementos cuando indique que el complemento está deshabilitado o sin autorizar, y actualice AutoJs6 cuando exija un host más reciente.

******

### Preguntas frecuentes

******

#### ¿Cómo confirmo que el complemento está activo?

Abra el centro de complementos de AutoJs6; ver el complemento `OpenCC` en la lista y habilitado significa que el host lo ha reconocido. Después ejecute el script de `Autocomprobación rápida` anterior; una salida de `漢字轉換` confirma que funciona.

#### ¿Puedo usar OpenCC sin instalar AutoJs6?

Sí. Abra el icono `OpenCC` y convierta texto en el editor sin conexión. AutoJs6 solo es necesario cuando un script llama al complemento mediante el objeto global `opencc`; ambos modos proceden del mismo APK.

#### Un script informa `Missing required plugin for "OpenCC plugin"`. ¿Qué debo hacer?

Esto significa que AutoJs6 no encontró el complemento en el dispositivo. Instale el complemento y vuelva a ejecutar el script; no es necesario reiniciar AutoJs6. Si el mensaje persiste tras la instalación, asegúrese de que el sistema o una aplicación de seguridad no hayan desinstalado el complemento, y compruebe su estado de habilitación y autorización en el centro de complementos.

#### ¿Cuál es la diferencia entre `s2tw` y `s2twp` (`s2twi`)?

`s2tw` solo convierte las formas de los caracteres (por ejemplo, `软` se convierte en `軟`) y no toca el vocabulario; `s2twp` además sustituye el vocabulario de China continental por el vocabulario habitual de Taiwán (por ejemplo, `软件` se convierte en `軟體` y `鼠标` en `滑鼠`), y `s2twi` es su alias. Prefiera `s2twp` para textos dirigidos a lectores taiwaneses y `s2tw` cuando solo haya que unificar las formas de los caracteres.

#### ¿Por qué `opencc` no está disponible en los scripts que se ejecutan en el motor Node.js?

`opencc` es por ahora exclusivo de Rhino, el motor JavaScript predeterminado de AutoJs6; el entorno de ejecución de Node.js aún no ofrece una implementación correspondiente. Consulte [ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md) para conocer los planes relacionados.

#### ¿La conversión requiere conexión a la red? ¿Los textos largos son lentos?

No se necesita red; toda la conversión se realiza localmente sobre los diccionarios de OpenCC incluidos en el complemento. Cada llamada a un método es un viaje de ida y vuelta entre procesos, e incluso los textos largos suelen convertirse en un solo viaje; en bucles intensivos, prefiera los tipos básicos para evitar los viajes adicionales de los métodos compuestos.

#### ¿Qué permisos solicita el complemento? ¿Están seguros mis datos?

La conversión usa diccionarios locales y nunca sube el texto. La aplicación solicita Internet para consultar actualizaciones en GitHub. Las consultas automáticas están activadas por defecto, como máximo cada 12 horas, también con datos medidos; pueden desactivarse en Ajustes.

******

### Permisos y seguridad

******

La aplicación independiente y la entrada de complemento AutoJs6 tienen límites separados y explícitos:

- La conversión usa diccionarios locales y nunca sube el texto. La aplicación solicita Internet para consultar actualizaciones en GitHub. Las consultas automáticas están activadas por defecto, como máximo cada 12 horas, también con datos medidos; pueden desactivarse en Ajustes.
- Acciones explícitas: el Launcher no acepta texto compartido ni URI, solo lee el portapapeles tras `Pegar` y abre la hoja del sistema únicamente tras `Compartir`.
- Servicio protegido: solo los hosts con el permiso, como AutoJs6, pueden enlazarse y llamarlo. AutoJs6 también verifica la firma del paquete; otras aplicaciones no pueden invocar el servicio.
- Procesamiento local: ambas entradas usan los diccionarios integrados totalmente sin conexión. Entrada y resultado no se registran, conservan, respaldan, suben ni recopilan.

Obtenga el complemento únicamente desde la página oficial [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) o desde el centro de complementos de AutoJs6. Los paquetes de origen desconocido pueden no superar la verificación del host u ocultar riesgos aunque el número de versión parezca idéntico.

******

### Interfaz del complemento

******

La siguiente información está dirigida a los desarrolladores del host AutoJs6 y de complementos; el host usa estos identificadores para descubrir el complemento y negociar la compatibilidad:

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

`OpenccPluginService` responde a la acción `org.autojs.plugin.OPENCC` (categoría `opencc`) mediante `org.autojs.plugin.opencc.api.IOpenccPlugin` de opencc-api. La versión 2 del contrato agrega descubrimiento de tipos, conversión por lotes y conversión encadenada después de los métodos originales `getInfo()` y `convert(text, conversionType)`, y anuncia su versión y los tipos admitidos mediante `PluginInfo.capabilities`; los hosts antiguos conservan los métodos y números de transacción originales. También se proporciona una `WakeActivity` para despertar el proceso del complemento.

El complemento compila directamente OpenCC oficial `ver.1.4.2` en el commit `025f371dc76b598d77384fbdab90c937471844d8` con los recursos de la misma versión. Cada ABI contiene un único `libopencc_jni.so` enlazado estáticamente y alineado a 16 KB; la conversión sigue siendo totalmente local.

******

### Hoja de ruta

******

Los planes del complemento y su grado de avance se mantienen como una lista marcable en ROADMAP.md, organizada por hitos con criterios de aceptación, y abarcan la documentación y la experiencia de publicación, la ingeniería y la integración continua, las mejoras de la capacidad de conversión y la evolución del entorno de ejecución. Los elementos sin marcar expresan intenciones, no capacidades actuales; la discusión mediante Issues es bienvenida.

- [Ver ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### Historial de versiones

******

#### v1.4.2

_2026/09/19_

- `Corrección` Advertencias de lectura de SDK XML v4 con AGP 9.1 y comprobaciones de alineación nativa de APK activadas por error al ensamblar pruebas unitarias JVM, mediante los plugins de compilación compartidos 1.8.3
- `Mejora` Tras compileSdk, targetSdk sube a 37 (Android 17); el comportamiento del plugin no depende del nuevo objetivo

#### v1.4.1

_2026/09/15_

- `Mejora` compileSdk sube a 37 (Android 17); targetSdk se mantiene en 36 hasta verificar el comportamiento que depende del objetivo

#### v1.4.0

_2026/09/13_

- `Función` Unificar la interfaz independiente con Material 3 y añadir ajustes, información e historial de versiones, con preferencias de idioma y tema
- `Función` Añadir búsquedas manuales y automáticas opcionales de actualizaciones de GitHub, un intervalo de 12 horas y gestión de versiones ignoradas; el texto convertido permanece en el dispositivo
- `Corrección` Usar fechas de compilación en inglés independientemente del idioma de la máquina
- `Corrección` Informar solo de las ABI nativas presentes en el APK instalado
- `Corrección` Comparar correctamente los identificadores numéricos de versiones preliminares al buscar actualizaciones
- `Mejora` Puntuación uniforme en los textos de la interfaz
- `Mejora` Verificación de compilación de la alineación de páginas de 16 KB en bibliotecas nativas de 64 bits, con controles del contrato manifest e informes JSON
- `Mejora` Activación del host, metadatos, documentación traducida y recopilación de APK firmados conforme a las convenciones comunes

##### Para ver más historial de versiones

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/assets/doc/CHANGELOG-es.md)

******

### Compilación y verificación

******

Esta sección está dirigida a los desarrolladores que deseen compilar el complemento desde el código fuente; los usuarios normales pueden simplemente instalar los APK precompilados de la página Releases.

Compilar un APK debug:

```powershell
.\gradlew.bat :app:assembleDebug
```

Ejecutar las pruebas unitarias JVM y compilar el APK de pruebas instrumentation:

```powershell
.\gradlew.bat :app:testDebugUnitTest :app:assembleDebugAndroidTest
```

Compilar los APK release:

```powershell
.\gradlew.bat :app:assembleRelease
```

Recopilar los artefactos de publicación y añadir la versión, la ABI y la suma de comprobación CRC32 al nombre de cada archivo:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

Compilar los APK release y preparar sumas de comprobación y notas de la versión:

```powershell
py scripts\release\prepare_release.py
```

Comprobar que las fuentes de la documentación multilingüe y los archivos generados están sincronizados (la integración continua también lo comprueba):

```powershell
py .python\generate_markdown.py --check
```

La compilación requiere JDK 17 o superior y el SDK de Android 37; las versiones de Gradle y de los plugins se gestionan de forma centralizada mediante `version.properties` y `io.github.supermonster003.autojs6-platform-versions`.

******

### Localización y generación de documentos

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

`.readme/android_strings.json` es la única fuente para la interfaz independiente y los errores del servicio; los JSON de idioma proporcionan el README y el texto del centro de complementos. Edite siempre las fuentes JSON bajo `.readme/` y `.changelog/` y ejecute de nuevo `py .python/generate_markdown.py`; los `strings.xml`, `plugin_instruction.md`, README y changelogs generados no se editan a mano. `--check` verifica los 47 archivos generados.

******

### Licencia

******

El código del proyecto se distribuye bajo la [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE). La conversión de chino usa directamente [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0); las fuentes y licencias incluidas de OpenCC, Marisa Trie, Darts Clone y RapidJSON se detallan en los [avisos de terceros](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md).

******

### Enlaces

******

- Documentación de AutoJs6 OpenCC: https://docs.autojs6.com/#/opencc
- Proyecto AutoJs6: https://github.com/SuperMonster003/AutoJs6
- Proyecto oficial OpenCC: https://github.com/BYVoid/OpenCC
- Avisos de terceros: https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md


[16 KB page alignment and build verification](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/16kb.md)
