3-Hanzi CC es un conversor de chino sin conexión basado en OpenCC. Convierte texto entre chino simplificado, chino tradicional, tradicional de Hong Kong, tradicional de Taiwán y shinjitai japonés. Puedes usarlo por separado desde el lanzador, y además ofrece el objeto global `opencc` a los scripts de AutoJs6.

### Primeros pasos

1. Abre 3-Hanzi CC desde el lanzador y escribe texto en "Texto de origen", o toca "Pegar" para leerlo del portapapeles.
2. Elige una dirección en "Tipo de conversión" y toca "Convertir".
3. Revisa la salida en "Resultado" y toca "Copiar" o "Compartir" para usarla.
4. En los scripts de AutoJs6, llama directamente al objeto global `opencc`; el ejemplo está más abajo.

### Funciones principales

- **14 conversiones**: cubren las direcciones habituales entre simplificado, tradicional, tradicional de Hong Kong, tradicional de Taiwán y shinjitai japonés. Los tipos marcados con "Terminología de Taiwán" también reemplazan palabras; por ejemplo, "鼠标" pasa a ser "滑鼠".
- **Edición rápida**: "Invertir" cambia a la dirección de conversión opuesta, "Intercambiar" intercambia el texto de origen y el resultado, y "Borrar" elimina el texto.
- **Conversión sin conexión**: la conversión se hace en el dispositivo con diccionarios integrados y no necesita red; el texto nunca se sube ni se guarda.
- **Personalización**: ajusta el idioma, el modo oscuro, el color del tema y el icono del lanzador. Con "Recordar el tipo de conversión" activado, el último tipo de conversión se restaura la próxima vez que abras la aplicación.
- **Herramienta de plugin**: en AutoJs6 6.8.0 o posterior, el plugin también ofrece la herramienta `opencc_convert`, que pueden llamar plugins como MCP Server y la API `plugins.tools` de los scripts.

### Uso en scripts

En los scripts de AutoJs6, usa el objeto global `opencc` sin importar nada. Cada tipo de conversión tiene un método con el mismo nombre, y `convert` recibe el tipo como argumento:

```js
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
```

- Los tipos de conversión no distinguen mayúsculas de minúsculas, por ejemplo `S2T`, `S2TWP`, `HK2S` y `T2JP`. Los métodos combinados como `s2jp` y `hk2tw` ejecutan varias conversiones seguidas.
- Los scripts de Node.js lo cargan con `require('autojs6:opencc')` y los de Bun usan `host.opencc`; los métodos son los mismos y todos devuelven una Promise.

### Requisitos

- Android 7.0 o posterior. AutoJs6 no es necesario para usar la aplicación por separado desde el lanzador.
- Los scripts requieren AutoJs6 6.7.1 Alpha4 o posterior, con este plugin activado en "Centro de plugins".
- Los scripts de Node.js requieren el plugin Node.js Runtime 1.7.0 o posterior; los de Bun requieren el plugin Bun Runtime 0.2.6 o posterior, con `text.opencc` activado en su página de ajustes (activado de forma predeterminada).
- El permiso de red solo se usa para buscar actualizaciones de la aplicación. "Buscar actualizaciones automáticamente" está activado de forma predeterminada, comprueba como máximo una vez cada 12 horas y se puede desactivar en "Ajustes".

### Preguntas frecuentes

**Uso sin AutoJs6**

Abre 3-Hanzi CC desde el lanzador para convertir texto; AutoJs6 solo es necesario cuando los scripts llaman a `opencc`.

**La diferencia entre `s2tw` y `s2twp`**

`s2tw` solo convierte los caracteres; por ejemplo, "软件" pasa a ser "軟件". `s2twp` también usa el vocabulario habitual de Taiwán; por ejemplo, "软件" pasa a ser "軟體". `s2twi` es un alias de `s2twp`.

**Cuando un script indica que falta un plugin**

Comprueba que este plugin esté instalado y activado en "Centro de plugins" de AutoJs6 y vuelve a ejecutar el script. No hace falta reiniciar AutoJs6.

Todos los métodos y tipos de conversión están en [Documentación de AutoJs6 > OpenCC](https://docs.autojs6.com/#/opencc), y el resto de la información en la [página del proyecto](https://github.com/SuperMonster003/AutoJs6-Plugin-Three-Hanzi-CC).
