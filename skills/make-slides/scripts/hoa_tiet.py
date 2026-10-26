#!/usr/bin/env python3
"""hoa_tiet.py — bộ sinh texture/hoạ tiết nền cho slide, xuất PNG trong suốt (+ SVG trừ kiểu giấy).

Kiểu (--kieu)          Hợp với lĩnh vực
  cham                 lưới chấm mờ dần — công nghệ, dữ liệu, kinh tế
  mach                 đường mạch điện (đoạn vuông góc + chân hàn) — điện tử, CNTT, kỹ thuật
  song                 đường sóng/đồng mức chạy ngang — địa lý, môi trường, KHXH (nhịp mềm), y sinh
  giay                 vân giấy (hạt + sợi) rất nhẹ — KHXH, nhân văn, lịch sử, văn học
  ke-o                 giấy kẻ ô (ô nhỏ + ô lớn) — toán, KHTN, kỹ thuật
  luc-giac             lưới lục giác/tổ ong nét mảnh — hoá học, vật liệu, công nghệ
  gach-cheo            dải gạch chéo mảnh — kinh tế, hành chính, nhấn mép slide
  dong-muc             đường đồng mức địa hình thật — địa lý, môi trường, KHXH, lịch sử
  vong-dong-tam        cung tròn đồng tâm toả từ góc — sóng, tín hiệu, truyền thông, vật lý
  khoi-hinh-hoc        khối tròn/dải lớn trong suốt kiểu áp phích Thuỵ Sĩ — kinh tế, sự kiện, bìa hiện đại
  chu-thap             lưới dấu cộng — kỹ thuật, toán, dữ liệu
  luoi-phoi-canh       lưới phối cảnh hội tụ — công nghệ, kỹ thuật, tương lai
  hat                  hạt sáng li ti cho nền tối — thiên văn, công nghệ, sự kiện
  duong-ke-le          vạch lề + dòng kẻ trang vở/tạp chí — văn học, giáo dục, KHXH
  anh-sang             quầng sáng mềm tạo chiều sâu (không nét)
  tam-giac-luoi / tam-giac-cum   (gọi hoa_tiet_tam_giac.py) — motif tam giác (bộ nhận diện Bách khoa…)

Chồng nhiều lớp: --lop '[{"kieu":"anh-sang","mau":"1488DB","dam_ve":"tr"},{"kieu":"mach","mau":"55EDD9","dam_ve":"br"}]' --out bia

Độ đậm: --dam-ve trai|phai|tren|duoi|giua|tl|tr|bl|br|khong : phía hoạ tiết đậm nhất, mờ dần về phía đối diện.
Màu: --mau (hex) theo bảng màu đề tài; --do-duc 0–1 nhân thêm độ trong suốt chung.

Ví dụ:
  python3 hoa_tiet.py --kieu mach --mau 1488DB --dam-ve br --out mach_xanh
  python3 hoa_tiet.py --kieu giay --mau 6B4E3A --out giay_nga
  python3 hoa_tiet.py --kieu song --mau 7B1E2B --dam-ve duoi --do-duc 0.5 --out song_do_ruou
"""
import argparse, json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

def rgba(h, a): h = h.replace("#", ""); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), max(0, min(255, int(255 * a))))

def fade(x, y, W, H, d):
    u, v = x / W, y / H
    f = {"trai": 1 - u, "phai": u, "tren": 1 - v, "duoi": v, "giua": 1 - min(1, math.hypot(u - .5, v - .5) * 2),
         "tl": 1 - min(1, math.hypot(u, v) / 1.2), "tr": 1 - min(1, math.hypot(1 - u, v) / 1.2),
         "bl": 1 - min(1, math.hypot(u, 1 - v) / 1.2), "br": 1 - min(1, math.hypot(1 - u, 1 - v) / 1.2), "khong": 1}[d]
    return max(0.0, min(1.0, f))

class Canvas:
    def __init__(s, W, H, ss=2):
        s.W, s.H, s.ss = W, H, ss
        s.img = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.img, "RGBA")
        s.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    def line(s, pts, col, a, w):
        s.d.line([(x * s.ss, y * s.ss) for x, y in pts], fill=rgba(col, a), width=max(1, round(w * s.ss)), joint="curve")
        s.svg.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="#{col}" stroke-opacity="{a:.3f}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
    def circle(s, x, y, r, col, a, fill=True, w=1):
        b = [(x - r) * s.ss, (y - r) * s.ss, (x + r) * s.ss, (y + r) * s.ss]
        if fill: s.d.ellipse(b, fill=rgba(col, a)); s.svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#{col}" fill-opacity="{a:.3f}"/>')
        else: s.d.ellipse(b, outline=rgba(col, a), width=max(1, round(w * s.ss))); s.svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" stroke="#{col}" stroke-opacity="{a:.3f}" stroke-width="{w}"/>')
    def save(s, out, svg=True):
        s.img.resize((s.W, s.H), Image.LANCZOS).save(out + ".png", optimize=True)
        if svg: open(out + ".svg", "w").write("\n".join(s.svg + ["</svg>"]))
        return out + ".png"

def ve(a):
    random.seed(a.seed)
    W, H, col, k = a.w, a.h, a.mau.replace("#", ""), a.do_duc
    F = lambda x, y: fade(x, y, W, H, a.dam_ve)
    cv = Canvas(W, H)
    s = a.buoc
    if a.kieu == "cham":
        for y in range(s // 2, H, s):
            for x in range(s // 2, W, s):
                f = F(x, y)
                if f > 0.03: cv.circle(x, y, a.net * 1.6 * (0.5 + 0.5 * f), col, 0.55 * f * k)
    elif a.kieu == "ke-o":
        for i, x in enumerate(range(0, W + 1, s)):
            big = i % 5 == 0
            for y0 in range(0, H, s):
                f = F(x, y0 + s / 2)
                if f > 0.03: cv.line([(x, y0), (x, y0 + s)], col, (0.45 if big else 0.22) * f * k, a.net * (1.6 if big else 1))
        for i, y in enumerate(range(0, H + 1, s)):
            big = i % 5 == 0
            for x0 in range(0, W, s):
                f = F(x0 + s / 2, y)
                if f > 0.03: cv.line([(x0, y), (x0 + s, y)], col, (0.45 if big else 0.22) * f * k, a.net * (1.6 if big else 1))
    elif a.kieu == "luc-giac":
        r = s / 2; hw = math.sqrt(3) * r
        for row in range(-1, int(H / (1.5 * r)) + 2):
            for c in range(-1, int(W / hw) + 2):
                cx = c * hw + (row % 2) * hw / 2; cy = row * 1.5 * r
                f = F(cx, cy)
                if f < 0.04 or random.random() > 0.35 + 0.65 * f: continue
                pts = [(cx + r * math.cos(math.radians(60 * i + 30)), cy + r * math.sin(math.radians(60 * i + 30))) for i in range(7)]
                cv.line(pts, col, 0.5 * f * k, a.net)
    elif a.kieu == "mach":
        g = s / 2
        nodes = [(x, y) for x in range(0, W, int(g)) for y in range(0, H, int(g))]
        random.shuffle(nodes)
        for (x, y) in nodes[: int(len(nodes) * 0.10 * a.mat_do)]:
            f = F(x, y)
            if random.random() > f: continue
            pts = [(x, y)]; dx, dy = random.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])
            for _ in range(random.randint(2, 5)):
                L = g * random.randint(1, 4)
                x, y = x + dx * L, y + dy * L; pts.append((x, y))
                if random.random() < 0.5:  # bẻ góc 45° rồi rẽ vuông
                    d2 = g * random.randint(1, 2); x, y = x + (dx or random.choice([-1, 1])) * d2, y + (dy or random.choice([-1, 1])) * d2; pts.append((x, y))
                dx, dy = random.choice([(dy, dx), (-dy, -dx), (dx, dy)])
            a_ = 0.55 * f * k
            cv.line(pts, col, a_, a.net)
            cv.circle(*pts[0], a.net * 2.2, col, a_, fill=False, w=a.net)
            cv.circle(*pts[-1], a.net * 2.2, col, a_)
    elif a.kieu == "song":
        n = int(H / s) + 2
        ph = [random.uniform(0, 6.28) for _ in range(3)]
        for i in range(n):
            y0 = i * s
            pts = []
            for x in range(0, W + 1, 8):
                y = y0 + s * 0.9 * math.sin(x / W * 2.2 * math.pi + ph[0] + i * 0.15) + s * 0.45 * math.sin(x / W * 5.1 * math.pi + ph[1]) + i * 0
                pts.append((x, y))
            # cắt thành đoạn theo độ đậm để mờ dần
            seg = []
            for (x, y) in pts:
                f = F(x, min(max(y, 0), H))
                seg.append((x, y, f))
            for j in range(0, len(seg) - 1, 6):
                part = seg[j:j + 7]; f = sum(p[2] for p in part) / len(part)
                if f > 0.03: cv.line([(p[0], p[1]) for p in part], col, 0.5 * f * k, a.net)
    elif a.kieu == "gach-cheo":
        for x0 in range(-H, W, s):
            pts = [(x0, H), (x0 + H, 0)]
            # vẽ thành đoạn ngắn để mờ dần
            for t in range(0, 20):
                p0 = (x0 + H * t / 20, H - H * t / 20); p1 = (x0 + H * (t + 1) / 20, H - H * (t + 1) / 20)
                f = F((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
                if f > 0.03: cv.line([p0, p1], col, 0.4 * f * k, a.net)
    elif a.kieu == "dong-muc":
        # đường đồng mức thật (địa hình giả lập bằng tổng các gò Gauss), vẽ bằng matplotlib contour
        import numpy as np
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        gx, gy = np.meshgrid(np.linspace(0, W, 240), np.linspace(0, H, 135))
        z = np.zeros_like(gx)
        for _ in range(7):
            cx, cy, r, amp = random.uniform(0, W), random.uniform(0, H), random.uniform(0.15, 0.4) * W, random.uniform(-1, 1.4)
            z += amp * np.exp(-((gx - cx) ** 2 + (gy - cy) ** 2) / (2 * r * r))
        cs = plt.contour(gx, gy, z, levels=max(6, int(14 * a.mat_do)))
        for seg_level in cs.allsegs:
            for seg in seg_level:
                if len(seg) < 4: continue
                pts = [(float(x), float(y)) for x, y in seg[::2]]
                for j in range(0, len(pts) - 1, 8):
                    part = pts[j:j + 9]; f = sum(F(x, y) for x, y in part) / len(part)
                    if f > 0.03: cv.line(part, col, 0.5 * f * k, a.net)
        plt.close("all")
    elif a.kieu == "vong-dong-tam":
        # các cung tròn đồng tâm toả ra từ một góc (--dam-ve chọn góc), nét đều, thưa dần
        cx, cy = {"tl": (0, 0), "tr": (W, 0), "bl": (0, H), "br": (W, H), "giua": (W / 2, H / 2)}.get(a.dam_ve, (W, H))
        R = math.hypot(W, H)
        r = s
        while r < R:
            f = max(0.0, 1 - r / (R * 0.75))
            if f > 0.03:
                pts = [(cx + r * math.cos(math.radians(d)), cy + r * math.sin(math.radians(d))) for d in range(0, 361, 2)]
                pts = [(x, y) for x, y in pts if -5 <= x <= W + 5 and -5 <= y <= H + 5]
                if len(pts) > 2: cv.line(pts, col, 0.5 * f * k, a.net)
            r += s * (1 + 0.15 * random.random())
    elif a.kieu == "khoi-hinh-hoc":
        # khối hình học lớn kiểu áp phích Thuỵ Sĩ: hình tròn, phần tư tròn, dải chữ nhật, trong suốt chồng nhau
        def poly(points, alpha):
            cv.d.polygon([(x * cv.ss, y * cv.ss) for x, y in points], fill=rgba(col, alpha))
            cv.svg.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" fill="#{col}" fill-opacity="{alpha:.3f}"/>')
        bx, by = {"tl": (0, 0), "tr": (W, 0), "bl": (0, H), "br": (W, H)}.get(a.dam_ve, (W, H))
        R = min(W, H) * 0.95
        poly([(bx + R * math.cos(math.radians(d)), by + R * math.sin(math.radians(d))) for d in range(0, 361, 3)], 0.10 * k)
        poly([(bx + R * 0.62 * math.cos(math.radians(d)), by + R * 0.62 * math.sin(math.radians(d))) for d in range(0, 361, 3)], 0.12 * k)
        sx = W * 0.62 if bx else W * 0.12
        poly([(sx, 0), (sx + W * 0.06, 0), (sx + W * 0.06, H), (sx, H)], 0.07 * k)
        cv.circle(W * 0.18 if bx else W * 0.82, H * 0.78 if by else H * 0.22, s * 0.5, col, 0.25 * k)   # chấm nhấn đối góc
    elif a.kieu == "chu-thap":
        for y in range(s // 2, H, s):
            for x in range(s // 2, W, s):
                f = F(x, y)
                if f > 0.03:
                    m = a.net * 3.2
                    cv.line([(x - m, y), (x + m, y)], col, 0.5 * f * k, a.net); cv.line([(x, y - m), (x, y + m)], col, 0.5 * f * k, a.net)
    elif a.kieu == "luoi-phoi-canh":
        # lưới phối cảnh (mặt sàn) hội tụ về một điểm trên đường chân trời — công nghệ, kỹ thuật
        hz, vx = H * 0.45, W * (0.7 if a.dam_ve in ("phai", "tr", "br") else 0.3 if a.dam_ve in ("trai", "tl", "bl") else 0.5)
        for i in range(-30, 31):
            x0 = vx + i * s * 1.6
            f = max(0.0, 1 - abs(i) / 30)
            cv.line([(vx, hz), (x0 + (x0 - vx) * 3, H + H)], col, 0.35 * f * k, a.net)
        y, step = hz + 6, 6
        while y < H:
            f = min(1.0, (y - hz) / (H - hz))
            cv.line([(0, y), (W, y)], col, 0.4 * f * k, a.net)
            step *= 1.28; y += step
    elif a.kieu == "hat":
        # hạt sáng li ti (bụi sao) cho nền tối, mờ dần
        for _ in range(int(W * H / 2600 * a.mat_do)):
            x, y = random.uniform(0, W), random.uniform(0, H); f = F(x, y)
            if random.random() < f: cv.circle(x, y, random.choice([0.8, 1.0, 1.4, 2.0]) * a.net, col, random.uniform(0.2, 0.7) * f * k)
    elif a.kieu == "duong-ke-le":
        # đường kẻ lề kiểu trang sách/tạp chí: vạch lề dọc + vài dòng kẻ ngang mảnh
        lx = W * 0.06
        cv.line([(lx, 0), (lx, H)], col, 0.35 * k, a.net * 1.2)
        for y in range(int(s * 1.5), H, s):
            f = F(W / 2, y)
            if f > 0.03: cv.line([(lx + s * 0.4, y), (W, y)], col, 0.18 * f * k, a.net * 0.8)
    elif a.kieu == "anh-sang":
        # quầng sáng mềm (tạo chiều sâu cho nền tối / nền màu), không có nét
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); px = img.load()
        cx, cy = {"tl": (0, 0), "tr": (W, 0), "bl": (0, H), "br": (W, H), "giua": (W / 2, H / 2)}.get(a.dam_ve, (W * 0.8, H * 0.2))
        R = math.hypot(W, H) * 0.6
        small = Image.new("RGBA", (W // 8, H // 8), (0, 0, 0, 0)); sp = small.load()
        for yy in range(H // 8):
            for xx in range(W // 8):
                dd = math.hypot(xx * 8 - cx, yy * 8 - cy) / R
                sp[xx, yy] = rgba(col, max(0, 1 - dd) ** 2 * 0.45 * k)
        small.resize((W, H), Image.BILINEAR).save(a.out + ".png", optimize=True); return a.out + ".png"
    elif a.kieu == "giay":
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); px = img.load()
        for _ in range(int(W * H * 0.06 * a.mat_do)):
            x, y = random.randrange(W), random.randrange(H)
            f = F(x, y); px[x, y] = rgba(col, random.uniform(0.04, 0.16) * f * k)
        d = ImageDraw.Draw(img, "RGBA")
        for _ in range(int(W * H / 9000 * a.mat_do)):
            x, y = random.uniform(0, W), random.uniform(0, H); ang = random.uniform(0, math.pi); L = random.uniform(6, 22)
            f = F(x, y)
            d.line([(x, y), (x + L * math.cos(ang), y + L * math.sin(ang))], fill=rgba(col, 0.10 * f * k), width=1)
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        img.save(a.out + ".png", optimize=True); return a.out + ".png"
    elif a.kieu.startswith("tam-giac"):
        kieu = "luoi" if a.kieu == "tam-giac-luoi" else "cum"
        cmd = [sys.executable, os.path.join(HERE, "hoa_tiet_tam_giac.py"), "--kieu", kieu, "--w", str(W), "--h", str(H), "--canh", str(s), "--out", a.out, "--do-duc", str(k), "--seed", str(a.seed)]
        if kieu == "luoi": cmd += ["--mau", col, "--vung", "chu-nhat", "--dam-ve", {"tl": "trai", "bl": "trai", "tr": "phai", "br": "phai"}.get(a.dam_ve, a.dam_ve), "--net", str(a.net)]
        else: cmd += ["--goc", a.dam_ve if a.dam_ve in ("tl", "tr", "bl", "br") else "tr", "--bang", a.bang or f"{col}:0.6,{col}:0.35,FFFFFF:0.5"]
        return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()
    else:
        raise SystemExit(f"Không có kiểu {a.kieu}")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    return cv.save(a.out)

def ket_hop(layers, out, W=2400, H=1350, seed=11):
    """Chồng nhiều lớp texture thành một PNG: layers = [{kieu, mau, dam_ve, do_duc, buoc, net, mat_do}, …] (lớp đầu ở dưới)"""
    import tempfile
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tmp = tempfile.mkdtemp()
    for i, L in enumerate(layers):
        a = argparse.Namespace(**{**DEF, "w": W, "h": H, "seed": seed + i * 7, **L, "out": os.path.join(tmp, f"lop{i}")})
        f = ve(a)
        lay = Image.open(f).convert("RGBA")
        if lay.size != (W, H): lay = lay.resize((W, H))
        base = Image.alpha_composite(base, lay)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    base.save(out + ".png", optimize=True)
    return out + ".png"

DEF = dict(kieu="cham", mau="1488DB", bang="", dam_ve="khong", w=2400, h=1350, buoc=60, net=1.5, mat_do=1.0, do_duc=1.0, seed=11, out="hoa_tiet")

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for kk, v in DEF.items(): ap.add_argument("--" + kk.replace("_", "-"), type=type(v), default=v)
    ap.add_argument("--lop", default="", help='chồng nhiều lớp: JSON [{"kieu":"mach","mau":"55EDD9","dam_ve":"br"}, …]')
    a = ap.parse_args(argv)
    if a.lop:
        print(ket_hop(json.loads(a.lop), a.out, a.w, a.h, a.seed))
    else:
        print(ve(a))

if __name__ == "__main__":
    main()
