#!/usr/bin/env python3
"""kiem_tra_goi.py — kiểm tra cấu trúc gói Office Open XML (.pptx/.ppsx/.docx).

Dùng thay `validate.py` của skill pptx khi môi trường không có skill đó (Gemini CLI, máy cá nhân).
Không kiểm theo lược đồ XSD đầy đủ; bắt các lỗi làm PowerPoint báo "cần sửa chữa tệp":
  - gói zip hỏng, tên phần trùng;
  - phần XML không đúng cú pháp;
  - [Content_Types].xml thiếu khai báo cho phần có trong gói;
  - quan hệ (.rels) trỏ tới phần không tồn tại;
  - id quan hệ trùng trong một tệp .rels;
  - id đối tượng (p:cNvPr/@id) trùng trong một slide (trừ bản dự phòng mc:Fallback);
  - (cảnh báo) mục thư mục trong zip;
  - python-pptx (hoặc python-docx) không mở được.

Cách dùng: python3 kiem_tra_goi.py file.pptx [file2.ppsx ...]
Kết quả: in "PASSED" khi không có LỖI; mã thoát 1 khi có LỖI.
"""
import posixpath
import sys
import zipfile
from collections import Counter

from lxml import etree

CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def _rels_base(rels_name):
    # ppt/slides/_rels/slide1.xml.rels -> ppt/slides/slide1.xml ; _rels/.rels -> ""
    folder, fname = posixpath.split(rels_name)
    parent = posixpath.dirname(folder)
    return posixpath.join(parent, fname[: -len(".rels")]) if fname != ".rels" else ""


def kiem_tra(path):
    loi, canh_bao = [], []
    try:
        z = zipfile.ZipFile(path)
    except FileNotFoundError:
        return ["không tìm thấy tệp"], []
    except zipfile.BadZipFile as e:
        return [f"không phải gói zip hợp lệ: {e}"], []

    with z:
        names = z.namelist()
        bad = z.testzip()
        if bad:
            loi.append(f"phần bị hỏng trong zip: {bad}")
        for n, c in Counter(names).items():
            if c > 1:
                loi.append(f"tên phần trùng {c} lần: {n}")
        parts = {n for n in names if not n.endswith("/")}
        thu_muc = [n for n in names if n.endswith("/")]
        if thu_muc:
            canh_bao.append(f"{len(thu_muc)} mục thư mục trong zip (OneDrive/SharePoint có thể không mở được); "
                            "xoá bằng: zip -dq <tệp> '*/'")

        trees = {}
        for n in sorted(parts):
            if n.endswith((".xml", ".rels")):
                try:
                    trees[n] = etree.fromstring(z.read(n))
                except etree.XMLSyntaxError as e:
                    loi.append(f"XML sai cú pháp: {n}: {e}")

        ct = trees.get("[Content_Types].xml")
        if ct is None:
            loi.append("thiếu [Content_Types].xml")
        else:
            defaults = {d.get("Extension", "").lower() for d in ct.findall(f"{{{CT_NS}}}Default")}
            overrides = {o.get("PartName", "").lstrip("/") for o in ct.findall(f"{{{CT_NS}}}Override")}
            for n in parts:
                if n == "[Content_Types].xml":
                    continue
                ext = n.rsplit(".", 1)[-1].lower() if "." in n else ""
                if n not in overrides and ext not in defaults:
                    loi.append(f"[Content_Types] không khai báo kiểu cho: {n}")
            for o in overrides:
                if o not in parts:
                    canh_bao.append(f"[Content_Types] khai báo phần không có trong gói: /{o}")

        for n, t in trees.items():
            if not n.endswith(".rels"):
                continue
            base = _rels_base(n)
            ids = Counter()
            for r in t.findall(f"{{{REL_NS}}}Relationship"):
                ids[r.get("Id")] += 1
                if r.get("TargetMode") == "External":
                    continue
                target = r.get("Target", "")
                if target.startswith("/"):
                    full = target.lstrip("/")
                else:
                    full = posixpath.normpath(posixpath.join(posixpath.dirname(base), target))
                if full not in parts:
                    loi.append(f"{n}: quan hệ {r.get('Id')} trỏ tới phần không tồn tại: {full}")
            for i, c in ids.items():
                if c > 1:
                    loi.append(f"{n}: id quan hệ trùng {i}")

        for n, t in trees.items():
            if n.startswith("ppt/slides/slide") and n.endswith(".xml"):
                # bỏ qua bản dự phòng trong mc:Fallback (trùng id với mc:Choice là đúng chuẩn)
                ids = Counter(e.get("id") for e in t.iter(f"{{{P_NS}}}cNvPr")
                              if not any(a.tag == f"{{{MC_NS}}}Fallback" for a in e.iterancestors()))
                for i, c in ids.items():
                    if c > 1:
                        loi.append(f"{n}: id đối tượng trùng {i} ({c} lần)")

    if not loi:
        try:
            if path.lower().endswith(".docx"):
                import docx
                docx.Document(path)
            else:
                import pptx
                src = path
                if path.lower().endswith(".ppsx"):
                    # python-pptx chỉ nhận kiểu presentation.main; mở bản sao trong bộ nhớ đã đổi kiểu
                    import io
                    buf = io.BytesIO()
                    with zipfile.ZipFile(path) as zi, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
                        for it in zi.infolist():
                            data = zi.read(it.filename)
                            if it.filename == "[Content_Types].xml":
                                data = data.replace(b"slideshow.main+xml", b"presentation.main+xml")
                            zo.writestr(it, data)
                    buf.seek(0)
                    src = buf
                pptx.Presentation(src)
        except ImportError:
            canh_bao.append("chưa cài python-pptx/python-docx, bỏ qua bước mở thử")
        except Exception as e:  # noqa: BLE001
            loi.append(f"không mở được bằng python-pptx/python-docx: {e}")
    return loi, canh_bao


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    co_loi = False
    for p in argv[1:]:
        loi, cb = kiem_tra(p)
        print(f"== {p}")
        for x in loi:
            print(f"LỖI: {x}")
        for x in cb:
            print(f"CẢNH BÁO: {x}")
        print("FAILED" if loi else "PASSED")
        co_loi |= bool(loi)
    return 1 if co_loi else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
