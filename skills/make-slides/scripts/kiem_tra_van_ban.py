#!/usr/bin/env python3
"""kiem_tra_van_ban.py — kiểm tra (và tự sửa) VĂN BẢN trên slide: đọc được, không quá nhiều chữ, giãn dòng, hài hoà cỡ chữ,
và đặc biệt là CÁCH XUỐNG DÒNG — đo bằng chính phông chữ của bài (assets/fonts) như PowerPoint dàn chữ.

Kiểm:
  1. Cỡ chữ: nội dung ≥ --co-toi-thieu (mặc định 24pt); chữ phụ (nguồn, chú thích, thông tin, nhãn) ≥ --co-phu (16pt).
  2. Lượng chữ: số chữ nội dung mỗi slide ≤ --chu-toi-da (30); mỗi ý ≤ 2 dòng; mỗi hộp ≤ 5 dòng.
  3. Giãn dòng: đoạn nhiều dòng phải 90–140% (tiêu đề 85–115%).
  4. Hài hoà: tiêu đề ≥ 1,25 × chữ nội dung; ≤ 4 cỡ chữ mỗi slide; tiêu đề cùng cỡ trong cả bài.
  5. Tràn khung: tổng chiều cao dòng vượt khung.
  6. Dòng mồ côi: dòng cuối đoạn chỉ còn 1 chữ, hoặc quá ngắn (< 20% bề rộng, ≤ 2 chữ); dòng ngắn bất thường giữa đoạn.
  7. Tiêu đề 2 dòng: dòng trên phải NGẮN hơn dòng dưới; điểm ngắt phải ở ranh giới cụm từ (không tách từ ghép,
     không để dòng kết thúc bằng hư từ "của, và, với, các…", không tách số – đơn vị).
  8. Ngắt dòng chủ ý (xuống dòng bằng tay): không làm rời cụm từ / đổi nghĩa câu.
  9. Tiêu đề sáo rỗng kiểu đếm số: "Ba phương pháp…", "Ba con số đáng chú ý", "4 phần trong lộ trình".

Dùng:
  python3 kiem_tra_van_ban.py Slide.pptx [--co-toi-thieu 24] [--chu-toi-da 30] [--json]
  python3 kiem_tra_van_ban.py Slide.pptx --sua Slide_da_sua.pptx     # tự khắc phục phần sửa được, rồi kiểm lại
Tách từ ghép tiếng Việt bằng pyvi nếu cài được (pip install pyvi --break-system-packages); không có thì dùng danh sách từ ghép có sẵn.
Tự sửa (không đổi câu chữ): giảm cỡ chữ từng bước (không dưới mức tối thiểu) để hết dòng mồ côi/tràn khung; chèn ngắt dòng
đúng ranh giới cụm từ cho tiêu đề 2 dòng (dòng trên ngắn hơn); thay khoảng trắng số – đơn vị bằng khoảng trắng không ngắt.
Phần không tự sửa được (cần rút gọn hoặc kéo dài nội dung) được báo kèm gợi ý số chữ cần bớt/thêm.
"""
import json, os, re, sys, zipfile
import xml.etree.ElementTree as ET
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kiem_tra_slide import NS, resolve_mc  # noqa: E402

FONT_DIR = os.path.join(ROOT, "assets", "fonts")
FILES = json.load(open(os.path.join(FONT_DIR, "files.json"), encoding="utf-8"))
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
EMU_PT = 12700
NBSP = "\u00a0"

# hư từ: không để cuối dòng (làm rời cụm), nên đứng ĐẦU dòng sau
HU_TU = set("của và với các những cho để khi từ đến theo về tại là như hay hoặc mà nhưng do vì nên thì một mỗi rằng trong ngoài trên dưới giữa qua bởi được bị đã đang sẽ cũng còn rất quá không chưa có này kia ấy nào bằng nhằm dùng giúp tới sau trước dù nếu tuy".split())
# động từ vị ngữ thường gặp: ngắt TRƯỚC chúng = tách chủ ngữ | vị ngữ, tự nhiên cho tiêu đề ("Cầu chia áp | giữ điểm làm việc ổn định")
DONG_TU = set("giữ tăng giảm nâng hạ làm tạo giúp quyết cần phải chỉ đạt mở đổi thay ảnh tác dẫn đưa chiếm vượt cải góp mang đem biến chuyển thúc hỗ đẩy kéo xây hình phát thu tiết bảo".split())
# từ ghép thường gặp: không được tách qua hai dòng (bổ sung dần khi gặp)
TU_GHEP = set(x.strip() for x in """hành vi, học tập, sinh viên, học sinh, giáo viên, xã hội, mạng xã, công nghệ, giáo dục, khuếch đại, phân cực, thiết kế, làm việc,
kết quả, đánh giá, nguyên lý, hoạt động, phương pháp, nghiên cứu, thực trạng, giải pháp, chất lượng, phát triển, nhà trường, chuyển đổi, trí tuệ, nhân tạo,
dữ liệu, khoa học, văn học, lịch sử, văn hoá, văn hóa, kinh tế, môi trường, biến đổi, khí hậu, đồng bằng, sức khỏe, sức khoẻ, điện tử, mạch điện, tín hiệu,
trở kháng, độ lợi, điện áp, dòng điện, ổn định, thời gian, thời lượng, trung bình, xao nhãng, tự học, bài vở, trao đổi, khảo sát, phỏng vấn, năm nhất,
quan trọng, hiệu quả, chương trình, kế hoạch, báo cáo, tổng kết, ứng dụng, dạy học, ngữ văn, tác động, ảnh hưởng, thông tin, truyền thông, cộng đồng,
gia đình, kỹ năng, kĩ năng, năng lực, phẩm chất, tư duy, sáng tạo, vấn đề, nội dung, mục tiêu, nhiệm vụ, quản lý, quản lí, tài chính, doanh nghiệp,
thị trường, sản phẩm, dịch vụ, khách hàng, an toàn, bảo mật, hệ thống, phần mềm, phần cứng, thuật toán, lập trình, mô hình, thí nghiệm, phản ứng,
tế bào, di truyền, sinh học, hoá học, hóa học, vật lý, vật lí, toán học, hình học, đại số, xác suất, thống kê, bền vững, nông nghiệp, thuỷ sản, thủy sản,
du lịch, di sản, lễ hội, truyền thống, dân tộc, địa phương, tri thức, hạnh phúc, tự do, công bằng, bình đẳng, đạo đức, pháp luật, chính sách, tâm lý,
tâm lí, nhận thức, cảm xúc, động lực, áp lực, tuổi trẻ, thanh niên, điện thoại, máy tính, trực tuyến, kết luận, tổng quan, giới thiệu, cầu chia, chia áp,
điểm làm, vùng tích, tích cực, bão hòa, bão hoà""".replace("\n", " ").split(","))
DON_VI = r"(?:V|mV|kV|A|mA|µA|μA|Ω|kΩ|MΩ|W|kW|Hz|kHz|MHz|GHz|s|ms|µs|F|µF|μF|nF|pF|dB|%|°C|m|cm|mm|km|kg|g|tấn|ha|đồng|triệu|tỷ|nghìn|giờ|phút|giây|ngày|tháng|năm|lần|học sinh|sinh viên|người|trường|tiết|bài|điểm)"
SO_DON_VI = re.compile(r"(\d[\d.,]*) (" + DON_VI + r")(?![\w])")
SAO_RONG = re.compile(r"^\s*(?:(?:hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|\d+)\s+(?:phương pháp|cách|bước|con số|số liệu|điểm|ý|lý do|yếu tố|giải pháp|bài học|vấn đề|phần|nội dung|đặc điểm|nguyên tắc|mục tiêu|xu hướng|thách thức|lợi ích|kỹ năng|trụ cột|chặng|giai đoạn|câu hỏi|điều)\b"
                      r"|.*\b(?:đáng chú ý|nổi bật|quan trọng nhất|cần biết|bạn nên biết|trong lộ trình|cốt lõi)\s*$)", re.I)
TEN_PHU = re.compile(r"^(source|info|contact|kicker|hint|by|lockup|brandmark|hchon|sec|!!sec|given|cap\d+|sn\d+|dn\d+|xl|yl|note|role)$")
TEN_TIEU_DE = re.compile(r"^(title|statement|question|big)$")
TEN_TRANG_TRI = re.compile(r"^(!!.*|bignum|!!sec|word|mark|eq.*|sym\d+|v\d+|value|mk\d+|an\d+|num\d+|herotxt)$")

_font_cache = {}
def font_for(face, bold, italic, size):
    f = FILES.get(face)
    path = None
    if f:
        slot = "boldItalic" if bold and italic else "bold" if bold else "italic" if italic else "regular"
        path = os.path.join(FONT_DIR, f.get(slot) or f.get("bold" if bold else "regular") or f["regular"])
    path = path or FALLBACK
    key = (path, round(size * 4))
    if key not in _font_cache: _font_cache[key] = ImageFont.truetype(path, max(1, round(size * 4)))   # đo ở 4× rồi chia
    return _font_cache[key], (f is not None)

def width(text, face, bold, italic, size, spc=0):
    if not text: return 0.0
    fnt, _ = font_for(face, bold, italic, size)
    return fnt.getlength(text) / 4 + spc * len(text)

def line_ratio(face, bold, italic):
    fnt, _ = font_for(face, bold, italic, 20)
    a, d = fnt.getmetrics()
    return (a + d) / (20 * 4)

# ---------------------------------------------------------------- đọc hộp chữ
def read_boxes(xml):
    root = resolve_mc(ET.fromstring(xml))
    boxes = []
    for sp in root.iter(f"{{{NS['p']}}}sp"):
        if sp.find(".//{http://schemas.microsoft.com/office/drawing/2010/main}m") is not None: continue   # khối equation
        tb = sp.find("p:txBody", NS)
        if tb is None: continue
        nv = sp.find(".//p:cNvPr", NS); name = nv.get("name") if nv is not None else ""
        x = sp.find(".//a:xfrm", NS)
        if x is None: continue
        ext = x.find("a:ext", NS); off = x.find("a:off", NS)
        bp = tb.find("a:bodyPr", NS)
        ins = lambda k, d: int(bp.get(k, d)) / EMU_PT if bp is not None else d / EMU_PT
        W = int(ext.get("cx")) / EMU_PT - ins("lIns", 91440) - ins("rIns", 91440)
        H = int(ext.get("cy")) / EMU_PT - ins("tIns", 45720) - ins("bIns", 45720)
        wrap = (bp.get("wrap") if bp is not None else None) != "none"
        paras = []
        for p in tb.findall("a:p", NS):
            ppr = p.find("a:pPr", NS)
            ln = ppr.find("a:lnSpc/a:spcPct", NS) if ppr is not None else None
            lnpts = ppr.find("a:lnSpc/a:spcPts", NS) if ppr is not None else None
            sb = ppr.find("a:spcBef/a:spcPts", NS) if ppr is not None else None
            sa = ppr.find("a:spcAft/a:spcPts", NS) if ppr is not None else None
            segs, cur = [], []
            for el in p:
                tag = el.tag.split("}")[1]
                if tag == "r":
                    rp = el.find("a:rPr", NS); t = el.find("a:t", NS)
                    if t is None or not t.text: continue
                    lat = rp.find("a:latin", NS) if rp is not None else None
                    cur.append({"text": t.text, "sz": int(rp.get("sz", "1800")) / 100 if rp is not None else 18,
                                "b": rp is not None and rp.get("b") == "1", "i": rp is not None and rp.get("i") == "1",
                                "face": lat.get("typeface") if lat is not None else "Montserrat", "spc": int(rp.get("spc", "0")) / 100 if rp is not None else 0})
                elif tag == "br":
                    segs.append(cur); cur = []
            segs.append(cur)
            if not any(seg for seg in segs): continue
            paras.append({"segs": segs, "lnPct": int(ln.get("val")) / 100000 if ln is not None else 1.0, "lnPts": int(lnpts.get("val")) / 100 if lnpts is not None else None,
                          "bef": int(sb.get("val")) / 100 if sb is not None else 0, "aft": int(sa.get("val")) / 100 if sa is not None else 0, "el": p})
        if paras: boxes.append({"name": name, "W": W, "H": H, "y": int(off.get("y")) / 914400 if off is not None else 0, "wrap": wrap, "paras": paras, "sp": sp})
    return boxes

# ---------------------------------------------------------------- dàn dòng (greedy, như PowerPoint: ngắt ở khoảng trắng thường)
def tokens(seg, scale=1.0):
    """chia đoạn thành 'từ' (giữa khoảng trắng thường; NBSP giữ dính) kèm bề rộng"""
    out = []
    for r in seg:
        parts = re.split(r"( )", r["text"])
        for pt in parts:
            if pt == "": continue
            w = width(pt, r["face"], r["b"], r["i"], r["sz"] * scale, r["spc"])
            if pt == " ":
                out.append({"sp": True, "w": w, "t": " "})
            elif out and not out[-1].get("sp") and not out[-1].get("end"):
                out[-1]["t"] += pt; out[-1]["w"] += w        # nối mảnh cùng từ khác run
            else:
                out.append({"sp": False, "w": w, "t": pt})
        if out: out[-1]["end"] = False
    words, pending_space = [], 0.0
    for tk in out:
        if tk["sp"]:
            if words: words[-1]["space"] = words[-1].get("space", 0) + tk["w"]
        else:
            words.append({"t": tk["t"], "w": tk["w"], "space": 0.0})
    return words

def wrap_words(words, W, do_wrap=True):
    lines, cur, cw = [], [], 0.0
    for wd in words:
        add = wd["w"] if not cur else cur[-1]["space"] + wd["w"]
        if do_wrap and cur and cw + add > W + 0.6:
            lines.append(cur); cur, cw = [wd], wd["w"]
        else:
            cur.append(wd); cw += add
    if cur: lines.append(cur)
    return lines

def line_w(line): return sum(w["w"] for w in line) + sum(w["space"] for w in line[:-1])
def line_t(line): return " ".join(w["t"] for w in line)

def layout(box, scale=1.0):
    """trả về [(para, [ [lines của seg] ])], tổng chiều cao"""
    res, total = [], 0.0
    for i, p in enumerate(box["paras"]):
        segs_lines = []
        maxsz, face, b, it = 0, "Montserrat", False, False
        for seg in p["segs"]:
            for r in seg:
                if r["sz"] > maxsz: maxsz, face, b, it = r["sz"], r["face"], r["b"], r["i"]
            segs_lines.append(wrap_words(tokens(seg, scale), box["W"], box["wrap"]) if seg else [[]])
        n = sum(len(sl) for sl in segs_lines)
        lh = p["lnPts"] if p["lnPts"] else maxsz * scale * line_ratio(face, b, it) * p["lnPct"]
        total += n * lh + (p["bef"] if i else 0) + (p["aft"] if i < len(box["paras"]) - 1 else 0)
        res.append((p, segs_lines, maxsz * scale))
    return res, total

# ---------------------------------------------------------------- phân loại & luật
def role(box):
    n = box["name"]
    sizes = [r["sz"] for p in box["paras"] for s in p["segs"] for r in s]
    if not sizes: return "khac"
    if TEN_TRANG_TRI.match(n) or max(sizes) >= 72: return "trang-tri"
    if TEN_TIEU_DE.match(n) or n.startswith("title"): return "tieu-de"
    if TEN_PHU.match(n): return "phu"
    return "noi-dung"

def ends_bad(word):
    w = word.strip(",.;:").lower()
    return w in HU_TU

# Tách từ tiếng Việt bằng pyvi (nếu có: pip install pyvi --break-system-packages) → biết chính xác cặp âm tiết nào là một từ ghép
try:
    from pyvi import ViTokenizer
except Exception:  # không có pyvi: chỉ dùng danh sách TU_GHEP
    ViTokenizer = None
_PAIRS = set()
def nap_tu_ghep(text):
    """nạp các cặp âm tiết thuộc cùng một từ trong đoạn đang xét"""
    global _PAIRS
    _PAIRS = set()
    if not ViTokenizer or not text.strip(): return
    for tok in ViTokenizer.tokenize(text.replace(NBSP, " ")).split():
        syl = tok.lower().split("_")
        for x, y in zip(syl, syl[1:]): _PAIRS.add((x, y))

def splits_compound(a, b):
    x = a.replace(NBSP, " ").split(" ")[-1].strip(",.;:!?“”\"()").lower()
    y = b.replace(NBSP, " ").split(" ")[0].strip(",.;:!?“”\"()").lower()
    return f"{x} {y}" in TU_GHEP or (x, y) in _PAIRS

def best_break(words, W, prefer_top_short=True):
    """chọn điểm ngắt 2 dòng: dòng trên ≤ dòng dưới, ngắt ở ranh giới cụm (trước hư từ/sau dấu câu), không để dòng trên kết thúc bằng hư từ"""
    cands = []
    for k in range(1, len(words)):
        l1, l2 = words[:k], words[k:]
        w1, w2 = line_w(l1), line_w(l2)
        if w1 > W + 0.6 or w2 > W + 0.6: continue
        last = l1[-1]["t"]; first = l2[0]["t"]
        ranh_gioi = first.strip(",.").lower() in HU_TU or last.endswith((",", ":", ";", "–", "—"))
        score = 100.0 if ranh_gioi else 75.0 if first.lower() in DONG_TU else 0.0                       # chỉ ngắt ở ranh giới cụm từ: trước hư từ / sau dấu câu
        if ends_bad(last): score -= 200                            # dòng trên kết thúc bằng hư từ → rời cụm
        if splits_compound(last, first): score -= 200             # tách từ ghép (hành | vi)
        if re.match(r"^\d", last) and re.match(DON_VI, first): score -= 200
        if prefer_top_short:
            score += 20 if w1 <= w2 + 1 else -150      # quy tắc cứng: dòng trên phải ngắn hơn dòng dưới
        score -= abs(w1 / (w1 + w2) - 0.42) * 40                  # dòng trên ~42% tổng: cân, dòng dưới dài hơn
        cands.append((score, k, w1, w2))
    return max(cands) if cands else None

def kiem(path, co_min=24, co_phu=16, chu_max=30):
    z = zipfile.ZipFile(path)
    slides = sorted([n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)], key=lambda n: int(re.findall(r"\d+", n)[-1]))
    out, title_sizes = [], {}
    add = lambda lv, s, m, fix=None: out.append({"muc": lv, "slide": s, "noi_dung": m, "sua": fix})
    for idx, n in enumerate(slides, 1):
        boxes = read_boxes(z.read(n))
        words_body, sizes_slide, title_sz, body_sz = 0, set(), None, []
        for bx in boxes:
            rl = role(bx)
            if rl in ("trang-tri", "khac"): continue
            lay, total = layout(bx)
            szs = [r["sz"] for p in bx["paras"] for s in p["segs"] for r in s]
            sizes_slide.update(szs)
            txt = " ".join(r["text"] for p in bx["paras"] for s in p["segs"] for r in s)
            nm = bx["name"]
            # 1. cỡ chữ
            if rl == "noi-dung":
                body_sz += szs
                words_body += len(txt.split())
                if min(szs) < co_min: add("LỖI", idx, f"'{nm}': chữ nội dung {min(szs):g}pt < {co_min}pt — khó đọc ở cuối phòng", ("co", nm))
            elif rl == "phu" and min(szs) < co_phu:
                add("CẢNH BÁO", idx, f"'{nm}': chữ phụ {min(szs):g}pt < {co_phu}pt", ("co", nm))
            elif rl == "tieu-de":
                title_sz = max(szs)
                if nm == "title" and bx["y"] < 1.3: title_sizes.setdefault(title_sz, []).append(idx)   # chỉ tiêu đề slide nội dung (đầu trang)
                if max(szs) < max(co_min + 4, 28): add("LỖI", idx, f"'{nm}': tiêu đề {max(szs):g}pt quá nhỏ (cần ≥ {max(co_min + 4, 28)}pt)")
                if SAO_RONG.search(txt): add("CẢNH BÁO", idx, f"tiêu đề sáo rỗng kiểu đếm số: '{txt}' — viết thành thông điệp (kết luận, phát hiện, câu hỏi) thay vì đếm mục")
            # 5. tràn khung
            one_line = sum(len([ln for sl in s_ for ln in sl if ln]) for (_, s_, _) in lay) <= 1
            if total > bx["H"] + 2 and not one_line:   # một dòng vượt chiều cao khung chút ít: PowerPoint không cắt, bỏ qua
                add("LỖI", idx, f"'{nm}': chữ tràn khung ({total:.0f}pt > {bx['H']:.0f}pt) — rút gọn nội dung hoặc giảm cỡ (không dưới {co_min}pt)", ("tran", nm))
            nlines_box = 0
            for (p, segs_lines, psz) in lay:
                lines_all = [ln for sl in segs_lines for ln in sl if ln]
                nlines_box += len(lines_all)
                # 3. giãn dòng
                if len(lines_all) >= 2 and not p["lnPts"]:
                    lo, hi = (0.85, 1.15) if rl == "tieu-de" else (0.9, 1.4)
                    if p["lnPct"] < lo: add("LỖI", idx, f"'{nm}': giãn dòng {p['lnPct']:.0%} quá sít (cần {lo:.0%}–{hi:.0%})", ("gian", nm))
                    elif p["lnPct"] > hi: add("CẢNH BÁO", idx, f"'{nm}': giãn dòng {p['lnPct']:.0%} quá thưa (cần {lo:.0%}–{hi:.0%})", ("gian", nm))
                # 2. mỗi ý ≤ 2 dòng (nội dung)
                if rl == "noi-dung" and len(lines_all) > 2:
                    add("CẢNH BÁO", idx, f"'{nm}': một ý dài {len(lines_all)} dòng — rút còn ≤ 2 dòng (chi tiết đưa vào ghi chú)")
                nap_tu_ghep(" ".join(r["text"] for s in p["segs"] for r in s))
                for si, sl in enumerate(segs_lines):
                    sl = [ln for ln in sl if ln]
                    if not sl: continue
                    # 6. dòng mồ côi / dòng quá ngắn
                    if len(sl) >= 2:
                        last = sl[-1]
                        short = len(last) == 1 or (len(last) <= 2 and line_w(last) < 0.2 * bx["W"])
                        if short and rl != "trang-tri":
                            add("LỖI", idx, f"'{nm}': dòng cuối chỉ còn '{line_t(last)}' — giảm cỡ, rút gọn hoặc kéo dài câu", ("mo-coi", nm))
                        for ln in sl[:-1]:
                            if line_w(ln) < 0.25 * bx["W"] and si == 0 and len(segs_lines) == 1:
                                add("CẢNH BÁO", idx, f"'{nm}': dòng '{line_t(ln)}' ngắn bất thường giữa đoạn")
                        # dòng kết thúc bằng hư từ / tách số – đơn vị (xuống dòng tự động)
                        for a_, b_ in zip(sl[:-1], sl[1:]):
                            if ends_bad(a_[-1]["t"]):
                                add("CẢNH BÁO" if rl != "tieu-de" else "LỖI", idx, f"'{nm}': dòng kết thúc bằng hư từ '{a_[-1]['t']}' (… {line_t(a_[-2:])} | {line_t(b_[:2])} …) — cụm từ bị tách", ("ngat", nm))
                            if splits_compound(a_[-1]["t"], b_[0]["t"]):
                                add("LỖI", idx, f"'{nm}': xuống dòng tách từ ghép '{a_[-1]['t']} | {b_[0]['t']}' — đổi nghĩa/khó đọc; giảm cỡ, rút gọn hoặc ngắt dòng chủ động", ("ngat", nm))
                            if re.match(r"^\d[\d.,]*$", a_[-1]["t"]) and re.match(DON_VI + "$", b_[0]["t"]):
                                add("LỖI", idx, f"'{nm}': số và đơn vị bị tách '{a_[-1]['t']} | {b_[0]['t']}' — dùng khoảng trắng không ngắt", ("nbsp", nm))
                    # 7. tiêu đề 2 dòng: dòng trên ngắn hơn
                    if rl == "tieu-de" and len(segs_lines) == 1 and len(sl) == 2:
                        w1, w2 = line_w(sl[0]), line_w(sl[1])
                        if w1 > w2 + 2:
                            add("CẢNH BÁO", idx, f"'{nm}': tiêu đề 2 dòng, dòng trên dài hơn ('{line_t(sl[0])}' | '{line_t(sl[1])}') — ưu tiên dòng trên ngắn, dòng dưới dài", ("tieu-de-2", nm))
                    if rl == "tieu-de" and len(sl) >= 3:
                        add("CẢNH BÁO", idx, f"'{nm}': tiêu đề {len(sl)} dòng — rút gọn (≤ 12 từ, ≤ 2 dòng)")
                # 8. ngắt dòng chủ ý giữa cụm
                if len(segs_lines) >= 2:
                    for a_, b_ in zip(segs_lines[:-1], segs_lines[1:]):
                        a_ = [ln for ln in a_ if ln]; b_ = [ln for ln in b_ if ln]
                        if a_ and b_ and splits_compound(a_[-1][-1]["t"], b_[0][0]["t"]):
                            add("LỖI", idx, f"'{nm}': xuống dòng thủ công tách từ ghép '{a_[-1][-1]['t']} | {b_[0][0]['t']}'", ("ngat-tay", nm))
                        if a_ and b_ and ends_bad(a_[-1][-1]["t"]):
                            add("LỖI", idx, f"'{nm}': xuống dòng thủ công sau hư từ '{a_[-1][-1]['t']}' — tách cụm từ, đổi nhịp đọc câu", ("ngat-tay", nm))
            if rl == "noi-dung" and nlines_box > 5:
                add("CẢNH BÁO", idx, f"'{nm}': {nlines_box} dòng trong một khung — quá nhiều chữ (≤ 5 dòng)")
        # 2. lượng chữ cả slide
        if words_body > chu_max:
            add("LỖI" if words_body > chu_max * 1.5 else "CẢNH BÁO", idx, f"{words_body} chữ nội dung trên slide (tối đa {chu_max}) — gây xao nhãng; chuyển chi tiết sang ghi chú diễn giả")
        # 4. hài hoà
        if title_sz and body_sz:
            mode = max(set(body_sz), key=body_sz.count)   # cỡ chữ nội dung phổ biến nhất
            if title_sz < 1.25 * mode:
                add("CẢNH BÁO", idx, f"tiêu đề {title_sz:g}pt chỉ gấp {title_sz / mode:.2f} lần chữ nội dung {mode:g}pt (nên ≥ 1,25)")
        real = {s for s in sizes_slide if s < 72}
        if len(real) > 4: add("CẢNH BÁO", idx, f"{len(real)} cỡ chữ khác nhau trên một slide ({', '.join(f'{s:g}' for s in sorted(real))}) — giữ ≤ 4")
    if len(title_sizes) > 1:
        add("CẢNH BÁO", 0, "tiêu đề dùng nhiều cỡ: " + "; ".join(f"{s:g}pt ở slide {', '.join(map(str, v[:5]))}" for s, v in sorted(title_sizes.items())) + " — thống nhất cỡ tiêu đề")
    return out, len(slides)

# ---------------------------------------------------------------- tự sửa
def set_size(box, scale):
    for p in box["paras"]:
        for el in p["el"].iter():
            if el.tag.endswith("}rPr") or el.tag.endswith("}endParaRPr"):
                if el.get("sz"): el.set("sz", str(int(round(int(el.get("sz")) * scale / 50.0) * 50)))

def fix_box_size(box, co_min, rl):
    """giảm cỡ từng 1pt (không dưới mức tối thiểu) đến khi hết tràn khung và dòng mồ côi"""
    szs = [r["sz"] for p in box["paras"] for s in p["segs"] for r in s]
    floor = co_min if rl == "noi-dung" else (max(co_min + 4, 28) if rl == "tieu-de" else 14)
    nap_tu_ghep(" ".join(r["text"] for p in box["paras"] for s in p["segs"] for r in s))
    def ok(scale):
        lay, total = layout(box, scale)
        if total > box["H"] + 2: return False
        for (p, segs_lines, _) in lay:
            for sl in segs_lines:
                sl = [ln for ln in sl if ln]
                if len(sl) >= 2 and (len(sl[-1]) == 1 or (len(sl[-1]) <= 2 and line_w(sl[-1]) < 0.2 * box["W"])): return False
                for a_, b_ in zip(sl[:-1], sl[1:]):
                    if splits_compound(a_[-1]["t"], b_[0]["t"]): return False
        return True
    if ok(1.0): return None
    top = max(szs)
    s = top - 1
    while s >= floor:
        if ok(s / top): return s / top
        s -= 1
    return False

def insert_break(p_el, char_index):
    """thay khoảng trắng tại vị trí char_index (tính trên chuỗi đoạn) bằng <a:br/>, không đổi chữ"""
    pos = 0
    children = list(p_el)
    for i, el in enumerate(children):
        if not el.tag.endswith("}r"): continue
        t = el.find("a:t", NS)
        if t is None or t.text is None: continue
        L = len(t.text)
        if pos <= char_index < pos + L:
            k = char_index - pos
            before, after = t.text[:k], t.text[k + 1:]
            rpr = el.find("a:rPr", NS)
            t.text = before
            br = ET.Element(f"{{{NS['a']}}}br")
            if rpr is not None: br.append(ET.fromstring(ET.tostring(rpr)))
            r2 = ET.fromstring(ET.tostring(el)); r2.find("a:t", NS).text = after
            p_el.insert(i + 1, br); p_el.insert(i + 2, r2)
            return True
        pos += L
    return False

def sua(path, out_path, co_min=24):
    zin = zipfile.ZipFile(path)
    ET.register_namespace("a", NS["a"]); ET.register_namespace("p", NS["p"]); ET.register_namespace("r", NS["r"])
    ET.register_namespace("mc", NS["mc"]); ET.register_namespace("a14", NS["a14"])
    ET.register_namespace("m", "http://schemas.openxmlformats.org/officeDocument/2006/math")
    ET.register_namespace("p14", "http://schemas.microsoft.com/office/powerpoint/2010/main")
    ET.register_namespace("p159", "http://schemas.microsoft.com/office/powerpoint/2015/09/main")
    log, files = [], {}
    for n in zin.namelist():
        data = zin.read(n)
        if re.match(r"ppt/slides/slide\d+\.xml$", n):
            idx = int(re.findall(r"\d+", n)[-1])
            xml = data.decode("utf8")
            # số – đơn vị: khoảng trắng không ngắt (chỉ trong <a:t>)
            xml2 = re.sub(r"(<a:t>)([^<]*)(</a:t>)", lambda m: m.group(1) + SO_DON_VI.sub(lambda x: x.group(1) + NBSP + x.group(2), m.group(2)) + m.group(3), xml)
            if xml2 != xml: log.append(f"slide {idx}: nối số – đơn vị bằng khoảng trắng không ngắt")
            # ElementTree không giữ mc:AlternateContent nguyên vẹn khi resolve → sửa trên cây gốc (không resolve)
            root = ET.fromstring(xml2.encode("utf8"))
            for sp in root.iter(f"{{{NS['p']}}}sp"):
                if sp.find(".//{http://schemas.microsoft.com/office/drawing/2010/main}m") is not None: continue
                holder = ET.Element("x"); holder.append(sp)
                bxs = read_boxes_from_sp(sp)
                if not bxs: continue
                bx = bxs; rl = role(bx)
                if rl in ("trang-tri", "khac"): continue
                # tiêu đề 2 dòng: chèn ngắt dòng ở điểm tốt nhất
                if rl == "tieu-de" and len(bx["paras"]) == 1 and len(bx["paras"][0]["segs"]) == 1:
                    seg = bx["paras"][0]["segs"][0]
                    nap_tu_ghep("".join(r["text"] for r in seg))
                    words = tokens(seg)
                    lines = wrap_words(words, bx["W"], bx["wrap"])
                    bad = len(lines) == 2 and (line_w(lines[0]) > line_w(lines[1]) + 2 or ends_bad(lines[0][-1]["t"]))
                    if bad:
                        # tìm điểm ngắt đúng ranh giới cụm từ; nếu không vừa, giảm dần cỡ tiêu đề (không dưới mức tối thiểu)
                        top = max(r["sz"] for r in seg); floor = max(co_min + 4, 28); s_ = top; chosen = None
                        while s_ >= floor and not chosen:
                            ws = tokens(seg, s_ / top); b = best_break(ws, bx["W"])
                            if b and b[0] >= 60: chosen = (s_, b, ws)
                            s_ -= 1
                        if chosen:
                            s_, b, ws = chosen; k = b[1]
                            char_index = len(" ".join(w["t"] for w in ws[:k]))
                            if insert_break(bx["paras"][0]["el"], char_index):
                                bx = read_boxes_from_sp(sp)
                                if s_ < top: set_size(bx, s_ / top); bx = read_boxes_from_sp(sp)
                                log.append(f"slide {idx}: '{bx['name']}' ngắt tiêu đề thành '{line_t(ws[:k])}' | '{line_t(ws[k:])}'" + (f", cỡ {top:g}→{s_:g}pt" if s_ < top else ""))
                        else:
                            log.append(f"slide {idx}: '{bx['name']}' tiêu đề 2 dòng chưa có điểm ngắt đúng ranh giới cụm từ — viết lại tiêu đề (ngắn hơn hoặc có hư từ/dấu phẩy để tách ý)")
                # đoạn nội dung 1 ý xuống 2 dòng mà tách từ ghép / kết thúc bằng hư từ → ngắt chủ động ở ranh giới cụm từ
                if rl == "noi-dung" and len(bx["paras"]) == 1 and len(bx["paras"][0]["segs"]) == 1:
                    seg = bx["paras"][0]["segs"][0]
                    nap_tu_ghep("".join(r["text"] for r in seg))
                    words = tokens(seg); lines = wrap_words(words, bx["W"], bx["wrap"])
                    if len(lines) == 2 and (splits_compound(lines[0][-1]["t"], lines[1][0]["t"]) or ends_bad(lines[0][-1]["t"])):
                        b = best_break(words, bx["W"], prefer_top_short=False)
                        if b and b[0] >= 60:
                            k = b[1]
                            if insert_break(bx["paras"][0]["el"], len(" ".join(w["t"] for w in words[:k]))):
                                log.append(f"slide {idx}: '{bx['name']}' ngắt dòng ở ranh giới cụm: '{line_t(words[:k])}' | '{line_t(words[k:])}'")
                                bx = read_boxes_from_sp(sp)
                sc = fix_box_size(bx, co_min, rl)
                if sc:
                    set_size(bx, sc); log.append(f"slide {idx}: '{bx['name']}' giảm cỡ chữ ×{sc:.2f} để hết tràn khung/dòng mồ côi")
                elif sc is False:
                    lay, total = layout(bx)
                    log.append(f"slide {idx}: '{bx['name']}' KHÔNG tự sửa được bằng cỡ chữ (đã chạm mức tối thiểu) — {goi_y(bx)}")
            data = ET.tostring(root, xml_declaration=True, encoding="UTF-8")
        files[n] = data
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zin.namelist(): zo.writestr(n, files[n])
    return log

def read_boxes_from_sp(sp):
    wrapper = ET.Element(f"{{{NS['p']}}}sld"); c = ET.SubElement(wrapper, f"{{{NS['p']}}}cSld"); tree = ET.SubElement(c, f"{{{NS['p']}}}spTree")
    tree.append(sp)
    bs = read_boxes(ET.tostring(wrapper))
    # read_boxes làm việc trên bản sao → trỏ el về đoạn thật
    if not bs: return None
    real_ps = [p for p in sp.find("p:txBody", NS).findall("a:p", NS)]
    k = 0
    for p in bs[0]["paras"]:
        while k < len(real_ps) and not "".join(t.text or "" for t in real_ps[k].iter(f"{{{NS['a']}}}t")): k += 1
        if k < len(real_ps): p["el"] = real_ps[k]; k += 1
    return bs[0]

def goi_y(bx):
    """gợi ý số chữ cần bớt (tràn) hoặc bớt/thêm (mồ côi)"""
    lay, total = layout(bx)
    for (p, segs_lines, psz) in lay:
        for sl in segs_lines:
            sl = [ln for ln in sl if ln]
            if len(sl) >= 2 and len(sl[-1]) <= 2:
                free = bx["W"] - line_w(sl[-1])
                avg = line_w(sl[0]) / max(1, len(sl[0]))
                return f"dòng cuối '{line_t(sl[-1])}': bớt {len(sl[-1])} chữ để gọn dòng trên, hoặc thêm khoảng {int(free * 0.6 / avg)} chữ để dòng cuối dài ra"
    if total > bx["H"]:
        return f"cần bớt khoảng {int((total - bx['H']) / total * 100)}% số chữ"
    return "rút gọn nội dung"

def main():
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    arg = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
    co_min, co_phu, chu_max = arg("--co-toi-thieu", 24), arg("--co-phu", 16), arg("--chu-toi-da", 30)
    src = a[0]
    if "--sua" in a:
        dst = a[a.index("--sua") + 1]
        for line in sua(src, dst, co_min): print("  sửa:", line)
        src = dst
        print(f"Đã ghi {dst}; kiểm lại:\n")
    out, n = kiem(src, co_min, co_phu, chu_max)
    if "--json" in a: print(json.dumps(out, ensure_ascii=False, indent=1)); sys.exit(0)
    print(f"{src}: {n} slide · cỡ nội dung tối thiểu {co_min}pt · tối đa {chu_max} chữ/slide")
    order = {"LỖI": 0, "CẢNH BÁO": 1}
    seen = set()
    for lv in order:
        rows = [o for o in out if o["muc"] == lv and (o["slide"], o["noi_dung"]) not in seen]
        for o in rows: seen.add((o["slide"], o["noi_dung"]))
        print(f"\n{lv} ({len(rows)})")
        for o in sorted(rows, key=lambda o: o["slide"]): print(f"  [{'toàn bài' if o['slide'] == 0 else 'slide ' + str(o['slide'])}] {o['noi_dung']}")
    sys.exit(1 if any(o["muc"] == "LỖI" for o in out) else 0)

if __name__ == "__main__":
    main()
