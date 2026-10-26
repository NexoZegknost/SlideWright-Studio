// Tranh minh hoạ vẽ bằng SVG (tông rượu vang – đồng – kem), xuất PNG bằng sharp
const sharp = require("sharp"), fs = require("fs");
const OUT = process.cwd() + "/anh/"; require("fs").mkdirSync(OUT, { recursive: true });
let seed = 5; const rnd = () => ((seed = (seed * 9301 + 49297) % 233280) / 233280);

function curtain(x0, w, h, flip) {
  // rèm nhung: dải nếp gấp lặp + mép dưới vén cong
  const id = "cg" + (flip ? "R" : "L");
  const path = flip
    ? `M ${x0 + w} 0 L ${x0} 0 C ${x0 + w * 0.15} ${h * 0.35}, ${x0 + w * 0.55} ${h * 0.55}, ${x0 + w * 0.42} ${h} L ${x0 + w} ${h} Z`
    : `M ${x0} 0 L ${x0 + w} 0 C ${x0 + w * 0.85} ${h * 0.35}, ${x0 + w * 0.45} ${h * 0.55}, ${x0 + w * 0.58} ${h} L ${x0} ${h} Z`;
  return `<linearGradient id="${id}" x1="0" y1="0" x2="${w / 7}" y2="0" gradientUnits="userSpaceOnUse" spreadMethod="reflect">
    <stop offset="0" stop-color="#4A0A10"/><stop offset="0.55" stop-color="#8E1E28"/><stop offset="1" stop-color="#B0353C"/></linearGradient>
    <path d="${path}" fill="url(#${id})"/>
    <path d="${path}" fill="url(#shadeV)"/>`;
}
function stage(W = 2400, H = 1350) {
  const fy = H * 0.74, vx = W / 2, vy = H * 0.42;
  let planks = "";
  for (let i = -14; i <= 14; i++) planks += `<line x1="${vx + i * 26}" y1="${fy}" x2="${vx + i * 210}" y2="${H}" stroke="#1E0E08" stroke-width="3" opacity="0.55"/>`;
  for (let k = 1; k < 5; k++) { const y = fy + (H - fy) * (k / 5) ** 1.6; planks += `<line x1="0" y1="${y}" x2="${W}" y2="${y}" stroke="#1E0E08" stroke-width="2" opacity="0.35"/>`; }
  let swags = "";
  for (let i = 0; i < 6; i++) { const x = (W / 6) * i; swags += `<path d="M ${x} 0 L ${x + W / 6} 0 L ${x + W / 6} 120 Q ${x + W / 12} 230 ${x} 120 Z" fill="url(#swag)"/>`; }
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><defs>
    <radialGradient id="bg" cx="0.5" cy="0.35" r="0.75"><stop offset="0" stop-color="#5E1419"/><stop offset="0.6" stop-color="#330709"/><stop offset="1" stop-color="#1A0305"/></radialGradient>
    <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5A3422"/><stop offset="1" stop-color="#24120B"/></linearGradient>
    <linearGradient id="shadeV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0.35"/><stop offset="0.5" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.45"/></linearGradient>
    <linearGradient id="swag" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5A0E15"/><stop offset="1" stop-color="#9A262F"/></linearGradient>
    <radialGradient id="pool" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#F6E6C7" stop-opacity="0.22"/><stop offset="1" stop-color="#F6E6C7" stop-opacity="0"/></radialGradient>
    </defs>
    <rect width="${W}" height="${H}" fill="url(#bg)"/>
    <polygon points="0,${fy} ${W},${fy} ${W},${H} 0,${H}" fill="url(#floor)"/>${planks}
    <rect x="0" y="${fy - 6}" width="${W}" height="10" fill="#B97341" opacity="0.7"/>
    <ellipse cx="${W * 0.62}" cy="${fy + 120}" rx="${W * 0.22}" ry="90" fill="url(#pool)"/>
    ${curtain(0, W * 0.2, H, false)}${curtain(W * 0.8, W * 0.2, H, true)}
    ${swags}<rect x="0" y="0" width="${W}" height="26" fill="#B97341" opacity="0.8"/></svg>`;
}
function tshirt(W = 1227, H = 1500) {
  const cx = W / 2, top = H * 0.2, sw = W * 0.62;
  const shirt = `M ${cx - sw * 0.22} ${top} Q ${cx} ${top + 90} ${cx + sw * 0.22} ${top}
    L ${cx + sw * 0.5} ${top + 60} L ${cx + sw * 0.72} ${top + 330} L ${cx + sw * 0.48} ${top + 420} L ${cx + sw * 0.4} ${top + 300}
    L ${cx + sw * 0.4} ${top + 930} Q ${cx} ${top + 965} ${cx - sw * 0.4} ${top + 930} L ${cx - sw * 0.4} ${top + 300}
    L ${cx - sw * 0.48} ${top + 420} L ${cx - sw * 0.72} ${top + 330} L ${cx - sw * 0.5} ${top + 60} Z`;
  const py = top + 470, r = 175;
  let rays = "";
  for (let i = 0; i < 18; i++) { const a = (i / 18) * Math.PI * 2; rays += `<line x1="${cx + Math.cos(a) * (r + 18)}" y1="${py + Math.sin(a) * (r + 18)}" x2="${cx + Math.cos(a) * (r + 62)}" y2="${py + Math.sin(a) * (r + 62)}" stroke="#B97341" stroke-width="10" stroke-linecap="round"/>`; }
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><defs>
    <radialGradient id="bg" cx="0.5" cy="0.42" r="0.7"><stop offset="0" stop-color="#FBF3E4"/><stop offset="1" stop-color="#EAD9BF"/></radialGradient>
    <linearGradient id="cloth" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F3DFA6"/><stop offset="1" stop-color="#E2C27E"/></linearGradient>
    <filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="22"/></filter>
    <clipPath id="cp"><circle cx="${cx}" cy="${py}" r="${r}"/></clipPath></defs>
    <rect width="${W}" height="${H}" fill="url(#bg)"/>
    <path d="${shirt}" fill="#6D5352" opacity="0.35" filter="url(#sh)" transform="translate(18 34)"/>
    <path d="${shirt}" fill="url(#cloth)"/>
    <path d="M ${cx - sw * 0.22} ${top} Q ${cx} ${top + 90} ${cx + sw * 0.22} ${top}" fill="none" stroke="#C9A35E" stroke-width="16"/>
    <line x1="${cx - sw * 0.4}" y1="${top + 300}" x2="${cx - sw * 0.4}" y2="${top + 380}" stroke="#C9A35E" stroke-width="5"/>
    <line x1="${cx + sw * 0.4}" y1="${top + 300}" x2="${cx + sw * 0.4}" y2="${top + 380}" stroke="#C9A35E" stroke-width="5"/>
    ${rays}<circle cx="${cx}" cy="${py}" r="${r}" fill="#551015"/>
    <g clip-path="url(#cp)">
      <circle cx="${cx}" cy="${py + 30}" r="${r * 0.9}" fill="#7A1E26"/>
      <path d="M ${cx - 95} ${py - 30} Q ${cx - 110} ${py - 150} ${cx} ${py - 150} Q ${cx + 115} ${py - 150} ${cx + 100} ${py - 25} Q ${cx + 60} ${py - 95} ${cx} ${py - 92} Q ${cx - 60} ${py - 95} ${cx - 95} ${py - 30} Z" fill="#2A0709"/>
      <ellipse cx="${cx}" cy="${py - 20}" rx="72" ry="88" fill="#E9C9A0"/>
      <path d="M ${cx - 125} ${py + 210} Q ${cx - 120} ${py + 80} ${cx} ${py + 78} Q ${cx + 120} ${py + 80} ${cx + 125} ${py + 210} Z" fill="#2A0709"/>
      <rect x="${cx + 70}" y="${py + 20}" width="22" height="70" rx="8" fill="#B97341" transform="rotate(-25 ${cx + 80} ${py + 55})"/>
      <circle cx="${cx + 62}" cy="${py + 8}" r="22" fill="#F6E6C7"/>
      <path d="M ${cx - 30} ${py + 15} Q ${cx} ${py + 38} ${cx + 30} ${py + 15}" fill="none" stroke="#551015" stroke-width="7" stroke-linecap="round"/>
      <circle cx="${cx - 26}" cy="${py - 30}" r="7" fill="#551015"/><circle cx="${cx + 26}" cy="${py - 30}" r="7" fill="#551015"/>
    </g>
    <circle cx="${cx}" cy="${py}" r="${r}" fill="none" stroke="#F6E6C7" stroke-width="8"/></svg>`;
}
function audience(W = 2240, H = 1592) {
  let people = "", glows = "";
  const rows = [{ y: H * 0.62, s: 0.62, n: 11 }, { y: H * 0.8, s: 0.82, n: 8 }, { y: H * 1.0, s: 1.05, n: 6 }];
  rows.forEach((r, ri) => {
    for (let i = 0; i < r.n; i++) {
      const x = (W / r.n) * (i + 0.5) + (rnd() - 0.5) * 60 + (ri % 2 ? 40 : 0), s = r.s * (0.92 + rnd() * 0.16);
      const hr = 70 * s, by = r.y;
      const phone = rnd() < 0.55;
      if (phone) {
        const px = x + (rnd() < 0.5 ? -1 : 1) * 30 * s, pyy = by - 150 * s;
        glows += `<ellipse cx="${px}" cy="${pyy - 30 * s}" rx="${120 * s}" ry="${95 * s}" fill="url(#glow)"/>`;
        people += `<rect x="${px - 16 * s}" y="${pyy - 24 * s}" width="${32 * s}" height="${50 * s}" rx="${6 * s}" fill="#F6E6C7" opacity="0.95"/>`;
      }
      const tilt = phone ? 14 : (rnd() - 0.5) * 10;
      people = `<g transform="rotate(${tilt} ${x} ${by - 200 * s})"><ellipse cx="${x}" cy="${by - 245 * s}" rx="${hr * 0.86}" ry="${hr}" fill="#1C0406"/></g>
        <path d="M ${x - 150 * s} ${by + 40} Q ${x - 145 * s} ${by - 170 * s} ${x} ${by - 175 * s} Q ${x + 145 * s} ${by - 170 * s} ${x + 150 * s} ${by + 40} Z" fill="#240608"/>` + people;
    }
  });
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7A1E26"/><stop offset="0.45" stop-color="#4A0C11"/><stop offset="1" stop-color="#1E0406"/></linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#F6E6C7" stop-opacity="0.55"/><stop offset="1" stop-color="#F6E6C7" stop-opacity="0"/></radialGradient>
    <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6E6C7" stop-opacity="0.5"/><stop offset="1" stop-color="#F6E6C7" stop-opacity="0.05"/></linearGradient>
    <filter id="b"><feGaussianBlur stdDeviation="14"/></filter></defs>
    <rect width="${W}" height="${H}" fill="url(#bg)"/>
    <rect x="0" y="${H * 0.36}" width="${W}" height="10" fill="#B97341" opacity="0.6"/>
    <polygon points="${W * 0.47},0 ${W * 0.53},0 ${W * 0.6},${H * 0.36} ${W * 0.4},${H * 0.36}" fill="url(#beam)" filter="url(#b)"/>
    <ellipse cx="${W / 2}" cy="${H * 0.355}" rx="${W * 0.1}" ry="18" fill="#F6E6C7" opacity="0.45" filter="url(#b)"/>
    <ellipse cx="${W / 2}" cy="${H * 0.27}" rx="22" ry="26" fill="#1C0406"/>
    <path d="M ${W / 2 - 40} ${H * 0.355} L ${W / 2 - 34} ${H * 0.29} Q ${W / 2} ${H * 0.28} ${W / 2 + 34} ${H * 0.29} L ${W / 2 + 40} ${H * 0.355} Z" fill="#1C0406"/>
    ${glows}${people}</svg>`;
}
(async () => {
  await sharp(Buffer.from(stage())).png().toFile(OUT + "san-khau.png");
  await sharp(Buffer.from(tshirt())).png().toFile(OUT + "chiec-ao.png");
  await sharp(Buffer.from(audience())).png().toFile(OUT + "khan-gia.png");
  console.log("ok");
})();
