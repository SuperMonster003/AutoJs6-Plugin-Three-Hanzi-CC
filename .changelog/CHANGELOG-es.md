******

### Historial de versiones

******

# v1.0.1

###### 2026/07/14

* `Mejora` Se añadieron compilaciones APK divididas por ABI para `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` y un APK `universal`
* `Mejora` Se añadieron metadatos de ABI compatibles a la información de ejecución del complemento para que el host pueda identificar variantes compatibles
* `Mejora` Los nombres de los APK publicados ahora incluyen la versión, la variante ABI y el resumen CRC32

# v1.0.0

###### 2026/07/14

* `Función` Se añadió el servicio del complemento OpenCC con ID `opencc` y motor `opencc`
* `Función` Se añadió descubrimiento e invocación desde el host mediante `org.autojs.plugin.OPENCC`
* `Función` Se admitieron tipos de conversión OpenCC comunes: `S2T`, `S2TW`, `S2TWP`, `S2HK`, `T2S`, `T2TW`, `T2HK`, `T2JP`, `TW2S`, `TW2T`, `TW2SP`, `HK2S`, `HK2T` y `JP2T`
* `Función` Se añadieron metadatos e instrucciones de uso localizados para español, francés, ruso, árabe, japonés, coreano, inglés, chino simplificado, chino tradicional de Hong Kong y chino tradicional de Taiwán
* `Función` Se añadió un README bilingüe chino/inglés con ejemplos de uso, instrucciones de compilación y enlaces relacionados
