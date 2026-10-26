#!/usr/bin/env python3
"""kiem_tra_hieu_ung.py — tự kiểm tra hiệu ứng và chuyển trang theo ĐÚNG cách PowerPoint diễn giải danh sách hiệu ứng.

PowerPoint không chạy theo độ trễ ghi trong XML mà theo danh sách trong Animation Pane:
  - On Click      → bắt đầu khi nhấp;
  - With Previous → bắt đầu cùng lúc với mục đứng trước + độ trễ riêng;
  - After Previous→ bắt đầu khi mục đứng trước KẾT THÚC + độ trễ riêng.
Một hiệu ứng lặp "tới hết slide" không bao giờ kết thúc → mục "After Previous" sau nó không bao giờ chạy.

Kiểm tra:
  1. Mô phỏng từng cú nhấp → đối tượng có hiệu ứng mở đầu mà không bao giờ hiện (LỖI); hiệu ứng nhấn mạnh/kết thúc
     không bao giờ chạy (LỖI); thời điểm PowerPoint chạy lệch với thời điểm dự định trong XML (CẢNH BÁO).
  2. Số cú nhấp > 5, hiệu ứng chờ > 2 đối tượng nội dung (CẢNH BÁO).
  3. Morph: có đối tượng chung "!!tên" với slide trước (không có → LỖI), có đổi vị trí/cỡ/xoay/màu (không → CẢNH BÁO
     "morph tĩnh"), đối tượng chung bị gắn hiệu ứng mở đầu (CẢNH BÁO: sẽ biến mất rồi hiện lại sau morph),
     cặp ảnh ↔ hình (CẢNH BÁO).
  4. Chuyển trang cổ điển (lật 3D, cắt, hoà tan, ô cờ, rèm sáo…) (CẢNH BÁO).

Dùng:  python3 kiem_tra_hieu_ung.py Slide.pptx [--json] [--chi-tiet]
Mã thoát 1 khi còn LỖI.
"""
import json, math, re, sys, zipfile
import xml.etree.ElementTree as ET

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
      "p14": "http://schemas.microsoft.com/office/powerpoint/2010/main",
      "p159": "http://schemas.microsoft.com/office/powerpoint/2015/09/main"}
P = "{%s}" % NS["p"]
INF = math.inf
CO_DIEN = {  # tên phần tử chuyển trang → mô tả
    "cut": "cắt", "dissolve": "hoà tan (nhoè hạt)", "randomBar": "sọc ngẫu nhiên", "checker": "ô cờ", "blinds": "rèm sáo",
    "strips": "dải chéo", "wedge": "nêm", "wheel": "bánh xe", "newsflash": "xoay báo", "plus": "dấu cộng", "diamond": "kim cương",
    "random": "ngẫu nhiên", "flip": "lật 3D", "cube": "khối 3D", "gallery": "phòng tranh 3D", "prism": "lăng kính 3D", "box": "hộp 3D",
    "vortex": "xoáy", "ripple": "gợn sóng", "honeycomb": "tổ ong", "glitter": "lấp lánh", "shred": "xé vụn", "switch": "lật đổi 3D",
    "flash": "chớp sáng", "doors": "cửa 3D", "window": "cửa sổ 3D", "ferris": "đu quay", "conveyor": "băng chuyền 3D", "flythrough": "bay xuyên",
    "warp": "bóp méo", "orbit": "quỹ đạo 3D", "rotate": "xoay 3D", "airplane": "máy bay giấy", "crush": "vò giấy", "curtains": "rèm sân khấu 3D",
    "drape": "rèm rủ", "fracture": "vỡ kính", "peelOff": "bóc", "pageCurlDouble": "lật trang", "pageCurlSingle": "lật trang", "wind": "gió", "prestige": "lật 3D",
}
HIEN_DAI = {"fade", "push", "wipe", "cover", "pull", "split", "zoom", "circle", "pan", "reveal", "morph", "none"}


def ms(v, default=0):
    if v is None: return default
    if v == "indefinite": return INF
    try: return int(v)
    except ValueError: return default


def own_delay(ctn):
    c = ctn.find("p:stCondLst/p:cond", NS)
    return ms(c.get("delay")) if c is not None else 0


def behaviour_len(node):
    """độ dài một nút hiệu ứng (preset): lớn nhất của (trễ + thời lượng × lặp) các hành vi con"""
    ctn = node
    rep = ctn.get("repeatCount")
    if rep == "indefinite": return INF
    end = 0
    for c in ctn.iter(P + "cTn"):
        if c is ctn: continue
        d = ms(c.get("dur"), 0)
        if d == INF:
            end = max(end, own_delay(c)); continue
        k = 2 if c.get("autoRev") == "1" else 1
        r = c.get("repeatCount")
        if r == "indefinite": return INF
        r = int(r) / 1000 if r else 1
        end = max(end, own_delay(c) + d * k * r)
    if rep: end *= int(rep) / 1000
    it = ctn.find("p:iterate", NS)
    if it is not None: end *= 1.5   # ước lượng phần lan theo chữ
    return end


def targets(node):
    return sorted({t.get("spid") for t in node.iter(P + "spTgt")})


def resolve(el):
    """thay mc:AlternateContent bằng nhánh Choice (PowerPoint 2016+ đọc nhánh này)"""
    return el


def slide_shapes(root):
    out = {}
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag not in ("sp", "pic", "graphicFrame", "cxnSp"): continue
        nv = el.find(".//p:cNvPr", NS)
        if nv is None: continue
        x = el.find(".//a:xfrm", NS)
        geo = None
        if x is not None and x.find("a:off", NS) is not None:
            o, e = x.find("a:off", NS), x.find("a:ext", NS)
            geo = (int(o.get("x")), int(o.get("y")), int(e.get("cx")), int(e.get("cy")), int(x.get("rot", "0")))
        sp = el.find("p:spPr", NS)
        fill = None
        if sp is not None:
            c = sp.find("a:solidFill/a:srgbClr", NS)
            if c is not None:
                a = c.find("a:alpha", NS)
                fill = (c.get("val"), a.get("val") if a is not None else "100000")
        text = "".join(t.text or "" for t in el.iter("{%s}t" % NS["a"]))
        out.setdefault(nv.get("id"), {"id": nv.get("id"), "name": nv.get("name", ""), "kind": tag, "geo": geo, "fill": fill, "text": text})
    return out


def transition_of(xml):
    m = re.search(r"<p159:morph[^>]*option=\"(\w+)\"", xml)
    if m: return "morph", m.group(1)
    m = re.search(r"<p:transition\b[^>]*>(.*?)</p:transition>", xml, re.S)
    if not m: return None, None
    inner = m.group(1)
    m2 = re.search(r"<(?:p|p14):(\w+)", inner)
    return (m2.group(1) if m2 else "fade"), None


def kiem(path, chi_tiet=False):
    z = zipfile.ZipFile(path)
    names = sorted([n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)], key=lambda n: int(re.findall(r"\d+", n)[-1]))
    # thứ tự trình chiếu theo presentation.xml
    pres = z.read("ppt/presentation.xml").decode("utf8")
    rels = z.read("ppt/_rels/presentation.xml.rels").decode("utf8")
    rid2t = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels)) | {a: b for b, a in re.findall(r'Target="([^"]+)"[^>]*Id="(rId\d+)"', rels)}
    order = [("ppt/" + rid2t[r]).replace("ppt//", "ppt/") for r in re.findall(r'<p:sldId [^>]*r:id="(rId\d+)"', pres) if r in rid2t]
    order = [o for o in order if o in names] or names
    out = []
    add = lambda lv, s, msg: out.append({"muc": lv, "slide": s, "noi_dung": msg})
    prev_shapes = None
    for idx, n in enumerate(order, 1):
        xml = z.read(n).decode("utf8")
        root = ET.fromstring(xml)
        shapes = slide_shapes(root)
        byid = {k: v for k, v in shapes.items()}
        nm = lambda sp: (byid.get(sp) or {}).get("name", "#" + sp)
        tr, opt = transition_of(xml)

        # ---------- 4. chuyển trang cổ điển
        if tr and tr not in HIEN_DAI:
            add("CẢNH BÁO", idx, f"chuyển trang cổ điển '{tr}' ({CO_DIEN.get(tr, 'kiểu cũ')}) — dùng Morph, push, pan, wipe, reveal hoặc fade")

        # ---------- 3. morph
        entr_names = set()
        timing = root.find("p:timing", NS)
        if timing is not None:
            for c in timing.iter(P + "cTn"):
                if c.get("presetClass") == "entr":
                    for sp in targets(c): entr_names.add(nm(sp))
        if tr == "morph":
            if prev_shapes is None:
                add("CẢNH BÁO", idx, "Morph ở slide đầu tiên không có tác dụng")
            else:
                pa = {v["name"]: v for v in prev_shapes.values() if v["name"].startswith("!!")}
                pb = {v["name"]: v for v in shapes.values() if v["name"].startswith("!!")}
                chung = sorted(set(pa) & set(pb))
                if not chung:
                    add("LỖI", idx, "Morph nhưng không có đối tượng chung '!!tên' với slide trước — chỉ còn mờ chéo; thêm cảnh morph (chuyen_trang.js)")
                else:
                    dong = [k for k in chung if pa[k]["geo"] != pb[k]["geo"] or pa[k]["fill"] != pb[k]["fill"] or pa[k]["text"] != pb[k]["text"]]
                    if not dong:
                        add("CẢNH BÁO", idx, f"morph tĩnh: {len(chung)} đối tượng chung nhưng không đổi vị trí/cỡ/màu — đổi tư thế để chuyển động")
                    for k in chung:
                        if pa[k]["kind"] != pb[k]["kind"]:
                            add("CẢNH BÁO", idx, f"'{k}' là {pa[k]['kind']} ở slide trước nhưng {pb[k]['kind']} ở slide này — morph chỉ mờ chéo")
                        if k in entr_names:
                            add("CẢNH BÁO", idx, f"'{k}' vừa morph vừa có hiệu ứng mở đầu — sẽ biến mất rồi hiện lại; bỏ hiệu ứng mở đầu của nó")
                    if chi_tiet:
                        add("THÔNG TIN", idx, f"morph ({opt}): {len(chung)} đối tượng chung, {len(dong)} chuyển động — {', '.join(chung[:8])}")

        # ---------- 1–2. mô phỏng hiệu ứng như PowerPoint
        if timing is not None:
            main = timing.find(".//p:cTn[@nodeType='mainSeq']", NS)
            groups = main.findall("p:childTnLst/p:par/p:cTn", NS) if main is not None else []
            n_click, n_idle = 0, set()
            entered, shown_never = set(), []
            for gi, g in enumerate(groups):
                auto = any(c.get("evt") == "onBegin" for c in g.findall("p:stCondLst/p:cond", NS))
                if not auto: n_click += 1
                items = []
                for par in g.findall("p:childTnLst/p:par/p:cTn", NS):
                    pstart = own_delay(par)
                    for eff in par.findall("p:childTnLst/p:par/p:cTn", NS):
                        if eff.get("presetClass") is None: continue
                        items.append({"node": eff, "type": eff.get("nodeType"), "delay": own_delay(eff), "par": pstart,
                                      "len": behaviour_len(eff), "cls": eff.get("presetClass"), "sp": targets(eff),
                                      "idle": eff.get("repeatCount") == "indefinite"})
                # neo = thời điểm bắt đầu của mục Click/After gần nhất; With Previous = neo + trễ riêng;
                # After Previous = khi mọi mục từ neo trước đó kết thúc (∞ nếu có hiệu ứng lặp vô hạn)
                anchor, seg_end = 0, 0
                for i, it in enumerate(items):
                    if it["type"] == "afterEffect" and i > 0: anchor = seg_end; seg_end = anchor
                    elif it["type"] != "withEffect" or i == 0: anchor = 0
                    s = anchor + it["delay"]
                    e = s + it["len"]
                    seg_end = max(seg_end, e)
                    xml_s = it["par"] + it["delay"]
                    ten = ", ".join(nm(sp) for sp in it["sp"])
                    if it["idle"] and it["cls"] != "path" and not any(nm(sp).startswith(("nen", "den", "hat", "vong", "!!")) for sp in it["sp"]):
                        n_idle.update(it["sp"])
                    if s == INF:
                        what = {"entr": "không bao giờ hiện", "exit": "không bao giờ rời đi", "emph": "hiệu ứng nhấn mạnh/chờ không bao giờ chạy", "path": "chuyển động không bao giờ chạy"}[it["cls"]]
                        add("LỖI", idx, f"'{ten}' {what} — đứng sau một hiệu ứng lặp vô hạn trong danh sách với kiểu After Previous (cú nhấp {gi + 1})")
                    elif abs(s - xml_s) > 60 and s != INF and xml_s != INF:
                        add("CẢNH BÁO", idx, f"'{ten}': PowerPoint chạy lúc {s / 1000:.2f}s nhưng XML dự định {xml_s / 1000:.2f}s (cú nhấp {gi + 1})")
                    if it["cls"] == "entr" and s != INF: entered.update(it["sp"])
                    if chi_tiet:
                        add("THÔNG TIN", idx, f"nhấp {gi + 1}{' (tự chạy)' if auto else ''}: {it['cls']:<5} {ten[:30]:<30} {s / 1000 if s != INF else -1:6.2f}s → {'∞' if e == INF else f'{e / 1000:.2f}s'}")
            if n_click > 5: add("CẢNH BÁO", idx, f"{n_click} cú nhấp (khuyến nghị ≤ 5)")
            if len(n_idle) > 2: add("CẢNH BÁO", idx, f"{len(n_idle)} đối tượng nội dung có hiệu ứng chờ (khuyến nghị ≤ 2)")
        prev_shapes = shapes
    return out


def main():
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    out = kiem(a[0], chi_tiet="--chi-tiet" in a)
    if "--json" in a:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        print(f"{a[0]}: kiểm tra hiệu ứng và chuyển trang (mô phỏng cách PowerPoint chạy danh sách hiệu ứng)\n")
        for lv in ("LỖI", "CẢNH BÁO", "THÔNG TIN"):
            rows = [o for o in out if o["muc"] == lv]
            if lv == "THÔNG TIN" and not rows: continue
            print(f"{lv} ({len(rows)})")
            for o in rows: print(f"  [slide {o['slide']}] {o['noi_dung']}")
            print()
    sys.exit(1 if any(o["muc"] == "LỖI" for o in out) else 0)


if __name__ == "__main__":
    main()
