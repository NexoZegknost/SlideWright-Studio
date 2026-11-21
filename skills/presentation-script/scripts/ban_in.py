"""Bản in kịch bản thuyết trình (.docx) — bố cục tài liệu chuyên nghiệp, A4.

Bìa có khối thông số; tiêu đề mục có đường kẻ; bảng phân bổ thời gian có hàng tiêu đề
màu, hàng xen màu, dòng tổng; mỗi slide một thẻ (thanh đầu, ảnh thu nhỏ, lời nói có nhãn
mốc treo lề); hỏi đáp có huy hiệu số; thẻ nhắc có đường cắt. Đầu trang ghi tên bài,
chân trang "Trang x / y". Phông Times New Roman, in đen trắng vẫn rõ thứ bậc.
"""
import os
import re

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

import kb_chung as kb

PHONG = "Times New Roman"
NAVY = "1F3864"
NHAN = "2E75B6"
NHAT = "EAF0F8"
XEN = "F5F7FB"
VACH = "BFC9D9"
XAM = "595959"
XAM_NHAT = "8C8C8C"
LUU_Y_NEN = "FFF6E0"
LUU_Y_CHU = "9C6500"
RONG = 17.0  # cm, bề rộng vùng chữ


# ---------------------------------------------------------------- chữ và đoạn
def R(p, text, co=12.5, dam=False, nghieng=False, mau=None, gian=None, hoa=False):
    run = p.add_run(text)
    run.font.name = PHONG
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for k in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(k), PHONG)
    run.font.size = Pt(co)
    run.bold = dam
    run.italic = nghieng
    if mau:
        run.font.color.rgb = RGBColor.from_string(mau)
    if hoa:
        run.font.all_caps = True
    if gian:
        sp = OxmlElement("w:spacing")
        sp.set(qn("w:val"), str(int(gian * 20)))
        rpr.append(sp)
    return run


def P(cont, truoc=0, sau=4, can=None, dong=1.15, giu_tiep=False):
    p = cont.add_paragraph()
    f = p.paragraph_format
    f.space_before, f.space_after, f.line_spacing = Pt(truoc), Pt(sau), dong
    if can is not None:
        p.alignment = can
    if giu_tiep:
        f.keep_with_next = True
    return p


def o_dau(cell):
    """Đoạn đầu tiên của ô (Word luôn tạo sẵn một đoạn trống)."""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    return p


def vien_doan(p, canh="bottom", mau=VACH, sz=6, cach=4):
    pPr = p._p.get_or_add_pPr()
    bdr = pPr.find(qn("w:pBdr"))
    if bdr is None:
        bdr = OxmlElement("w:pBdr")
        pPr.append(bdr)
    e = OxmlElement(f"w:{canh}")
    e.set(qn("w:val"), "single")
    e.set(qn("w:sz"), str(sz))
    e.set(qn("w:space"), str(cach))
    e.set(qn("w:color"), mau)
    bdr.append(e)


def nen_doan(p, mau):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), mau)
    p._p.get_or_add_pPr().append(shd)


def truong(p, ma, co=9, mau=XAM_NHAT):
    """Chèn trường PAGE / NUMPAGES."""
    for loai, txt in (("begin", None), (None, ma), ("separate", None), (None, "1"), ("end", None)):
        r = R(p, "", co, mau=mau)
        if loai:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), loai)
        elif txt == ma:
            e = OxmlElement("w:instrText")
            e.set(qn("xml:space"), "preserve")
            e.text = f" {ma} "
        else:
            e = OxmlElement("w:t")
            e.text = txt
        r._element.append(e)


# ---------------------------------------------------------------- bảng
def bang(cont, so_hang, cot_cm, vien="khung", mau_vien=VACH):
    t = cont.add_table(rows=so_hang, cols=len(cot_cm))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tblPr = t._element.tblPr
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    for gc, w in zip(t._element.tblGrid.findall(qn("w:gridCol")), cot_cm):
        gc.set(qn("w:w"), str(int(Cm(w).twips)))
    for row in t.rows:
        for c, w in zip(row.cells, cot_cm):
            c.width = Cm(w)
    b = OxmlElement("w:tblBorders")
    for canh in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{canh}")
        if vien == "khong" or (vien == "ngang" and canh in ("left", "right", "insideV")):
            e.set(qn("w:val"), "nil")
        else:
            e.set(qn("w:val"), "dashed" if vien == "cat" else "single")
            e.set(qn("w:sz"), "6" if vien == "cat" else "4")
            e.set(qn("w:color"), mau_vien)
        b.append(e)
    tblPr.append(b)
    le = OxmlElement("w:tblCellMar")
    for canh, v in (("top", 70), ("bottom", 70), ("left", 110), ("right", 110)):
        e = OxmlElement(f"w:{canh}")
        e.set(qn("w:w"), str(v))
        e.set(qn("w:type"), "dxa")
        le.append(e)
    tblPr.append(le)
    return t


def them_hang(t, cot_cm):
    row = t.add_row()
    for c, w in zip(row.cells, cot_cm):
        c.width = Cm(w)
    return row


def to(cell, mau):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), mau)
    cell._tc.get_or_add_tcPr().append(shd)


def vien_o(cell, **canh):
    tcPr = cell._tc.get_or_add_tcPr()
    b = OxmlElement("w:tcBorders")
    for k, (val, mau, sz) in canh.items():
        e = OxmlElement(f"w:{k}")
        e.set(qn("w:val"), val)
        if val != "nil":
            e.set(qn("w:sz"), str(sz))
            e.set(qn("w:color"), mau)
        b.append(e)
    tcPr.append(b)


def khong_tach(row, cao=None):
    trPr = row._tr.get_or_add_trPr()
    e = OxmlElement("w:cantSplit")
    e.set(qn("w:val"), "true")
    trPr.append(e)
    if cao:
        row.height = Cm(cao)
        row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST


def lap_tieu_de(row):
    trPr = row._tr.get_or_add_trPr()
    e = OxmlElement("w:tblHeader")
    e.set(qn("w:val"), "true")
    trPr.append(e)


# ---------------------------------------------------------------- thành phần
def tieu_de_muc(doc, so, ten, ngat_trang=True):
    if ngat_trang:
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        doc.paragraphs[-1].paragraph_format.space_after = Pt(0)
    p = P(doc, truoc=0, sau=10, giu_tiep=True)
    R(p, f"{so}  ", 15, True, mau=NHAN)
    R(p, ten, 15, True, mau=NAVY)
    vien_doan(p, mau=NAVY, sz=8, cach=4)


def loi_co_nhan(p, text, tu_nhan, co=12.5):
    """In đậm từ nhấn; chỉ dẫn diễn xuất ([Dừng], [Nhìn]…) in nghiêng màu nhạt."""
    mau = [re.escape(t) for t in sorted(tu_nhan, key=len, reverse=True) if t]
    mau.append(r"\[(?:Dừng|Nhìn|Chậm|Hỏi)[^\]]*\]")
    rx = re.compile("(" + "|".join(mau) + ")", re.I)
    for phan in rx.split(text):
        if not phan:
            continue
        if phan.startswith("["):
            R(p, phan, co - 1.5, nghieng=True, mau=XAM_NHAT)
        elif any(phan.lower() == t.lower() for t in tu_nhan):
            R(p, phan, co, True, mau=NAVY)
        else:
            R(p, phan, co)


def dong_moc(cell, nhan, text, tu_nhan, dau=False):
    """Đoạn lời nói có nhãn mốc treo lề trái (MỞ, NHẤP 1, CHUYỂN…)."""
    p = o_dau(cell) if dau else cell.add_paragraph()
    f = p.paragraph_format
    f.left_indent, f.first_line_indent = Cm(2.1), Cm(-2.1)
    f.space_after, f.line_spacing = Pt(5), 1.2
    f.tab_stops.add_tab_stop(Cm(2.1), WD_TAB_ALIGNMENT.LEFT)
    R(p, nhan, 8.5, True, mau=NHAN, gian=0.6, hoa=True)
    R(p, "\t", 8.5)
    loi_co_nhan(p, kb.nfc(text), tu_nhan)


def dau_chan_trang(sec, tieu):
    sec.different_first_page_header_footer = True
    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    hp.paragraph_format.tab_stops.add_tab_stop(Cm(RONG), WD_TAB_ALIGNMENT.RIGHT)
    R(hp, "KỊCH BẢN THUYẾT TRÌNH", 8.5, True, mau=NHAN, gian=1)
    R(hp, "\t" + (tieu[:90] if tieu else ""), 9, mau=XAM_NHAT)
    vien_doan(hp, mau=VACH, sz=4, cach=4)
    for ft in (sec.footer, sec.first_page_footer):
        fp = ft.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        R(fp, "Trang ", 9, mau=XAM_NHAT)
        truong(fp, "PAGE")
        R(fp, " / ", 9, mau=XAM_NHAT)
        truong(fp, "NUMPAGES")


# ---------------------------------------------------------------- dựng tài liệu
def dung_docx(kbj, sl, duong_ra):
    theo_so = {s["so"]: s for s in sl.get("slides", [])}
    toc_do = kbj.get("toc_do") or sl.get("toc_do") or kb.TOC_DO_MAC_DINH
    ctx = kb.doc_contexts().get(kbj.get("boi_canh", ""), {})

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name, st.font.size = PHONG, Pt(12.5)
    rpr = st.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for k in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(k), PHONG)
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2)
    sec.top_margin, sec.bottom_margin = Cm(2), Cm(1.8)
    sec.header_distance = sec.footer_distance = Cm(1)
    tieu = kbj.get("tieu_de", "")
    dau_chan_trang(sec, tieu)

    # thời gian từng slide
    dong, lk = [], 0.0
    for s in sorted(kbj["slides"], key=lambda x: x["so"]):
        goc = theo_so.get(s["so"], {})
        nhap = goc.get("so_nhap", len(s.get("nhip", [])))
        g = kb.giay_noi(kb.loi_noi_slide(s), toc_do, nhap)
        dong.append((s, goc, nhap, lk, g))
        lk += g
    tong = lk
    muc_tieu = (kbj.get("thoi_luong_phut") or 0) * 60
    hd = kbj.get("hoi_dap", [])
    ten_td = lambda s, goc: s.get("tieu_de") or goc.get("tieu_de", "")  # noqa: E731

    # ---- bìa
    p = P(doc, truoc=6, sau=6)
    R(p, "KỊCH BẢN THUYẾT TRÌNH", 10, True, mau=NHAN, gian=2.5)
    p = P(doc, sau=6, dong=1.05)
    R(p, tieu, 22, True, mau=NAVY)
    if kbj.get("su_kien"):
        p = P(doc, sau=2)
        R(p, kbj["su_kien"], 13, mau=XAM)
    vien_doan(doc.paragraphs[-1], mau=NAVY, sz=12, cach=10)
    P(doc, sau=6)

    so_lieu = [
        (kb.mm_ss(tong), "thời lượng ước tính" + (f" · dành {kb.mm_ss(muc_tieu)}" if muc_tieu else "")),
        (str(len(dong)), "slide"),
        (str(toc_do), "âm tiết / phút"),
        (str(len(hd)), "câu hỏi dự kiến"),
    ]
    cot = [RONG / 4] * 4
    t = bang(doc, 1, cot, vien="khong")
    for c, (so, nhan) in zip(t.rows[0].cells, so_lieu):
        to(c, NHAT)
        vien_o(c, left=("single", "FFFFFF", 24), right=("single", "FFFFFF", 24))
        p = o_dau(c)
        p.paragraph_format.space_before = Pt(4)
        R(p, so, 20, True, mau=NAVY)
        p = c.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        R(p, nhan, 9, mau=XAM, gian=0.3)
    P(doc, sau=8)

    thong_tin = [(k, kbj.get(v)) for k, v in (("Người trình bày", "nguoi_trinh_bay"), ("Sự kiện", "su_kien"),
                                             ("Thời gian, địa điểm", "thoi_gian_dia_diem"))]
    if ctx.get("ten"):
        thong_tin.append(("Bối cảnh", ctx["ten"]))
    thong_tin = [(k, v) for k, v in thong_tin if v]
    if thong_tin:
        t = bang(doc, 0, [4.2, RONG - 4.2], vien="ngang")
        for k, v in thong_tin:
            r = them_hang(t, [4.2, RONG - 4.2])
            R(o_dau(r.cells[0]), k, 10.5, mau=XAM)
            R(o_dau(r.cells[1]), v, 12)
        P(doc, sau=8)

    if kbj.get("chuan_bi"):
        p = P(doc, truoc=4, sau=4, giu_tiep=True)
        R(p, "Chuẩn bị trước buổi trình bày", 12, True, mau=NAVY)
        for m in kbj["chuan_bi"]:
            p = P(doc, sau=3)
            p.paragraph_format.left_indent = Cm(0.8)
            p.paragraph_format.first_line_indent = Cm(-0.6)
            R(p, "☐  ", 12, mau=NHAN)
            R(p, m, 12)

    # ---- 1. phân bổ thời gian
    p = P(doc, truoc=14, sau=10, giu_tiep=True)
    R(p, "1  ", 15, True, mau=NHAN)
    R(p, "Phân bổ thời gian", 15, True, mau=NAVY)
    vien_doan(p, mau=NAVY, sz=8, cach=4)
    cot = [1.5, RONG - 1.5 - 2.2 * 3, 2.2, 2.2, 2.2]
    t = bang(doc, 1, cot, vien="ngang")
    lap_tieu_de(t.rows[0])
    for c, (txt, can) in zip(t.rows[0].cells, (("Slide", 1), ("Nội dung", 0), ("Bắt đầu", 1), ("Kết thúc", 1), ("Thời lượng", 1))):
        to(c, NAVY)
        p = o_dau(c)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if can else None
        R(p, txt, 10.5, True, mau="FFFFFF")
    for k, (s, goc, nhap, bd, g) in enumerate(dong):
        r = them_hang(t, cot)
        khong_tach(r)
        for j, (c, txt) in enumerate(zip(r.cells, (f"{s['so']:02d}", ten_td(s, goc), kb.mm_ss(bd), kb.mm_ss(bd + g), kb.mm_ss(g)))):
            if k % 2:
                to(c, XEN)
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = o_dau(c)
            if j != 1:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            R(p, txt, 11, j == 0, mau=NAVY if j == 0 else None)
    r = them_hang(t, cot)
    for c in r.cells:
        vien_o(c, top=("single", NAVY, 8))
    R(o_dau(r.cells[1]), "Tổng", 11, True)
    p = o_dau(r.cells[4])
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    R(p, kb.mm_ss(tong), 11, True, mau=NAVY)
    if muc_tieu:
        p = P(doc, truoc=4, sau=0)
        lech = (tong - muc_tieu) / muc_tieu
        R(p, f"Thời gian dành cho bài: {kb.mm_ss(muc_tieu)} · chênh lệch {lech:+.0%}. "
             f"Ước theo tốc độ {toc_do} âm tiết/phút, mỗi [Dừng] 2 giây.", 9.5, nghieng=True, mau=XAM)

    # ---- 2. lời nói từng slide
    tieu_de_muc(doc, "2", "Lời nói từng slide")
    cot = [5.2, RONG - 5.2]
    for s, goc, nhap, bd, g in dong:
        t = bang(doc, 2, cot, vien="khung")
        h0, h1 = t.rows[0].cells
        to(h0, NAVY)
        to(h1, NHAT)
        khong_tach(t.rows[0])
        khong_tach(t.rows[1])
        p = o_dau(h0)
        p.paragraph_format.keep_with_next = True
        R(p, "SLIDE ", 9, True, mau="D9E2F3", gian=1)
        R(p, f"{s['so']:02d}", 16, True, mau="FFFFFF")
        p = h0.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        R(p, f"{kb.mm_ss(bd)} – {kb.mm_ss(bd + g)}", 10, mau="D9E2F3")
        h1.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = o_dau(h1)
        p.paragraph_format.keep_with_next = True
        R(p, ten_td(s, goc), 13, True, mau=NAVY)
        p = h1.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        phu = f"≈ {round(g)} giây"
        phu += f" · {nhap} cú nhấp" if nhap else " · không có hiệu ứng"
        if s.get("nhan"):
            phu += " · nhấn: " + ", ".join(s["nhan"])
        R(p, phu, 9.5, mau=XAM)

        b0, b1 = t.rows[1].cells
        anh = s.get("anh") or goc.get("anh")
        p = o_dau(b0)
        if anh and os.path.exists(anh):
            p.add_run().add_picture(anh, width=Cm(4.8))
        else:
            R(p, "(không có ảnh slide)", 9, nghieng=True, mau=XAM_NHAT)
        nhan = [kb.nfc(x) for x in s.get("nhan", [])]
        muc = []
        if s.get("mo"):
            muc.append(("Mở", s["mo"]))
        for i, n in enumerate(s.get("nhip", []), 1):
            muc.append((f"Nhấp {i}" if nhap else "Nói", n))
        if s.get("chuyen"):
            muc.append(("Chuyển", s["chuyen"]))
        for k, (nm, text) in enumerate(muc):
            dong_moc(b1, nm, text, nhan, dau=(k == 0))
        if s.get("luu_y"):
            p = b1.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            nen_doan(p, LUU_Y_NEN)
            R(p, "LƯU Ý  ", 8.5, True, mau=LUU_Y_CHU, gian=0.6)
            R(p, s["luu_y"], 11, nghieng=True, mau=LUU_Y_CHU)
        P(doc, sau=8)

    # ---- 3. hỏi đáp
    so_muc = 3
    if hd:
        tieu_de_muc(doc, str(so_muc), "Hỏi đáp dự kiến")
        so_muc += 1
        cot = [1.3, RONG - 1.3]
        t = bang(doc, 0, cot, vien="ngang")
        for i, q in enumerate(hd, 1):
            r = them_hang(t, cot)
            khong_tach(r)
            c0, c1 = r.cells
            to(c0, NAVY)
            c0.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            p = o_dau(c0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(3)
            R(p, str(i), 13, True, mau="FFFFFF")
            p = o_dau(c1)
            p.paragraph_format.space_before = Pt(3)
            R(p, q.get("hoi", ""), 12.5, True, mau=NAVY)
            p = c1.add_paragraph()
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.2
            R(p, "Trả lời  ", 8.5, True, mau=NHAN, gian=0.6, hoa=True)
            R(p, q.get("tra_loi", ""), 12.5)
            phu = []
            if q.get("nguon"):
                phu.append(f"Nguồn: {q['nguon']}")
            if q.get("slide_du_phong"):
                phu.append(f"Slide hỗ trợ: {q['slide_du_phong']}")
            if phu:
                p = c1.add_paragraph()
                p.paragraph_format.space_after = Pt(4)
                R(p, " · ".join(phu), 9.5, nghieng=True, mau=XAM)

    # ---- 4. thẻ nhắc
    tieu_de_muc(doc, str(so_muc), "Thẻ nhắc")
    p = P(doc, sau=8)
    R(p, "Cắt theo đường đứt nét, xếp theo số slide; mỗi thẻ ghi mốc giờ bắt đầu, từ khoá cần nói và câu chuyển.",
      10, nghieng=True, mau=XAM)
    cot = [RONG / 2, RONG / 2]
    t = bang(doc, 0, cot, vien="cat", mau_vien=XAM_NHAT)
    hang = None
    for k, (s, goc, nhap, bd, g) in enumerate(dong):
        if k % 2 == 0:
            hang = them_hang(t, cot)
            khong_tach(hang, cao=5.2)
        c = hang.cells[k % 2]
        p = o_dau(c)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(RONG / 2 - 0.5), WD_TAB_ALIGNMENT.RIGHT)
        R(p, f"{s['so']:02d}", 22, True, mau=NHAN)
        R(p, f"\t{kb.mm_ss(bd)}", 11, True, mau=XAM)
        p = c.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        R(p, ten_td(s, goc), 12.5, True, mau=NAVY)
        for y in (s.get("the_nhac") or s.get("nhan") or []):
            p = c.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5)
            p.paragraph_format.first_line_indent = Cm(-0.4)
            p.paragraph_format.space_after = Pt(1)
            R(p, "▪ ", 10, mau=NHAN)
            R(p, y, 12)
        if s.get("chuyen"):
            p = c.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            R(p, "→ " + s["chuyen"], 10, nghieng=True, mau=XAM)
    doc.save(duong_ra)
