# 🎨 コラージュ — PROGRESS

更新日: 2026-10-04

## 現在の作業

1. 白黒オプアート肖像をAffinityで編集し、花・葉のポスターカラー風イラストを別レイヤーで追加する（Codexの作業）。
2. コラージュのリールを、Instagram以外のSNS（YouTubeショーツ、TikTok、X）へ自動で展開する仕組みを作っている（詳細は `SNS自動投稿_引き継ぎ.md`）。

## オプアート肖像（Affinity）の現状

- 編集元PSD: `60年代モノクロ_オプアート肖像_レイヤー分解.psd`
- 確認用PNG: `60年代モノクロ_オプアート肖像_確認用.png`
- PSDはAffinity Photoで6レイヤーが正しく読み込めることを確認済み。
- 既存レイヤー: Background / Person base / Earring / Circular chest piece / Left wrist piece / Right hand piece。
- 人物と黒白アクセサリーの形状は変更しない。
- ちぎり表現は使わない。輪郭はきれいに保つ。
- 花・葉は写実ではなく、簡単なポスターカラー風のベタ面イラスト。
- 色はコーラルピンク、淡いピーチ、くすんだ青緑、生成りを中心にする。
- 色は写真の現実色を再現する着彩ではなく、白黒写真に重ねる独立したデザイン要素として扱う。
- 花・葉・色面は、Affinityで後から動かせるよう別レイヤーに分ける。

### Codexへの次の作業（Affinity）

1. Affinityを起動し、MCPを有効化する。
2. 接続経路は `Codex → mcp-proxy → Affinity (localhost:6767/sse)` を使用する。
3. `60年代モノクロ_オプアート肖像_レイヤー分解.psd` を開く。
4. 人物と既存アクセサリーはそのまま保持する。
5. 花・葉をポスターカラー風のベタ面で追加する。ちぎり表現は使わない。
6. 花・葉・色面を別レイヤーに分ける。
7. 編集可能なPSD/Affinityファイルとして保存し、確認用PNGも出力する。

## 008 新作コラージュ（2026-10-11）

- 白黒の女性＋オプアートの装身具＋手描きの花・葉（額装の実物写真をユーザーが共有）。
- タイトル案「008-Op Garden」、キャプション案を `008-Op-Garden.txt` に作成（007と同じ形式）。ユーザー確認待ち。未投稿。
- リール（15秒・9:16・無音・文字なし）をCapCutプロジェクト `1011 (1)` で編集完了（2026-10-11、Claude）。**書き出しは未実施**。
  - 素材: `E:\XXX\art\コラージュ\OUT OF SCALE\008-Op Garden\capcut_cuts\` の13本（元動画8本から制作順に切り出し、2〜6倍速。元動画は無変更）。
  - 構成: 完成カット → 下地塗り → 切り抜き → 円・花・葉 → 貼り付け → 細部描き込み → 完成。13〜15秒に `008-Op-Garden_top.png`（拡大119%）をフェードイン1.9秒で重ねる。
  - MANABU確認：基本OK。トップ画像を作り直し済み：Codexが `008-Op-Garden_cover_natural.png`（1080×1920、壁に掛かった額、額全体が3:4範囲内）を作成。Claudeが CapCut の最後の画像を差し替え（約13.1〜15秒、拡大100%、フェードイン1.8秒）。旧 `008-Op-Garden_top.png` はタイムラインから外しただけで、ファイルは残している。
  - 構成は「完成カットで始める」で確定（MANABU了承）。
  - **書き出し済み（2026-10-11）**: `E:\XXX\art\コラージュ\OUT OF SCALE\008-Op Garden\008-Op-Garden_reel_15s.mp4`（1080×1920・30fps・15秒・無音）。
  - スマホ受け渡し用に `H:\マイドライブ\コラージュ\008-Op-Garden.mp4` と `008-Op-Garden.txt` を配置済み（スマホのドライブはmmmm9691のアカウント）。G:側にも同じ動画のコピーあり。
  - **Instagram投稿済み（2026-10-11 21:50ごろ、MANABUがEditsから）**。音楽は Serge Gainsbourg & Brigitte Bardot「Comic Strip」。カバーは `008-Op-Garden_表紙.png`。
  - 個人Facebook（facebook.com/manabu.kurokui、フォロワー約1200人）にも掲載済み。Business Suite連携のFBページ「collage ＆ monotype」はフォロワー1人なので、届けたいのは個人アカウントの方。
  - FBグループ3つに作品写真＋文章（リンクなし）を投稿（2026-10-11 22:50ごろ、MANABU承認のうえClaudeが操作）：COLLAGE GROUP（5.1万人）・COLLAGE（12.7万人）・COLLAGE ARTISTS WORLDWIDE（1.9万人）。結果：COLLAGE GROUP・COLLAGE ARTISTS WORLDWIDE は**公開済み**、COLLAGE は最初キーワードで自動却下 → 短文（"008 Op Garden" / Hand-cut paper collage with flowers painted by hand. / Made with scissors, glue and brush.）に編集して出し直したら**公開済み**（23:15ごろ）。jewelry・Japan・greetings・series・analógico・portrait・60s は他人の公開投稿にあり原因ではない。外した語（op-art / OUT OF SCALE / pintadas a mano / black-and-white / 🌸 など）のどれかが禁止語。
  - 9月の007リールのリンク共有（承認待ち）は、CAWは取り下げ済み。COLLAGE と COLLAGE GROUP は削除ボタン→確認を押しても残る（2026-10-11 23:00時点）。MANABUに手動削除を依頼。
  - 次: 2026-10-12に007の作品写真を3グループへ投稿（MANABU依頼。写真は実物の額装写真、AI画像は使わない。COLLAGEは自動却下されにくい文面で）。
  - 他SNS（TikTok・YouTube等）は未投稿。
  - 初動（投稿2時間）: FB閲覧103・IG閲覧205、3秒再生19、平均再生率37%、完了率4.5%、0:01の離脱が最多。IGリール一覧では008=308 / 007=10万 / 002=2,387。→ 完成から始める構成が一目で分かる作品には逆効果と分析（手順書に反映）。008第2版（塗り→花→白黒の女性が現れる→壁の完成）は未着手・MANABU判断待ち。上げる場合はドライブの無音版 `008-Op-Garden.mp4` を使い、各アプリで音楽を付ける。
- この一連は共有スキル `collage-reel` にまとめた（「コラージュ動画作って」で開始）。

## SNS自動投稿の現状（10/4時点。詳細は `SNS自動投稿_引き継ぎ.md`）

- **YouTube**: 旧「002 Bauhaus」音声あり版 `UfAgKwfR8Mk` は2026-10-04に削除済み。無音版 `Vy409LVy8N0` はプライベートで、サムネイルは未設定。
- **決定済み**: 無音版にサムネイルを設定する。YouTubeの公開範囲は当面プライベート。音楽はInstagramで使った Kraftwerk「Das Model」を希望。YouTube Studioの音声ライブラリで検索したが、追加可能な音源は見つからなかった。
- **TikTok・X**: Bufferへの接続とn8nノードは作成済み。**実際の予約は未実施**。Drive公開リンクの動画をBufferが取得できるかは未確認。
- **「007 夜と昼」**: 元動画 `007_夜と昼_reel_15s.mp4` は**無音**（Instagramで音楽を付けた）。Driveに `007-Day-and-Night.mp4/.txt` がある。未投稿。
- **期限**: Bufferのキー 11/2頃、Instagramトークン 12/2頃。Google認証は約7日で切れる（アプリがテスト中）。
- **投稿禁止**: `動画コラージュ/0906 (1).mp4`。
- 投稿・公開・共有の変更は、ユーザーの明示的な承認後にだけ行う。秘密情報はチャットにもファイルにも書かない。

## 次にやること（SNS）

1. 無音版 `Vy409LVy8N0` のサムネイルを設定する（ユーザー承認済み）。
2. YouTubeで「Das Model」を使う別の正規手段を検討する（Studioの音声ライブラリでは利用不可）。
3. 承認を得て、TikTok・Xの予約を1本ずつ試す（まず「002 Bauhaus」）。
4. n8nの常駐化とトークン更新の運用を決める。
