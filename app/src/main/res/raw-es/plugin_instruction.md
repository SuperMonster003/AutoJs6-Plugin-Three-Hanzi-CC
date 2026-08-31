El complemento OpenCC (OpenCC Plugin) aporta a AutoJs6 la conversión de texto chino basada en [OpenCC](https://github.com/BYVoid/OpenCC). Una vez instalado el complemento, el objeto global `opencc` de los scripts de AutoJs6 funciona de inmediato: una sola línea de código convierte el texto entre chino simplificado, chino tradicional, chino tradicional de Hong Kong, chino tradicional de Taiwán y shinjitai japonés, sin necesidad de importar módulos y sin acceso a la red.

### Inicio rápido

Tras la instalación, el siguiente script se ejecuta tal cual; los comentarios muestran la salida esperada:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
```

### Tipos de conversión

El método `convert` y los métodos abreviados del mismo nombre admiten los siguientes 14 tipos de conversión estándar de OpenCC, donde S designa el chino simplificado, T el chino tradicional (estándar de OpenCC), HK el chino tradicional de Hong Kong, TW el chino tradicional de Taiwán y JP el shinjitai japonés:

```text
S2T   T2S   S2TW  TW2S  S2TWP  TW2SP  S2HK
HK2S  T2TW  TW2T  T2HK  HK2T   T2JP   JP2T
```

Los tipos con sufijo `P` realizan además una sustitución de vocabulario sobre la conversión de caracteres, de modo que el resultado suena natural para los lectores locales; los tipos sin `P` solo convierten las formas de los caracteres, sin tocar el vocabulario.

### Autocomprobación rápida

Después de confirmar que el complemento está instalado y habilitado en el centro de complementos, ejecute este script de una sola línea para una verificación de extremo a extremo:

```javascript
console.log(opencc.s2t("汉字转换"));
```

Una salida de `漢字轉換` significa que toda la cadena del complemento funciona. Si el script falla, siga el mensaje de error: instale este complemento cuando indique que falta el complemento, active el interruptor correspondiente en el centro de complementos cuando indique que el complemento está deshabilitado o sin autorizar, y actualice AutoJs6 cuando exija un host más reciente.

Consulte la [documentación de AutoJs6 OpenCC](https://docs.autojs6.com/#/opencc) y el [README del proyecto](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC) para ver la lista completa de métodos y la referencia de tipos de conversión.
