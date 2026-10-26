#!/usr/bin/env python3
"""hoa_tiet_tam_giac.py — vẽ hoạ tiết lưới tam giác (motif kiểu "mắt lưới tam giác ghép lục giác"), xuất PNG trong suốt + SVG.

Dùng cho bộ nhận diện có motif tam giác (ví dụ Trường ĐH Bách khoa – ĐHQG-HCM: assets/thuong-hieu/bk-hcmut)
hoặc tự chọn bảng màu để sáng tạo hoạ tiết mới.

Kiểu (--kieu):
  luoi     lưới tam giác chỉ có nét (wireframe), đậm về một phía (--dam-ve) và mờ dần về phía đối diện; vùng lục giác hoặc chữ nhật
  cum      cụm tam giác tô màu bám một góc, thưa dần ra xa góc (góc slide, đầu trang)
  da-giac  lục giác ghép tam giác tô nhiều màu
  dai      dải tam giác chạy ngang một mép (đầu/chân slide)

Ví dụ:
  python3 hoa_tiet_tam_giac.py --kieu cum --goc tr --bang sang --out cum_phai_tren
  python3 hoa_tiet_tam_giac.py --kieu luoi --mau FFFFFF --vung chu-nhat --dam-ve trai --w 3840 --h 2160 --out luoi_trang
  python3 hoa_tiet_tam_giac.py --kieu cum --bang "0B3C7D:0.8,1488DB:0.6,FFFFFF:0.3" --goc bl --out cum_tuy_chon
  python3 hoa_tiet_tam_giac.py --thuong-hieu bk-hcmut --bo-mac-dinh --outdir hoa-tiet   # sinh cả bộ hoạ tiết mặc định
"""
import argparse, json, math, os, random
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANG = {  # bảng màu có sẵn: (hex, độ đục)
    "sang": [("FFFFFF", 0.9), ("E6F1FB", 0.9), ("BFDDF3", 0.8), ("8EC5EA", 0.7), ("D5D9E0", 0.85), ("A9B2BE", 0.6), ("1488DB", 0.35)],
    "toi": [("FFFFFF", 0.10), ("FFFFFF", 0.18), ("1488DB", 0.45), ("5FB2EA", 0.35), ("032B91", 0.35), ("0A1F6B", 0.45)],
    "nhieu-mau": [("E6F1FB", 1), ("BFDDF3", 1), ("8EC5EA", 1), ("4FA6E3", 1), ("1488DB", 1), ("A9B2BE", 1), ("7C8796", 1), ("D5D9E0", 1), ("FFFFFF", 1), ("6B7FB8", 1)],
}

def rgba(h, a): return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(255 * a))

def tri_grid(W, H, s):
    """lưới tam giác đều cạnh s phủ W×H; trả về list (đỉnh, tâm)"""
    h = s * math.sqrt(3) / 2
    out = []
    for r in range(-1, int(H / h) + 2):
        y0, y1 = r * h, (r + 1) * h
        off = (r % 2) * s / 2
        for c in range(-2, int(W / s) + 3):
            x = c * s + off
            up = [(x, y1), (x + s / 2, y0), (x + s, y1)]
            dn = [(x + s / 2, y0), (x + s, y1), (x + 1.5 * s, y0)]
            for t in (up, dn):
                cx, cy = sum(p[0] for p in t) / 3, sum(p[1] for p in t) / 3
                out.append((t, (cx, cy)))
    return out

def in_hex(p, cx, cy, R):
    x, y = abs(p[0] - cx), abs(p[1] - cy)
    return y <= R * math.sqrt(3) / 2 and (math.sqrt(3) * x + y) <= R * math.sqrt(3)

def fade(p, W, H, huong):
    x, y = p[0] / W, p[1] / H
    return {"trai": 1 - x, "phai": x, "tren": 1 - y, "duoi": y, "giua": 1 - min(1, math.hypot(x - .5, y - .5) * 2), "khong": 1}.get(huong, 1)

def render(tris, W, H, mode, out, ss=2):
    img = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    for t, col, a, lw in tris:
        pts = [(x * ss, y * ss) for x, y in t]
        ps = " ".join(f"{x:.1f},{y:.1f}" for x, y in t)
        if mode == "line":
            d.line(pts + [pts[0]], fill=rgba(col, a), width=max(1, int(lw * ss)), joint="curve")
            svg.append(f'<polygon points="{ps}" fill="none" stroke="#{col}" stroke-opacity="{a:.3f}" stroke-width="{lw}"/>')
        else:
            d.polygon(pts, fill=rgba(col, a))
            svg.append(f'<polygon points="{ps}" fill="#{col}" fill-opacity="{a:.3f}"/>')
    svg.append("</svg>")
    img.resize((W, H), Image.LANCZOS).save(out + ".png", optimize=True)
    open(out + ".svg", "w").write("\n".join(svg))
    return out + ".png"

def ve(a):
    random.seed(a.seed)
    W, H, s = a.w, a.h, a.canh
    grid = tri_grid(W, H, s)
    cx, cy, R = W / 2, H / 2, min(W / 2, H / math.sqrt(3)) * 0.98
    bang = BANG.get(a.bang) or [(x.split(":")[0], float(x.split(":")[1]) if ":" in x else 1.0) for x in a.bang.split(",")]
    tris = []
    if a.kieu == "luoi":
        # nét mảnh, chỉ lấy tam giác hướng lên (nét các cạnh đủ tạo lưới đầy), đậm về phía --dam-ve, mờ dần phía đối diện
        for t, c in grid:
            if a.vung == "luc-giac" and not all(in_hex(p, cx, cy, R) for p in t): continue
            f = fade(c, W, H, a.dam_ve)
            if f <= 0.02: continue
            tris.append((t, a.mau, max(0.05, min(1, f)) * a.do_duc, a.net))
        mode = "line"
    elif a.kieu == "da-giac":
        for t, c in grid:
            if not all(in_hex(p, cx, cy, R) for p in t): continue
            col, al = random.choice(bang)
            tris.append((t, col, al * (0.55 + 0.45 * random.random()) * a.do_duc, 0))
        mode = "fill"
    elif a.kieu == "cum":
        gx = {"tl": 0, "bl": 0, "tr": W, "br": W}[a.goc]; gy = {"tl": 0, "tr": 0, "bl": H, "br": H}[a.goc]
        D = math.hypot(W, H)
        for t, c in grid:
            dist = math.hypot(c[0] - gx, c[1] - gy) / D
            pr = max(0, 1 - dist / a.tam) ** 1.3
            if random.random() > pr: continue
            col, al = random.choice(bang)
            tris.append((t, col, al * (0.5 + 0.5 * pr) * a.do_duc, 0))
        mode = "fill"
    elif a.kieu == "dai":
        for t, c in grid:
            v = c[1] / H if a.mep == "tren" else 1 - c[1] / H
            pr = max(0, 1 - v / a.tam) ** 1.2
            if random.random() > pr: continue
            col, al = random.choice(bang)
            tris.append((t, col, al * (0.5 + 0.5 * pr) * a.do_duc, 0))
        mode = "fill"
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    return render(tris, W, H, mode, a.out)

def bo_mac_dinh(outdir, brand):
    """bộ hoạ tiết mặc định theo bộ nhận diện (màu lấy từ brand.json)"""
    c = brand["mau"]
    N, X = c["xanh_dam"], c["xanh_tuoi"]
    jobs = [
        dict(kieu="cum", goc="tr", bang="sang", w=1800, h=1100, canh=150, tam=0.75, out="cum-sang-phai-tren"),
        dict(kieu="cum", goc="bl", bang="sang", w=1800, h=1100, canh=150, tam=0.75, out="cum-sang-trai-duoi"),
        dict(kieu="cum", goc="tr", bang="toi", w=1800, h=1100, canh=150, tam=0.8, out="cum-toi-phai-tren"),
        dict(kieu="cum", goc="bl", bang="toi", w=1800, h=1100, canh=150, tam=0.8, out="cum-toi-trai-duoi"),
        dict(kieu="dai", mep="tren", bang="sang", w=3840, h=520, canh=150, tam=1.0, out="dai-sang-dau-trang"),
        dict(kieu="dai", mep="duoi", bang="sang", w=3840, h=420, canh=150, tam=1.0, out="dai-sang-chan-trang"),
        dict(kieu="luoi", mau="FFFFFF", vung="chu-nhat", dam_ve="phai", w=2400, h=1350, canh=110, net=2.0, do_duc=0.35, out="luoi-trang-dam-phai"),
        dict(kieu="luoi", mau=X, vung="chu-nhat", dam_ve="trai", w=2400, h=1350, canh=110, net=2.0, do_duc=0.45, out="luoi-xanh-dam-trai"),
        dict(kieu="luoi", mau="FFFFFF", vung="luc-giac", dam_ve="giua", w=1600, h=1400, canh=110, net=2.0, do_duc=0.6, out="luc-giac-luoi-trang"),
        dict(kieu="da-giac", bang="nhieu-mau", w=1600, h=1400, canh=110, out="luc-giac-nhieu-mau"),
    ]
    made = []
    for j in jobs:
        a = argparse.Namespace(**{**DEF, **j, "out": os.path.join(outdir, j["out"])})
        made.append(ve(a))
    return made

DEF = dict(kieu="cum", goc="tr", bang="sang", mau="1488DB", vung="luc-giac", dam_ve="khong", mep="tren", w=1600, h=1000, canh=140, tam=0.8, net=1.5, do_duc=1.0, seed=7, out="hoa_tiet")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k, v in DEF.items():
        ap.add_argument("--" + k.replace("_", "-"), type=type(v), default=v)
    ap.add_argument("--thuong-hieu", default=None, help="tên thư mục trong assets/thuong-hieu (lấy màu)")
    ap.add_argument("--bo-mac-dinh", action="store_true", help="sinh cả bộ hoạ tiết mặc định của thương hiệu")
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()
    if a.bo_mac_dinh:
        brand = json.load(open(os.path.join(ROOT, "assets", "thuong-hieu", a.thuong_hieu or "bk-hcmut", "brand.json"), encoding="utf-8"))
        for f in bo_mac_dinh(a.outdir, brand): print(f)
    else:
        print(ve(a))
