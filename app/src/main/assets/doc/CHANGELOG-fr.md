******

### Historique des versions

******

# v1.1.0

###### 2026/08/31

* `Fonctionnalité` Passage au contrat de plugin OpenCC version 2 avec `getSupportedConversionTypes()`, afin que les hôtes récents découvrent les 14 types de conversion réellement pris en charge
* `Fonctionnalité` Ajout de `convertBatch(texts, conversionType)` pour convertir jusqu'à 1024 segments de texte en un seul aller-retour Binder, tout en conservant le traitement élément par élément pour les anciens hôtes
* `Fonctionnalité` Ajout de `convertChain(text, conversionTypes)` pour exécuter jusqu'à 32 étapes en un seul appel, ce qui réduit les méthodes composées des hôtes récents de 3 allers-retours Binder au maximum à 1
* `Amélioration` Transmission des instructions localisées via `PluginInfo.instruction` et publication de la version du contrat et des types de conversion pris en charge dans les capabilities
* `Amélioration` Conservation des méthodes AIDL et numéros de transaction d'origine, avec des tests unitaires et Binder réels couvrant les appels étendus, le repli hérité, les limites de taille et les erreurs

# v1.0.2

###### 2026/08/31

* `Note` Cette version améliore uniquement la documentation et le processus de compilation; le comportement de conversion OpenCC et les 14 types de conversion principaux restent inchangés
* `Amélioration` Refonte du README dans les 10 langues avec les étapes d'installation, un guide de sélection des paquets, une vérification rapide, la liste complète des 33 méthodes de script, une FAQ et des précisions sur les permissions et la sécurité
* `Amélioration` Génération des instructions du centre de plugins depuis la même source JSON localisée que le README et le CHANGELOG, afin de synchroniser tous les documents Android depuis une source unique
* `Amélioration` Renforcement de la validation de la documentation et exécution dans GitHub Actions, avec détection automatique des structures incohérentes entre langues, des fichiers générés désynchronisés, des artefacts orphelins, des versions non alignées et des marqueurs résiduels
* `Amélioration` Ajout de ROADMAP.md avec des listes de jalons vérifiables pour la documentation, l'ingénierie, les capacités de conversion et l'évolution de l'environnement d'exécution
* `Amélioration` Migration de la configuration Gradle vers `org.autojs.build.platform-versions` 1.4.1 et utilisation de foojay pour la résolution automatique du JDK, afin de simplifier et d'uniformiser l'environnement de compilation

# v1.0.1

###### 2026/07/14

* `Amélioration` Distribution de paquets séparés par architecture de processeur (ABI): paquets à ABI unique pour `arm64-v8a`, `armeabi-v7a`, `x86_64` et `x86`, plus un paquet `universal` regroupant toutes les architectures, afin que chaque appareil n'installe que le nécessaire et que les téléchargements restent légers
* `Amélioration` Signalement de la liste des ABI prises en charge dans les informations du plugin, afin qu'AutoJs6 et le centre de plugins puissent identifier les variantes du plugin adaptées à l'appareil actuel
* `Amélioration` Ajout de la version, de l'ABI et de la somme de contrôle CRC32 aux noms des fichiers APK publiés, ce qui facilite la vérification de l'intégrité des fichiers téléchargés

# v1.0.0

###### 2026/07/14

* `Fonctionnalité` Première version stable: fournit à AutoJs6 la conversion de chinois OpenCC sous forme de plugin autonome, l'ID du plugin et le moteur étant tous deux `opencc`
* `Fonctionnalité` Découverte et appel automatiques du plugin par AutoJs6 via `org.autojs.plugin.OPENCC`; il fonctionne dès l'installation, sans configuration ni redémarrage
* `Fonctionnalité` Prise en charge des 14 types de conversion standard OpenCC, couvrant la conversion simplifié-traditionnel, les variantes de Hong Kong et de Taïwan ainsi que le shinjitai japonais: `S2T`/`S2TW`/`S2TWP`/`S2HK`/`T2S`/`T2TW`/`T2HK`/`T2JP`/`TW2S`/`TW2T`/`TW2SP`/`HK2S`/`HK2T`/`JP2T`
* `Fonctionnalité` Métadonnées du plugin et instructions d'utilisation localisées en 10 langues: chinois simplifié, chinois traditionnel de Hong Kong, chinois traditionnel de Taïwan, anglais, français, espagnol, japonais, coréen, russe et arabe
* `Fonctionnalité` README multilingue avec des exemples d'utilisation, des instructions de compilation et des liens associés
