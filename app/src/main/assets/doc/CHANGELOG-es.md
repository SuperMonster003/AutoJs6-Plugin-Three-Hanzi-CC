******

### Historial de versiones

******

# v1.0.1

###### 2026/07/14

* `Mejora` Distribución de paquetes divididos por arquitectura de procesador (ABI): paquetes de una sola ABI para `arm64-v8a`, `armeabi-v7a`, `x86_64` y `x86`, más un paquete `universal` con todas las arquitecturas, de modo que cada dispositivo instala solo lo que necesita y las descargas son más pequeñas
* `Mejora` Publicación de la lista de ABI compatibles en la información del complemento, para que AutoJs6 y el centro de complementos puedan identificar las variantes del complemento adecuadas para el dispositivo actual
* `Mejora` Incorporación de la versión, la ABI y la suma de comprobación CRC32 a los nombres de los archivos APK publicados, lo que facilita verificar la integridad de los archivos descargados

# v1.0.0

###### 2026/07/14

* `Función` Primera versión estable: proporciona a AutoJs6 la conversión de chino de OpenCC como complemento independiente, con el ID del complemento y el motor establecidos ambos en `opencc`
* `Función` AutoJs6 descubre y llama al complemento automáticamente mediante `org.autojs.plugin.OPENCC`; funciona justo después de la instalación, sin configuración ni reinicio
* `Función` Compatibilidad con los 14 tipos de conversión estándar de OpenCC, que cubren la conversión entre simplificado y tradicional, las variantes de Hong Kong y Taiwán y el shinjitai japonés: `S2T`/`S2TW`/`S2TWP`/`S2HK`/`T2S`/`T2TW`/`T2HK`/`T2JP`/`TW2S`/`TW2T`/`TW2SP`/`HK2S`/`HK2T`/`JP2T`
* `Función` Metadatos del complemento e instrucciones de uso localizados en 10 idiomas: chino simplificado, chino tradicional de Hong Kong, chino tradicional de Taiwán, inglés, francés, español, japonés, coreano, ruso y árabe
* `Función` README multilingüe con ejemplos de uso, instrucciones de compilación y enlaces relacionados
