#!/usr/bin/env python3
"""Dựng ảnh xem trước các phong cách gợi ý, dùng chính đề tài của người dùng.

Cách dùng:
  python3 xem_truoc_phong_cach.py --title "Đề tài" [--sub "Phụ đề"] --styles sang-trong,hoc-thuat,hanh-chinh \
      [--labels "Đề xuất,Phương án 2,Phương án 3"] [--body "Ý chính 1|Ý chính 2|Ý chính 3"] --out xem-truoc.png

Mỗi phong cách là một hàng gồm: slide bìa (nền đậm) + slide nội dung (nền sáng, 3 thẻ) + dải màu và tên phông.
Cần Pillow (pip install pillow).
"""
import argparse, json, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
STY = json.load(open(os.path.join(ROOT, "assets", "styles.json"), encoding="utf-8"))
FILES = json.load(open(os.path.join(ROOT, "assets", "fonts", "files.json"), encoding="utf-8"))


def font(name, size, bold=False, italic=False):
    if "(nghiêng)" in name:
        italic = True
    name = name.split("|")[0].replace("(nghiêng)", "").strip()
    f = FILES[name]
    slot = "boldItalic" if bold and italic else "bold" if bold else "italic" if italic else "regular"
    return ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", f.get(slot, f.get("bold" if bold else "regular", f["regular"]))), size)


def wrap(d, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def H(c):
    return "#" + c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--sub", default="")
    ap.add_argument("--styles", required=True)
    ap.add_argument("--labels", default="")
    ap.add_argument("--body", default="Bối cảnh|Nội dung chính|Kết luận")
    ap.add_argument("--out", required=True)
    ap.add_argument("--spec", default="", help="JSON {khoá: phong cách} do dinh_huong.js sinh (thêm vào danh sách phong cách)")
    a = ap.parse_args()
    if a.spec:
        STY.update(json.load(open(a.spec, encoding="utf-8")))
    keys = [k.strip() for k in a.styles.split(",") if k.strip()]
    labels = [l.strip() for l in a.labels.split(",")] if a.labels else []
    body = [b.strip() for b in a.body.split("|")][:3]

    SW, SH, PAD = 640, 360, 28  # mỗi slide 640×360
    ROWH = SH + 70
    img = Image.new("RGB", (PAD * 3 + SW * 2, PAD + ROWH * len(keys)), "#ECEEF2")
    d = ImageDraw.Draw(img)
    lab_f = font("Montserrat", 20, bold=True)
    for r, k in enumerate(keys):
        s = STY[k]; c = s["colors"]; hf = s["fonts"]["head"]; bf = s["fonts"]["body"]
        it = "(nghiêng)" in hf
        y0 = PAD + r * ROWH
        name = (labels[r] + " · " if r < len(labels) and labels[r] else f"Phương án {r + 1} · ") + s["ten"]
        d.text((PAD, y0), name, font=lab_f, fill="#1F2430")
        fonts_line = "Phông: " + " / ".join(x.split("|")[0].replace("(nghiêng)", "").strip() for x in (hf, bf, s["fonts"].get("accent")) if x)
        d.text((PAD + SW * 2 + PAD - d.textlength(fonts_line, font=font("Montserrat", 15)), y0 + 4), fonts_line, font=font("Montserrat", 15), fill="#5A6070")
        y = y0 + 34
        # slide bìa
        cv = Image.new("RGB", (SW, SH), H(c["dark"])); cd = ImageDraw.Draw(cv)
        xt = s.get("xem_truoc", {})
        def overlay(canvas, f):
            if f and os.path.exists(f):
                tx = Image.open(f).convert("RGBA").resize((SW, SH)); canvas.paste(tx, (0, 0), tx)
        overlay(cv, xt.get("texture_bia")); cd = ImageDraw.Draw(cv)
        if xt.get("logo_bia") and os.path.exists(xt["logo_bia"]):
            lg = Image.open(xt["logo_bia"]).convert("RGBA"); lg.thumbnail((200, 30)); cv.paste(lg, (40, 40), lg)
        tf = font(hf, 40, bold=not it)
        ty = 112
        for line in wrap(cd, a.title, tf, SW - 90)[:3]:
            cd.text((40, ty), line, font=tf, fill="#FFFFFF"); ty += 50
        if a.sub:
            for line in wrap(cd, a.sub, font(bf, 19), SW - 90)[:2]:
                cd.text((40, ty + 10), line, font=font(bf, 19), fill=H(c["accentOnDark"])); ty += 26
        img.paste(cv, (PAD, y))
        # slide nội dung: ba cột không nền, mở bằng vạch mảnh, cột giữa được nhấn (không biểu tượng trong vòng tròn)
        cv = Image.new("RGB", (SW, SH), H(c.get("light", "FFFFFF")))
        overlay(cv, xt.get("texture_noi_dung")); cd = ImageDraw.Draw(cv)
        cd.text((36, 30), "Ba ý chính của bài", font=font(hf, 28, bold=not it), fill=H(c["text"]))
        cw = (SW - 72 - 32) / 3
        for j, t_ in enumerate(body):
            x = 36 + j * (cw + 16)
            cd.rectangle((x, 104, x + cw, 107), fill=H(c["accent"] if j == 1 else c["text"]))
            cd.text((x, 122), ["01", "02", "03"][j], font=font(hf, 30, bold=True), fill=H(c["accentText"] if j == 1 else c["text"]))
            yy = 172
            for line in wrap(cd, t_, font(bf, 16, bold=True), cw - 10)[:3]:
                cd.text((x, yy), line, font=font(bf, 16, bold=True), fill=H(c["text"])); yy += 21
            for line in wrap(cd, "Nội dung minh hoạ cho phong cách", font(bf, 14), cw - 10)[:2]:
                cd.text((x, yy + 6), line, font=font(bf, 14), fill=H(c["muted"])); yy += 19
        for j, kk in enumerate([x for x in ("dark", "accent", "accent2", "accentText", "soft") if x in c]):
            cd.rectangle((SW - 36 - (5 - j) * 26, SH - 30, SW - 36 - (5 - j) * 26 + 20, SH - 14), fill=H(c[kk]), outline="#D0D4DC")
        if s["fonts"].get("accent") and s.get("muc") != "chinh-quy":
            cd.text((SW - 200, 26), "Ấn tượng", font=font(s["fonts"]["accent"], 34), fill=H(c["accentText"]))
        img.paste(cv, (PAD * 2 + SW, y))
    img.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
