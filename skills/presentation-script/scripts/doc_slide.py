#!/usr/bin/env python3
"""Đọc bộ slide (.pptx) thành slide.json để viết kịch bản thuyết trình.

Lấy cho từng slide: tiêu đề, chữ trên slide, ghi chú diễn giả hiện có, số cú nhấp
(hiệu ứng "On Click"), slide ẩn; đề xuất thời lượng từng slide theo tổng thời gian.

    python3 doc_slide.py bai.pptx --ra slide.json --phut 15 --boi-canh cong-so [--anh anh_slide]

--anh: dựng ảnh thu nhỏ từng slide (LibreOffice → pdftoppm) để chèn vào bản in kịch bản.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

from pptx import Presentation
from pptx.util import Emu

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kb_chung as kb  # noqa: E402

NS_P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"


def so_cu_nhap(slide):
    """Số cú nhấp = số nhóm hiệu ứng bắt đầu bằng clickEffect trong chuỗi chính."""
    n = 0
    for ctn in slide._element.iter(NS_P + "cTn"):
        if ctn.get("nodeType") == "clickEffect":
            n += 1
    return n


def chu_trong_hinh(shape):
    out = []
    if shape.shape_type == 6 and hasattr(shape, "shapes"):  # nhóm
        for s in shape.shapes:
            out += chu_trong_hinh(s)
        return out
    if getattr(shape, "has_text_frame", False) and shape.has_text_frame:
        t = kb.nfc(shape.text_frame.text).strip()
        if t:
            out.append((shape, t))
    if getattr(shape, "has_table", False) and shape.has_table:
        for row in shape.table.rows:
            for cell in row.cells:
                t = kb.nfc(cell.text).strip()
                if t:
                    out.append((shape, t))
    return out


def tieu_de(slide, cac_chu):
    if slide.shapes.title is not None and slide.shapes.title.has_text_frame:
        t = kb.nfc(slide.shapes.title.text_frame.text).strip()
        if t:
            return t
    # hộp chữ đặt tên "tieu-de" (quy ước của make-slides bản Gemini app) là tiêu đề
    for shape, t in cac_chu:
        if (shape.name or "").lower() in ("tieu-de", "title"):
            return t.replace("\n", " ")
    # không có placeholder tiêu đề: lấy khối chữ có cỡ lớn nhất, ưu tiên nằm trên;
    # bỏ cảnh morph (tên "!!…") và con số/ký hiệu ngắn (số phần "01", "×2") vì chúng to nhưng không phải tiêu đề
    ung_vien = [(sh, t) for sh, t in cac_chu if not (sh.name or "").startswith("!!")]
    dai = [(sh, t) for sh, t in ung_vien if len(re.sub(r"[\W\d_]", "", t)) >= 4]
    tot, diem = "", -1
    for shape, t in (dai or ung_vien):
        if not getattr(shape, "has_text_frame", False):
            continue
        co = 0
        for p in shape.text_frame.paragraphs:
            for r in p.runs:
                if r.font.size:
                    co = max(co, r.font.size.pt)
        top = Emu(shape.top or 0).inches if shape.top is not None else 5
        d = co * 10 - top
        if co and d > diem and len(t) <= 160:
            tot, diem = t, d
    return tot.replace("\n", " ")


def vai_slide(i, n, tieu, so_chu):
    t = tieu.lower()
    if i == 1:
        return "bia"
    if i == n and re.search(r"cảm ơn|trân trọng|thank|hỏi đáp|q&a", t):
        return "ket"
    if re.search(r"^(phần|chương|mục)\s+[ivx\d]+", t) or (so_chu <= 8 and re.match(r"^\d{1,2}\b", t)):
        return "chia-phan"
    return "noi-dung"


def de_xuat_giay(slides, tong_giay):
    """Chia tổng thời gian theo trọng số: bìa/kết ngắn, slide nhiều bước dài hơn."""
    co_dinh = {"bia": 30, "ket": 20, "chia-phan": 15}
    tg_co_dinh = sum(co_dinh.get(s["vai"], 0) for s in slides if not s["an"])
    con = max(0, tong_giay - tg_co_dinh)
    trong_so = {}
    for s in slides:
        if s["an"] or s["vai"] in co_dinh:
            continue
        trong_so[s["so"]] = 1 + 0.4 * s["so_nhap"] + min(s["so_am_tiet"], 60) / 40
    tong_ts = sum(trong_so.values()) or 1
    for s in slides:
        if s["an"]:
            s["giay_de_xuat"] = 0
        elif s["vai"] in co_dinh:
            s["giay_de_xuat"] = co_dinh[s["vai"]]
        else:
            s["giay_de_xuat"] = int(round(con * trong_so[s["so"]] / tong_ts / 5) * 5) or 15


def dung_anh(pptx, thu_muc):
    os.makedirs(thu_muc, exist_ok=True)
    if not shutil.which("soffice") or not shutil.which("pdftoppm"):
        print("CẢNH BÁO: thiếu soffice hoặc pdftoppm, bỏ qua ảnh thu nhỏ.", file=sys.stderr)
        return {}
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, pptx],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
        pdf = os.path.join(tmp, os.path.splitext(os.path.basename(pptx))[0] + ".pdf")
        subprocess.run(["pdftoppm", "-png", "-r", "60", pdf, os.path.join(thu_muc, "slide")], check=True)
    anh = {}
    for ten in sorted(os.listdir(thu_muc)):
        m = re.match(r"slide-0*(\d+)\.png$", ten)
        if m:
            anh[int(m.group(1))] = os.path.join(thu_muc, ten)
    return anh


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx")
    ap.add_argument("--ra", default="slide.json")
    ap.add_argument("--phut", type=float, help="tổng thời lượng trình bày (phút)")
    ap.add_argument("--boi-canh", default="", help="khoá bối cảnh trong make-slides/assets/contexts.json")
    ap.add_argument("--toc-do", type=int, help="âm tiết/phút (mặc định theo bối cảnh)")
    ap.add_argument("--anh", help="thư mục ghi ảnh thu nhỏ từng slide")
    a = ap.parse_args()

    prs = Presentation(a.pptx)
    n = len(prs.slides)
    slides = []
    for i, slide in enumerate(prs.slides, 1):
        cac_chu = []
        for shape in slide.shapes:
            cac_chu += chu_trong_hinh(shape)
        td = tieu_de(slide, cac_chu)
        chu = "\n".join(t for _, t in cac_chu)
        ghi_chu = ""
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None:
            ghi_chu = kb.nfc(slide.notes_slide.notes_text_frame.text).strip()
        so_at = kb.dem_am_tiet(chu)
        slides.append({
            "so": i,
            "tieu_de": td,
            "vai": vai_slide(i, n, td, so_at),
            "chu": chu,
            "so_am_tiet": so_at,
            "so_nhap": so_cu_nhap(slide),
            "an": slide._element.get("show") == "0",
            "ghi_chu": ghi_chu,
        })

    ctx = kb.doc_contexts().get(a.boi_canh, {})
    toc_do = a.toc_do or kb.TOC_DO.get(a.boi_canh, kb.TOC_DO_MAC_DINH)
    phut = a.phut
    if not phut and ctx.get("sec_per_slide"):
        phut = round(sum(1 for s in slides if not s["an"]) * ctx["sec_per_slide"] / 60, 1)
    if phut:
        de_xuat_giay(slides, phut * 60)

    if a.anh:
        anh = dung_anh(a.pptx, a.anh)
        for s in slides:
            if s["so"] in anh:
                s["anh"] = os.path.abspath(anh[s["so"]])

    kq = {"nguon": os.path.abspath(a.pptx), "boi_canh": a.boi_canh, "thoi_luong_phut": phut,
          "toc_do": toc_do, "slides": slides}
    kb.ghi_json(kq, a.ra)

    print(f"{n} slide · {sum(s['so_nhap'] for s in slides)} cú nhấp · tốc độ {toc_do} âm tiết/phút"
          + (f" · tổng {phut} phút" if phut else ""))
    print(f"{'STT':>3}  {'Vai':<10} {'Nhấp':>4} {'Giây':>5}  Tiêu đề")
    for s in slides:
        an = " (ẩn)" if s["an"] else ""
        print(f"{s['so']:>3}  {s['vai']:<10} {s['so_nhap']:>4} {s.get('giay_de_xuat', '-'):>5}  {s['tieu_de'][:70]}{an}")
    print(f"→ {a.ra}")


if __name__ == "__main__":
    main()
