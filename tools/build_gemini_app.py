#!/usr/bin/env python3
"""build_gemini_app.py — đóng gói hai skill cho Gemini app (tải lên tại Skills → Create → Upload).

Mỗi skill thành một tệp .zip có SKILL.md ở thư mục gốc:
  dist/slidewright-make-slides-gemini-app-<phiên bản>.zip
  dist/slidewright-presentation-script-gemini-app-<phiên bản>.zip

Nguồn: skills/ (dùng chung với Claude và Gemini CLI) + gemini-app/ (phần riêng của Gemini app).
Phiên bản lấy từ gemini-extension.json (workflow release đã đồng bộ theo tag).
Cần Node.js để tính sẵn bảng màu (tools/phuong_an.js).

Dùng: python3 tools/build_gemini_app.py [--ra dist]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MS = os.path.join(GOC, "skills", "make-slides")
PS = os.path.join(GOC, "skills", "presentation-script")
APP = os.path.join(GOC, "gemini-app")

# Tài liệu quy tắc dùng được khi không có Node/LibreOffice (bỏ các quy trình kỹ thuật riêng của bản Claude)
REF_MAKE_SLIDES = [
    "boi-canh.md", "noi-dung-slide.md", "dau-hieu-ai.md", "phoi-mau.md", "phong-cach.md", "phong-chu.md",
    "nguyen-tac-thiet-ke.md", "van-ban-hanh-chinh.md", "dan-y-mau.md", "kiem-soat-van-ban.md",
]
ASSET_MAKE_SLIDES = ["contexts.json", "styles.json"]
# Script kiểm tra chạy bằng Python thuần (+ python-pptx/lxml/Pillow)
SCRIPT_MAKE_SLIDES = [
    "kiem_tra_slide.py", "kiem_tra_hieu_ung.py", "kiem_tra_goi.py", "kiem_soat_van_ban.py", "kiem_tra_van_ban.py",
]
FONT_META = ["files.json", "phan-loai.json"]  # siêu dữ liệu phông cho kiem_soat_van_ban.py (không kèm tệp phông)
BO_QUA = (".pyc", ".DS_Store")


def phien_ban():
    return json.load(open(os.path.join(GOC, "gemini-extension.json"), encoding="utf-8"))["version"]


def chep(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def chep_cay(src, dst):
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", *("*" + x for x in BO_QUA)),
                    dirs_exist_ok=True)


def nen(thu_muc, tep_zip):
    with zipfile.ZipFile(tep_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for goc, _, tep in os.walk(thu_muc):
            for t in sorted(tep):
                if t.endswith(BO_QUA):
                    continue
                p = os.path.join(goc, t)
                z.write(p, os.path.relpath(p, thu_muc))


def make_slides(ra, v):
    d = os.path.join(ra, "make-slides")
    s = open(os.path.join(APP, "make-slides", "SKILL.md.tmpl"), encoding="utf-8").read()
    os.makedirs(d)
    open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8").write(s.replace("{{VERSION}}", v))
    chep_cay(os.path.join(APP, "make-slides", "scripts"), os.path.join(d, "scripts"))
    chep_cay(os.path.join(APP, "make-slides", "assets"), os.path.join(d, "assets"))
    for f in REF_MAKE_SLIDES:
        chep(os.path.join(MS, "references", f), os.path.join(d, "references", f))
    for f in ASSET_MAKE_SLIDES:
        chep(os.path.join(MS, "assets", f), os.path.join(d, "assets", f))
    for f in FONT_META:
        chep(os.path.join(MS, "assets", "fonts", f), os.path.join(d, "assets", "fonts", f))
    for f in SCRIPT_MAKE_SLIDES:
        chep(os.path.join(MS, "scripts", f), os.path.join(d, "scripts", f))
    subprocess.run(["node", os.path.join(GOC, "tools", "phuong_an.js"), os.path.join(d, "assets", "phuong-an.json")],
                   check=True)
    return d


def presentation_script(ra, v):
    d = os.path.join(ra, "presentation-script")
    chep_cay(PS, d)
    os.remove(os.path.join(d, "SKILL.md"))
    chep(os.path.join(MS, "assets", "contexts.json"), os.path.join(d, "assets", "contexts.json"))
    s = open(os.path.join(PS, "SKILL.md"), encoding="utf-8").read()
    ghi_chu = open(os.path.join(APP, "presentation-script", "ghi-chu-app.md"), encoding="utf-8").read()
    thay = [
        (r"Đường dẫn `references/`, `scripts/` tính từ thư mục skill này \(.*?\)\. ",
         "Đường dẫn `references/`, `scripts/`, `assets/` tính từ thư mục skill này. "),
        (r"\(`\.\./make-slides/assets/contexts\.json`\)", "(`assets/contexts.json`)"),
        (r"hỏi gộp một lượt bằng AskUserQuestion", "hỏi gộp một lượt trong hội thoại"),
        (r"Gửi bằng SendUserFile:", "Đưa tệp để tải về:"),
    ]
    for mau, moi in thay:
        s, n = re.subn(mau, moi, s, count=1)
        if n != 1:
            sys.exit(f"LỖI: không tìm thấy đoạn cần đổi trong presentation-script/SKILL.md: {mau}")
    s = re.sub(r"^(# .+\n)", lambda m: m.group(1) + "\n" + ghi_chu.replace("{{VERSION}}", v) + "\n", s, count=1,
               flags=re.M)
    open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8").write(s)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ra", default=os.path.join(GOC, "dist"))
    a = ap.parse_args()
    v = phien_ban()
    tam = os.path.join(a.ra, "gemini-app")
    shutil.rmtree(tam, ignore_errors=True)
    os.makedirs(tam)
    ket_qua = []
    for ten, ham in (("make-slides", make_slides), ("presentation-script", presentation_script)):
        d = ham(tam, v)
        z = os.path.join(a.ra, f"slidewright-{ten}-gemini-app-{v}.zip")
        nen(d, z)
        ket_qua.append(z)
        print(f"{z}  ({os.path.getsize(z) // 1024} KB)")
    return ket_qua


if __name__ == "__main__":
    main()
