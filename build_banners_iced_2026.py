"""
Generate Teatower 'Thés Glacés 2026' banners in 5 formats.

Output: marketing/banners_iced_tea_2026/
  - homepage_2432x788.jpg
  - homepage_1392x752.jpg
  - category_1785x893.jpg
  - keyword_1320x660.jpg
  - skyscraper_480x1800.jpg
"""
from __future__ import annotations
import os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import numpy as np

random.seed(42)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "marketing", "banners_iced_tea_2026")
SRC_DIR = os.path.join(OUT_DIR, "source_packs")
os.makedirs(OUT_DIR, exist_ok=True)

# Selected iced-tea collection 2026 — blue iced-tea pouches from Shopify
PACK_FILES = [
    ("01_vergers_ete_v2.png", "Vergers d'Été", True),    # has black bg → keying
    ("02_peche_vigne.jpg", "Pêche de Vigne BIO", False),
    ("03_passion_exotique.jpg", "Passion Exotique", False),
    ("04_gourmandise.jpg", "Gourmandise Glacée", False),
    ("05_marrakech_sunset.jpg", "Marrakech Sunset BIO", False),
]

FONTS = "C:/Windows/Fonts"
F_BOLD = os.path.join(FONTS, "segoeuib.ttf")
F_REG = os.path.join(FONTS, "segoeui.ttf")
F_LIGHT = os.path.join(FONTS, "segoeuil.ttf")
F_ITALIC = os.path.join(FONTS, "georgiai.ttf")  # serif italic for elegance


def font(path, size):
    return ImageFont.truetype(path, size)


# Teatower iced palette
NAVY = (24, 47, 76)         # deep navy (text on light, claim baseline)
TEAL = (44, 156, 167)       # teatower teal
ICE_LIGHT = (200, 240, 245) # pale ice
ICE_MID = (110, 200, 215)   # mid turquoise
GOLD = (220, 174, 92)       # accent amber
WHITE = (255, 255, 255)


def load_pack(fn: str, has_dark_bg: bool) -> Image.Image:
    """Load a packshot, key out background (white or black), return RGBA cropped to content."""
    path = os.path.join(SRC_DIR, fn)
    img = Image.open(path).convert("RGBA")
    if has_dark_bg:
        img = key_out_dark(img)
    else:
        img = key_out_white(img)
    return tighten_to_content(img)


def key_out_white(img: Image.Image, thresh: int = 12) -> Image.Image:
    """
    Floodfill near-white from each corner to remove ONLY the external white background,
    preserving white regions inside the packaging.
    """
    img = img.convert("RGB").copy()
    w, h = img.size
    sentinel = (255, 0, 255)
    for pt in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        try:
            ImageDraw.floodfill(img, pt, sentinel, thresh=thresh)
        except Exception:
            pass
    arr = np.array(img)
    mask = (arr[:, :, 0] == 255) & (arr[:, :, 1] == 0) & (arr[:, :, 2] == 255)
    alpha = np.where(mask, 0, 255).astype(np.uint8)
    # restore non-sentinel pixels: where mask -> use white (cosmetic), else keep RGB
    arr[mask] = [255, 255, 255]
    rgba = np.dstack([arr, alpha])
    return Image.fromarray(rgba, mode="RGBA")


def key_out_dark(img: Image.Image, thresh: int = 60) -> Image.Image:
    """Floodfill near-black from corners (Vergers d'Été case)."""
    img = img.convert("RGB").copy()
    w, h = img.size
    sentinel = (255, 0, 255)
    for pt in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        try:
            ImageDraw.floodfill(img, pt, sentinel, thresh=thresh)
        except Exception:
            pass
    arr = np.array(img)
    mask = (arr[:, :, 0] == 255) & (arr[:, :, 1] == 0) & (arr[:, :, 2] == 255)
    alpha = np.where(mask, 0, 255).astype(np.uint8)
    arr[mask] = [255, 255, 255]
    rgba = np.dstack([arr, alpha])
    return Image.fromarray(rgba, mode="RGBA")


def tighten_to_content(img: Image.Image) -> Image.Image:
    """Crop to alpha bbox + add small margin for shadow."""
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    w, h = img.size
    pad = max(8, int(0.03 * max(w, h)))
    canvas = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    canvas.paste(img, (pad, pad))
    return canvas


def add_shadow(pack: Image.Image, blur: int = 18, offset=(8, 14), opacity: int = 120) -> Image.Image:
    """Composite a soft drop shadow under the packshot."""
    base = pack
    alpha = base.split()[-1]
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", base.size, (0, 0, 0, opacity))
    shadow.paste(shadow_layer, (0, 0), alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    canvas = Image.new("RGBA", (base.size[0] + offset[0] * 2, base.size[1] + offset[1] * 2), (0, 0, 0, 0))
    canvas.paste(shadow, (offset[0], offset[1]), shadow)
    canvas.paste(base, (0, 0), base)
    return canvas


def vertical_gradient(size, top, bottom):
    w, h = size
    grad = Image.new("RGB", (1, h), top)
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        grad.putpixel((0, y), (r, g, b))
    return grad.resize(size)


def diagonal_gradient(size, c1, c2):
    """Soft diagonal gradient for a more dynamic background."""
    w, h = size
    base = Image.new("RGB", (w, h), c1)
    overlay = Image.new("RGBA", (w, h), c2 + (0,))
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    # gradient mask: diagonal
    for i in range(0, w + h, 2):
        v = int(255 * i / (w + h))
        md.line([(i, 0), (0, i)], fill=v, width=2)
    overlay.putalpha(mask)
    base.paste(overlay, (0, 0), overlay)
    return base


def build_background(size):
    """Ice-tea palette: deep teal -> ice-mint with soft light blobs."""
    w, h = size
    bg = vertical_gradient(size, (18, 80, 110), (110, 200, 215))
    # soft light blobs (sun/highlights)
    bg = bg.convert("RGBA")
    blobs = Image.new("RGBA", size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(blobs)
    for _ in range(int(0.0006 * w * h ** 0.5) + 6):
        cx = random.randint(0, w)
        cy = random.randint(0, h)
        r = random.randint(int(min(w, h) * 0.08), int(min(w, h) * 0.30))
        a = random.randint(18, 55)
        bd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, a))
    blobs = blobs.filter(ImageFilter.GaussianBlur(int(min(w, h) * 0.05)))
    bg = Image.alpha_composite(bg, blobs)
    # subtle vignette
    vignette = Image.new("L", size, 0)
    vd = ImageDraw.Draw(vignette)
    vd.rectangle([0, 0, w, h], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(int(min(w, h) * 0.2)))
    return bg.convert("RGB")


def fit_pack(pack: Image.Image, target_h: int) -> Image.Image:
    w, h = pack.size
    scale = target_h / h
    return pack.resize((int(w * scale), int(h * scale)), Image.LANCZOS)


def draw_text_with_shadow(d, xy, text, fnt, fill=WHITE, shadow=(0, 0, 0, 120), shadow_off=3):
    x, y = xy
    d.text((x + shadow_off, y + shadow_off), text, font=fnt, fill=shadow)
    d.text((x, y), text, font=fnt, fill=fill)


def text_size(d, text, fnt):
    bbox = d.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_cta(canvas: Image.Image, xy, text, fnt, padding=(36, 18), fill=GOLD, fg=NAVY, radius=999):
    d = ImageDraw.Draw(canvas)
    tw, th = text_size(d, text, fnt)
    pw, ph = padding
    x, y = xy
    box = [x, y, x + tw + 2 * pw, y + th + 2 * ph]
    # shadow
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([box[0] + 4, box[1] + 8, box[2] + 4, box[3] + 8],
                         radius=min(radius, ph + th // 2 + 4), fill=(0, 0, 0, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    canvas.paste(sh, (0, 0), sh)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle(box, radius=min(radius, ph + th // 2 + 4), fill=fill)
    d.text((x + pw, y + ph - 2), text, font=fnt, fill=fg)
    return box


def draw_logo(canvas: Image.Image, xy, scale=1.0):
    """Simple Teatower wordmark."""
    d = ImageDraw.Draw(canvas)
    f = font(F_BOLD, int(34 * scale))
    fl = font(F_LIGHT, int(20 * scale))
    x, y = xy
    d.text((x, y), "TEATOWER", font=f, fill=WHITE, spacing=2)
    d.text((x, y + int(36 * scale)), "T E A   M A K E R S   ·   2 0 2 6", font=fl, fill=(230, 240, 245))


def add_iced_motif(canvas: Image.Image):
    """Light watery dotted motif overlay (drops/bubbles)."""
    w, h = canvas.size
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for _ in range(int(w * h / 60000)):
        cx = random.randint(0, w)
        cy = random.randint(0, h)
        r = random.randint(2, 6)
        a = random.randint(40, 120)
        od.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, a), width=2)
    canvas.alpha_composite(overlay)


# =========================================================================
# Layout helpers
# =========================================================================

def compose_packs_row(packs, max_h, gap, overlap=0.0, scales=None):
    """Return RGBA image of packs side-by-side. scales: per-pack height multiplier."""
    if scales is None:
        scales = [1.0] * len(packs)
    sized = [fit_pack(p, int(max_h * s)) for p, s in zip(packs, scales)]
    # add shadow per pack
    sized = [add_shadow(p) for p in sized]
    total_w = sum(p.size[0] for p in sized) - int(overlap * sum(p.size[0] for p in sized[:-1])) + gap * (len(sized) - 1)
    max_p_h = max(p.size[1] for p in sized)
    canvas = Image.new("RGBA", (total_w, max_p_h), (0, 0, 0, 0))
    x = 0
    for i, p in enumerate(sized):
        canvas.paste(p, (x, max_p_h - p.size[1]), p)
        x += p.size[0] + gap - (int(overlap * p.size[0]) if i < len(sized) - 1 else 0)
    return canvas


# =========================================================================
# Banner builders
# =========================================================================

def banner_homepage_wide(packs):
    """2432 x 788 — landscape wide. Claim left (45%), packs right (50%)."""
    W, H = 2432, 788
    bg = build_background((W, H)).convert("RGBA")
    add_iced_motif(bg)

    # Packs strip occupies right 50% only
    text_zone_w = int(W * 0.46)
    pack_zone_x = text_zone_w + 40
    pack_zone_w = W - pack_zone_x - 80

    selection = [packs[i] for i in [0, 1, 2, 3, 4]]
    strip = compose_packs_row(selection, max_h=int(H * 0.74), gap=-30,
                              scales=[0.88, 0.96, 1.05, 0.96, 0.88])
    if strip.size[0] > pack_zone_w:
        ratio = pack_zone_w / strip.size[0]
        strip = strip.resize((int(strip.size[0] * ratio), int(strip.size[1] * ratio)), Image.LANCZOS)
    sx = pack_zone_x + (pack_zone_w - strip.size[0]) // 2
    sy = (H - strip.size[1]) // 2 + 10
    bg.paste(strip, (sx, sy), strip)

    # Strong dark veil over text zone
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for x in range(text_zone_w + 80):
        a = int(150 * (1 - x / (text_zone_w + 80)))
        sd.line([(x, 0), (x, H)], fill=(8, 25, 45, a))
    bg.alpha_composite(shade)

    d = ImageDraw.Draw(bg)
    draw_logo(bg, (80, 60), scale=1.4)

    f_kicker = font(F_REG, 32)
    f_h1 = font(F_BOLD, 168)
    f_h2 = font(F_ITALIC, 56)
    f_sub = font(F_LIGHT, 36)

    d.text((90, 230), "COLLECTION  2026", font=f_kicker, fill=GOLD)
    draw_text_with_shadow(d, (80, 280), "Thés Glacés", f_h1)
    draw_text_with_shadow(d, (88, 470), "L'été en infusion à froid.", f_h2,
                          fill=(245, 250, 252))
    d.text((90, 555), "5 recettes fruitées · prêtes en 5 min · sans sucre ajouté",
           font=f_sub, fill=(230, 240, 245))

    draw_cta(bg, (90, 640), "Découvrir la collection  →", font(F_BOLD, 36))

    return bg.convert("RGB")


def banner_homepage_square(packs):
    """1392 x 752 — homepage compact. Claim left, packs right."""
    W, H = 1392, 752
    bg = build_background((W, H)).convert("RGBA")
    add_iced_motif(bg)

    text_zone_w = int(W * 0.48)
    pack_zone_x = text_zone_w + 30
    pack_zone_w = W - pack_zone_x - 60

    selection = [packs[i] for i in [0, 1, 2, 3]]
    strip = compose_packs_row(selection, max_h=int(H * 0.64), gap=-30,
                              scales=[0.92, 1.02, 1.02, 0.92])
    if strip.size[0] > pack_zone_w:
        ratio = pack_zone_w / strip.size[0]
        strip = strip.resize((int(strip.size[0] * ratio), int(strip.size[1] * ratio)), Image.LANCZOS)
    sx = pack_zone_x + (pack_zone_w - strip.size[0]) // 2
    sy = (H - strip.size[1]) // 2 + 20
    bg.paste(strip, (sx, sy), strip)

    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for x in range(text_zone_w + 60):
        a = int(150 * (1 - x / (text_zone_w + 60)))
        sd.line([(x, 0), (x, H)], fill=(8, 25, 45, a))
    bg.alpha_composite(shade)

    d = ImageDraw.Draw(bg)
    draw_logo(bg, (60, 50), scale=1.2)

    f_kicker = font(F_REG, 26)
    f_h1 = font(F_BOLD, 110)
    f_h2 = font(F_ITALIC, 40)
    f_sub = font(F_LIGHT, 26)

    d.text((70, 200), "COLLECTION  2026", font=f_kicker, fill=GOLD)
    draw_text_with_shadow(d, (60, 240), "Thés Glacés", f_h1)
    draw_text_with_shadow(d, (66, 370), "L'été en infusion à froid.", f_h2,
                          fill=(245, 250, 252))
    d.text((70, 435), "5 recettes — prêtes en 5 min", font=f_sub, fill=(230, 240, 245))

    draw_cta(bg, (70, 500), "Découvrir  →", font(F_BOLD, 30))

    return bg.convert("RGB")


def banner_category(packs):
    """1785 x 893 — category banner. Claim left, packs in arc on right."""
    W, H = 1785, 893
    bg = build_background((W, H)).convert("RGBA")
    add_iced_motif(bg)

    selection = [packs[i] for i in [0, 1, 2, 3, 4]]
    strip = compose_packs_row(selection, max_h=int(H * 0.66), gap=-40,
                              scales=[0.88, 0.96, 1.05, 0.96, 0.88])
    sx = W - strip.size[0] - 60
    sy = H - strip.size[1] - 70
    bg.paste(strip, (sx, sy), strip)

    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for x in range(int(W * 0.58)):
        a = int(120 * (1 - x / (W * 0.58)))
        sd.line([(x, 0), (x, H)], fill=(10, 30, 50, a))
    bg.alpha_composite(shade)

    d = ImageDraw.Draw(bg)
    draw_logo(bg, (75, 60), scale=1.3)

    f_kicker = font(F_REG, 30)
    f_h1 = font(F_BOLD, 150)
    f_h2 = font(F_ITALIC, 50)
    f_sub = font(F_LIGHT, 32)

    d.text((85, 240), "COLLECTION  ICED  ·  2026", font=f_kicker, fill=GOLD)
    draw_text_with_shadow(d, (75, 290), "Thés Glacés", f_h1)
    draw_text_with_shadow(d, (82, 460), "L'été se déguste à froid.", f_h2,
                          fill=(245, 250, 252))
    d.text((85, 540), "Infusion à froid · 5 recettes · 100% naturel",
           font=f_sub, fill=(230, 240, 245))

    draw_cta(bg, (85, 620), "Voir la collection  →", font(F_BOLD, 34))

    return bg.convert("RGB")


def banner_keyword(packs):
    """1320 x 660 — keyword banner. Compact: claim left, 3 packs right."""
    W, H = 1320, 660
    bg = build_background((W, H)).convert("RGBA")
    add_iced_motif(bg)

    selection = [packs[i] for i in [0, 2, 4]]
    strip = compose_packs_row(selection, max_h=int(H * 0.74), gap=-20,
                              scales=[0.95, 1.05, 0.95])
    sx = W - strip.size[0] - 50
    sy = (H - strip.size[1]) // 2 + 10
    bg.paste(strip, (sx, sy), strip)

    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for x in range(int(W * 0.58)):
        a = int(120 * (1 - x / (W * 0.58)))
        sd.line([(x, 0), (x, H)], fill=(10, 30, 50, a))
    bg.alpha_composite(shade)

    d = ImageDraw.Draw(bg)
    draw_logo(bg, (55, 45), scale=1.05)

    f_kicker = font(F_REG, 22)
    f_h1 = font(F_BOLD, 100)
    f_h2 = font(F_ITALIC, 36)
    f_sub = font(F_LIGHT, 24)

    d.text((65, 170), "COLLECTION  2026", font=f_kicker, fill=GOLD)
    draw_text_with_shadow(d, (55, 205), "Thés Glacés", f_h1)
    draw_text_with_shadow(d, (60, 320), "Infusion à froid, plaisir net.", f_h2,
                          fill=(245, 250, 252))
    d.text((65, 380), "5 recettes prêtes en 5 min", font=f_sub, fill=(230, 240, 245))

    draw_cta(bg, (65, 440), "Découvrir  →", font(F_BOLD, 26))

    return bg.convert("RGB")


def banner_skyscraper(packs):
    """480 x 1800 — vertical skyscraper. Claim top, packs stacked, CTA bottom."""
    W, H = 480, 1800
    bg = build_background((W, H)).convert("RGBA")
    add_iced_motif(bg)

    d = ImageDraw.Draw(bg)
    # logo small at top
    draw_logo(bg, (40, 50), scale=0.95)

    f_kicker = font(F_REG, 22)
    f_h1 = font(F_BOLD, 78)
    f_h2 = font(F_ITALIC, 30)
    f_sub = font(F_LIGHT, 22)

    d.text((50, 175), "COLLECTION  2026", font=f_kicker, fill=GOLD)
    draw_text_with_shadow(d, (50, 210), "Thés", f_h1)
    draw_text_with_shadow(d, (50, 295), "Glacés", f_h1)
    draw_text_with_shadow(d, (50, 400), "L'été en infusion", f_h2, fill=(245, 250, 252))
    draw_text_with_shadow(d, (50, 438), "à froid.", f_h2, fill=(245, 250, 252))

    # Vertical pack stack (4 packs, alternating align)
    stack_top = 510
    stack_bottom = 1620
    available_h = stack_bottom - stack_top
    selection = [packs[i] for i in [0, 1, 2, 3]]
    pack_h = int(available_h / 4) - 10
    y = stack_top
    for i, p in enumerate(selection):
        scaled = fit_pack(p, pack_h)
        scaled = add_shadow(scaled, blur=14, offset=(6, 10))
        if scaled.size[0] > W - 60:
            ratio = (W - 60) / scaled.size[0]
            scaled = scaled.resize((int(scaled.size[0] * ratio), int(scaled.size[1] * ratio)), Image.LANCZOS)
        x = (W - scaled.size[0]) // 2 + (-30 if i % 2 == 0 else 30)
        bg.paste(scaled, (x, y), scaled)
        y += pack_h + 10

    # CTA at bottom
    cta_text = "Découvrir →"
    cta_font = font(F_BOLD, 26)
    cta_box = draw_cta(bg, (50, 1700), cta_text, cta_font)

    d.text((50, 1755), "teatower.com", font=font(F_LIGHT, 22), fill=(230, 240, 245))

    return bg.convert("RGB")


# =========================================================================
# Run
# =========================================================================

def main():
    packs = [load_pack(fn, dark) for fn, _, dark in PACK_FILES]

    targets = [
        ("homepage_2432x788.jpg", banner_homepage_wide),
        ("homepage_1392x752.jpg", banner_homepage_square),
        ("category_1785x893.jpg", banner_category),
        ("keyword_1320x660.jpg", banner_keyword),
        ("skyscraper_480x1800.jpg", banner_skyscraper),
    ]
    for fn, fn_build in targets:
        out = fn_build(packs)
        out_path = os.path.join(OUT_DIR, fn)
        out.save(out_path, "JPEG", quality=92, optimize=True)
        print(f"OK {fn}  {out.size[0]}x{out.size[1]}  ({os.path.getsize(out_path)//1024} KB)")


if __name__ == "__main__":
    main()
