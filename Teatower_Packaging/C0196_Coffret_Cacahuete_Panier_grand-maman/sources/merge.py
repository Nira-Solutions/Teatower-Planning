import sys, os, copy, pypdf, pypdfium2 as pdfium
B, SRC = sys.argv[1], sys.argv[2]
gab = pypdf.PdfReader(os.path.join(SRC, "Giftbox_2026_GABARIT.pdf"))
def fit(path, ref):
    r = pypdf.PdfReader(path); p = r.pages[0]
    if len(r.pages) > 1: print("WARN pages", path, len(r.pages))
    W, H = float(ref.mediabox.width), float(ref.mediabox.height)
    w, h = float(p.mediabox.width), float(p.mediabox.height)
    print(os.path.basename(path), "chrome", round(w,2), round(h,2), "target", W, H)
    p.add_transformation(pypdf.Transformation().scale(W/w, H/h)); p.mediabox = pypdf.generic.RectangleObject([0,0,W,H])
    p.cropbox = p.mediabox; p.trimbox = ref.trimbox; p.bleedbox = ref.bleedbox
    return p
pages = [fit(os.path.join(B,"corps.pdf"), gab.pages[0]), fit(os.path.join(B,"couvercle.pdf"), gab.pages[1])]
w = pypdf.PdfWriter()
for p in pages: w.add_page(p)
w.write(os.path.join(B, "C0196_PRINT.pdf"))
# preview = art + gabarit par-dessus
w2 = pypdf.PdfWriter(); r = pypdf.PdfReader(os.path.join(B, "C0196_PRINT.pdf"))
for i, p in enumerate(r.pages):
    p.merge_page(gab.pages[i]); w2.add_page(p)
w2.write(os.path.join(B, "C0196_PREVIEW.pdf"))
for n in ["C0196_PRINT", "C0196_PREVIEW"]:
    d = pdfium.PdfDocument(os.path.join(B, n + ".pdf"))
    for i, pg in enumerate(d):
        pg.render(scale=float(sys.argv[3]) if len(sys.argv)>3 else 2).to_pil().save(os.path.join(B, f"{n}_{i}.png"))
print("done")
