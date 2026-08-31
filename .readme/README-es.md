<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>Complemento OpenCC para la conversión de texto chino</p>

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

El complemento OpenCC (OpenCC Plugin) aporta a AutoJs6 la conversión de texto chino basada en [OpenCC](https://github.com/BYVoid/OpenCC). Una vez instalado el complemento, el objeto global `opencc` de los scripts de AutoJs6 funciona de inmediato: una sola línea de código convierte el texto entre chino simplificado, chino tradicional, chino tradicional de Hong Kong, chino tradicional de Taiwán y shinjitai japonés, sin necesidad de importar módulos y sin acceso a la red.

El complemento sigue un reparto de tareas entre host y complemento: el host AutoJs6 proporciona la API `opencc` que los scripts llaman directamente, mientras que el complemento incorpora el motor de conversión y los diccionarios de OpenCC como una aplicación independiente. Desde AutoJs6 6.8.0, el host ya no integra el entorno de ejecución de OpenCC y se apoya en este complemento; así el paquete del host se mantiene ligero y el motor de conversión puede actualizarse con independencia del host.

******

### Funciones destacadas

******

- Funciona desde el primer momento: una vez instalado, AutoJs6 descubre el complemento automáticamente; no hace falta reiniciar el host ni configurar nada antes de que los scripts puedan llamar al objeto global `opencc`.
- 14 conversiones estándar: cubre la conversión entre simplificado y tradicional de OpenCC, las variantes de Hong Kong y Taiwán y el shinjitai japonés, incluida la conversión al vocabulario habitual de Taiwán (como el intercambio entre `软件` y `軟體`).
- 33 métodos de script: además del método general `opencc.convert(text, type)`, cada tipo de conversión tiene un método abreviado con el mismo nombre, más 18 métodos de alias y métodos compuestos como `s2jp` y `tw2hk`.
- Totalmente sin conexión: la conversión se realiza localmente sobre los diccionarios integrados del complemento; el complemento no solicita permiso de red y no recopila ningún dato.
- Paquetes a medida: 4 paquetes de una sola ABI y un paquete `universal` con todas las ABI, de modo que cada dispositivo instala solo lo que necesita.
- Multilingüe: los metadatos del complemento, las instrucciones de uso, el README y el changelog cubren 10 idiomas.
- Servicio en segundo plano ligero: el complemento no tiene interfaz propia; el host lo despierta y se enlaza a él bajo demanda, y las conexiones inactivas se liberan automáticamente.

******

### Cómo se usa

******

1. Actualice AutoJs6 a la compilación interna 3923 (6.7.1 Alpha4) o superior; la versión oficial 6.8.0 y todas las posteriores cumplen este requisito.
2. Descargue e instale el APK del complemento desde la página [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) o desde el centro de complementos de AutoJs6; en caso de duda, elija el paquete `universal` o consulte `Cómo elegir un paquete` más abajo.
3. Abra el centro de complementos de AutoJs6 y confirme que el complemento `OpenCC` está reconocido y habilitado; los paquetes oficiales superan automáticamente la verificación de firma, sin necesidad de autorización manual.
4. Use directamente el objeto global `opencc` en los scripts, por ejemplo `opencc.s2t("汉字")`; no se necesita require ni import, y no hace falta reiniciar AutoJs6 después de instalar el complemento.

> El complemento es compatible con dispositivos con Android 7.0 (API 24) o superior. Si un script indica que falta el complemento o que el host está desactualizado, consulte las `Preguntas frecuentes` más abajo.

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

Cada paso de un método compuesto es una llamada independiente al complemento; `twi2jp`, por ejemplo, realiza 3 conversiones sucesivas. Para bucles intensivos o textos muy largos, prefiera los tipos básicos para reducir el número de llamadas.

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

#### ¿Por qué no hay un icono del complemento en la lista de aplicaciones?

Es lo esperado. El complemento no tiene interfaz propia ni crea ningún icono de inicio; tras la instalación, AutoJs6 lo descubre y lo llama en segundo plano, y toda la interacción ocurre dentro de AutoJs6.

#### Un script informa `Missing required plugin for "OpenCC plugin"`. ¿Qué debo hacer?

Esto significa que AutoJs6 no encontró el complemento en el dispositivo. Instale el complemento y vuelva a ejecutar el script; no es necesario reiniciar AutoJs6. Si el mensaje persiste tras la instalación, asegúrese de que el sistema o una aplicación de seguridad no hayan desinstalado el complemento, y compruebe su estado de habilitación y autorización en el centro de complementos.

#### ¿Cuál es la diferencia entre `s2tw` y `s2twp` (`s2twi`)?

`s2tw` solo convierte las formas de los caracteres (por ejemplo, `软` se convierte en `軟`) y no toca el vocabulario; `s2twp` además sustituye el vocabulario de China continental por el vocabulario habitual de Taiwán (por ejemplo, `软件` se convierte en `軟體` y `鼠标` en `滑鼠`), y `s2twi` es su alias. Prefiera `s2twp` para textos dirigidos a lectores taiwaneses y `s2tw` cuando solo haya que unificar las formas de los caracteres.

#### ¿Por qué `opencc` no está disponible en los scripts que se ejecutan en el motor Node.js?

`opencc` es por ahora exclusivo de Rhino, el motor JavaScript predeterminado de AutoJs6; el entorno de ejecución de Node.js aún no ofrece una implementación correspondiente. Consulte [ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md) para conocer los planes relacionados.

#### ¿La conversión requiere conexión a la red? ¿Los textos largos son lentos?

No se necesita red; toda la conversión se realiza localmente sobre los diccionarios de OpenCC incluidos en el complemento. Cada llamada a un método es un viaje de ida y vuelta entre procesos, e incluso los textos largos suelen convertirse en un solo viaje; en bucles intensivos, prefiera los tipos básicos para evitar los viajes adicionales de los métodos compuestos.

#### ¿Qué permisos solicita el complemento? ¿Están seguros mis datos?

El complemento solo declara el permiso de complemento usado para comunicarse con AutoJs6 y no solicita permisos sensibles del sistema como red o almacenamiento; su servicio está protegido por el mismo permiso, por lo que otras aplicaciones no pueden llamarlo. El texto que se convierte permanece en la memoria del dispositivo y nunca se almacena ni se sube.

******

### Permisos y seguridad

******

El complemento y AutoJs6 establecen la confianza mediante los mecanismos de permisos y firmas del sistema Android:

- Permisos mínimos: el manifiesto declara únicamente el permiso de complemento `org.autojs.permission.PLUGIN`, sin ningún permiso sensible del sistema como red, almacenamiento o cámara.
- Protección bidireccional: el servicio del complemento está protegido por el mismo permiso, de modo que solo los hosts que poseen el permiso de complemento (como AutoJs6) pueden enlazarse a él y llamarlo; otras aplicaciones no tienen acceso.
- Autorización por firma: AutoJs6 verifica la firma del complemento; los paquetes oficiales se autorizan automáticamente, mientras que las compilaciones con otras firmas deben autorizarse manualmente en el centro de complementos antes de cargarse.
- Procesamiento local: la conversión ocurre por completo en el dispositivo; el complemento nunca se conecta a la red, no escribe nada en el disco y no recopila datos del usuario.

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
aidl methods: getInfo(), convert(text, conversionType)
minimum host build: 3923 (6.7.1 Alpha4)
conversion library: com.github.brooklet:android-opencc:1.2.2
```

`OpenccPluginService` responde a la acción `org.autojs.plugin.OPENCC` (categoría `opencc`); la interfaz Binder es `org.autojs.plugin.opencc.api.IOpenccPlugin`, proporcionada por opencc-api, con exactamente dos métodos, `getInfo()` y `convert(text, conversionType)`. También se proporciona una `WakeActivity` para que el host pueda despertar el proceso del complemento.

`PluginInfo.supportedAbis` informa de las cuatro arquitecturas `arm64-v8a`, `armeabi-v7a`, `x86_64` y `x86` para que el host y el centro de complementos puedan identificar las variantes disponibles; la conversión corre a cargo del motor y los diccionarios de OpenCC de `com.github.brooklet:android-opencc:1.2.2`.

******

### Hoja de ruta

******

Los planes del complemento y su grado de avance se mantienen como una lista marcable en ROADMAP.md, organizada por hitos con criterios de aceptación, y abarcan la documentación y la experiencia de publicación, la ingeniería y la integración continua, las mejoras de la capacidad de conversión y la evolución del entorno de ejecución. Los elementos sin marcar expresan intenciones, no capacidades actuales; la discusión mediante Issues es bienvenida.

- [Ver ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### Historial de versiones

******

#### v1.0.2

_2026/08/31_

- `Aviso` Esta versión mejora únicamente la documentación y el flujo de compilación; el comportamiento de conversión de OpenCC y los 14 tipos de conversión principales no cambian
- `Mejora` Reestructuración del README en los 10 idiomas con pasos de instalación, una guía para elegir paquetes, una comprobación rápida, la lista completa de 33 métodos de script, preguntas frecuentes y detalles sobre permisos y seguridad
- `Mejora` Generación de las instrucciones del centro de complementos desde la misma fuente JSON localizada que el README y el CHANGELOG, manteniendo sincronizados todos los documentos de Android desde una única fuente
- `Mejora` Refuerzo de la validación de la documentación y ejecución en GitHub Actions, con detección automática de estructuras incoherentes entre idiomas, archivos generados desactualizados, artefactos huérfanos, versiones no alineadas y marcadores residuales
- `Mejora` Incorporación de ROADMAP.md con listas de hitos verificables para documentación, ingeniería, capacidades de conversión y evolución del entorno de ejecución
- `Mejora` Migración de la configuración de Gradle a `org.autojs.build.platform-versions` 1.4.1 y uso de foojay para resolver el JDK automáticamente, simplificando y normalizando el entorno de compilación

#### v1.0.1

_2026/07/14_

- `Mejora` Distribución de paquetes divididos por arquitectura de procesador (ABI): paquetes de una sola ABI para `arm64-v8a`, `armeabi-v7a`, `x86_64` y `x86`, más un paquete `universal` con todas las arquitecturas, de modo que cada dispositivo instala solo lo que necesita y las descargas son más pequeñas
- `Mejora` Publicación de la lista de ABI compatibles en la información del complemento, para que AutoJs6 y el centro de complementos puedan identificar las variantes del complemento adecuadas para el dispositivo actual
- `Mejora` Incorporación de la versión, la ABI y la suma de comprobación CRC32 a los nombres de los archivos APK publicados, lo que facilita verificar la integridad de los archivos descargados

#### v1.0.0

_2026/07/14_

- `Función` Primera versión estable: proporciona a AutoJs6 la conversión de chino de OpenCC como complemento independiente, con el ID del complemento y el motor establecidos ambos en `opencc`
- `Función` AutoJs6 descubre y llama al complemento automáticamente mediante `org.autojs.plugin.OPENCC`; funciona justo después de la instalación, sin configuración ni reinicio
- `Función` Compatibilidad con los 14 tipos de conversión estándar de OpenCC, que cubren la conversión entre simplificado y tradicional, las variantes de Hong Kong y Taiwán y el shinjitai japonés: `S2T`/`S2TW`/`S2TWP`/`S2HK`/`T2S`/`T2TW`/`T2HK`/`T2JP`/`TW2S`/`TW2T`/`TW2SP`/`HK2S`/`HK2T`/`JP2T`
- `Función` Metadatos del complemento e instrucciones de uso localizados en 10 idiomas: chino simplificado, chino tradicional de Hong Kong, chino tradicional de Taiwán, inglés, francés, español, japonés, coreano, ruso y árabe
- `Función` README multilingüe con ejemplos de uso, instrucciones de compilación y enlaces relacionados

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

Compilar los APK release; se firman automáticamente cuando se configura una identidad de firma en `sign.properties`, ignorado por Git, y los artefactos sin firmar no deben publicarse:

```powershell
.\gradlew.bat :app:assembleRelease
```

Recopilar los artefactos de publicación y añadir la versión, la ABI y la suma de comprobación CRC32 al nombre de cada archivo:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

Comprobar que las fuentes de la documentación multilingüe y los archivos generados están sincronizados (la integración continua también lo comprueba):

```powershell
py .python\generate_markdown.py --check
```

La compilación requiere JDK 17 o superior y el SDK de Android 36; las versiones de Gradle y de los plugins se gestionan de forma centralizada mediante `version.properties` y `org.autojs.build.platform-versions`.

******

### Localización y generación de documentos

******

```text
.readme/common.json
.readme/lang_*.json
.readme/template_readme.md
.readme/template_plugin_instruction.md
.changelog/lang_*.json
.changelog/template_changelog.md
.python/generate_markdown.py
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml` contiene la descripción localizada del complemento y los mensajes de error, y `plugin_instruction.md` contiene las instrucciones de uso que se muestran en el centro de complementos del host. Para el README y el changelog, edite siempre las fuentes JSON bajo `.readme/` y `.changelog/` y vuelva a ejecutar `py .python/generate_markdown.py`; los archivos generados nunca se editan a mano. Ejecute `py .python/generate_markdown.py --check` para comprobar que las fuentes y los archivos generados están sincronizados.

******

### Licencia

******

El código del proyecto se distribuye bajo la [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE). La conversión de chino corre a cargo de [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0) y su envoltorio para Android [android-opencc](https://github.com/qichuan/android-opencc).

******

### Enlaces

******

- Documentación de AutoJs6 OpenCC: https://docs.autojs6.com/#/opencc
- Proyecto AutoJs6: https://github.com/SuperMonster003/AutoJs6
- Proyecto oficial OpenCC: https://github.com/BYVoid/OpenCC
- Proyecto Android OpenCC: https://github.com/qichuan/android-opencc
