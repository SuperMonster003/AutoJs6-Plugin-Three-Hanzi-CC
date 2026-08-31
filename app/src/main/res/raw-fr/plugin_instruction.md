Le plugin OpenCC (OpenCC Plugin) apporte à AutoJs6 la conversion de texte chinois basée sur [OpenCC](https://github.com/BYVoid/OpenCC). Une fois le plugin installé, l'objet global `opencc` des scripts AutoJs6 fonctionne immédiatement: une seule ligne de code convertit le texte entre chinois simplifié, chinois traditionnel, chinois traditionnel de Hong Kong, chinois traditionnel de Taïwan et shinjitai japonais, sans import de module et sans accès au réseau.

### Démarrage rapide

Après l'installation, le script suivant s'exécute tel quel; les commentaires indiquent la sortie attendue:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
```

### Types de conversion

La méthode `convert` et les méthodes raccourcies du même nom prennent en charge les 14 types de conversion standard OpenCC suivants, où S désigne le chinois simplifié, T le chinois traditionnel (norme OpenCC), HK le chinois traditionnel de Hong Kong, TW le chinois traditionnel de Taïwan et JP le shinjitai japonais:

```text
S2T   T2S   S2TW  TW2S  S2TWP  TW2SP  S2HK
HK2S  T2TW  TW2T  T2HK  HK2T   T2JP   JP2T
```

Les types portant le suffixe `P` effectuent aussi une substitution de vocabulaire en plus de la conversion des caractères, afin que le résultat paraisse naturel aux lecteurs locaux; les types sans `P` ne convertissent que les formes de caractères, sans toucher au vocabulaire.

### Autodiagnostic rapide

Après avoir confirmé que le plugin est installé et activé dans le centre de plugins, exécutez ce script d'une seule ligne pour une vérification de bout en bout:

```javascript
console.log(opencc.s2t("汉字转换"));
```

Une sortie `漢字轉換` signifie que toute la chaîne du plugin fonctionne. Si le script échoue, suivez le message d'erreur: installez ce plugin s'il signale un plugin manquant, activez le commutateur correspondant dans le centre de plugins s'il signale un plugin désactivé ou non autorisé, et mettez AutoJs6 à jour s'il exige un hôte plus récent.

Consultez la [documentation AutoJs6 OpenCC](https://docs.autojs6.com/#/opencc) et le [README du projet](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC) pour la liste complète des méthodes et la référence des types de conversion.
