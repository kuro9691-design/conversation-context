# BUNK CONTEXT（恒久的な前提・ルール）

## プロジェクト
- BUNK: 手製ジン形式、週1回（金曜）のInstagramカルーセル投稿、全144回×10枚。画像はMidjourney。
- 制作ロジックは skill `bunk-midjourney-prompts` に従う。Vol.1は手動投稿。Vol.2以降を自動投稿の対象にする。
- 投稿カレンダー（スプレッドシートID `1ORcWdqVgFZ6crdF15bXNjwNXYwTxzsAs0If952DLr-Q`）の「準備完了」列は人が手動でTRUEにする（数式にしない）。

## 自動投稿（n8n）
- 設計書: `BUNK_n8nカルーセル自動投稿_設計書.md`（トリガー・13ノード構成・エラー処理の方針）。
- n8nはこのPCで `npx` キャッシュのv2.33.7を使い、`http://localhost:5678` で起動する（pm2・サービス登録なし。止まっていたら手動起動）。データは `~/.n8n`。
- 既存Credential「Instagram account」（長期トークン設定済み）を再利用する。

## 認証情報の扱い
- APIキー・トークン・App Secretはn8nのCredentialにローカル保持。チャット・ファイル・ログに出さない。
- `~/.n8n/config` の暗号化キーも出力しない。

## 関連資料
- Substack展開構想: `BUNK_Substack展開_引き継ぎ_20260828.md`（構想段階。Vol.3制作・転職活動が優先）。
