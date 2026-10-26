#!/usr/bin/env python3
"""kiem_tra_bo_cuc.py — kiểm tra HÌNH HỌC của slide sau khi dàn trang thật (LibreOffice → PDF), đo bằng nét chữ thật:

  1. Đường kẻ chạm/cắt qua chữ (ví dụ vạch dưới con số chạm chân chữ "g", "y").
  2. Chữ tràn qua mép khối màu chứa nó, hoặc sát mép khối (< 4pt).
  3. Chữ chồng lên chữ của hộp khác; chữ đè lên logo/ảnh nhỏ.
  4. Chữ ra ngoài slide hoặc sát mép slide (< 0,25"); vật thể ra ngoài slide (trừ nền, texture, ảnh tràn viền).
  5. Hộp chữ lệch lề nhau rất ít (0,01–0,08") — nhìn như đặt nhầm.
  6. Cân đối: khoảng trống lớn bất thường giữa các phần; khối màu chứa chữ mà phần lớn để trống.

Dùng:  python3 kiem_tra_bo_cuc.py Slide.pptx [--json] [--anh thu_muc]   (--anh: lưu ảnh từng slide có khoanh vùng lỗi)
Cần: LibreOffice (soffice), PyMuPDF, Pillow. Phông của gói được cài tạm vào ~/.fonts để đo đúng.
Mã thoát 1 khi còn LỖI.
"""
import json, os, re, subprocess, sys, tempfile, zipfile
import xml.etree.ElementTree as ET
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kiem_tra_slide import NS, resolve_mc  # noqa: E402

FONT_DIR = os.path.join(ROOT, "assets", "fonts")
FILES = json.load(open(os.path.join(FONT_DIR, "files.json"), encoding="utf-8"))
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
PT = 72.0
TEN_NEN = re.compile(r"^(nen|den\d*|hat\d+|vong\d*|sang\d*|texture|bg|motif\w*|mesh|word|img\d*|shade|panel|frame|bignum|!!sec|sec|eq\w*|sym\d+)$")

# ---------------------------------------------------------------- phông: tên trong PDF → tệp
_FONT_BY_PS = {}
for fam, slots in FILES.items():
    for slot, rel in slots.items():
        _FONT_BY_PS[os.path.splitext(os.path.basename(rel))[0].lower().replace("-", "")] = os.path.join(FONT_DIR, rel)
_cache = {}
def ink_box(text, psname, size):
    """khung nét mực (x0, y0, x1, y1) so với gốc dòng (baseline), đơn vị pt"""
    key = psname.split("+")[-1].lower().replace("-", "").replace(",", "")
    path = _FONT_BY_PS.get(key)
    if not path:
        for k, v in _FONT_BY_PS.items():
            if key.startswith(k) or k.startswith(key): path = v; break
    path = path or FALLBACK
    fk = (path, int(size * 4))
    if fk not in _cache: _cache[fk] = ImageFont.truetype(path, max(4, int(size * 4)))
    t = text.replace(" ", " ").rstrip()
    if not t.strip(): return None
    b = _cache[fk].getbbox(t, anchor="ls")
    return (b[0] / 4, b[1] / 4, b[2] / 4, b[3] / 4)

def install_fonts():
    dst = os.path.expanduser("~/.fonts/makeslides")
    os.makedirs(dst, exist_ok=True)
    for slots in FILES.values():
        for rel in slots.values():
            s = os.path.join(FONT_DIR, rel); d = os.path.join(dst, os.path.basename(rel))
            if not os.path.exists(d):
                with open(s, "rb") as a, open(d, "wb") as b: b.write(a.read())
    subprocess.run(["fc-cache", "-f", dst], capture_output=True)

def to_pdf(pptx, outdir):
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, pptx], capture_output=True, timeout=240)
    pdf = os.path.join(outdir, os.path.splitext(os.path.basename(pptx))[0] + ".pdf")
    if not os.path.exists(pdf): raise SystemExit("Không chuyển được sang PDF (cần LibreOffice)")
    return pdf

# ---------------------------------------------------------------- hình học
def inter(a, b): return max(0.0, min(a[2], b[2]) - max(a[0], b[0])) * max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
def area(a): return max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
def contains(outer, inner, tol=1.0): return inner[0] >= outer[0] - tol and inner[1] >= outer[1] - tol and inner[2] <= outer[2] + tol and inner[3] <= outer[3] + tol
def fmt(b): return f"({b[0] / PT:.2f}\", {b[1] / PT:.2f}\")"

def page_items(page):
    W, H = page.rect.width, page.rect.height
    spans = []
    for blk in page.get_text("dict")["blocks"]:
        if blk["type"] != 0: continue
        for ln in blk["lines"]:
            for s in ln["spans"]:
                if not s["text"].strip(): continue
                ib = ink_box(s["text"], s["font"], s["size"])
                if not ib: continue
                ox, oy = s["origin"]
                ink = (ox + ib[0], oy + ib[1], ox + ib[2], oy + ib[3])
                ghost = s["size"] >= 100 or s.get("alpha", 255) < 160
                spans.append({"text": s["text"].strip(), "size": s["size"], "ink": ink, "box": tuple(s["bbox"]), "ghost": ghost, "base": oy, "x0": ox})
    lines, blocks = [], []
    for d in page.get_drawings():
        r = d["rect"]; b = (r.x0, r.y0, r.x1, r.y1)
        wid = d.get("width") or 0
        if (d.get("fill") is None) and d.get("color") is not None and (r.height <= 3 or r.width <= 3):
            half = max(wid, 0.75) / 2
            lines.append({"box": (b[0] - (half if r.width <= 3 else 0), b[1] - (half if r.height <= 3 else 0), b[2] + (half if r.width <= 3 else 0), b[3] + (half if r.height <= 3 else 0))})
        elif d.get("fill") is not None and area(b) < 0.6 * W * H and r.width > 14 and r.height > 14 and (d.get("fill_opacity") or 1) > 0.5:
            # (chấm/hạt trang trí nhỏ hơn 14pt không phải khối chứa chữ)
            blocks.append({"box": b, "dai": r.height >= 0.95 * H or r.width >= 0.95 * W})
    imgs = []
    for im in page.get_image_info():
        b = tuple(im["bbox"])
        if area(b) < 0.5 * W * H: imgs.append({"box": b})
    return spans, lines, blocks, imgs, W, H

def xml_shapes(z, n):
    root = resolve_mc(ET.fromstring(z.read(n)))
    out = []
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag not in ("sp", "pic", "graphicFrame", "cxnSp"): continue
        nv = el.find(".//p:cNvPr", NS); x = el.find(".//a:xfrm", NS)
        if nv is None or x is None or x.find("a:off", NS) is None: continue
        o, e = x.find("a:off", NS), x.find("a:ext", NS)
        has_text = el.find(".//a:t", NS) is not None
        out.append({"name": nv.get("name", ""), "kind": tag, "text": has_text, "x": int(o.get("x")) / 914400, "y": int(o.get("y")) / 914400, "w": int(e.get("cx")) / 914400, "h": int(e.get("cy")) / 914400})
    return out

def kiem(path, anh=None):
    install_fonts()
    import pymupdf as fitz
    tmp = tempfile.mkdtemp()
    pdf = to_pdf(os.path.abspath(path), tmp)
    doc = fitz.open(pdf)
    z = zipfile.ZipFile(path)
    sx = z.read("ppt/presentation.xml").decode("utf8")
    m = re.search(r'<p:sldSz cx="(\d+)" cy="(\d+)"', sx)
    SW, SH = int(m.group(1)) / 914400, int(m.group(2)) / 914400
    slides = sorted([n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)], key=lambda n: int(re.findall(r"\d+", n)[-1]))
    out = []
    add = lambda lv, s, msg, box=None: out.append({"muc": lv, "slide": s, "noi_dung": msg, "box": box})
    for idx, page in enumerate(doc, 1):
        spans, lines, blocks, imgs, W, H = page_items(page)
        live = [s for s in spans if not s["ghost"]]
        mg = 0.25 * PT
        for s in live:
            ink, t = s["ink"], s["text"][:30]
            # 4. ra ngoài / sát mép slide
            if ink[0] < -0.5 or ink[1] < -0.5 or ink[2] > W + 0.5 or ink[3] > H + 0.5:
                add("LỖI", idx, f"chữ '{t}' ra ngoài slide tại {fmt(ink)}", ink)
            elif ink[0] < mg or ink[2] > W - mg or ink[1] < mg * 0.6 or ink[3] > H - mg * 0.6:
                add("CẢNH BÁO", idx, f"chữ '{t}' sát mép slide (< 0,25\")", ink)
            # 1. đường kẻ chạm/cắt chữ: khoảng hở < 3pt = LỖI, < 6pt = CẢNH BÁO
            for l in lines:
                lb = l["box"]
                if not (lb[0] < ink[2] and lb[2] > ink[0]): continue
                gap = -1 if inter(lb, ink) > 0 else (lb[1] - ink[3] if lb[1] >= ink[3] else ink[1] - lb[3] if lb[3] <= ink[1] else -1)
                if gap < 6:
                    lv = "LỖI" if gap < 3 else "CẢNH BÁO"
                    msg = "cắt qua" if gap < 0 else f"cách {gap:.1f}pt"
                    add(lv, idx, f"đường kẻ {msg} chữ '{t}' (cỡ {s['size']:.0f}pt) — cần hở ≥ 6pt so với chân/đỉnh chữ", ink)
                    break
            # 2. chữ vs khối màu
            for b in blocks:
                bb = b["box"]
                if inter(bb, ink) <= 0: continue
                if not contains(bb, ink, 1.0):
                    if area(bb) > 4 * area(ink) or inter(bb, ink) < 0.9 * area(ink):
                        add("LỖI", idx, f"chữ '{t}' tràn qua mép khối màu {fmt(bb)}", ink)
                elif min(ink[0] - bb[0], bb[2] - ink[2]) < 4 and area(bb) > 2 * area(ink):
                    add("CẢNH BÁO", idx, f"chữ '{t}' sát mép khối màu (< 4pt)", ink)
            # 3b. chữ đè logo/ảnh nhỏ
            for im in imgs:
                ib = im["box"]
                if area(ib) < 0.12 * W * H and inter(ib, ink) > 0.15 * min(area(ib), area(ink)):
                    add("LỖI", idx, f"chữ '{t}' đè lên ảnh/logo {fmt(ib)}", ink)
        # 3. chữ chồng chữ (khác dòng); cùng dòng: dấu đầu dòng sát chữ
        for i in range(len(live)):
            for j in range(i + 1, len(live)):
                a, b = live[i], live[j]
                if abs(a["base"] - b["base"]) < 1.5:
                    l, r = (a, b) if a["ink"][0] <= b["ink"][0] else (b, a)
                    if l["text"] in ("•", "–", "-", "▪", "◦") and 0 <= r["ink"][0] - l["ink"][2] < 4 and abs(l["ink"][0] - r["ink"][0]) < 30:
                        add("CẢNH BÁO", idx, f"dấu đầu dòng sát chữ '{r['text'][:20]}' ({r['ink'][0] - l['ink'][2]:.1f}pt) — tăng thụt lề dấu đầu dòng", r["ink"])
                    continue
                ov = inter(a["ink"], b["ink"])
                if ov > 4 and ov > 0.05 * min(area(a["ink"]), area(b["ink"])):
                    add("LỖI", idx, f"chữ '{a['text'][:20]}' chồng lên chữ '{b['text'][:20]}'", a["ink"])
        # 6a. khoảng trống lớn
        items = sorted([s["ink"] for s in live] + [im["box"] for im in imgs if area(im["box"]) > 400] + [b["box"] for b in blocks], key=lambda b: b[1])
        if items:
            bottom = items[0][3]; worst = (0, None)
            for b in items[1:]:
                gap = b[1] - bottom
                if gap > worst[0]: worst = (gap, (bottom, b[1]))
                bottom = max(bottom, b[3])
            if worst[0] > 0.3 * H:
                add("GỢI Ý", idx, f"khoảng trống {worst[0] / PT:.2f}\" giữa {worst[1][0] / PT:.2f}\" và {worst[1][1] / PT:.2f}\" — dồn nội dung lại hoặc tăng cỡ phần chính")
        # 6b. khối màu chứa chữ mà phần lớn trống
        for b in blocks:
            if b.get("dai"): continue          # dải/cột màu suốt chiều slide là mảng bố cục, không phải hộp chữ
            bb = b["box"]; inside = [s["ink"] for s in live if contains(bb, s["ink"], 1)]
            if inside and area(bb) > 0.06 * W * H:
                used = (max(i[3] for i in inside) - min(i[1] for i in inside)) / (bb[3] - bb[1])
                if used < 0.4: add("GỢI Ý", idx, f"khối màu {fmt(bb)} chỉ dùng {used:.0%} chiều cao cho chữ — thu khối theo nội dung")
        # 4b + 5. từ XML: vật thể ra ngoài slide, lệch lề
        if idx <= len(slides):
            shp = xml_shapes(z, slides[idx - 1])
            for s in shp:
                if TEN_NEN.match(s["name"]) or (s["w"] >= SW * 0.95 and s["h"] >= SH * 0.95): continue
                if s["x"] < -0.01 or s["y"] < -0.01 or s["x"] + s["w"] > SW + 0.01 or s["y"] + s["h"] > SH + 0.01:
                    add("CẢNH BÁO", idx, f"vật thể '{s['name']}' ra ngoài slide ({s['x']:.2f}, {s['y']:.2f}, {s['w']:.2f}×{s['h']:.2f}\")")
            tb = [s for s in shp if s["text"] and not TEN_NEN.match(s["name"])]
            seen = set()
            for i in range(len(tb)):
                for j in range(i + 1, len(tb)):
                    a, b = tb[i], tb[j]
                    d = abs(a["x"] - b["x"])
                    vert_close = abs((a["y"] + a["h"] / 2) - (b["y"] + b["h"] / 2)) < 2.5
                    if 0.01 < d < 0.08 and vert_close and (a["name"], b["name"]) not in seen:
                        seen.add((a["name"], b["name"]))
                        add("GỢI Ý", idx, f"'{a['name']}' và '{b['name']}' lệch lề trái {d:.2f}\" — căn thẳng hàng")
    if anh:
        os.makedirs(anh, exist_ok=True)
        from PIL import Image, ImageDraw
        for idx, page in enumerate(doc, 1):
            boxes = [o["box"] for o in out if o["slide"] == idx and o["box"] and o["muc"] != "GỢI Ý"]
            if not boxes: continue
            pix = page.get_pixmap(dpi=110); f = os.path.join(anh, f"slide{idx}.png"); pix.save(f)
            im = Image.open(f).convert("RGB"); d = ImageDraw.Draw(im); k = 110 / 72
            for b in boxes: d.rectangle([b[0] * k - 3, b[1] * k - 3, b[2] * k + 3, b[3] * k + 3], outline=(255, 0, 80), width=3)
            im.save(f)
    return out, len(doc)

def main():
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    anh = a[a.index("--anh") + 1] if "--anh" in a else None
    out, n = kiem(a[0], anh)
    uniq, seen = [], set()
    for o in out:
        k = (o["slide"], o["noi_dung"])
        if k not in seen: seen.add(k); uniq.append(o)
    if "--json" in a:
        print(json.dumps([{k: v for k, v in o.items() if k != "box"} for o in uniq], ensure_ascii=False, indent=1)); sys.exit(0)
    print(f"{a[0]}: {n} slide (đo trên bản dàn trang LibreOffice)")
    for lv in ("LỖI", "CẢNH BÁO", "GỢI Ý"):
        rows = [o for o in uniq if o["muc"] == lv]
        print(f"\n{lv} ({len(rows)})")
        for o in sorted(rows, key=lambda o: o["slide"]): print(f"  [slide {o['slide']}] {o['noi_dung']}")
    if anh: print(f"\nẢnh khoanh vùng lỗi: {anh}")
    sys.exit(1 if any(o["muc"] == "LỖI" for o in uniq) else 0)

if __name__ == "__main__":
    main()
