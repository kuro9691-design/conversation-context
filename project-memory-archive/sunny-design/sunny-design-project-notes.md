# sunny-design.jp 施工事例CPT移行プロジェクト 技術ノート

> 復旧版。2026-10-25の作業開始時点で、本来このパスにあるはずの旧ノートは不在だった。  
> 下記は、ユーザー提供のClaude引き継ぎ、`_PROGRESS_20261023.md`、および2026-10-25のWordPress実機監査から再構成した事実である。

**最終更新：2026-10-27（Codex）**

## 絶対条件

- 本番トップ `https://sunny-design.jp/`（固定ページID 864）は無変更。
- 本番メインヘッダー（ElementorテンプレートID 721）は無変更。
- 削除、slug変更、リダイレクト、本番反映はMANABUの実行前承認が必要。
- 設定値は推測せず実測し、保存後はforce reloadして再実測する。
- 作業の区切りごとに本ノートを更新する。

## 2026-10-25 実機監査結果

### 投稿・CPT

- `sunny_works`：公開13件（ID 9507〜9519）。公開URLは現在 `/sunny_works/{slug}/`。
- `general_works`：公開3件（ID 9831, 9837, 9836）。公開URLは現在 `/general_works/{slug}/`。
- 両CPTとも `has_archive = true`、`rewrite = true`、`rewrite_slug` は空欄、`rewrite_withfront = true`。
- 両CPTのREST型情報で、共有タクソノミーは `structure / building_type / taste`。
- 固定ページID 646（`/works/`）は公開中。
- 固定ページID 9789（`/top-page/`）は公開・パスワード保護中。
- 本番トップは固定ページID 864。実機body classで `page-id-864` を確認。

### ACF

- フィールドグループ「施工事例 詳細情報」（ID 9498）は有効、REST表示も有効。
- ロケーションルールは OR 条件で `sunny_works` と `general_works` の両方。
- 実機確認した11フィールド：
  - `catch_copy_ja`
  - `feature_tags_ja`
  - `feature_tags_en`
  - `site_area`
  - `completion_year`
  - `video_url`
  - `credit_line`
  - `thumbnail_1`
  - `thumbnail_2`
  - `credit_line_en`
  - `location`

### Elementorテンプレート

- ID 9546：`sunny_works Single Template v5`、Single Post、公開済み。Instancesは「施工事例」「一般建築」。
- v7という名称のSingleテンプレートは、全36件のテンプレート一覧には存在しなかった。現行はv5。
- ID 9697：`sunny_works Archive`、Archive、公開済み。Instancesは「施工事例 archive」「一般建築 archive」。
- ID 9738：`sunny_works Loop Card – NEXT WORKS`、Loop Item、公開済み。
- ID 9793：`sunny_works Loop Card – HOME`、Loop Item、公開済み。
- ID 9662：`TEST_ヘッダー（施工事例のみ・メニュー配色変更）`、Header、公開済み。Instancesは「施工事例」「一般建築」。
- ID 9667：`TEST_ポップアップメニュー（施工事例のみ・seek仕様）`、Popup、公開済み。Instancesは「施工事例」「一般建築」。
- ID 721：`SUNNY 2 Header`、Header、公開済み。InstancesはEntire site。
- 公開HTMLの `data-elementor-id` でも、両CPTのSingleに9546、両CPTのArchiveに9697が適用されていることを確認。

### Code Snippets

- ID 5「NEXT WORKS」は有効（PHP）。
- `elementor/query/next_works`：住宅ID 9507〜9519固定。現在の投稿IDが配列内なら次の3件へ循環し、`post_type = sunny_works`。
- `elementor/query/home_works`：住宅ID 9507〜9519固定順、`post_type = sunny_works`、6件表示。
- ID 6「施工事例：用途タクソノミー登録」は無効。`usage_type` 登録停止方針と一致。
- ID 8「一時：デバッグ表示ON(kurokui_adminのみ)」は有効。ただし `?debugme` がある管理者アクセス時のみ `display_errors` を有効にするコード。

### トップページ一般建築スライダー（2026-10-27）

- 対象はパスワード保護中の確認用トップページID 9789（`/top-page/`）。本番トップID 864は無変更。
- 一般建築のLoop Grid要素IDは `a2d657f`。テンプレートはID 9793、取得元は `general_works`、Query IDは `home_general_works`、Items Per Pageは4。
- Elementor Proライセンス未接続のため、新規Loop Carousel追加は「接続して有効化」でブロックされた。既存Loop Gridをページ内HTMLウィジェットのCSS/JavaScriptで横スライダー化した。
- 仕様：1件表示、4.5秒自動送り、遷移0.8秒、無限ループ、左右ボタン、ホバー／フォーカス中は停止。PC実測で1件1010px、スマホ実測で表示幅・カード幅とも345px、操作ボタン38px。
- 2026-10-27時点の公開3件に先頭クローン1件を加え、DOM上は4件。4件目の一般建築が公開されればクエリに自動追加される。
- 共有Loop Item内の画像リンクが住宅「坂の上の船」に固定されていたため、このトップページのスライダー内だけREST APIから各 `general_works` の個別URLを取得して補正する。実測済みURLは村山歯科 `murayama-dental-clinic`、玖珂 `kuga-clinic`、ひろち `hirochi-dental-clinic`。

### 確認用トップページ住宅スライダー（Elementor未保存、2026-10-27）

- 対象はパスワード保護中の確認用トップページID 9789。本番トップID 864は無変更。
- 表示順は「WORKS / 住宅 → 上段4件固定表示 → VIEW MORE → 下段の住宅全件スライダー → Works / 一般建築」。
- 上段Loop Gridは要素ID `9814965`。クエリフックが6件を返すため、5件目以降をページ内CSSで非表示にして4件表示とする。
- 下段スライダーは複製Loop Gridの要素ID `c4f29d9`。公開中の住宅全13件を表示し、各物件のACFサムネイル2枚を1組として扱う。
- 下段はSEEK FREE PLANNINGの施工事例スライダーを参考に、キャッチコピー・和英説明を非表示とし、横1：縦1.618の黄金比にトリミングした写真を等間隔で並べる。PCでは写真6枚が横一列に見える。写真にマウスオン／キーボードフォーカスすると、半透明の物件名帯が下から表示される。
- レスポンシブ表示はPC 3組、タブレット2組、スマホ1組。1回に1組ずつ左へ移動し、4.5秒自動送り、遷移0.8秒、左右ボタン、ホバー／フォーカス中は停止する。
- 左右ボタンは写真列の両端中央へ重ね、下部に全13件分の位置表示ドットを置く。
- DOMクローンはElementor側で削除されるため使わず、移動完了後に先頭カードを末尾へ並べ替える方式でループ化した。全13件を一巡すると表示順とドットが先頭へ戻る。
- `VIEW MORE` の直下へ表示するため、ページ読込後に住宅スライダー要素をVIEW MOREボタンと同じ内側コンテナの末尾へ移動する。
- PC幅1366pxで、スライダー幅1197.89px、1組幅399.30px、同時表示3組、1操作で先頭物件が1件進むことを確認した。
- 同PC幅で各写真は約184.64×298.77px、実測縦横比1.61809、1物件内の写真2枚、完全表示3組（写真6枚）、位置表示13個、左右ボタン2個を確認した。物件名帯は通常時に写真下へ隠れ、ホバー／フォーカス時に0.4秒でせり上がる。
- 既存の `elementor/query/home_works` は6件表示のまま変更していない。下段スライダーだけページ内JavaScriptからREST APIで住宅ID 9507〜9519とACF `thumbnail_1` / `thumbnail_2`、添付画像URLを読み込み、既存の固定順（9507→9519）で13カードを生成する。本番トップや上段4件への影響を避ける構成。
- 参考元SEEKのElementor Loop Carouselは、1物件＝1枚、PC 5枚、タブレット2枚、スマホ2枚、15px間隔、1枚ずつ移動、2秒自動送り、3秒遷移、無限ループ、矢印・ドット付き。カードは背景画像 `cover` で、約228.59×292px。タイトル帯は通常 `translateY(66.19px)` で隠れ、PCホバー時に下から表示される。ホバー不可端末では写真のみのままリンクする。
- 住宅2つのLoop Gridと一般建築Loop Gridのリンクは、REST APIから各CPTの個別URLを取得して補正する。
- Elementorの「公開」は未実行。確認用プレビューのみで検証済み。

### 確認用トップページ追加カテゴリ枠（Elementor未保存、2026-10-27）

- 住宅スライダーの下、既存 `Works / 一般建築` の上に、`Works / 店舗・オフィス` と `Works / リノベーション` の独立カテゴリ枠を追加する準備をした。表示順は住宅 → 店舗・オフィス → リノベーション → 一般建築。
- 店舗・オフィスとリノベーションは、物件0件の状態では見出し・区切り線・空カードを含めて非表示。各枠のカードコンテナに物件が追加された時だけ、カテゴリ全体を表示する条件付き構成。
- 旧プレビュー用のダミーカードは削除し、再プレビュー時にも残存しないよう既存の一時生成要素を除去してから枠を再生成する。
- 現在は両カテゴリとも0件として非表示、住宅13件と既存一般建築の表示は維持されることを確認した。
- 既存詳細ページへのリンク接続は未実施。店舗・オフィス／リノベーションをどの投稿タイプ・タクソノミーで管理するか、および対応する既存詳細ページURLの確認が必要。
- Elementorの「公開」は未実行。確認用プレビューのみで検証済み。

### ブログ個別記事タイトルの見た目調整（公開済み、2026-10-28）

- 記事タイトルの文章は変更しない。先に作成した `ブログ記事タイトル改善案_20261027.md` は撤回扱いで、本番投稿タイトルには反映しない。
- 固定ページID 650（`/blog/`）のPostsウィジェットで、記事タイトルを22px・Semi Bold（600）・行高32px・下余白14pxへ調整した。
- Single PostテンプレートID 2434のPost Titleを、PC 36px・Bold（700）・行高50px、スマホ28px・Bold（700）・行高1.45へ調整した。
- 共通見出しの `Blog` / `More Posts`、記事本文、スラッグ、公開日、カテゴリーは変更していない。
- 2026-10-28に固定ページID 650とSingle PostテンプレートID 2434を公開。公開画面で一覧22px／600／行高32px／下余白14px、詳細PC 36px／700／行高50pxの反映を確認した。

### ブログのアーカイブ表示改善（未保存、2026-10-28）

- 固定ページID 650とSingle PostテンプレートID 2434の `wp-widget-archives` に、ウィジェット単位のElementor Custom CSSで同じデザインを設定した。
- 背景 `#f4f4f1`、上部3pxの黒線、内側余白24px×22px、見出しと月別行の細い区切り、各月の右矢印を採用。
- リストの黒丸を削除し、Single側の投稿件数は `li` の文字サイズを0にして非表示。リンク文字は13pxで維持する。
- ホバー／キーボードフォーカス時はリンクが左から5px動き、矢印が右へ3px動く。
- 一覧・詳細ともElementorの未保存プレビュー。保存・公開前にMANABUの確認が必要。

## 引き継ぎとの差分・要注意事項

1. 「general_works用Single/Archiveは未着手」という記録と異なり、現在はID 9546と9697が `general_works` にも本番適用済み。
2. 一般建築SingleではNEXT WORKS自体が表示されるが、ID 5のクエリが `sunny_works` 固定のため、表示先は住宅3件（坂の上の船、丘の空母、囲空の家）。一般建築用NEXT WORKSではない。
3. 一般建築ArchiveにもID 9697が適用されるが、見出しは `WORKS / 住宅` のまま。
4. `has_archive` は両CPTですでにtrue。カットオーバー手順の「has_archive:trueへ変更」は現状では不要。`sunny_works` の `rewrite_slug` は空欄のため、住宅URLはまだ `/sunny_works/`。
5. 住宅Archiveを管理者ログイン状態で見ると `acf-image.php` 58行目のWarningが複数表示された。匿名ブラウザではWarningは表示されなかったため、一般訪問者への露出は確認されなかったが、根本条件は残っている可能性がある。
6. 共通ヘッダーメニュー `menu1` は、WORKS配下13件とIDEAS配下8件を削除済み。WORKSは `/works/`、IDEASは `/ideas/` への直接リンク。ElementorヘッダーテンプレートID 721自体は無変更。
7. 固定ページ646（`/works/`）は公開中で、削除・リダイレクト・slug切替は未実施。

## 現在の未着手／要判断タスク

1. `general_works` の既存共用Single/Archiveを、一般建築として仕上げるか、専用テンプレートに分離するか判断。
2. 一般建築のNEXT WORKSを非表示にするか、一般建築3件の循環に作り替えるか判断。
3. アーカイブ側サムネイル2枚間のgap調整。
4. 確認用トップページの住宅スライダー仕様を保存・公開するかの最終承認。
5. スマホメニュー本番全ページ展開（迫谷様確認後）。
6. `/works/` 正式カットオーバー。実行前にバックアップ・手順書・MANABU承認が必要。

## カットオーバー時の現状前提

- 固定ページ646 `/works/` が現在のパスを占有。
- `sunny_works` は `has_archive = true` 済み、`rewrite_slug` 空欄。
- 実施候補：バックアップ → 固定ページ646の扱い決定 → `rewrite_slug = works` → パーマリンク保存 → 301 → BRADEを含む全件確認。
- 上記は取り消し困難な本番変更のため、MANABU承認前は実行しない。

## 再発防止メモ

- Loop Gridのクエリキーは `post_query_` 接頭辞が必要。
- ACF動的タグは `field_key:field_name` 形式。
- 動的タグのbefore/afterに記号を入れると、空値時にウィジェットごと消える。記号は静的テキストへ置く。
- 全幅セクションは `content_width: "full"` を明示。
- ギャラリーは `thumbnail_image_size = 1536x1536` を明示。
- アイキャッチ動的タグは `post-featured-image`。
- Elementorの数値0は文字列ではなく数値型。
- 公開済みページはdraft保存では反映されない。公開更新ボタンで反映する。
- ACF画像／Relationshipのクリアは `null`。
- CPTUIのselect値は `'1'/'0'`。
- Code Snippetsの有効化は一覧のbulk-activateが確実。
- 設定変更後はElementorのファイル・データを再生成し、force reload後に実測する。
- モバイル検証は同一オリジンiframeで幅指定する。

## 2026-10-25 作業影響

- WordPress／本番サイトへの変更：なし。
- 本番トップID 864：無変更。
- 本番ヘッダーID 721：無変更。
- ローカル変更：本ノートを復旧作成。
