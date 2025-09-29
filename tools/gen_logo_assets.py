# tools/gen_logo_assets.py
# Gera PNGs do RadarBR a partir de static/img/logo-source.png
# Saída: logos do header (TRANSPARENTES), favicons (fundo branco), OG/social.

import os
from PIL import Image, ImageFilter

BASE = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(BASE, "static", "img", "logo-source.png")
OUT = os.path.join(BASE, "static", "img")
os.makedirs(OUT, exist_ok=True)

if not os.path.exists(SRC):
    raise SystemExit("[ERRO] Coloque seu logo-fonte em static/img/logo-source.png")

# --------- utilidades ---------
def to_rgba(img):
    return img if img.mode == "RGBA" else img.convert("RGBA")

def remove_near_white(img, bright_thr=228, chroma_thr=28):
    """
    Transforma em TRANSPARENTE o que for 'quase branco/creme':
      - brilho médio alto  (>= bright_thr)
      - pouca saturação    (max-min <= chroma_thr)
    Funciona bem para fundos #FFF, #FFFEF5, etc.
    """
    img = to_rgba(img)
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r,g,b,a = px[x,y]
            if a == 0:
                continue
            mx, mn = max(r,g,b), min(r,g,b)
            bright = (r+g+b)//3
            if bright >= bright_thr and (mx-mn) <= chroma_thr:
                px[x,y] = (r,g,b,0)
    return img

def trim_alpha(img, pad=8):
    """Corta bordas transparentes com um padding leve."""
    img = to_rgba(img)
    alpha = img.split()[-1]
    bbox = alpha.getbbox()
    if not bbox:
        return img
    x0,y0,x1,y1 = bbox
    x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
    x1 = min(img.size[0], x1 + pad); y1 = min(img.size[1], y1 + pad)
    return img.crop((x0,y0,x1,y1))

def resize_h(img, h):
    w,_ = img.size
    nw = max(1, round(w * (h / img.size[1])))
    return img.resize((nw, h), Image.LANCZOS)

def square_icon(img, size, bg=(255,255,255,255), padding_ratio=0.22):
    """Centraliza o logo no quadrado com folga (bom p/ maskable)."""
    canvas = Image.new("RGBA", (size,size), bg)
    w,h = img.size
    max_dim = int(size * (1 - 2*padding_ratio))
    scale = min(max_dim / w, max_dim / h)
    nw, nh = max(1,int(round(w*scale))), max(1,int(round(h*scale)))
    logo = img.resize((nw,nh), Image.LANCZOS)
    canvas.alpha_composite(logo, ((size-nw)//2, (size-nh)//2))
    return canvas

def fit_on_canvas(img, size, bg=(255,255,255,255), margin_ratio=0.12):
    cw,ch = size
    canvas = Image.new("RGBA", size, bg)
    w,h = img.size
    max_w, max_h = int(cw*(1-2*margin_ratio)), int(ch*(1-2*margin_ratio))
    scale = min(max_w/w, max_h/h)
    nw,nh = max(1,int(round(w*scale))), max(1,int(round(h*scale)))
    logo = img.resize((nw,nh), Image.LANCZOS)
    # sombra leve
    shadow = Image.new("RGBA", (nw,nh), (0,0,0,150)).filter(ImageFilter.GaussianBlur(8))
    x,y = (cw-nw)//2, (ch-nh)//2
    canvas.alpha_composite(shadow, (x+8,y+8))
    canvas.alpha_composite(logo, (x,y))
    return canvas

# --------- processo ---------
src = Image.open(SRC)
# 1) remove fundo quase branco/creme e corta as bordas
clean = trim_alpha(remove_near_white(src, bright_thr=228, chroma_thr=28), pad=6)

# 2) LOGOS DO HEADER (TRANSPARENTES)
resize_h(clean, 104).save(os.path.join(OUT, "logo-radarbr.png"), "PNG")     # 1x
resize_h(clean, 208).save(os.path.join(OUT, "logo-radarbr@2x.png"), "PNG")  # 2x (retina)

# 3) FAVICONS (fundo branco)
for sz, name in [(32,"favicon-32.png"), (180,"favicon-180.png"),
                 (192,"favicon-192.png"), (512,"favicon-512.png")]:
    square_icon(clean, sz, bg=(255,255,255,255), padding_ratio=0.22).save(os.path.join(OUT,name), "PNG")

# 4) SOCIAL (fundo branco)
fit_on_canvas(clean, (1200,630)).save(os.path.join(OUT,"og-1200x630.png"), "PNG")
fit_on_canvas(clean, (1080,1080), margin_ratio=0.18).save(os.path.join(OUT,"social-1080x1080.png"), "PNG")

print("[OK] Gerados com sucesso em static/img/")
