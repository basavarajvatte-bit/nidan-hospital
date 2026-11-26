// Vatte Hospital OS — UPI QR code (no outside library; works offline).
// QR encoder: byte mode, error-correction level M, versions 1–40, best mask chosen (based on the public QR standard / Nayuki's method).
// upiQR() draws a QR for "upi://pay?..." so any UPI app (GPay, PhonePe, Paytm, BHIM) opens with the amount and bill number filled in.

const ECC_PER_BLOCK = [-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28, 26, 26, 26, 26, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28];
const NUM_BLOCKS = [-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5, 5, 8, 9, 9, 10, 10, 11, 13, 14, 16, 17, 17, 18, 20, 21, 23, 25, 26, 28, 29, 31, 33, 35, 37, 38, 40, 43, 45, 47, 49];
const ECL_BITS = 0; // level M = 0b00 in format bits

function rawModules(ver) {
  let r = (16 * ver + 128) * ver + 64;
  if (ver >= 2) { const n = Math.floor(ver / 7) + 2; r -= (25 * n - 10) * n - 55; if (ver >= 7) r -= 36; }
  return r;
}
const dataCodewords = ver => Math.floor(rawModules(ver) / 8) - ECC_PER_BLOCK[ver] * NUM_BLOCKS[ver];

function rsDivisor(deg) {
  const r = new Array(deg).fill(0); r[deg - 1] = 1; let root = 1;
  for (let i = 0; i < deg; i++) {
    for (let j = 0; j < r.length; j++) { r[j] = rsMul(r[j], root); if (j + 1 < r.length) r[j] ^= r[j + 1]; }
    root = rsMul(root, 2);
  }
  return r;
}
function rsRemainder(data, div) {
  const r = div.map(() => 0);
  for (const b of data) { const f = b ^ r.shift(); r.push(0); div.forEach((c, i) => { r[i] ^= rsMul(c, f); }); }
  return r;
}
function rsMul(x, y) {
  let z = 0;
  for (let i = 7; i >= 0; i--) { z = (z << 1) ^ ((z >>> 7) * 0x11D); z ^= ((y >>> i) & 1) * x; }
  return z;
}

export function qrMatrix(text) {
  const bytes = Array.from(new TextEncoder().encode(text));
  let ver = 1;
  for (; ver <= 40; ver++) {
    const cap = dataCodewords(ver) * 8, ccBits = ver <= 9 ? 8 : 16;
    if (4 + ccBits + bytes.length * 8 <= cap) break;
  }
  if (ver > 40) throw new Error("Text QR ke liye bahut lamba hai");
  // ---- bit stream
  const bits = [];
  const put = (v, n) => { for (let i = n - 1; i >= 0; i--) bits.push((v >>> i) & 1); };
  put(4, 4); put(bytes.length, ver <= 9 ? 8 : 16); bytes.forEach(b => put(b, 8));
  const capBits = dataCodewords(ver) * 8;
  put(0, Math.min(4, capBits - bits.length));
  put(0, (8 - bits.length % 8) % 8);
  for (let pad = 0xEC; bits.length < capBits; pad ^= 0xEC ^ 0x11) put(pad, 8);
  const data = [];
  for (let i = 0; i < bits.length; i += 8) data.push(bits.slice(i, i + 8).reduce((a, b) => (a << 1) | b, 0));
  // ---- error correction + interleave
  const nb = NUM_BLOCKS[ver], ecl = ECC_PER_BLOCK[ver], raw = Math.floor(rawModules(ver) / 8);
  const nShort = nb - raw % nb, shortLen = Math.floor(raw / nb);
  const div = rsDivisor(ecl), blocks = [];
  for (let i = 0, k = 0; i < nb; i++) {
    const d = data.slice(k, k + shortLen - ecl + (i < nShort ? 0 : 1)); k += d.length;
    const e = rsRemainder(d, div);
    if (i < nShort) d.push(0);
    blocks.push(d.concat(e));
  }
  const all = [];
  for (let i = 0; i < blocks[0].length; i++) blocks.forEach((b, j) => { if (i !== shortLen - ecl || j >= nShort) all.push(b[i]); });
  // ---- modules
  const size = ver * 4 + 17;
  const M = Array.from({ length: size }, () => new Array(size).fill(false));
  const F = Array.from({ length: size }, () => new Array(size).fill(false)); // function modules
  const set = (x, y, v) => { M[y][x] = v; F[y][x] = true; };
  for (let i = 0; i < size; i++) { set(6, i, i % 2 === 0); set(i, 6, i % 2 === 0); }
  const finder = (cx, cy) => {
    for (let dy = -4; dy <= 4; dy++) for (let dx = -4; dx <= 4; dx++) {
      const d = Math.max(Math.abs(dx), Math.abs(dy)), x = cx + dx, y = cy + dy;
      if (x >= 0 && x < size && y >= 0 && y < size) set(x, y, d !== 2 && d !== 4);
    }
  };
  finder(3, 3); finder(size - 4, 3); finder(3, size - 4);
  const align = ver === 1 ? [] : (() => {
    const n = Math.floor(ver / 7) + 2, step = ver === 32 ? 26 : Math.ceil((ver * 4 + 4) / (n * 2 - 2)) * 2, r = [6];
    for (let p = size - 7; r.length < n; p -= step) r.splice(1, 0, p);
    return r;
  })();
  align.forEach((ax, i) => align.forEach((ay, j) => {
    if ((i === 0 && j === 0) || (i === 0 && j === align.length - 1) || (i === align.length - 1 && j === 0)) return;
    for (let dy = -2; dy <= 2; dy++) for (let dx = -2; dx <= 2; dx++) set(ax + dx, ay + dy, Math.max(Math.abs(dx), Math.abs(dy)) !== 1);
  }));
  const drawFormat = mask => {
    const d = ECL_BITS << 3 | mask; let r = d;
    for (let i = 0; i < 10; i++) r = (r << 1) ^ ((r >>> 9) * 0x537);
    const b = (d << 10 | r) ^ 0x5412, bit = i => ((b >>> i) & 1) !== 0;
    for (let i = 0; i <= 5; i++) set(8, i, bit(i));
    set(8, 7, bit(6)); set(8, 8, bit(7)); set(7, 8, bit(8));
    for (let i = 9; i < 15; i++) set(14 - i, 8, bit(i));
    for (let i = 0; i < 8; i++) set(size - 1 - i, 8, bit(i));
    for (let i = 8; i < 15; i++) set(8, size - 15 + i, bit(i));
    set(8, size - 8, true);
  };
  drawFormat(0);
  if (ver >= 7) {
    let r = ver; for (let i = 0; i < 12; i++) r = (r << 1) ^ ((r >>> 11) * 0x1F25);
    const b = ver << 12 | r;
    for (let i = 0; i < 18; i++) { const v = ((b >>> i) & 1) !== 0, a = size - 11 + i % 3, c = Math.floor(i / 3); set(a, c, v); set(c, a, v); }
  }
  // data placement (zig-zag)
  let i = 0;
  for (let right = size - 1; right >= 1; right -= 2) {
    if (right === 6) right = 5;
    for (let vert = 0; vert < size; vert++) for (let j = 0; j < 2; j++) {
      const x = right - j, up = ((right + 1) & 2) === 0, y = up ? size - 1 - vert : vert;
      if (!F[y][x] && i < all.length * 8) { M[y][x] = ((all[i >>> 3] >>> (7 - (i & 7))) & 1) !== 0; i++; }
    }
  }
  // masks
  const maskFn = [(x, y) => (x + y) % 2 === 0, (x, y) => y % 2 === 0, x => x % 3 === 0, (x, y) => (x + y) % 3 === 0,
    (x, y) => (Math.floor(x / 3) + Math.floor(y / 2)) % 2 === 0, (x, y) => x * y % 2 + x * y % 3 === 0,
    (x, y) => (x * y % 2 + x * y % 3) % 2 === 0, (x, y) => ((x + y) % 2 + x * y % 3) % 2 === 0];
  const applyMask = m => { for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) if (!F[y][x] && maskFn[m](x, y)) M[y][x] = !M[y][x]; };
  let best = 0, bestP = Infinity;
  for (let m = 0; m < 8; m++) { applyMask(m); drawFormat(m); const p = penalty(M, size); if (p < bestP) { bestP = p; best = m; } applyMask(m); }
  applyMask(best); drawFormat(best);
  return M;
}

function penalty(M, size) {
  let p = 0, dark = 0;
  const lineScore = get => {
    let s = 0, run = 1, prev = get(0);
    const seq = [prev];
    for (let i = 1; i < size; i++) {
      const c = get(i); seq.push(c);
      if (c === prev) { run++; if (run === 5) s += 3; else if (run > 5) s++; } else { run = 1; prev = c; }
    }
    // finder-like patterns 1:1:3:1:1 with 4 light modules on a side
    const str = seq.map(v => v ? "1" : "0").join("");
    for (const pat of ["10111010000", "00001011101"]) for (let k = str.indexOf(pat); k >= 0; k = str.indexOf(pat, k + 1)) s += 40;
    return s;
  };
  for (let y = 0; y < size; y++) p += lineScore(x => M[y][x]);
  for (let x = 0; x < size; x++) p += lineScore(y => M[y][x]);
  for (let y = 0; y < size - 1; y++) for (let x = 0; x < size - 1; x++) {
    const c = M[y][x]; if (c === M[y][x + 1] && c === M[y + 1][x] && c === M[y + 1][x + 1]) p += 3;
  }
  for (const row of M) for (const v of row) if (v) dark++;
  const total = size * size;
  p += (Math.ceil(Math.abs(dark * 20 - total * 10) / total) - 1) * 10;
  return p;
}

export function qrSvg(text, px = 220) {
  const M = qrMatrix(text), n = M.length, q = 4, s = n + q * 2;
  let d = "";
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) if (M[y][x]) d += `M${x + q},${y + q}h1v1h-1z`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${s} ${s}" width="${px}" height="${px}" shape-rendering="crispEdges" style="background:#fff"><rect width="${s}" height="${s}" fill="#fff"/><path d="${d}" fill="#000"/></svg>`;
}

// UPI payment link (NPCI format). Amount with 2 decimals; note = bill number.
export function upiLink({ vpa, name, amount, note }) {
  const e = encodeURIComponent;
  return `upi://pay?pa=${String(vpa).replace(/[^a-zA-Z0-9.@_-]/g, "")}&pn=${e((name || "Hospital").slice(0, 50))}&am=${Number(amount).toFixed(2)}&cu=INR&tn=${e((note || "").slice(0, 60))}`;
}

// Draw the QR box. hospital = { upi_id, upi_name, name }
export function upiBox(hospital, amount, billNo) {
  if (!(Number(amount) > 0)) return "";
  if (!hospital?.upi_id) return `<div class="card" style="text-align:center"><small class="muted">📱 UPI QR ke liye Doctor / Admin ek baar <b>Accounts → ⚙️ Rate list</b> mein hospital ki UPI ID daalein.</small></div>`;
  const link = upiLink({ vpa: hospital.upi_id, name: hospital.upi_name || hospital.name, amount, note: billNo });
  let svg = "";
  try { svg = qrSvg(link); } catch (e) { svg = `<p class="msg err">QR nahi bana: ${e.message}</p>`; }
  return `<div class="card upiqr" style="text-align:center">
    <b>📱 UPI se pay karein — ₹${Number(amount).toLocaleString("en-IN", { maximumFractionDigits: 2 })}</b><br>
    <div style="display:inline-block;margin:8px 0;padding:6px;background:#fff;border:1px solid #e2e8f0;border-radius:8px">${svg}</div><br>
    <small>${(hospital.upi_name || hospital.name || "").replace(/[<>&"]/g, "")} · ${hospital.upi_id.replace(/[<>&"]/g, "")} · Bill ${String(billNo || "").replace(/[<>&"]/g, "")}</small><br>
    <small class="muted">GPay / PhonePe / Paytm / BHIM se scan karein — rakam apne aap bhar jayegi.<br>Paisa aane ke baad UPI ka transaction number (UTR) "Payment save karo" mein likhein.</small>
    <div class="noprint" style="margin-top:6px"><a href="${link}"><button class="small ghost">📲 Isi phone ke UPI app se pay</button></a></div></div>`;
}
