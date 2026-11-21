#!/usr/bin/env python3
"""Dựng đầu ra từ kich_ban.json:
  1. ghi lời nói vào ghi chú diễn giả của bộ slide (tệp mới, không ghi đè bản gốc);
  2. bản in kịch bản Word (.docx): bảng thời gian, lời nói từng slide kèm ảnh thu nhỏ,
     hỏi đáp dự kiến, thẻ nhắc.

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
MAU_NHAN = "1F4E79"   # nhãn mốc trong bản in (xanh đậm, in đen trắng vẫn rõ)
MAU_PHU = "595959"


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


# ---------------------------------------------------------------- bản in Word
def dat_phong(run, co=None, dam=None, nghieng=None, mau=None, ten="Times New Roman"):
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor
    run.font.name = ten
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rf)
    for k in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(k), ten)
    if co:
        run.font.size = Pt(co)
    if dam is not None:
        run.bold = dam
    if nghieng is not None:
        run.italic = nghieng
    if mau:
        run.font.color.rgb = RGBColor.from_string(mau)
    return run


def doan(container, text="", co=13, dam=False, nghieng=False, can=None, sau=4, mau=None):
    from docx.shared import Pt
    p = container.add_paragraph()
    p.paragraph_format.space_after = Pt(sau)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    if can:
        p.alignment = can
    if text:
        dat_phong(p.add_run(text), co, dam, nghieng, mau)
    return p


def loi_co_nhan(p, text, tu_nhan, co=13):
    """Viết lời nói, in đậm từ nhấn, in nghiêng các nhãn [Dừng]/[Nhìn]/[Chậm]."""
    mau = [re.escape(t) for t in sorted(tu_nhan, key=len, reverse=True) if t]
    mau.append(r"\[(?:Dừng|Nhìn|Chậm|Hỏi)[^\]]*\]")
    rx = re.compile("(" + "|".join(mau) + ")", re.I)
    for phan in rx.split(text):
        if not phan:
            continue
        if phan.startswith("["):
            dat_phong(p.add_run(phan), co, False, True, MAU_PHU)
        elif any(phan.lower() == t.lower() for t in tu_nhan):
            dat_phong(p.add_run(phan), co, True)
        else:
            dat_phong(p.add_run(phan), co)


def so_trang(section):
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = dat_phong(p.add_run(), 11)
    for loai, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if loai:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), loai)
        else:
            e = OxmlElement("w:instrText")
            e.set(qn("xml:space"), "preserve")
            e.text = txt
        r._element.append(e)


def vien_bang(table, mau="BFBFBF"):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    tblPr = table._element.tblPr
    b = OxmlElement("w:tblBorders")
    for canh in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{canh}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), mau)
        b.append(e)
    tblPr.append(b)


def do_rong(table, cac_cot):
    """Đặt độ rộng cột cố định (Word và LibreOffice đều tôn trọng): tblLayout fixed + tblGrid + từng ô."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    table.autofit = False
    tblPr = table._element.tblPr
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    grid = table._element.tblGrid
    for gc, w in zip(grid.findall(qn("w:gridCol")), cac_cot):
        gc.set(qn("w:w"), str(int(w.twips)))
    for row in table.rows:
        for c, w in zip(row.cells, cac_cot):
            c.width = w


def khong_tach(row):
    """Giữ một hàng bảng trên cùng một trang khi đủ chỗ."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    trPr = row._tr.get_or_add_trPr()
    e = OxmlElement("w:cantSplit")
    e.set(qn("w:val"), "true")
    trPr.append(e)


def to_nen(cell, mau):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), mau)
    cell._tc.get_or_add_tcPr().append(shd)


def dung_docx(kbj, sl, duong_ra):
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.shared import Cm, Pt

    theo_so = {s["so"]: s for s in sl.get("slides", [])}
    toc_do = kbj.get("toc_do") or sl.get("toc_do") or kb.TOC_DO_MAC_DINH
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2)
    sec.top_margin = sec.bottom_margin = Cm(1.8)
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(13)
    so_trang(sec)

    doan(doc, "KỊCH BẢN THUYẾT TRÌNH", 16, True, can=WD_ALIGN_PARAGRAPH.CENTER, sau=2)
    doan(doc, kbj.get("tieu_de", ""), 14, True, can=WD_ALIGN_PARAGRAPH.CENTER, sau=8)
    tt = []
    for khoa, nhan in (("nguoi_trinh_bay", "Người trình bày"), ("su_kien", "Sự kiện"), ("thoi_gian_dia_diem", "Thời gian, địa điểm")):
        if kbj.get(khoa):
            tt.append(f"{nhan}: {kbj[khoa]}")
    # bảng thời gian
    dong, lk = [], 0.0
    for s in sorted(kbj["slides"], key=lambda x: x["so"]):
        nhap = theo_so.get(s["so"], {}).get("so_nhap", len(s.get("nhip", [])))
        g = kb.giay_noi(kb.loi_noi_slide(s), toc_do, nhap)
        dong.append((s, lk, g))
        lk += g
    muc_tieu = (kbj.get("thoi_luong_phut") or 0) * 60
    tt.append(f"Thời lượng: ≈ {kb.mm_ss(lk)}" + (f" (dành {kb.mm_ss(muc_tieu)})" if muc_tieu else "")
              + f" · {len(dong)} slide · tốc độ nói {toc_do} âm tiết/phút")
    for t in tt:
        doan(doc, t, 12, can=WD_ALIGN_PARAGRAPH.CENTER, sau=2, mau=MAU_PHU)
    doan(doc, "", sau=6)

    if kbj.get("chuan_bi"):
        doan(doc, "Chuẩn bị trước buổi trình bày", 13, True, sau=4)
        for m in kbj["chuan_bi"]:
            doan(doc, "☐ " + m, 12, sau=2)
        doan(doc, "", sau=4)

    doan(doc, "1. Phân bổ thời gian", 14, True, sau=4)
    bang = doc.add_table(rows=1, cols=4)
    bang.alignment = WD_TABLE_ALIGNMENT.CENTER
    vien_bang(bang)
    for c, t in zip(bang.rows[0].cells, ("Slide", "Nội dung", "Bắt đầu", "Thời lượng")):
        c.paragraphs[0].text = ""
        dat_phong(c.paragraphs[0].add_run(t), 12, True)
        to_nen(c, "D9E2F3")
    for s, bd, g in dong:
        r = bang.add_row().cells
        for c, t in zip(r, (str(s["so"]), s.get("tieu_de") or theo_so.get(s["so"], {}).get("tieu_de", ""), kb.mm_ss(bd), kb.mm_ss(g))):
            dat_phong(c.paragraphs[0].add_run(t), 12)
    do_rong(bang, (Cm(1.6), Cm(10.6), Cm(2.4), Cm(2.4)))
    for row in bang.rows:
        khong_tach(row)

    doan(doc, "", sau=2).add_run().add_break(WD_BREAK.PAGE)
    doan(doc, "2. Lời nói từng slide", 14, True, sau=6)
    for s, bd, g in dong:
        goc = theo_so.get(s["so"], {})
        tbl = doc.add_table(rows=1, cols=2)
        vien_bang(tbl, "D9D9D9")
        do_rong(tbl, (Cm(5.6), Cm(11.4)))
        khong_tach(tbl.rows[0])
        trai, phai = tbl.rows[0].cells
        p = trai.paragraphs[0]
        dat_phong(p.add_run(f"Slide {s['so']}"), 12, True, mau=MAU_NHAN)
        dat_phong(p.add_run(f"\n{kb.mm_ss(bd)} – {kb.mm_ss(bd + g)}"), 11, mau=MAU_PHU)
        anh = s.get("anh") or goc.get("anh")
        if anh and os.path.exists(anh):
            trai.add_paragraph().add_run().add_picture(anh, width=Cm(5.2))
        td = s.get("tieu_de") or goc.get("tieu_de", "")
        if td:
            doan(phai, td, 13, True, sau=4)
        nhan = [kb.nfc(t) for t in s.get("nhan", [])]
        muc = []
        if s.get("mo"):
            muc.append(("Mở", s["mo"]))
        for i, n in enumerate(s.get("nhip", []), 1):
            muc.append((f"Nhấp {i}" if goc.get("so_nhap", 1) else "Nói", n))
        if s.get("chuyen"):
            muc.append(("Chuyển", s["chuyen"]))
        for nhan_muc, text in muc:
            p = doan(phai, sau=4)
            dat_phong(p.add_run(f"[{nhan_muc}] "), 12, True, mau=MAU_NHAN)
            loi_co_nhan(p, kb.nfc(text), nhan)
        if s.get("luu_y"):
            doan(phai, "Lưu ý: " + s["luu_y"], 12, nghieng=True, mau=MAU_PHU, sau=2)
        doan(doc, "", sau=4)

    hd = kbj.get("hoi_dap", [])
    if hd:
        doan(doc, "", sau=2).add_run().add_break(WD_BREAK.PAGE)
        doan(doc, "3. Hỏi đáp dự kiến", 14, True, sau=6)
        for i, q in enumerate(hd, 1):
            doan(doc, f"Câu {i}. {q.get('hoi', '')}", 13, True, sau=2)
            doan(doc, q.get("tra_loi", ""), 13, sau=2)
            phu = []
            if q.get("slide_du_phong"):
                phu.append(f"slide hỗ trợ: {q['slide_du_phong']}")
            if q.get("nguon"):
                phu.append(f"nguồn: {q['nguon']}")
            if phu:
                doan(doc, "(" + "; ".join(phu) + ")", 11, nghieng=True, mau=MAU_PHU, sau=8)
            else:
                doan(doc, "", sau=4)

    # thẻ nhắc: một trang, mỗi ô một slide — in ra cầm tay hoặc đặt cạnh máy
    doan(doc, "", sau=2).add_run().add_break(WD_BREAK.PAGE)
    doan(doc, f"{4 if hd else 3}. Thẻ nhắc", 14, True, sau=6)
    cot = 2
    the = doc.add_table(rows=0, cols=cot)
    vien_bang(the, "7F7F7F")
    hang = None
    do_rong(the, (Cm(8.5), Cm(8.5)))
    for k, (s, bd, g) in enumerate(dong):
        if k % cot == 0:
            hang_moi = the.add_row()
            khong_tach(hang_moi)
            hang = hang_moi.cells
        c = hang[k % cot]
        p = c.paragraphs[0]
        dat_phong(p.add_run(f"{s['so']} · {kb.mm_ss(bd)}  "), 11, True, mau=MAU_NHAN)
        dat_phong(p.add_run(s.get("tieu_de") or theo_so.get(s["so"], {}).get("tieu_de", "")), 11, True)
        y = s.get("the_nhac") or s.get("nhan") or []
        if y:
            dat_phong(c.add_paragraph().add_run(" · ".join(y)), 11)
        if s.get("chuyen"):
            dat_phong(c.add_paragraph().add_run("→ " + s["chuyen"][:90]), 10, nghieng=True, mau=MAU_PHU)
    doc.save(duong_ra)


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
