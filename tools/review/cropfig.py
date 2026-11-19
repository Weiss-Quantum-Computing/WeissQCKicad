# usage: cropfig.py raw.pdf outbase   -> outbase.pdf/.svg/.png (or outbase p1.. if several pages)
import sys, pymupdf as fitz
raw, outbase = sys.argv[1], sys.argv[2]
doc = fitz.open(raw)
n = doc.page_count
res = []
for i, page in enumerate(doc):
    pr = page.rect
    bb = None
    for d in page.get_drawings():
        r = d["rect"]
        if r.is_empty or r.is_infinite: continue
        if r.width > 0.97*pr.width and r.height > 0.97*pr.height: continue  # page-sized background
        bb = fitz.Rect(r) if bb is None else bb | r
    for b in page.get_text("blocks"):
        r = fitz.Rect(b[:4])
        if not r.is_empty: bb = r if bb is None else bb | r
    if bb is None:
        res.append((i, 'EMPTY')); continue
    m = 12
    bb = fitz.Rect(bb.x0-m, bb.y0-m, bb.x1+m, bb.y1+m) & pr
    page.set_cropbox(bb)
    base = outbase if n == 1 else f"{outbase} (sheet {i+1} of {n})"
    single = fitz.open(); single.insert_pdf(doc, from_page=i, to_page=i); single.save(base + ".pdf", garbage=3, deflate=True)
    p2 = single[0]
    open(base + ".svg", "w", encoding="utf8").write(p2.get_svg_image(text_as_path=True))
    scale = min(4.0, 6000.0/max(bb.width, bb.height))
    scale = max(scale, 2.0)
    pix = p2.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    pix.save(base + ".png")
    res.append((i, f"{bb.width/72*25.4:.0f}x{bb.height/72*25.4:.0f}mm", f"{pix.width}x{pix.height}px"))
print(n, res)
