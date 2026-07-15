******

### Historique des versions

******

# v1.0.1

###### 2026/07/14

* `Amélioration` Ajout de builds APK divisés par ABI pour `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` et un APK `universal`
* `Amélioration` Ajout des métadonnées ABI prises en charge aux informations d'exécution du plugin afin que l'hôte puisse identifier les variantes compatibles
* `Amélioration` Les noms des APK publiés incluent maintenant la version, la variante ABI et le résumé CRC32

# v1.0.0

###### 2026/07/14

* `Fonctionnalité` Ajout du service de plugin OpenCC avec l'ID `opencc` et le moteur `opencc`
* `Fonctionnalité` Ajout de la découverte et de l'appel par l'hôte via `org.autojs.plugin.OPENCC`
* `Fonctionnalité` Prise en charge des types de conversion OpenCC courants: `S2T`, `S2TW`, `S2TWP`, `S2HK`, `T2S`, `T2TW`, `T2HK`, `T2JP`, `TW2S`, `TW2T`, `TW2SP`, `HK2S`, `HK2T` et `JP2T`
* `Fonctionnalité` Ajout des métadonnées de plugin et des instructions d'utilisation localisées en espagnol, français, russe, arabe, japonais, coréen, anglais, chinois simplifié, chinois traditionnel de Hong Kong et chinois traditionnel de Taïwan
* `Fonctionnalité` Ajout d'un README bilingue chinois/anglais avec des exemples d'utilisation, des instructions de compilation et des liens associés
