from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    Image,
    KeepTogether,
)


ROOT = Path(r"G:\マイドライブ\sunny-design")
OUT = ROOT / "output" / "pdf" / "SUNNY_DESIGN_顧問建築士_市場分析レポート_20261027.pdf"
ASSETS = ROOT / "assets" / "concepts"

W, H = A4
INK = colors.HexColor("#232323")
MUTED = colors.HexColor("#6E6C67")
PAPER = colors.HexColor("#F7F4EE")
WHITE = colors.HexColor("#FFFDF8")
BRASS = colors.HexColor("#A88952")
BLUEGRAY = colors.HexColor("#56636A")
RULE = colors.HexColor("#D8D2C7")
PALE = colors.HexColor("#EAE5DB")


def register_fonts():
    pdfmetrics.registerFont(TTFont("NotoSansJP", r"C:\Windows\Fonts\NotoSansJP-VF.ttf"))
    pdfmetrics.registerFont(TTFont("NotoSerifJP", r"C:\Windows\Fonts\NotoSerifJP-VF.ttf"))


register_fonts()

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="JPBody", fontName="NotoSansJP", fontSize=9.2, leading=15,
    textColor=INK, spaceAfter=3*mm,
))
styles.add(ParagraphStyle(
    name="JPSmall", fontName="NotoSansJP", fontSize=7.5, leading=11.5,
    textColor=MUTED, spaceAfter=2*mm,
))
styles.add(ParagraphStyle(
    name="Kicker", fontName="NotoSansJP", fontSize=7.2, leading=9,
    textColor=BRASS, charSpace=2.1, spaceAfter=4*mm,
))
styles.add(ParagraphStyle(
    name="H1JP", fontName="NotoSerifJP", fontSize=24, leading=34,
    textColor=INK, spaceAfter=7*mm,
))
styles.add(ParagraphStyle(
    name="H2JP", fontName="NotoSerifJP", fontSize=16.5, leading=24,
    textColor=INK, spaceBefore=2*mm, spaceAfter=5*mm,
))
styles.add(ParagraphStyle(
    name="H3JP", fontName="NotoSansJP", fontSize=10.5, leading=15,
    textColor=INK, spaceAfter=2*mm,
))
styles.add(ParagraphStyle(
    name="BigNumber", fontName="NotoSerifJP", fontSize=28, leading=31,
    textColor=BRASS, alignment=TA_LEFT,
))
styles.add(ParagraphStyle(
    name="CardText", fontName="NotoSansJP", fontSize=8.3, leading=13,
    textColor=INK,
))
styles.add(ParagraphStyle(
    name="Quote", fontName="NotoSerifJP", fontSize=13, leading=22,
    textColor=INK, leftIndent=5*mm, borderColor=BRASS, borderWidth=0,
    borderPadding=0,
))
styles.add(ParagraphStyle(
    name="CenterSmall", fontName="NotoSansJP", fontSize=7.5, leading=11,
    textColor=MUTED, alignment=TA_CENTER,
))


class ReportDoc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=18*mm,
            rightMargin=18*mm,
            topMargin=20*mm,
            bottomMargin=17*mm,
            title="SUNNY DESIGN 顧問建築士 市場分析レポート",
            author="黒杭デザイン / Codex",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=draw_page))


def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, W, H, stroke=0, fill=1)
    if doc.page > 1:
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.4)
        canvas.line(18*mm, H-13*mm, W-18*mm, H-13*mm)
        canvas.setFont("NotoSansJP", 6.8)
        canvas.setFillColor(MUTED)
        canvas.drawString(18*mm, H-9.5*mm, "SUNNY DESIGN / CORPORATE ARCHITECT ADVISORY")
        canvas.drawRightString(W-18*mm, 9*mm, f"{doc.page:02d}")
    canvas.restoreState()


def P(text, style="JPBody"):
    return Paragraph(text, styles[style])


def bullet(text):
    return Paragraph(f"<font color='#A88952'>●</font>　{text}", styles["JPBody"])


def img(path, width):
    im = Image(str(path))
    iw, ih = im.imageWidth, im.imageHeight
    im.drawWidth = width
    im.drawHeight = width * ih / iw
    return im


def card(number, title, text, width=53*mm):
    data = [[P(number, "BigNumber")], [P(title, "H3JP")], [P(text, "CardText")]]
    t = Table(data, colWidths=[width], rowHeights=[14*mm, 8*mm, None])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), WHITE),
        ("BOX", (0,0), (-1,-1), 0.45, RULE),
        ("LINEABOVE", (0,0), (-1,0), 1.5, BRASS),
        ("LEFTPADDING", (0,0), (-1,-1), 5*mm),
        ("RIGHTPADDING", (0,0), (-1,-1), 5*mm),
        ("TOPPADDING", (0,0), (-1,-1), 4*mm),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4*mm),
    ]))
    return t


def section_title(kicker, title, intro=None):
    out = [P(kicker, "Kicker"), P(title, "H1JP")]
    if intro:
        out.append(P(intro, "JPBody"))
    return out


story = []

# 1 Cover
story += [Spacer(1, 13*mm), P("MARKET ANALYSIS / 2026.10.27", "Kicker")]
story += [P("企業の建築判断を支える<br/>「顧問建築士」市場分析", "H1JP")]
story += [P("SUNNY DESIGN 法人向け新規サービス構想", "H3JP"), Spacer(1, 8*mm)]
story.append(img(ASSETS / "sunny-design-corporate-advisory-concept-v1.png", 174*mm))
story += [Spacer(1, 8*mm), P("調査・企画：黒杭デザイン", "JPSmall")]
story += [P("本資料は公開統計・競合公開情報・SUNNY DESIGN公開情報、および関係者から共有された実例候補を基にした事業仮説です。未確認事項は明示しています。", "JPSmall")]
story.append(PageBreak())

# 2 Executive summary
story += section_title("01 / EXECUTIVE SUMMARY", "結論：参入価値は高い。<br/>ただし、検索待ちでは売れない。")
story.append(P("完全な競合不在市場ではありません。設計監理、CM、発注者支援、見積査定という既存領域を、地域中小企業向けに分かりやすく再商品化できる余白が大きい市場です。", "Quote"))
story.append(Spacer(1, 6*mm))
summary_cards = Table([[card("7/10", "ブルーオーシャン度", "直接競合は少ない一方、工務店・管理会社・設計事務所など代替競合は多い。"),
                        card("3段階", "商品設計", "スポット診断 → 案件支援 → 月額顧問。最初から顧問契約を売らない。"),
                        card("90日", "市場検証", "経営者10社、相談3件、有料1件を本サイト化の判断基準にする。")]],
                      colWidths=[58*mm]*3, hAlign="LEFT")
summary_cards.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),0), ("RIGHTPADDING",(0,0),(-1,-1),2*mm)]))
story.append(summary_cards)
story.append(Spacer(1, 8*mm))
story += [P("勝ち筋", "H2JP"), bullet("『安くする人』ではなく、『経営者が安心して発注判断できる状態をつくる専門家』として位置づける。"), bullet("現行住宅サイトと分け、法人向け独立LPで検証する。"), bullet("紹介営業を主軸にし、サイトは紹介後の信用確認とスポット相談の受け皿にする。")]
story.append(PageBreak())

# 3 Evidence
story += section_title("02 / MARKET SIGNAL", "市場を支える3つの追い風")
data = [
    [P("2兆8,252億円", "BigNumber"), P("+25.5%", "BigNumber"), P("133.5", "BigNumber")],
    [P("非住宅リフォーム・リニューアル<br/>2025年度第3四半期受注高", "CardText"), P("同受注高の前年同期比", "CardText"), P("建築総合工事費デフレーター<br/>2025年12月", "CardText")],
]
t = Table(data, colWidths=[58*mm]*3, rowHeights=[22*mm, 18*mm])
t.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,-1),WHITE), ("BOX",(0,0),(-1,-1),0.45,RULE),
    ("INNERGRID",(0,0),(-1,-1),0.35,RULE), ("LEFTPADDING",(0,0),(-1,-1),5*mm),
    ("TOPPADDING",(0,0),(-1,-1),5*mm), ("VALIGN",(0,0),(-1,-1),"TOP"),
]))
story.append(t)
story.append(Spacer(1, 8*mm))
story += [P("解釈", "H2JP"), bullet("改修市場が大きく、発注判断が繰り返し発生している。"), bullet("工事費上昇により、見積条件・工法・優先順位を精査する価値が増している。"), bullet("高額発注では、数％の判断差でも専門家報酬を上回る可能性がある。")]
story += [Spacer(1, 5*mm), P("地域の母集団", "H2JP")]
local = Table([[card("122,155", "広島県内の民営事業所", "2021年。すべてが対象ではないが、施設保有企業の母集団は十分に大きい。", 82*mm),
                card("約1,700", "広島県建築士会の会員", "建築士は多いが、法人発注者側の中立顧問という見せ方は検索上まだ少ない。", 82*mm)]], colWidths=[87*mm,87*mm])
local.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),0)]))
story.append(local)
story.append(PageBreak())

# 4 Competition / positioning
story += section_title("03 / COMPETITION", "競合が少ないのではなく、<br/>見せ方が空いている。")
comp = [
    [P("選択肢", "H3JP"), P("顧客が期待すること", "H3JP"), P("弱点・空白", "H3JP")],
    [P("工務店・建設会社", "CardText"), P("施工、緊急対応、価格提示", "CardText"), P("工事受注と助言の利害が一致しない場合がある", "CardText")],
    [P("一般的な設計事務所", "CardText"), P("設計力、監理、デザイン", "CardText"), P("継続的な経営判断支援として商品化されていない", "CardText")],
    [P("管理会社・不動産会社", "CardText"), P("日常管理、物件情報、業者手配", "CardText"), P("建築技術・見積精査の深さにばらつき", "CardText")],
    [P("積算・CM・コンサル", "CardText"), P("大規模案件の発注者支援", "CardText"), P("中小企業には難しく、高額・大企業向けに見えやすい", "CardText")],
]
ct = Table(comp, colWidths=[42*mm,57*mm,75*mm], repeatRows=1)
ct.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),BLUEGRAY), ("TEXTCOLOR",(0,0),(-1,0),WHITE),
    ("BACKGROUND",(0,1),(-1,-1),WHITE), ("GRID",(0,0),(-1,-1),0.4,RULE),
    ("VALIGN",(0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),4*mm),
    ("RIGHTPADDING",(0,0),(-1,-1),4*mm), ("TOPPADDING",(0,0),(-1,-1),4*mm),
    ("BOTTOMPADDING",(0,0),(-1,-1),4*mm),
]))
story.append(ct)
story += [Spacer(1, 9*mm), P("推奨ポジション", "H2JP"), P("建てる会社を決める前に、相談できる建築士。", "Quote"), Spacer(1, 4*mm), P("施工会社を敵にするのではなく、発注条件を整え、見積・品質・工期・将来維持費を同じテーブルで判断できるようにする『企業側の建築参謀』です。", "JPBody")]
story.append(PageBreak())

# 5 Target and offer ladder
story += section_title("04 / TARGET & OFFER", "最初に狙う企業と、<br/>売りやすい入口")
targets = Table([
    [P("優先", "H3JP"), P("顧客像", "H3JP"), P("発生する課題", "H3JP")],
    [P("A", "BigNumber"), P("複数施設を持つ地域企業", "CardText"), P("修繕、出店、法規、業者選定が繰り返し発生", "CardText")],
    [P("B", "BigNumber"), P("建築専門社員がいない20-300人規模", "CardText"), P("社長・総務が数千万円の判断を背負う", "CardText")],
    [P("C", "BigNumber"), P("改修・移転・出店直前の企業", "CardText"), P("問題が顕在化し、スポット診断を買いやすい", "CardText")],
], colWidths=[25*mm,67*mm,82*mm])
targets.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),BLUEGRAY),("TEXTCOLOR",(0,0),(-1,0),WHITE),
    ("BACKGROUND",(0,1),(-1,-1),WHITE),("GRID",(0,0),(-1,-1),0.4,RULE),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),4*mm),
    ("TOPPADDING",(0,0),(-1,-1),4*mm),("BOTTOMPADDING",(0,0),(-1,-1),4*mm),
]))
story.append(targets)
story += [Spacer(1, 9*mm), P("商品は3段階", "H2JP")]
ladder = Table([[card("01", "スポット診断", "相談・資料レビュー・確認事項を1枚に整理。需要の入口。"),
                 card("02", "案件単位の発注者支援", "見積条件の統一、比較、代替案、打合せ同席。"),
                 card("03", "企業のかかりつけ建築士", "月次相談、一次判断、年次レビュー、修繕計画。")]], colWidths=[58*mm]*3)
ladder.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),0), ("RIGHTPADDING",(0,0),(-1,-1),2*mm)]))
story.append(ladder)
story.append(PageBreak())

# 6 Pricing / success fee
story += section_title("05 / PRICING", "10万円の相談ではなく、<br/>高額判断の価値で設計する。")
prices = [
    [P("商品", "H3JP"), P("初期仮説（税別）", "H3JP"), P("境界", "H3JP")],
    [P("初回相談", "CardText"), P("1万-1.5万円", "CardText"), P("資料精査・現地訪問なし", "CardText")],
    [P("見積・改修セカンドオピニオン", "CardText"), P("5万-10万円", "CardText"), P("資料量・工種数で個別設定", "CardText")],
    [P("案件単位の発注者支援", "CardText"), P("20万円から", "CardText"), P("打合せ回数・成果物を固定", "CardText")],
    [P("ライト顧問", "CardText"), P("月5万円前後", "CardText"), P("オンライン中心・訪問別料金", "CardText")],
    [P("複数施設顧問", "CardText"), P("月10万円から", "CardText"), P("棟数・訪問・応答条件で設計", "CardText")],
]
pt = Table(prices, colWidths=[58*mm,42*mm,74*mm], repeatRows=1)
pt.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),BLUEGRAY),("TEXTCOLOR",(0,0),(-1,0),WHITE),
    ("BACKGROUND",(0,1),(-1,-1),WHITE),("GRID",(0,0),(-1,-1),0.4,RULE),
    ("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),4*mm),
    ("TOPPADDING",(0,0),(-1,-1),3.5*mm),("BOTTOMPADDING",(0,0),(-1,-1),3.5*mm),
]))
story.append(pt)
story += [Spacer(1, 8*mm), P("大型案件の成果連動", "H2JP"), P("固定報酬＋成果報酬は成立し得ます。ただし、基準見積、同等条件、対象外項目、算定時点、報酬率、上限額を契約で定義します。単純な削減額歩合にすると、仕様縮小や品質低下まで成果に見えるため危険です。", "JPBody")]
example = Table([[P("実例候補（要確認）", "H3JP"), P("約4,000万円の見積相談後、約2,000万円の差額が生じたとの口頭情報。10%なら200万円。ただし、同一仕様・最終契約額・因果関係・掲載許可の確認前は実績として断定しない。", "CardText")]], colWidths=[48*mm,126*mm])
example.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#F0EBE1")),("BOX",(0,0),(-1,-1),0.7,BRASS),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),5*mm),("RIGHTPADDING",(0,0),(-1,-1),5*mm),("TOPPADDING",(0,0),(-1,-1),5*mm),("BOTTOMPADDING",(0,0),(-1,-1),5*mm)]))
story.append(example)
story.append(PageBreak())

# 7 Website strategy and screens 1-2
story += section_title("06 / WEBSITE", "サイトは契約を売り切る場ではなく、<br/>相談への不安を消す場。")
story.append(P("市場検証は1ページLP。本格公開は主要8ページ＋法定・運用2ページの約10ページを推奨します。現行住宅サイトとは目的が異なるため、法人向けの独立導線にします。", "JPBody"))
story.append(Spacer(1, 4*mm))
two = Table([
    [img(ASSETS / "sunny-design-corporate-advisory-concept-v1.png", 84*mm), img(ASSETS / "sunny-design-corporate-advisory-service-v1.png", 84*mm)],
    [P("01 / TOP<br/>価値と不安を一画面で伝える", "CenterSmall"), P("02 / SERVICE<br/>頼める業務を経営者の言葉で整理", "CenterSmall")],
], colWidths=[87*mm,87*mm])
two.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),3*mm),("TOPPADDING",(0,0),(-1,-1),2*mm),("BOTTOMPADDING",(0,0),(-1,-1),4*mm)]))
story.append(two)
story += [Spacer(1, 5*mm), P("主要ページ", "H2JP"), P("TOP / 顧問建築士とは / サービス / 事例 / 料金・契約 / ご相談の流れ / 建築士紹介 / FAQ・問い合わせ", "JPBody")]
story.append(PageBreak())

# 8 Screens 3-4
story += section_title("07 / DESIGN CONCEPT", "嘘くさくない。<br/>静かに、判断力を見せる。")
story.append(P("住宅作品集の延長ではなく、企業資産を扱う専門家としての落ち着き、透明性、知性を表現します。未確認の数字、架空の顧客ロゴ、受賞歴、偽ポートレートは使用しません。", "JPBody"))
two2 = Table([
    [img(ASSETS / "sunny-design-corporate-advisory-case-v1.png", 84*mm), img(ASSETS / "sunny-design-corporate-advisory-architect-v1.png", 84*mm)],
    [P("03 / CASE<br/>課題・介入・判断・結果を可視化", "CenterSmall"), P("04 / ARCHITECT<br/>実績と思想を誇張せず提示", "CenterSmall")],
], colWidths=[87*mm,87*mm])
two2.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),3*mm),("TOPPADDING",(0,0),(-1,-1),2*mm),("BOTTOMPADDING",(0,0),(-1,-1),4*mm)]))
story.append(two2)
story += [Spacer(1, 6*mm), P("コピーの原則", "H2JP"), bullet("施工会社批判ではなく、条件整理と判断支援を語る。"), bullet("『必ず安くなる』『顧問料以上を保証』は言わない。"), bullet("ボレットは数字・損失・疑問を使い、本文への興味を作る。")]
story.append(PageBreak())

# 9 Risks and validation
story += section_title("08 / RISK & VALIDATION", "先に確認すべき5つ。<br/>その後、90日で売れるか試す。")
risks = [
    ("01", "中立性", "施工、紹介料、提携、工事利益の有無を確認。"),
    ("02", "業務範囲", "相談、現地調査、数量査定、交渉、監理を分ける。"),
    ("03", "成果定義", "削減額だけでなく品質・工期・維持費を含める。"),
    ("04", "一人依存", "緊急対応、休日、遠方、同時案件の条件を決める。"),
    ("05", "専門領域", "構造・設備・消防・法務の連携先を明示する。"),
]
rt = Table([[P(n,"BigNumber"), P(t,"H3JP"), P(d,"CardText")] for n,t,d in risks], colWidths=[25*mm,40*mm,109*mm])
rt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),WHITE),("LINEBELOW",(0,0),(-1,-1),0.4,RULE),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),4*mm),("TOPPADDING",(0,0),(-1,-1),4*mm),("BOTTOMPADDING",(0,0),(-1,-1),4*mm)]))
story.append(rt)
story += [Spacer(1, 8*mm), P("90日検証", "H2JP")]
timeline = Table([[card("10社", "経営者ヒアリング", "直近3年の建物の困りごとと支払経験を聞く。"), card("5者", "紹介者候補", "税理士、不動産、保険、金融、商工会議所へ説明。"), card("3→1", "合格ライン", "スポット相談3件、有料案件1件で本サイト化。")]], colWidths=[58*mm]*3)
timeline.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),2*mm)]))
story.append(timeline)
story.append(PageBreak())

# 10 recommendation and sources
story += section_title("09 / RECOMMENDATION", "最終判断")
story.append(P("参入を推奨します。", "H1JP"))
story.append(P("SUNNY DESIGNには、27年・200件超の設計経験という参入資格があります。成功の鍵は、デザインの派手さではなく、中立性の証明、具体的な事例、明確な業務範囲、紹介チャネルです。", "JPBody"))
story += [Spacer(1, 4*mm), P("次の順序", "H2JP"), bullet("迫谷氏へ事実確認：中立性・業務範囲・対応条件・実例。"), bullet("独立LPとスポット診断商品を作成。"), bullet("90日検証を実施し、有料1件で本格サイトへ移行。")]
story += [Spacer(1, 8*mm), P("主要公開資料", "H2JP")]
sources = [
    "国土交通省『国土交通月例経済（2026年3月号）』 https://www.mlit.go.jp/toukeijouhou/getsurei/r08/03/overview.pdf",
    "国土交通省『建築物リフォーム・リニューアル調査』 https://www.mlit.go.jp/statistics/details/t-other-2_tk_000221.html",
    "広島県『経済センサス』 https://www.pref.hiroshima.lg.jp/site/toukei/keizaicensus.html",
    "広島県建築士会『会員PR』 https://www.k-hiroshima.or.jp/nyukai/kaiinweb.php",
    "SUNNY DESIGN 公開サイト https://sunny-design.jp/",
    "清水哲建築設計事務所『施設保有法人向け建築顧問』 https://shimizu-arc.com/QAF.html",
    "住まい工房S『企業のかかりつけ建築士』 https://www.sumai-s.com/blog",
]
for s in sources:
    story.append(P(s, "JPSmall"))
story += [Spacer(1, 6*mm), P("注意：価格・成果報酬率・サイト構成は検証前の仮説です。契約条件、法的責任、建築士業務との区分は、正式提供前に専門家を交えて確認してください。", "JPSmall")]


OUT.parent.mkdir(parents=True, exist_ok=True)
doc = ReportDoc(str(OUT))
doc.build(story)
print(OUT)
