<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>中国語テキスト変換用 OpenCC プラグイン</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-OpenCC?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-OpenCC?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-OpenCC?color=534BAE&label=License"/></a>
  </p>
</div>

******

### 言語 (Languages)

******

現在の README.md は次の言語に対応しています:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-es.md)
- 日本語 [ja] # 現在
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ar.md)

******

### 概要

******

OpenCC プラグイン (OpenCC Plugin) は, [OpenCC](https://github.com/BYVoid/OpenCC) ベースの中国語テキスト変換機能を AutoJs6 に提供します. 本プラグインをインストールすると, AutoJs6 スクリプトのグローバルオブジェクト `opencc` がそのまま利用可能になり, 簡体字, 繁体字, 香港繁体字, 台湾正体字, 日本語新字体の間の変換が 1 行のコードで完結します. モジュールのインポートもネットワーク接続も不要です.

プラグインはホストとプラグインの分業設計を採用しています: AutoJs6 ホストはスクリプトが直接呼び出す `opencc` API を提供し, プラグインは OpenCC 変換エンジンと辞書を独立したアプリとして同梱します. AutoJs6 6.8.0 以降, ホストは OpenCC ランタイムを内蔵せず, 中国語変換機能は本プラグインが必要に応じて提供します; これによりホストのインストールパッケージは軽量に保たれ, 変換エンジンをホストとは独立して更新できます.

******

### 主な機能

******

- すぐに使える: 端末にインストールするだけで AutoJs6 が自動的にプラグインを検出します. ホストの再起動も設定も不要で, スクリプトからすぐにグローバルオブジェクト `opencc` を呼び出せます.
- 14 種類の標準変換: OpenCC の簡体字と繁体字の変換, 香港/台湾の地域字形変換, 日本語新字体変換をカバーし, 台湾の常用語彙変換 (`软件` と `軟體` の相互変換など) にも対応します.
- 33 個のスクリプトメソッド: 汎用の `opencc.convert(text, type)` に加え, 各変換タイプに同名のショートカットメソッドがあり, さらに `s2jp` や `tw2hk` など 18 個のエイリアスと組み合わせメソッドを提供します.
- 完全オフライン: 変換はプラグイン内蔵の辞書により端末内で完結します. プラグインはネットワーク権限を要求せず, データも一切収集しません.
- 必要な分だけ選べるパッケージ: 4 種類の単一アーキテクチャ版と全アーキテクチャ入りの `universal` 版を提供し, 端末に合ったパッケージだけをインストールできるためサイズを抑えられます.
- 多言語対応: プラグイン情報, 使用説明, README, 更新履歴が 10 言語をカバーします.
- 軽量なバックグラウンド動作: プラグインは独自の画面を持たず, ホストが必要時にウェイクアップとバインドを行い, アイドル時は接続が自動的に解放されます.

******

### 使用方法

******

1. AutoJs6 を内部ビルド番号 3923 (6.7.1 Alpha4) 以上に更新します; リリース版 6.8.0 以降はすべて要件を満たします.
2. [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) ページまたは AutoJs6 のプラグインセンターからプラグイン APK をダウンロードしてインストールします; どのパッケージを選ぶか迷ったら `universal` 版を選ぶか, 下記の `インストールパッケージの選び方` を参照してください.
3. AutoJs6 のプラグインセンターを開き, `OpenCC` プラグインが認識され有効になっていることを確認します; 公式リリースパッケージは署名検証を自動的に通過するため, 手動での承認は不要です.
4. スクリプト内でグローバルオブジェクト `opencc` を直接使います. 例: `opencc.s2t("汉字")`; require や import は不要で, プラグインのインストール後に AutoJs6 を再起動する必要もありません.

> プラグインは Android 7.0 (API 24) 以上の端末に対応しています. スクリプト実行時にプラグインの欠落やホストのバージョン不足が表示された場合は, 下記の `よくある質問` を参照してください.

******

### クイックスタート

******

インストール後, 以下のスクリプトはそのまま実行できます. コメントは期待される出力です:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.t2jp("圖書館"));      // => 図書館
```

ショートカットメソッドは汎用メソッド `opencc.convert(text, type)` と等価です; `opencc` オブジェクト自体も関数として呼び出せ, 変換タイプ名は大文字と小文字を区別しません:

```javascript
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
console.log(opencc("汉字转换", "s2t"));         // => 漢字轉換
```

すべてのメソッドは変換後の文字列を同期的に返します. 変換はローカル辞書上で行われ, ネットワークリクエストは一切発生しません.

******

### 変換タイプ

******

`convert` メソッドと同名のショートカットは以下の 14 種類の OpenCC 標準変換タイプに対応しています. タイプ名の S は簡体字, T は繁体字 (OpenCC 標準), HK は香港繁体字, TW は台湾正体字, JP は日本語新字体を表します:

| タイプ | 変換方向 |
|---|---|
| `S2T` | 簡体字から繁体字へ |
| `T2S` | 繁体字から簡体字へ |
| `S2TW` | 簡体字から台湾正体字へ |
| `TW2S` | 台湾正体字から簡体字へ |
| `S2TWP` | 簡体字から台湾正体字へ, 台湾の常用語彙への置換も実施 (`内存` が `記憶體` になるなど) |
| `TW2SP` | 台湾正体字から簡体字へ, 大陸の常用語彙への置換も実施 (`滑鼠` が `鼠标` になるなど) |
| `S2HK` | 簡体字から香港繁体字へ |
| `HK2S` | 香港繁体字から簡体字へ |
| `T2TW` | 繁体字から台湾正体字へ |
| `TW2T` | 台湾正体字から繁体字へ |
| `T2HK` | 繁体字から香港繁体字へ |
| `HK2T` | 香港繁体字から繁体字へ |
| `T2JP` | 繁体字 (旧字体) から日本語新字体へ |
| `JP2T` | 日本語新字体から繁体字 (旧字体) へ |

`P` サフィックス付きのタイプは, 文字単位の変換に加えて語彙の置換も行い, 現地の表現習慣により適した結果を生成します; `P` なしのタイプは字形のみを変換し, 語彙には手を加えません.

`T2JP` と `JP2T` は繁体字の旧字体と日本語新字体 (Shinjitai) の間で変換します. 例えば `圖書館` と `図書館` のような漢字の字形差を扱うものであり, 中国語と日本語の間の翻訳ではありません.

******

### スクリプトメソッド

******

ホスト側のグローバルオブジェクト `opencc` は合計 33 個のメソッドを提供します: 汎用メソッド `convert`, 14 個のコアショートカット, そして 18 個のエイリアスと組み合わせメソッドです. `convert(text, type)` の `type` 引数は 32 個すべての変換名 (コアと組み合わせの両方) を大文字小文字の区別なく受け付けます; 未知のタイプを渡すと `Unknown OpenCC conversion type` エラーがスローされます.

14 個のコアショートカットは上表の変換タイプと 1 対 1 に対応し, 1 回の呼び出しで 1 回のプラグイン変換を実行します:

```text
s2t   t2s   s2tw  tw2s  s2twp  tw2sp  s2hk
hk2s  t2tw  tw2t  t2hk  hk2t   t2jp   jp2t
```

`s2twi` と `twi2s` はそれぞれ `s2twp` と `tw2sp` のエイリアスで (`twi` は Taiwan idiom, つまり台湾の常用語彙を表します), 動作は完全に同じです.

残りの 16 個の組み合わせメソッドは複数のコア変換を順に連結したもので, 直通辞書のない変換方向をカバーします:

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

組み合わせメソッドの各ステップは独立したプラグイン呼び出しです. 例えば `twi2jp` は 3 回の変換を順に実行します; 高頻度ループや非常に長いテキストでは, コアタイプを優先すると呼び出し回数を減らせます.

******

### インストールパッケージの選び方

******

各リリースには 5 つの APK が含まれ, 違いは内蔵される OpenCC ネイティブライブラリのプロセッサアーキテクチャ (ABI) だけです:

| パッケージ | 対象 |
|---|---|
| `arm64-v8a` | 最近の Android スマートフォンとタブレットの大多数 (64 ビット ARM). 最優先の選択肢 |
| `armeabi-v7a` | やや古い 32 ビット ARM 端末 |
| `x86_64` | 64 ビット x86 エミュレータと少数の x86 端末 |
| `x86` | 32 ビット x86 エミュレータと少数の x86 端末 |
| `universal` | 全 4 アーキテクチャを内蔵しサイズは最大; あらゆる端末で動作し, 迷ったときの確実な選択肢 |

端末のアーキテクチャと一致しない単一アーキテクチャ版を誤ってインストールすると, プラグインは変換サービスを提供できません. `universal` 版に入れ替えれば解決します.

******

### クイックセルフチェック

******

プラグインがインストールされ, プラグインセンターで有効になっていることを確認したら, 以下の 1 行スクリプトを実行するとエンドツーエンドの検証ができます:

```javascript
console.log(opencc.s2t("汉字转换"));
```

`漢字轉換` が出力されればプラグインの連携は完全に機能しています. スクリプトがエラーになった場合はメッセージに従って対処してください: プラグインの欠落と表示されたら本プラグインをインストールし, 無効または未承認と表示されたらプラグインセンターで該当スイッチをオンにし, より新しいホストが必要と表示されたら AutoJs6 を更新します.

******

### よくある質問

******

#### プラグインが有効になったことを確認するには?

AutoJs6 のプラグインセンターを開き, `OpenCC` プラグインが表示され有効になっていればホストに認識されています; 続けて上記の `クイックセルフチェック` スクリプトを実行し, `漢字轉換` が出力されれば動作しています.

#### アプリ一覧にプラグインのアイコンがないのはなぜ?

これは正常な動作です. プラグインは独自の画面を持たず, ランチャーアイコンも作成しません. インストール後は AutoJs6 がバックグラウンドで自動的に検出して呼び出し, すべての操作は AutoJs6 内で完結します.

#### スクリプトで `"OpenCC plugin" に必要なプラグインがありません` と表示されたら?

AutoJs6 が端末上で本プラグインを見つけられなかったことを意味します. プラグインをインストールしてからスクリプトを再実行してください. AutoJs6 の再起動は不要です; インストール済みでも表示が消えない場合は, システムやセキュリティアプリによってアンインストールされていないかを確認し, プラグインセンターの有効化と承認の状態も確認してください.

#### `s2tw` と `s2twp` (`s2twi`) の違いは?

`s2tw` は字形のみを変換し (`软` が `軟` になるなど), 語彙には手を加えません; `s2twp` はさらに大陸の語彙を台湾の常用語彙に置換します (`软件` が `軟體` に, `鼠标` が `滑鼠` になるなど). `s2twi` はそのエイリアスです. 台湾の読者向けの正式なテキストには通常 `s2twp` を, 字形の統一だけが必要な場合は `s2tw` を選びます.

#### Node.js エンジンのスクリプトで `opencc` が使えないのはなぜ?

`opencc` は現在 Rhino (AutoJs6 の既定 JavaScript エンジン) 専用のグローバルオブジェクトで, Node.js ランタイムには対応する実装がまだありません. 関連する対応計画は [ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md) を参照してください.

#### 変換にネットワーク接続は必要? 長いテキストは遅くならない?

ネットワークは不要です. すべての変換はプラグインに内蔵された OpenCC 辞書によりローカルで行われます. メソッド呼び出し 1 回がプロセス間通信 1 往復に対応し, 長めのテキストでも通常は 1 往復で変換できます; 高頻度のループ呼び出しでは, 組み合わせメソッドによる複数往復を避けるためコアタイプの使用を推奨します.

#### プラグインはどの権限を要求する? データは安全?

プラグインは AutoJs6 との通信に使うプラグイン権限のみを宣言し, ネットワークやストレージなどの機微なシステム権限は一切要求しません; サービス自体も同じ権限で保護されており, 他のアプリからは呼び出せません. 変換対象のテキストは端末のメモリ内でのみ処理され, 保存もアップロードもされません.

******

### 権限とセキュリティ

******

プラグインと AutoJs6 は Android の権限機構と署名機構によって信頼関係を確立します:

- 最小権限: マニフェストにはプラグイン権限 `org.autojs.permission.PLUGIN` のみを宣言し, ネットワーク, ストレージ, カメラなどの機微なシステム権限は含まれません.
- 双方向の保護: プラグインサービスも同じ権限で保護されており, プラグイン権限を持つホスト (AutoJs6 など) だけがバインドと呼び出しを行えます. 他のアプリはアクセスできません.
- 署名による承認: AutoJs6 はプラグインの署名を検証します. 公式リリースパッケージは自動的に承認され, それ以外の署名のビルドはプラグインセンターで手動承認しない限りロードされません.
- ローカル処理: 変換は完全に端末内で行われます. プラグインはネットワークに接続せず, ディスクにも書き込まず, ユーザーデータを一切収集しません.

プラグインは公式の [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) ページまたは AutoJs6 プラグインセンターからのみ入手してください. 出所不明のパッケージは, バージョン番号が同じに見えてもホストの検証を通過できなかったり, リスクを含んでいたりする可能性があります.

******

### プラグインインターフェース

******

以下の情報は AutoJs6 ホストとプラグインの開発者向けです. ホストはこれらの識別子でプラグインを発見し, 互換性ネゴシエーションを行います:

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

`OpenccPluginService` は `org.autojs.plugin.OPENCC` アクション (カテゴリ `opencc`) に応答します. Binder インターフェースは opencc-api の `org.autojs.plugin.opencc.api.IOpenccPlugin` で, メソッドは `getInfo()` と `convert(text, conversionType)` の 2 つだけです; また, ホストがプラグインプロセスを起動するための `WakeActivity` も提供します.

`PluginInfo.supportedAbis` は `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` の 4 アーキテクチャを報告し, ホストとプラグインセンターが利用可能なバリアントを識別できるようにします; 変換は `com.github.brooklet:android-opencc:1.2.2` が提供する OpenCC エンジンと辞書によって行われます.

******

### 開発ロードマップ

******

プラグインの機能計画と進捗はチェック可能なリストとして ROADMAP.md で管理されています. マイルストーンごとに整理され受け入れ条件が付記されており, ドキュメントとリリース体験, エンジニアリングと継続的インテグレーション, 変換機能の強化, ランタイムの進化などの方向をカバーします. 未チェックの項目は計画上の意向であり現行バージョンの機能ではありません. Issues でのディスカッションを歓迎します.

- [ROADMAP.md を見る](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### リリース履歴

******

#### v1.0.2

_2026/08/31_

- `ヒント` このバージョンはドキュメントとビルド工程のみを改善します. OpenCC の変換動作と 14 種類のコア変換タイプに変更はありません
- `改善` 10 言語の README を再構成し, インストール手順, パッケージ選択ガイド, クイック自己診断, 33 個のスクリプトメソッド一覧, FAQ, 権限とセキュリティの説明を追加しました
- `改善` プラグインセンターの使用説明を README と CHANGELOG と同じ多言語 JSON ソースから生成し, Android の全ドキュメント成果物を単一ソースから同期できるようにしました
- `改善` ドキュメント検証を強化して GitHub Actions に統合し, 言語間の構造不一致, 生成ファイルのずれ, 孤立した成果物, バージョン不一致, 残存プレースホルダーを自動検出します
- `改善` ROADMAP.md を追加し, ドキュメント, エンジニアリング, 変換機能, ランタイム進化の計画を検証可能なマイルストーン一覧で公開しました
- `改善` Gradle 設定を `org.autojs.build.platform-versions` 1.4.1 に移行し, foojay による JDK の自動解決を導入してビルド環境を簡素化し統一しました

#### v1.0.1

_2026/07/14_

- `改善` プロセッサアーキテクチャ (ABI) 別に分割したインストールパッケージを提供: `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` の単一アーキテクチャ版と全アーキテクチャ入りの `universal` 版により, 端末は必要な分だけをインストールでき, ダウンロードサイズも小さくなります
- `改善` プラグイン情報でサポート対象の ABI リストを報告し, AutoJs6 とプラグインセンターが現在の端末で利用可能なプラグインバリアントを識別できるようになりました
- `改善` リリース APK のファイル名にバージョン, ABI, CRC32 チェックサムを付加し, ダウンロードしたファイルの完全性を確認しやすくしました

#### v1.0.0

_2026/07/14_

- `機能` 初の正式リリース: 独立したプラグインとして AutoJs6 に OpenCC 中国語変換機能を提供します. プラグイン ID とエンジンはともに `opencc` です
- `機能` AutoJs6 は `org.autojs.plugin.OPENCC` を通じてプラグインを自動的に発見して呼び出します. インストールするだけで動作し, 設定も再起動も不要です
- `機能` OpenCC の標準変換タイプ全 14 種類に対応し, 簡体字と繁体字の変換, 香港/台湾の地域字形, 日本語新字体をカバーします: `S2T`/`S2TW`/`S2TWP`/`S2HK`/`T2S`/`T2TW`/`T2HK`/`T2JP`/`TW2S`/`TW2T`/`TW2SP`/`HK2S`/`HK2T`/`JP2T`
- `機能` プラグイン情報と使用説明を 10 言語でローカライズ: 簡体字中国語, 香港繁体字, 台湾正体字, 英語, フランス語, スペイン語, 日本語, 韓国語, ロシア語, アラビア語
- `機能` 使用例, ビルド手順, 関連リンクを含む多言語 README を提供します

##### その他のリリース履歴

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/assets/doc/CHANGELOG-ja.md)

******

### ビルドと検証

******

このセクションはソースからプラグインをビルドしたい開発者向けです; 一般ユーザーは Releases ページのビルド済み APK をそのままインストールすれば十分です.

debug APK をビルド:

```powershell
.\gradlew.bat :app:assembleDebug
```

release APK をビルド; バージョン管理対象外の `sign.properties` に署名情報を設定すると自動的に署名されます. 未署名の成果物は公開できません:

```powershell
.\gradlew.bat :app:assembleRelease
```

リリース成果物を収集し, ファイル名にバージョン, ABI, CRC32 チェックサムを付加:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

多言語ドキュメントのソースと生成物が同期しているかを検証 (CI でも実行されます):

```powershell
py .python\generate_markdown.py --check
```

ビルドには JDK 17 以上と Android SDK 36 が必要です; Gradle と各プラグインのバージョンは `version.properties` と `org.autojs.build.platform-versions` によって一元管理されます.

******

### ローカライズとドキュメント生成

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

`strings.xml` はローカライズされたプラグイン説明とエラーメッセージを, `plugin_instruction.md` はホストのプラグインセンター内に表示される使用説明を提供します. README と更新履歴は必ず `.readme/` と `.changelog/` 配下の JSON ソースを編集してから `py .python/generate_markdown.py` を実行して再生成します. 生成物を手で編集することはありません; `py .python/generate_markdown.py --check` を実行すると, ソースと生成物が同期しているかを検証できます.

******

### ライセンス

******

プロジェクトのコードは [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE) でライセンスされています. 中国語変換機能は [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0) とその Android ラッパー [android-opencc](https://github.com/qichuan/android-opencc) によって提供されます.

******

### リンク

******

- AutoJs6 OpenCC ドキュメント: https://docs.autojs6.com/#/opencc
- AutoJs6 プロジェクト: https://github.com/SuperMonster003/AutoJs6
- OpenCC 公式プロジェクト: https://github.com/BYVoid/OpenCC
- Android OpenCC プロジェクト: https://github.com/qichuan/android-opencc
