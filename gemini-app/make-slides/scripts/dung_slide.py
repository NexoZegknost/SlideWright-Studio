#!/usr/bin/env python3
"""dung_slide.py — dựng bộ slide PowerPoint (.pptx + .ppsx) từ tệp đặc tả JSON, chỉ cần python-pptx.

Bản dành cho Gemini app của SlideWright - Studio: không cần Node.js, không nhúng phông
(dùng phông có sẵn trong Office), có chuyển trang Morph với cảnh xuyên suốt, hiệu ứng xuất hiện
theo mạch nói, ghi chú diễn giả và mã ngôn ngữ vi-VN.

Dùng:  python3 dung_slide.py dac_ta.json [--ra thu_muc]
Mẫu đặc tả: ../assets/mau-dac-ta.json. Các loại slide (trường "loai"):
  bia, chia-phan, y-chinh, hai-cot, the, so-lieu, trich-dan, dong-thoi-gian, bang, anh, cau-hoi, ket
In CẢNH BÁO khi chữ có thể tràn khung, cỡ chữ dưới mức của bối cảnh, quá nhiều chữ hoặc quá 5 cú nhấp.
Mã thoát 1 khi đặc tả sai (thiếu trường bắt buộc, loại slide lạ).
"""
import argparse
import json
import math
import os
import re
import sys
import zipfile

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

# Toạ độ viết theo lưới 13,333 × 7,5; khi đặt vào slide nhân K để ra khổ 10 × 5,625 inch
# (khổ LAYOUT_16x9 mà thông số cỡ chữ của contexts.json và các script kiểm tra dùng).
W, H = 13.333, 7.5
K = 0.75
M = 0.75                    # lề (đơn vị lưới)


def I(v):
    return Inches(v * K)
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"

# Phông có sẵn trong Microsoft Office (Windows và macOS), đủ dấu tiếng Việt
PHONG_OFFICE = {"serif": "Cambria", "sans": "Calibri", "mono": "Consolas"}

CANH_BAO = []


def canh_bao(so, noi_dung):
    CANH_BAO.append(f"[slide {so}] {noi_dung}" if so else noi_dung)


# ------------------------------------------------------------------ tiện ích chữ
def rgb(h):
    return RGBColor.from_string(h.lstrip("#").upper())


def dat_alpha(shape, phan_tram):
    """Độ đục của nền hình (0–100)."""
    clr = shape.fill._xPr.find(qn("a:solidFill")).find(qn("a:srgbClr"))
    a = etree.SubElement(clr, qn("a:alpha"))
    a.set("val", str(int(phan_tram * 1000)))


def bo_vien(shape):
    shape.line.fill.background()


def uoc_luong_dong(doan, rong_in, co_pt):
    """Số dòng ước lượng cho một đoạn (bề rộng ký tự trung bình ≈ 0,5 em)."""
    doan = doan.replace("**", "")
    ky_tu_moi_dong = max(1, int(rong_in * 72 / (co_pt * 0.5)))
    return max(1, math.ceil(len(doan) / ky_tu_moi_dong))


def kiem_tran(so, ten, doan_list, rong_in, cao_in, co_pt, gian=1.15):
    rong_in, cao_in = rong_in * K, cao_in * K
    dong = sum(uoc_luong_dong(d, rong_in - 0.2, co_pt) for d in doan_list)
    can = dong * co_pt * gian / 72 + 0.15
    if can > cao_in + 0.05:
        canh_bao(so, f"{ten}: chữ có thể tràn khung (cần ~{can:.1f}\", khung {cao_in:.1f}\") — rút gọn nội dung")


class Bo:
    """Bộ dựng một bài: giữ phong cách, cỡ chữ, bộ đếm slide."""

    def __init__(self, dt):
        self.dt = dt
        pc = dt["phong_cach"]
        self.c = {k: v.lstrip("#") for k, v in pc["mau"].items()}
        self.head = pc.get("phong_tieu_de") or PHONG_OFFICE["serif"]
        self.body = pc.get("phong_noi_dung") or PHONG_OFFICE["sans"]
        cc = dt.get("co_chu", {})
        self.body_min = int(cc.get("body_min", 24))
        self.title_min = int(cc.get("title_min", 36))
        self.max_tu = int(cc.get("max_words", 30))
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = I(W), I(H)
        self.blank = self.prs.slide_layouts[6]
        self.n = len(dt["slides"])
        self.morph = dt.get("morph", True)

    # ---------------------------------------------------------- hộp chữ
    def hop_chu(self, sl, x, y, w, h, doan, co, mau, phong=None, dam=False, nghieng=False,
                can=PP_ALIGN.LEFT, doc=MSO_ANCHOR.TOP, ten=None, gian=1.1, cach_sau=6):
        tb = sl.shapes.add_textbox(I(x), I(y), I(w), I(h))
        if ten:
            tb.name = ten
        tf = tb.text_frame
        tf.word_wrap = True
        tf.auto_size = None
        tf.vertical_anchor = doc
        for m in ("margin_left", "margin_right"):
            setattr(tf, m, I(0.05))
        if isinstance(doan, str):
            doan = [doan]
        for i, d in enumerate(doan):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = can
            p.line_spacing = gian
            p.space_after = Pt(cach_sau)
            # **cụm** → in đậm, màu nhấn đúng tương phản với nền
            mau_nhan = self.c["accentOnDark"] if mau.upper() in ("FFFFFF", self.c["accentOnDark"].upper()) \
                else self.c["accentText"]
            for k, doan_nho in enumerate(re.split(r"\*\*", d)):
                if not doan_nho:
                    continue
                nhan = k % 2 == 1
                r = p.add_run()
                r.text = doan_nho
                f = r.font
                f.size = Pt(co)
                f.bold = dam or nhan
                f.italic = nghieng
                f.name = phong or self.body
                f.color.rgb = rgb(mau_nhan if nhan and mau_nhan.upper() != mau.upper() else mau)
                r._r.get_or_add_rPr().set("lang", "vi-VN")
            p._p.get_or_add_pPr()
            end = p._p.find(qn("a:endParaRPr"))
            if end is None:
                end = etree.SubElement(p._p, qn("a:endParaRPr"))
            end.set("lang", "vi-VN")
        return tb

    def hinh(self, sl, kieu, x, y, w, h, mau, ten=None, alpha=None):
        s = sl.shapes.add_shape(kieu, I(x), I(y), I(w), I(h))
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(mau)
        bo_vien(s)
        if alpha is not None:
            dat_alpha(s, alpha)
        if ten:
            s.name = ten
        s.shadow.inherit = False
        st = s._element.find(qn("p:style"))  # bỏ kiểu mặc định của theme (viền, đổ bóng)
        if st is not None:
            s._element.remove(st)
        return s

    def nen(self, sl, toi):
        sl.background.fill.solid()
        sl.background.fill.fore_color.rgb = rgb(self.c["dark"] if toi else self.c["light"])

    # ---------------------------------------------------------- cảnh morph xuyên suốt
    def canh(self, sl, i, vai):
        """Ba đối tượng !!… có mặt trên mọi slide ở tư thế khác nhau → Morph tạo chuyển động liền mạch."""
        c = self.c
        if vai in ("bia", "ket"):
            vx, vy, vd, va = 7.9, -1.6, 7.6, 18
        elif vai in ("chia-phan", "cau-hoi"):
            vx, vy, vd, va = -2.2, 1.2, 6.4, 16
        else:
            lech = (i % 3) * 0.35
            vx, vy, vd, va = 11.45 - lech, -0.95 + lech / 2, 2.6, 22
        toi = vai in ("bia", "ket", "chia-phan", "cau-hoi")
        self.hinh(sl, MSO_SHAPE.OVAL, vx, vy, vd, vd, c["accent2"] if not toi else c["accent"], "!!vong", va)
        # chấm nhấn: nhỏ, đổi chỗ theo slide
        cx = W - 1.0 - ((i * 1.7) % 4.0) if not toi else W - 1.0
        self.hinh(sl, MSO_SHAPE.OVAL, cx, H - 0.62, 0.16, 0.16, c["accent"] if not toi else c["accentOnDark"], "!!cham")
        # thanh tiến độ: dài dần theo bài
        rong = max(0.05, W * (i + 1) / self.n)
        self.hinh(sl, MSO_SHAPE.RECTANGLE, 0, H - 0.1, rong, 0.1, c["accent"], "!!tien-do")

    # ---------------------------------------------------------- tiêu đề slide nội dung
    def tieu_de(self, sl, so, s, rong=W - 2 * M - 2.2):
        co = max(self.title_min, int(s.get("co_tieu_de", self.title_min)))
        kiem_tran(so, "tiêu đề", [s["tieu_de"]], rong, 1.75, co)
        return self.hop_chu(sl, M, 0.3, rong, 1.75, s["tieu_de"], co, self.c["text"], self.head,
                            dam=True, doc=MSO_ANCHOR.BOTTOM, gian=1.0, ten="tieu-de")

    # ---------------------------------------------------------- các loại slide
    def bia(self, sl, so, s):
        c = self.c
        buoc = []
        if s.get("nhan"):
            self.hop_chu(sl, M, 1.55, 8.5, 0.5, s["nhan"], 16, c["accentOnDark"], self.body, dam=True)
        co = max(self.title_min + 8, 48)
        kiem_tran(so, "tiêu đề bìa", [s["tieu_de"]], 8.6, 2.6, co)
        self.hop_chu(sl, M, 2.05, 8.6, 2.6, s["tieu_de"], co, "FFFFFF", self.head, dam=True,
                     doc=MSO_ANCHOR.BOTTOM, gian=1.0, ten="tieu-de")
        if s.get("phu_de"):
            kiem_tran(so, "phụ đề", [s["phu_de"]], 8.6, 1.3, max(self.body_min, 22))
            t = self.hop_chu(sl, M, 4.8, 8.6, 1.3, s["phu_de"], max(self.body_min, 22), c["accentOnDark"], self.body)
            buoc.append((t.shape_id, None))
        if s.get("thong_tin"):
            self.hop_chu(sl, M, 6.25, 8.6, 0.6, s["thong_tin"], 16, c["accentOnDark"], self.body)
        return buoc

    def chia_phan(self, sl, so, s):
        c = self.c
        if s.get("so"):
            self.hop_chu(sl, M + 3.6, 0.9, 3.5, 1.6, str(s["so"]), 80, c["accentOnDark"], self.head, dam=True)
        co = max(self.title_min + 4, 44)
        kiem_tran(so, "tiêu đề phần", [s["tieu_de"]], 8.2, 2.3, co)
        self.hop_chu(sl, M + 3.6, 2.75, 8.2, 2.3, s["tieu_de"], co, "FFFFFF", self.head, dam=True, gian=1.0,
                     ten="tieu-de")
        buoc = []
        if s.get("mo_ta"):
            t = self.hop_chu(sl, M + 3.6, 5.05, 8.2, 1.4, s["mo_ta"], self.body_min, c["accentOnDark"], self.body)
            buoc.append((t.shape_id, None))
        return buoc

    def y_chinh(self, sl, so, s):
        c = self.c
        self.tieu_de(sl, so, s)
        y = s.get("y", [])
        co = max(self.body_min, int(s.get("co_chu", self.body_min)))
        co_nhan = bool(s.get("diem_nhan"))
        rong = 7.4 if co_nhan else W - 2 * M - 1.0
        kiem_tran(so, "nội dung", y, rong, 4.6, co)
        tb = self.hop_chu(sl, M, 2.2, rong, 4.6, y, co, c["text"], self.body, cach_sau=14)
        for p in tb.text_frame.paragraphs:
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", str(I(0.32)))
            pPr.set("indent", str(-I(0.32)))
            bu = etree.SubElement(pPr, qn("a:buClr"))
            etree.SubElement(bu, qn("a:srgbClr")).set("val", c["accent"])
            etree.SubElement(pPr, qn("a:buChar")).set("char", "–")
        buoc = [(tb.shape_id, i) for i in range(len(y))]
        if co_nhan:
            dn = s["diem_nhan"]
            self.hinh(sl, MSO_SHAPE.RECTANGLE, 8.75, 2.2, 3.85, 4.4, c["soft"])
            t1 = self.hop_chu(sl, 9.0, 2.45, 3.4, 1.6, dn.get("so", ""), 60, c["accentText"], self.head, dam=True,
                              doc=MSO_ANCHOR.BOTTOM, gian=1.0)
            t2 = self.hop_chu(sl, 9.0, 4.15, 3.4, 2.2, dn.get("chu", ""), max(18, self.body_min - 4), c["text"], self.body)
            kiem_tran(so, "điểm nhấn", [dn.get("chu", "")], 3.4, 2.2, max(18, self.body_min - 4))
            buoc.append((t1.shape_id, None))
        return buoc

    def hai_cot(self, sl, so, s):
        c = self.c
        self.tieu_de(sl, so, s)
        buoc = []
        rong = (W - 2 * M - 0.6) / 2
        for k, cot in enumerate(s.get("cot", [])[:2]):
            x = M + k * (rong + 0.6)
            self.hinh(sl, MSO_SHAPE.RECTANGLE, x, 2.25, 0.08, 4.3, c["accent"] if k == 0 else c["accent2"])
            self.hop_chu(sl, x + 0.3, 2.2, rong - 0.3, 0.7, cot.get("tieu_de", ""), max(self.body_min, 24),
                         c["accentText"], self.head, dam=True)
            nd = cot.get("y", [])
            kiem_tran(so, f"cột {k + 1}", nd, rong - 0.3, 3.6, self.body_min)
            t = self.hop_chu(sl, x + 0.3, 2.95, rong - 0.3, 3.6, nd, self.body_min, c["text"], self.body, cach_sau=10)
            buoc.append((t.shape_id, None))
        return buoc

    def the(self, sl, so, s):
        c = self.c
        self.tieu_de(sl, so, s)
        ds = s.get("the", [])[:4]
        if not ds:
            return []
        # độ rộng không đều: thẻ đầu (ý chính) rộng hơn để tránh hàng thẻ bằng nhau
        tong = W - 2 * M - 0.35 * (len(ds) - 1)
        he = [1.35] + [1.0] * (len(ds) - 1) if len(ds) > 1 else [1.0]
        rongs = [tong * h / sum(he) for h in he]
        x, buoc = M, []
        for k, (t, r) in enumerate(zip(ds, rongs)):
            nen = c["dark"] if k == 0 else c["soft"]
            chu = "FFFFFF" if k == 0 else c["text"]
            nhan = c["accentOnDark"] if k == 0 else c["accentText"]
            self.hinh(sl, MSO_SHAPE.RECTANGLE, x, 2.25, r, 4.35, nen)
            self.hop_chu(sl, x + 0.25, 2.45, r - 0.5, 1.1, t.get("tieu_de", ""), max(22, self.body_min - 2), nhan,
                         self.head, dam=True, doc=MSO_ANCHOR.BOTTOM, gian=1.0)
            co = max(18, self.body_min - 4)
            kiem_tran(so, f"thẻ {k + 1}", [t.get("noi_dung", "")], r - 0.5, 2.7, co)
            tb = self.hop_chu(sl, x + 0.25, 3.65, r - 0.5, 2.75, t.get("noi_dung", ""), co, chu, self.body)
            buoc.append((tb.shape_id, None))
            x += r + 0.35
        return buoc

    def so_lieu(self, sl, so, s):
        c = self.c
        self.tieu_de(sl, so, s)
        ds = s.get("so_lieu", [])[:3]
        rong = (W - 2 * M - 0.5 * (len(ds) - 1)) / max(1, len(ds))
        buoc = []
        for k, d in enumerate(ds):
            x = M + k * (rong + 0.5)
            t = self.hop_chu(sl, x, 2.3, rong, 2.0, d.get("so", ""), 72 if len(ds) < 3 else 60,
                             c["accentText"] if k else c["text"], self.head, dam=True, doc=MSO_ANCHOR.BOTTOM, gian=1.0)
            self.hinh(sl, MSO_SHAPE.RECTANGLE, x, 4.45, min(2.2, rong), 0.05, c["accent"])
            kiem_tran(so, f"số liệu {k + 1}", [d.get("chu", "")], rong, 1.7, max(18, self.body_min - 4))
            self.hop_chu(sl, x, 4.6, rong, 1.7, d.get("chu", ""), max(18, self.body_min - 4), c["muted"], self.body)
            buoc.append((t.shape_id, None))
        if s.get("nguon"):
            self.hop_chu(sl, M, 6.55, W - 2 * M - 2, 0.45, "Nguồn: " + s["nguon"], 12, c["muted"], self.body)
        return buoc

    def trich_dan(self, sl, so, s):
        c = self.c
        self.hinh(sl, MSO_SHAPE.RECTANGLE, M, 1.6, 0.1, 3.6, c["accent"])
        co = max(self.body_min + 6, 32)
        kiem_tran(so, "trích dẫn", [s["trich"]], W - 2 * M - 2.2, 3.6, co)
        self.hop_chu(sl, M + 0.45, 1.5, W - 2 * M - 2.2, 3.8, s["trich"], co, c["text"], self.head,
                     nghieng=True, doc=MSO_ANCHOR.MIDDLE, gian=1.15, ten="tieu-de")
        buoc = []
        if s.get("nguon"):
            t = self.hop_chu(sl, M + 0.45, 5.45, 9, 0.7, s["nguon"], max(18, self.body_min - 4), c["accentText"],
                             self.body, dam=True)
            buoc.append((t.shape_id, None))
        return buoc

    def dong_thoi_gian(self, sl, so, s):
        c = self.c
        self.tieu_de(sl, so, s)
        ds = s.get("moc", [])[:5]
        y0 = 3.35
        self.hinh(sl, MSO_SHAPE.RECTANGLE, M, y0, W - 2 * M, 0.05, c["muted"], alpha=50)
        rong = (W - 2 * M) / max(1, len(ds))
        buoc = []
        for k, d in enumerate(ds):
            x = M + k * rong
            self.hinh(sl, MSO_SHAPE.OVAL, x, y0 - 0.14, 0.33, 0.33, c["accent"])
            t = self.hop_chu(sl, x, 2.35, rong - 0.2, 0.85, d.get("moc", ""), max(22, self.body_min - 2),
                             c["accentText"], self.head, dam=True, doc=MSO_ANCHOR.BOTTOM)
            co = max(18, self.body_min - 4)
            kiem_tran(so, f"mốc {k + 1}", [d.get("noi_dung", "")], rong - 0.2, 2.9, co)
            t2 = self.hop_chu(sl, x, 3.75, rong - 0.25, 2.9, d.get("noi_dung", ""), co, c["text"], self.body)
            buoc.append((t2.shape_id, None))
        return buoc

    def bang(self, sl, so, s):
        c = self.c
        self.tieu_de(sl, so, s)
        hang = s.get("hang", [])
        if not hang:
            return []
        so_cot = max(len(h) for h in hang)
        cao = min(4.5, 0.62 * len(hang))
        tb = sl.shapes.add_table(len(hang), so_cot, I(M), I(2.25), I(W - 2 * M), I(cao)).table
        co = max(18, self.body_min - 4)
        for i, h in enumerate(hang):
            for j in range(so_cot):
                o = tb.cell(i, j)
                o.text = str(h[j]) if j < len(h) else ""
                o.fill.solid()
                o.fill.fore_color.rgb = rgb(c["dark"] if i == 0 else (c["soft"] if i % 2 else c["light"]))
                for p in o.text_frame.paragraphs:
                    for r in p.runs:
                        r.font.size = Pt(co)
                        r.font.bold = i == 0
                        r.font.name = self.body
                        r.font.color.rgb = rgb("FFFFFF" if i == 0 else c["text"])
                        r._r.get_or_add_rPr().set("lang", "vi-VN")
        if len(hang) > 7:
            canh_bao(so, f"bảng {len(hang)} hàng — nên ≤ 7 hàng hoặc tách slide")
        return []

    def anh(self, sl, so, s):
        c = self.c
        p = s.get("anh", "")
        if p and os.path.exists(p):
            pic = sl.shapes.add_picture(p, I(0), I(0), height=I(H))
            if pic.width > I(W * 0.5):  # cắt cho vừa nửa trái
                ti_le = I(W * 0.5) / pic.width
                pic.crop_right = 1 - ti_le
                pic.width = I(W * 0.5)
            pic.name = "anh"
            if s.get("mo_ta_anh"):
                pic._element.nvPicPr.cNvPr.set("descr", s["mo_ta_anh"])
        else:
            canh_bao(so, f"không thấy ảnh '{p}' — để khối màu thay thế, cần bổ sung ảnh")
            self.hinh(sl, MSO_SHAPE.RECTANGLE, 0, 0, W * 0.5, H, c["soft"])
        x = W * 0.5 + 0.6
        rong = W * 0.5 - 1.3
        co = max(self.title_min - 4, 32)
        kiem_tran(so, "tiêu đề", [s["tieu_de"]], rong, 1.9, co)
        self.hop_chu(sl, x, 0.8, rong, 1.9, s["tieu_de"], co, c["text"], self.head, dam=True, doc=MSO_ANCHOR.BOTTOM,
                     gian=1.0, ten="tieu-de")
        nd = s.get("y", [])
        kiem_tran(so, "nội dung", nd, rong, 3.6, self.body_min)
        t = self.hop_chu(sl, x, 2.95, rong, 3.6, nd, self.body_min, c["text"], self.body, cach_sau=10)
        return [(t.shape_id, i) for i in range(len(nd))]

    def cau_hoi(self, sl, so, s):
        c = self.c
        co = max(self.title_min + 6, 44)
        kiem_tran(so, "câu hỏi", [s["cau_hoi"]], 9.6, 3.4, co)
        self.hop_chu(sl, M + 2.2, 1.6, 9.6, 3.4, s["cau_hoi"], co, "FFFFFF", self.head, dam=True,
                     doc=MSO_ANCHOR.MIDDLE, gian=1.05, ten="tieu-de")
        buoc = []
        if s.get("goi_y"):
            t = self.hop_chu(sl, M + 2.2, 5.15, 9.6, 1.2, s["goi_y"], max(20, self.body_min - 2), c["accentOnDark"], self.body)
            buoc.append((t.shape_id, None))
        return buoc

    def ket(self, sl, so, s):
        c = self.c
        co = max(self.title_min + 6, 44)
        kiem_tran(so, "lời kết", [s["tieu_de"]], 8.6, 2.4, co)
        self.hop_chu(sl, M, 1.9, 8.6, 2.4, s["tieu_de"], co, "FFFFFF", self.head, dam=True,
                     doc=MSO_ANCHOR.BOTTOM, gian=1.0, ten="tieu-de")
        buoc = []
        if s.get("y"):
            t = self.hop_chu(sl, M, 4.55, 8.6, 1.8, s["y"], max(20, self.body_min - 2), c["accentOnDark"], self.body)
            buoc.append((t.shape_id, None))
        return buoc

    LOAI = {
        "bia": ("bia", True), "chia-phan": ("chia_phan", True), "y-chinh": ("y_chinh", False),
        "hai-cot": ("hai_cot", False), "the": ("the", False), "so-lieu": ("so_lieu", False),
        "trich-dan": ("trich_dan", False), "dong-thoi-gian": ("dong_thoi_gian", False),
        "bang": ("bang", False), "anh": ("anh", False), "cau-hoi": ("cau_hoi", True), "ket": ("ket", True),
    }

    def dung(self):
        for i, s in enumerate(self.dt["slides"]):
            so = i + 1
            loai = s.get("loai")
            if loai not in self.LOAI:
                sys.exit(f"LỖI: slide {so}: loại '{loai}' không có. Dùng: {', '.join(self.LOAI)}")
            ham, toi = self.LOAI[loai]
            sl = self.prs.slides.add_slide(self.blank)
            self.nen(sl, toi)
            if self.morph:
                self.canh(sl, i, loai)
            buoc = getattr(self, ham)(sl, so, s)
            if s.get("ghi_chu"):
                sl.notes_slide.notes_text_frame.text = s["ghi_chu"]
            else:
                canh_bao(so, "thiếu ghi chú diễn giả")
            if len(buoc) > 5:
                canh_bao(so, f"{len(buoc)} cú nhấp — nên ≤ 5; gộp ý hoặc tách slide")
            if s.get("hieu_ung", True) and buoc:
                gan_hieu_ung(sl, buoc)
            if so > 1:
                gan_chuyen_trang(sl, "morph" if self.morph else "fade")
            dem_chu(so, s, self.max_tu, loai)
        return self.prs


def dem_chu(so, s, max_tu, loai):
    if loai in ("bia", "chia-phan", "cau-hoi", "ket", "bang"):
        return
    chu = []
    for k in ("tieu_de", "trich", "nguon"):
        if s.get(k):
            chu.append(s[k])
    chu += s.get("y", [])
    for cot in s.get("cot", []):
        chu += [cot.get("tieu_de", "")] + cot.get("y", [])
    for t in s.get("the", []):
        chu += [t.get("tieu_de", ""), t.get("noi_dung", "")]
    for d in s.get("so_lieu", []):
        chu += [d.get("so", ""), d.get("chu", "")]
    for d in s.get("moc", []):
        chu += [d.get("moc", ""), d.get("noi_dung", "")]
    n = len(" ".join(chu).split())
    if n > max_tu + 10:
        canh_bao(so, f"{n} chữ — bối cảnh cho phép khoảng {max_tu}; rút gọn")


# ------------------------------------------------------------------ hiệu ứng và chuyển trang (XML)
def gan_hieu_ung(sl, buoc):
    """Mỗi bước là một cú nhấp: mờ dần xuất hiện (fade). buoc: [(spid, chỉ_số_đoạn | None)]."""
    nid = [2]

    def ctn():
        nid[0] += 1
        return nid[0]

    cac_nhap = []
    for spid, doan in buoc:
        tgt = f'<p:spTgt spid="{spid}"/>' if doan is None else \
            f'<p:spTgt spid="{spid}"><p:txEl><p:pRg st="{doan}" end="{doan}"/></p:txEl></p:spTgt>'
        a, b, e, s1, f1 = ctn(), ctn(), ctn(), ctn(), ctn()
        cac_nhap.append(
            f'<p:par><p:cTn id="{a}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>'
            f'<p:par><p:cTn id="{b}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            f'<p:par><p:cTn id="{e}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" grpId="0" nodeType="clickEffect">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            f'<p:set><p:cBhvr><p:cTn id="{s1}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl>{tgt}</p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="visible"/></p:to></p:set>'
            f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{f1}" dur="500"/><p:tgtEl>{tgt}</p:tgtEl></p:cBhvr></p:animEffect>'
            f'</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')
    bld = []
    for spid in dict.fromkeys(sp for sp, _ in buoc):
        theo_doan = any(sp == spid and d is not None for sp, d in buoc)
        bld.append(f'<p:bldP spid="{spid}" grpId="0" build="p"/>' if theo_doan else f'<p:bldP spid="{spid}" grpId="0" animBg="1"/>')
    xml = (f'<p:timing xmlns:p="{NS_P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
           f'<p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
           + "".join(cac_nhap) +
           '</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
           '</p:childTnLst></p:cTn></p:par></p:tnLst><p:bldLst>' + "".join(bld) + '</p:bldLst></p:timing>')
    _chen_sau_clrmap(sl, etree.fromstring(xml), cuoi=True)


def gan_chuyen_trang(sl, kieu):
    if kieu == "morph":
        xml = ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
               '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
               f'<p:transition xmlns:p="{NS_P}" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="slow" p14:dur="1400">'
               '<p159:morph option="byObject"/></p:transition></mc:Choice>'
               f'<mc:Fallback><p:transition xmlns:p="{NS_P}" spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')
    else:
        xml = f'<p:transition xmlns:p="{NS_P}" spd="med"><p:fade/></p:transition>'
    _chen_sau_clrmap(sl, etree.fromstring(xml), cuoi=False)


def _chen_sau_clrmap(sl, el, cuoi):
    sld = sl._element
    clr = sld.find(qn("p:clrMapOvr"))
    if cuoi:
        sld.append(el)  # timing đứng sau transition
    else:
        clr.addnext(el)


# ------------------------------------------------------------------ lưu
def luu(prs, ten, thu_muc):
    os.makedirs(thu_muc, exist_ok=True)
    pptx_path = os.path.join(thu_muc, ten + ".pptx")
    prs.save(pptx_path)
    ppsx_path = os.path.join(thu_muc, ten + ".ppsx")
    with zipfile.ZipFile(pptx_path) as zi, zipfile.ZipFile(ppsx_path, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            data = zi.read(it.filename)
            if it.filename == "[Content_Types].xml":
                data = data.replace(b"presentationml.presentation.main+xml", b"presentationml.slideshow.main+xml")
            zo.writestr(it, data)
    return pptx_path, ppsx_path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dac_ta")
    ap.add_argument("--ra", default=".")
    a = ap.parse_args()
    dt = json.load(open(a.dac_ta, encoding="utf-8"))
    for k in ("ten_tep", "phong_cach", "slides"):
        if k not in dt:
            sys.exit(f"LỖI: đặc tả thiếu trường '{k}'")
    for k in ("dark", "light", "soft", "text", "muted", "accent", "accent2", "accentText", "accentOnDark"):
        if k not in dt["phong_cach"].get("mau", {}):
            sys.exit(f"LỖI: phong_cach.mau thiếu màu '{k}'")
    prs = Bo(dt).dung()
    p1, p2 = luu(prs, re.sub(r"[^\w.-]+", "_", dt["ten_tep"]), a.ra)
    print(p1)
    print(p2)
    if CANH_BAO:
        print(f"\nCẢNH BÁO ({len(CANH_BAO)})")
        for x in CANH_BAO:
            print("  " + x)
    else:
        print("\nKhông có cảnh báo.")


if __name__ == "__main__":
    main()
