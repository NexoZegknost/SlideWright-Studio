"""Hàm dùng chung cho skill presentation-script: đếm âm tiết, ước thời lượng nói,
tách các mốc trong lời nói ([Mở], [Nhấp n], [Nhấn], [Dừng], [Chuyển])."""
import json
import math
import os
import re
import unicodedata

THU_MUC = os.path.dirname(os.path.abspath(__file__))
GOC_SKILL = os.path.dirname(THU_MUC)
CONTEXTS = os.path.join(GOC_SKILL, "..", "make-slides", "assets", "contexts.json")

# Tốc độ nói mặc định (âm tiết/phút) theo bối cảnh của make-slides.
TOC_DO = {
    "hoc-sinh-sinh-vien": 130,
    "cong-so": 130,
    "hoi-nghi": 120,
    "bao-ve-do-an": 135,
    "giang-day": 120,
    "tap-huan": 125,
    "online": 135,
    "thi-pitch": 145,
    "doc-truoc": 130,
    "trinh-chieu-tu-dong": 130,
}
TOC_DO_MAC_DINH = 130
GIAY_MOI_NHAP = 0.5   # thao tác bấm chuyển bước
GIAY_MOI_DUNG = 2.0   # mỗi [Dừng] trong lời nói

_TU = re.compile(r"[0-9]+(?:[.,][0-9]+)*|[^\W\d_]+", re.UNICODE)
_NHAN = re.compile(r"\[(?:Mở|Nhấp\s*\d*|Nhấn|Dừng|Chuyển|Hỏi|Nhìn|Chậm)[^\]]*\]")


def nfc(s):
    return unicodedata.normalize("NFC", s or "")


def doc_contexts():
    try:
        with open(CONTEXTS, encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return {}


def am_tiet_so(so):
    """Ước số âm tiết khi đọc một con số (2025 → hai nghìn không trăm hai mươi lăm ≈ 7)."""
    chu_so = re.sub(r"\D", "", so)
    if not chu_so:
        return 0
    if len(chu_so) == 1:
        return 1
    return min(12, math.ceil(len(chu_so) * 1.6))


def dem_am_tiet(text):
    """Đếm âm tiết đọc thành tiếng, bỏ qua các nhãn mốc trong ngoặc vuông."""
    text = _NHAN.sub(" ", nfc(text))
    n = 0
    for t in _TU.findall(text):
        n += am_tiet_so(t) if t[0].isdigit() else 1
    return n


def so_dung(text):
    return len(re.findall(r"\[Dừng[^\]]*\]", nfc(text)))


def giay_noi(text, toc_do=TOC_DO_MAC_DINH, so_nhap=0):
    """Thời lượng ước tính (giây) của một đoạn lời nói."""
    return dem_am_tiet(text) / toc_do * 60 + so_dung(text) * GIAY_MOI_DUNG + so_nhap * GIAY_MOI_NHAP


def loi_noi_slide(s):
    """Ghép toàn bộ lời nói của một slide trong kich_ban.json thành một chuỗi."""
    phan = [s.get("mo", "")]
    phan += list(s.get("nhip", []))
    phan.append(s.get("chuyen", ""))
    return " ".join(p for p in phan if p)


def ghi_chu_slide(s):
    """Ghi chú diễn giả theo đúng mẫu của make-slides."""
    dong = []
    if s.get("mo"):
        dong.append(f"[Mở] {s['mo']}")
    for i, nhip in enumerate(s.get("nhip", []), 1):
        dong.append(f"[Nhấp {i}] {nhip}")
    if s.get("nhan"):
        dong.append("[Nhấn] " + ", ".join(s["nhan"]))
    if s.get("chuyen"):
        dong.append(f"[Chuyển] {s['chuyen']}")
    if s.get("luu_y"):
        dong.append(f"[Lưu ý] {s['luu_y']}")
    return "\n".join(dong)


def mm_ss(giay):
    giay = int(round(giay))
    return f"{giay // 60:02d}:{giay % 60:02d}"


def doc_json(duong_dan):
    with open(duong_dan, encoding="utf-8") as f:
        return json.load(f)


def ghi_json(du_lieu, duong_dan):
    with open(duong_dan, "w", encoding="utf-8") as f:
        json.dump(du_lieu, f, ensure_ascii=False, indent=2)
