// Vatte Hospital OS — Phase 10: Accounts (bills, payments, refunds, expenses, day book, cash close, rate list)
// Every money change goes through a server function; nothing can be edited or deleted — mistakes are reversed.
import { upiBox } from "./qr.js";
let C, TAB = "new", RATES = [], CART = [], PAT = null, SUG = null;
const $ = id => document.getElementById(id);
const rs = n => "₹" + Number(n || 0).toLocaleString("en-IN", { maximumFractionDigits: 2 });
const dt = t => new Date(t).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
const ist = () => new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Kolkata" }));
const ymd = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const METHODS = [["cash", "💵 Cash"], ["upi", "📱 UPI"], ["card", "💳 Card"], ["bank", "🏦 Bank"]];
const ST = { unpaid: "🔴 Baaki", partial: "🟡 Thoda baaki", paid: "🟢 Poora mila", cancelled: "✖️ Cancel" };
const boss = () => ["doctor", "admin", "accountant"].includes(C.me.role);
const err = (el, e) => { if (el) { el.className = "msg err"; el.textContent = "❌ " + (e.message || e); } };

export function render(ctx) {
  C = ctx; TAB = "new"; CART = []; PAT = null; SUG = null;
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button>
    <h2 style="margin:0 0 6px">💰 Accounts</h2>
    <div class="row" id="tabs" style="gap:6px;margin-bottom:10px;flex-wrap:wrap">
      <button class="small" data-t="new">🧾 Naya bill</button>
      <button class="small ghost" data-t="bills">📋 Bills</button>
      ${boss() ? `<button class="small ghost" data-t="book">📒 Hisaab (Day book)</button>
      <button class="small ghost" data-t="cash">💵 Cash close</button>
      <button class="small ghost" data-t="rates">⚙️ Rate list</button>` : ""}
    </div><div id="body"><div class="card">Loading…</div></div><div id="receipt"></div>`;
  $("bk").onclick = C.goHome;
  C.app.querySelectorAll("#tabs [data-t]").forEach(b => b.onclick = () => {
    TAB = b.dataset.t; C.app.querySelectorAll("#tabs [data-t]").forEach(x => x.classList.toggle("ghost", x !== b)); show();
  });
  loadRates().then(show);
}
async function loadRates() {
  const { data } = await C.sb.from("service_charges").select("*").order("category").order("name");
  RATES = data || [];
}
function show() {
  ({ new: newBill, bills, book: dayBook, cash: cashClose, rates: rateList })[TAB]();
}

// ---------------------------------------------------------------- new bill
function newBill() {
  $("body").innerHTML = `<div class="card">
      <label>Patient (naam / UHID / phone)</label><input id="pq" autocomplete="off" placeholder="Kam se kam 2 akshar" value="${PAT ? C.esc(PAT.full_name) : ""}">
      <div id="pres"></div>
      <div id="pchip" style="margin-top:6px">${PAT ? `✅ <b>${C.esc(PAT.full_name)}</b> · ${C.esc(PAT.uhid)}` : ""}</div></div>
    <div id="cartbox"></div>`;
  let t;
  $("pq").oninput = () => { clearTimeout(t); t = setTimeout(async () => {
    const q = $("pq").value.replace(/[%,()"\\*]/g, "").trim();
    if (q.length < 2) { $("pres").innerHTML = ""; return; }
    const { data } = await C.sb.rpc("search_patients", { q });
    $("pres").innerHTML = (data || []).slice(0, 6).map(p => `<button class="small ghost" style="margin:3px" data-p='${C.esc(JSON.stringify({ id: p.id, full_name: p.full_name, uhid: p.uhid, phone: p.phone }))}'>${C.esc(p.full_name)} · ${C.esc(p.uhid)}${p.exact ? "" : " ≈"}</button>`).join("") || "<small class='muted'>Koi nahi mila</small>";
    $("pres").querySelectorAll("[data-p]").forEach(b => b.onclick = () => pickPatient(JSON.parse(b.dataset.p)));
  }, 300); };
  if (PAT) drawCart();
}

async function pickPatient(p) {
  PAT = p; $("pres").innerHTML = ""; $("pq").value = p.full_name;
  $("pchip").innerHTML = `✅ <b>${C.esc(p.full_name)}</b> · ${C.esc(p.uhid)}`;
  const { data, error } = await C.sb.rpc("suggest_bill", { p_patient: p.id });
  SUG = error ? null : data;
  CART = (SUG?.items || []).map(x => ({ ...x }));
  drawCart();
}

function drawCart(msg = "") {
  const total = CART.reduce((s, x) => s + (Number(x.quantity) || 0) * (Number(x.rate) || 0), 0);
  $("cartbox").innerHTML = `<div class="card">
    <h3 style="margin:0 0 6px">Bill ki cheezein</h3>
    ${SUG?.items?.length ? `<p class="muted" style="margin:0 0 6px;font-size:12px">💡 Visit / admit ${SUG.admitted_days ? `(${SUG.admitted_days} din)` : ""} / lab ke hisaab se apne aap bhara gaya — zaroorat ho to badlo.</p>` : ""}
    ${CART.length ? `<div style="overflow-x:auto"><table><tr><th>Cheez</th><th>Qty</th><th>Rate</th><th>Rakam</th><th></th></tr>${CART.map((x, i) => `<tr>
      <td>${C.esc(x.description)}</td>
      <td><input type="number" min="1" max="1000" value="${x.quantity}" data-q="${i}" style="width:60px"></td>
      <td><input type="number" min="0" step="0.01" value="${x.rate}" data-r="${i}" style="width:80px"></td>
      <td>${rs(x.quantity * x.rate)}</td><td><button class="small ghost" data-del="${i}">✖</button></td></tr>`).join("")}</table></div>` : `<p class="muted">Abhi kuch nahi — neeche se jodo.</p>`}
    <div class="row" style="gap:6px;margin-top:8px;flex-wrap:wrap">
      <select id="addr" style="flex:1;min-width:160px"><option value="">＋ Rate list se jodo…</option>${RATES.filter(r => r.active).map(r =>
        `<option value="${r.id}">${C.esc(r.name)} — ${rs(r.price)}</option>`).join("")}</select>
    </div>
    <div class="row" style="gap:6px;margin-top:6px">
      <input id="cn" placeholder="Ya apni cheez likho" style="flex:2"><input id="cr" type="number" min="0" placeholder="Rate" style="flex:1"><button class="small" id="cadd">Jodo</button>
    </div>
    <div class="row" style="gap:6px;margin-top:10px">
      <div style="flex:1"><label>Discount (₹)</label><input id="disc" type="number" min="0" value="0"></div>
      <div style="flex:2"><label>Discount ka kaaran</label><input id="dr" placeholder="Discount ho to zaroori"></div>
    </div>
    <p style="font-size:20px;margin:10px 0">Kul: <b id="gt">${rs(total)}</b></p>
    <p class="msg ${msg ? "err" : ""}" id="cmsg">${C.esc(msg)}</p>
    <button class="full" id="make" ${CART.length ? "" : "disabled"}>🧾 Bill banao</button>
    <small class="muted">Bill banne ke baad uski rakam badli nahi ja sakti (galti ho to cancel karke naya). 10% se zyada discount sirf Doctor.</small></div>`;
  const upd = () => { const d = Number($("disc").value) || 0; $("gt").textContent = rs(CART.reduce((s, x) => s + x.quantity * x.rate, 0) - d); };
  $("cartbox").querySelectorAll("[data-q]").forEach(i => i.onchange = () => { CART[i.dataset.q].quantity = Math.max(1, parseInt(i.value) || 1); drawCart(); });
  $("cartbox").querySelectorAll("[data-r]").forEach(i => i.onchange = () => { CART[i.dataset.r].rate = Math.max(0, Number(i.value) || 0); drawCart(); });
  $("cartbox").querySelectorAll("[data-del]").forEach(b => b.onclick = () => { CART.splice(b.dataset.del, 1); drawCart(); });
  $("addr").onchange = e => { const r = RATES.find(x => x.id === e.target.value); if (r) { CART.push({ description: r.name, quantity: 1, rate: Number(r.price), charge_id: r.id }); drawCart(); } };
  $("cadd").onclick = () => { const n = $("cn").value.trim(), r = Number($("cr").value); if (!n || !(r >= 0) || $("cr").value === "") return; CART.push({ description: n, quantity: 1, rate: r }); drawCart(); };
  $("disc").oninput = upd;
  $("make").onclick = async () => {
    $("make").disabled = true;
    const { data: inv, error } = await C.sb.rpc("create_bill", {
      p_patient: PAT.id, p_category: SUG?.category || "opd", p_items: CART, p_discount: Number($("disc").value) || 0,
      p_discount_reason: $("dr").value.trim() || null, p_encounter: SUG?.encounter_id || null });
    if (error) { err($("cmsg"), error); $("make").disabled = false; return; }
    CART = []; SUG = null; const p = PAT; PAT = null;
    openBill(inv.id, `✓ Bill ${inv.invoice_no} ban gaya — ab payment lo`, p);
  };
}

// ---------------------------------------------------------------- one bill: details, pay, refund, cancel, print
async function openBill(id, note = "") {
  const [{ data: i, error }, { data: items }, { data: pays }, { data: H }] = await Promise.all([
    C.sb.from("invoices").select("*, patients(full_name, uhid, phone, address)").eq("id", id).single(),
    C.sb.from("invoice_items").select("description, quantity, rate").eq("invoice_id", id),
    C.sb.from("payments").select("id, amount, method, reference, note, reverses_id, created_at").eq("invoice_id", id).order("created_at"),
    C.sb.from("hospitals").select("name, upi_id, upi_name").maybeSingle()
  ]);
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const net = i.total - i.discount, paid = (pays || []).reduce((s, p) => s + Number(p.amount), 0), due = Math.round((net - paid) * 100) / 100;
  const refunded = new Set((pays || []).filter(p => p.reverses_id).map(p => p.reverses_id));
  $("body").innerHTML = `
    ${note ? `<div class="card msg ok">${C.esc(note)}</div>` : ""}
    <div class="card">
      <div class="row" style="justify-content:space-between"><h3 style="margin:0">🧾 ${C.esc(i.invoice_no)}</h3><span>${ST[i.status]}</span></div>
      <p class="muted" style="margin:4px 0">${C.esc(i.patients?.full_name)} · ${C.esc(i.patients?.uhid)} · ${dt(i.created_at)} · ${C.esc(i.category.toUpperCase())}</p>
      <table>${(items || []).map(x => `<tr><td>${C.esc(x.description)}</td><td>${x.quantity} × ${rs(x.rate)}</td><td style="text-align:right">${rs(x.quantity * x.rate)}</td></tr>`).join("")}
        <tr><td colspan="2"><b>Kul</b></td><td style="text-align:right">${rs(i.total)}</td></tr>
        ${Number(i.discount) ? `<tr><td colspan="2">Discount <small class="muted">(${C.esc(i.discount_reason || "")})</small></td><td style="text-align:right">− ${rs(i.discount)}</td></tr>` : ""}
        <tr><td colspan="2"><b>Dena hai</b></td><td style="text-align:right"><b>${rs(net)}</b></td></tr>
        <tr><td colspan="2">Mila</td><td style="text-align:right">${rs(paid)}</td></tr>
        <tr><td colspan="2"><b>Baaki</b></td><td style="text-align:right"><b style="color:${due > 0 ? "#b91c1c" : "#15803d"}">${rs(due)}</b></td></tr></table>
      ${i.status === "cancelled" ? `<p class="msg err">Cancel: ${C.esc(i.cancel_reason || "")}</p>` : ""}
      <div class="row" style="gap:6px;margin-top:8px;flex-wrap:wrap">
        <button class="small ghost" id="print">🖨️ Receipt</button>
        ${boss() && i.status !== "cancelled" && paid === 0 ? `<button class="small ghost" id="cx">✖️ Bill cancel</button>` : ""}
        <button class="small ghost" id="back2">← Bills list</button>
      </div></div>
    ${i.status !== "cancelled" && due > 0 ? upiBox(H, due, i.invoice_no) : ""}
    ${i.status !== "cancelled" && due > 0 ? `<div class="card" style="background:#f0fdfa">
      <h3 style="margin:0 0 6px">💵 Payment lo</h3>
      <label>Rakam (baaki ${rs(due)})</label><input id="pa" type="number" min="1" step="0.01" value="${due}">
      <div class="row" style="gap:6px;margin-top:6px;flex-wrap:wrap">${METHODS.map(([m, l], k) => `<button class="small ${k ? "ghost" : ""}" data-m="${m}">${l}</button>`).join("")}</div>
      <input id="pref" placeholder="UPI / card / bank ka transaction number" style="margin-top:6px;display:none">
      <p class="msg" id="pmsg"></p><button class="full" id="pay">Payment save karo</button></div>` : ""}
    <div class="card"><h3 style="margin:0 0 6px">Payments</h3>${(pays || []).length ? pays.map(p => `<div class="row" style="gap:6px;align-items:center;padding:4px 0">
      <div style="flex:1">${Number(p.amount) < 0 ? "↩️ Refund" : "✅"} <b>${rs(p.amount)}</b> · ${C.esc(p.method)}${p.reference ? " · " + C.esc(p.reference) : ""}
        <br><small class="muted">${dt(p.created_at)}${p.note ? " · " + C.esc(p.note) : ""}</small></div>
      ${boss() && Number(p.amount) > 0 && !refunded.has(p.id) ? `<button class="small ghost" data-rf="${p.id}">↩️ Refund</button>` : ""}</div>`).join("") : "<p class='muted' style='margin:0'>Abhi koi payment nahi.</p>"}
      <p class="msg" id="rmsg"></p></div>`;
  $("back2").onclick = () => { TAB = "bills"; C.app.querySelectorAll("#tabs [data-t]").forEach(x => x.classList.toggle("ghost", x.dataset.t !== "bills")); bills(); };
  $("print").onclick = () => receipt(i, items || [], pays || [], net, paid, due);
  let method = "cash";
  C.app.querySelectorAll("[data-m]").forEach(b => b.onclick = () => {
    method = b.dataset.m; C.app.querySelectorAll("[data-m]").forEach(x => x.classList.toggle("ghost", x !== b));
    $("pref").style.display = method === "cash" ? "none" : "";
  });
  if ($("pay")) $("pay").onclick = async () => {
    $("pay").disabled = true;
    const { error } = await C.sb.rpc("record_payment", { p_invoice: id, p_amount: Number($("pa").value), p_method: method, p_reference: $("pref").value.trim() || null });
    if (error) { err($("pmsg"), error); $("pay").disabled = false; return; }
    openBill(id, "✓ Payment save ho gayi");
  };
  if ($("cx")) $("cx").onclick = () => askReason("Bill cancel ka kaaran", async r => {
    const { error } = await C.sb.rpc("cancel_bill", { p_invoice: id, p_reason: r });
    if (error) return err($("rmsg"), error);
    openBill(id, "Bill cancel ho gaya");
  });
  C.app.querySelectorAll("[data-rf]").forEach(b => b.onclick = () => askReason("Refund ka kaaran", async r => {
    const { error } = await C.sb.rpc("refund_payment", { p_payment: b.dataset.rf, p_reason: r });
    if (error) return err($("rmsg"), error);
    openBill(id, "↩️ Refund ho gaya (ulti entry ban gayi)");
  }));
}

function askReason(label, cb) {
  const box = $("rmsg");
  box.className = "msg"; box.innerHTML = `<span class="row" style="gap:6px"><input id="why" placeholder="${C.esc(label)}" style="flex:1"><button class="small" id="whyok">OK</button></span>`;
  $("whyok").onclick = () => { const r = $("why").value.trim(); if (!r) return; cb(r); };
}

async function receipt(i, items, pays, net, paid, due) {
  const { data: h } = await C.sb.from("hospitals").select("name, upi_id, upi_name").maybeSingle();
  $("receipt").innerHTML = `<div class="card" id="rcpt" style="max-width:420px;margin:10px auto;font-size:14px">
    <div style="text-align:center"><b style="font-size:18px">${C.esc(h?.name || C.me.hospital_name || "Hospital")}</b><br><small>Receipt / Bill</small></div>
    <hr><div>Bill: <b>${C.esc(i.invoice_no)}</b> · ${dt(i.created_at)}<br>Patient: <b>${C.esc(i.patients?.full_name)}</b> (${C.esc(i.patients?.uhid)})</div><hr>
    <table style="width:100%">${items.map(x => `<tr><td>${C.esc(x.description)} ${x.quantity > 1 ? "× " + x.quantity : ""}</td><td style="text-align:right">${rs(x.quantity * x.rate)}</td></tr>`).join("")}
      ${Number(i.discount) ? `<tr><td>Discount</td><td style="text-align:right">− ${rs(i.discount)}</td></tr>` : ""}
      <tr><td><b>Kul dena</b></td><td style="text-align:right"><b>${rs(net)}</b></td></tr>
      <tr><td>Mila</td><td style="text-align:right">${rs(paid)}</td></tr><tr><td><b>Baaki</b></td><td style="text-align:right"><b>${rs(due)}</b></td></tr></table>
    <hr><small>${pays.map(p => `${dt(p.created_at)} · ${rs(p.amount)} · ${p.method}${p.reference ? " (" + C.esc(p.reference) + ")" : ""}`).join("<br>")}</small>
    ${i.status !== "cancelled" && due > 0 ? upiBox(h, due, i.invoice_no).replace(' class="card upiqr"', ' class="upiqr"') : ""}
    <p style="text-align:center;margin-top:10px"><small>Dhanyavaad 🙏</small></p></div>
    <div class="row noprint" style="gap:6px;justify-content:center"><button id="rp">🖨️ Print / PDF</button><button class="ghost" id="rc">Band karo</button></div>`;
  $("rp").onclick = () => { document.body.classList.add("printing"); window.print(); setTimeout(() => document.body.classList.remove("printing"), 500); };
  $("rc").onclick = () => { $("receipt").innerHTML = ""; };
  $("receipt").scrollIntoView({ behavior: "smooth" });
}

// ---------------------------------------------------------------- bills list
async function bills(filter = "due") {
  $("body").innerHTML = `<div class="card row" style="gap:6px;flex-wrap:wrap">
      ${[["due", "🔴 Baaki"], ["today", "📅 Aaj ke"], ["all", "Sab (aakhri 100)"]].map(([k, l]) => `<button class="small ${k === filter ? "" : "ghost"}" data-f="${k}">${l}</button>`).join("")}
      <input id="bq" placeholder="Bill no. / patient" style="flex:1;min-width:120px"></div><div id="blist">Loading…</div>`;
  C.app.querySelectorAll("[data-f]").forEach(b => b.onclick = () => bills(b.dataset.f));
  let q = C.sb.from("invoices").select("id, invoice_no, total, discount, status, category, created_at, patients(full_name, uhid, phone)").order("created_at", { ascending: false }).limit(100);
  if (filter === "due") q = q.in("status", ["unpaid", "partial"]);
  if (filter === "today") q = q.gte("created_at", new Date(ymd(ist()) + "T00:00:00+05:30").toISOString());
  const { data, error } = await q;
  if (error) { $("blist").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const draw = () => {
    const s = ($("bq").value || "").toLowerCase();
    const list = data.filter(i => !s || i.invoice_no.toLowerCase().includes(s) || (i.patients?.full_name || "").toLowerCase().includes(s) || (i.patients?.uhid || "").toLowerCase().includes(s));
    $("blist").innerHTML = list.length ? list.map(i => `<div class="card click" data-b="${i.id}" style="padding:8px 12px;margin:6px 0">
      <div class="row" style="justify-content:space-between"><b>${C.esc(i.patients?.full_name || "")}</b><span>${rs(i.total - i.discount)}</span></div>
      <small class="muted">${C.esc(i.invoice_no)} · ${dt(i.created_at)} · ${ST[i.status]}</small></div>`).join("") : `<div class="card"><p class="muted" style="margin:0">Koi bill nahi.</p></div>`;
    C.app.querySelectorAll("[data-b]").forEach(c => c.onclick = () => openBill(c.dataset.b));
  };
  $("bq").oninput = draw; draw();
}

// ---------------------------------------------------------------- day book + expenses
async function dayBook(from = null, to = null, note = "") {
  const today = ymd(ist()); from = from || today; to = to || today;
  const { data, error } = await C.sb.rpc("day_book", { p_from: from, p_to: to });
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const inn = data.filter(r => r.kind === "payment").reduce((s, r) => s + Number(r.amount), 0);
  const ref = -data.filter(r => r.kind === "refund").reduce((s, r) => s + Number(r.amount), 0);
  const out = -data.filter(r => r.kind.startsWith("expense")).reduce((s, r) => s + Number(r.amount), 0);
  const by = {}; data.forEach(r => { by[r.method] = (by[r.method] || 0) + Number(r.amount); });
  const K = { payment: "✅ Aaya", refund: "↩️ Refund", expense: "🔻 Kharcha", expense_reversed: "↩️ Kharcha ulta" };
  $("body").innerHTML = `
    <div class="card row" style="gap:6px;flex-wrap:wrap;align-items:end">
      <div><label>Se</label><input type="date" id="f" value="${from}"></div><div><label>Tak</label><input type="date" id="t" value="${to}"></div>
      <button class="small" id="go">Dikhao</button></div>
    ${note ? `<div class="card msg ok">${C.esc(note)}</div>` : ""}
    <div class="card"><b>Aaya ${rs(inn)}</b> · Refund ${rs(ref)} · Kharcha ${rs(out)} · <b>Bacha ${rs(inn - ref - out)}</b>
      <br><small class="muted">${Object.entries(by).map(([m, v]) => `${m}: ${rs(v)}`).join(" · ") || "—"}</small></div>
    <div class="card" style="overflow-x:auto"><table><tr><th>Samay</th><th>Kya</th><th>Rakam</th><th>Balance</th></tr>${data.map(r => `<tr>
      <td>${dt(r.at)}</td><td>${K[r.kind] || r.kind} · ${C.esc(r.method)}<br><small class="muted">${C.esc(r.detail || "")}</small>
        ${r.kind === "expense" ? `<br><a href="#" data-rx="${r.ref_id}" style="font-size:12px">ulti karo (galat entry)</a>` : ""}</td>
      <td style="color:${Number(r.amount) < 0 ? "#b91c1c" : "#15803d"}">${rs(r.amount)}</td><td>${rs(r.balance)}</td></tr>`).join("") || `<tr><td colspan="4" class="muted">Is samay mein kuch nahi.</td></tr>`}</table></div>
    <div class="card"><h3 style="margin:0 0 6px">🔻 Kharcha likho</h3>
      <div class="row" style="gap:6px"><input id="ec" list="ecats" placeholder="Category (jaise Bijli, Kiraya, Saman)" style="flex:2"><input id="ea" type="number" min="1" placeholder="₹" style="flex:1"></div>
      <datalist id="ecats">${["Bijli bill", "Kiraya", "Saaf-safai", "Office saman", "Dawai kharid", "Marammat", "Chai-nashta", "Petrol", "Internet / phone", "Other"].map(x => `<option value="${x}">`).join("")}</datalist>
      <input id="et" placeholder="Kisko diya (optional)" style="margin-top:6px"><input id="en" placeholder="Note (optional)" style="margin-top:6px">
      <div class="row" style="gap:6px;margin-top:6px;flex-wrap:wrap">${METHODS.map(([m, l], k) => `<button class="small ${k ? "ghost" : ""}" data-em="${m}">${l}</button>`).join("")}</div>
      <p class="msg" id="emsg"></p><button class="full" id="esave">Kharcha save karo</button></div>`;
  $("go").onclick = () => dayBook($("f").value, $("t").value);
  let em = "cash";
  C.app.querySelectorAll("[data-em]").forEach(b => b.onclick = () => { em = b.dataset.em; C.app.querySelectorAll("[data-em]").forEach(x => x.classList.toggle("ghost", x !== b)); });
  $("esave").onclick = async () => {
    const { error } = await C.sb.rpc("record_expense", { p_category: $("ec").value, p_amount: Number($("ea").value), p_paid_to: $("et").value || null, p_method: em, p_note: $("en").value || null, p_day: null });
    if (error) return err($("emsg"), error);
    dayBook(from, to, "✓ Kharcha save ho gaya");
  };
  C.app.querySelectorAll("[data-rx]").forEach(a => a.onclick = e => {
    e.preventDefault();
    const box = $("emsg"); box.className = "msg";
    box.innerHTML = `<span class="row" style="gap:6px"><input id="rxw" placeholder="Ulti karne ka kaaran" style="flex:1"><button class="small" id="rxok">Ulti karo</button></span>`;
    box.scrollIntoView({ behavior: "smooth" });
    $("rxok").onclick = async () => {
      const { error } = await C.sb.rpc("reverse_expense", { p_expense: a.dataset.rx, p_reason: $("rxw").value });
      if (error) return err(box, error);
      dayBook(from, to, "Galat kharcha ulta kar diya (record mein dono entry rahengi)");
    };
  });
}

// ---------------------------------------------------------------- cash close
async function cashClose(note = "") {
  const today = ymd(ist());
  const [{ data: book }, { data: closes }] = await Promise.all([
    C.sb.rpc("day_book", { p_from: today, p_to: today }),
    C.sb.from("cash_closings").select("*").order("day", { ascending: false }).limit(15)
  ]);
  const cash = (book || []).filter(r => r.method === "cash").reduce((s, r) => s + Number(r.amount), 0);
  const done = (closes || []).find(c => c.day === today);
  $("body").innerHTML = `
    ${note ? `<div class="card msg ok">${C.esc(note)}</div>` : ""}
    <div class="card"><h3 style="margin:0 0 6px">💵 Aaj ka cash (${today})</h3>
      <p style="font-size:18px;margin:4px 0">App ke hisaab se galle mein: <b>${rs(cash)}</b></p>
      ${done ? `<p class="msg ok">✓ Aaj ka cash close ho chuka: gina ${rs(done.counted_cash)} · fark ${rs(done.difference)}</p>` : `
      <label>Aapne gin kar kitna paaya?</label><input id="cc" type="number" min="0" step="0.01">
      <label>Fark ho to kaaran</label><input id="cn" placeholder="Jaise: chhutta diya, galti">
      <p class="msg" id="ccmsg"></p><button class="full" id="ccgo">Cash close karo</button>
      <small class="muted">Ek din mein ek hi baar. Close ke baad badla nahi ja sakta.</small>`}</div>
    <div class="card"><h3 style="margin:0 0 6px">Pichhle cash close</h3>${(closes || []).map(c => `<div>${c.day}: app ${rs(c.expected_cash)} · gina ${rs(c.counted_cash)} ·
      <b style="color:${Number(c.difference) ? "#b91c1c" : "#15803d"}">fark ${rs(c.difference)}</b>${c.note ? " · " + C.esc(c.note) : ""}</div>`).join("") || "<p class='muted' style='margin:0'>Abhi koi nahi.</p>"}</div>`;
  if ($("ccgo")) $("ccgo").onclick = async () => {
    const { error } = await C.sb.rpc("close_cash", { p_day: today, p_counted: Number($("cc").value), p_note: $("cn").value || null });
    if (error) return err($("ccmsg"), error);
    cashClose("✓ Aaj ka cash close ho gaya");
  };
}

// ---------------------------------------------------------------- rate list
async function upiSettings() {
  const box = $("upibox"); if (!box) return;
  const { data: h } = await C.sb.from("hospitals").select("name, upi_id, upi_name").maybeSingle();
  const canEdit = ["doctor", "admin"].includes(C.me.role);
  box.innerHTML = `<h3 style="margin:0 0 6px">📱 UPI QR (bill par)</h3>
    <p class="muted" style="margin:0 0 6px;font-size:13px">Hospital ke bank account ki UPI ID daalo (jaise <b>vattehospital@okaxis</b>). Har bill par baaki rakam ka QR apne aap banega. Ye password nahi hai — sirf paisa lene ka pata hai.</p>
    <label>UPI ID</label><input id="upi" value="${C.esc(h?.upi_id || "")}" placeholder="naam@bank" autocapitalize="off" ${canEdit ? "" : "disabled"}>
    <label>QR par naam</label><input id="upn" value="${C.esc(h?.upi_name || h?.name || "")}" ${canEdit ? "" : "disabled"}>
    ${canEdit ? `<button class="full" id="upisv">💾 UPI save</button>` : "<small class='muted'>Sirf Doctor / Admin badal sakte hain.</small>"}<p class="msg" id="upim"></p>
    <div id="upitest"></div>`;
  const test = async () => { const { data: x } = await C.sb.from("hospitals").select("name, upi_id, upi_name").maybeSingle(); if (x?.upi_id) $("upitest").innerHTML = `<small class="muted">Test: ₹1 ka QR — apne phone se scan karke naam check kar lo (pay mat karna).</small>` + upiBox(x, 1, "TEST"); };
  test();
  if ($("upisv")) $("upisv").onclick = async () => {
    const { error } = await C.sb.rpc("set_hospital_upi", { p_upi: $("upi").value, p_name: $("upn").value });
    if (error) return err($("upim"), error);
    $("upim").className = "msg ok"; $("upim").textContent = "✓ UPI save ho gayi"; test();
  };
}

function rateList(note = "") {
  const CAT = { opd: "OPD", ipd: "IPD", lab: "Lab", procedure: "Procedure", bed: "Bed", pharmacy: "Pharmacy", other: "Other" };
  setTimeout(upiSettings, 0);
  $("body").innerHTML = `${note ? `<div class="card msg ok">${C.esc(note)}</div>` : ""}
    <div class="card" id="upibox"></div>
    <div class="card" style="overflow-x:auto"><h3 style="margin:0 0 6px">⚙️ Rate list</h3><table><tr><th>Naam</th><th>Rate (₹)</th><th>Roz ka?</th><th>Chalu</th><th></th></tr>${RATES.map(r => `<tr>
      <td>${C.esc(r.name)}<br><small class="muted">${CAT[r.category]}</small></td>
      <td><input type="number" min="0" value="${r.price}" data-pr="${r.id}" style="width:90px"></td><td>${r.per_day ? "✓" : ""}</td>
      <td><input type="checkbox" data-ac="${r.id}" ${r.active ? "checked" : ""}></td><td><button class="small ghost" data-sv="${r.id}">Save</button></td></tr>`).join("")}</table>
      <p class="msg" id="rmsg2"></p></div>
    <div class="card"><h3 style="margin:0 0 6px">＋ Nayi cheez</h3>
      <input id="nn" placeholder="Naam (jaise X-ray chest)"><div class="row" style="gap:6px;margin-top:6px">
      <select id="nc">${Object.entries(CAT).map(([k, v]) => `<option value="${k}">${v}</option>`).join("")}</select><input id="np" type="number" min="0" placeholder="₹"></div>
      <label style="display:flex;gap:6px;align-items:center;margin-top:6px"><input type="checkbox" id="nd"> Roz ke hisaab se (admit patient)</label>
      <button class="full" id="nadd">Jodo</button></div>`;
  C.app.querySelectorAll("[data-sv]").forEach(b => b.onclick = async () => {
    const id = b.dataset.sv;
    const { error } = await C.sb.from("service_charges").update({ price: Number(C.app.querySelector(`[data-pr="${id}"]`).value), active: C.app.querySelector(`[data-ac="${id}"]`).checked }).eq("id", id);
    if (error) return err($("rmsg2"), error);
    await loadRates(); rateList("✓ Rate save ho gaya (purane bill nahi badlenge)");
  });
  $("nadd").onclick = async () => {
    const { error } = await C.sb.from("service_charges").insert({ name: $("nn").value.trim(), category: $("nc").value, price: Number($("np").value), per_day: $("nd").checked });
    if (error) return err($("rmsg2"), error);
    await loadRates(); rateList("✓ Nayi cheez jud gayi");
  };
}
