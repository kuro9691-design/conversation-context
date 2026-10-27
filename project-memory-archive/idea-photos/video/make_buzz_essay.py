# -*- coding: utf-8 -*-
"""映像エッセイ「バズは入口。作品の行きつく先は集合意識。」 16:9 / 74秒
全映像・全音をこのスクリプト内で手続き的に生成する（外部素材なし）。
usage:
  python make_buzz_essay.py stills 3 9 20 ...   # 指定秒のプレビュー静止画
  python make_buzz_essay.py render               # 本番書き出し
"""
import sys, os, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

f32 = np.float32
W, H, FPS, DUR = 1920, 1080, 24, 74.0
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_MP4 = os.path.join(HERE, "buzz_entrance_collective_16x9.mp4")
TMP = os.environ.get("BUZZ_TMP", HERE)
FONT = "C:/Windows/Fonts/BIZ-UDMinchoM.ttc"
rng = np.random.default_rng(7)

# ---------------------------------------------------------------- utilities
def ss(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)

def noise(h, w, cells, seed, interp=cv2.INTER_CUBIC, ch=None):
    r = np.random.default_rng(seed)
    if ch is None:
        ch = max(2, int(round(cells * h / w)))
    return cv2.resize(r.random((ch, max(2, cells))).astype(f32), (w, h), interpolation=interp)

def fbm(h, w, seed=0, octaves=((3, 1), (7, .5), (16, .25), (40, .12), (120, .06))):
    acc = np.zeros((h, w), f32); tot = 0
    for i, (c, a) in enumerate(octaves):
        acc += noise(h, w, c, seed * 31 + i) * a; tot += a
    acc -= acc.min(); acc /= acc.max() + 1e-6
    return acc

def noise1d(n, cells, seed):
    r = np.random.default_rng(seed)
    return cv2.resize(r.random((1, cells)).astype(f32), (n, 1), interpolation=cv2.INTER_CUBIC)[0]

def vgrad(h, w, top, bot, power=1.0):
    t = (np.linspace(0, 1, h, dtype=f32) ** power)[:, None]
    col = np.array(top, f32)[None] * (1 - t) + np.array(bot, f32)[None] * t
    return np.repeat(col[:, None, :], w, axis=1).astype(f32)

def paste(dst, rgb, a, x, y, op=1.0):
    h, w = a.shape; x = int(round(x)); y = int(round(y))
    x0, y0 = max(x, 0), max(y, 0); x1, y1 = min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if x1 <= x0 or y1 <= y0 or op <= 0: return
    sa = a[y0 - y:y1 - y, x0 - x:x1 - x, None] * op
    src = rgb if np.ndim(rgb) == 1 else rgb[y0 - y:y1 - y, x0 - x:x1 - x]
    dst[y0:y1, x0:x1] = dst[y0:y1, x0:x1] * (1 - sa) + src * sa

def add(dst, a, color, x, y, op=1.0):
    h, w = a.shape; x = int(round(x)); y = int(round(y))
    x0, y0 = max(x, 0), max(y, 0); x1, y1 = min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if x1 <= x0 or y1 <= y0 or op <= 0: return
    dst[y0:y1, x0:x1] += a[y0 - y:y1 - y, x0 - x:x1 - x, None] * np.array(color, f32) * op

def shadow(dst, a, x, y, op=0.35, blur=9, dx=8, dy=11):
    sh = cv2.GaussianBlur(a, (0, 0), blur)
    paste(dst, np.zeros(3, f32), sh, x + dx, y + dy, op)

def rotate(rgb, a, deg):
    h, w = a.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), deg, 1.0)
    c, s = abs(M[0, 0]), abs(M[0, 1])
    nw, nh = int(h * s + w * c) + 4, int(h * c + w * s) + 4
    M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
    r = cv2.warpAffine(rgb, M, (nw, nh), flags=cv2.INTER_LINEAR)
    al = cv2.warpAffine(a, M, (nw, nh), flags=cv2.INTER_LINEAR)
    return r, al

def zoom(img, s, cx=0.5, cy=0.5, dx=0.0, dy=0.0):
    M = np.array([[s, 0, (1 - s) * cx * W + dx], [0, s, (1 - s) * cy * H + dy]], f32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def torn(h, w, margin=6, amp=5.0, seed=0, cells=None):
    yy, xx = np.mgrid[0:h, 0:w].astype(f32)
    cx = cells or max(4, w // 10); cy = cells or max(4, h // 10)
    pl = noise1d(h, cy, seed) * amp; pr = noise1d(h, cy, seed + 1) * amp
    pt = noise1d(w, cx, seed + 2) * amp; pb = noise1d(w, cx, seed + 3) * amp
    fine = (np.random.default_rng(seed).random((h, w)).astype(f32) - .5) * 1.2
    d = np.minimum.reduce([xx - margin - pl[:, None], (w - 1 - margin - pr[:, None]) - xx,
                           yy - margin - pt[None, :], (h - 1 - margin - pb[None, :]) - yy]) + fine
    return np.clip(d + .5, 0, 1).astype(f32)

def sepia(rgb, seed=0, fade=0.15):
    h, w = rgb.shape[:2]
    g = rgb @ np.array([.3, .59, .11], f32)
    g = 0.12 + 0.76 * g
    g = g * (1 - fade) + fade * 0.75
    out = g[..., None] * np.array([1.0, .87, .70], f32) + np.array([.05, .035, .015], f32)
    yy, xx = np.mgrid[0:h, 0:w].astype(f32)
    v = 1 - 0.45 * (((xx / w - .5) * 1.6) ** 2 + ((yy / h - .5) * 1.6) ** 2)
    out *= np.clip(v, 0.4, 1)[..., None]
    out *= (0.9 + 0.1 * fbm(h, w, seed=seed + 40))[..., None]
    r = np.random.default_rng(seed)
    sc = np.zeros((h, w), f32)
    for _ in range(14):
        x = r.integers(0, w); cv2.line(sc, (int(x), 0), (int(x + r.integers(-20, 20)), h), float(r.uniform(.04, .12)), 1, cv2.LINE_AA)
    for _ in range(60):
        cv2.circle(sc, (int(r.integers(0, w)), int(r.integers(0, h))), int(r.integers(1, 3)), float(r.uniform(.05, .2)), -1, cv2.LINE_AA)
    out = out + sc[..., None] * 0.8
    return np.clip(out, 0, 1).astype(f32)

def photo_print(content, seed, border=22, deg=0.0, torn_edge=True):
    h, w = content.shape[:2]
    img = sepia(content, seed)
    H2, W2 = h + 2 * border, w + 2 * border
    card = np.ones((H2, W2, 3), f32) * np.array([.90, .87, .80], f32)
    card *= (0.94 + 0.06 * fbm(H2, W2, seed=seed + 7))[..., None]
    card[border:border + h, border:border + w] = img
    a = torn(H2, W2, margin=3, amp=6 if torn_edge else 1.5, seed=seed + 11)
    return rotate(card, a, deg) if deg else (card, a)

def supersample_poly(h, w, pts, k=4):
    m = np.zeros((h * k, w * k), np.uint8)
    cv2.fillPoly(m, [np.int32(np.array(pts) * k)], 255, cv2.LINE_AA)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(f32) / 255

# ---------------------------------------------------------------- base textures
YY, XX = np.mgrid[0:H, 0:W].astype(f32)
PAPER = fbm(H, W, seed=1)
_fib = noise(H, W, 900, 2, ch=60, interp=cv2.INTER_LINEAR)
PAPER_RGB = (np.array([.88, .85, .78], f32) * (0.86 + 0.14 * PAPER)[..., None]
             - (_fib[..., None] - .5) * 0.035).astype(f32)
VIGN = np.clip(1 - 0.42 * (((XX / W - .5) * 1.25) ** 2 + ((YY / H - .5) * 1.5) ** 2) * 1.6, 0.45, 1).astype(f32)
GRAIN = [cv2.GaussianBlur(rng.standard_normal((H, W)).astype(f32), (0, 0), 0.7) for _ in range(6)]

def make_moon(r, seed=5):
    s = int(r * 2 + 4); c = s / 2
    yy, xx = np.mgrid[0:s, 0:s].astype(f32)
    d = np.hypot(xx - c + .5, yy - c + .5)
    a = np.clip(r - d + .5, 0, 1)
    tex = fbm(s, s, seed=seed, octaves=((3, 1), (6, .6), (12, .3), (30, .15)))
    limb = np.sqrt(np.clip(1 - (d / r) ** 2, 0, 1))
    shade = (0.78 + 0.22 * tex) * (0.72 + 0.28 * limb)
    return (np.array([.95, .93, .86], f32) * shade[..., None]).astype(f32), a.astype(f32)

def make_glow(r, k=5):
    s = int(r * k * 2); c = s / 2
    yy, xx = np.mgrid[0:s, 0:s].astype(f32)
    d = np.hypot(xx - c, yy - c)
    return (0.55 * np.exp(-(d / (r * 1.5)) ** 2) + 0.18 * np.exp(-(d / (r * 3.6)) ** 2)).astype(f32)

MOON = {r: make_moon(r) for r in (46, 60, 70, 150)}
GLOW = {r: make_glow(r) for r in (46, 60, 70)}

def draw_moon(dst, cx, cy, r, op=1.0):
    g = GLOW[r]; add(dst, g, (.75, .78, .85), cx - g.shape[1] / 2, cy - g.shape[0] / 2, op * 0.6)
    rgb, a = MOON[r]; paste(dst, rgb, a, cx - a.shape[1] / 2, cy - a.shape[0] / 2, op)

def make_city(h, seed, bw=(30, 110), win=(14, 11), p=0.18, scale=1.0):
    r = np.random.default_rng(seed)
    a = np.zeros((h, W), f32); L = np.zeros((h, W), f32)
    x = 0
    while x < W:
        w = int(r.integers(*bw) * scale); bh = int(r.integers(int(h * .25), h - 6))
        a[h - bh:, x:x + w] = 1
        sy, sx = int(win[0] * scale), int(win[1] * scale)
        ww, wh = max(2, int(4 * scale)), max(2, int(5 * scale))
        for wy in range(h - bh + sy // 2 + 2, h - 4, sy):
            for wx in range(x + 4, x + w - 5, sx):
                if r.random() < p: L[wy:wy + wh, wx:wx + ww] = r.uniform(.4, 1)
        x += w + int(r.integers(0, 6))
    return a, L

CITY_NEAR = make_city(300, 3)
CITY_FAR = make_city(110, 4, bw=(14, 50), win=(7, 6), p=0.12, scale=0.55)
FLICK = np.random.default_rng(9).random((300, W)).astype(f32) * 6.28

# skies
NIGHT_SKY = vgrad(H, W, (.012, .017, .038), (.055, .072, .10), 1.3)
_st = np.zeros((H, W), f32); _r = np.random.default_rng(12)
for _ in range(260):
    _st[_r.integers(0, int(H * .6)), _r.integers(0, W)] = _r.uniform(.15, .6)
NIGHT_SKY += cv2.GaussianBlur(_st, (0, 0), .7)[..., None] * 2.2 * np.array([.8, .85, 1], f32)
_cl = fbm(H, W, seed=21, octaves=((2, 1), (5, .5), (11, .25), (24, .12)))
_cl = cv2.resize(cv2.resize(_cl, (W // 3, H)), (W, H))
DAY_SKY = vgrad(H, W, (.60, .68, .74), (.90, .88, .82), .9)
DAY_SKY = DAY_SKY * (1 - 0.35 * np.clip(_cl - .45, 0, 1)[..., None]) + np.clip(_cl - .5, 0, 1)[..., None] * .35
NIGHT_SKY = NIGHT_SKY + np.clip(_cl - .55, 0, 1)[..., None] * np.array([.05, .06, .08], f32)

def city_frame(t, night, moon=True):
    f = (NIGHT_SKY if night else DAY_SKY).copy()
    if night and moon: draw_moon(f, W * .74, H * .24, 60)
    hy = int(H * .70)
    a, L = CITY_FAR
    col = (.04, .05, .075) if night else (.66, .70, .72)
    paste(f, np.array(col, f32), a, 0, hy - a.shape[0])
    if night:
        add(f, L, (1, .8, .55), 0, hy - a.shape[0], 1.2)
        add(f, cv2.GaussianBlur(L, (0, 0), 4), (1, .75, .5), 0, hy - a.shape[0], 1.5)
    f[hy:] = f[hy:] * 0.3 + np.array((.03, .035, .05) if night else (.55, .58, .60), f32) * .7
    a, L = CITY_NEAR
    y0 = H - a.shape[0]
    paste(f, np.array((.012, .016, .026) if night else (.40, .44, .48), f32), a, 0, y0)
    if night:
        fl = L * (0.8 + 0.2 * np.sin(FLICK * 3 + t * 2.0))
        add(f, fl, (1, .78, .5), 0, y0, 1.1)
        add(f, cv2.GaussianBlur(L, (0, 0), 6), (1, .7, .45), 0, y0, 1.4)
    else:
        add(f, L, (-.08, -.08, -.06), 0, y0, 1.0)
    return f

def make_forest(night):
    f = (NIGHT_SKY if night else DAY_SKY).copy()
    if night: draw_moon(f, W * .30, H * .22, 46)
    layers = [(.50, 70, 5, 0), (.58, 80, 8, 0), (.69, 70, 13, 0), (.80, 45, 22, 1)]
    cd = [(.70, .74, .75), (.56, .62, .60), (.40, .47, .42), (.22, .27, .22)]
    cn = [(.065, .085, .12), (.045, .06, .085), (.028, .038, .055), (.012, .016, .022)]
    for i, (b, amp, cells, trees) in enumerate(layers):
        prof = H * b + (noise1d(W, cells, 50 + i) - .5) * 2 * amp
        if trees: prof -= np.abs(np.sin(np.arange(W) * .09)) * 26 * noise1d(W, 160, 70) + noise1d(W, 400, 71) * 18
        m = np.clip(YY - prof[None, :] + .5, 0, 1)[..., None]
        f = f * (1 - m) + np.array((cn if night else cd)[i], f32) * m
    return f.astype(f32)

FOREST = {False: make_forest(False), True: make_forest(True)}

# sea
HY = int(H * .56); HS = H - HY
_tex = noise(HS * 2, W * 2, 30, 31, ch=160, interp=cv2.INTER_LINEAR) * .6 + noise(HS * 2, W * 2, 70, 32, ch=400, interp=cv2.INTER_LINEAR) * .4
_jj = np.arange(HS, dtype=f32)
_mapy = np.repeat(((HS * 2 - 1) * (_jj / HS) ** .55)[:, None], W * 2, 1).astype(f32)
_mapx = np.repeat(np.arange(W * 2, dtype=f32)[None], HS, 0)
SEA_TEX = cv2.remap(_tex, _mapx, _mapy, cv2.INTER_LINEAR)
SEA_TEX = (SEA_TEX - SEA_TEX.min()) / (SEA_TEX.max() - SEA_TEX.min())
_persp = (_jj / HS)[:, None]

def sea_frame(t, night, moon_x=W * .62, moon_y=H * .25, far_city=False, figure=False):
    f = (NIGHT_SKY if night else DAY_SKY).copy()
    if night: draw_moon(f, moon_x, moon_y, 60)
    if far_city:
        a, L = CITY_FAR
        hh = 60; aa = cv2.resize(a, (W, hh)); LL = cv2.resize(L, (W, hh))
        paste(f, np.array((.04, .05, .07) if night else (.70, .73, .74), f32), aa, 0, HY - hh + 4)
        if night:
            add(f, LL * (0.8 + 0.2 * math.sin(t * 1.3)), (1, .8, .55), 0, HY - hh + 4, 1.4)
            add(f, cv2.GaussianBlur(LL, (0, 0), 3), (1, .75, .5), 0, HY - hh + 4, 1.6)
    off = int(t * 40) % W
    tex = SEA_TEX[:, off:off + W]
    if night:
        sea = (np.array([.015, .022, .035], f32) * (1 - tex[..., None]) + np.array([.07, .085, .11], f32) * tex[..., None])
        path = np.exp(-((XX[:HS] - moon_x) / (40 + _persp * 260)) ** 2) * np.clip((tex - .55) * 3, 0, 1)
        sea += path[..., None] * np.array([.75, .75, .7], f32) * (0.9 - .5 * _persp)[..., None]
    else:
        sea = (np.array([.42, .50, .55], f32) * (1 - tex[..., None]) + np.array([.74, .77, .77], f32) * tex[..., None])
        sea = sea * (0.85 + 0.15 * (1 - _persp))[..., None]
    f[HY:] = sea
    f[HY - 1:HY + 2] = f[HY - 1:HY + 2] * .7 + f[HY - 3:HY - 2].mean(0, keepdims=True) * .3
    return f

# room with window
WIN = (int(W * .31), int(H * .14), int(W * .69), int(H * .80))
def make_room(night):
    x0, y0, x1, y1 = WIN
    a = np.ones((H, W), f32); a[y0:y1, x0:x1] = 0
    fr = 16; mul = 9; cx = (x0 + x1) // 2; cy = (y0 + y1) // 2 - 40
    a[y0:y0 + fr, x0:x1] = 1; a[y1 - fr:y1, x0:x1] = 1; a[y0:y1, x0:x0 + fr] = 1; a[y0:y1, x1 - fr:x1] = 1
    a[y0:y1, cx - mul // 2:cx + mul // 2] = 1; a[cy - mul // 2:cy + mul // 2, x0:x1] = 1
    a = cv2.GaussianBlur(a, (0, 0), .8)
    if night:
        base = np.array([.045, .052, .075], f32) * (0.8 + .2 * PAPER)[..., None]
        light = np.exp(-(((XX - W * .5) / (W * .35)) ** 2 + ((YY - H * .55) / (H * .5)) ** 2))
        base = base + light[..., None] * np.array([.03, .035, .05], f32)
    else:
        base = PAPER_RGB * np.array([.92, .90, .86], f32)
        light = np.exp(-(((XX - W * .5) / (W * .4)) ** 2 + ((YY - H * .5) / (H * .6)) ** 2))
        base = base * (0.6 + 0.4 * light)[..., None]
    sill = np.zeros((H, W), f32); sill[y1:y1 + 22, x0 - 30:x1 + 30] = 1
    base = base * (1 - .25 * cv2.GaussianBlur(sill, (0, 0), 6)[..., None])
    return base.astype(f32), a

ROOM = {False: make_room(False), True: make_room(True)}

def curtain(dst, t, night, x0, x1, y0, y1, op=0.5):
    w, h = x1 - x0, y1 - y0
    yy, xx = np.mgrid[0:h, 0:w].astype(f32)
    sway = 10 * np.sin(t * .8 + yy / h * 2.2) * (yy / h)
    folds = 0.5 + 0.5 * np.sin((xx + sway) / w * 2 * math.pi * 5.5 + np.sin(xx / 37) * .6)
    a = (0.30 + 0.35 * folds) * np.clip((w - xx - sway * .5) / 40, 0, 1)
    col = np.array([.08, .09, .12] if night else [.97, .96, .92], f32)
    paste(dst, col, a.astype(f32), x0, y0, op)

def room_frame(t, night, outside):
    f = outside.copy()
    base, a = ROOM[night]
    f = f * (1 - a[..., None]) + base * a[..., None]
    x0, y0, x1, y1 = WIN
    curtain(f, t, night, x0 - 40, x0 + int((x1 - x0) * .32), y0 - 20, y1 + 10, .75 if not night else .6)
    return f

# --------------------------------------------------------------- text
def text_sprite(line, size, tracking=.10):
    font = ImageFont.truetype(FONT, size)
    adv = [font.getlength(c) for c in line]
    tw = int(sum(adv) + size * tracking * (len(line) - 1)) + size
    im = Image.new("L", (tw, int(size * 1.6)), 0); d = ImageDraw.Draw(im)
    x = size / 2
    for c, a in zip(line, adv):
        d.text((x, size * .25), c, font=font, fill=255); x += a + size * tracking
    return np.asarray(im, dtype=f32) / 255

CAPS = []  # (text, t0, t1, cx, cy, size, style)
def cap(text, t0, t1, cx=.5, cy=.80, size=54, style="light", align="center"):
    CAPS.append((text_sprite(text, size), t0, t1, cx, cy, style, align))

cap("なぜ、ある作品だけが知らない人にも届くのか。", 0.9, 5.7, cy=.54, size=56)
cap("人は、説明より先に反応するものがある。", 6.8, 16.0)
cap("身体の記憶。", 17.4, 30.0, cy=.79, style="ink")
cap("忘れていた風景。", 20.6, 30.0, cy=.855, style="ink")
cap("繰り返される物語。", 23.8, 30.0, cy=.92, style="ink")
cap("好きな作家の骨格を、飽きるまで借りる。", 31.4, 37.6, cy=.85)
cap("借りるのは見た目ではない。", 38.3, 44.3, cy=.84, cx=.56, style="ink")
cap("構図、余白、反復、温度。", 40.3, 44.3, cy=.91, cx=.56, style="ink")
cap("反復の先で、借りた骨格は自分の言葉になる。", 46.0, 57.4, cy=.82)
cap("バズは入口。", 60.0, 72.6, cx=.09, cy=.43, size=62, align="left")
cap("作品の行きつく先は、集合意識。", 64.2, 72.6, cx=.09, cy=.56, size=62, align="left")

def draw_caps(f, t):
    for spr, t0, t1, cx, cy, style, align in CAPS:
        if not (t0 <= t <= t1): continue
        op = ss(t0, t0 + .7, t) * (1 - ss(t1 - .7, t1, t))
        if op <= 0: continue
        h, w = spr.shape
        x = (W * cx - w / 2) if align == "center" else (W * cx - h * .3); y = H * cy - h / 2 + 8 * (1 - ss(t0, t0 + 1.0, t))
        band = cv2.GaussianBlur(cv2.dilate(spr, np.ones((25, 25), np.uint8)), (0, 0), 22)
        if style == "light":
            paste(f, np.array([0, 0, 0], f32), np.clip(band * .55, 0, .55), x, y, op)
            paste(f, np.array([.96, .95, .91], f32), spr, x, y, op)
        else:
            paste(f, np.array([.93, .90, .83], f32), np.clip(band * .7, 0, .7), x, y, op)
            paste(f, np.array([.10, .09, .08], f32), spr, x, y, op)

# --------------------------------------------------------------- scene 1 : night opening
def scene1(t):
    f = NIGHT_SKY * 0.8
    f = f.copy()
    draw_moon(f, W * .70, H * .26, 60, op=.25 + .75 * ss(1.0, 5.5, t))
    a, L = CITY_FAR; y = int(H * .92) - a.shape[0]
    paste(f, np.array([.01, .012, .02], f32), a, 0, y)
    add(f, L * (.8 + .2 * np.sin(FLICK[:a.shape[0]] * 2 + t * 1.5)), (1, .78, .5), 0, y, .9 * ss(2, 6, t))
    paste(f, np.array([.01, .012, .02], f32), np.ones((H - int(H * .92), W), f32), 0, int(H * .92))
    return zoom(f, 1.0 + 0.012 * t, .7, .3)

# --------------------------------------------------------------- scene 2 : contrasts
SHOTS = [("room", False, "city"), ("room", True, "city"), ("city", False), ("forest", True),
         ("sea", False), ("city", True), ("forest", False), ("sea", True),
         ("room", False, "forest"), ("room", True, "sea"), ("city", False), ("sea", True)]
S2_T0, S2_T1 = 6.0, 17.0
_durs = np.linspace(1.15, 0.75, len(SHOTS)); _durs = _durs / _durs.sum() * (S2_T1 - S2_T0)
SHOT_T = np.concatenate([[S2_T0], S2_T0 + np.cumsum(_durs)])

def outside(kind, night, t):
    if kind == "city": return city_frame(t, night)
    if kind == "forest": return FOREST[night]
    return sea_frame(t, night)

def render_shot(i, t):
    sh = SHOTS[i]; lt = t - SHOT_T[i]
    if sh[0] == "room": f = room_frame(t, sh[1], outside(sh[2], sh[1], t))
    else: f = outside(sh[0], sh[1], t)
    return zoom(f, 1.02 + 0.03 * lt, .5, .45)

def scene2(t):
    i = int(np.clip(np.searchsorted(SHOT_T, t, side="right") - 1, 0, len(SHOTS) - 1))
    f = render_shot(i, t)
    xf = 3 / FPS
    if i > 0 and t - SHOT_T[i] < xf:
        k = (t - SHOT_T[i]) / xf
        f = render_shot(i - 1, t) * (1 - k) + f * k
    return f

# --------------------------------------------------------------- collage pieces
def _fig_photo():
    c = cv2.resize(sea_frame(3.0, False), (640, 460), interpolation=cv2.INTER_AREA)
    c = c[:, 30:590].copy()
    h, w = c.shape[:2]
    k = 4; m = np.zeros((h * k, w * k), np.uint8)
    body = [(.27, 1.0), (.30, .84), (.36, .77), (.46, .73), (.475, .64), (.565, .64), (.58, .73), (.68, .77), (.74, .84), (.77, 1.0)]
    cv2.fillPoly(m, [np.int32([(x * w * k, y * h * k) for x, y in body])], 255, cv2.LINE_AA)
    cv2.ellipse(m, (int(w * .52 * k), int(h * .565 * k)), (int(w * .052 * k), int(h * .085 * k)), 0, 0, 360, 255, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 3)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(f32)[..., None] / 255
    c = c * (1 - m) + np.array([.08, .08, .09], f32) * m
    return photo_print(c, 101, deg=-3.0)

def _window_photo():
    c = cv2.resize(room_frame(2.0, True, sea_frame(2.0, True)), (480, 270), interpolation=cv2.INTER_AREA)
    c = cv2.resize(c[:, 90:390], (300, 380))
    return photo_print(c * 1.6, 202, border=16, deg=4.0)

def _net(size=520, seed=3, ink=(.12, .11, .10)):
    k = 2; S = size * k
    m = np.zeros((S, S), np.uint8)
    for i in range(-S, 2 * S, 26 * k):
        cv2.line(m, (i, 0), (i + S, S), 255, 2 * k, cv2.LINE_AA)
        cv2.line(m, (i, S), (i + S, 0), 255, 2 * k, cv2.LINE_AA)
    yy, xx = np.mgrid[0:S, 0:S].astype(f32)
    mx = xx + 9 * k * np.sin(yy / (60 * k)) ; my = yy + 14 * k * np.sin(xx / (90 * k)) + 20 * k * (xx / S - .5) ** 2 * 4
    m = cv2.remap(m, mx.astype(f32), my.astype(f32), cv2.INTER_LINEAR)
    m = cv2.resize(m, (size, size), interpolation=cv2.INTER_AREA).astype(f32) / 255
    a = m * torn(size, size, margin=10, amp=14, seed=seed) * .85
    return np.ones((size, size, 3), f32) * np.array(ink, f32), a

def _moon_cut(r=150):
    rgb, a = MOON[r]
    rgb = rgb * np.array([1, .97, .9], f32)
    s = a.shape[0]
    a = a * np.clip(torn(s, s, margin=0, amp=0, seed=4) + 1, 0, 1)
    return rgb, a

def _strip(kind, w, h, seed, night=False):
    if kind == "sea":
        src = sea_frame(5.0, night)[HY - 40:HY - 40 + int(H * .3)]
    else:
        src = np.zeros((H, W, 3), f32) + np.array([.93, .92, .88], f32)
        curtain(src, 1.0, True, 0, W, 0, H, 1.0)
        src = src * .5 + PAPER_RGB * .5
    c = cv2.resize(src, (w, h), interpolation=cv2.INTER_AREA)
    return c, torn(h, w, margin=4, amp=10, seed=seed)

FIG = _fig_photo()
WINP = _window_photo()
NET = _net()
MOONC = _moon_cut()
SEAS = _strip("sea", 900, 170, 301)
CURT = _strip("curt", 230, 720, 302)
SEAS = rotate(*SEAS, 1.5)

COLLAGE = [  # sprite, x, y, arrival
    (CURT, 150, 50, 16.6), (FIG, 330, 100, 17.0), (NET, 820, 50, 18.8), (MOONC, 1250, 90, 20.0),
    (SEAS, 500, 540, 21.6), (WINP, 1360, 360, 23.4)]

def scene3(t):
    f = PAPER_RGB.copy()
    for (rgb, a), x, y, ta in COLLAGE:
        k = ss(ta, ta + 1.1, t)
        if k <= 0: continue
        dy = 30 * (1 - k)
        drift = 6 * math.sin(t * .3 + x)
        shadow(f, a, x + drift, y + dy, op=.3 * k)
        paste(f, rgb, a, x + drift, y + dy, k)
    return zoom(f, 1.0 + 0.006 * (t - 16.5), .5, .45)

# --------------------------------------------------------------- scene 4a : iterations + skeleton
TW, TH, TG = 500, 281, 40
TX0, TY0 = (W - (3 * TW + 2 * TG)) // 2, 95
VARIANTS = [(.67, .30, .30, .55), (.33, .30, .62, .67), (.70, .62, .25, .33), (.30, .64, .55, .50), (.66, .33, .40, .62), (.50, .25, .33, .67)]

def mini(var, seed):
    mx, my, wx, hz = var
    c = vgrad(TH, TW, (.03, .04, .07), (.10, .12, .16))
    c[int(TH * hz):] = np.array([.03, .04, .055], f32)
    cv2.line(c, (0, int(TH * hz)), (TW, int(TH * hz)), (.2, .22, .26), 1, cv2.LINE_AA)
    g = make_glow(14, 4); add(c, g, (.7, .74, .8), TW * mx - g.shape[1] / 2, TH * my - g.shape[0] / 2, .7)
    cv2.circle(c, (int(TW * mx), int(TH * my)), 14, (.86, .88, .9), -1, cv2.LINE_AA)
    x0 = int(TW * wx) - 60
    cv2.rectangle(c, (x0, int(TH * .18)), (x0 + 120, int(TH * .82)), (.55, .5, .45), 2, cv2.LINE_AA)
    cv2.line(c, (x0 + 60, int(TH * .18)), (x0 + 60, int(TH * .82)), (.55, .5, .45), 1, cv2.LINE_AA)
    c *= (0.85 + 0.3 * fbm(TH, TW, seed=seed))[..., None]
    return c

MINIS = [mini(v, 400 + i) for i, v in enumerate(VARIANTS)]
NOISEI = [cv2.GaussianBlur(np.random.default_rng(500 + i).random((TH, TW, 3)).astype(f32), (0, 0), 6) * .5 for i in range(6)]

def scene4a(t):
    f = vgrad(H, W, (.07, .065, .06), (.035, .033, .03)) * (0.85 + 0.15 * PAPER)[..., None]
    for i in range(6):
        cx, cy = TX0 + (i % 3) * (TW + TG), TY0 + (i // 3) * (TH + TG)
        t0 = 30.6 + i * .55
        k = ss(t0, t0 + 1.6, t)
        sig = 0.5 + 12 * (1 - k)
        img = cv2.GaussianBlur(MINIS[i], (0, 0), sig) * k + NOISEI[i] * (1 - k)
        img = img * (0.3 + 0.7 * ss(t0 - .3, t0 + .2, t))
        f[cy - 2:cy + TH + 2, cx - 2:cx + TW + 2] = .14
        f[cy:cy + TH, cx:cx + TW] = img
        # shared skeleton guide lines (red pencil)
        g = ss(33.0 + i * .12, 35.5 + i * .12, t)
        if g > 0:
            lay = np.zeros((TH, TW), f32)
            for xv in (TW // 3, 2 * TW // 3):
                cv2.line(lay, (xv, 0), (xv, int(TH * g)), 1, 1, cv2.LINE_AA)
            for yv in (TH // 3, 2 * TH // 3):
                cv2.line(lay, (0, yv), (int(TW * g), yv), 1, 1, cv2.LINE_AA)
            cv2.rectangle(lay, (18, 14), (TW - 18, TH - 14), .6, 1, cv2.LINE_AA)
            paste(f, np.array([.85, .32, .26], f32), lay, cx, cy, .75 * g)
    return zoom(f, 1.0 + .004 * (t - 30.5), .5, .4)

# --------------------------------------------------------------- scene 4b : book / cut / collage / T-shirt
def _book():
    bw, bh = 540, 690
    pg = np.ones((bh, bw, 3), f32) * np.array([.89, .85, .74], f32)
    pg *= (0.9 + 0.1 * fbm(bh, bw, seed=601))[..., None]
    r = np.random.default_rng(602)
    ill = sea_frame(4.0, True, moon_x=W * .5, moon_y=H * .28)
    ill = cv2.resize(ill[:, 300:1620], (420, 330), interpolation=cv2.INTER_AREA)
    g = ill @ np.array([.3, .59, .11], f32)
    yy, xx = np.mgrid[0:330, 0:420]
    dots = ((np.sin(xx * .9) * np.sin(yy * .9) * .5 + .5) < g * 1.8).astype(f32)
    ill = np.array([.89, .85, .74], f32) * (1 - .8 * (1 - dots[..., None]))
    pg[60:390, 70:490] = ill
    for row, y in enumerate(range(430, bh - 50, 24)):
        x = 70
        end = 490 if r.random() > .15 else r.integers(200, 480)
        while x < end:
            cw = int(r.integers(10, 15))
            pg[y:y + 12, x:x + cw] = pg[y:y + 12, x:x + cw] * .45 + .05
            x += cw + int(r.integers(2, 5)) + (12 if r.random() < .08 else 0)
    gut = np.clip(1 - np.arange(bw, dtype=f32) / 60, 0, 1)
    pg *= (1 - .3 * gut)[None, :, None]
    return pg, torn(bh, bw, margin=2, amp=2, seed=603), (70, 60, 490, 390)

BOOK, BOOKA, CUT = _book()
CUTP = (BOOK[CUT[1]:CUT[3], CUT[0]:CUT[2]].copy(), torn(CUT[3] - CUT[1], CUT[2] - CUT[0], margin=1, amp=3, seed=610))
NET2 = _net(300, 11)
SEA2 = (cv2.resize(SEAS[0], (520, 120)), cv2.resize(SEAS[1], (520, 120)))
FIG2 = (cv2.resize(FIG[0], (FIG[0].shape[1] * 2 // 5, FIG[0].shape[0] * 2 // 5)), cv2.resize(FIG[1], (FIG[1].shape[1] * 2 // 5, FIG[1].shape[0] * 2 // 5)))
MOON2 = (cv2.resize(MOONC[0], (150, 150)), cv2.resize(MOONC[1], (150, 150)))
GW, GH = 640, 560

def _tshirt():
    w, h = 760, 820
    pts = [(.30, .02), (.42, .07), (.58, .07), (.70, .02), (.98, .16), (.90, .36), (.78, .31), (.79, .99), (.21, .99), (.22, .31), (.10, .36), (.02, .16)]
    a = supersample_poly(h, w, [(x * w, y * h) for x, y in pts])
    col = np.cv = cv2.GaussianBlur(fbm(h, w, seed=701, octaves=((3, 1), (6, .5), (14, .2))), (0, 0), 6)
    rgb = np.array([.93, .92, .89], f32) * (0.82 + 0.2 * col)[..., None]
    neck = np.zeros((h, w), f32); cv2.ellipse(neck, (w // 2, int(h * .05)), (int(w * .09), int(h * .05)), 0, 0, 180, 1, 6, cv2.LINE_AA)
    rgb *= (1 - .25 * neck)[..., None]
    return rgb.astype(f32), a, (0.82 + 0.2 * col)

TSH = _tshirt()

def group_layer(t):
    P = np.zeros((GH, GW, 3), f32); A = np.zeros((GH, GW), f32)
    def put(spr, x, y, ta, sx=0, sy=0):
        k = ss(ta, ta + .9, t)
        if k <= 0: return
        rgb, a = spr
        x += sx * (1 - k); y += sy * (1 - k)
        paste(P, rgb, a, x, y, k)
        paste(A[..., None], np.ones(1, f32), a, x, y, k)
    put(SEA2, 60, 330, 38.6, 0, 120)
    put(NET2, 300, 40, 39.1, 200, -60)
    put(CUTP, 40, 40, 38.0, -600, 120)
    put(MOON2, 420, 70, 39.6, 120, -100)
    put(FIG2, 220, 260, 40.1, 0, 200)
    return P, A

def scene4b(t):
    f = PAPER_RGB * np.array([.82, .80, .76], f32)
    bx, by = 80, 95
    shadow(f, BOOKA, bx, by, .35)
    paste(f, BOOK, BOOKA, bx, by)
    k = ss(38.0, 38.4, t)
    if k > 0:  # hole where the piece was cut
        x0, y0, x1, y1 = CUT
        hole = np.zeros_like(BOOKA); hole[y0:y1, x0:x1] = CUTP[1]
        paste(f, PAPER_RGB[by:by + hole.shape[0], bx:bx + hole.shape[1]] * .62, hole, bx, by, k)
        shadow(f, hole, bx - 6, by - 7, .25 * k, blur=3, dx=0, dy=0)
    P, A = group_layer(t)
    mv = ss(41.0, 42.6, t)
    ts = ss(40.4, 41.6, t)
    tx, ty = 1180, 70
    if ts > 0:
        shadow(f, TSH[1], tx, ty, .3 * ts, blur=14)
        paste(f, TSH[0], TSH[1], tx, ty, ts)
    s = 1 - .42 * mv
    gx = 690 * (1 - mv) + (tx + 760 / 2 - GW * s / 2) * mv
    gy = 130 * (1 - mv) + (ty + 210) * mv
    gw, gh = int(GW * s), int(GH * s)
    Ps, As = cv2.resize(P, (gw, gh)), cv2.resize(A, (gw, gh))
    if mv < 1: shadow(f, As, gx, gy, .3 * (1 - mv))
    if mv > 0:  # printed: tint with fabric shading
        sh = TSH[2][int(gy - ty):int(gy - ty) + gh, int(gx - tx):int(gx - tx) + gw]
        if sh.shape == As.shape: Ps = Ps * (1 - mv * (1 - sh[..., None]))
    reg = f[int(gy):int(gy) + gh, int(gx):int(gx) + gw]
    hh, ww = reg.shape[:2]
    reg[:] = reg * (1 - As[:hh, :ww, None] * (1 - .12 * mv)) + Ps[:hh, :ww] * (1 - .12 * mv)
    return zoom(f, 1.0 + .004 * (t - 37.5), .5, .4)

# --------------------------------------------------------------- scene 5 : day and night coexist
def scene5(t):
    lt = t - 44.0
    day = sea_frame(t, False, far_city=True)
    night = sea_frame(t, True, moon_x=W * .70, moon_y=H * .22, far_city=True)
    width = 3 + 900 * ss(48.0, 57.0, t) ** 1.4
    nz = (noise(H, W, 6, 801) - .5) * (60 + 500 * ss(47, 57, t))
    edge = XX - W * (.5 - .12 * ss(44, 58, t)) + nz
    m = np.clip(.5 + edge / (2 * width), 0, 1)
    m = m * m * (3 - 2 * m)
    m = 0.15 + 0.7 * m if t > 55 and False else m
    f = day * (1 - m[..., None]) + night * m[..., None]
    seam = np.exp(-(edge / 3.0) ** 2) * (1 - ss(46.5, 50, t))
    f += seam[..., None] * np.array([.6, .58, .52], f32)
    # torn paper frame: the world is a collage
    frame_a = 1 - torn(H, W, margin=34, amp=14, seed=820)
    f = f * (1 - frame_a[..., None]) + PAPER_RGB * .85 * frame_a[..., None]
    return zoom(f, 1.04 - .03 * ss(44, 58, t), .5, .5)

# --------------------------------------------------------------- scene 6 : dark, moon, window, far lights
W6 = (1250, 160, 1710, 880)
def scene6(t):
    f = vgrad(H, W, (.02, .022, .03), (.012, .014, .02)) * (0.85 + .15 * PAPER)[..., None]
    x0, y0, x1, y1 = W6
    sky = vgrad(y1 - y0, x1 - x0, (.03, .04, .07), (.07, .085, .11))
    f[y0:y1, x0:x1] = sky
    draw_moon(f, 1555, 320, 46, op=ss(59.5, 62.5, t))
    a, L = CITY_FAR
    ac = cv2.resize(a[:, :x1 - x0 + 200], (x1 - x0, 50)); Lc = cv2.resize(L[:, :x1 - x0 + 200], (x1 - x0, 50))
    paste(f, np.array([.02, .025, .035], f32), ac, x0, y1 - 80)
    paste(f, np.array([.02, .025, .035], f32), np.ones((30, x1 - x0), f32), x0, y1 - 30)
    add(f, Lc * (.75 + .25 * math.sin(t * 1.1)), (1, .8, .55), x0, y1 - 80, 1.6)
    add(f, cv2.GaussianBlur(Lc, (0, 0), 3), (1, .75, .5), x0, y1 - 80, 2.0)
    fr = np.zeros((H, W), f32)
    cv2.rectangle(fr, (x0, y0), (x1, y1), 1, 12); cv2.line(fr, ((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1), 1, 7)
    cv2.line(fr, (x0, (y0 + y1) // 2 - 40), (x1, (y0 + y1) // 2 - 40), 1, 7)
    paste(f, np.array([.035, .038, .05], f32), cv2.GaussianBlur(fr, (0, 0), 1), 0, 0)
    curtain(f, t, True, x0 - 30, x0 + 150, y0 - 20, y1 + 10, .7)
    return zoom(f, 1.0 + .025 * ss(58, 74, t), .72, .45)

# --------------------------------------------------------------- timeline
SCENES = [(0.0, 6.4, scene1), (6.0, 17.6, scene2), (16.8, 31.0, scene3), (30.2, 38.0, scene4a),
          (37.4, 45.0, scene4b), (44.0, 59.6, scene5), (58.0, DUR, scene6)]

def frame_at(t, fi=0):
    act = [(s, e, fn) for s, e, fn in SCENES if s <= t < e] or [SCENES[-1]]
    if len(act) == 1: f = act[0][2](t)
    else:
        (s0, e0, f0), (s1, e1, f1) = act[0], act[1]
        k = ss(s1, e0, t); f = f0(t) * (1 - k) + f1(t) * k
    f = f * (0.92 + 0.08 * PAPER[..., None])
    f = f * VIGN[..., None]
    f = f * np.array([1.0, .99, .965], f32) + .010
    draw_caps(f, t)
    f += GRAIN[fi % 6][..., None] * .016
    f *= ss(0, 1.2, t) * (1 - ss(DUR - 1.6, DUR - .05, t))
    return np.clip(f * 255 + .5, 0, 255).astype(np.uint8)

# --------------------------------------------------------------- audio
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)

def make_audio(path):
    from scipy.signal import fftconvolve, butter, sosfilt
    SR = 48000; N = int(SR * DUR); tt = np.arange(N) / SR
    L = np.zeros(N); R = np.zeros(N); r = np.random.default_rng(99)
    def env_arr(n, att, rel):
        e = np.ones(n); a = min(int(att * SR), n); rr = min(int(rel * SR), n)
        e[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
        e[n - rr:] *= np.cos(np.linspace(0, np.pi / 2, rr)) ** 2
        return e
    def pad(note, t0, t1, amp, att=3.0, rel=4.0, pan=0.0, bright=.12):
        i0, i1 = int(t0 * SR), min(int((t1 + rel) * SR), N); n = i1 - i0
        x = tt[i0:i1] - t0; f = midi(note); s = np.zeros(n)
        for d in (-.0035, 0, .0041):
            s += np.sin(2 * np.pi * f * (1 + d) * x + r.uniform(0, 6.28))
            s += bright * np.sin(2 * np.pi * 2 * f * (1 + d) * x + r.uniform(0, 6.28))
        s *= (1 + .18 * np.sin(2 * np.pi * r.uniform(.07, .15) * x + r.uniform(0, 6)))
        e = env_arr(n, att, rel); e2 = np.ones(n); e2[int((t1 - t0) * SR):] = 0
        tail = env_arr(n, att, 0.001); s *= amp / 3 * tail
        k = int((t1 - t0) * SR)
        if k < n: s[k:] *= np.exp(-np.arange(n - k) / (rel * SR / 3))
        L[i0:i1] += s * (1 - pan) / 2 * 2 ** .5; R[i0:i1] += s * (1 + pan) / 2 * 2 ** .5
    def bell(note, t0, amp, decay=3.0, pan=0.0):
        i0 = int(t0 * SR); n = min(int(decay * 3 * SR), N - i0)
        if n <= 0: return
        x = np.arange(n) / SR; f = midi(note)
        s = (np.sin(2 * np.pi * f * x) + .35 * np.sin(2 * np.pi * f * 2.0 * x) * np.exp(-x * 2) + .12 * np.sin(2 * np.pi * f * 3.01 * x) * np.exp(-x * 4))
        s *= np.exp(-x / decay) * np.clip(x / .012, 0, 1) * amp
        L[i0:i0 + n] += s * (1 - pan) / 2 * 2 ** .5; R[i0:i0 + n] += s * (1 + pan) / 2 * 2 ** .5
    def breath(t0, t1, amp, lo, hi, att=2.5, rel=2.5):
        i0, i1 = int(t0 * SR), min(int(t1 * SR), N); n = i1 - i0
        sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos")
        for ch, A in ((0, L), (1, R)):
            s = sosfilt(sos, r.standard_normal(n)) * env_arr(n, att, rel) * amp
            A[i0:i1] += s
    # S1 drone
    for nt, a in ((38, .16), (45, .10), (26, .10)): pad(nt, 0.0, 6.6, a, att=4, rel=3)
    breath(0.3, 6.5, .05, 300, 1400, 3, 2)
    # S2 Bm9 -> Gmaj7#11, soft bells on cuts
    for nt, a, p in ((35, .12, 0), (47, .10, -.3), (54, .07, .3), (57, .06, -.2), (61, .05, .4)): pad(nt, 6.0, 11.5, a, 2.5, 2.5, p)
    for nt, a, p in ((31, .12, 0), (43, .10, .2), (50, .08, -.3), (54, .06, .3), (61, .05, -.4), (64, .035, .4)): pad(nt, 11.2, 17.0, a, 2.0, 3.0, p)
    pent = [74, 76, 78, 81, 83, 86]
    for i, ts in enumerate(SHOT_T[:-1]):
        bell(pent[(i * 3) % 6], ts, .045, 1.6, (-1) ** i * .5)
    # S3 Dadd9 -> Gmaj9
    for nt, a, p in ((38, .13, 0), (45, .10, -.3), (52, .07, .3), (54, .06, -.2), (57, .05, .3), (64, .03, 0)): pad(nt, 16.6, 23.5, a, 3, 3, p)
    for nt, a, p in ((31, .12, 0), (43, .10, .3), (50, .07, -.3), (54, .06, .2), (57, .05, -.2), (59, .04, .4)): pad(nt, 23.0, 30.8, a, 3, 3, p)
    breath(17, 30, .03, 500, 3000, 4, 4)
    for ts, nt in ((17.4, 78), (20.6, 76), (23.8, 74)): bell(nt, ts, .05, 3.0, 0)
    # S4 Em9 -> Asus with repeating motif
    for nt, a, p in ((40, .12, 0), (47, .09, -.3), (50, .07, .3), (54, .06, -.2), (55, .04, .3)): pad(nt, 30.4, 37.6, a, 2.5, 3, p)
    for nt, a, p in ((33, .11, 0), (45, .10, .2), (52, .07, -.3), (59, .05, .3), (62, .04, -.3)): pad(nt, 37.4, 44.6, a, 2.5, 3, p)
    motif = [74, 69, 66, 76, 69, 66, 71, 69]
    step = 60 / 84 / 2
    k = 0; ts = 31.0
    while ts < 52.5:
        amp = .035 * ss(30.8, 34, ts) * (1 - .7 * ss(46, 52.5, ts)) + .01
        bell(motif[k % 8] - (0 if ts < 37.5 else 0), ts, amp, 1.1, .45 * math.sin(k * .7))
        k += 1; ts += step
    # S5 Gmaj7 -> Bm11 -> A6sus swell
    for nt, a, p in ((31, .12, 0), (43, .10, .2), (50, .07, -.3), (54, .06, .3), (59, .05, -.2), (62, .04, .3)): pad(nt, 44.4, 49.6, a, 2.5, 3, p)
    for nt, a, p in ((35, .11, 0), (47, .09, -.2), (54, .07, .3), (57, .06, -.3), (61, .05, .2), (64, .04, -.3)): pad(nt, 49.4, 53.8, a, 2, 3, p)
    for nt, a, p in ((33, .12, 0), (45, .11, .2), (52, .08, -.3), (57, .07, .3), (59, .06, -.2), (64, .05, .3), (69, .04, 0), (76, .03, -.4), (81, .022, .4)):
        pad(nt, 53.6, 58.8, a, 4.0, 2.5, p, bright=.2)
    breath(52, 59, .045, 800, 5000, 5, 1.5)
    # S6 Dmaj9 resolve
    for nt, a, p in ((26, .09, 0), (38, .12, 0), (45, .10, -.3), (54, .07, .3), (57, .06, -.2), (61, .05, .3), (64, .04, -.3)):
        pad(nt, 58.4, 72.5, a, 3.0, 4.0, p)
    bell(74, 60.0, .07, 4.0, -.2); bell(81, 64.2, .055, 4.5, .25); bell(78, 64.25, .03, 4.5, -.25)
    breath(58.5, 73, .025, 300, 1200, 4, 5)
    # reverb
    ir_n = int(4.0 * SR); x = np.arange(ir_n) / SR
    irL = r.standard_normal(ir_n) * np.exp(-x / 1.1); irR = r.standard_normal(ir_n) * np.exp(-x / 1.1)
    irL /= np.sqrt((irL ** 2).sum()); irR /= np.sqrt((irR ** 2).sum())
    wL = fftconvolve(L, irL)[:N]; wR = fftconvolve(R, irR)[:N]
    outL = L * .55 + wL * .6; outR = R * .55 + wR * .6
    sos = butter(2, 30, btype="high", fs=SR, output="sos")
    outL, outR = sosfilt(sos, outL), sosfilt(sos, outR)
    fade = np.ones(N); fi = int(.8 * SR); fo = int(3.5 * SR)
    fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
    st = np.stack([outL, outR], 1) * fade[:, None]
    st = st / np.abs(st).max() * .80
    from scipy.io import wavfile
    wavfile.write(path, SR, (st * 32767).astype(np.int16))

# --------------------------------------------------------------- main
def ffmpeg_exe():
    import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "render"
    if mode == "stills":
        ts = [float(x) for x in sys.argv[2:]]
        thumbs = []
        for t in ts:
            img = frame_at(t, int(t * FPS))
            cv2.imwrite(os.path.join(TMP, f"still_{t:05.1f}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            thumbs.append(cv2.resize(img, (640, 360), interpolation=cv2.INTER_AREA))
        while len(thumbs) % 3: thumbs.append(np.zeros_like(thumbs[0]))
        rows = [np.hstack(thumbs[i:i + 3]) for i in range(0, len(thumbs), 3)]
        cv2.imwrite(os.path.join(TMP, "contact.png"), cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR))
        print("ok")
    else:
        wav = os.path.join(TMP, "buzz_audio.wav")
        make_audio(wav); print("audio ok", flush=True)
        cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT_MP4]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n = int(DUR * FPS)
        for i in range(n):
            p.stdin.write(frame_at(i / FPS, i).tobytes())
            if i % 120 == 0: print(f"frame {i}/{n}", flush=True)
        p.stdin.close(); p.wait(); print("done", OUT_MP4)
