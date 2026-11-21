#!/usr/bin/env python3
"""kiem_tra_canva.py — kiểm tra thiết kế slide trên Canva từ dữ liệu `read-design`, không cần tải tệp.

Đầu vào: JSON của `read-design` mở phiên sửa (`open_transaction: true`, `fields: ["design_content"]`) —
cả phản hồi, chỉ phần `design_content`, hoặc dạng rút gọn chỉ giữ phần tử chữ:
  {"pages": [{"index": 1, "width": 1920, "height": 1080, "elements": [
      {"locator_id": "...", "type": "text", "top": 0, "left": 0, "width": 0, "height": 0, "opacity": 1,
       "rotation": 0, "textRegions": [{"characters": "...", "formatting": {"fontSize": 0, "color": "#ffffff",
       "fontWeight": "bold", "lineHeight": 1.1}}]}]}]}
Phần tử khác chữ (rect, ảnh) giữ top/left/width/height/type để kiểm tra chồng lấn với khối.

Kiểm tra từng trang:
  co-chu     cỡ chữ quy ra pt (trang 1920px = 960pt): nội dung < --co-toi-thieu, tiêu đề < --co-tieu-de, mọi chữ < 12pt
  luong-chu  số chữ/trang > --chu-toi-da; đoạn nhiều dòng quá dài
  bo-cuc     chữ đè chữ (theo vùng nét chữ ước tính), hai khối chữ quá sát, khung chữ hẹp hơn chữ (nét bị lòi/cắt),
             các hộp chữ ghép thành một dòng lệch chân chữ, lề trái lệch vài px, chữ ra ngoài/sát mép trang,
             chữ xoay, chữ mờ (độ đục < 100%)
  mau        màu chữ ngoài bảng màu (--bang-mau), cặp màu đối nhau (lam–cam, đỏ–lục, vàng–tím), > 3 sắc màu chữ
  dan-y      chữ không có trong dàn ý (Canva tự thêm, nhãn nội bộ bị chép), ý trong dàn ý bị thiếu (--dan-y)
  chu        chính tả, dấu câu, viết hoa, mã chữ — dùng lại bộ kiểm của kiem_soat_van_ban.py trên từng hộp chữ
             (giữ nguyên chỗ xuống dòng, không báo nhầm "dính chữ")

Dùng:
  python3 kiem_tra_canva.py canva.json [--boi-canh <khoá contexts.json>] [--bang-mau "#1F3A5F,#FAF7F0,#B8862B"]
                            [--dan-y dan_y.json] [--chi bo-cuc,co-chu] [--json]
  dan_y.json: {"sections": [{"title": "...", "points": ["..."], "description": "..."}]} — đúng outline đã gửi create-design.
Mỗi mục báo kèm locator_id để sửa bằng `edit-design`. Ước lượng chữ (bề rộng, chân chữ) là gần đúng: mục bố cục
phải được xác nhận bằng ảnh trang trả về sau mỗi lần sửa. Mã thoát 1 khi còn LỖI.
"""
import colorsys, json, os, re, sys, unicodedata
from collections import defaultdict
from difflib import SequenceMatcher

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
CONTEXTS = json.load(open(os.path.join(os.path.dirname(HERE), "assets", "contexts.json"), encoding="utf-8"))

# bề rộng ký tự trung bình (theo em) cho phông sans đậm vừa — đủ để phát hiện khung hẹp rõ rệt
def _w(ch):
    if ch.isdigit(): return 0.58
    if ch == " ": return 0.26
    if ch in "%@&": return 0.85
    if ch in ".,:;!'|ịíìỉĩi": return 0.27
    if ch in "-–()[]/": return 0.36
    if ch in "mwMW": return 0.86
    if ch.isupper(): return 0.68
    return 0.54
def be_rong(text, fs, spacing=0.0): return sum(_w(c) for c in text) * fs + max(0, len(text) - 1) * spacing * fs
TREN_CAO = set("ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ")
CO_DUOI = set("gjpqyịọụỵẹặậệợựạ,;")

def nap(path):
    d = json.load(open(path, encoding="utf-8"))
    if "design_content" in d: d = d["design_content"]
    pages = []
    for i, p in enumerate(d.get("pages", []), 1):
        dim = p.get("dimensions") or {}
        pages.append({"index": p.get("index", i), "width": p.get("width", dim.get("width", 1920)),
                      "height": p.get("height", dim.get("height", 1080)), "elements": p.get("elements", [])})
    return pages

def hop_chu(el):
    regs = el.get("textRegions") or []
    text = "".join(r.get("characters", "") for r in regs)
    fmts = [r.get("formatting", {}) for r in regs if r.get("characters", "").strip()]
    fs = max((f.get("fontSize", 0) for f in fmts), default=0)
    lh = max((f.get("lineHeight", 1.2) for f in fmts), default=1.2)
    sp = max((f.get("letterSpacing", 0) for f in fmts), default=0)
    lines = text.split("\n")
    x, y, w, h = el["left"], el["top"], el["width"], el["height"]
    one = len(lines) == 1 and h < fs * lh * 1.6
    base = y + (h - fs * lh * len(lines)) / 2 + (lh - 1) * fs / 2 + 0.8 * fs if fs else y   # chân chữ dòng đầu
    last_base = base + (len(lines) - 1) * fs * lh
    tall = any(c in TREN_CAO or c.isupper() or c in "bdfhklđtỉíìĩ" or unicodedata.normalize("NFD", c) != c for c in text)
    ink_top = base - (0.95 if tall else 0.55) * fs
    ink_bot = last_base + (0.22 if any(c in CO_DUOI for c in text) else 0.02) * fs
    widest = max((be_rong(l, fs, sp) for l in lines), default=0)
    return {"id": el.get("locator_id") or el.get("id"), "text": text, "lines": lines, "fs": fs, "lh": lh,
            "x": x, "y": y, "w": w, "h": h, "one": one, "base": base, "ink": (x, ink_top, x + min(w, widest), ink_bot),
            "widest": widest, "opacity": el.get("opacity", 1), "rot": el.get("rotation", 0),
            "colors": [f.get("color") for f in fmts if f.get("color")], "words": len(text.split()),
            "fonts": {f.get("fontRef") for f in fmts if f.get("fontRef")},
            "trang_tri": el.get("opacity", 1) < 0.99 or abs(el.get("rotation", 0)) > 0.5}

def hex2hsl(h):
    h = h.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, l, s = colorsys.rgb_to_hls(r, g, b); return hh * 360, s, l
def nhom_sac(h):
    hue, s, l = hex2hsl(h)
    if s < 0.25 or l > 0.92 or l < 0.08: return None
    for name, a, b in (("đỏ", 352, 15), ("cam", 15, 45), ("vàng", 45, 70), ("lục", 70, 170), ("lam", 170, 260), ("tím", 260, 318), ("hồng", 318, 352)):
        if (a <= hue < b) if a < b else (hue >= a or hue < b): return name
DOI = [("lam", "cam"), ("đỏ", "lục"), ("vàng", "tím")]
def khoang_mau(a, b):
    a, b = a.lstrip("#"), b.lstrip("#")
    return sum((int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) ** 2 for i in (0, 2, 4)) ** 0.5

def chuan(s): return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s).lower()).strip(" .,:;!?")

def kiem(pages, co_min=24, co_td=32, chu_max=30, bang_mau=None, dan_y=None):
    out = []
    def add(lv, p, nhom, msg, loc=None): out.append({"muc": lv, "trang": p, "nhom": nhom, "noi_dung": msg, "locator_id": loc})
    try:
        import kiem_soat_van_ban as K
    except Exception:
        K = None
    all_texts, kieu = [], {"cu": defaultdict(set), "moi": defaultdict(set)}
    for pg in pages:
        P, W, H = pg["index"], pg["width"], pg["height"]
        k = 960 / W                                  # px → pt (trang 16:9 rộng 13,33 in)
        boxes = [hop_chu(e) for e in pg["elements"] if e.get("type") == "text" and "".join(r.get("characters", "") for r in e.get("textRegions") or []).strip()]
        shapes = [e for e in pg["elements"] if e.get("type") != "text"]
        if not boxes: continue
        fmax = max(b["fs"] for b in boxes)
        for b in boxes:
            b["vai"] = "tieu-de" if b["fs"] >= 0.8 * fmax and b["words"] <= 14 else "noi-dung"
        # ---- cỡ chữ, lượng chữ
        words = sum(b["words"] for b in boxes)
        if words > chu_max: add("CẢNH BÁO", P, "luong-chu", f"{words} chữ trên trang (tối đa {chu_max}) — rút gọn, đưa chi tiết vào ghi chú diễn giả")
        for b in boxes:
            pt = b["fs"] * k
            t = b["text"].replace("\n", " / ")[:45]
            if b["trang_tri"]:
                if pt < 12: add("GỢI Ý", P, "co-chu", f"chữ trang trí '{t}' {pt:.0f}pt — không đọc được khi chiếu; xoá nếu không cần", b["id"])
            elif pt < 12: add("LỖI", P, "co-chu", f"'{t}' chỉ {pt:.0f}pt (< 12pt) — đặt font_size ≥ {int(co_min / k)}", b["id"])
            elif b["vai"] == "noi-dung" and pt < co_min: add("LỖI", P, "co-chu", f"'{t}' {pt:.0f}pt < {co_min}pt — đặt font_size ≥ {int(round(co_min / k))}", b["id"])
            elif b["vai"] == "tieu-de" and pt < co_td: add("CẢNH BÁO", P, "co-chu", f"tiêu đề '{t}' {pt:.0f}pt < {co_td}pt — đặt font_size ≥ {int(round(co_td / k))}", b["id"])
            if len(b["lines"]) > 4 and b["vai"] == "noi-dung": add("CẢNH BÁO", P, "luong-chu", f"'{t}' có {len(b['lines'])} dòng — tách bớt", b["id"])
            if b["opacity"] < 0.99: add("CẢNH BÁO", P, "bo-cuc", f"'{t}' mờ {b['opacity']:.0%} — đặt update_opacity = 1", b["id"])
            if abs(b["rot"]) > 0.5 and b["words"] >= 3: add("CẢNH BÁO", P, "bo-cuc", f"'{t}' xoay {b['rot']:.0f}° — chỉ xoay nhãn ngắn", b["id"])
            # ---- khung hẹp hơn chữ (một dòng)
            so = sum(ch.isdigit() or ch in "%" for ch in b["text"]) >= 0.6 * len(b["text"].replace(" ", ""))
            if b["one"] and b["widest"] > b["w"] * (1.02 if so else 1.08) + 1:      # chữ số ước lượng sát; chữ cái sai số lớn hơn
                add("CẢNH BÁO", P, "bo-cuc", f"khung '{t}' rộng {b['w']:.0f}px, chữ cần ~{b['widest']:.0f}px — nét có thể lòi/cắt; resize_element width ≈ {b['widest'] * 1.06:.0f} rồi xem ảnh", b["id"])
            if not b["one"] and not b["trang_tri"]:
                for l in b["lines"]:
                    if be_rong(l, b["fs"]) > b["w"] * 1.0 + 1:
                        add("CẢNH BÁO", P, "bo-cuc", f"dòng '{l[:30]}' (~{be_rong(l, b['fs']):.0f}px) có thể dài hơn khung {b['w']:.0f}px — sẽ ngắt thêm dòng, tràn thẻ; nới khung (resize_element) rồi xem ảnh", b["id"])
                        break
            # ---- mép trang
            m = 0.03 * W
            if b["x"] < -1 or b["y"] < -1 or b["x"] + b["w"] > W + 1 or b["y"] + b["h"] > H + 1:
                add("LỖI", P, "bo-cuc", f"'{t}' ra ngoài trang", b["id"])
            elif b["ink"][0] < m or b["ink"][1] < m * 0.8 or b["ink"][2] > W - m or b["ink"][3] > H - m * 0.8:
                add("CẢNH BÁO", P, "bo-cuc", f"'{t}' sát mép trang (lề an toàn {m:.0f}px)", b["id"])
        # ---- chữ đè chữ, quá sát
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, c = boxes[i], boxes[j]
                ax0, ay0, ax1, ay1 = a["ink"]; cx0, cy0, cx1, cy1 = c["ink"]
                ox, oy = min(ax1, cx1) - max(ax0, cx0), min(ay1, cy1) - max(ay0, cy0)
                ta, tc = a["text"].replace("\n", " ")[:25], c["text"].replace("\n", " ")[:25]
                if ox > 2 and oy > 0.1 * min(a["fs"], c["fs"]):
                    add("LỖI", P, "bo-cuc", f"chữ đè chữ: '{ta}' và '{tc}' chồng {ox:.0f}×{oy:.0f}px", a["id"])
                    continue
                if ox > 2 and oy > 2:
                    add("CẢNH BÁO", P, "bo-cuc", f"'{ta}' và '{tc}' gần chạm nhau theo chiều dọc — xem ảnh, giãn nếu dấu chạm chữ", a["id"])
                    continue
                gap_need = 0.12 * min(a["fs"], c["fs"])
                if oy > 0 and -gap_need < ox <= 2:
                    add("CẢNH BÁO", P, "bo-cuc", f"'{ta}' và '{tc}' cách nhau ngang chỉ {max(0, -ox):.0f}px — giãn ≥ {gap_need:.0f}px", c["id"])
                elif ox > 0 and -gap_need * 0.8 < oy <= 2:
                    add("CẢNH BÁO", P, "bo-cuc", f"'{ta}' và '{tc}' cách nhau dọc chỉ {max(0, -oy):.0f}px", c["id"])
        # ---- các hộp một dòng nằm cùng hàng phải cùng chân chữ
        row = [b for b in boxes if b["one"]]
        def cung_dong(b, c):
            return (min(b["ink"][3], c["ink"][3]) - max(b["ink"][1], c["ink"][1]) > 0.3 * min(b["fs"], c["fs"])
                    and c["x"] - (b["x"] + b["w"]) < 1.2 * max(b["fs"], c["fs"]) and b["x"] - (c["x"] + c["w"]) < 1.2 * max(b["fs"], c["fs"]))
        chua = list(row)
        while chua:
            g, moi = [chua.pop(0)], True
            while moi:
                moi = False
                for c in list(chua):
                    if any(cung_dong(z, c) for z in g): g.append(c); chua.remove(c); moi = True
            if len(g) < 2: continue
            g.sort(key=lambda z: z["x"])
            lech = max(z["base"] for z in g) - min(z["base"] for z in g)
            if lech > 0.06 * max(z["fs"] for z in g):
                ref = max(g, key=lambda z: z["fs"])
                goi_y = "; ".join(f"'{z['text'][:12]}' top ≈ {z['y'] + ref['base'] - z['base']:.0f}" for z in g if z is not ref)
                add("CẢNH BÁO", P, "bo-cuc", "các hộp '" + "' | '".join(z["text"][:15] for z in g) + f"' ghép thành một dòng nhưng lệch chân chữ {lech:.0f}px — căn theo '{ref['text'][:12]}': {goi_y}", ref["id"])
        # ---- lề trái lệch vài px
        lefts = sorted(((b["ink"][0], b) for b in boxes if b["w"] < W * 0.9), key=lambda t: t[0])
        for (x1, b1), (x2, b2) in zip(lefts, lefts[1:]):
            if 2.5 < x2 - x1 < 0.008 * W:
                add("GỢI Ý", P, "bo-cuc", f"lề trái '{b1['text'].replace(chr(10), ' ')[:15]}' ({x1:.0f}) và '{b2['text'].replace(chr(10), ' ')[:15]}' ({x2:.0f}) lệch {x2 - x1:.0f}px — căn thẳng một lề", b2["id"])
        # ---- chữ đè khối hình (khối nhỏ dạng thanh/vạch)
        for s in shapes:
            sx0, sy0, sx1, sy1 = s.get("left", 0), s.get("top", 0), s.get("left", 0) + s.get("width", 0), s.get("top", 0) + s.get("height", 0)
            if s.get("height", 0) > 0.12 * H and s.get("width", 0) > 0.12 * W: continue        # ảnh/khối lớn làm nền: bỏ qua
            for b in boxes:
                x0, y0, x1, y1 = b["ink"]
                if min(x1, sx1) - max(x0, sx0) > 4 and min(y1, sy1) - max(y0, sy0) > 2:
                    add("GỢI Ý", P, "bo-cuc", f"'{b['text'][:20]}' chạm khối/vạch nhỏ ({s.get('locator_id', '')[-8:]}) — xem ảnh, khối có thể có viền trong suốt", b["id"])
        # ---- màu
        cols = {c.lower() for b in boxes for c in b["colors"]}
        sac = {nhom_sac(c) for c in cols} - {None}
        for a_, b_ in DOI:
            if a_ in sac and b_ in sac: add("CẢNH BÁO", P, "mau", f"màu chữ có cặp đối nhau {a_}–{b_}")
        if bang_mau:
            for c in cols:
                if nhom_sac(c) and min(khoang_mau(c, m_) for m_ in bang_mau) > 60:
                    loc = next(b["id"] for b in boxes if c in [x.lower() for x in b["colors"]])
                    gan = min(bang_mau, key=lambda m_: khoang_mau(c, m_))
                    add("CẢNH BÁO", P, "mau", f"màu chữ {c} ({nhom_sac(c)}) ngoài bảng màu — đổi về {gan}", loc)
        if len(sac) > 3: add("CẢNH BÁO", P, "mau", f"{len(sac)} sắc màu chữ trên một trang ({', '.join(sorted(sac))})")
        # ---- chính tả, dấu câu, viết hoa (từng hộp, từng dòng)
        if K:
            for b in boxes:
                rl = "tieu-de" if b["vai"] == "tieu-de" else "noi-dung"
                for line in b["lines"]:
                    if not line.strip(): continue
                    tmp = []
                    K.kiem_chu(line, P, "canva", rl, lambda lv, s, g, msg, sua=False: tmp.append((lv, g, msg)), kieu,
                               defaultdict(lambda: defaultdict(set)), [], {"thang": set(), "cong": set()}, {"...": set(), "…": set()},
                               set(), defaultdict(set), {"runs": [], "bullet": False})
                    for lv, g, msg in tmp:
                        if "đầu đoạn viết thường" in msg: continue
                        add(lv, P, "chu", msg.replace("'canva': ", f"'{line[:25]}': ", 1) if msg.startswith("'canva'") else msg, b["id"])
        all_texts += [(P, b) for b in boxes]
    # ---- phông: một phông vừa hiện chữ Nhật/Trung vừa hiện chữ Việt có dấu thường thiếu một trong hai bộ chữ
    CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]")
    HAN = re.compile(r"[\u3400-\u9fff]")
    dung = defaultdict(lambda: {"cjk": False, "han": False, "viet": False})
    for P, b in all_texts:
        for f in b["fonts"]:
            dung[f]["cjk"] |= bool(CJK.search(b["text"])); dung[f]["han"] |= bool(HAN.search(b["text"]))
            dung[f]["viet"] |= any(K and c in K.VN_DAU for c in b["text"])
    gom = defaultdict(lambda: {"viet": [], "han": []})
    for P, b in all_texts:
        for f in b["fonts"]:
            if not (dung[f]["cjk"] and dung[f]["viet"]): continue
            if K and any(c in K.VN_DAU for c in b["text"]): gom[f]["viet"].append((P, b))
            elif HAN.search(b["text"]): gom[f]["han"].append((P, b))
    for f, g in gom.items():
        ten = f.split(",")[0]
        if g["viet"]:
            vd = "; ".join(f"trang {P} '{b['text'].replace(chr(10), ' ')[:18]}'" for P, b in g["viet"][:4])
            add("CẢNH BÁO", 0, "phong", f"phông {ten} hiện cả chữ Nhật/Trung lẫn {len(g['viet'])} hộp chữ Việt ({vd}…) — phông chữ Nhật hay thiếu dấu tiếng Việt (ra 'C ng học'); xem ảnh các hộp này, thiếu dấu thì tạo lại hộp chữ (mục 6 quy-trinh-canva.md)", g["viet"][0][1]["id"])
        if g["han"]:
            vd = "; ".join(f"trang {P} '{b['text'][:8]}'" for P, b in g["han"][:4])
            add("CẢNH BÁO", 0, "phong", f"phông {ten} hiện chữ Việt và {len(g['han'])} hộp chữ Hán ({vd}) — chữ Hán có thể hiện ô vuông □; xem ảnh", g["han"][0][1]["id"])
    if kieu["cu"] and kieu["moi"]:
        add("CẢNH BÁO", 0, "chu", f"lẫn kiểu bỏ dấu cũ ({', '.join(list(kieu['cu'])[:3])}) và mới ({', '.join(list(kieu['moi'])[:3])})")
    # ---- đối chiếu dàn ý
    if dan_y:
        items = []
        for sec in dan_y.get("sections", []):
            items += [sec.get("title", "")] + list(sec.get("points") or [])
        src = [chuan(x) for x in items if x.strip()]
        desc_tok = set(" ".join(chuan(sec.get("description", "")) for sec in dan_y.get("sections", [])).split())
        tu = lambda x: re.findall(r"[^\W_]+", x)
        vocab = set(tu(" ".join(src))) | set(tu(" ".join(desc_tok)))
        def bo_dau(w): return "".join(c for c in unicodedata.normalize("NFD", w) if not unicodedata.combining(c)).replace("đ", "d")
        goc = defaultdict(set)
        for w in vocab: goc[bo_dau(w)].add(w)
        NHAN = re.compile(r"^(slide|trang)\b|\b(slide bìa|slide kết|thông điệp kết|thông điệp chính|chia phần|phần mở đầu|lời kết|bố cục|ý chính|nội dung chính)\b")
        def trong_dan_y(t):
            return any(t in x or x in t or SequenceMatcher(None, t, x).ratio() > 0.72 for x in src)
        for P, b in all_texts:
            for line in b["lines"]:
                t = chuan(line)
                sai_dau = False
                ws = re.findall(r"[^\W\d_]+", t)
                for w in ws:                                                 # sai dấu so với dàn ý: phần còn lại của dòng phải khớp dàn ý
                    khac = [x for x in ws if x != w]
                    if khac and sum(x in vocab for x in khac) / len(khac) < 0.5: continue
                    if w not in vocab and goc.get(bo_dau(w)):
                        sai_dau = True
                        add("CẢNH BÁO", P, "dan-y", f"'{w}' không có trong dàn ý, gần với '{'/'.join(sorted(goc[bo_dau(w)]))}' — sai dấu? (find_and_replace_text)", b["id"])
                if sai_dau or not t or len(t) < 3 or re.fullmatch(r"[\d%.,\s–-]+", t) or trong_dan_y(t): continue
                if NHAN.search(t) and len(t.split()) <= 5:
                    add("LỖI", P, "dan-y", f"'{line[:40]}' là nhãn/chỉ dẫn nội bộ bị chép lên slide — xoá (delete_element)", b["id"])
                    continue
                tok = tu(t) or [t]
                if sum(w in vocab for w in tok) / len(tok) >= 0.6: continue           # lấy từ dàn ý/mô tả, chỉ tách dòng khác
                if b["trang_tri"]:
                    add("GỢI Ý", P, "dan-y", f"chữ trang trí '{line[:30]}' Canva tự thêm — kiểm tra đúng chính tả/nghĩa (kể cả tiếng nước ngoài), không dùng tên sách/thương hiệu thật", b["id"])
                else:
                    add("CẢNH BÁO", P, "dan-y", f"'{line[:40]}' không có trong dàn ý — Canva tự thêm; xoá hoặc thay bằng ý trong dàn ý", b["id"])
        by_page = defaultdict(str)
        for P, b in all_texts: by_page[0] += " " + chuan(b["text"])
        shown = set(tu(by_page[0]))
        for s_ in src:
            tok = tu(s_)
            if tok and sum(w in shown for w in tok) / len(tok) < 0.85:
                add("CẢNH BÁO", 0, "dan-y", f"ý trong dàn ý không thấy đủ trên slide: '{s_[:50]}'")
    return out

def main():
    a = sys.argv[1:]
    if not a or a[0].startswith("-"): print(__doc__); sys.exit(2)
    arg = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    bc = CONTEXTS.get(arg("--boi-canh")) if arg("--boi-canh") else None
    co_min = int(arg("--co-toi-thieu", bc["body_min"] if bc else 24))
    co_td = int(arg("--co-tieu-de", bc.get("title_min", 32) if bc else 32))
    chu_max = int(arg("--chu-toi-da", bc["max_words"] if bc else 30))
    bang = [x.strip() for x in arg("--bang-mau", "").split(",") if x.strip()] or None
    dy = json.load(open(arg("--dan-y"), encoding="utf-8")) if arg("--dan-y") else None
    out = kiem(nap(a[0]), co_min, co_td, chu_max, bang, dy)
    if arg("--chi"): out = [o for o in out if o["nhom"] in arg("--chi").split(",")]
    order = {"LỖI": 0, "CẢNH BÁO": 1, "GỢI Ý": 2}
    seen, rows = set(), []
    for o in sorted(out, key=lambda o: (order[o["muc"]], o["trang"])):
        k = (o["muc"], o["trang"], o["noi_dung"])
        if k not in seen: seen.add(k); rows.append(o)
    if "--json" in a: print(json.dumps(rows, ensure_ascii=False, indent=1))
    else:
        for lv in order:
            sub = [r for r in rows if r["muc"] == lv]
            print(f"\n{lv} ({len(sub)})")
            for r in sub:
                print(f"  [{'toàn bài' if r['trang'] == 0 else 'trang ' + str(r['trang'])}] {r['nhom']}: {r['noi_dung']}" + (f"  ⟨{r['locator_id']}⟩" if r["locator_id"] else ""))
    sys.exit(1 if any(r["muc"] == "LỖI" for r in rows) else 0)

if __name__ == "__main__":
    main()
