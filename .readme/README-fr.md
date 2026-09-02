<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>Convertisseur chinois OpenCC hors ligne, autonome et compatible avec AutoJs6</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-OpenCC?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-OpenCC?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-OpenCC?color=534BAE&label=License"/></a>
  </p>
</div>

******

### Langues (Languages)

******

Le README.md actuel prend en charge les langues suivantes:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-en.md)
- Français [fr] # actuel
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ar.md)

******

### Introduction

******

OpenCC réunit dans une seule installation deux accès à la conversion de texte chinois basée sur [OpenCC](https://github.com/BYVoid/OpenCC). Lancez directement l'application Android entièrement hors ligne, ou laissez AutoJs6 reconnaître le même APK comme plugin et utilisez l'objet global `opencc` dans les scripts. Les deux voies couvrent le chinois simplifié, le chinois traditionnel, les variantes de Hong Kong et de Taïwan, ainsi que le shinjitai japonais.

L'éditeur autonome et le service Binder AutoJs6 protégé par autorisation partagent un seul moteur OpenCC officiel, les mêmes dictionnaires verrouillés, le cache, les types de conversion et le modèle d'erreur. L'application ne nécessite pas AutoJs6, tandis que le mode plugin conserve l'API de script existante et permet de mettre le moteur à jour indépendamment de l'hôte.

******

### Points forts

******

- Un APK, deux usages: ouvrez l'icône de lancement pour convertir visuellement du texte sans AutoJs6, ou utilisez la même installation via l'API de script `opencc` d'AutoJs6.
- 14 conversions standard: couvre la conversion simplifié-traditionnel d'OpenCC, les variantes de Hong Kong et de Taïwan ainsi que le shinjitai japonais, y compris la conversion du vocabulaire courant de Taïwan (comme l'échange entre `软件` et `軟體`).
- 33 méthodes de script: outre la méthode générale `opencc.convert(text, type)`, chaque type de conversion dispose d'une méthode raccourcie du même nom, plus 18 méthodes d'alias et méthodes composées telles que `s2jp` et `tw2hk`.
- Entièrement hors ligne: la conversion s'effectue localement sur les dictionnaires intégrés du plugin; le plugin ne demande aucune autorisation réseau et ne collecte aucune donnée.
- Paquets au plus juste: 4 paquets à ABI unique et un paquet `universal` regroupant toutes les ABI, afin que chaque appareil n'installe que le nécessaire.
- Multilingue: l'interface autonome, les métadonnées du plugin, les instructions, le README et le changelog couvrent 10 langues.
- Un backend partagé: l'éditeur et le service léger réutilisent les mêmes ressources vérifiées et le même moteur natif; les connexions inactives du plugin sont libérées automatiquement.

******

### Capture d'écran

******

Ces captures Android non retouchées montrent l'éditeur autonome en mode jour, la disposition arabe RTL avec une police à 170% en mode nuit, puis l'entrée existante du centre de plugins AutoJs6.

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-phone-light.png?raw=true"
           alt="Conversion autonome hors ligne avec le thème clair" width="280" />
      <br />
      <sub>Conversion autonome hors ligne avec le thème clair</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-rtl-large-dark.png?raw=true"
           alt="Disposition arabe RTL à 170% avec le thème sombre" width="280" />
      <br />
      <sub>Disposition arabe RTL à 170% avec le thème sombre</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/plugin-center-enabled.png?raw=true"
           alt="OpenCC 1.0.2 reconnu et activé dans le centre de plugins" width="280" />
      <br />
      <sub>OpenCC 1.0.2 reconnu et activé dans le centre de plugins</sub>
    </td>
  </tr>
</table>

******

### Mode d'emploi

******

1. Téléchargez et installez un APK depuis la page [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) ou le centre de plugins AutoJs6. Choisissez le paquet correspondant à l'ABI de l'appareil; en cas de doute, choisissez `universal` ou consultez `Comment choisir un paquet` ci-dessous.
2. Pour un usage autonome, ouvrez `OpenCC` depuis le lanceur, saisissez ou collez explicitement le texte, choisissez l'un des 14 types et touchez `Convertir`. AutoJs6 et l'octroi d'une autorisation de plugin ne sont pas requis.
3. Pour le mode plugin, mettez AutoJs6 à jour vers le build interne 3923 (6.7.1 Alpha4) ou ultérieur; la version 6.8.0 et les suivantes satisfont cette exigence.
4. Ouvrez le centre de plugins AutoJs6 et vérifiez que `OpenCC` est reconnu et activé. Les paquets officiels passent automatiquement la vérification de signature, sans autorisation manuelle.
5. Utilisez directement l'objet global `opencc` dans les scripts, par exemple `opencc.s2t("汉字")`; aucun require, import ni redémarrage de l'hôte n'est nécessaire.

> Les deux modes prennent en charge Android 7.0 (API 24) ou ultérieur. Le build AutoJs6 minimal ne concerne que les scripts du plugin; l'application autonome ne dépend d'aucun hôte. Si un script signale un plugin absent ou un hôte ancien, consultez les `Questions fréquentes`.

******

### Démarrage rapide

******

Après l'installation, le script suivant s'exécute tel quel; les commentaires indiquent la sortie attendue:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.t2jp("圖書館"));      // => 図書館
```

Les méthodes raccourcies sont équivalentes à la méthode générale `opencc.convert(text, type)`; l'objet `opencc` lui-même peut aussi être appelé comme une fonction, et les noms de types de conversion sont insensibles à la casse:

```javascript
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
console.log(opencc("汉字转换", "s2t"));         // => 漢字轉換
```

Toutes les méthodes renvoient de manière synchrone la chaîne convertie; la conversion s'effectue sur les dictionnaires locaux et n'émet jamais de requête réseau.

******

### Types de conversion

******

La méthode `convert` et les méthodes raccourcies du même nom prennent en charge les 14 types de conversion standard OpenCC suivants, où S désigne le chinois simplifié, T le chinois traditionnel (norme OpenCC), HK le chinois traditionnel de Hong Kong, TW le chinois traditionnel de Taïwan et JP le shinjitai japonais:

| Type | Direction |
|---|---|
| `S2T` | Simplifié vers traditionnel |
| `T2S` | Traditionnel vers simplifié |
| `S2TW` | Simplifié vers traditionnel de Taïwan |
| `TW2S` | Traditionnel de Taïwan vers simplifié |
| `S2TWP` | Simplifié vers traditionnel de Taïwan, avec vocabulaire courant de Taïwan (par exemple `内存` devient `記憶體`) |
| `TW2SP` | Traditionnel de Taïwan vers simplifié, avec vocabulaire courant de Chine continentale (par exemple `滑鼠` devient `鼠标`) |
| `S2HK` | Simplifié vers traditionnel de Hong Kong |
| `HK2S` | Traditionnel de Hong Kong vers simplifié |
| `T2TW` | Traditionnel vers traditionnel de Taïwan |
| `TW2T` | Traditionnel de Taïwan vers traditionnel |
| `T2HK` | Traditionnel vers traditionnel de Hong Kong |
| `HK2T` | Traditionnel de Hong Kong vers traditionnel |
| `T2JP` | Traditionnel (kyujitai) vers shinjitai japonais |
| `JP2T` | Shinjitai japonais vers traditionnel (kyujitai) |

Les types portant le suffixe `P` effectuent aussi une substitution de vocabulaire en plus de la conversion des caractères, afin que le résultat paraisse naturel aux lecteurs locaux; les types sans `P` ne convertissent que les formes de caractères, sans toucher au vocabulaire.

`T2JP` et `JP2T` convertissent entre les formes traditionnelles kyujitai et le shinjitai japonais, par exemple `圖書館` et `図書館`; ils traitent des différences de forme des caractères et ne constituent pas une traduction entre le chinois et le japonais.

******

### Méthodes de script

******

L'objet global `opencc` côté hôte expose 33 méthodes au total: la méthode générale `convert`, 14 raccourcis de base et 18 méthodes d'alias et méthodes composées. L'argument `type` de `convert(text, type)` accepte les 32 noms de conversion (de base comme composés) sans distinction de casse; passer un type inconnu lève une erreur `Unknown OpenCC conversion type`.

Les 14 raccourcis de base correspondent un à un aux types de conversion du tableau ci-dessus; chaque appel effectue une conversion via le plugin:

```text
s2t   t2s   s2tw  tw2s  s2twp  tw2sp  s2hk
hk2s  t2tw  tw2t  t2hk  hk2t   t2jp   jp2t
```

`s2twi` et `twi2s` sont respectivement des alias de `s2twp` et `tw2sp` (`twi` signifie Taiwan idiom, c'est-à-dire vocabulaire courant de Taïwan) et se comportent de manière identique.

Les 16 méthodes composées restantes enchaînent plusieurs conversions de base dans l'ordre, couvrant les directions qui n'ont pas de dictionnaire direct:

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

Un hôte récent prenant en charge le contrat étendu transmet toute la chaîne composée en un seul appel au plugin; les 3 étapes de `twi2jp`, par exemple, ne demandent qu'un aller-retour Binder. Les anciens hôtes continuent d'appeler chaque étape et restent compatibles avec ce plugin.

******

### Comment choisir un paquet

******

Chaque version publiée comprend 5 APK qui ne diffèrent que par les architectures de processeur (ABI) de la bibliothèque native OpenCC qu'ils embarquent:

| Paquet | Recommandé pour |
|---|---|
| `arm64-v8a` | La grande majorité des téléphones et tablettes Android modernes (ARM 64 bits); premier choix |
| `armeabi-v7a` | Appareils ARM 32 bits plus anciens |
| `x86_64` | Émulateurs x86 64 bits et quelques appareils x86 |
| `x86` | Émulateurs x86 32 bits et quelques appareils x86 |
| `universal` | Regroupe les 4 architectures et est le plus volumineux; fonctionne sur tout appareil et reste le choix sûr en cas de doute |

Si un paquet à ABI unique ne correspondant pas à l'architecture de l'appareil a été installé par erreur, le plugin ne peut pas fournir la conversion; installer le paquet `universal` résout le problème.

******

### Autodiagnostic rapide

******

Après avoir confirmé que le plugin est installé et activé dans le centre de plugins, exécutez ce script d'une seule ligne pour une vérification de bout en bout:

```javascript
console.log(opencc.s2t("汉字转换"));
```

Une sortie `漢字轉換` signifie que toute la chaîne du plugin fonctionne. Si le script échoue, suivez le message d'erreur: installez ce plugin s'il signale un plugin manquant, activez le commutateur correspondant dans le centre de plugins s'il signale un plugin désactivé ou non autorisé, et mettez AutoJs6 à jour s'il exige un hôte plus récent.

******

### Questions fréquentes

******

#### Comment confirmer que le plugin est actif?

Ouvrez le centre de plugins d'AutoJs6; voir le plugin `OpenCC` répertorié et activé signifie que l'hôte l'a reconnu. Exécutez ensuite le script `Autodiagnostic rapide` ci-dessus; une sortie `漢字轉換` confirme qu'il fonctionne.

#### Puis-je utiliser OpenCC sans installer AutoJs6?

Oui. Ouvrez l'icône `OpenCC` et convertissez le texte dans l'éditeur hors ligne. AutoJs6 n'est nécessaire que lorsqu'un script appelle le plugin via l'objet global `opencc`; les deux modes proviennent du même APK.

#### Un script signale `Missing required plugin for "OpenCC plugin"`. Que faire?

Cela signifie qu'AutoJs6 n'a pas trouvé le plugin sur l'appareil. Installez le plugin puis exécutez à nouveau le script; aucun redémarrage d'AutoJs6 n'est nécessaire. Si le message persiste après l'installation, assurez-vous que le plugin n'a pas été désinstallé par le système ou une application de sécurité, et vérifiez son état d'activation et d'autorisation dans le centre de plugins.

#### Quelle est la différence entre `s2tw` et `s2twp` (`s2twi`)?

`s2tw` ne convertit que les formes de caractères (par exemple `软` devient `軟`) sans toucher au vocabulaire; `s2twp` remplace en plus le vocabulaire de Chine continentale par le vocabulaire courant de Taïwan (par exemple `软件` devient `軟體` et `鼠标` devient `滑鼠`), et `s2twi` en est l'alias. Préférez `s2twp` pour les textes destinés aux lecteurs taïwanais et `s2tw` lorsque seules les formes de caractères doivent être unifiées.

#### Pourquoi `opencc` est-il indisponible dans les scripts exécutés sur le moteur Node.js?

`opencc` est pour l'instant exclusif à Rhino, le moteur JavaScript par défaut d'AutoJs6; l'environnement d'exécution Node.js ne fournit pas encore d'implémentation correspondante. Consultez [ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md) pour les plans associés.

#### La conversion nécessite-t-elle une connexion réseau? Les textes longs sont-ils lents?

Aucun réseau n'est nécessaire; toute la conversion s'effectue localement sur les dictionnaires OpenCC intégrés au plugin. Chaque appel de méthode correspond à un aller-retour interprocessus, et même les textes longs se convertissent généralement en un seul aller-retour; dans les boucles intensives, privilégiez les types de base pour éviter les allers-retours supplémentaires des méthodes composées.

#### Quelles autorisations le plugin demande-t-il? Mes données sont-elles en sécurité?

Le plugin déclare uniquement l'autorisation de plugin servant à communiquer avec AutoJs6 et ne demande aucune autorisation système sensible telle que le réseau ou le stockage; son service est protégé par la même autorisation, de sorte que les autres applications ne peuvent pas l'appeler. Le texte en cours de conversion reste dans la mémoire de l'appareil et n'est jamais stocké ni téléversé.

******

### Autorisations et sécurité

******

L'application autonome et l'entrée plugin AutoJs6 ont des limites distinctes et explicites:

- Autorisations minimales: le manifeste ne déclare que `org.autojs.permission.PLUGIN` pour l'intégration, sans autorisation sensible de réseau, stockage ou caméra; l'utilisateur autonome n'accorde pas cette autorisation.
- Actions explicites: le Launcher n'accepte ni texte partagé ni URI, ne lit le presse-papiers qu'après `Coller` et n'ouvre la feuille de partage qu'après `Partager`.
- Service protégé: seuls les hôtes possédant l'autorisation, comme AutoJs6, peuvent s'y lier et l'appeler. AutoJs6 vérifie aussi la signature du paquet; les autres applications ne peuvent pas invoquer le service.
- Traitement local: les deux entrées utilisent les dictionnaires intégrés entièrement hors ligne. Entrées et résultats ne sont ni journalisés, ni conservés, ni sauvegardés, ni envoyés, ni collectés.

Obtenez le plugin uniquement depuis la page officielle [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) ou le centre de plugins d'AutoJs6. Les paquets d'origine inconnue peuvent échouer à la vérification de l'hôte ou dissimuler des risques, même lorsque le numéro de version semble identique.

******

### Interface du plugin

******

Les informations suivantes s'adressent aux développeurs de l'hôte AutoJs6 et de plugins; l'hôte utilise ces identifiants pour découvrir le plugin et négocier la compatibilité:

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

`OpenccPluginService` répond à l'action `org.autojs.plugin.OPENCC` (catégorie `opencc`) avec `org.autojs.plugin.opencc.api.IOpenccPlugin` fourni par opencc-api. La version 2 du contrat ajoute la découverte des types, la conversion par lot et la conversion en chaîne après les méthodes d'origine `getInfo()` et `convert(text, conversionType)`, puis annonce sa version et les types pris en charge via `PluginInfo.capabilities`; les anciens hôtes conservent les méthodes et numéros de transaction d'origine. Une `WakeActivity` permet aussi à l'hôte de réveiller le processus du plugin.

Le plugin compile directement OpenCC officiel `ver.1.4.2` au commit `025f371dc76b598d77384fbdab90c937471844d8` avec les ressources de la même version. Chaque ABI contient un seul `libopencc_jni.so` lié statiquement et aligné sur 16 KB; la conversion reste entièrement hors ligne.

******

### Feuille de route

******

Les plans du plugin et leur avancement sont tenus à jour sous forme de liste cochable dans ROADMAP.md, organisée par jalons avec des critères d'acceptation, couvrant la documentation et l'expérience de publication, l'ingénierie et l'intégration continue, le renforcement des capacités de conversion et l'évolution de l'environnement d'exécution. Les éléments non cochés expriment des intentions plutôt que des capacités actuelles; la discussion via Issues est la bienvenue.

- [Voir ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### Historique des versions

******

#### v1.2.0

_2026/09/01_

- `Note` Les dictionnaires d'OpenCC 1.4.2 modifient intentionnellement quelques résultats, notamment `复盘` -> `復盤`, `内卷` -> `內捲`, la préservation de `什么怎么这么` et `内存条` -> `記憶體模組`; la liste complète est dans le rapport de migration
- `Amélioration` Compiler directement OpenCC 1.4.2 officiel et les dictionnaires de la même version dans une bibliothèque JNI liée statiquement par ABI, tout en conservant une conversion entièrement hors ligne
- `Amélioration` Prendre en charge les appareils à pages de 16 KB avec NDK 28.2, l'alignement ELF et ZIP sur 16 KB et une vérification Binder sur un véritable émulateur 16 KB
- `Amélioration` Installer atomiquement le ZIP de ressources verrouillé avec contrôle de taille et SHA-256, récupération automatique après corruption, conversion JNI sûre pour Unicode et mise en cache des convertisseurs utilisés à chaud
- `Dépendance` Supprimer l'encapsulation non maintenue `com.github.brooklet:android-opencc:1.2.2` et verrouiller OpenCC officiel `ver.1.4.2` au commit `025f371dc76b598d77384fbdab90c937471844d8`
- `Dépendance` Documenter les sources et licences intégrées d'OpenCC, Marisa Trie, Darts Clone et RapidJSON dans `THIRD_PARTY_NOTICES.md`

#### v1.1.0

_2026/09/01_

- `Fonctionnalité` Passage au contrat de plugin OpenCC version 2 avec `getSupportedConversionTypes()`, afin que les hôtes récents découvrent les 14 types de conversion réellement pris en charge
- `Fonctionnalité` Ajout de `convertBatch(texts, conversionType)` pour convertir jusqu'à 1024 segments de texte en un seul aller-retour Binder, tout en conservant le traitement élément par élément pour les anciens hôtes
- `Fonctionnalité` Ajout de `convertChain(text, conversionTypes)` pour exécuter jusqu'à 32 étapes en un seul appel, ce qui réduit les méthodes composées des hôtes récents de 3 allers-retours Binder au maximum à 1
- `Amélioration` Transmission des instructions localisées via `PluginInfo.instruction` et publication de la version du contrat et des types de conversion pris en charge dans les capabilities
- `Amélioration` Conservation des méthodes AIDL et numéros de transaction d'origine, avec des tests unitaires et Binder réels couvrant les appels étendus, le repli hérité, les limites de taille et les erreurs
- `Amélioration` Uniformiser la mise en page du README et la gestion des versions de la plateforme Gradle

#### v1.0.2

_2026/08/31_

- `Note` Cette version améliore uniquement la documentation et le processus de compilation; le comportement de conversion OpenCC et les 14 types de conversion principaux restent inchangés
- `Amélioration` Refonte du README dans les 10 langues avec les étapes d'installation, un guide de sélection des paquets, une vérification rapide, la liste complète des 33 méthodes de script, une FAQ et des précisions sur les permissions et la sécurité
- `Amélioration` Génération des instructions du centre de plugins depuis la même source JSON localisée que le README et le CHANGELOG, afin de synchroniser tous les documents Android depuis une source unique
- `Amélioration` Renforcement de la validation de la documentation et exécution dans GitHub Actions, avec détection automatique des structures incohérentes entre langues, des fichiers générés désynchronisés, des artefacts orphelins, des versions non alignées et des marqueurs résiduels
- `Amélioration` Ajout de ROADMAP.md avec des listes de jalons vérifiables pour la documentation, l'ingénierie, les capacités de conversion et l'évolution de l'environnement d'exécution
- `Amélioration` Migration de la configuration Gradle vers `org.autojs.build.platform-versions` 1.4.1 et utilisation de foojay pour la résolution automatique du JDK, afin de simplifier et d'uniformiser l'environnement de compilation

##### Pour plus d'historique des versions

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/assets/doc/CHANGELOG-fr.md)

******

### Compilation et vérification

******

Cette section s'adresse aux développeurs souhaitant compiler le plugin depuis les sources; les utilisateurs ordinaires peuvent simplement installer les APK précompilés de la page Releases.

Compiler un APK debug:

```powershell
.\gradlew.bat :app:assembleDebug
```

Exécuter les tests unitaires JVM et compiler l'APK de test instrumentation:

```powershell
.\gradlew.bat :app:testDebugUnitTest :app:assembleDebugAndroidTest
```

Compiler les APK release:

```powershell
.\gradlew.bat :app:assembleRelease
```

Rassembler les artefacts de publication et ajouter la version, l'ABI et la somme de contrôle CRC32 au nom de chaque fichier:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

Compiler les APK release et préparer les sommes de contrôle et les notes de version:

```powershell
py scripts\release\prepare_release.py
```

Vérifier que les sources de la documentation multilingue et les fichiers générés sont synchronisés (également vérifié par l'intégration continue):

```powershell
py .python\generate_markdown.py --check
```

La compilation nécessite JDK 17 ou ultérieur ainsi que le SDK Android 36; les versions de Gradle et des plugins sont gérées de manière centralisée par `version.properties` et `io.github.supermonster003.autojs6-platform-versions`.

******

### Localisation et génération des documents

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

`.readme/android_strings.json` est la source unique des textes de l'interface autonome et des erreurs du service; les JSON de langue fournissent le README et le texte du centre de plugins. Modifiez toujours les sources JSON sous `.readme/` et `.changelog/`, puis relancez `py .python/generate_markdown.py`; les `strings.xml`, `plugin_instruction.md`, README et changelogs générés ne sont jamais modifiés à la main. `--check` vérifie les 47 fichiers générés.

******

### Licence

******

Le code du projet est distribué sous la [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE). La conversion du chinois repose directement sur [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0); les sources et licences intégrées d'OpenCC, Marisa Trie, Darts Clone et RapidJSON figurent dans les [mentions tierces](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md).

******

### Liens

******

- Documentation AutoJs6 OpenCC: https://docs.autojs6.com/#/opencc
- Projet AutoJs6: https://github.com/SuperMonster003/AutoJs6
- Projet officiel OpenCC: https://github.com/BYVoid/OpenCC
- Mentions tierces: https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md
