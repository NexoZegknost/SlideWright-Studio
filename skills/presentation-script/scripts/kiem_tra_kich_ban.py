#!/usr/bin/env python3
"""Kiểm tra kịch bản thuyết trình (kich_ban.json), đối chiếu với bộ slide (slide.json).

    python3 kiem_tra_kich_ban.py kich_ban.json [--slide slide.json]

In bảng thời lượng (ước theo tốc độ nói) và danh sách LỖI / CẢNH BÁO.
Thoát mã 1 khi còn LỖI.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kb_chung as kb  # noqa: E402

# Dùng lại bộ kiểm tra mã chữ và âm tiết tiếng Việt của make-slides (nếu có).
sys.path.insert(0, os.path.join(kb.GOC_SKILL, "..", "make-slides", "scripts"))
try:
    from kiem_soat_van_ban import kiem_am_tiet, ma_chu  # noqa: E402
except Exception:  # noqa: BLE001
    kiem_am_tiet = ma_chu = None

# Cụm sáo rỗng hoặc văn viết, nghe không tự nhiên khi nói (xem references/viet-loi-noi.md).
SAO_RONG = [
    "hãy cùng khám phá", "hành trình", "không chỉ", "đóng vai trò quan trọng", "vô cùng quan trọng",
    "như đã nêu trên", "trên đây là", "sau đây là", "dưới đây", "tóm lại, có thể thấy",
    "trong bối cảnh hiện nay", "ngày càng phát triển", "một cách hiệu quả", "nâng tầm",
    "bức tranh toàn cảnh", "chìa khóa", "chìa khoá", "đòn bẩy", "xin chân thành cảm ơn quý vị đã lắng nghe",
]
MARKDOWN = re.compile(r"\*\*|__|^#+\s|`|\$[^$]+\$|\\\(|\\\[", re.M)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


def cau(text):
    return [c.strip() for c in re.split(r"(?<=[.!?…])\s+|\n+", text) if c.strip()]


def am_tiet_list(text):
    return [t.lower() for t in kb._TU.findall(kb._NHAN.sub(" ", kb.nfc(text)))]


def doc_lai_slide(chu_slide, loi):
    """Tìm đoạn ≥ 10 âm tiết liên tiếp chép y nguyên từ slide sang lời nói."""
    a, b = am_tiet_list(chu_slide), " ".join(am_tiet_list(loi))
    for i in range(0, max(0, len(a) - 9)):
        doan = " ".join(a[i:i + 10])
        if doan in b:
            return doan
    return ""


def kiem_chinh_ta(text, nhan, loi, canh_bao):
    if ma_chu is None:
        return
    for muc, msg in ma_chu(text):
        (loi if muc == "LỖI" else canh_bao).append(f"{nhan}: {msg}")
    da = set()
    for tu in re.findall(r"[^\W\d_]+", kb._NHAN.sub(" ", kb.nfc(text))):
        if tu in da:
            continue
        da.add(tu)
        kq = kiem_am_tiet(tu)
        if kq and kq[0]:
            (loi if kq[0] == "LỖI" else canh_bao).append(f"{nhan}: chính tả — {kq[1]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kich_ban")
    ap.add_argument("--slide", help="slide.json do doc_slide.py tạo")
    a = ap.parse_args()

    kbj = kb.doc_json(a.kich_ban)
    sl = kb.doc_json(a.slide) if a.slide else {"slides": []}
    theo_so = {s["so"]: s for s in sl.get("slides", [])}
    toc_do = kbj.get("toc_do") or sl.get("toc_do") or kb.TOC_DO.get(kbj.get("boi_canh", ""), kb.TOC_DO_MAC_DINH)
    muc_tieu = (kbj.get("thoi_luong_phut") or sl.get("thoi_luong_phut") or 0) * 60
    loi, canh_bao = [], []

    da_viet = {s["so"] for s in kbj.get("slides", [])}
    for so, s in theo_so.items():
        if not s.get("an") and so not in da_viet:
            loi.append(f"Slide {so}: chưa có lời nói ({s.get('tieu_de', '')[:50]})")

    tong, dong_bang = 0.0, []
    ds = sorted(kbj.get("slides", []), key=lambda s: s["so"])
    for idx, s in enumerate(ds):
        so = s["so"]
        goc = theo_so.get(so, {})
        nhap = goc.get("so_nhap", len(s.get("nhip", [])))
        noi = kb.loi_noi_slide(s)
        g = kb.giay_noi(noi, toc_do, nhap)
        tong += g
        dat = s.get("giay") or goc.get("giay_de_xuat") or 0
        dong_bang.append((so, s.get("tieu_de") or goc.get("tieu_de", ""), dat, g, tong))
        nhan = f"Slide {so}"

        if not noi.strip():
            loi.append(f"{nhan}: lời nói trống")
            continue
        if goc and nhap > 0 and len(s.get("nhip", [])) != nhap:
            loi.append(f"{nhan}: slide có {nhap} cú nhấp nhưng kịch bản có {len(s.get('nhip', []))} nhịp — mỗi cú nhấp cần đúng một nhịp")
        if goc and nhap == 0 and len(s.get("nhip", [])) > 1:
            canh_bao.append(f"{nhan}: slide không có cú nhấp mà kịch bản chia {len(s['nhip'])} nhịp — gộp lại hoặc thêm hiệu ứng ở make-slides")
        if dat and abs(g - dat) > max(10, 0.3 * dat):
            canh_bao.append(f"{nhan}: lời nói ≈ {g:.0f} s, thời lượng dành cho slide {dat} s — {'cắt bớt' if g > dat else 'bổ sung ví dụ/dẫn chứng'}")
        if not s.get("mo") and goc.get("vai", "noi-dung") != "bia":
            canh_bao.append(f"{nhan}: thiếu câu mở [Mở]")
        if not s.get("chuyen") and idx < len(ds) - 1:
            canh_bao.append(f"{nhan}: thiếu câu chuyển [Chuyển] sang slide sau")
        for c in cau(noi):
            n = kb.dem_am_tiet(c)
            if n > 35:
                canh_bao.append(f"{nhan}: câu {n} âm tiết, khó nói một hơi — tách đôi: \"{c[:60]}…\"")
        chu_slide = goc.get("chu", "")
        if chu_slide:
            d = doc_lai_slide(chu_slide, noi)
            if d:
                canh_bao.append(f"{nhan}: đọc lại nguyên văn chữ trên slide (\"{d}…\") — diễn giải thay vì đọc")
            for tu in s.get("nhan", []):
                if kb.nfc(tu).lower() not in chu_slide.lower():
                    canh_bao.append(f"{nhan}: từ nhấn \"{tu}\" không có trên slide")
        for tu in s.get("nhan", []):
            if kb.nfc(tu).lower() not in noi.lower():
                canh_bao.append(f"{nhan}: từ nhấn \"{tu}\" không xuất hiện trong lời nói")
        thap = noi.lower()
        for cum in SAO_RONG:
            if cum in thap:
                canh_bao.append(f"{nhan}: cụm sáo rỗng/văn viết \"{cum}\"")
        if MARKDOWN.search(noi) or EMOJI.search(noi):
            canh_bao.append(f"{nhan}: còn ký hiệu Markdown/LaTeX/emoji trong lời nói")
        kiem_chinh_ta(noi, nhan, loi, canh_bao)
        if "[cần bổ sung]" in noi:
            canh_bao.append(f"{nhan}: còn [cần bổ sung] — báo người dùng")

    if muc_tieu:
        lech = (tong - muc_tieu) / muc_tieu
        thong_diep = f"tổng ≈ {kb.mm_ss(tong)} so với mục tiêu {kb.mm_ss(muc_tieu)} ({lech:+.0%})"
        if abs(lech) > 0.10:
            loi.append("Thời lượng: " + thong_diep)
        elif abs(lech) > 0.05:
            canh_bao.append("Thời lượng: " + thong_diep)

    hd = kbj.get("hoi_dap", [])
    if len(hd) < 3:
        canh_bao.append(f"Hỏi đáp: mới có {len(hd)} câu, nên chuẩn bị ≥ 5 câu")
    for i, q in enumerate(hd, 1):
        kiem_chinh_ta(q.get("hoi", "") + " " + q.get("tra_loi", ""), f"Hỏi đáp {i}", loi, canh_bao)
        if not q.get("tra_loi"):
            loi.append(f"Hỏi đáp {i}: chưa có gợi ý trả lời")
        elif re.search(r"\d", q["tra_loi"]) and not q.get("nguon"):
            canh_bao.append(f"Hỏi đáp {i}: câu trả lời có số liệu nhưng chưa ghi nguồn")

    print(f"Tốc độ {toc_do} âm tiết/phút")
    print(f"{'STT':>3}  {'Dành':>5} {'Ước':>5} {'Luỹ kế':>7}  Tiêu đề")
    for so, td, dat, g, lk in dong_bang:
        print(f"{so:>3}  {dat or '-':>5} {g:5.0f} {kb.mm_ss(lk):>7}  {td[:60]}")
    print(f"Tổng ≈ {kb.mm_ss(tong)}" + (f" / mục tiêu {kb.mm_ss(muc_tieu)}" if muc_tieu else ""))
    print()
    for m in loi:
        print("LỖI      ", m)
    for m in canh_bao:
        print("CẢNH BÁO ", m)
    print(f"\n{len(loi)} lỗi, {len(canh_bao)} cảnh báo")
    sys.exit(1 if loi else 0)


if __name__ == "__main__":
    main()
