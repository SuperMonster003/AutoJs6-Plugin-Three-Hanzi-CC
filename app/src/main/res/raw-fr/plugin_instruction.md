3-Hanzi CC est un convertisseur de chinois hors ligne basé sur OpenCC. Il convertit le texte entre chinois simplifié, chinois traditionnel, traditionnel de Hong Kong, traditionnel de Taïwan et shinjitai japonais. Vous pouvez l'utiliser seul depuis le lanceur, et il fournit aussi l'objet global `opencc` aux scripts AutoJs6.

### Prise en main

1. Ouvrez 3-Hanzi CC depuis le lanceur, saisissez du texte dans "Texte source" ou appuyez sur "Coller" pour lire le presse-papiers.
2. Choisissez une direction dans "Type de conversion", puis appuyez sur "Convertir".
3. Consultez la sortie dans "Résultat", puis appuyez sur "Copier" ou "Partager" pour l'utiliser.
4. Dans les scripts AutoJs6, appelez directement l'objet global `opencc`; l'exemple se trouve plus bas.

### Fonctionnalités principales

- **14 conversions**: couvrent les directions courantes entre simplifié, traditionnel, traditionnel de Hong Kong, traditionnel de Taïwan et shinjitai japonais. Les types marqués "Terminologie de Taïwan" remplacent aussi le vocabulaire, par exemple "鼠标" devient "滑鼠".
- **Édition rapide**: "Inverser" passe à la direction de conversion opposée, "Permuter" échange le texte source et le résultat, et "Effacer" supprime le texte.
- **Conversion hors ligne**: la conversion s'effectue sur l'appareil avec des dictionnaires intégrés, sans réseau; le texte n'est jamais envoyé ni enregistré.
- **Personnalisation**: réglez la langue, le mode sombre, la couleur du thème et l'icône du lanceur. Avec "Mémoriser le type de conversion" activé, le dernier type de conversion est rétabli à la prochaine ouverture.
- **Outil de plugin**: dans AutoJs6 6.8.0 ou version ultérieure, le plugin fournit aussi l'outil `opencc_convert`, que des plugins comme MCP Server et l'API `plugins.tools` des scripts peuvent appeler.

### Utilisation dans les scripts

Dans les scripts AutoJs6, utilisez l'objet global `opencc` sans rien importer. Chaque type de conversion a une méthode du même nom, et `convert` accepte le type en argument:

```js
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
```

- Les types de conversion ne sont pas sensibles à la casse, par exemple `S2T`, `S2TWP`, `HK2S` et `T2JP`. Les méthodes combinées comme `s2jp` et `hk2tw` enchaînent plusieurs conversions.
- Les scripts Node.js le chargent avec `require('autojs6:opencc')` et les scripts Bun utilisent `host.opencc`; les méthodes sont les mêmes et renvoient toutes une Promise.

### Prérequis

- Android 7.0 ou version ultérieure. AutoJs6 n'est pas nécessaire pour utiliser l'application seule depuis le lanceur.
- Les scripts nécessitent AutoJs6 6.7.1 Alpha4 ou version ultérieure, avec ce plugin activé dans "Centre des plugins".
- Les scripts Node.js nécessitent le plugin Node.js Runtime 1.7.0 ou version ultérieure; les scripts Bun nécessitent le plugin Bun Runtime 0.2.6 ou version ultérieure, avec `text.opencc` laissé activé dans sa page de paramètres (activé par défaut).
- L'autorisation réseau sert uniquement à rechercher les mises à jour de l'application. "Rechercher automatiquement les mises à jour" est activé par défaut, vérifie au plus une fois toutes les 12 heures et peut être désactivé dans "Paramètres".

### Questions fréquentes

**Utilisation sans AutoJs6**

Ouvrez 3-Hanzi CC depuis le lanceur pour convertir du texte; AutoJs6 n'est nécessaire que lorsque des scripts appellent `opencc`.

**La différence entre `s2tw` et `s2twp`**

`s2tw` convertit uniquement les caractères, par exemple "软件" devient "軟件"; `s2twp` remplace aussi le vocabulaire par les termes courants à Taïwan, par exemple "软件" devient "軟體". `s2twi` est un alias de `s2twp`.

**Lorsqu'un script signale un plugin manquant**

Vérifiez que ce plugin est installé et activé dans "Centre des plugins" d'AutoJs6, puis relancez le script. Il n'est pas nécessaire de redémarrer AutoJs6.

Toutes les méthodes et tous les types de conversion figurent dans [Documentation AutoJs6 > OpenCC](https://docs.autojs6.com/#/opencc), et les autres informations sur la [page du projet](https://github.com/SuperMonster003/AutoJs6-Plugin-Three-Hanzi-CC).
