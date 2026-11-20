#!/usr/bin/env python3
"""kiem_soat_van_ban.py — module KIỂM SOÁT VĂN BẢN toàn diện cho tệp .pptx: mọi thứ thuộc về chữ và cách chữ hiển thị.

Bảy nhóm kiểm tra (tên nhóm dùng cho --chi):
  phong      PHÔNG — phông bị loại, phông mã cũ (.VnTime, VNI-…), phông ngoài gói chưa nhúng, phông của gói chưa nhúng,
             thiếu ký tự (thiếu dấu tiếng Việt → ô vuông/phông thay thế), đậm/nghiêng giả, quá 3 họ phông,
             phông trang trí trong bài chính quy, phông trang trí dùng sai (quá dài, quá nhỏ, viết HOA, con số),
             phông đơn cách/trưng bày cho đoạn văn, tiêu đề không cùng họ phông, lẫn phông trong một đoạn,
             phông ngoài cặp phông của phong cách (--phong-cach).
  ma-chu     MÃ CHỮ — Unicode tổ hợp (NFD), ký tự ẩn (zero-width, soft hyphen, BOM, ký tự điều khiển), ký tự hỏng �,
             chữ mã TCVN3 chưa chuyển, chữ Ð (Eth) thay cho Đ, ký hiệu văn bản viết sai (BGDDT, GD&DT).
  chinh-ta   CHÍNH TẢ — âm tiết không có trong tiếng Việt, hai dấu thanh, đặt dấu sai vị trí (cưú → cứu),
             sai luật c/k, g/gh, ng/ngh, dấu thanh không hợp vần (cảp), lẫn kiểu bỏ dấu cũ/mới (hoà/hòa),
             lẫn i/y (kỹ/kĩ), lặp hư từ (của của), Markdown/LaTeX sót, chữ giữ chỗ còn sót ([cần bổ sung], Lorem…).
  dau-cau    DẤU CÂU & KHOẢNG TRẮNG — hai khoảng trắng, khoảng trắng đầu/cuối đoạn, trước dấu câu, sau "(" / trước ")",
             thiếu khoảng trắng sau dấu phẩy, dấu câu lặp, ngoặc/ngoặc kép lệch cặp, lẫn ngoặc thẳng/cong, "..." và "…",
             gạch nối làm gạch ngang, tiêu đề có dấu chấm cuối, gạch đầu dòng gõ tay, ký tự tab, dòng trống làm khoảng cách.
  viet-hoa   VIẾT HOA — đoạn viết HOA toàn bộ, Viết Hoa Mỗi Chữ kiểu tiếng Anh, tên cơ quan viết hoa sai,
             tên cơ quan chỉ có dạng viết tắt, đầu đoạn viết thường.
  hien-thi   HIỂN THỊ — Tự co chữ (normAutofit) làm chữ thực tế nhỏ hơn khai báo, chữ < 12pt, chữ ra ngoài slide,
             chữ không xuống dòng tràn khung, chữ xoay/chữ dọc, giãn/nén chữ, bóng/viền/phát sáng/WordArt,
             gạch chân không phải liên kết, liên kết hỏng, chữ mờ, căn đều hai bên, căn giữa đoạn dài,
             mã ngôn ngữ không phải vi-VN (gạch đỏ chính tả), m2/m3 không chỉ số trên, chữ bảng/biểu đồ quá nhỏ,
             khung giữ chỗ trống, hộp chữ bị ẩn, thiếu ghi chú diễn giả.
  dung-thu   DỰNG THỬ (chỉ khi --hien-thi) — dựng bằng LibreOffice với phông của gói, đọc phông thật đã dùng trong PDF:
             phông khai báo nhưng không hiển thị (bị thay), ký tự rơi sang phông dự phòng.

Dùng:
  python3 kiem_soat_van_ban.py Slide.pptx [--muc chinh-quy|ban-chinh-quy|kieu-cach] [--phong-cach <khoá styles.json>]
                               [--boi-canh <khoá contexts.json>] [--hien-thi] [--day-du] [--chi phong,chinh-ta] [--json]
  python3 kiem_soat_van_ban.py Slide.pptx --sua Slide_da_sua.pptx     # tự sửa phần an toàn rồi kiểm lại
  --day-du  gộp thêm kiem_tra_van_ban.py (cỡ chữ, lượng chữ, xuống dòng, tràn khung) và kiem_tra_slide.py
            (màu, dấu hiệu AI, công thức) vào MỘT báo cáo.
  --muc     mức trang trọng; bỏ trống thì lấy theo --phong-cach, không có nữa thì chỉ GỢI Ý về phông trang trí.

Tự sửa (--sua) chỉ làm những gì KHÔNG đổi câu chữ: chuẩn hoá Unicode dựng sẵn (NFC), bỏ ký tự ẩn, Ð → Đ,
gộp khoảng trắng thừa, bỏ khoảng trắng đầu/cuối đoạn và trước dấu câu, thêm khoảng trắng sau dấu phẩy/chấm phẩy,
đổi phông bị loại sang phông thay thế, gắn mã ngôn ngữ vi-VN cho đoạn tiếng Việt. Lỗi chính tả, viết hoa, phông,
cỡ chữ chỉ được BÁO kèm gợi ý — sửa trong script dựng rồi dựng lại.
Mã thoát 1 khi còn mục LỖI.
"""
import json, os, posixpath, re, shutil, subprocess, sys, tempfile, unicodedata, zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from xml.sax.saxutils import escape, unescape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kiem_tra_slide import NS, resolve_mc  # noqa: E402
import kiem_tra_van_ban as KV  # noqa: E402

NS = dict(NS)
NS.update({"c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
           "pr": "http://schemas.openxmlformats.org/package/2006/relationships"})
RID = f"{{{NS['r']}}}id"
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
FILES = json.load(open(os.path.join(FONT_DIR, "files.json"), encoding="utf-8"))
PHAN_LOAI = {k: v for k, v in json.load(open(os.path.join(FONT_DIR, "phan-loai.json"), encoding="utf-8")).items() if not k.startswith("_")}
STYLES = json.load(open(os.path.join(ROOT, "assets", "styles.json"), encoding="utf-8"))
CONTEXTS = json.load(open(os.path.join(ROOT, "assets", "contexts.json"), encoding="utf-8"))
EMU_PT = 12700

BANNED = {"Be Vietnam Pro": "Montserrat"}
PHONG_HE_THONG = {"Arial", "Times New Roman", "Calibri", "Calibri Light", "Cambria", "Segoe UI", "Tahoma", "Verdana", "Georgia", "Courier New", "Consolas"}
PHONG_KY_HIEU = {"Cambria Math", "Symbol", "Wingdings", "Wingdings 2", "Wingdings 3", "Webdings", "Segoe UI Symbol", "Segoe UI Emoji", "Noto Color Emoji"}
PHONG_MA_CU = re.compile(r"^(\.Vn|VNI[- ]|Vn[A-Z]|VNtimes|VN-)", re.I)
NHOM = ["phong", "ma-chu", "chinh-ta", "dau-cau", "viet-hoa", "hien-thi", "dung-thu"]
TEN_NHOM = {"phong": "phông", "ma-chu": "mã chữ", "chinh-ta": "chính tả", "dau-cau": "dấu câu", "viet-hoa": "viết hoa",
            "hien-thi": "hiển thị", "dung-thu": "dựng thử", "trinh-bay": "trình bày chữ"}

TEN_TIEU_DE = re.compile(r"^(title|statement|question|big)")
TEN_PHU = re.compile(r"^(source|info|contact|kicker|hint|by|lockup|brandmark|hchon|sec|given|cap\d+|sn\d+|dn\d+|xl|yl|note|role|footer|ftr|page)$")
TEN_TRANG_TRI = re.compile(r"^(!!.*|bignum|word|mark|eq.*|sym\d+|v\d+|value|mk\d+|an\d+|num\d+|herotxt)$")

VN_DAU = set("àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ")
VN_DAU |= {c.upper() for c in VN_DAU}
AN = {"\u200b": "zero-width space", "\u200c": "zero-width non-joiner", "\u200d": "zero-width joiner", "\u2060": "word joiner",
      "\ufeff": "BOM", "\u00ad": "soft hyphen", "\u200e": "dấu hướng LTR", "\u200f": "dấu hướng RTL"}
TCVN3 = set("¸µ¶·¹¨©ª«¬®¾»¼½Æ¿ÇËÌÎÏÑÖÛÜÞßçëîïñöûüþ÷¦§¡¢£¤¥")
HU_TU = set("của và với các những cho để khi từ đến theo về tại là như hay hoặc mà nhưng do vì nên thì một mỗi rằng trong ngoài trên dưới giữa qua bởi được bị đã đang sẽ cũng còn rất quá không chưa có này kia ấy nào bằng nhằm".split())

# ---------------------------------------------------------------- âm tiết tiếng Việt
TONE = {"\u0300": "huyền", "\u0301": "sắc", "\u0303": "ngã", "\u0309": "hỏi", "\u0323": "nặng"}
ONSETS = sorted("b c ch d đ g gh gi h k kh l m n ng ngh nh p ph q qu r s t th tr v x".split(), key=len, reverse=True)
VOWELS = set("aăâeêioôơuưy")
MODIFIED = set("ăâêôơư")
CHU_VN = set("abcdđeghiklmnopqrstuvxyăâêôơư")
RHYMES = set("""a ai ao au ay ac ach am an ang anh ap at ăc ăm ăn ăng ăp ăt âc âm ân âng âp ât âu ây
e ec em en eng eo ep et ê êch êm ên ênh êp êt êu i ia ich im in inh ip it iu iêc iêm iên iêng iêp iêt iêu
o oc oi om on ong op ot oong ooc ô ôc ôi ôm ôn ông ôp ôt ơ ơi ơm ơn ơp ơt
u ua uc ui um un ung up ut uôc uôi uôm uôn uông uôt ư ưa ưc ưi ưm ưn ưng ưt ưu ưp ươc ươi ươm ươn ương ươp ươt ươu
y yêm yên yêng yêt yêu oa oac oach oai oam oan oang oanh oao oap oat oay oăc oăm oăn oăng oăt oe oem oen oeo oet
uân uâng uât uây uê uêch uênh uy uya uych uyên uyêt uynh uyp uyt uyu uyn uơ""".split())
NGOAI_LE = {"đắk", "lắk", "đăk", "lăk", "krông", "kơ", "pơ", "plei", "ơi", "ừ", "ờ", "ạ", "ư", "ê", "à", "ồ", "ố", "ới", "ơ"}

def phan_tich(word):
    letters = []
    for ch in unicodedata.normalize("NFD", word):
        if unicodedata.combining(ch):
            if not letters: return None
            (letters[-1][1] if ch in TONE else letters[-1][0]).append(ch)
        else:
            letters.append([[ch], []])
    base = [unicodedata.normalize("NFC", "".join(b)) for b, _ in letters]
    tones = [(i, t) for i, (_, ts) in enumerate(letters) for t in ts]
    return base, tones

def tach_am(s):
    for o in ONSETS:
        if s.startswith(o):
            r = s[len(o):]
            if o == "gi" and r not in RHYMES and ("i" + r) in RHYMES: return "g", "i" + r
            if o == "qu" and r == "": continue
            return o, r
    return "", s

def dat_dau(base, idx, tone, hoa):
    out = []
    for j, b in enumerate(base):
        d = unicodedata.normalize("NFD", b)
        out.append(d + (tone if j == idx else ""))
    w = unicodedata.normalize("NFC", "".join(out))
    return w[:1].upper() + w[1:] if hoa else w

def kiem_am_tiet(word):
    """trả về (mức, mô tả, gợi ý) hoặc None; kèm kiểu bỏ dấu ('cu'/'moi') qua thuộc tính kieu"""
    low = word.lower()
    if low in NGOAI_LE: return None
    pt = phan_tich(low)
    if not pt: return None
    base, tones = pt
    s = "".join(base)
    if not s or not all(ch in CHU_VN for ch in s): return None          # có f j w z hoặc ký tự lạ → từ ngoại, bỏ qua
    if len(tones) > 1: return ("LỖI", f"'{word}' có {len(tones)} dấu thanh", None, None)
    onset, rhyme = tach_am(s)
    if rhyme not in RHYMES:
        if word.isupper() or len(word) == 1: return None                 # chữ viết tắt (BGDĐT, QĐ), chữ cái đứng riêng
        return ("CẢNH BÁO", f"'{word}' không phải âm tiết tiếng Việt (vần '{rhyme or '∅'}') — gõ sai?", None, None)
    r0 = rhyme[0]
    if onset in ("gh", "ngh") and r0 not in "ieê": return ("CẢNH BÁO", f"'{word}': {onset} chỉ đứng trước i, e, ê → viết {onset[:-1]}", None, None)
    if onset in ("g", "ng") and r0 in "eê" or onset == "ng" and r0 == "i": return ("CẢNH BÁO", f"'{word}': trước e, ê, i viết {onset}h", None, None)
    if onset == "c" and r0 in "ieêy": return ("CẢNH BÁO", f"'{word}': trước i, e, ê, y viết k", None, None)
    if onset == "k" and r0 not in "ieêy": return ("CẢNH BÁO", f"'{word}': k chỉ đứng trước i, e, ê, y → viết c", None, None)
    if onset == "q": return ("CẢNH BÁO", f"'{word}': q luôn đi với u (qu)", None, None)
    tac = rhyme[-1] in "ptc" or rhyme.endswith("ch")
    if not tones:
        if tac: return ("CẢNH BÁO", f"'{word}': vần tắc (-p, -t, -c, -ch) phải có dấu sắc hoặc nặng — thiếu dấu?", None, None)
        return None
    ti, tm = tones[0]
    if tac:
        if tm not in ("\u0301", "\u0323"): return ("CẢNH BÁO", f"'{word}': vần tắc (-p, -t, -c, -ch) chỉ mang dấu sắc hoặc nặng", None, None)
    vi = [j for j in range(len(onset), len(base)) if base[j] in VOWELS]
    if not vi: return None
    mods = [j for j in vi if base[j] in MODIFIED]
    coda = vi[-1] < len(base) - 1
    kieu = None
    if mods: exp = {mods[-1]}
    elif len(vi) == 1: exp = {vi[0]}
    elif coda: exp = {vi[-1]}
    elif len(vi) == 2:
        pair = base[vi[0]] + base[vi[1]]
        if pair in ("oa", "oe", "uy"):
            exp = {vi[0], vi[1]}; kieu = "cu" if ti == vi[1] else "moi"
        else: exp = {vi[0]}
    else: exp = {vi[1]}
    if ti not in exp:
        goi_y = dat_dau(base, min(exp), tm, word[:1].isupper())
        if word.isupper(): goi_y = goi_y.upper()
        return ("CẢNH BÁO", f"'{word}' đặt dấu sai vị trí → '{goi_y}'", goi_y, None)
    return (None, None, None, kieu)

# ---------------------------------------------------------------- tên cơ quan
CO_QUAN = ["Sở Giáo dục và Đào tạo", "Bộ Giáo dục và Đào tạo", "Phòng Giáo dục và Đào tạo", "Phòng Giáo dục phổ thông",
           "Ủy ban nhân dân", "Hội đồng nhân dân", "Ban Chấp hành", "Ban Thường vụ", "Ban Tuyên giáo", "Mặt trận Tổ quốc Việt Nam",
           "Đảng Cộng sản Việt Nam", "Thủ tướng Chính phủ", "Quốc hội", "Đoàn Thanh niên Cộng sản Hồ Chí Minh", "Hội đồng trường", "Ban Giám hiệu"]
VIET_TAT = {"UBND": "Ủy ban nhân dân", "HĐND": "Hội đồng nhân dân", "BCH": "Ban Chấp hành", "BGH": "Ban Giám hiệu",
            "Sở GDĐT": "Sở Giáo dục và Đào tạo", "Sở GD&ĐT": "Sở Giáo dục và Đào tạo", "Bộ GDĐT": "Bộ Giáo dục và Đào tạo",
            "Bộ GD&ĐT": "Bộ Giáo dục và Đào tạo", "Phòng GDĐT": "Phòng Giáo dục và Đào tạo", "Phòng GD&ĐT": "Phòng Giáo dục và Đào tạo",
            "Phòng GDPT": "Phòng Giáo dục phổ thông", "MTTQ": "Mặt trận Tổ quốc Việt Nam"}
def _cq_norm(s): return s.lower().replace("uỷ", "ủy")

GIU_CHO = re.compile(r"\[cần bổ sung\]|\[\s*(?:TODO|TBD|placeholder)\s*\]|lorem ipsum|click to add|nhấp để thêm|bấm để thêm|xxx+|\?\?\?", re.I)
MARKDOWN = re.compile(r"\*\*[^*\n]+\*\*|__[^_\n]+__|^#{1,6}\s|`[^`\n]+`|\[[^\]\n]+\]\(https?://[^)\s]+\)|^\s*>\s")
LATEX = re.compile(r"\$[^$\n]{2,}\$|\\(?:frac|sqrt|alpha|beta|cdot|times|sum|int|left|right|mathrm|text)\b")
KY_HIEU_SAI = re.compile(r"\b(?:[BSP]GD|GD)\s?(?:&\s?|-)?DT\b|\bGD\s?&\s?DT\b")
SO_TRONG_CHU = re.compile(r"\S*\d\S*")
DON_VI_MU = re.compile(r"(?<![\w])(m|cm|dm|mm|km)(2|3)(?![\w\d])")

# ---------------------------------------------------------------- đọc gói
class Goi:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path); self.names = set(self.z.namelist())
    def has(self, n): return n in self.names
    def xml(self, n): return ET.fromstring(self.z.read(n))
    def rels(self, part):
        d, b = posixpath.split(part); rn = posixpath.join(d, "_rels", b + ".rels")
        out = {}
        if rn not in self.names: return out
        for r in self.xml(rn).findall("pr:Relationship", NS):
            t = r.get("Target", "")
            tgt = t if r.get("TargetMode") == "External" else posixpath.normpath(posixpath.join(d, t))
            out[r.get("Id")] = (r.get("Type", "").rsplit("/", 1)[-1], tgt, r.get("TargetMode") == "External")
        return out

def mo_ta_bai(goi):
    pres = goi.xml("ppt/presentation.xml"); prels = goi.rels("ppt/presentation.xml")
    slides = [prels[s.get(RID)][1] for s in pres.findall("p:sldIdLst/p:sldId", NS) if s.get(RID) in prels]
    sz = pres.find("p:sldSz", NS)
    W, H = (int(sz.get("cx")) / EMU_PT, int(sz.get("cy")) / EMU_PT) if sz is not None else (960, 540)
    embedded = {f.get("typeface") for f in pres.findall("p:embeddedFontLst/p:embeddedFont/p:font", NS)}
    theme = {"major": None, "minor": None}
    for _, (typ, tgt, _) in prels.items():
        if typ == "theme" and goi.has(tgt):
            th = goi.xml(tgt)
            for k, tag in (("major", "majorFont"), ("minor", "minorFont")):
                lat = th.find(f".//a:{tag}/a:latin", NS)
                if lat is not None: theme[k] = lat.get("typeface")
            break
    return slides, W, H, embedded, theme

def _bp_inset(bp, k, d): return int(bp.get(k, d)) / EMU_PT if bp is not None else d / EMU_PT

def doc_run(r, kind, fld=False):
    rp = r.find("a:rPr", NS); t = r.find("a:t", NS)
    g = (lambda k, d=None: rp.get(k, d)) if rp is not None else (lambda k, d=None: d)
    lat = rp.find("a:latin", NS) if rp is not None else None
    sf = rp.find("a:solidFill/*", NS) if rp is not None else None
    al = sf.find("a:alpha", NS) if sf is not None else None
    eff = rp.find("a:effectLst", NS) if rp is not None else None
    ln = rp.find("a:ln", NS) if rp is not None else None
    hl = rp.find("a:hlinkClick", NS) if rp is not None else None
    return {"text": (t.text or "") if t is not None else "", "sz": int(g("sz")) / 100 if g("sz") else None,
            "b": g("b") == "1", "i": g("i") == "1", "u": g("u") not in (None, "none"), "cap": g("cap"),
            "spc": int(g("spc", "0")) / 100, "lang": g("lang"), "baseline": int(g("baseline", "0")),
            "latin": lat.get("typeface") if lat is not None else None,
            "alpha": int(al.get("val")) / 100000 if al is not None else 1.0,
            "hieu_ung": [c.tag.split("}")[1] for c in eff] if eff is not None else [],
            "vien": ln is not None and ln.find("a:noFill", NS) is None and len(ln) > 0,
            "grad": rp is not None and rp.find("a:gradFill", NS) is not None,
            "link": hl.get(RID) if hl is not None else None, "fld": fld}

def doc_txbody(tb):
    bp = tb.find("a:bodyPr", NS)
    paras = []
    for p in tb.findall("a:p", NS):
        ppr = p.find("a:pPr", NS)
        runs, line = [], 0
        for el in p:
            tag = el.tag.split("}")[1]
            if tag in ("r", "fld"):
                rr = doc_run(el, tag, tag == "fld"); rr["dong"] = line; runs.append(rr)
            elif tag == "br": line += 1; runs.append({"br": True, "text": "\n"})
        paras.append({"runs": runs, "algn": ppr.get("algn") if ppr is not None else None,
                      "bullet": ppr is not None and (ppr.find("a:buChar", NS) is not None or ppr.find("a:buAutoNum", NS) is not None),
                      "el": p})
    af = bp.find("a:normAutofit", NS) if bp is not None else None
    return {"paras": paras, "wrap": (bp.get("wrap") if bp is not None else None) != "none",
            "vert": bp.get("vert") if bp is not None else None, "warp": bp is not None and bp.find("a:prstTxWarp", NS) is not None,
            "autofit": (int(af.get("fontScale", "100000")) / 1000 if af is not None else None),
            "lnRed": int(af.get("lnSpcReduction", "0")) / 1000 if af is not None else 0,
            "ins": (_bp_inset(bp, "lIns", 91440), _bp_inset(bp, "rIns", 91440))}

def doc_slide(goi, part):
    root = resolve_mc(goi.xml(part))
    parent = {c: p for p in root.iter() for c in p}
    hops = []
    def in_group(el):
        p = parent.get(el)
        while p is not None:
            if p.tag == f"{{{NS['p']}}}grpSp": return True
            p = parent.get(p)
        return False
    def geom(el):
        x = el.find("p:spPr/a:xfrm", NS) if el.tag.endswith("}sp") else el.find("p:xfrm", NS)
        if x is None: return None, 0
        o, e = x.find("a:off", NS), x.find("a:ext", NS)
        if o is None or e is None: return None, 0
        return [int(o.get("x")) / EMU_PT, int(o.get("y")) / EMU_PT, int(e.get("cx")) / EMU_PT, int(e.get("cy")) / EMU_PT], int(x.get("rot", "0")) / 60000
    for sp in root.iter(f"{{{NS['p']}}}sp"):
        tb = sp.find("p:txBody", NS)
        if tb is None: continue
        nv = sp.find("p:nvSpPr/p:cNvPr", NS); ph = sp.find("p:nvSpPr/p:nvPr/p:ph", NS)
        box, rot = geom(sp)
        h = doc_txbody(tb)
        h.update({"name": nv.get("name", "") if nv is not None else "", "hidden": nv is not None and nv.get("hidden") == "1",
                  "ph": (ph.get("type", "body") if ph is not None else None), "box": box, "rot": rot, "group": in_group(sp),
                  "eq": sp.find(".//a14:m", NS) is not None, "kind": "sp"})
        hops.append(h)
    for gf in root.iter(f"{{{NS['p']}}}graphicFrame"):
        box, rot = geom(gf); nv = gf.find("p:nvGraphicFramePr/p:cNvPr", NS)
        for tc in gf.iter(f"{{{NS['a']}}}tc"):
            tb = tc.find("a:txBody", NS)
            if tb is None: continue
            h = doc_txbody(tb)
            h.update({"name": (nv.get("name", "bảng") if nv is not None else "bảng"), "hidden": False, "ph": None, "box": None, "rot": 0,
                      "group": True, "eq": False, "kind": "bang"})
            hops.append(h)
    return root, hops

def vai(h):
    sizes = [r["sz"] for p in h["paras"] for r in p["runs"] if not r.get("br") and r["sz"]]
    if h["kind"] == "bang": return "bang"
    if h["ph"] in ("title", "ctrTitle"): return "tieu-de"
    if h["ph"] in ("sldNum", "dt", "ftr"): return "phu"
    n = h["name"]
    if TEN_TRANG_TRI.match(n) or (sizes and max(sizes) >= 72): return "trang-tri"
    if TEN_TIEU_DE.match(n): return "tieu-de"
    if TEN_PHU.match(n): return "phu"
    return "noi-dung"

def text_doan(p): return "".join(r["text"] for r in p["runs"])

# ---------------------------------------------------------------- phông: tệp và bảng mã
_cmap, _fc = {}, {}
def tep_phong(face, b, i):
    f = FILES.get(face)
    if f:
        slot = "boldItalic" if b and i else "bold" if b else "italic" if i else "regular"
        rel = f.get(slot) or f.get("bold" if b else "regular") or f["regular"]
        return os.path.join(FONT_DIR, rel), slot in f
    key = (face, b, i)
    if key not in _fc:
        style = "Bold Italic" if b and i else "Bold" if b else "Italic" if i else "Regular"
        try:
            out = subprocess.run(["fc-match", "-f", "%{family}|%{file}", f"{face}:style={style}"], capture_output=True, text=True, timeout=10).stdout
            fam, fil = out.split("|", 1)
            _fc[key] = (fil, True) if face.lower() in [x.strip().lower() for x in fam.split(",")] else (None, False)
        except Exception:
            _fc[key] = (None, False)
    return _fc[key]

def bang_ma(path):
    if path not in _cmap:
        try:
            from fontTools.ttLib import TTFont
            _cmap[path] = set(TTFont(path, lazy=True, fontNumber=0).getBestCmap() or {})
        except Exception:
            _cmap[path] = None
    return _cmap[path]

def ho_phong(r, role, theme):
    f = r.get("latin")
    if f and f.startswith("+mj"): return theme["major"] or "Calibri Light"
    if f and f.startswith("+mn"): return theme["minor"] or "Calibri"
    if f: return f
    return (theme["major"] if role == "tieu-de" else theme["minor"]) or "Calibri"

def ten_phong_style(s):
    return {re.sub(r"\s*\(.*?\)", "", x).strip() for x in (s or "").split("|") if x.strip()}

# ---------------------------------------------------------------- kiểm tra
def kiem(path, muc=None, phong_cach=None, co_min=24, co_phu=16, bo_ghi_chu=False):
    goi = Goi(path)
    slides, SW, SH, embedded, theme = mo_ta_bai(goi)
    out = []
    def add(lv, s, nhom, msg, sua=False): out.append({"muc": lv, "slide": s, "nhom": nhom, "noi_dung": msg, "sua": sua})
    st = STYLES.get(phong_cach) if phong_cach else None
    if st and not muc: muc = st.get("muc")
    du_kien = set()
    if st:
        for k in ("head", "body", "accent", "quote"): du_kien |= ten_phong_style(st["fonts"].get(k))

    fam_slides, fam_roles, fake = defaultdict(set), defaultdict(Counter), defaultdict(set)
    missing = defaultdict(lambda: defaultdict(set))
    title_fams, body_fams = defaultdict(set), defaultdict(set)
    kieu_dau = {"cu": defaultdict(set), "moi": defaultdict(set)}
    iy = defaultdict(lambda: defaultdict(set))
    quotes = {"thang": set(), "cong": set()}; ellipsis = {"...": set(), "…": set()}
    lang_sai, notes_thieu, chart_nho = set(), [], []
    cq_day_du, cq_viet_tat = set(), defaultdict(set)
    I_Y = [("kỹ", "kĩ"), ("lý", "lí"), ("mỹ", "mĩ"), ("quý", "quí"), ("hy", "hi")]

    for idx, part in enumerate(slides, 1):
        root, hops = doc_slide(goi, part)
        srels = goi.rels(part)
        try:
            kv_boxes = {b["name"]: b for b in KV.read_boxes(goi.z.read(part))}
        except Exception:
            kv_boxes = {}
        for h in hops:
            if h["eq"]: continue
            rl = vai(h); nm = h["name"]
            all_runs = [r for p in h["paras"] for r in p["runs"] if not r.get("br")]
            full = " ".join(text_doan(p) for p in h["paras"]).strip()
            if not full:
                if h["ph"] and h["ph"] not in ("sldNum", "dt", "ftr", "pic"):
                    add("GỢI Ý", idx, "hien-thi", f"khung giữ chỗ '{nm}' trống — hiện chữ 'Click to add…' khi sửa; xoá khung")
                continue
            if h["hidden"] and not nm.startswith("!!"):
                add("GỢI Ý", idx, "hien-thi", f"hộp chữ '{nm}' đang bị ẩn — xoá nếu không dùng")
            scale = (h["autofit"] or 100) / 100

            # ---------- PHÔNG (từng run)
            for p in h["paras"]:
                fams_p = set()
                ptext = text_doan(p).strip()
                words = len(ptext.split())
                for r in p["runs"]:
                    if r.get("br") or not r["text"]: continue
                    fam = ho_phong(r, rl, theme)
                    if fam in PHONG_KY_HIEU: continue
                    fams_p.add(fam); fam_slides[fam].add(idx); fam_roles[fam][rl] += 1
                    if rl == "tieu-de": title_fams[fam].add(idx)
                    if rl == "noi-dung": body_fams[fam].add(idx)
                    fpath, exact = tep_phong(fam, r["b"], r["i"])
                    if fam in FILES and not exact:
                        fake[(fam, "đậm" if r["b"] and not r["i"] else "nghiêng" if r["i"] and not r["b"] else "đậm nghiêng")].add(idx)
                    cm = bang_ma(fpath) if fpath else None
                    if cm:
                        for ch in r["text"]:
                            if ch in " \t\n\r" or ord(ch) in cm or unicodedata.category(ch) in ("Cc", "Cf"): continue
                            missing[fam][ch].add(idx)
                    info = PHAN_LOAI.get(fam, {})
                    sz = (r["sz"] or 18) * scale
                    if info.get("loai") == "trang-tri":
                        if info.get("min_pt") and sz < info["min_pt"]:
                            add("CẢNH BÁO", idx, "phong", f"'{nm}': phông trang trí {fam} cỡ {sz:g}pt < {info['min_pt']}pt — khó đọc")
                        if info.get("khong_hoa") and (r["cap"] == "all" or (sum(c.isalpha() for c in r["text"]) >= 4 and r["text"].isupper())):
                            add("CẢNH BÁO", idx, "phong", f"'{nm}': phông viết tay {fam} viết HOA toàn bộ — không đọc được; dùng chữ thường")
                    if info.get("khong_so") and re.search(r"\d", r["text"]) and (info.get("loai") == "trang-tri" or sz >= 32):
                        so = SO_TRONG_CHU.search(r["text"]).group(0)[:20]
                        add("CẢNH BÁO", idx, "phong", f"'{nm}': con số '{so}' dùng {fam} ({'số kiểu cổ, cao thấp lệch' if info.get('loai') == 'serif' else 'phông viết tay'}) — đặt số bằng Montserrat/Lexend")
                for fam in fams_p:
                    info = PHAN_LOAI.get(fam, {})
                    if info.get("max_tu") and words > info["max_tu"]:
                        add("CẢNH BÁO", idx, "phong", f"'{nm}': phông trang trí {fam} cho đoạn {words} chữ (tối đa {info['max_tu']}) — đổi đoạn sang serif/sans")
                    if info.get("khong_doan") and words > 12:
                        add("CẢNH BÁO", idx, "phong", f"'{nm}': {fam} ({'đơn cách' if info.get('loai') == 'mono' else 'trưng bày'}) cho đoạn {words} chữ — chỉ dùng cho nhãn, số liệu, tiêu đề ngắn")
                if len(fams_p) > 2:
                    add("CẢNH BÁO", idx, "phong", f"'{nm}': một đoạn trộn {len(fams_p)} phông ({', '.join(sorted(fams_p))}) — giữ một phông cho mỗi đoạn")

            # ---------- MÃ CHỮ, CHÍNH TẢ, DẤU CÂU, VIẾT HOA (từng đoạn)
            for p in h["paras"]:
                t = text_doan(p)
                if not t.strip() or all(r.get("fld") or r.get("br") for r in p["runs"]): continue
                kiem_chu(t, idx, nm, rl, add, kieu_dau, iy, I_Y, quotes, ellipsis, cq_day_du, cq_viet_tat, p)
            # dòng trống làm khoảng cách
            empties, run_e = 0, 0
            for p in h["paras"]:
                if text_doan(p).strip(): run_e = 0
                else:
                    run_e += 1
                    if run_e == 2: empties += 1
            if empties: add("GỢI Ý", idx, "dau-cau", f"'{nm}': dùng 2+ đoạn trống làm khoảng cách — đặt khoảng cách đoạn (spcBef/spcAft)")

            # ---------- HIỂN THỊ
            sizes = [(r["sz"] or 18) for r in all_runs if r["text"].strip() and not r.get("fld")]
            if h["autofit"] is not None and h["kind"] == "sp":
                eff = min(sizes) * scale if sizes else 0
                if scale < 1:
                    lv = "LỖI" if rl == "noi-dung" and eff < co_min else "CẢNH BÁO"
                    add(lv, idx, "hien-thi", f"'{nm}': đang bật Tự co chữ ({h['autofit']:g}%{', giảm giãn dòng ' + format(h['lnRed'], 'g') + '%' if h['lnRed'] else ''}) — chữ hiển thị chỉ còn {eff:.1f}pt; tắt tự co, rút gọn chữ hoặc nới khung")
                else:                                   # bật tự co nhưng chưa co: chỉ báo khi chữ thực sự tràn (PowerPoint sẽ co khi mở)
                    kb = kv_boxes.get(nm)
                    if kb:
                        try:
                            _, total = KV.layout(kb)
                            if total > kb["H"] + 1:
                                est = min(sizes) * max(0.25, (kb["H"] / total) ** 0.5)
                                lv = "LỖI" if rl == "noi-dung" and est < co_min else "CẢNH BÁO"
                                add(lv, idx, "hien-thi", f"'{nm}': chữ cao {total:.0f}pt > khung {kb['H']:.0f}pt, đang bật Tự co chữ — PowerPoint sẽ tự thu chữ còn khoảng {est:.0f}pt khi mở; rút gọn chữ hoặc nới khung")
                        except Exception:
                            pass
            if sizes:
                tiny = min(sizes) * scale
                if tiny < 12 and rl != "trang-tri":
                    add("LỖI" if rl != "bang" else "CẢNH BÁO", idx, "hien-thi", f"'{nm}': chữ {tiny:g}pt < 12pt — không đọc được khi trình chiếu")
                elif rl == "bang" and tiny < co_phu:
                    add("CẢNH BÁO", idx, "hien-thi", f"bảng '{nm}': chữ trong ô {tiny:g}pt < {co_phu}pt — tách bảng hoặc bớt cột")
            if h["box"] and not h["group"]:
                x, y, w, hh = h["box"]; tol = 2
                if x < -tol or y < -tol or x + w > SW + tol or y + hh > SH + tol:
                    vis = max(0, min(x + w, SW) - max(x, 0)) * max(0, min(y + hh, SH) - max(y, 0)) / max(1, w * hh)
                    if not nm.startswith("!!"):
                        add("LỖI" if vis < 0.98 else "CẢNH BÁO", idx, "hien-thi", f"'{nm}': hộp chữ nằm {'ngoài' if vis < 0.05 else 'một phần ngoài'} slide ({vis:.0%} trong khung)")
                if not h["wrap"] and sizes:
                    try:
                        do_rong = KV.width
                        for p in h["paras"]:
                            segs, cur = [], 0.0
                            for r in p["runs"]:
                                if r.get("br"): segs.append(cur); cur = 0.0; continue
                                cur += do_rong(r["text"], ho_phong(r, rl, theme), r["b"], r["i"], (r["sz"] or 18) * scale, r["spc"])
                            segs.append(cur)
                            lw = max(segs) + sum(h["ins"])
                            if lw > w + 2:
                                over_slide = (p["algn"] in (None, "l") and x + lw > SW + 2)
                                add("LỖI" if over_slide else "CẢNH BÁO", idx, "hien-thi", f"'{nm}': tắt xuống dòng, dòng dài {lw:.0f}pt > khung {w:.0f}pt{' — tràn ra ngoài slide' if over_slide else ''}")
                                break
                    except Exception:
                        pass
            words_all = len(full.split())
            if h["rot"] % 360 not in (0,) and words_all >= 4 and not nm.startswith("!!"):
                add("CẢNH BÁO", idx, "hien-thi", f"'{nm}': hộp chữ xoay {h['rot']:g}° với {words_all} chữ — khó đọc; chỉ xoay nhãn ngắn")
            if h["vert"] and h["vert"] != "horz" and words_all >= 3:
                add("CẢNH BÁO", idx, "hien-thi", f"'{nm}': chữ dọc ({h['vert']}) {words_all} chữ — đổi sang chữ ngang")
            if h["warp"]:
                add("CẢNH BÁO", idx, "hien-thi", f"'{nm}': chữ uốn WordArt (prstTxWarp) — kiểu cũ, méo dấu tiếng Việt")
            seen_flags = set()
            for r in all_runs:
                if not r["text"].strip() or r.get("fld"): continue
                rw = len(r["text"].split())
                if rl in ("noi-dung", "bang") and r["spc"] < -1 and "nen" not in seen_flags:
                    seen_flags.add("nen"); add("CẢNH BÁO", idx, "hien-thi", f"'{nm}': chữ bị nén {r['spc']:g}pt — dấu tiếng Việt chạm nhau")
                if r["spc"] > 5 and rw >= 4 and "gian" not in seen_flags:
                    seen_flags.add("gian"); add("CẢNH BÁO", idx, "hien-thi", f"'{nm}': giãn chữ {r['spc']:g}pt cho {rw} chữ — chỉ giãn nhãn ngắn")
                fx = [e for e in r["hieu_ung"] if e in ("outerShdw", "innerShdw", "glow", "reflection", "prstShdw")]
                if (fx or r["vien"] or r["grad"]) and "fx" not in seen_flags:
                    seen_flags.add("fx")
                    kinds = [{"outerShdw": "bóng", "innerShdw": "bóng trong", "prstShdw": "bóng", "glow": "phát sáng", "reflection": "phản chiếu"}[e] for e in fx] + (["viền chữ"] if r["vien"] else []) + (["tô chuyển sắc"] if r["grad"] else [])
                    add("CẢNH BÁO" if rl == "noi-dung" else "GỢI Ý", idx, "hien-thi", f"'{nm}': chữ có {', '.join(dict.fromkeys(kinds))} — làm nhoè nét, nhất là dấu; dùng chữ phẳng trên nền tương phản")
                if r["u"] and not r["link"] and "u" not in seen_flags:
                    seen_flags.add("u"); add("CẢNH BÁO", idx, "hien-thi", f"'{nm}': gạch chân '{r['text'].strip()[:25]}' không phải liên kết — dễ tưởng là link; nhấn bằng chữ đậm hoặc màu")
                if r["link"]:
                    rel = srels.get(r["link"])
                    if not rel or not rel[1] or rel[1] in ("#", "http://", "https://"):
                        add("LỖI", idx, "hien-thi", f"'{nm}': liên kết '{r['text'].strip()[:25]}' không có đích")
                    elif rel[2] and re.match(r"https?://", r["text"].strip()) and len(r["text"].strip()) > 40:
                        add("GỢI Ý", idx, "hien-thi", f"'{nm}': hiện nguyên đường dẫn dài {len(r['text'].strip())} ký tự — đặt chữ mô tả hoặc mã QR")
                if r["alpha"] < 0.6 and rl in ("noi-dung", "tieu-de") and "alpha" not in seen_flags:
                    seen_flags.add("alpha"); add("CẢNH BÁO", idx, "hien-thi", f"'{nm}': chữ mờ (độ đục {r['alpha']:.0%}) — chữ nội dung cần đục 100%")
                if any(c in VN_DAU for c in r["text"]) and not (r["lang"] or "").lower().startswith("vi"):
                    lang_sai.add(idx)
            for p in h["paras"]:
                pt_ = text_doan(p).strip(); pw = len(pt_.split())
                if p["algn"] in ("just", "dist", "thaiDist", "justLow") and pw >= 6:
                    add("CẢNH BÁO", idx, "hien-thi", f"'{nm}': căn đều hai bên — trên slide tạo khoảng trắng loang giữa các chữ; căn trái"); break
                if p["algn"] == "ctr" and rl == "noi-dung" and pw >= 18:
                    add("CẢNH BÁO", idx, "hien-thi", f"'{nm}': căn giữa đoạn nội dung {pw} chữ — căn trái để mắt có điểm bắt đầu dòng"); break
            if DON_VI_MU.search(full) and not any(r["baseline"] > 0 for r in all_runs):
                add("GỢI Ý", idx, "hien-thi", f"'{nm}': '{DON_VI_MU.search(full).group(0)}' — viết {DON_VI_MU.search(full).group(1)}{'²' if DON_VI_MU.search(full).group(2) == '2' else '³'}")

        # tiêu đề kết bằng dấu chấm: kiểm ở kiem_chu; biểu đồ
        for rid, (typ, tgt, ext) in srels.items():
            if typ == "chart" and goi.has(tgt):
                ch = goi.xml(tgt)
                szs = [int(e.get("sz")) / 100 for e in ch.iter() if e.tag in (f"{{{NS['a']}}}defRPr", f"{{{NS['a']}}}rPr") and e.get("sz")]
                for e in ch.iter(f"{{{NS['a']}}}latin"):
                    fam = e.get("typeface")
                    if fam and not fam.startswith("+"): fam_slides[fam].add(idx); fam_roles[fam]["bieu-do"] += 1
                if not szs: chart_nho.append((idx, None))
                elif min(szs) < 12: chart_nho.append((idx, min(szs)))
        # ghi chú diễn giả
        if not bo_ghi_chu:
            notes = [tgt for typ, tgt, _ in srels.values() if typ == "notesSlide" and goi.has(tgt)]
            ntext = ""
            if notes:
                nroot = goi.xml(notes[0])
                for sp in nroot.iter(f"{{{NS['p']}}}sp"):
                    ph = sp.find("p:nvSpPr/p:nvPr/p:ph", NS)
                    if ph is not None and ph.get("type") == "body":
                        ntext = " ".join(t.text or "" for t in sp.iter(f"{{{NS['a']}}}t"))
            if len(ntext.split()) < 5: notes_thieu.append(idx)
            elif ntext:
                for lv, msg in ma_chu(ntext):
                    add("CẢNH BÁO", idx, "ma-chu", "ghi chú diễn giả: " + msg, True)

    # ---------- tổng hợp toàn bài: PHÔNG
    used = [f for f in fam_slides if f not in PHONG_KY_HIEU]
    for fam in sorted(used):
        ss = ", ".join(map(str, sorted(fam_slides[fam])[:8]))
        if fam in BANNED:
            add("LỖI", 0, "phong", f"phông {fam} đã loại khỏi gói (slide {ss}) — đổi sang {BANNED[fam]}", True)
        elif PHONG_MA_CU.match(fam):
            add("LỖI", 0, "phong", f"phông mã cũ {fam} (TCVN3/VNI, slide {ss}) — chữ hiện sai trên máy dùng Unicode; chuyển mã bằng Unikey rồi đổi phông")
        elif fam in FILES:
            if fam not in embedded:
                add("LỖI", 0, "phong", f"phông {fam} (slide {ss}) chưa nhúng vào tệp — máy không cài phông sẽ thay phông khác; chạy MS.embedFonts")
        elif fam in embedded:
            add("GỢI Ý", 0, "phong", f"phông {fam} ngoài bộ phông của gói (đã nhúng, slide {ss}) — kiểm tra giấy phép và dấu tiếng Việt")
        elif fam in PHONG_HE_THONG:
            add("GỢI Ý", 0, "phong", f"phông hệ thống {fam} (slide {ss}) ngoài bộ phông của gói — có trên Windows, có thể thiếu trên Mac/Linux")
        else:
            add("LỖI", 0, "phong", f"phông {fam} (slide {ss}) không có trong gói và chưa nhúng — máy khác sẽ hiện phông thay thế")
    for fam, chars in missing.items():
        sl = sorted({s for v in chars.values() for s in v})
        sample = ", ".join(f"'{c}' U+{ord(c):04X}" for c in list(chars)[:6])
        add("LỖI", 0, "phong", f"phông {fam} thiếu {len(chars)} ký tự ({sample}) ở slide {', '.join(map(str, sl[:8]))} — hiện ô vuông hoặc phông dự phòng; đổi phông hoặc ký tự")
    for (fam, kieu), ss in sorted(fake.items()):
        add("CẢNH BÁO", 0, "phong", f"phông {fam} không có kiểu {kieu} — PowerPoint tự tạo {kieu} giả, nét nhoè (slide {', '.join(map(str, sorted(ss)[:8]))}); bỏ {kieu} hoặc đổi phông")
    main_fams = [f for f in used if f not in PHONG_HE_THONG or fam_roles[f]["noi-dung"] + fam_roles[f]["tieu-de"]]
    if len(main_fams) > 3:
        add("CẢNH BÁO", 0, "phong", f"bài dùng {len(main_fams)} họ phông ({', '.join(sorted(main_fams))}) — tối đa 2 phông chính + 1 phông nhấn")
    deco = [f for f in used if PHAN_LOAI.get(f, {}).get("loai") == "trang-tri"]
    semi = [f for f in used if PHAN_LOAI.get(f, {}).get("ban_chinh_quy")]
    if muc == "chinh-quy":
        for f in deco: add("LỖI", 0, "phong", f"bài chính quy dùng phông trang trí {f} (slide {', '.join(map(str, sorted(fam_slides[f])[:8]))}) — chỉ dùng serif/sans-serif")
        for f in semi: add("CẢNH BÁO", 0, "phong", f"bài chính quy dùng phông bán chính quy {f} — cân nhắc Montserrat/Lexend/Noto Serif")
    elif muc is None and deco:
        add("GỢI Ý", 0, "phong", f"có phông trang trí {', '.join(deco)} — chỉ hợp bài kiểu cách (lễ, tri ân, sự kiện); bài chính quy thì đổi (chạy kèm --muc để kiểm chặt)")
    if du_kien:
        ngoai = [f for f in used if f not in du_kien and f not in PHONG_KY_HIEU and fam_roles[f]["noi-dung"] + fam_roles[f]["tieu-de"] > 0]
        for f in ngoai: add("CẢNH BÁO", 0, "phong", f"phông {f} ngoài cặp phông của phong cách '{phong_cach}' ({', '.join(sorted(du_kien))})")
    if len(title_fams) > 1:
        add("CẢNH BÁO", 0, "phong", "tiêu đề dùng nhiều họ phông: " + "; ".join(f"{f} (slide {', '.join(map(str, sorted(s)[:6]))})" for f, s in title_fams.items()) + " — thống nhất một phông tiêu đề")
    if len(body_fams) > 2:
        add("CẢNH BÁO", 0, "phong", f"chữ nội dung dùng {len(body_fams)} họ phông ({', '.join(sorted(body_fams))}) — thống nhất một phông nội dung")
    # ---------- tổng hợp: CHÍNH TẢ, DẤU CÂU, VIẾT HOA, HIỂN THỊ
    if kieu_dau["cu"] and kieu_dau["moi"]:
        ex = lambda d: ", ".join(f"{w} (slide {min(s)})" for w, s in list(d.items())[:4])
        add("CẢNH BÁO", 0, "chinh-ta", f"lẫn hai kiểu bỏ dấu — kiểu cũ: {ex(kieu_dau['cu'])}; kiểu mới: {ex(kieu_dau['moi'])}; thống nhất một kiểu")
    for (a, b), d in iy.items():
        if d[a] and d[b]: add("GỢI Ý", 0, "chinh-ta", f"lẫn '{a}' (slide {', '.join(map(str, sorted(d[a])[:4]))}) và '{b}' (slide {', '.join(map(str, sorted(d[b])[:4]))}) — thống nhất một cách viết")
    if quotes["thang"] and quotes["cong"]: add("GỢI Ý", 0, "dau-cau", f"lẫn ngoặc kép thẳng \" (slide {', '.join(map(str, sorted(quotes['thang'])[:5]))}) và ngoặc cong “ ” — dùng “ ”")
    elif quotes["thang"]: add("GỢI Ý", 0, "dau-cau", f"ngoặc kép thẳng \" ở slide {', '.join(map(str, sorted(quotes['thang'])[:5]))} — dấu hiệu chữ dán từ chatbot/mã; dùng “ ”")
    if ellipsis["..."] and ellipsis["…"]: add("GỢI Ý", 0, "dau-cau", "lẫn '...' và '…' — dùng một kiểu dấu chấm lửng")
    for ab, ss in cq_viet_tat.items():
        full_name = VIET_TAT[ab]
        if _cq_norm(full_name) not in cq_day_du:
            add("CẢNH BÁO", 0, "viet-hoa", f"chỉ có dạng viết tắt '{ab}' (slide {', '.join(map(str, sorted(ss)[:5]))}) — viết đầy đủ '{full_name}' ít nhất ở lần đầu")
    if lang_sai:
        add("GỢI Ý", 0, "hien-thi", f"chữ tiếng Việt gắn mã ngôn ngữ khác vi-VN ở slide {', '.join(map(str, sorted(lang_sai)[:10]))} — PowerPoint gạch đỏ chính tả khi sửa (tự sửa được)", True)
    for i, m in chart_nho:
        add("CẢNH BÁO", i, "hien-thi", "biểu đồ dùng cỡ chữ mặc định (≈10pt) — đặt nhãn, trục, chú giải ≥ 14pt" if m is None else f"biểu đồ có chữ {m:g}pt < 12pt — tăng cỡ nhãn/trục/chú giải")
    if notes_thieu:
        add("CẢNH BÁO", 0, "hien-thi", f"thiếu ghi chú diễn giả ở slide {', '.join(map(str, notes_thieu[:15]))}{'…' if len(notes_thieu) > 15 else ''}")
    return out, len(slides), {"embedded": embedded, "fams": {f: sorted(s) for f, s in fam_slides.items()}, "theme": theme, "muc": muc}

def ma_chu(t):
    res = []
    if unicodedata.normalize("NFC", t) != t: res.append(("LỖI", "chữ dùng dấu tổ hợp (Unicode NFD) — dấu có thể tách khỏi chữ, tìm/sắp xếp sai"))
    an = sorted({AN.get(c) or f"U+{ord(c):04X}" for c in t if c in AN or (unicodedata.category(c) in ("Cc", "Co") and c not in "\t\n\r")})
    if an: res.append(("LỖI", f"có ký tự ẩn ({', '.join(an)})"))
    if "\ufffd" in t: res.append(("LỖI", f"có ký tự hỏng '�' trong '{t.strip()[:40]}' — chữ bị mất khi chuyển mã"))
    if sum(c in TCVN3 for c in t) >= 2: res.append(("LỖI", f"chữ mã TCVN3 chưa chuyển sang Unicode: '{t.strip()[:40]}'"))
    if "Ð" in t or "ð" in t: res.append(("LỖI", "dùng chữ Ð/ð (Eth, U+00D0/U+00F0) thay cho Đ/đ — trông giống nhưng tìm kiếm, sắp xếp sai"))
    return res

def kiem_chu(t, idx, nm, rl, add, kieu_dau, iy, I_Y, quotes, ellipsis, cq_day_du, cq_viet_tat, p):
    tn = unicodedata.normalize("NFC", t)
    s = tn.strip()
    # mã chữ
    for lv, msg in ma_chu(t):
        add(lv, idx, "ma-chu", f"'{nm}': {msg}", "hỏng" not in msg and "TCVN3" not in msg)
    if KY_HIEU_SAI.search(tn) and not re.search(r"\bGDĐT\b", KY_HIEU_SAI.search(tn).group(0)):
        add("LỖI", idx, "ma-chu", f"'{nm}': ký hiệu '{KY_HIEU_SAI.search(tn).group(0)}' thiếu chữ Đ — viết ĐT (BGDĐT, SGDĐT, GDĐT)")
    # chính tả
    co_tv = any(c in VN_DAU for c in tn)
    for w in re.findall(r"[^\W\d_]+", tn):
        if not any(c in VN_DAU for c in w):
            r = kiem_am_tiet(w) if co_tv and w.islower() and len(w) <= 7 else None   # từ không dấu: chỉ luật c/k, g/gh, ng/ngh
            if r and r[0] and ("viết" in r[1] or "đi với u" in r[1]): add(r[0], idx, "chinh-ta", f"'{nm}': {r[1]}")
            continue
        r = kiem_am_tiet(w)
        if not r: continue
        lv, msg, goi_y, kieu = r
        if kieu: kieu_dau[kieu][w.lower()].add(idx)
        if lv:
            if w[:1].isupper() and lv == "CẢNH BÁO" and not w.isupper(): lv = "GỢI Ý"     # tên riêng, địa danh dân tộc
            add(lv, idx, "chinh-ta", f"'{nm}': {msg}")
    low = tn.lower()
    for a, b in I_Y:
        for x in (a, b):
            if re.search(rf"(?<![\w]){x}(?![\w])", low): iy[(a, b)][x].add(idx)
    for m in re.finditer(r"(?<![\w])([^\W\d_]+) \1(?![\w])", low):
        if m.group(1) in HU_TU: add("CẢNH BÁO", idx, "chinh-ta", f"'{nm}': lặp từ '{m.group(0)}'")
    if GIU_CHO.search(tn): add("CẢNH BÁO", idx, "chinh-ta", f"'{nm}': còn chữ giữ chỗ '{GIU_CHO.search(tn).group(0)}' — bổ sung nội dung")
    if MARKDOWN.search(tn): add("LỖI", idx, "chinh-ta", f"'{nm}': ký hiệu Markdown sót '{MARKDOWN.search(tn).group(0).strip()[:30]}' — hiển thị nguyên dấu */#/`")
    if LATEX.search(tn): add("LỖI", idx, "chinh-ta", f"'{nm}': mã LaTeX hiện nguyên dạng '{LATEX.search(tn).group(0)[:30]}' — dựng bằng MS.equation")
    # dấu câu & khoảng trắng
    if "  " in tn: add("CẢNH BÁO", idx, "dau-cau", f"'{nm}': hai khoảng trắng liền nhau trong '{s[:40]}'", True)
    if tn != tn.strip(" ") and s: add("GỢI Ý", idx, "dau-cau", f"'{nm}': khoảng trắng thừa đầu/cuối đoạn '{s[:30]}'", True)
    m = re.search(r"\S( +)([,;:!?)\]]|\.(?!\.))", tn)
    if m: add("CẢNH BÁO", idx, "dau-cau", f"'{nm}': khoảng trắng trước dấu câu '…{tn[max(0, m.start() - 8):m.end() + 2]}…'", True)
    m = re.search(r"[(\[] +| +[)\]]", tn)
    if m: add("CẢNH BÁO", idx, "dau-cau", f"'{nm}': khoảng trắng sát trong ngoặc '…{tn[max(0, m.start() - 6):m.end() + 6]}…'", True)
    m = re.search(r"[,;](?=[^\s\d,;\"”’)\]])", tn)
    if m: add("CẢNH BÁO", idx, "dau-cau", f"'{nm}': thiếu khoảng trắng sau dấu '{m.group(0)}' ở '…{tn[max(0, m.start() - 8):m.end() + 8]}…'", True)
    m = re.search(r"(?<=[a-zà-ỹđ]{2})[.:](?=[A-ZÀ-ỸĐ][a-zà-ỹđ])", tn)
    if m and not re.search(r"https?://|www\.", tn): add("CẢNH BÁO", idx, "dau-cau", f"'{nm}': thiếu khoảng trắng sau dấu '{m.group(0)}' ở '…{tn[max(0, m.start() - 8):m.end() + 8]}…'")
    m = re.search(r"([!?,;:])\1+|(?<!\.)\.\.(?!\.)|[!?][!?]+", tn)
    if m: add("CẢNH BÁO", idx, "dau-cau", f"'{nm}': dấu câu lặp '{m.group(0)}'")
    for o, c in (("(", ")"), ("[", "]"), ("“", "”")):
        if tn.count(o) != tn.count(c): add("CẢNH BÁO", idx, "dau-cau", f"'{nm}': ngoặc {o}{c} lệch cặp ({tn.count(o)} mở, {tn.count(c)} đóng) trong '{s[:40]}'")
    if tn.count('"') % 2: add("CẢNH BÁO", idx, "dau-cau", f"'{nm}': ngoặc kép \" lệch cặp trong '{s[:40]}'")
    if '"' in tn: quotes["thang"].add(idx)
    if "“" in tn or "”" in tn: quotes["cong"].add(idx)
    if "..." in tn: ellipsis["..."].add(idx)
    if "…" in tn: ellipsis["…"].add(idx)
    m = re.search(r"\d+\s?-\s?\d+", tn)
    if m and not re.search(r"\d{1,4}/\d{2,4}|[A-ZĐ]{2,}-\d|\d-[A-ZĐ]", tn): add("GỢI Ý", idx, "dau-cau", f"'{nm}': khoảng số '{m.group(0)}' dùng gạch nối — dùng gạch ngắn '–' (10–20)")
    if " - " in tn: add("GỢI Ý", idx, "dau-cau", f"'{nm}': gạch nối ' - ' dùng như gạch ngang — dùng '–' hoặc viết thành câu")
    if rl == "tieu-de" and re.search(r"(?<!\.)[.:;]$", s) and not s.endswith("..."): add("CẢNH BÁO", idx, "dau-cau", f"tiêu đề '{s[:40]}' kết bằng dấu '{s[-1]}' — bỏ dấu cuối tiêu đề")
    if re.match(r"^\s*(?:[-+*•◦▪►✓o]|–)\s+\S", tn) and not p["bullet"]: add("CẢNH BÁO", idx, "dau-cau", f"'{nm}': gạch đầu dòng gõ tay '{s[:20]}' — dùng định dạng bullet (thụt lề treo)")
    if "\t" in tn: add("GỢI Ý", idx, "dau-cau", f"'{nm}': có ký tự tab trong chữ — căn bằng khung/bảng")
    # viết hoa
    letters = [c for c in s if c.isalpha()]
    caps_attr = any(r.get("cap") == "all" for r in p["runs"] if not r.get("br"))
    nwords = len(s.split())
    if letters and (caps_attr or (len(letters) >= 8 and all(c.isupper() for c in letters))):
        if rl in ("noi-dung", "bang") and nwords >= 6: add("CẢNH BÁO", idx, "viet-hoa", f"'{nm}': đoạn {nwords} chữ viết HOA toàn bộ — khó đọc, dấu chồng; viết thường")
        elif rl == "tieu-de" and nwords >= 12: add("GỢI Ý", idx, "viet-hoa", f"tiêu đề {nwords} chữ viết HOA — rút gọn hoặc viết thường")
    ws = [w for w in re.findall(r"[^\W\d_]+", s) if len(w) > 1]
    if rl == "tieu-de" and len(ws) >= 4 and all(w[0].isupper() for w in ws) and not all(w.isupper() for w in ws):
        add("CẢNH BÁO", idx, "viet-hoa", f"tiêu đề '{s[:40]}' Viết Hoa Mỗi Chữ (kiểu tiếng Anh) — chỉ viết hoa chữ đầu và tên riêng")
    low = _cq_norm(tn)
    for cq in CO_QUAN:
        k = _cq_norm(cq)
        for m in re.finditer(rf"(?<![\w]){re.escape(k)}(?![\w])", low):
            if cq == "Thủ tướng Chính phủ" or not low[max(0, m.start() - 4):m.start()].endswith("phi "):
                cq_day_du.add(k)
                got = tn[m.start():m.end()]
                if got.replace("Uỷ", "Ủy") != cq and not got.isupper():
                    add("CẢNH BÁO", idx, "viet-hoa", f"'{nm}': '{got}' → viết '{cq}'")
    for ab in VIET_TAT:
        for m in re.finditer(rf"(?<![\w/-]){re.escape(ab)}(?![\w-])", tn):
            cq_viet_tat[ab].add(idx)
    if rl == "noi-dung" and letters and s[0].isalpha() and s[0].islower() and not re.match(r"^(e|i|x|y|n|m|k)\b|^https?|^www", s):
        add("GỢI Ý", idx, "viet-hoa", f"'{nm}': đầu đoạn viết thường '{s[:25]}'")

# ---------------------------------------------------------------- dựng thử (LibreOffice + pdffonts)
def norm_fam(s): return re.sub(r"[^a-z0-9]", "", s.lower())
def dung_thu(path, info, slides_n):
    out = []
    if not shutil.which("soffice") or not shutil.which("pdffonts"):
        return [("CẢNH BÁO", 0, "dung-thu", "không dựng thử được (cần LibreOffice và poppler-utils)")]
    dst = os.path.expanduser("~/.fonts/makeslides"); os.makedirs(dst, exist_ok=True)
    for slots in FILES.values():
        for rel in slots.values():
            d = os.path.join(dst, os.path.basename(rel))
            if not os.path.exists(d): shutil.copy(os.path.join(FONT_DIR, rel), d)
    subprocess.run(["fc-cache", "-f", dst], capture_output=True)
    tmp = tempfile.mkdtemp(prefix="ksvb_")
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, path], capture_output=True, timeout=300)
    pdf = os.path.join(tmp, os.path.splitext(os.path.basename(path))[0] + ".pdf")
    if not os.path.exists(pdf): return [("CẢNH BÁO", 0, "dung-thu", "LibreOffice không chuyển được sang PDF")]
    goi = Goi(path); slides = mo_ta_bai(goi)[0]
    visible = [i for i, part in enumerate(slides, 1) if goi.xml(part).get("show") != "0"]
    per = defaultdict(set)
    for f, ss in info["fams"].items():
        for s in ss: per[s].add(f)
    declared_all = {norm_fam(f) for f in info["fams"]} | {norm_fam(f) for f in PHONG_KY_HIEU}
    match = lambda r, d: r.startswith(d) or (d.startswith(r) and len(r) > 4)
    try:
        import pymupdf as fitz
    except Exception:
        try:
            import fitz
        except Exception:
            fitz = None
    pages = []
    if fitz:
        doc = fitz.open(pdf)
        for pg in doc:
            spans = []
            for b in pg.get_text("dict")["blocks"]:
                for ln in b.get("lines", []):
                    for sp in ln["spans"]:
                        if sp["text"].strip(): spans.append((norm_fam(re.split(r"[-,]", sp["font"].split("+", 1)[-1])[0]), sp["text"]))
            pages.append(spans)
    else:                                                     # không có PyMuPDF: chỉ biết phông của cả tệp
        res = subprocess.run(["pdffonts", pdf], capture_output=True, text=True).stdout.splitlines()[2:]
        allf = [(norm_fam(re.split(r"[-,]", l.split()[0].split("+", 1)[-1])[0]), "") for l in res if l.split()]
        pages = [allf] * len(visible)
        out.append(("GỢI Ý", 0, "dung-thu", "không có PyMuPDF (pip install pymupdf) — chỉ đối chiếu phông của cả tệp, không theo từng slide"))
    for page, sidx in enumerate(visible, 1):
        if page > len(pages): break
        spans = pages[page - 1]
        rendered = {f for f, _ in spans}
        for f in sorted(per[sidx]):
            if f in PHONG_KY_HIEU: continue
            nf = norm_fam(f)
            if rendered and not any(match(r, nf) for r in rendered):
                out.append(("CẢNH BÁO", sidx, "dung-thu", f"phông {f} không hiển thị được trên máy dựng — chữ bị thay bằng phông khác; nhúng phông hoặc đổi sang phông của gói"))
        fb = defaultdict(str)
        for f, t in spans:
            if f and not any(match(f, d) for d in declared_all) and f not in ("opensymbol", "symbol"): fb[f] += t.strip() + " "
        for f, t in fb.items():
            sample = t.strip()[:28] + ("…" if len(t.strip()) > 28 else "")
            out.append(("CẢNH BÁO", sidx, "dung-thu", f"chữ '{sample}' hiển thị bằng phông dự phòng {f} — phông khai báo không dùng được hoặc thiếu ký tự"))
    shutil.rmtree(tmp, ignore_errors=True)
    return out

# ---------------------------------------------------------------- tự sửa (chỉ phần không đổi câu chữ)
def _sua_text(t):
    t2 = unicodedata.normalize("NFC", t)
    t2 = "".join(c for c in t2 if c not in AN and not (unicodedata.category(c) in ("Cc",) and c not in "\t\n\r"))
    t2 = t2.replace("Ð", "Đ").replace("ð", "đ")
    t2 = re.sub(r"(?<=\S) {2,}(?=\S)", " ", t2)
    t2 = re.sub(r"(?<=\S) +(?=[,;:!?)\]])", "", t2)
    t2 = re.sub(r"(?<=\S) +\.(?!\.)", ".", t2)
    t2 = re.sub(r"([(\[]) +", r"\1", t2)
    t2 = re.sub(r"[,;](?=[^\s\d,;\"”’)\]])", lambda m: m.group(0) + " ", t2)
    return t2

def sua(path, out_path):
    zin = zipfile.ZipFile(path); log = []
    goi = Goi(path); thu_tu = {part: i for i, part in enumerate(mo_ta_bai(goi)[0], 1)}
    for part, i in list(thu_tu.items()):
        for typ, tgt, _ in goi.rels(part).values():
            if typ == "notesSlide": thu_tu[tgt] = i
    rx_p = re.compile(r"<a:p>.*?</a:p>|<a:p\s[^>]*>.*?</a:p>", re.S)
    rx_t = re.compile(r"<a:t>(.*?)</a:t>", re.S)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zo:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if re.match(r"ppt/(slides/slide|notesSlides/notesSlide)\d+\.xml$", item.filename):
                xml = data.decode("utf8"); before = xml; counts = Counter()
                def fix_p(mp):
                    px = mp.group(0)
                    ts = [unescape(m.group(1)) for m in rx_t.finditer(px)]
                    new = [_sua_text(x) for x in ts]
                    for k in range(1, len(new)):                       # khoảng trắng kép vắt qua hai run
                        if new[k - 1].endswith(" ") and new[k].startswith(" "): new[k] = new[k].lstrip(" ")
                    if new:                                            # đầu/cuối đoạn
                        new[0] = new[0].lstrip(" "); new[-1] = new[-1].rstrip(" ")
                    for a, b in zip(ts, new):
                        if a != b: counts["chu"] += 1
                    it = iter(new)
                    px = rx_t.sub(lambda m: "<a:t>" + escape(next(it)) + "</a:t>", px)
                    if any(c in VN_DAU for c in "".join(new)):           # mã ngôn ngữ vi-VN
                        def lang(m):
                            tag = m.group(0)
                            if re.search(r'\blang="vi', tag): return tag
                            counts["lang"] += 1
                            return re.sub(r'\blang="[^"]*"', 'lang="vi-VN"', tag) if "lang=" in tag else tag.replace(m.group(1), m.group(1) + ' lang="vi-VN"', 1)
                        px = re.sub(r"(<a:(?:rPr|endParaRPr))(?=[\s/>])[^>]*>", lang, px)
                        n0 = px.count("<a:r><a:t>"); px = px.replace("<a:r><a:t>", '<a:r><a:rPr lang="vi-VN"/><a:t>'); counts["lang"] += n0
                    return px
                xml = rx_p.sub(fix_p, xml)
                for bad, good in BANNED.items():
                    n = xml.count(f'typeface="{bad}"')
                    if n: xml = xml.replace(f'typeface="{bad}"', f'typeface="{good}"'); counts["phong"] += n
                if xml != before:
                    s = thu_tu.get(item.filename, "?"); loai = "ghi chú slide" if "notes" in item.filename else "slide"
                    parts = []
                    if counts["chu"]: parts.append(f"chuẩn hoá {counts['chu']} đoạn chữ (Unicode, ký tự ẩn, khoảng trắng)")
                    if counts["lang"]: parts.append(f"gắn vi-VN cho {counts['lang']} run")
                    if counts["phong"]: parts.append(f"đổi {counts['phong']} chỗ phông bị loại")
                    log.append(f"{loai} {s}: " + "; ".join(parts))
                data = xml.encode("utf8")
            elif item.filename == "ppt/presentation.xml" or re.match(r"ppt/(theme/theme|slideMasters/slideMaster|slideLayouts/slideLayout)\d+\.xml$", item.filename):
                xml = data.decode("utf8")
                for bad, good in BANNED.items(): xml = xml.replace(f'typeface="{bad}"', f'typeface="{good}"')
                data = xml.encode("utf8")
            zo.writestr(item, data)
    return log

# ---------------------------------------------------------------- gộp các script khác (--day-du)
def gop_day_du(path, co_min, co_phu, chu_max):
    rows = []
    try:
        import kiem_tra_van_ban as KV
        o, _ = KV.kiem(path, co_min, co_phu, chu_max)
        rows += [{"muc": x["muc"], "slide": x["slide"], "nhom": "trinh-bay", "noi_dung": x["noi_dung"], "sua": bool(x.get("sua"))} for x in o]
    except Exception as e:
        rows.append({"muc": "CẢNH BÁO", "slide": 0, "nhom": "trinh-bay", "noi_dung": f"không chạy được kiem_tra_van_ban.py: {e}", "sua": False})
    try:
        import kiem_tra_slide as KS
        o, _, _ = KS.check(path)
        rows += [{"muc": a, "slide": b, "nhom": c, "noi_dung": d, "sua": False} for a, b, c, d in o if c != "phông"]
    except Exception as e:
        rows.append({"muc": "CẢNH BÁO", "slide": 0, "nhom": "màu", "noi_dung": f"không chạy được kiem_tra_slide.py: {e}", "sua": False})
    return rows

def main():
    a = sys.argv[1:]
    if not a or a[0].startswith("-"): print(__doc__); sys.exit(2)
    arg = lambda k, d=None: (type(d)(a[a.index(k) + 1]) if d is not None else a[a.index(k) + 1]) if k in a else d
    src = a[0]
    bc = CONTEXTS.get(arg("--boi-canh")) if arg("--boi-canh") else None
    co_min = arg("--co-toi-thieu", bc["body_min"] if bc else 24)
    co_phu, chu_max = arg("--co-phu", 16), arg("--chu-toi-da", bc["max_words"] if bc else 30)
    muc, pc = arg("--muc"), arg("--phong-cach")
    if pc and pc not in STYLES: sys.exit(f"Không có phong cách '{pc}'. Có: {', '.join(STYLES)}")
    if muc and muc not in ("chinh-quy", "ban-chinh-quy", "kieu-cach"): sys.exit("--muc nhận chinh-quy | ban-chinh-quy | kieu-cach")
    if "--sua" in a:
        dst = arg("--sua")
        log = sua(src, dst)
        if "--day-du" in a:                         # gộp cả phần tự sửa cỡ chữ / xuống dòng của kiem_tra_van_ban.py
            tmp = dst + ".tmp.pptx"
            try:
                log += [x for x in KV.sua(dst, tmp, co_min)]
                os.replace(tmp, dst)
            except Exception as e:
                log.append(f"không chạy được phần tự sửa của kiem_tra_van_ban.py: {e}")
                if os.path.exists(tmp): os.remove(tmp)
        for line in log: print("  sửa:", line)
        print(f"Đã ghi {dst} ({len(log)} phần được sửa); kiểm lại:\n")
        src = dst
    out, n, info = kiem(src, muc, pc, co_min, co_phu, "--bo-qua-ghi-chu" in a)
    if "--hien-thi" in a:
        out += [{"muc": lv, "slide": s, "nhom": g, "noi_dung": m, "sua": False} for lv, s, g, m in dung_thu(src, info, n)]
    if "--day-du" in a: out += gop_day_du(src, co_min, co_phu, chu_max)
    chi = set(arg("--chi").split(",")) if arg("--chi") else None
    if chi: out = [o for o in out if o["nhom"] in chi]
    seen, rows = set(), []
    order = {"LỖI": 0, "CẢNH BÁO": 1, "GỢI Ý": 2}
    for o in sorted(out, key=lambda o: (order[o["muc"]], o["slide"], NHOM.index(o["nhom"]) if o["nhom"] in NHOM else 99)):
        k = (o["muc"], o["slide"], o["noi_dung"])
        if k in seen: continue
        seen.add(k); rows.append(o)
    if "--json" in a:
        print(json.dumps(rows, ensure_ascii=False, indent=1)); sys.exit(1 if any(r["muc"] == "LỖI" for r in rows) else 0)
    print(f"{src}: {n} slide · mức {info['muc'] or 'chưa rõ'} · phông dùng: {', '.join(sorted(info['fams'])) or '—'} · đã nhúng: {', '.join(sorted(info['embedded'])) or 'không'}")
    groups = Counter(); lv_count = Counter()
    for r in rows: groups[(r["nhom"], r["muc"])] += 1; lv_count[r["muc"]] += 1
    nh = sorted({r["nhom"] for r in rows}, key=lambda g: NHOM.index(g) if g in NHOM else 99)
    if nh:
        print("\nTổng hợp theo nhóm:")
        for g in nh: print(f"  {TEN_NHOM.get(g, g):<14} LỖI {groups[(g, 'LỖI')]:>3} · CẢNH BÁO {groups[(g, 'CẢNH BÁO')]:>3} · GỢI Ý {groups[(g, 'GỢI Ý')]:>3}")
    for lv in order:
        sub = [r for r in rows if r["muc"] == lv]
        print(f"\n{lv} ({len(sub)})")
        for r in sub:
            print(f"  [{'toàn bài' if r['slide'] == 0 else 'slide ' + str(r['slide'])}] {TEN_NHOM.get(r['nhom'], r['nhom'])}: {r['noi_dung']}{'  (tự sửa được: --sua)' if r['sua'] else ''}")
    sys.exit(1 if lv_count["LỖI"] else 0)

if __name__ == "__main__":
    main()
