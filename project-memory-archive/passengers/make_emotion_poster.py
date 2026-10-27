from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
BG = "#b9d4dc"
INK = "#172426"
PINK = "#dc9a9d"
BONE = "#eee3c8"
OCHRE = "#d7a13f"
DEEP = "#405f69"
MUTED = "#6e7f81"

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

font_jp = "C:/Windows/Fonts/YuGothM.ttc"
font_jp_bold = "C:/Windows/Fonts/YuGothB.ttc"
font_en = "C:/Windows/Fonts/arialbd.ttf"
font_en_regular = "C:/Windows/Fonts/arial.ttf"

def f(path, size):
    return ImageFont.truetype(path, size)

def centered(text, y, font, fill=INK, spacing=4):
    box = d.textbbox((0, 0), text, font=font, spacing=spacing)
    d.text(((W - (box[2] - box[0])) / 2, y), text, font=font, fill=fill, spacing=spacing)

def node(x, y, color, jp, en, width=250):
    d.rectangle((x, y, x + width, y + 112), fill=color, outline=INK, width=4)
    d.text((x + 18, y + 15), jp, font=f(font_jp_bold, 34), fill=INK)
    d.text((x + 18, y + 65), en, font=f(font_en, 17), fill=INK)

# Editor's grid
for x in (54, 270, 540, 810, 1026):
    d.line((x, 0, x, H), fill="#83a9b3", width=1)
for y in (70, 220, 480, 830, 1090, 1280):
    d.line((0, y, W, y), fill="#83a9b3", width=1)

# Header
d.rectangle((54, 55, 1026, 126), fill=INK)
d.text((76, 75), "ART / INNER LOGIC", font=f(font_en, 18), fill=BONE)
d.text((835, 75), "01", font=f(font_en, 18), fill=BONE)
centered("感動を中心にする", 158, f(font_jp_bold, 52))
centered("PUT EMOTION AT THE CENTER", 230, f(font_en, 19), MUTED)

# Structural lines behind the core
d.line((160, 530, 918, 530), fill=INK, width=3)
d.line((540, 356, 540, 864), fill=INK, width=3)
d.line((235, 680, 840, 424), fill=INK, width=3)
d.line((235, 424, 840, 680), fill=INK, width=3)

# Central force / quiet salt-flat palette
d.ellipse((280, 330, 800, 850), fill=DEEP, outline=INK, width=6)
d.ellipse((350, 400, 730, 780), outline=OCHRE, width=6)
d.arc((305, 355, 775, 825), 40, 215, fill=PINK, width=18)
d.arc((305, 355, 775, 825), 225, 30, fill=BONE, width=18)
d.line((430, 604, 650, 604), fill=BONE, width=3)
centered("感動", 520, f(font_jp_bold, 86), BONE)
centered("EMOTION", 631, f(font_en, 29), BONE)
centered("腹に来る力", 683, f(font_jp, 27), BONE)

# Nodes: Japanese first, English below
node(65, 355, BONE, "記憶", "MEMORY")
node(765, 355, PINK, "違和感", "DISSONANCE")
node(65, 770, OCHRE, "夢の論理", "DREAM LOGIC", 292)
node(723, 770, BONE, "コラージュ", "COLLAGE", 292)
node(415, 897, PINK, "絵画", "PAINTING", 250)

# Small directional annotations
d.text((64, 326), "REAL FRAGMENTS", font=f(font_en, 14), fill=MUTED)
d.text((760, 326), "THE SHIFT", font=f(font_en, 14), fill=MUTED)
d.text((64, 742), "DREAM ENTERS", font=f(font_en, 14), fill=MUTED)
d.text((723, 742), "COLLIDE", font=f(font_en, 14), fill=MUTED)
d.text((414, 869), "ONE COMPLETE DREAM", font=f(font_en, 14), fill=MUTED)

# Footer declaration
d.rectangle((54, 1080, 1026, 1270), fill=INK)
centered("シュールは、この世界に夢の論理が侵入すること。", 1120, f(font_jp_bold, 30), BONE)
centered("SURREALISM IS DREAM LOGIC ENTERING THIS WORLD.", 1170, f(font_en, 16), PINK)
centered("美しいかどうかではなく、腹に来るか。", 1215, f(font_jp_bold, 34), BONE)

img.save("C:/Users/user/Documents/ChatGPT/passengers/emotion-at-the-center.png", quality=95)
