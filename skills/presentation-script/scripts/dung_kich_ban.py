#!/usr/bin/env python3
"""Dựng đầu ra từ kich_ban.json:
  1. ghi lời nói vào ghi chú diễn giả của bộ slide (tệp mới, không ghi đè bản gốc);
  2. bản in kịch bản Word (.docx, bố cục ở ban_in.py): bìa có khối thông số, bảng phân bổ
     thời gian, thẻ lời nói từng slide kèm ảnh thu nhỏ, hỏi đáp dự kiến, thẻ nhắc.

    python3 dung_kich_ban.py kich_ban.json [--slide slide.json] \
        [--pptx bai.pptx --ra-pptx bai_kich_ban.pptx [--ppsx]] [--ra-docx KichBan.docx]
"""
import argparse
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kb_chung as kb  # noqa: E402

NHAN_GHI_CHU = re.compile(r"^\[(Mở|Nhấp\s*\d*|Nhấn|Chuyển|Lưu ý|Dừng)\]")


# ---------------------------------------------------------------- ghi chú PowerPoint
def ghi_ghi_chu(pptx_vao, pptx_ra, kbj):
    from pptx import Presentation
    prs = Presentation(pptx_vao)
    theo_so = {s["so"]: s for s in kbj["slides"]}
    for i, slide in enumerate(prs.slides, 1):
        s = theo_so.get(i)
        if not s:
            continue
        tf = slide.notes_slide.notes_text_frame
        cu = kb.nfc(tf.text).strip() if tf is not None else ""
        # giữ lại dòng không phải lời nói (nguồn ảnh, tác giả, tài liệu…)
        giu = [d for d in cu.splitlines() if d.strip() and not NHAN_GHI_CHU.match(d.strip())]
        moi = kb.ghi_chu_slide(s)
        if giu:
            moi += "\n\n" + "\n".join(giu)
        tf.text = moi
    prs.save(pptx_ra)


def sang_ppsx(pptx, ppsx):
    """Đổi loại tệp chính để mở thẳng vào chế độ trình chiếu."""
    with zipfile.ZipFile(pptx) as zi, zipfile.ZipFile(ppsx, "w", zipfile.ZIP_DEFLATED) as zo:
        for item in zi.infolist():
            data = zi.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = data.replace(b"presentationml.presentation.main+xml", b"presentationml.slideshow.main+xml")
            zo.writestr(item, data)


from ban_in import dung_docx  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kich_ban")
    ap.add_argument("--slide")
    ap.add_argument("--pptx", help="bộ slide gốc để ghi ghi chú diễn giả")
    ap.add_argument("--ra-pptx")
    ap.add_argument("--ppsx", action="store_true", help="xuất thêm .ppsx cạnh --ra-pptx")
    ap.add_argument("--ra-docx")
    a = ap.parse_args()

    kbj = kb.doc_json(a.kich_ban)
    sl = kb.doc_json(a.slide) if a.slide else {}
    if a.pptx:
        ra = a.ra_pptx or os.path.splitext(a.pptx)[0] + "_kich_ban.pptx"
        if os.path.abspath(ra) == os.path.abspath(a.pptx):
            sys.exit("Không ghi đè bộ slide gốc — chọn tên khác cho --ra-pptx")
        ghi_ghi_chu(a.pptx, ra, kbj)
        print("→", ra)
        if a.ppsx:
            sang_ppsx(ra, os.path.splitext(ra)[0] + ".ppsx")
            print("→", os.path.splitext(ra)[0] + ".ppsx")
    if a.ra_docx:
        dung_docx(kbj, sl, a.ra_docx)
        print("→", a.ra_docx)
    if not a.pptx and not a.ra_docx:
        sys.exit("Cần --pptx và/hoặc --ra-docx")


if __name__ == "__main__":
    main()
