// Vatte Hospital OS — Phase 11: Pharmacy (sale, stock in, stock, expiry / reorder, orders, today's sale + H1 register, medicine list)
// Stock changes only through server functions; the server picks the batch (earliest expiry first) and the price (batch MRP).
let C, TAB = "sell", MEDS = [], PAT = null, CART = [], RECV = [];
const $ = id => document.getElementById(id);
const rs = n => "₹" + Number(n || 0).toLocaleString("en-IN", { maximumFractionDigits: 2 });
const dt = t => new Date(t).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
const ist = () => new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Kolkata" }));
const ymd = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const my = d => d ? new Date(d).toLocaleDateString("en-IN", { month: "short", year: "2-digit" }) : "—";
const daysTo = d => Math.round((new Date(d) - new Date(ymd(ist()))) / 864e5);
const clean = s => String(s || "").replace(/[%,()"\\*]/g, "").trim();
const err = (el, e) => { if (el) { el.className = "msg err"; el.textContent = "❌ " + (e.message || e); } };
const ok = (el, t) => { if (el) { el.className = "msg ok"; el.textContent = t; } };
const SCH = { OTC: "", H: `<span class="badge">H</span>`, H1: `<span class="badge pending">H1</span>`, X: `<span class="badge pending">X</span>` };
const METHODS = [["cash", "💵 Cash"], ["upi", "📱 UPI"], ["card", "💳 Card"]];

export function render(ctx) {
  C = ctx; TAB = "sell"; PAT = null; CART = []; RECV = [];
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button>
    <h2 style="margin:0 0 6px">💊 Pharmacy</h2>
    <div class="row" id="tabs" style="gap:6px;margin-bottom:10px">
      ${[["sell", "💊 Becho"], ["recv", "🚚 Maal aaya"], ["stock", "📋 Stock"], ["alert", "⏰ Expiry / Kam"], ["order", "📦 Order"], ["today", "🧾 Aaj ki bikri"], ["meds", "⚙️ Dawa list"]]
        .map(([k, l]) => `<button class="small ${k === TAB ? "" : "ghost"}" data-t="${k}">${l}</button>`).join("")}
    </div><div id="body"><div class="card">Loading…</div></div><div id="receipt"></div>`;
  $("bk").onclick = C.goHome;
  C.app.querySelectorAll("#tabs [data-t]").forEach(b => b.onclick = () => {
    TAB = b.dataset.t; C.app.querySelectorAll("#tabs [data-t]").forEach(x => x.classList.toggle("ghost", x !== b));
    $("receipt").innerHTML = ""; show();
  });
  show();
}
async function loadMeds(q = "") {
  const { data, error } = await C.sb.rpc("pharmacy_stock", { p_q: q || null });
  if (error) throw error;
  return data || [];
}
function show() {
  ({ sell, recv, stock, alert: alerts, order: orders, today, meds: medList })[TAB]();
}

// ---------------------------------------------------------------- sell
function sell() {
  $("body").innerHTML = `<div class="card">
      <label>1️⃣ Patient (naam / UHID / phone)</label><input id="pq" autocomplete="off" placeholder="Kam se kam 2 akshar" value="${PAT ? C.esc(PAT.full_name) : ""}">
      <div id="pres"></div><div id="pchip" style="margin-top:6px">${PAT ? `✅ <b>${C.esc(PAT.full_name)}</b> · ${C.esc(PAT.uhid)}` : ""}</div></div>
    <div class="card"><label>2️⃣ Dawa dhoondo</label><input id="mq" autocomplete="off" placeholder="Dawa ka naam ya generic naam">
      <div id="mres"></div></div>
    <div id="cartbox"></div>`;
  let t1, t2;
  $("pq").oninput = () => { clearTimeout(t1); t1 = setTimeout(async () => {
    const q = clean($("pq").value);
    if (q.length < 2) { $("pres").innerHTML = ""; return; }
    const { data } = await C.sb.rpc("search_patients", { q });
    $("pres").innerHTML = (data || []).slice(0, 6).map(p => `<button class="small ghost" style="margin:3px" data-p='${C.esc(JSON.stringify({ id: p.id, full_name: p.full_name, uhid: p.uhid }))}'>${C.esc(p.full_name)} · ${C.esc(p.uhid)}${p.exact ? "" : " ≈"}</button>`).join("")
      || "<small class='muted'>Koi nahi mila — pehle Reception mein register karein</small>";
    $("pres").querySelectorAll("[data-p]").forEach(b => b.onclick = () => {
      PAT = JSON.parse(b.dataset.p); $("pres").innerHTML = ""; $("pq").value = PAT.full_name;
      $("pchip").innerHTML = `✅ <b>${C.esc(PAT.full_name)}</b> · ${C.esc(PAT.uhid)}`; drawCart(); showRx(PAT.id);
    });
  }, 300); };
  $("mq").oninput = () => { clearTimeout(t2); t2 = setTimeout(async () => {
    const q = clean($("mq").value);
    if (q.length < 2) { $("mres").innerHTML = ""; return; }
    let rows; try { rows = await loadMeds(q); } catch (e) { $("mres").innerHTML = `<p class="msg err">${C.esc(e.message)}</p>`; return; }
    rows = rows.filter(m => m.active).slice(0, 10);
    $("mres").innerHTML = rows.length ? rows.map((m, i) => `<button class="small ${m.stock ? "ghost" : "ghost soon"}" style="margin:3px" data-i="${i}" ${m.stock ? "" : "disabled"}>
        ${C.esc(m.name)} ${C.esc(m.strength || "")} ${SCH[m.schedule] || ""} · <b>${m.stock}</b> pcs${m.stock ? "" : " (khatam)"}</button>`).join("")
      : "<small class='muted'>Dawa list mein nahi — ⚙️ Dawa list mein jodein</small>";
    $("mres").querySelectorAll("[data-i]").forEach(b => b.onclick = () => {
      const m = rows[+b.dataset.i];
      const have = CART.find(x => x.medicine_id === m.medicine_id);
      if (have) have.quantity = Math.min(have.quantity + 1, m.stock);
      else CART.push({ medicine_id: m.medicine_id, name: `${m.name} ${m.strength || ""}`.trim(), schedule: m.schedule, stock: m.stock,
                       rate: Number(m.batches?.find(z => new Date(z.expiry) >= new Date(ymd(ist())))?.mrp || m.mrp || 0), quantity: 1 });
      $("mq").value = ""; $("mres").innerHTML = ""; drawCart();
    });
  }, 300); };
  drawCart();
}

// latest doctor prescription (3 days) → one tap adds its medicines with quantity = doses per day × days
async function showRx(pid) {
  const { data } = await C.sb.from("prescriptions").select("items, created_at").eq("patient_id", pid)
    .gte("created_at", new Date(Date.now() - 3 * 864e5).toISOString()).order("created_at", { ascending: false }).limit(1);
  const rx = data?.[0];
  if (!rx || !$("pchip")) return;
  const perDay = f => { const m = String(f || "").match(/^\d(-\d){1,3}$/); return m ? f.split("-").reduce((s, x) => s + Number(x), 0) : 1; };
  $("pchip").insertAdjacentHTML("beforeend", `<div class="card" style="margin-top:8px;background:#f0fdfa">📝 <b>Doctor ki parchi</b> <small class="muted">${dt(rx.created_at)}</small><br>
    <small>${rx.items.map(i => `${C.esc(i.medicine)} · ${C.esc(i.frequency || "")}${i.days ? " × " + i.days + " din" : ""}`).join("<br>")}</small><br>
    <button class="small" id="rxadd" style="margin-top:6px">＋ Parchi ki dawa bill mein jodo</button><p class="msg" id="rxm"></p></div>`);
  $("rxadd").onclick = async () => {
    const stock = await loadMeds().catch(() => []);
    const miss = [];
    for (const i of rx.items) {
      const m = stock.find(x => x.medicine_id === i.medicine_id) || stock.find(x => `${x.name} ${x.strength || ""}`.trim().toLowerCase() === String(i.medicine).trim().toLowerCase());
      if (!m || !m.active || !m.stock) { miss.push(i.medicine); continue; }
      const want = Math.min(m.stock, Math.max(1, perDay(i.frequency) * (i.days || 1)));
      if (!CART.some(x => x.medicine_id === m.medicine_id))
        CART.push({ medicine_id: m.medicine_id, name: `${m.name} ${m.strength || ""}`.trim(), schedule: m.schedule, stock: m.stock,
                    rate: Number(m.batches?.[0]?.mrp || m.mrp || 0), quantity: want });
    }
    drawCart();
    if (miss.length) { $("rxm").className = "msg err"; $("rxm").textContent = "Stock mein nahi / list mein nahi: " + miss.join(", "); }
  };
}

function drawCart(msg = "") {
  if (!$("cartbox")) return;
  if (!CART.length) { $("cartbox").innerHTML = ""; return; }
  const total = CART.reduce((s, x) => s + x.quantity * x.rate, 0);
  const rx = CART.some(x => ["H1", "X"].includes(x.schedule));
  $("cartbox").innerHTML = `<div class="card"><h3 style="margin:0 0 6px">3️⃣ Bill</h3>
    <div style="overflow-x:auto"><table><tr><th>Dawa</th><th>Qty</th><th>Rate*</th><th>Rakam</th><th></th></tr>${CART.map((x, i) => `<tr>
      <td>${C.esc(x.name)} ${SCH[x.schedule] || ""}<br><small class="muted">stock ${x.stock}</small></td>
      <td><input type="number" min="1" max="${x.stock}" value="${x.quantity}" data-q="${i}" style="width:64px"></td>
      <td>${rs(x.rate)}</td><td>${rs(x.quantity * x.rate)}</td><td><button class="small ghost" data-del="${i}">✖</button></td></tr>`).join("")}</table></div>
    <p class="muted" style="font-size:12px;margin:4px 0">* Andaazan. Asli rate batch ke MRP se server lagayega (pehle expire hone wala batch pehle).</p>
    ${rx ? `<label>👨‍⚕️ Doctor ka naam (H1 / X dawa ke liye zaroori)</label><input id="rxd" placeholder="Jaise: Dr. Vatte">
      <label>Parchi note (optional)</label><input id="rxn">` : ""}
    <div class="row" style="gap:6px;margin-top:6px"><div style="flex:1"><label>Discount ₹</label><input id="disc" type="number" min="0" value="0"></div>
      <div style="flex:2"><label>Discount ka kaaran</label><input id="dr"></div></div>
    <h3 style="margin:10px 0 4px">Kul: ${rs(total)}</h3>
    <button class="full" id="mk" ${PAT ? "" : "disabled"}>${PAT ? "🧾 Bill banao" : "Pehle patient chunein"}</button>
    <p class="msg" id="cmsg">${C.esc(msg)}</p></div>`;
  $("cartbox").querySelectorAll("[data-q]").forEach(inp => inp.onchange = () => {
    const x = CART[+inp.dataset.q]; x.quantity = Math.max(1, Math.min(x.stock, parseInt(inp.value) || 1)); drawCart();
  });
  $("cartbox").querySelectorAll("[data-del]").forEach(b => b.onclick = () => { CART.splice(+b.dataset.del, 1); drawCart(); });
  $("mk").onclick = async () => {
    $("mk").disabled = true;
    const { data: inv, error } = await C.sb.rpc("pharmacy_sell", {
      p_patient: PAT.id, p_items: CART.map(x => ({ medicine_id: x.medicine_id, quantity: x.quantity })),
      p_discount: Number($("disc").value) || 0, p_discount_reason: $("dr").value,
      p_rx_doctor: $("rxd")?.value || null, p_rx_note: $("rxn")?.value || null });
    if (error) { $("mk").disabled = false; return err($("cmsg"), error); }
    CART = []; const p = PAT; PAT = null;
    sell(); payBox(inv, p);
  };
}

async function payBox(inv, p) {
  const net = Number(inv.total) - Number(inv.discount);
  $("cartbox").innerHTML = `<div class="card" style="border-color:#99f6e4;background:#f0fdfa">
    <h3 style="margin:0">✅ Bill ${C.esc(inv.invoice_no)} bana — ${rs(net)}</h3>
    <p class="muted" style="margin:4px 0">${C.esc(p?.full_name || "")}</p>
    ${net > 0 ? `<label>Kitna mila ₹</label><input id="pa" type="number" min="0" step="0.01" value="${net}">
    <div class="row" style="gap:6px;margin-top:6px">${METHODS.map(([k, l], i) => `<label class="row" style="gap:4px"><input type="radio" name="pm" value="${k}" ${i ? "" : "checked"} style="width:auto">${l}</label>`).join("")}</div>
    <input id="pr" placeholder="UPI / card transaction no. (cash mein khaali)">
    <button class="full" id="pgo">💵 Paisa lo</button>` : ""}
    <button class="ghost full" id="prc">🖨️ Receipt</button><p class="msg" id="pmsg"></p></div>`;
  if ($("pgo")) $("pgo").onclick = async () => {
    $("pgo").disabled = true;
    const { error } = await C.sb.rpc("record_payment", { p_invoice: inv.id, p_amount: Number($("pa").value), p_method: C.app.querySelector("[name=pm]:checked").value, p_reference: $("pr").value });
    if (error) { $("pgo").disabled = false; return err($("pmsg"), error); }
    ok($("pmsg"), "✓ Paisa mil gaya"); $("pgo").remove(); receipt(inv.id);
  };
  $("prc").onclick = () => receipt(inv.id);
}

async function receipt(id) {
  const [{ data: i }, { data: items }, { data: pays }, { data: h }] = await Promise.all([
    C.sb.from("invoices").select("*, patients(full_name, uhid)").eq("id", id).single(),
    C.sb.from("invoice_items").select("description, quantity, rate").eq("invoice_id", id),
    C.sb.from("payments").select("amount, method, created_at").eq("invoice_id", id),
    C.sb.from("hospitals").select("name").maybeSingle()]);
  if (!i) return;
  const net = i.total - i.discount, paid = (pays || []).reduce((s, p) => s + Number(p.amount), 0);
  $("receipt").innerHTML = `<div class="card" id="rcpt" style="max-width:420px;margin:10px auto;font-size:14px">
    <div style="text-align:center"><b style="font-size:18px">${C.esc(h?.name || "Hospital")} — Pharmacy</b><br><small>Dawa bill</small></div><hr>
    <div>Bill: <b>${C.esc(i.invoice_no)}</b> · ${dt(i.created_at)}<br>Patient: <b>${C.esc(i.patients?.full_name)}</b> (${C.esc(i.patients?.uhid)})
      ${i.rx_doctor ? `<br>Doctor: ${C.esc(i.rx_doctor)}` : ""}${i.status === "cancelled" ? "<br><b style='color:red'>CANCEL</b>" : ""}</div><hr>
    <table style="width:100%">${(items || []).map(x => `<tr><td>${C.esc(x.description)} × ${x.quantity}</td><td style="text-align:right">${rs(x.quantity * x.rate)}</td></tr>`).join("")}
      ${Number(i.discount) ? `<tr><td>Discount</td><td style="text-align:right">− ${rs(i.discount)}</td></tr>` : ""}
      <tr><td><b>Kul</b></td><td style="text-align:right"><b>${rs(net)}</b></td></tr>
      <tr><td>Mila</td><td style="text-align:right">${rs(paid)}</td></tr><tr><td><b>Baaki</b></td><td style="text-align:right"><b>${rs(net - paid)}</b></td></tr></table>
    <p style="text-align:center;margin-top:10px"><small>Dawa doctor ki salah se hi lein · Dhanyavaad 🙏</small></p></div>
    <div class="row noprint" style="gap:6px;justify-content:center"><button id="rp">🖨️ Print / PDF</button><button class="ghost" id="rc">Band karo</button></div>`;
  $("rp").onclick = () => { document.body.classList.add("printing"); window.print(); setTimeout(() => document.body.classList.remove("printing"), 500); };
  $("rc").onclick = () => { $("receipt").innerHTML = ""; };
  $("receipt").scrollIntoView({ behavior: "smooth" });
}

// ---------------------------------------------------------------- stock in
async function recv() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const [rows, { data: sup }] = await Promise.all([loadMeds().catch(() => []), C.sb.from("suppliers").select("name").order("name")]);
  MEDS = rows.filter(m => m.active);
  if (!RECV.length) RECV = [{}];
  $("body").innerHTML = `<div class="card">
      <p class="muted" style="margin:0 0 6px">Supplier ka bill haath mein lekar har dawa ki line bharo. Expired / galat MRP wala maal server nahi lega.</p>
      <label>Supplier ka naam</label><input id="sn" list="sups" placeholder="Jaise: Tata 1mg">
      <datalist id="sups">${(sup || []).map(s => `<option value="${C.esc(s.name)}">`).join("")}</datalist>
      <label>Supplier bill number</label><input id="sb"></div>
    <div id="lines"></div>
    <div class="card"><button class="ghost full" id="add">＋ Ek aur dawa</button>
      <h3 id="rt" style="margin:10px 0 4px"></h3><button class="full" id="save">✅ Stock mein chadhao</button><p class="msg" id="rmsg"></p></div>`;
  $("add").onclick = () => { readLines(); RECV.push({}); drawLines(); };
  $("save").onclick = async () => {
    readLines();
    const items = RECV.filter(x => x.medicine_id);
    $("save").disabled = true;
    const { data, error } = await C.sb.rpc("pharmacy_receive", { p_supplier_name: $("sn").value, p_invoice_no: $("sb").value, p_items: items });
    $("save").disabled = false;
    if (error) return err($("rmsg"), error);
    RECV = []; recv();
    setTimeout(() => ok($("rmsg"), `✓ ${items.length} dawa stock mein chadh gayi · bill ${rs(data.total)}`), 300);
  };
  drawLines();
}
function readLines() {
  document.querySelectorAll("[data-line]").forEach(el => {
    const i = +el.dataset.line, g = k => el.querySelector(`[data-k="${k}"]`).value;
    RECV[i] = { medicine_id: g("m"), batch_no: g("b"), expiry: g("e"), quantity: +g("q") || 0, free_qty: +g("f") || 0,
                purchase_price: g("p") === "" ? null : +g("p"), mrp: g("r") === "" ? null : +g("r") };
  });
}
function drawLines() {
  $("lines").innerHTML = RECV.map((x, i) => `<div class="card" data-line="${i}">
    <div class="row" style="justify-content:space-between"><b>Dawa ${i + 1}</b>${RECV.length > 1 ? `<button class="small ghost" data-rm="${i}">✖</button>` : ""}</div>
    <select data-k="m"><option value="">— dawa chunein —</option>${MEDS.map(m => `<option value="${m.medicine_id}" ${m.medicine_id === x.medicine_id ? "selected" : ""}>${C.esc(m.name)} ${C.esc(m.strength || "")}</option>`).join("")}</select>
    <div class="row" style="gap:6px"><div style="flex:1"><label>Batch no.</label><input data-k="b" value="${C.esc(x.batch_no || "")}"></div>
      <div style="flex:1"><label>Expiry</label><input data-k="e" type="date" value="${C.esc(x.expiry || "")}"></div></div>
    <div class="row" style="gap:6px"><div style="flex:1"><label>Qty (pcs)</label><input data-k="q" type="number" min="1" value="${x.quantity || ""}"></div>
      <div style="flex:1"><label>Free</label><input data-k="f" type="number" min="0" value="${x.free_qty || ""}"></div></div>
    <div class="row" style="gap:6px"><div style="flex:1"><label>Kharid rate / pc ₹</label><input data-k="p" type="number" min="0" step="0.01" value="${x.purchase_price ?? ""}"></div>
      <div style="flex:1"><label>MRP / pc ₹</label><input data-k="r" type="number" min="0" step="0.01" value="${x.mrp ?? ""}"></div></div></div>`).join("");
  $("lines").querySelectorAll("[data-rm]").forEach(b => b.onclick = () => { readLines(); RECV.splice(+b.dataset.rm, 1); drawLines(); });
  const tot = () => { readLines(); $("rt").textContent = "Kul kharid: " + rs(RECV.reduce((s, x) => s + (x.quantity || 0) * (x.purchase_price || 0), 0)); };
  $("lines").querySelectorAll("input,select").forEach(e => e.onchange = tot); tot();
}

// ---------------------------------------------------------------- stock
async function stock(q = "") {
  $("body").innerHTML = `<div class="card"><input id="sq" placeholder="🔎 Dawa dhoondo" value="${C.esc(q)}"></div><div id="slist">Loading…</div>`;
  let t; $("sq").oninput = () => { clearTimeout(t); t = setTimeout(() => drawStock(clean($("sq").value)), 300); };
  drawStock(q);
}
async function drawStock(q) {
  let rows; try { rows = await loadMeds(q); } catch (e) { $("slist").innerHTML = `<div class="card msg err">${C.esc(e.message)}</div>`; return; }
  const boss = ["doctor", "admin"].includes(C.me.role);
  $("slist").innerHTML = rows.length ? `<div class="card" style="overflow-x:auto"><table><tr><th>Dawa</th><th>Stock</th><th>Agli expiry</th><th>Rack</th></tr>${rows.map((m, i) => `
    <tr data-i="${i}" style="cursor:pointer;${m.active ? "" : "opacity:.5"}"><td>${C.esc(m.name)} ${C.esc(m.strength || "")} ${SCH[m.schedule] || ""}</td>
    <td>${m.stock < m.reorder_level ? "🔴 " : ""}<b>${m.stock}</b>${m.expired_qty ? `<br><small style="color:var(--red)">${m.expired_qty} expired</small>` : ""}</td>
    <td>${m.next_expiry ? (daysTo(m.next_expiry) <= 60 ? "🟠 " : "") + my(m.next_expiry) : "—"}</td><td>${C.esc(m.rack || "")}</td></tr>
    <tr id="bx${i}" style="display:none"><td colspan="4">${(m.batches || []).map(b => `<div class="row" style="gap:6px;margin:3px 0">
      <span>Batch <b>${C.esc(b.batch)}</b> · exp ${my(b.expiry)} · ${b.qty} pcs · MRP ${rs(b.mrp)}</span>
      <button class="small ghost" data-adj="${b.batch_id}" data-n="${C.esc(m.name + " " + b.batch)}">− Kam karo</button>
      ${boss ? `<button class="small ghost" data-add="${b.batch_id}" data-n="${C.esc(m.name + " " + b.batch)}">＋</button>` : ""}</div>`).join("") || "<small class='muted'>Koi batch nahi</small>"}</td></tr>`).join("")}</table>
    <p class="muted" style="font-size:12px">Dawa par tap karo → batch dikhenge. 🔴 = kam stock · 🟠 = 60 din mein expiry</p><p class="msg" id="smsg"></p></div>`
    : `<div class="card"><p class="muted">Kuch nahi mila.</p></div>`;
  $("slist").querySelectorAll("tr[data-i]").forEach(r => r.onclick = () => { const b = $("bx" + r.dataset.i); b.style.display = b.style.display === "none" ? "" : "none"; });
  const adj = sign => b => b.onclick = async e => {
    e.stopPropagation();
    const n = parseInt(prompt(`${b.dataset.n}: kitne pcs ${sign < 0 ? "kam" : "zyada"} karne hain?`) || "");
    if (!n || n < 1) return;
    const why = prompt("Kaaran? (jaise: toot gayi, ginti mein fark)") || "";
    if (!why.trim()) return;
    const { error } = await C.sb.rpc("pharmacy_adjust", { p_batch: b.dataset.adj || b.dataset.add, p_change: sign * n, p_reason: why });
    if (error) return err($("smsg"), error);
    drawStock(clean($("sq").value));
  };
  $("slist").querySelectorAll("[data-adj]").forEach(adj(-1));
  $("slist").querySelectorAll("[data-add]").forEach(adj(1));
}

// ---------------------------------------------------------------- expiry / low stock
async function alerts() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const lim = ymd(new Date(ist().getTime() + 60 * 864e5));
  const [{ data: exp }, { data: low, error }] = await Promise.all([
    C.sb.from("medicine_batches").select("id, batch_no, expiry_date, quantity, medicines(name, strength)").gt("quantity", 0).lte("expiry_date", lim).order("expiry_date"),
    C.sb.rpc("pharmacy_reorder")]);
  const today = ymd(ist());
  $("body").innerHTML = `<div class="card"><h3 style="margin:0 0 6px">⏰ 60 din mein expiry</h3>
      ${(exp || []).length ? `<table><tr><th>Dawa</th><th>Batch</th><th>Expiry</th><th>Pcs</th><th></th></tr>${exp.map(b => `<tr>
        <td>${C.esc(b.medicines?.name)} ${C.esc(b.medicines?.strength || "")}</td><td>${C.esc(b.batch_no)}</td>
        <td>${b.expiry_date < today ? "❌ Expired" : "🟠 " + daysTo(b.expiry_date) + " din"}</td><td>${b.quantity}</td>
        <td>${b.expiry_date < today ? `<button class="small ghost" data-w="${b.id}">Zero karo</button>` : ""}</td></tr>`).join("")}</table>
        <p class="muted" style="font-size:12px">Expired dawa kabhi bikti nahi. "Zero karo" Doctor ki approval ke baad hota hai. Jo jaldi expire hogi, use supplier ko wapas bhejne ki koshish karein.</p>`
      : "<p class='muted'>Koi dawa jaldi expire nahi ho rahi ✓</p>"}<p class="msg" id="wmsg"></p></div>
    <div class="card"><h3 style="margin:0 0 6px">🔴 Kam stock — kya mangwana hai</h3>
      ${error ? `<p class="msg err">${C.esc(error.message)}</p>` : (low || []).length ? `<div style="overflow-x:auto"><table><tr><th>Dawa</th><th>Stock</th><th>30 din bikri</th><th>Mangao</th><th>Last supplier</th></tr>${low.map(r => `<tr>
        <td>${C.esc(r.name)}</td><td>${r.stock} / ${r.reorder_level}</td><td>${r.sold_30d}</td><td><b>${r.suggest}</b></td><td>${C.esc(r.last_supplier || "—")}</td></tr>`).join("")}</table></div>
        <button class="full" id="od">🤖 Pharmacy AI se order list banwao (approval se)</button>` : "<p class='muted'>Sab dawa ka stock theek hai ✓</p>"}
      <p class="msg" id="omsg"></p></div>`;
  $("body").querySelectorAll("[data-w]").forEach(b => b.onclick = async () => {
    b.disabled = true;
    const { data: t, error } = await C.sb.rpc("agent_submit", { p_action: "pharmacy.writeoff_expired", p_input: { batch_id: b.dataset.w } });
    if (error) return err($("wmsg"), error);
    ok($("wmsg"), t.status === "waiting_approval" ? "✋ Doctor ki approval ke liye bhej diya" : "✓ " + (t.summary || ""));
  });
  if ($("od")) $("od").onclick = async () => {
    $("od").disabled = true;
    const { data: t, error } = await C.sb.rpc("agent_submit", { p_action: "pharmacy.order_draft", p_input: {} });
    if (error) { $("od").disabled = false; return err($("omsg"), error); }
    ok($("omsg"), t.status === "waiting_approval" ? "✋ Doctor / Admin ki approval ke liye bhej diya. Approve hote hi 📦 Order mein list aa jayegi." : "✓ " + (t.summary || t.error || ""));
  };
}

// ---------------------------------------------------------------- orders
async function orders() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const { data, error } = await C.sb.from("purchases").select("id, status, total, created_at, purchase_items(description, quantity, rate)")
    .eq("kind", "request").eq("purpose", "pharmacy").order("created_at", { ascending: false }).limit(20);
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const ST = { approved: "🟡 Bhejna hai", received: "🟢 Maal aa gaya", cancelled: "✖️ Cancel" };
  $("body").innerHTML = (data || []).length ? data.map(p => `<div class="card">
      <div class="row" style="justify-content:space-between"><b>${ST[p.status] || p.status}</b><small class="muted">${dt(p.created_at)} · andaazan ${rs(p.total)}</small></div>
      <table>${p.purchase_items.map(x => `<tr><td>${C.esc(x.description)}</td><td><b>${x.quantity}</b> pcs</td></tr>`).join("")}</table>
      ${p.status === "approved" ? `<div class="row" style="gap:6px;margin-top:8px">
        <button class="small" data-copy="${p.id}">📋 WhatsApp ke liye copy</button>
        <button class="small ghost" data-done="${p.id}">✅ Maal aa gaya</button><button class="small ghost" data-cx="${p.id}">✖ Cancel</button></div>` : ""}
      <p class="msg" id="m${p.id}"></p></div>`).join("")
    : `<div class="card"><p class="muted">Abhi koi order list nahi. ⏰ Expiry / Kam mein jaakar AI se banwayein.</p></div>`;
  $("body").querySelectorAll("[data-copy]").forEach(b => b.onclick = async () => {
    const p = data.find(z => z.id === b.dataset.copy);
    const txt = `Namaste, ${C.me.hospital_name || "Hospital"} ke liye order:\n` + p.purchase_items.map((x, i) => `${i + 1}. ${x.description.split(" · last:")[0]} — ${x.quantity} pcs`).join("\n");
    try { await navigator.clipboard.writeText(txt); ok($("m" + p.id), "✓ Copy ho gaya — WhatsApp mein paste karein"); }
    catch { prompt("Ye text copy karein:", txt); }
  });
  const setSt = (sel, st) => $("body").querySelectorAll(sel).forEach(b => b.onclick = async () => {
    const id = b.dataset.done || b.dataset.cx;
    const { error } = await C.sb.rpc("pharmacy_order_status", { p_purchase: id, p_status: st });
    if (error) return err($("m" + id), error);
    if (st === "received") { TAB = "recv"; C.app.querySelectorAll("#tabs [data-t]").forEach(x => x.classList.toggle("ghost", x.dataset.t !== "recv")); return recv(); }
    orders();
  });
  setSt("[data-done]", "received"); setSt("[data-cx]", "cancelled");
}

// ---------------------------------------------------------------- today's sale + H1 register
async function today(view = "sale") {
  $("body").innerHTML = `<div class="card row" style="gap:6px">
      <button class="small ${view === "sale" ? "" : "ghost"}" data-v="sale">🧾 Aaj ke bill</button>
      <button class="small ${view === "h1" ? "" : "ghost"}" data-v="h1">📕 H1 register (30 din)</button></div><div id="tl">Loading…</div>`;
  $("body").querySelectorAll("[data-v]").forEach(b => b.onclick = () => today(b.dataset.v));
  const from = view === "sale" ? ymd(ist()) : ymd(new Date(ist().getTime() - 30 * 864e5));
  let q = C.sb.from("invoices").select("id, invoice_no, total, discount, status, created_at, rx_doctor, patients(full_name, uhid), invoice_items(description, quantity)")
    .eq("category", "pharmacy").gte("created_at", new Date(from + "T00:00:00+05:30").toISOString()).order("created_at", { ascending: false }).limit(200);
  if (view === "h1") q = q.not("rx_doctor", "is", null).neq("status", "cancelled");
  const { data, error } = await q;
  if (error) { $("tl").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  if (view === "h1") {
    $("tl").innerHTML = `<div class="card" style="overflow-x:auto">${(data || []).length ? `<table><tr><th>Date</th><th>Patient</th><th>Doctor</th><th>Dawa</th></tr>${data.map(i => `<tr>
      <td>${dt(i.created_at)}</td><td>${C.esc(i.patients?.full_name)}<br><small>${C.esc(i.patients?.uhid)}</small></td><td>${C.esc(i.rx_doctor)}</td>
      <td>${i.invoice_items.map(x => C.esc(x.description) + " × " + x.quantity).join("<br>")}</td></tr>`).join("")}</table>` : "<p class='muted'>Koi H1 / X bikri nahi.</p>"}
      <button class="ghost small" id="pr1" style="margin-top:8px">🖨️ Print</button></div>`;
    $("pr1").onclick = () => window.print();
    return;
  }
  const live = (data || []).filter(i => i.status !== "cancelled");
  const sum = live.reduce((s, i) => s + (i.total - i.discount), 0);
  const ST = { unpaid: "🔴 Baaki", partial: "🟡 Thoda baaki", paid: "🟢 Paid", cancelled: "✖️ Cancel" };
  $("tl").innerHTML = `<div class="card"><b>${live.length} bill · ${rs(sum)}</b></div>` + ((data || []).map(i => `<div class="card">
      <div class="row" style="justify-content:space-between"><b>${C.esc(i.invoice_no)} · ${rs(i.total - i.discount)}</b><span>${ST[i.status] || i.status}</span></div>
      <small class="muted">${dt(i.created_at)} · ${C.esc(i.patients?.full_name)} (${C.esc(i.patients?.uhid)})</small>
      <div style="font-size:13px;margin-top:4px">${i.invoice_items.map(x => C.esc(x.description) + " × " + x.quantity).join("<br>")}</div>
      <div class="row" style="gap:6px;margin-top:6px"><button class="small ghost" data-r="${i.id}">🖨️ Receipt</button>
        ${["unpaid", "partial"].includes(i.status) ? `<button class="small" data-pay="${i.id}">💵 Paisa lo</button>` : ""}
        ${i.status === "unpaid" ? `<button class="small ghost" data-cx="${i.id}">✖ Cancel (stock wapas)</button>` : ""}</div>
      <p class="msg" id="m${i.id}"></p></div>`).join("") || `<div class="card"><p class="muted">Aaj abhi koi bill nahi.</p></div>`);
  $("tl").querySelectorAll("[data-r]").forEach(b => b.onclick = () => receipt(b.dataset.r));
  $("tl").querySelectorAll("[data-pay]").forEach(b => b.onclick = async () => {
    const { data: inv } = await C.sb.from("invoices").select("*, patients(full_name)").eq("id", b.dataset.pay).single();
    const paid = (await C.sb.rpc("invoice_paid", { p_invoice: inv.id })).data || 0;
    $("tl").innerHTML = `<div id="cartbox"></div>`;
    payBox({ ...inv, total: inv.total - paid }, inv.patients);
  });
  $("tl").querySelectorAll("[data-cx]").forEach(b => b.onclick = async () => {
    const why = prompt("Cancel ka kaaran?") || "";
    if (!why.trim()) return;
    const { error } = await C.sb.rpc("pharmacy_cancel_sale", { p_invoice: b.dataset.cx, p_reason: why });
    if (error) return err($("m" + b.dataset.cx), error);
    today("sale");
  });
}

// ---------------------------------------------------------------- medicine list
async function medList(edit = null) {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  let rows; try { rows = await loadMeds(); } catch (e) { $("body").innerHTML = `<div class="card msg err">${C.esc(e.message)}</div>`; return; }
  const m = edit ? rows.find(r => r.medicine_id === edit) : null;
  const { data: full } = m ? await C.sb.from("medicines").select("gst_pct").eq("id", m.medicine_id).single() : { data: null };
  $("body").innerHTML = `<div class="card"><h3 style="margin:0 0 6px">${m ? "✏️ Dawa badlo" : "＋ Nayi dawa"}</h3>
      <label>Naam (brand)</label><input id="n" value="${C.esc(m?.name || "")}">
      <label>Generic naam</label><input id="g" value="${C.esc(m?.generic_name || "")}">
      <div class="row" style="gap:6px"><div style="flex:1"><label>Roop</label><select id="f">${["Tablet", "Capsule", "Syrup", "Injection", "IV fluid", "Ointment", "Drops", "Sachet", "Inhaler", "Other"].map(x => `<option ${x === m?.form ? "selected" : ""}>${x}</option>`).join("")}</select></div>
        <div style="flex:1"><label>Strength</label><input id="s" value="${C.esc(m?.strength || "")}" placeholder="500 mg"></div></div>
      <div class="row" style="gap:6px"><div style="flex:1"><label>Schedule</label><select id="sc">${[["OTC", "OTC (bina parchi)"], ["H", "H"], ["H1", "H1 (register)"], ["X", "X"]].map(([k, l]) => `<option value="${k}" ${k === (m?.schedule || "OTC") ? "selected" : ""}>${l}</option>`).join("")}</select></div>
        <div style="flex:1"><label>GST %</label><select id="gst">${[0, 5, 12, 18, 28].map(x => `<option ${x === Number(full?.gst_pct ?? 12) ? "selected" : ""}>${x}</option>`).join("")}</select></div></div>
      <div class="row" style="gap:6px"><div style="flex:1"><label>MRP / pc ₹</label><input id="mrp" type="number" step="0.01" min="0" value="${m?.mrp ?? ""}"></div>
        <div style="flex:1"><label>Kam stock alert (pcs)</label><input id="ro" type="number" min="0" value="${m?.reorder_level ?? 10}"></div>
        <div style="flex:1"><label>Rack</label><input id="rk" value="${C.esc(m?.rack || "")}"></div></div>
      ${m ? `<label class="row" style="gap:6px"><input type="checkbox" id="ac" style="width:auto" ${m.active ? "checked" : ""}> Chalu (bikri ke liye)</label>` : ""}
      <button class="full" id="sv">💾 Save</button>${m ? `<button class="ghost full" id="cn">Naya jodo</button>` : ""}<p class="msg" id="mm"></p></div>
    <div class="card" style="overflow-x:auto"><table><tr><th>Dawa</th><th>Sch.</th><th>MRP</th><th>Alert</th></tr>${rows.map(r => `<tr data-e="${r.medicine_id}" style="cursor:pointer;${r.active ? "" : "opacity:.5"}">
      <td>${C.esc(r.name)} ${C.esc(r.strength || "")}<br><small class="muted">${C.esc(r.generic_name || "")} · ${C.esc(r.form || "")}</small></td>
      <td>${C.esc(r.schedule)}</td><td>${r.mrp != null ? rs(r.mrp) : "—"}</td><td>${r.reorder_level}</td></tr>`).join("")}</table>
      <p class="muted" style="font-size:12px">Badalne ke liye dawa par tap karo.</p></div>`;
  $("body").querySelectorAll("[data-e]").forEach(r => r.onclick = () => medList(r.dataset.e));
  if ($("cn")) $("cn").onclick = () => medList();
  $("sv").onclick = async () => {
    const { error } = await C.sb.rpc("pharmacy_save_medicine", {
      p_id: m?.medicine_id || null, p_name: $("n").value, p_generic: $("g").value, p_form: $("f").value, p_strength: $("s").value,
      p_mrp: $("mrp").value === "" ? null : Number($("mrp").value), p_reorder: parseInt($("ro").value) || 0,
      p_schedule: $("sc").value, p_gst: Number($("gst").value), p_rack: $("rk").value, p_active: $("ac") ? $("ac").checked : true });
    if (error) return err($("mm"), error);
    medList();
    setTimeout(() => ok($("mm"), "✓ Save ho gaya"), 300);
  };
}
