# 🎨 コラージュ — CONTEXT

## 目的

コラージュ作品の画像制作・編集を行う。Affinity Designer / Photo で後編集できる成果物を優先する。

## 固定ルール

- 元画像の形状を変えない編集では、元の画素形状・構図を保持する。
- レイヤー保持形式は PSD を優先し、確認用 PNG も併せて出力する。
- `sources/` 配下のファイルは参照専用として扱う。
- Affinityでの被写体切り抜きは、AffinityのMCPではなくカーソル操作で行う（MCPではAI機能がPERMISSION_DENIEDになるため）。手順：オブジェクト選択ツールで被写体をクリック → ピクセル → 新規マスク → マスクレイヤー。元画像は残す。

## コラージュ動画（リール）の作り方

- 「コラージュ動画作って」で始める。手順の正本は共有スキル `collage-reel`（`C:\Users\user\Documents\ChatGPT\cropri-design-library\skills\collage-reel\SKILL.md`、Claude・Codex共通）。
- 流れ：PCのGoogleフォトから素材を1つずつダウンロード → タイトル・キャプション → 早回し確認 → カット切り出し → 壁掛けトップ画像 → CapCutで15秒・9:16・無音 → 書き出し → `H:\マイドライブ\コラージュ\`（mmmm9691のドライブ＝スマホで見えるほう）に `NNN-Title.mp4` と `.txt` を置く。このフォルダ（G:、aimanabu9691）はスマホから見えない。
- 投稿はMANABUがスマホで行う（ドライブから動画とキャプションを落とし、各SNSへ。Instagramは Edits で音楽を付ける）。AIは投稿しない。

## SNS自動投稿のルール

- 投稿・公開・共有設定の変更は、ユーザーが明示的に承認してから行う。取り消せないものは特に。
- トークン・APIキー・WebhookのURLは、チャットにもファイルにも書かない。n8nのCredentialはユーザーが画面で入れる。
- `動画コラージュ/0906 (1).mp4` は投稿しない。
- 仕組み・ID・使い方・現在の状態は `SNS自動投稿_引き継ぎ.md` を読む（その作業をするときだけ）。

## 共有場所

- Google Drive プロジェクトフォルダ: https://drive.google.com/drive/folders/1GTV6c34GQiWLofNRI2EJvxCV6Chd1VWn

