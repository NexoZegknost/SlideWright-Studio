#!/usr/bin/env python3
"""kiem_tra_slide.py — tự kiểm tra một tệp .pptx của makeSlides trước khi bàn giao.

Ba nhóm kiểm tra:
  1. MÀU   — tương phản chữ/nền (WCAG 4.5:1, chữ lớn 3:1), chữ sáng cùng tông với nền đậm
             (ví dụ chữ xanh nhạt trên nền xanh đậm), nhịp sáng – tối của cả bài, số màu chữ.
  2. DẤU HIỆU AI — emoji/ký hiệu/biểu tượng đứng trước đoạn văn, icon trong vòng tròn, vòng "VS",
             nhãn "Điểm chính", tiêu đề chung chung hoặc có dấu hai chấm, từ sáo rỗng, lạm dụng gạch ngang,
             ba ý dài bằng nhau, bố cục lặp liên tiếp, lời kết sáo.
  3. KỸ THUẬT — công thức gõ bằng chữ thường (phải dùng khối Equation), phông bị loại (Be Vietnam Pro).

Dùng:  python3 kiem_tra_slide.py Slide_X.pptx [--json]
Mã thoát 1 khi còn mục LỖI. Mục CẢNH BÁO cần xem và quyết định; GỢI Ý để tham khảo.
"""
import colorsys, json, re, sys, zipfile
import xml.etree.ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "a14": "http://schemas.microsoft.com/office/drawing/2010/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
EMU = 914400
BANNED_FONTS = {"Be Vietnam Pro"}

# ---------------------------------------------------------------- màu
def rgb(h): return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
def lum(h):
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = map(f, rgb(h)); return 0.2126 * r + 0.7152 * g + 0.0722 * b
def contrast(a, b):
    x, y = sorted([lum(a), lum(b)], reverse=True); return (x + 0.05) / (y + 0.05)
def hue_chroma(h):
    r, g, b = rgb(h); return colorsys.rgb_to_hsv(r, g, b)[0] * 360, max(r, g, b) - min(r, g, b)
def same_hue(fg, bg):
    (h1, c1), (h2, c2) = hue_chroma(fg), hue_chroma(bg)
    d = abs(h1 - h2) % 360; d = min(d, 360 - d)
    return c1 >= 0.35 and c2 >= 0.12 and d < 30
# vòng màu của hoạ sĩ (RYB): cặp đối nhau là lam–cam, đỏ–lục, vàng–tím (cùng luật với scripts/mau.js)
_RYB = [(0, 0), (30, 60), (60, 120), (120, 180), (240, 240), (300, 300), (360, 360)]
def ryb(h):
    for (a0, b0), (a1, b1) in zip(_RYB, _RYB[1:]):
        if h <= a1: return b0 + (h - a0) * (b1 - b0) / (a1 - a0)
    return h
def ryb_dist(a, b):
    d = abs(ryb(hue_chroma(a)[0]) - ryb(hue_chroma(b)[0])) % 360; return min(d, 360 - d)
def opposite(a, b):
    """hai màu có sắc đối nhau (lệch ≥ 140° trên vòng RYB), cả hai có sắc và ít nhất một màu tươi"""
    (_, c1), (_, c2) = hue_chroma(a), hue_chroma(b)
    return c1 >= 0.12 and c2 >= 0.12 and max(c1, c2) >= 0.35 and ryb_dist(a, b) >= 140

def solid(el):
    """màu srgb + độ đục (0–1) của <a:solidFill> con trực tiếp, hoặc None"""
    if el is None: return None
    sf = el.find("a:solidFill", NS)
    if sf is None: return None
    c = sf.find("a:srgbClr", NS)
    if c is None: return None
    al = c.find("a:alpha", NS)
    return c.get("val").upper(), (int(al.get("val")) / 100000 if al is not None else 1.0)

# ---------------------------------------------------------------- đọc slide
def resolve_mc(root):
    """thay mc:AlternateContent bằng nội dung mc:Choice (thứ PowerPoint hiển thị)"""
    for parent in root.iter():
        for i, ch in enumerate(list(parent)):
            if ch.tag == f"{{{NS['mc']}}}AlternateContent":
                choice = ch.find("mc:Choice", NS)
                parent.remove(ch)
                if choice is not None:
                    for j, x in enumerate(list(choice)): parent.insert(i + j, x)
    return root

def box(el):
    x = el.find(".//a:xfrm", NS)
    if x is None: return None
    o, e = x.find("a:off", NS), x.find("a:ext", NS)
    if o is None or e is None: return None
    return [int(o.get("x")) / EMU, int(o.get("y")) / EMU, int(e.get("cx")) / EMU, int(e.get("cy")) / EMU]

def read_slide(xml):
    root = resolve_mc(ET.fromstring(xml))
    bg = None
    bgp = root.find(".//p:bg/p:bgPr", NS)
    if bgp is not None:
        s = solid(bgp); bg = s[0] if s else None
    shapes = []
    tree = root.find(".//p:spTree", NS)
    for el in tree.iter():
        tag = el.tag.split("}")[1]
        if tag not in ("sp", "pic", "graphicFrame"): continue
        nv = el.find(".//p:cNvPr", NS)
        sh = {"kind": tag, "name": nv.get("name") if nv is not None else "", "box": box(el), "fill": None, "geom": None, "paras": [], "eq": False, "fonts": set(), "cells": []}
        if tag == "sp":
            sp = el.find("p:spPr", NS)
            sh["fill"] = solid(sp)
            g = sp.find("a:prstGeom", NS) if sp is not None else None
            sh["geom"] = g.get("prst") if g is not None else None
            sh["eq"] = el.find(".//a14:m", NS) is not None
            for p in el.findall(".//p:txBody/a:p", NS):
                runs = []
                for r in p.findall("a:r", NS):
                    rp = r.find("a:rPr", NS); t = r.find("a:t", NS)
                    if t is None or not (t.text or ""): continue
                    col = solid(rp)
                    lat = rp.find("a:latin", NS) if rp is not None else None
                    if lat is not None: sh["fonts"].add(lat.get("typeface"))
                    runs.append({"text": t.text, "color": col, "sz": int(rp.get("sz", "1800")) / 100 if rp is not None else 18, "b": rp is not None and rp.get("b") == "1"})
                if runs: sh["paras"].append(runs)
        elif tag == "pic":
            sh["descr"] = nv.get("descr", "") if nv is not None else ""
        elif tag == "graphicFrame":
            for tc in el.findall(".//a:tc", NS):
                fill = solid(tc.find("a:tcPr", NS))
                for r in tc.findall(".//a:r", NS):
                    rp = r.find("a:rPr", NS); t = r.find("a:t", NS)
                    if t is not None and t.text: sh["cells"].append({"text": t.text, "color": solid(rp), "fill": fill, "sz": int(rp.get("sz", "1400")) / 100 if rp is not None else 14})
        shapes.append(sh)
    return bg, shapes

def inside(pt, b): return b and b[0] <= pt[0] <= b[0] + b[2] and b[1] <= pt[1] <= b[1] + b[3]
def center(b): return (b[0] + b[2] / 2, b[1] + min(b[3], 0.6) / 2)

def background_under(i, shapes, bg):
    sh = shapes[i]
    if sh["fill"] and sh["fill"][1] >= 0.5: return sh["fill"][0], None
    c = center(sh["box"]) if sh["box"] else None
    for j in range(i - 1, -1, -1):
        o = shapes[j]
        if c and inside(c, o["box"]):
            if o["kind"] == "pic" and o.get("descr", "").startswith(("hoa-tiet", "Logo")): continue  # hoạ tiết trong suốt, logo: bỏ qua
            if o["kind"] == "pic" and o["box"][2] * o["box"][3] > 2: return None, "ảnh"
            if o["fill"] and o["fill"][1] >= 0.5: return o["fill"][0], None
    return bg or "FFFFFF", None

# ---------------------------------------------------------------- dấu hiệu AI
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]")
LEAD_SYMBOL = re.compile(r"^\s*([\u2190-\u21FF\u2022\u25A0-\u25FF\u2713-\u2718\u2794-\u27BF\u2605\u2606\u261B-\u261E\u27A4►▶▸»✦✧◆◇●○■□✓✔✗✘➜➤→⇒⮕]|[-*]\s)")
GENERIC_TITLES = {"giới thiệu", "nội dung", "tổng quan", "kết luận", "tóm tắt", "cảm ơn", "hỏi đáp", "q&a", "mục lục", "thank you", "agenda", "overview", "introduction", "conclusion"}
BUZZ = ["toàn diện", "nâng tầm", "bứt phá", "đột phá", "hành trình", "khám phá thế giới", "chìa khoá vàng", "chìa khóa vàng", "kỷ nguyên mới", "không ngừng", "hãy cùng", "trong bối cảnh", "ngày càng", "đóng vai trò quan trọng", "vô cùng quan trọng", "mang lại hiệu quả", "giải pháp tối ưu", "tối ưu hoá", "tối ưu hóa", "khai phá", "tiềm năng to lớn", "cuộc cách mạng", "game changer", "leverage", "seamless", "unlock", "empower", "delve"]
CLICHE_CLOSE = re.compile(r"cảm ơn.{0,25}(lắng nghe|theo dõi|chú ý)|thank you for (your )?(attention|listening)|cảm ơn\s*[–—-]\s*hỏi đáp", re.I)
LABELS = re.compile(r"^(điểm chính|key takeaways?|ý chính|lưu ý quan trọng|tóm lại)\s*:?\s*$", re.I)
NOT_ONLY = re.compile(r"không chỉ\b.{1,60}\bmà còn", re.I)
UNITS = {"V", "mV", "kV", "A", "mA", "µA", "μA", "uA", "Ω", "kΩ", "MΩ", "W", "mW", "Hz", "kHz", "MHz", "s", "ms", "µs", "F", "µF", "μF", "nF", "pF", "H", "mH", "dB", "%", "m", "cm", "mm", "km", "kg", "g", "N", "J", "K", "°C", "lần"}
OPS = re.compile(r"[\/·×÷\^√∑∏∫∂∞≤≥≠]|\b(sqrt|frac|sum)\b|_\{|\^\{")
def is_words_slash(t):
    """'Lớp/nhóm', 'Thành viên / phân công' là chữ thường, không phải công thức; 'VE / IE' là công thức"""
    if not re.fullmatch(r"[\w\s]+/[\w\s]+", t): return False
    toks = re.findall(r"\w+", t)
    return not all(len(x) <= 4 and re.search(r"[A-Z]", x) for x in toks)

def formula_like(text):
    t = text.strip()
    VAR = r"(?<![\wÀ-ỹ])[A-Za-zα-ωΑ-Ω][A-Za-z0-9]{0,3}(?![\wÀ-ỹ])"   # ký hiệu đại lượng: ngắn, chữ Latin/Hy Lạp, có thể kèm chỉ số
    for m in re.finditer(VAR + r"\)?\s*[\/·×÷\^]\s*\(?" + r"(" + VAR + r"|\d)", t):
        left = re.match(r"[A-Za-zα-ωΑ-Ω][A-Za-z0-9]*", m.group(0)).group(0)
        if (re.search(r"[A-Z0-9α-ωΑ-Ω]", left) or len(left) <= 2) and not re.search(r"\b(https?|www)\b", t) and not is_words_slash(t): return True
    if OPS.search(t) and re.search(r"[A-Za-zα-ωΑ-Ω]\w*\s*[=≈]", t): return True
    for m in re.finditer(r"([A-Za-zα-ωΑ-Ω][\w]{0,4})\s*[=≈]\s*([^,;=]{1,40})", t):
        rhs = m.group(2).strip()
        toks = re.findall(r"[A-Za-zα-ωΑ-ΩµΩ°%][\wΩ°]*", rhs)
        if any(tok not in UNITS for tok in toks) and re.search(r"[+\-−·×/()]", rhs): return True
    return False

def signature(shapes):
    return tuple(sorted((s["kind"], round(s["box"][0] * 2), round(s["box"][1] * 2), round(s["box"][2] * 2), round(s["box"][3] * 2)) for s in shapes if s["box"]))

# ---------------------------------------------------------------- chạy
def check(path):
    z = zipfile.ZipFile(path)
    slides = sorted([n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)], key=lambda n: int(re.findall(r"\d+", n)[-1]))
    out = []  # (mức, slide, nhóm, nội dung)
    add = lambda lv, s, g, m: out.append((lv, s, g, m))
    tones, text_hues, sigs, dashes, eq_count, title_colon, banned = [], set(), [], 0, 0, 0, {}
    deck_colors = {}  # màu có sắc dùng trong bài (chữ + mảng màu) → số slide
    for idx, n in enumerate(slides, 1):
        bg, shapes = read_slide(z.read(n))
        bgc = bg or "FFFFFF"
        tones.append("tối" if lum(bgc) < 0.2 else "sáng")
        sigs.append(signature(shapes))
        texts = []
        for i, sh in enumerate(shapes):
            for f in sh["fonts"] & BANNED_FONTS: banned.setdefault(f, set()).add(idx)
            if sh["eq"]: eq_count += 1; continue
            # bảng: màu chữ trên nền ô
            for cell in sh["cells"]:
                if cell["color"]:
                    under = cell["fill"][0] if cell["fill"] else bgc
                    cr = contrast(cell["color"][0], under)
                    if cr < (3 if cell["sz"] >= 18 else 4.5): add("LỖI", idx, "màu", f"bảng: chữ '{cell['text'][:25]}' {cell['color'][0]} trên ô {under} tương phản {cr:.2f}")
                if formula_like(cell["text"]): add("CẢNH BÁO", idx, "công thức", f"bảng có công thức dạng chữ: '{cell['text'][:40]}' → dùng khối Equation (MS.equation) hoặc tách ra slide công thức")
            if not sh["paras"]: continue
            under, why = background_under(i, shapes, bgc)
            for para in sh["paras"]:
                full = "".join(r["text"] for r in para)
                texts.append((sh, full, para))
                for r in para:
                    if not r["color"]: continue
                    col, alpha = r["color"]
                    h, c = hue_chroma(col)
                    if c >= 0.35: text_hues.add(round(h / 30) % 12)
                    if why == "ảnh":
                        add("CẢNH BÁO", idx, "màu", f"'{sh['name']}': chữ đặt trực tiếp trên ảnh — thêm lớp phủ màu (độ trong 15–25%) hoặc dời chữ"); break
                    decorative = alpha < 0.6 or r["sz"] >= 90
                    cr = contrast(col, under)
                    need = 3.0 if (r["sz"] >= 18 or (r["sz"] >= 14 and r["b"])) else 4.5
                    if not decorative and cr < need:
                        add("LỖI", idx, "màu", f"'{sh['name']}': chữ '{r['text'][:30]}' {col} trên nền {under} tương phản {cr:.2f} < {need}")
                    if c >= 0.12: deck_colors.setdefault(col, set()).add(idx)
                    if lum(under) < 0.2 and not decorative:
                        if c >= 0.15 and 255 <= h <= 335:
                            add("LỖI", idx, "màu", f"'{sh['name']}': chữ tím {col} trên nền tối {under} bị chìm — dùng trắng, ngà hoặc màu sáng ấm/lục bạc hà")
                        elif c >= 0.12 and cr < 7:
                            add("LỖI", idx, "màu", f"'{sh['name']}': chữ màu {col} trên nền tối {under} chỉ {cr:.2f}:1 (cần ≥ 7:1 cho chữ màu trên nền tối)")
                    if opposite(col, under):
                        add("CẢNH BÁO" if decorative else "LỖI", idx, "màu", f"'{sh['name']}': chữ {col} trên nền {under} là hai màu đối nhau (rung màu, khó đọc) — đổi sang màu tương đồng hoặc trắng/ngà")
                    if same_hue(col, under):
                        lv = "GỢI Ý" if decorative else "CẢNH BÁO"
                        add(lv, idx, "màu", f"'{sh['name']}': chữ {col} cùng tông với nền {under} (đơn sắc, chữ chìm) — dùng trắng/ngà hoặc màu nhấn khác sắc")
                        break
            # ký hiệu/emoji đầu đoạn
            for para in sh["paras"]:
                full = "".join(r["text"] for r in para)
                if EMOJI.search(full): add("LỖI", idx, "dấu hiệu AI", f"emoji trong '{full[:40]}'")
                elif LEAD_SYMBOL.match(full): add("LỖI", idx, "dấu hiệu AI", f"ký hiệu/biểu tượng đứng đầu đoạn: '{full[:40]}'")
        # mảng màu đặt trên nền: không dùng màu đối nhau với nền slide
        for s in shapes:
            if s["fill"] and s["fill"][1] >= 0.5 and s["box"]:
                fc = s["fill"][0]
                if hue_chroma(fc)[1] >= 0.12: deck_colors.setdefault(fc, set()).add(idx)
                if opposite(fc, bgc) and s["box"][2] * s["box"][3] > 0.3:
                    add("CẢNH BÁO", idx, "màu", f"mảng '{s['name']}' {fc} đối nhau với nền {bgc} — dùng sắc tương đồng với nền")
        # icon đứng trước chữ, icon trong vòng tròn
        pics = [s for s in shapes if s["kind"] == "pic" and s["box"] and not s.get("descr", "").startswith(("makeslides-eq", "Logo")) and s["box"][2] <= 1.1 and s["box"][3] <= 1.1 and 0.6 <= s["box"][2] / max(s["box"][3], 0.01) <= 1.6]
        for pc in pics:
            px, py, pw, ph = pc["box"]
            for s in shapes:
                if not s["paras"] or not s["box"]: continue
                x, y, w, h = s["box"]
                right_of = px + pw - 0.05 <= x <= px + pw + 0.7 and y < py + ph and py < y + h
                below = py + ph - 0.05 <= y <= py + ph + 0.9 and x < px + pw and px < x + w
                if right_of or below:
                    add("LỖI", idx, "dấu hiệu AI", f"biểu tượng '{pc['name']}' đặt trước chữ '{s['name']}' — bỏ biểu tượng, dùng chữ đậm/số liệu/ảnh thật"); break
            for s in shapes:
                if s["geom"] == "ellipse" and s["box"] and inside((px + pw / 2, py + ph / 2), s["box"]):
                    add("LỖI", idx, "dấu hiệu AI", f"biểu tượng trong vòng tròn ('{s['name']}' + '{pc['name']}')"); break
        # chữ
        for sh, full, para in texts:
            low = full.lower().strip()
            if low in ("vs", "vs.", "v.s."): add("CẢNH BÁO", idx, "dấu hiệu AI", "vòng/nhãn 'VS' — để hai cột tự đối lập, bỏ chữ VS")
            if LABELS.match(low): add("CẢNH BÁO", idx, "dấu hiệu AI", f"nhãn khuôn mẫu '{full.strip()}' — để câu kết luận tự đứng")
            if CLICHE_CLOSE.search(full): add("CẢNH BÁO", idx, "dấu hiệu AI", f"lời kết sáo '{full[:40]}' — kết bằng thông điệp cần nhớ/liên hệ; lời cảm ơn để nhỏ")
            if NOT_ONLY.search(full): add("GỢI Ý", idx, "dấu hiệu AI", f"cấu trúc 'không chỉ… mà còn' — nói thẳng ý chính")
            for b in BUZZ:
                if b in low: add("CẢNH BÁO", idx, "dấu hiệu AI", f"từ sáo rỗng '{b}' trong '{full[:40]}'")
            dashes += len(re.findall(r"\s[–—]\s", full))
            if sh["name"] in ("title", "statement", "question") or sh["name"].startswith("title"):
                t = full.strip().rstrip(".").lower()
                if t in GENERIC_TITLES: add("CẢNH BÁO", idx, "dấu hiệu AI", f"tiêu đề chung chung '{full.strip()}' — viết tiêu đề là câu thông điệp")
                if re.search(r"\S:\s", full): title_colon += 1
            if formula_like(full): add("CẢNH BÁO", idx, "công thức", f"'{sh['name']}': '{full[:45]}' là công thức gõ bằng chữ → dùng khối Equation (MS.equation)")
        # ba ý dài bằng nhau
        for s in shapes:
            if len(s["paras"]) == 3:
                lens = [len("".join(r["text"] for r in p).split()) for p in s["paras"]]
                if min(lens) >= 3 and max(lens) - min(lens) <= 1: add("GỢI Ý", idx, "dấu hiệu AI", f"'{s['name']}': ba ý dài đúng bằng nhau ({lens}) — đổi độ dài, gộp hoặc bớt một ý")
        # lưới thẻ đều nhau
        cards = [s for s in shapes if s["geom"] in ("roundRect", "rect") and s["fill"] and s["box"] and 1.5 < s["box"][2] < 4 and s["box"][3] > 2]
        sizes = {(round(c["box"][2], 1), round(c["box"][3], 1)) for c in cards}
        if len(cards) >= 3 and len(sizes) == 1: add("GỢI Ý", idx, "dấu hiệu AI", f"{len(cards)} thẻ đúng bằng nhau xếp hàng — cân nhắc bố cục bất đối xứng (baThe không nền, bento, luoiThuySy)")
    # toàn bài
    nS = len(slides)
    for f, ss in banned.items(): add("LỖI", 0, "phông", f"phông {f} (đã loại khỏi gói) dùng ở slide {', '.join(map(str, sorted(ss)))} — đổi sang Montserrat hoặc Lexend")
    for i in range(2, nS):
        if sigs[i] and sigs[i] == sigs[i - 1] == sigs[i - 2]: add("CẢNH BÁO", i + 1, "dấu hiệu AI", f"slide {i - 1}–{i + 1} cùng một bố cục — đổi bố cục để tạo nhịp")
    dark = tones.count("tối")
    if nS and dark / nS > 0.5: add("CẢNH BÁO", 0, "màu", f"{dark}/{nS} slide nền tối — bài nặng màu; giữ nền tối cho bìa, chia phần, tuyên bố")
    run, prev = 0, None
    for i, t in enumerate(tones, 1):
        run = run + 1 if t == prev else 1; prev = t
        if run == 5: add("GỢI Ý", i, "màu", f"5 slide liên tiếp cùng nền {t} — chèn một slide khác nền để tạo nhịp")
    # cặp màu đối nhau cùng xuất hiện trong bài (ví dụ lam + cam, đỏ + lục)
    cols = sorted(deck_colors, key=lambda k: -len(deck_colors[k]))
    seen_pairs = set()
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            if opposite(a, b):
                key = tuple(sorted((round(ryb(hue_chroma(a)[0]) / 30), round(ryb(hue_chroma(b)[0]) / 30))))
                if key in seen_pairs: continue
                seen_pairs.add(key)
                add("CẢNH BÁO", 0, "màu", f"bài dùng cùng lúc {a} (slide {', '.join(map(str, sorted(deck_colors[a])[:4]))}) và {b} (slide {', '.join(map(str, sorted(deck_colors[b])[:4]))}) — hai màu đối nhau; giữ bảng màu tương đồng")
    if len(text_hues) > 3: add("CẢNH BÁO", 0, "màu", f"chữ dùng {len(text_hues)} sắc màu khác nhau — giữ 1 màu nhấn (+1 màu phụ)")
    if dashes > max(3, nS // 3): add("CẢNH BÁO", 0, "dấu hiệu AI", f"{dashes} gạch ngang ' – ' nối ý — viết thành câu hoặc dùng dấu phẩy, chấm")
    if title_colon > max(2, nS // 4): add("CẢNH BÁO", 0, "dấu hiệu AI", f"{title_colon} tiêu đề dạng 'A: B' — đa dạng hoá: câu khẳng định, câu hỏi, một cụm từ")
    return out, eq_count, nS

def main():
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    out, eq, n = check(sys.argv[1])
    order = {"LỖI": 0, "CẢNH BÁO": 1, "GỢI Ý": 2}
    seen, rows = set(), []
    for r in sorted(out, key=lambda r: (order[r[0]], r[1])):
        if r in seen: continue
        seen.add(r); rows.append(r)
    if "--json" in sys.argv:
        print(json.dumps([dict(muc=a, slide=b, nhom=c, noi_dung=d) for a, b, c, d in rows], ensure_ascii=False, indent=1))
    else:
        print(f"{sys.argv[1]}: {n} slide, {eq} khối equation")
        for lv in order:
            sub = [r for r in rows if r[0] == lv]
            print(f"\n{lv} ({len(sub)})")
            for _, s, g, m in sub: print(f"  [{'toàn bài' if s == 0 else 'slide ' + str(s)}] {g}: {m}")
    sys.exit(1 if any(r[0] == "LỖI" for r in rows) else 0)

if __name__ == "__main__":
    main()
