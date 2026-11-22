#!/usr/bin/env python3
"""build_gemini_app.py — đóng gói hai skill cho Gemini app (tải lên tại Skills → Create → Upload).

Mỗi skill thành một tệp .zip có SKILL.md ở thư mục gốc:
  dist/slidewright-make-slides-gemini-app-<phiên bản>.zip
  dist/slidewright-presentation-script-gemini-app-<phiên bản>.zip

Nguồn: skills/ (tài liệu quy tắc dùng chung với Claude và Gemini CLI) + gemini-app/ (SKILL.md riêng).
Gemini app từ chối nạp skill có kèm mã chạy được, nên gói chỉ chứa SKILL.md, tệp .md và .json;
có tệp thực thi lọt vào thì dừng với LỖI.
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
BO_QUA = (".pyc", ".DS_Store")
# Gemini Chat: "Skill … contains executable code or scripts, which are not supported"
DUOI_THUC_THI = (".py", ".js", ".mjs", ".cjs", ".ts", ".sh", ".bash", ".ps1", ".bat", ".cmd", ".ipynb", ".rb", ".pl")
REF_PRESENTATION_SCRIPT = ["viet-loi-noi.md", "hoi-dap.md", "dinh-dang-kich-ban.md"]


def phien_ban():
    return json.load(open(os.path.join(GOC, "gemini-extension.json"), encoding="utf-8"))["version"]


def chep(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


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
    for f in REF_MAKE_SLIDES:
        chep(os.path.join(MS, "references", f), os.path.join(d, "references", f))
    for f in ASSET_MAKE_SLIDES:
        chep(os.path.join(MS, "assets", f), os.path.join(d, "assets", f))
    subprocess.run(["node", os.path.join(GOC, "tools", "phuong_an.js"), os.path.join(d, "assets", "phuong-an.json")],
                   check=True)
    return d


def presentation_script(ra, v):
    d = os.path.join(ra, "presentation-script")
    s = open(os.path.join(APP, "presentation-script", "SKILL.md.tmpl"), encoding="utf-8").read()
    os.makedirs(d)
    open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8").write(s.replace("{{VERSION}}", v))
    for f in REF_PRESENTATION_SCRIPT:
        chep(os.path.join(PS, "references", f), os.path.join(d, "references", f))
    chep(os.path.join(MS, "assets", "contexts.json"), os.path.join(d, "assets", "contexts.json"))
    return d


def kiem_goi(d):
    """Chặn tệp thực thi; mô tả ≤ 1024 ký tự; SKILL.md có frontmatter name/description."""
    loi = []
    for goc, _, tep in os.walk(d):
        for t in tep:
            if t.lower().endswith(DUOI_THUC_THI):
                loi.append(f"tệp thực thi: {os.path.relpath(os.path.join(goc, t), d)}")
    s = open(os.path.join(d, "SKILL.md"), encoding="utf-8").read()
    m = re.match(r"---\nname: ([a-z0-9-]+)\ndescription: (.+?)\n---\n", s, flags=re.S)
    if not m:
        loi.append("SKILL.md thiếu frontmatter name/description")
    elif len(m.group(2)) > 1024:
        loi.append(f"description dài {len(m.group(2))} ký tự (> 1024)")
    if "{{" in s:
        loi.append("SKILL.md còn chỗ {{…}} chưa thay")
    if loi:
        sys.exit("LỖI gói " + os.path.basename(d) + ":\n  " + "\n  ".join(loi))


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
        kiem_goi(d)
        z = os.path.join(a.ra, f"slidewright-{ten}-gemini-app-{v}.zip")
        nen(d, z)
        ket_qua.append(z)
        print(f"{z}  ({os.path.getsize(z) // 1024} KB)")
    return ket_qua


if __name__ == "__main__":
    main()
