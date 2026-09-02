<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>単独でも AutoJs6 でも使えるオフライン OpenCC 中国語変換</p>

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

OpenCC は 1 つのインストールで, [OpenCC](https://github.com/BYVoid/OpenCC) ベースの中国語テキスト変換を 2 つの入口から利用できます. 完全オフラインの Android アプリとして直接起動するか, 同じ APK を AutoJs6 プラグインとして認識させてスクリプトのグローバルオブジェクト `opencc` を使用します. どちらも簡体字, 繁体字, 香港/台湾の字形, 日本語新字体をカバーします.

単独エディターと権限で保護された AutoJs6 Binder サービスは, 1 つの公式 OpenCC エンジン, 同じ固定辞書, キャッシュ, 変換タイプ, エラーモデルを共有します. アプリ単独では AutoJs6 は不要で, プラグインモードでは既存のスクリプト API を維持したまま変換エンジンをホストと独立して更新できます.

******

### 主な機能

******

- 1 つの APK を 2 通りに使用: ランチャーアイコンから AutoJs6 なしで画面変換を行うか, 同じインストールを AutoJs6 の `opencc` スクリプト API から利用できます.
- 14 種類の標準変換: OpenCC の簡体字と繁体字の変換, 香港/台湾の地域字形変換, 日本語新字体変換をカバーし, 台湾の常用語彙変換 (`软件` と `軟體` の相互変換など) にも対応します.
- 33 個のスクリプトメソッド: 汎用の `opencc.convert(text, type)` に加え, 各変換タイプに同名のショートカットメソッドがあり, さらに `s2jp` や `tw2hk` など 18 個のエイリアスと組み合わせメソッドを提供します.
- 完全オフライン: 変換はプラグイン内蔵の辞書により端末内で完結します. プラグインはネットワーク権限を要求せず, データも一切収集しません.
- 必要な分だけ選べるパッケージ: 4 種類の単一アーキテクチャ版と全アーキテクチャ入りの `universal` 版を提供し, 端末に合ったパッケージだけをインストールできるためサイズを抑えられます.
- 多言語対応: 単独 UI, プラグイン情報, 使用説明, README, 更新履歴が 10 言語をカバーします.
- 共有バックエンド: エディターと軽量プラグインサービスは同じ検証済みリソースとネイティブエンジンを再利用し, アイドル接続は自動的に解放されます.

******

### 画面スクリーンショット

******

未加工の Android 実行画面として, ライトテーマの単独エディター, 文字サイズ 170% のアラビア語 RTL ダークレイアウト, 既存の AutoJs6 プラグインセンター入口を示します.

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-phone-light.png?raw=true"
           alt="ライトテーマでの単独オフライン変換" width="280" />
      <br />
      <sub>ライトテーマでの単独オフライン変換</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-rtl-large-dark.png?raw=true"
           alt="ダークテーマ, 文字サイズ 170% のアラビア語 RTL レイアウト" width="280" />
      <br />
      <sub>ダークテーマ, 文字サイズ 170% のアラビア語 RTL レイアウト</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/plugin-center-enabled.png?raw=true"
           alt="プラグインセンターで認識され有効になった OpenCC 1.0.2" width="280" />
      <br />
      <sub>プラグインセンターで認識され有効になった OpenCC 1.0.2</sub>
    </td>
  </tr>
</table>

******

### 使用方法

******

1. [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) または AutoJs6 プラグインセンターから 1 つの APK をダウンロードしてインストールします. 端末の ABI に合う版を選び, 不明な場合は `universal` または下記の `インストールパッケージの選び方` を参照します.
2. 単独で使う場合はランチャーから `OpenCC` を開き, テキストを入力または明示的に貼り付け, 14 タイプから選んで `変換` を押します. AutoJs6 もプラグイン権限の付与も不要です.
3. プラグインとして使う場合は AutoJs6 を内部ビルド 3923 (6.7.1 Alpha4) 以上に更新します. リリース 6.8.0 以降は要件を満たします.
4. AutoJs6 プラグインセンターで `OpenCC` が認識され有効であることを確認します. 公式パッケージは署名検証を自動通過し, 手動承認は不要です.
5. スクリプトでグローバルオブジェクト `opencc` を直接使います. 例: `opencc.s2t("汉字")`; require, import, ホスト再起動は不要です.

> 両モードとも Android 7.0 (API 24) 以上に対応します. AutoJs6 の最小ビルド要件はプラグインスクリプトだけに適用され, 単独アプリはホストに依存しません. スクリプトで不足が表示された場合は `よくある質問` を参照してください.

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

拡張契約に対応する新しいホストは, 組み合わせチェーン全体を 1 回のプラグイン呼び出しで送ります. 例えば `twi2jp` の 3 変換ステージに必要な Binder 往復は 1 回だけです; 古いホストは各ステージを引き続き呼び出し, このプラグインとの互換性を維持します.

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

#### AutoJs6 をインストールせずに OpenCC を使える?

はい. ランチャーの `OpenCC` アイコンを開けば, オフラインエディターで変換できます. AutoJs6 が必要なのはスクリプトからグローバルオブジェクト `opencc` 経由で呼び出す場合だけで, 両モードは同じ APK に含まれます.

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

単独アプリと AutoJs6 プラグイン入口には分離された明確な境界があります:

- 最小権限: マニフェストは連携用の `org.autojs.permission.PLUGIN` だけを宣言し, ネットワーク, ストレージ, カメラなどの機微な権限はありません. 単独利用者がプラグイン権限を付与する必要もありません.
- 明示操作: Launcher は共有テキストや URI を受け付けず, `貼り付け` 後だけクリップボードを読み, `共有` 後だけシステム共有画面を開きます.
- 保護されたサービス: AutoJs6 など権限を持つホストだけがバインドして呼び出せます. AutoJs6 はパッケージ署名も検証し, 他のアプリはサービスを呼び出せません.
- ローカル処理: 両入口とも内蔵辞書で完全オフライン変換します. 入力と結果をログ, 永続化, バックアップ, 送信, 収集しません.

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
aidl contract version: 2
aidl methods: getInfo(), convert(text, conversionType), getSupportedConversionTypes(), convertBatch(texts, conversionType), convertChain(text, conversionTypes)
batch/chain limits: 1024 texts / 32 stages
minimum host build: 3923 (6.7.1 Alpha4)
conversion backend: OpenCC 1.4.2 (ver.1.4.2)
OpenCC source commit: 025f371dc76b598d77384fbdab90c937471844d8
OpenCC resources SHA-256: 9ea0d303219b34d014d5c116677b5d325043beafb2c8a62ee889ca67f4d054a5
```

`OpenccPluginService` は `org.autojs.plugin.OPENCC` アクション (カテゴリ `opencc`) に opencc-api の `org.autojs.plugin.opencc.api.IOpenccPlugin` で応答します. 契約バージョン 2 は既存の `getInfo()` と `convert(text, conversionType)` の後ろにタイプ検出, 一括変換, チェーン変換を追加し, `PluginInfo.capabilities` でバージョンと対応タイプを通知します; 古いホストは既存のメソッドとトランザクション番号をそのまま使用できます. ホストがプラグインプロセスを起動するための `WakeActivity` も提供します.

プラグインはコミット `025f371dc76b598d77384fbdab90c937471844d8` に固定した公式 OpenCC `ver.1.4.2` と同一リリースのリソースを直接ビルドします. 各 ABI には静的リンクされ 16 KB 境界に整列した `libopencc_jni.so` が 1 つだけ含まれ, 変換は常に完全オフラインです.

******

### 開発ロードマップ

******

プラグインの機能計画と進捗はチェック可能なリストとして ROADMAP.md で管理されています. マイルストーンごとに整理され受け入れ条件が付記されており, ドキュメントとリリース体験, エンジニアリングと継続的インテグレーション, 変換機能の強化, ランタイムの進化などの方向をカバーします. 未チェックの項目は計画上の意向であり現行バージョンの機能ではありません. Issues でのディスカッションを歓迎します.

- [ROADMAP.md を見る](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### リリース履歴

******

#### v1.3.0

_2026/09/03_

- `ヒント` 同じ APK を Android 7.0 以降で完全オフラインの単独アプリとしても, 従来の AutoJs6 プラグインとしても利用できるようになりました; AutoJs6 が必要なのはプラグイン経由の場合だけです
- `機能` ホーム画面の起動項目と, 14 種類すべての OpenCC 変換に対応する完全オフラインエディターを追加; 変換, キャンセル, クリア, 貼り付け, 入れ替え, コピー, 共有, 長文のバックグラウンド処理, 回転/プロセス再作成後の状態復元に対応
- `機能` ライト/ダークテーマ, RTL, 大きな文字, TalkBack のセマンティクスとフォーカス順, ハードウェアキーボードのショートカット, 個別にスクロール/選択できる編集領域, スマートフォン/タブレット/分割画面のレスポンシブレイアウトを備えた 10 言語の単独 UI を追加
- `改善` 単独アプリと Binder の両入口でプロセス共通の公式 OpenCC バックエンドを使用し, applicationId, 署名 ID, プラグインの権限境界, AIDL トランザクション番号, オフライン/履歴なしの既定値を維持
- `改善` 検証範囲を minSdk 24, 32 ビット ARM, arm64, x86, x86_64, 実際の 16 KB ページ環境へ拡大; 最終 APK の locale, manifest, R8, ELF, ZIP 属性を監査し, 再現可能な未編集 UI スクリーンショットを固定
- `改善` v1.2.0 からの上書き更新でパッケージ UID とプラグインサービスを保持したまま Launcher が 1 つだけ追加されることを確認し, 署名済み minified release 上で UI 変換と旧式の生 Binder 変換を実行

#### v1.2.0

_2026/09/01_

- `ヒント` OpenCC 1.4.2 の辞書更新により, `复盘` -> `復盤`, `内卷` -> `內捲`, `什么怎么这么` の保持, `内存条` -> `記憶體模組` など少数の結果が意図的に変わります. 全レビュー一覧は移行レポートに記録しています
- `改善` 公式 OpenCC 1.4.2 と同一リリースの辞書を ABI ごとに 1 つの静的リンク JNI ライブラリへ直接ビルドし, すべての変換を完全オフラインに維持
- `改善` NDK 28.2, 16 KB の ELF および ZIP アラインメント, 実際の 16 KB エミュレーターでの Binder 検証により 16 KB ページサイズ端末に対応
- `改善` 固定されたリソース ZIP をサイズと SHA-256 の検証付きでアトミックにインストールし, 破損時の自動復旧, Unicode 安全な JNI 変換, ホットパスのコンバーターキャッシュを実装
- `依存関係` 保守されていない `com.github.brooklet:android-opencc:1.2.2` ラッパーを削除し, 公式 OpenCC `ver.1.4.2` をコミット `025f371dc76b598d77384fbdab90c937471844d8` に固定
- `依存関係` 同梱する OpenCC, Marisa Trie, Darts Clone, RapidJSON の出典とライセンスを `THIRD_PARTY_NOTICES.md` に記載

#### v1.1.0

_2026/09/01_

- `機能` OpenCC プラグイン契約をバージョン 2 に更新し, `getSupportedConversionTypes()` を追加しました. 新しいホストはプラグインが実際に対応する 14 種類の変換タイプを動的に検出できます
- `機能` `convertBatch(texts, conversionType)` を追加し, 1 回の Binder 往復で最大 1024 個のテキストを変換できるようにしました. 古いホスト向けの項目別呼び出しも維持します
- `機能` `convertChain(text, conversionTypes)` を追加し, 1 回の呼び出しで最大 32 ステージを順に実行できるようにしました. 新しいホストの組み合わせメソッドは最大 3 回の Binder 往復から 1 回に減ります
- `改善` `PluginInfo.instruction` で呼び出し側の言語に合った説明を提供し, capabilities で契約バージョンと対応変換タイプを報告します
- `改善` 既存の AIDL メソッドとトランザクション番号を維持し, 拡張呼び出し, 旧契約へのフォールバック, サイズ上限, エラー経路を単体テストと実 Binder テストで検証します
- `改善` README のレイアウトと Gradle プラットフォームのバージョン管理方式を統一

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

JVM 単体テストを実行し instrumentation テスト APK をビルド:

```powershell
.\gradlew.bat :app:testDebugUnitTest :app:assembleDebugAndroidTest
```

release APK をビルド:

```powershell
.\gradlew.bat :app:assembleRelease
```

リリース成果物を収集し, ファイル名にバージョン, ABI, CRC32 チェックサムを付加:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

release APK をビルドし, チェックサムとリリースノートを準備:

```powershell
py scripts\release\prepare_release.py
```

多言語ドキュメントのソースと生成物が同期しているかを検証 (CI でも実行されます):

```powershell
py .python\generate_markdown.py --check
```

ビルドには JDK 17 以上と Android SDK 36 が必要です; Gradle と各プラグインのバージョンは `version.properties` と `io.github.supermonster003.autojs6-platform-versions` によって一元管理されます.

******

### ローカライズとドキュメント生成

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

`.readme/android_strings.json` が単独 UI とサービスエラー文字列の唯一のソースで, 言語 JSON が README とプラグインセンター文を提供します. `.readme/` と `.changelog/` の JSON を編集して `py .python/generate_markdown.py` を再実行し, 生成された `strings.xml`, `plugin_instruction.md`, README, 更新履歴は手で編集しません. `--check` は 47 生成物を検証します.

******

### ライセンス

******

プロジェクトのコードは [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE) でライセンスされています. 中国語変換には [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0) を直接使用し, 同梱する OpenCC, Marisa Trie, Darts Clone, RapidJSON の出典とライセンスは[サードパーティー通知](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md)に記載しています.

******

### リンク

******

- AutoJs6 OpenCC ドキュメント: https://docs.autojs6.com/#/opencc
- AutoJs6 プロジェクト: https://github.com/SuperMonster003/AutoJs6
- OpenCC 公式プロジェクト: https://github.com/BYVoid/OpenCC
- サードパーティー通知: https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md
