// Mẫu minh hoạ đủ bốn nhóm hiệu ứng (mở đầu, nhấn mạnh, chờ, kết thúc): "Hiệu ứng ánh đèn sân khấu" — tâm lý học xã hội
// Chạy (trong thư mục làm việc, đã npm install như quy-trinh-pptx.md):
//   node illus.js && node deck.js      (illus.js vẽ tranh minh hoạ SVG → PNG vào ./anh)
const LIB = require("path").join(__dirname, "..", "..", "scripts") + "/";
const { L, setScale, setCurrent, W, H, M, CW } = require(LIB + "layouts.js");
const DH = require(LIB + "dinh_huong.js");
const HU = require(LIB + "hieu_ung.js");
const MS = require(LIB + "makeslides.js");
const pptxgen = require("pptxgenjs");
const A = process.cwd() + "/anh/";   // tranh do illus.js vẽ

(async () => {
  // 1) định hướng: đề tài → lĩnh vực KHXH → bảng màu rượu vang – đồng – kem (rèm nhung sân khấu), Lora + Montserrat
  const kq = DH.dinhHuong({ chuDe: "Hiệu ứng ánh đèn sân khấu (spotlight effect) trong tâm lý học xã hội", boiCanh: "hoc-sinh-sinh-vien" });
  const pa = kq.phuongAn[0];
  const S = DH.apDung(pa); setCurrent(S); setScale(24);
  const tex = DH.taoTexture(pa, process.cwd() + "/tex");
  const den = await HU.anhSang(A + "den-chum.png", { mau: S.c.accentOnDark, hinh: "chum", manh: 0.42, w: 900, h: 1100 });
  const C = S.c;

  const pres = new pptxgen(); pres.layout = "LAYOUT_16x9"; pres.title = "Hiệu ứng ánh đèn sân khấu";
  const PLAN = {}; let n = 0;
  const add = (r, extra = {}) => { PLAN[++n] = { transition: "fade", steps: r.steps, autoFirst: r.autoFirst, idle: r.idle, ket: r.ket, ...extra }; return r; };
  // lớp sân khấu dùng chung cho bìa và kết: tranh sân khấu + đèn rọi quét chậm + bụi sáng lơ lửng trong luồng đèn
  const sanKhau = (sl, seed) => {
    sl.addImage({ path: A + "san-khau.png", x: 0, y: 0, w: W, h: H, objectName: "nen", altText: "hoa-tiet:san-khau (tranh nền tối, chữ đặt trên mảng tường trơn)" });
    return [
      HU.denSanKhau(sl, den, { x: 1.7, y: -0.15, w: 3.6, h: 4.4, dx: 2.9, period: 18000 }),
      ...HU.hatBui(sl, { so: 14, mau: C.accentOnDark, vung: { x: 2.0, y: 0.6, w: 6.0, h: 3.4 }, co: [0.04, 0.1], trong: [40, 70], seed }),
    ];
  };

  // ---- 1. Bìa (dựng tay trên lớp sân khấu)
  {
    const sl = pres.addSlide(); sl.background = { color: C.dark };
    const cho = sanKhau(sl, 3);
    sl.addText("TÂM LÝ HỌC XÃ HỘI", { objectName: "kicker", x: M, y: 1.0, w: CW, h: 0.4, fontFace: S.body, bold: true, fontSize: 16, charSpacing: 3, color: C.accentOnDark, align: "center", margin: 0 });
    sl.addText("Hiệu ứng\nánh đèn sân khấu", { objectName: "title", x: 1.2, y: 1.45, w: W - 2.4, h: 1.9, fontFace: S.head, bold: true, fontSize: 50, color: "FFFFFF", align: "center", valign: "middle", margin: 0, lineSpacingMultiple: 0.95 });
    sl.addText("Vì sao ta tưởng cả phòng đang nhìn mình", { objectName: "sub", x: 1.2, y: 3.45, w: W - 2.4, h: 0.5, fontFace: S.body, fontSize: 24, color: C.accentOnDark, align: "center", margin: 0 });
    sl.addNotes("Mở đầu: hỏi lớp đã bao giờ thấy ngượng vì nghĩ ai cũng đang nhìn mình chưa.");
    add({ steps: [[{ n: "kicker", eff: "fade", dur: 700 }, { n: "title", eff: "riseWords", start: "after", dur: 700 }, { n: "sub", eff: "floatUp", start: "after" }]], autoFirst: true, idle: cho }, { transition: "fadeBlack" });
  }

  // ---- 2. Câu hỏi mở — nền texture trôi chậm, câu hỏi nổi khẽ trong lúc chờ lớp trả lời
  {
    const r = L.hoiDap(pres, S, { kicker: "Thử nhớ lại", question: "Lần trước có bạn vấp ngã,\nbạn còn nhớ đó là ai không?",
      answer: "Người vấp ngã thì nhớ rất lâu.", nen: DH.nen(tex, "nhan-manh", 0), nenDong: { le: 0.35, period: 26000 },
      notes: "Để lớp trả lời vài giây rồi mới nhấp hiện lời đáp." }, { dark: true });
    r.steps = [[{ n: "kicker", eff: "fade" }, { n: "question", eff: "riseWords", start: "after", dur: 600 }], ...r.steps];
    r.autoFirst = true;
    r.idle.push({ n: "question", eff: "chuNoi", batDau: 0, period: 6500 });
    add(r);
  }

  // ---- 3. Định nghĩa
  {
    const r = L.tuyenBo(pres, S, { statement: "Ta luôn nghĩ người khác\nđể ý mình nhiều hơn thực tế", highlight: "để ý mình nhiều hơn thực tế",
      by: "Gilovich, Medvec & Savitsky, 2000", nen: DH.nen(tex, "noi-dung", 1) });
    r.steps = [[{ n: "statement", eff: "expand", dur: 900 }, { n: "by", eff: "fade", start: "after" }]];
    r.idle = [{ n: "statement", eff: "gachChan", period: 11000, dur: 1800 }];
    add(r);
  }

  // ---- 4. Thí nghiệm
  {
    const r = L.anhChu(pres, S, { img: A + "chiec-ao.png", kicker: "Thí nghiệm, 2000", title: "Chiếc áo\ngây bối rối",
      bullets: ["Mặc áo in hình ca sĩ lỗi thời", "Vào phòng, đoán số người để ý"],
      nen: DH.nen(tex, "noi-dung", 2), notes: "Thí nghiệm của Gilovich và cộng sự ở Đại học Cornell; chiếc áo được chọn vì đa số sinh viên thấy ngại khi mặc." });
    r.steps = [[{ n: "img", eff: "fade", dur: 900 }, { n: "kicker", eff: "fade", start: "after" }, { n: "title", eff: "floatUp", start: "with" }], [{ n: "body", eff: "floatUp", byPara: true }]];
    r.autoFirst = true;
    r.idle = [{ n: "img", eff: "tho", batDau: 0, ti: 103, period: 14000 }];
    add(r);
  }

  // ---- 5. Kết quả — đoán trước, thực tế sau; cú nhấp cuối làm nhạt con số đoán (nhấn mạnh)
  {
    const r = L.thangSo(pres, S, { title: "Người mặc đoán gấp đôi thực tế",
      items: [{ value: "23%", label: "thật sự nhớ ra chiếc áo" }, { value: "46%", label: "người mặc tự đoán" }], nen: DH.nen(tex, "chia-phan", 0) }, { dark: true });
    r.slide.addText("Nguồn: Gilovich, Medvec & Savitsky (2000)", { objectName: "source", x: M, y: 5.05, w: CW, h: 0.35, fontFace: S.body, fontSize: 16, color: "D9C6BE", margin: 0 });
    r.steps = [
      [{ n: "v1", eff: "fade" }, { n: "b1", eff: "wipe", dir: "left" }, { n: "l1", eff: "fade", start: "after", dur: 300 }],
      [{ n: "v0", eff: "zoom", dur: 700 }, { n: "b0", eff: "wipe", dir: "left" }, { n: "l0", eff: "fade", start: "after", dur: 300 }, { n: "source", eff: "fade", start: "with" }],
      [{ n: "v1", eff: "dim", mau: "9A6A6C" }, { n: "l1", eff: "dim", mau: "9A6A6C" }, { n: "v0", eff: "pulse", start: "after", ti: 112 }],
    ];
    r.idle = [{ n: "v0", eff: "nhip", period: 9000 }];
    add(r);
  }

  // ---- 6. Cơ chế
  {
    const r = L.baThe(pres, S, { title: "Ánh đèn bật lên từ bên trong", highlight: 0, nen: DH.nen(tex, "noi-dung", 1), cards: [
      { mark: "Neo", head: "Tự soi mình", text: "Lấy cảm giác của ta làm mốc" },
      { mark: "Bận", head: "Ai cũng bận", text: "Họ đang mải lo chuyện mình" },
      { mark: "Lộ", head: "Tưởng bị lộ", text: "Nỗi lo ít hiện ra hơn ta nghĩ" }] });
    add(r);
  }

  // ---- 7. Góc nhìn khán giả
  {
    const r = L.anhLopKhoi(pres, S, { img: A + "khan-gia.png", kicker: "Ở hàng ghế khán giả", title: "Mỗi người\nmột ngọn đèn",
      text: "Họ còn đang bận lo phần mình", nen: DH.nen(tex, "noi-dung", 2) });
    r.idle = [{ n: "img", eff: "tho", ti: 103, period: 16000, batDau: "vao" }];
    add(r, { transition: ["push", "u"] });
  }

  // ---- 8. Hạ bớt ánh đèn — mỗi bước mới hiện thì bước trước nhạt đi
  {
    const r = L.buocDoc(pres, S, { title: "Hạ bớt\nánh đèn", steps: [
      { head: "Ai đang nhìn?", text: "Đếm người, đừng đoán" },
      { head: "Đổi chỗ ngồi", text: "Nhớ lúc mình ngồi xem" },
      { head: "Chờ một nhịp", text: "Ngượng sẽ nhạt dần" },
      { head: "Nói tiếp", text: "Người nghe cần ý của bạn" }] });
    r.steps = r.steps.map((g, i) => (i ? [...g, { n: `st${i - 1}`, eff: "dim", mau: "B8A9A4", start: "with" }, { n: `sn${i - 1}`, eff: "dim", mau: "B8A9A4", start: "with" }] : g));
    r.idle = [{ n: "title", eff: "chuNoi", batDau: "vao", delay: 2500, period: 8000 }];
    add(r);
  }

  // ---- 9. Kết — sân khấu, đèn quét, sóng chữ; cú nhấp cuối hạ màn (hiệu ứng kết thúc)
  {
    const r = L.ketThuc(pres, S, { big: "Không ai soi bạn\nkỹ bằng chính bạn", sub: "Hẹn gặp ở phần thảo luận", truoc: (sl) => sanKhau(sl, 9) });
    r.idle = r.idle.filter((e) => e.n !== "big");
    r.idle.push({ n: "big", eff: "songChu", period: 7000 });
    r.ket = [{ n: "big", eff: "sinkOut", dur: 900 }, { n: "sub", eff: "fadeOut", start: "with" }, { n: "den", eff: "fadeOut", start: "with", dur: 1500 }];
    add(r, { transition: "fadeBlack" });
  }

  let buf = await pres.write({ outputType: "nodebuffer" });
  buf = await MS.applyEffects(buf, PLAN);
  buf = await MS.embedFonts(buf, [S.head, S.body]);
  const out = await MS.save(buf, process.cwd() + "/HieuUng_AnhDenSanKhau");
  console.log(out.join("\n"));
})().catch((e) => { console.error(e); process.exit(1); });
