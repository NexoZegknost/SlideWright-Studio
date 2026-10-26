#!/usr/bin/env python3
"""hoa_tiet_trong_dong.py — Tạo họa tiết vòng tròn đồng tâm kiểu mặt trống đồng (hình học, tự vẽ, không bản quyền).
Xuất 3 bản PNG nền trong suốt: <ten>.png (đậm), <ten>_dim.png (45% – nền tối sau chữ), <ten>_faint.png (35% – góc slide sáng).
Dùng: python3 hoa_tiet_trong_dong.py --color E3B35B --out trong_dong
Gợi ý đặt: slide bìa/chuyển phần lệch phải, tràn một phần ra mép; slide nội dung để bản _faint nhỏ ở góc trên phải (trên layout).
"""
import argparse, math
from PIL import Image, ImageDraw
ap = argparse.ArgumentParser(); ap.add_argument("--color", default="E3B35B"); ap.add_argument("--out", default="trong_dong"); ap.add_argument("--size", type=int, default=2000)
a = ap.parse_args()
N = a.size; c = N / 2; k = N / 2000; G = tuple(int(a.color[i:i + 2], 16) for i in (0, 2, 4))
im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
ring = lambda r, w, al: d.ellipse([c - r * k, c - r * k, c + r * k, c + r * k], outline=G + (al,), width=max(1, int(w * k)))
pts = [(c + (230 if i % 2 == 0 else 70) * k * math.cos(math.pi * i / 14 - math.pi / 2), c + (230 if i % 2 == 0 else 70) * k * math.sin(math.pi * i / 14 - math.pi / 2)) for i in range(28)]
d.polygon(pts, fill=G + (150,)); ring(260, 10, 150); ring(300, 4, 120)
for i in range(48):
    t = 2 * math.pi * i / 48
    d.polygon([(c + 310 * k * math.cos(t - .05), c + 310 * k * math.sin(t - .05)), (c + 310 * k * math.cos(t + .05), c + 310 * k * math.sin(t + .05)), (c + 380 * k * math.cos(t), c + 380 * k * math.sin(t))], fill=G + (110,))
ring(400, 6, 130); ring(430, 3, 100)
for i in range(72):
    t = 2 * math.pi * i / 72; x, y = c + 480 * k * math.cos(t), c + 480 * k * math.sin(t); d.ellipse([x - 9 * k, y - 9 * k, x + 9 * k, y + 9 * k], fill=G + (120,))
ring(530, 4, 110)
for i in range(120):
    t = 2 * math.pi * i / 120; d.line([(c + 560 * k * math.cos(t), c + 560 * k * math.sin(t)), (c + 640 * k * math.cos(t), c + 640 * k * math.sin(t))], fill=G + (90,), width=max(1, int(5 * k)))
ring(670, 8, 120); ring(710, 3, 90)
d.line([(c + (760 if i % 2 == 0 else 800) * k * math.cos(2 * math.pi * i / 180), c + (760 if i % 2 == 0 else 800) * k * math.sin(2 * math.pi * i / 180)) for i in range(181)], fill=G + (100,), width=max(1, int(5 * k)))
ring(850, 10, 110); ring(900, 3, 80)
im.save(f"{a.out}.png")
for suf, f in (("_dim", .45), ("_faint", .35)):
    x = im.copy(); x.putalpha(im.split()[3].point(lambda v, f=f: int(v * f))); x.save(f"{a.out}{suf}.png")
print("Đã tạo", a.out + ".png, _dim.png, _faint.png")
