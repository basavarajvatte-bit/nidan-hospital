// Vatte Hospital OS — Phase 13: Operations (my attendance & leave, repairs, purchase requests, equipment)
let C, TAB = "me";
const $ = id => document.getElementById(id);
const rs = n => "₹" + Number(n || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 });
const ist = () => new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Kolkata" }));
const ymd = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const dmy = d => d ? new Date(d).toLocaleDateString("en-IN", { day: "2-digit", month: "short" }) : "";
const dt = t => t ? new Date(t).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }) : "";
const tm = t => t ? new Date(t).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }) : "";
const err = (el, e) => { if (el) { el.className = "msg err"; el.textContent = "❌ " + (e.message || e); } };
const ok = (el, t) => { if (el) { el.className = "msg ok"; el.textContent = t; } };
const can = r => r.includes(C.me.role);
const ATT = { present: "✅ Haazir", half_day: "🌓 Aadha din", absent: "❌ Gair-haazir", leave: "🏖️ Chhutti", off: "💤 Off" };
const LK = { casual: "Casual", sick: "Beemari", earned: "Earned", unpaid: "Bina salary", other: "Other" };
const TST = { open: "🔴 Khula", in_progress: "🟡 Kaam chalu", done: "🟢 Theek", cancelled: "✖️ Cancel" };
const PST = { pending_approval: "🟡 Manzoori baaki", approved: "🟢 Manzoor — maal lana hai", received: "✅ Aa gaya", cancelled: "✖️ Mana / cancel" };

export function render(ctx) {
  C = ctx; TAB = "me";
  const tabs = [["me", "🙋 Meri hazri"], ["fix", "🛠️ Repair / shikayat"], ["buy", "🛒 Kharid"], can(["doctor", "admin", "hr"]) && ["assets", "⚙️ Machine list"]].filter(Boolean);
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button><h2 style="margin:0 0 6px">🛠️ Operations</h2>
    <div class="row" id="tabs" style="gap:6px;margin-bottom:10px">${tabs.map(([k, l]) => `<button class="small ${k === TAB ? "" : "ghost"}" data-t="${k}">${l}</button>`).join("")}</div>
    <div id="body"><div class="card">Loading…</div></div>`;
  $("bk").onclick = C.goHome;
  C.app.querySelectorAll("#tabs [data-t]").forEach(b => b.onclick = () => {
    TAB = b.dataset.t; C.app.querySelectorAll("#tabs [data-t]").forEach(x => x.classList.toggle("ghost", x !== b)); show();
  });
  show();
}
function show() { ({ me, fix, buy, assets })[TAB](); }

// ---------------------------------------------------------------- my attendance & leave
async function me() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const { data: s } = await C.sb.from("staff_members").select("id, full_name, designation, shift").eq("profile_id", C.me.id).maybeSingle();
  if (!s) { $("body").innerHTML = `<div class="card"><p>Aapka login abhi kisi staff card se nahi juda.</p><p class="muted">HR / Doctor se kahein: <b>HR → 👥 Staff</b> mein aapke naam par "App login" chunein.</p></div>`; return; }
  const today = ymd(ist()), m0 = today.slice(0, 8) + "01";
  const [{ data: att }, { data: lv }] = await Promise.all([
    C.sb.from("attendance").select("day, status, check_in, check_out").eq("staff_id", s.id).gte("day", m0).order("day", { ascending: false }),
    C.sb.from("leave_requests").select("*").eq("staff_id", s.id).order("created_at", { ascending: false }).limit(10)]);
  const t = (att || []).find(a => a.day === today);
  const cnt = k => (att || []).filter(a => a.status === k).length;
  $("body").innerHTML = `<div class="card"><b>${C.esc(s.full_name)}</b> <small class="muted">${C.esc(s.designation)}</small>
      <p style="margin:6px 0">Aaj: ${t ? ATT[t.status] : "abhi hazri nahi"}${t?.check_in ? ` · aaye ${tm(t.check_in)}` : ""}${t?.check_out ? ` · gaye ${tm(t.check_out)}` : ""}</p>
      ${!t?.check_in ? `<button class="full" id="cin">👋 Check-in (main aa gaya / gayi)</button>` : !t?.check_out ? `<button class="full ghost" id="cout">🏠 Check-out (ja raha / rahi)</button>` : "<p class='muted'>Aaj ka kaam poora ✓</p>"}
      <p class="msg" id="cm"></p>
      <small class="muted">Is mahine: ✅ ${cnt("present")} · 🌓 ${cnt("half_day")} · 🏖️ ${cnt("leave")} · ❌ ${cnt("absent")}</small></div>
    <div class="card"><h3 style="margin:0 0 6px">🏖️ Chhutti maango</h3>
      <div class="row" style="gap:6px"><div style="flex:1"><label>Se</label><input type="date" id="lf" min="${today}"></div><div style="flex:1"><label>Tak</label><input type="date" id="lt" min="${today}"></div></div>
      <label>Kis tarah ki</label><select id="lk">${Object.entries(LK).map(([k, v]) => `<option value="${k}">${v}</option>`).join("")}</select>
      <label>Kaaran</label><input id="lr"><button class="full" id="lgo">Arzi bhejo</button><p class="msg" id="lm"></p>
      ${(lv || []).map(l => `<div style="margin:4px 0;font-size:13px">${{ pending: "🟡 Baaki", approved: "✅ Mili", rejected: "❌ Nahi mili", cancelled: "✖️" }[l.status]} ${dmy(l.from_day)} – ${dmy(l.to_day)} · ${LK[l.kind]}${l.decision_note ? " · " + C.esc(l.decision_note) : ""}</div>`).join("")}</div>`;
  const chk = out => async () => {
    const { error } = await C.sb.rpc("hr_self_check", { p_out: out });
    if (error) return err($("cm"), error);
    me();
  };
  if ($("cin")) $("cin").onclick = chk(false);
  if ($("cout")) $("cout").onclick = chk(true);
  $("lgo").onclick = async () => {
    const { error } = await C.sb.rpc("hr_request_leave", { p_staff: null, p_from: $("lf").value || null, p_to: $("lt").value || null, p_kind: $("lk").value, p_reason: $("lr").value });
    if (error) return err($("lm"), error);
    me(); setTimeout(() => ok($("lm"), "✓ Arzi chali gayi — HR / Doctor ke faisle par notification aayega"), 300);
  };
}

// ---------------------------------------------------------------- repairs
async function fix() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const [{ data: tk }, { data: as }] = await Promise.all([
    C.sb.from("ops_tickets").select("*, ops_assets(name)").order("created_at", { ascending: false }).limit(60),
    C.sb.from("ops_assets").select("id, name, location").neq("status", "retired").order("name")]);
  const boss = can(["doctor", "admin", "hr"]);
  const open = (tk || []).filter(t => ["open", "in_progress"].includes(t.status)), closed = (tk || []).filter(t => !["open", "in_progress"].includes(t.status));
  $("body").innerHTML = `<div class="card"><h3 style="margin:0 0 6px">＋ Kuch kharab hai? Likho</h3>
      <label>Kya kharab hai</label><input id="tt" placeholder="Jaise: Ward 2 ka pankha nahi chal raha">
      <div class="row" style="gap:6px"><div style="flex:1"><label>Kahan</label><input id="tl" placeholder="Ward 2"></div>
        <div style="flex:1"><label>Machine (agar hai)</label><select id="ta"><option value="">—</option>${(as || []).map(a => `<option value="${a.id}">${C.esc(a.name)}${a.location ? " · " + C.esc(a.location) : ""}</option>`).join("")}</select></div></div>
      <label class="row" style="gap:6px"><input type="checkbox" id="tu" style="width:auto"> 🚨 Urgent (patient ka kaam ruka hai)</label>
      <button class="full" id="tgo">Bhejo</button><p class="msg" id="tm"></p></div>
    ${open.map(t => `<div class="card" ${t.priority === "urgent" ? `style="border-color:#fca5a5"` : ""}>
      <div class="row" style="justify-content:space-between"><b>#${t.ticket_no} ${t.priority === "urgent" ? "🚨 " : ""}${C.esc(t.title)}</b><span>${TST[t.status]}</span></div>
      <small class="muted">${C.esc(t.location || "")}${t.ops_assets ? " · " + C.esc(t.ops_assets.name) : ""} · ${dt(t.created_at)}${t.assigned_to ? " · " + C.esc(t.assigned_to) : ""}</small>
      ${boss || t.reported_by === C.me.id ? `<div class="row" style="gap:6px;margin-top:6px">
        ${t.status === "open" && boss ? `<button class="small ghost" data-w="${t.id}">🔧 Kaam shuru</button>` : ""}
        ${boss ? `<button class="small" data-d="${t.id}">✅ Theek ho gaya</button>` : ""}<button class="small ghost" data-c="${t.id}">✖ Cancel</button></div>` : ""}
      <p class="msg" id="m${t.id}"></p></div>`).join("") || `<div class="card"><p class="muted">Koi khula repair nahi ✓</p></div>`}
    ${closed.length ? `<div class="card"><h4 style="margin:0 0 6px">Band hue</h4>${closed.slice(0, 15).map(t => `<div style="margin:4px 0;font-size:13px">${TST[t.status]} #${t.ticket_no} ${C.esc(t.title)}${t.done_note ? " — " + C.esc(t.done_note) : ""}${t.cost ? " · " + rs(t.cost) : ""}</div>`).join("")}</div>` : ""}`;
  $("tgo").onclick = async () => {
    const { error } = await C.sb.rpc("ops_open_ticket", { p_title: $("tt").value, p_location: $("tl").value, p_asset: $("ta").value || null, p_priority: $("tu").checked ? "urgent" : "normal" });
    if (error) return err($("tm"), error);
    fix();
  };
  const upd = (sel, st) => $("body").querySelectorAll(sel).forEach(b => b.onclick = async () => {
    const id = b.dataset.w || b.dataset.d || b.dataset.c;
    let who = null, note = null, cost = null;
    if (st === "in_progress") who = prompt("Kaun theek karega? (naam / mistri)") || null;
    if (st === "done") { note = prompt("Kya theek kiya?") || ""; if (!note.trim()) return; const c = prompt("Kharcha ₹ (nahi to khaali)") || ""; cost = c ? Number(c) : null; }
    const { error } = await C.sb.rpc("ops_update_ticket", { p_id: id, p_status: st, p_assigned: who, p_note: note, p_cost: cost });
    if (error) return err($("m" + id), error);
    fix();
  });
  upd("[data-w]", "in_progress"); upd("[data-d]", "done"); upd("[data-c]", "cancelled");
}

// ---------------------------------------------------------------- purchase requests
let ITEMS = [{}];
async function buy() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const { data } = await C.sb.from("purchases").select("*, purchase_items(description, quantity, rate), suppliers(name)")
    .eq("purpose", "general").order("created_at", { ascending: false }).limit(40);
  const boss = can(["doctor", "admin"]), payer = can(["doctor", "admin", "accountant"]), recv = can(["doctor", "admin", "accountant", "hr"]);
  $("body").innerHTML = `<div class="card"><h3 style="margin:0 0 6px">＋ Kuch kharidna hai? (dawa ke alawa)</h3>
      <label>Kis kaam ke liye</label><input id="bn" placeholder="Jaise: Reception ke liye printer paper">
      <label>Dukaan / supplier (agar pata hai)</label><input id="bs">
      <div id="bl"></div><button class="small ghost" id="ba">＋ Ek aur cheez</button>
      <h3 id="bt" style="margin:8px 0 4px"></h3><button class="full" id="bgo">Manzoori ke liye bhejo</button><p class="msg" id="bm"></p></div>
    ${(data || []).map(p => `<div class="card">
      <div class="row" style="justify-content:space-between"><b>${C.esc(p.note || "Kharid")}</b><span>${PST[p.status] || p.status}</span></div>
      <small class="muted">${dt(p.created_at)} · andaazan ${rs(p.total)}${p.suppliers ? " · " + C.esc(p.suppliers.name) : ""}${p.decision_note ? " · " + C.esc(p.decision_note) : ""}</small>
      <div style="font-size:13px">${p.purchase_items.map(x => `${C.esc(x.description)} × ${x.quantity}${Number(x.rate) ? " @ " + rs(x.rate) : ""}`).join("<br>")}</div>
      <div class="row" style="gap:6px;margin-top:6px">
        ${p.status === "pending_approval" && boss ? `<button class="small" data-y="${p.id}">✅ Manzoor</button><button class="small ghost" data-n="${p.id}">❌ Mana</button>` : ""}
        ${p.status === "approved" && recv ? `<button class="small" data-r="${p.id}">📦 Maal aa gaya</button>` : ""}</div>
      <p class="msg" id="m${p.id}"></p></div>`).join("")}`;
  const draw = () => {
    $("bl").innerHTML = ITEMS.map((x, i) => `<div class="row" style="gap:6px" data-i="${i}"><input data-k="d" placeholder="Cheez" value="${C.esc(x.description || "")}" style="flex:3">
      <input data-k="q" type="number" min="1" placeholder="Kitne" value="${x.quantity || ""}" style="flex:1"><input data-k="r" type="number" min="0" placeholder="Rate ₹" value="${x.rate ?? ""}" style="flex:1"></div>`).join("");
    $("bl").querySelectorAll("input").forEach(e => e.oninput = read);
    read();
  };
  const read = () => {
    ITEMS = [...$("bl").querySelectorAll("[data-i]")].map(r => ({ description: r.querySelector("[data-k=d]").value, quantity: Number(r.querySelector("[data-k=q]").value) || 0, rate: r.querySelector("[data-k=r]").value === "" ? null : Number(r.querySelector("[data-k=r]").value) }));
    $("bt").textContent = "Andaazan: " + rs(ITEMS.reduce((s, x) => s + x.quantity * (x.rate || 0), 0));
  };
  draw();
  $("ba").onclick = () => { read(); ITEMS.push({}); draw(); };
  $("bgo").onclick = async () => {
    read();
    const { error } = await C.sb.rpc("proc_request", { p_supplier: $("bs").value, p_items: ITEMS.filter(x => x.description.trim()), p_note: $("bn").value });
    if (error) return err($("bm"), error);
    ITEMS = [{}]; buy();
  };
  const dec = (sel, yes) => $("body").querySelectorAll(sel).forEach(b => b.onclick = async () => {
    const id = b.dataset.y || b.dataset.n, note = yes ? "" : (prompt("Mana karne ka kaaran?") || "");
    if (!yes && !note.trim()) return;
    const { error } = await C.sb.rpc("proc_decide", { p_id: id, p_approve: yes, p_note: note });
    if (error) return err($("m" + id), error);
    buy();
  });
  dec("[data-y]", true); dec("[data-n]", false);
  $("body").querySelectorAll("[data-r]").forEach(b => b.onclick = async () => {
    const id = b.dataset.r, bill = prompt("Dukaan ke bill ka number (nahi to khaali)") || "";
    let amt = null, method = null;
    if (payer) {
      const a = prompt("Kitna paisa diya ₹? (abhi nahi diya to khaali — Accounts se baad mein)") || "";
      if (a) { amt = Number(a); method = (prompt("Kaise diya? cash / upi / bank", "cash") || "cash").trim().toLowerCase(); }
    }
    const { error } = await C.sb.rpc("proc_receive", { p_id: id, p_invoice_no: bill, p_amount: amt, p_method: method });
    if (error) return err($("m" + id), error);
    buy();
  });
}

// ---------------------------------------------------------------- equipment
async function assets(edit = null) {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const { data } = await C.sb.from("ops_assets").select("*").order("name");
  const a = edit ? data.find(x => x.id === edit) : null;
  const due = x => x.service_every_days && x.last_service ? new Date(new Date(x.last_service).getTime() + x.service_every_days * 864e5) : null;
  const today = new Date(ymd(ist()));
  $("body").innerHTML = `<div class="card"><h3 style="margin:0 0 6px">${a ? "✏️ Machine badlo" : "＋ Nayi machine / saaman"}</h3>
      <div class="row" style="gap:6px"><div style="flex:2"><label>Naam</label><input id="n" value="${C.esc(a?.name || "")}" placeholder="ECG machine"></div>
        <div style="flex:1"><label>Kahan</label><input id="l" value="${C.esc(a?.location || "")}"></div></div>
      <div class="row" style="gap:6px"><div style="flex:1"><label>Serial no.</label><input id="sn" value="${C.esc(a?.serial_no || "")}"></div>
        <div style="flex:1"><label>Service wala</label><input id="v" value="${C.esc(a?.vendor || "")}"></div><div style="flex:1"><label>Uska phone</label><input id="vp" value="${C.esc(a?.vendor_phone || "")}"></div></div>
      <div class="row" style="gap:6px"><div style="flex:1"><label>Aakhri service</label><input type="date" id="ls" value="${a?.last_service || ""}" max="${ymd(ist())}"></div>
        <div style="flex:1"><label>Har kitne din mein service</label><input type="number" id="ev" min="7" max="1095" value="${a?.service_every_days || ""}" placeholder="180"></div>
        <div style="flex:1"><label>Haalat</label><select id="st">${[["working", "Chalu"], ["down", "Band / kharab"], ["retired", "Hata di"]].map(([k, v]) => `<option value="${k}" ${a?.status === k ? "selected" : ""}>${v}</option>`).join("")}</select></div></div>
      <button class="full" id="sv">💾 Save</button>${a ? `<button class="ghost full" id="nw">Nayi jodo</button>` : ""}<p class="msg" id="am"></p></div>
    <div class="card" style="overflow-x:auto"><table><tr><th>Machine</th><th>Haalat</th><th>Agli service</th></tr>${(data || []).map(x => { const d = due(x); return `<tr data-e="${x.id}" style="cursor:pointer;${x.status === "retired" ? "opacity:.5" : ""}">
      <td>${C.esc(x.name)}<br><small class="muted">${C.esc(x.location || "")}${x.vendor_phone ? " · 📞 " + C.esc(x.vendor_phone) : ""}</small></td>
      <td>${{ working: "🟢 Chalu", down: "🔴 Band", retired: "⚪ Hata di" }[x.status]}</td>
      <td>${d ? (d <= today ? "🔴 " : (d - today) / 864e5 <= 7 ? "🟠 " : "") + dmy(d) : "—"}</td></tr>`; }).join("") || "<tr><td colspan=3 class='muted'>Abhi koi machine nahi</td></tr>"}</table></div>`;
  $("body").querySelectorAll("[data-e]").forEach(r => r.onclick = () => assets(r.dataset.e));
  if ($("nw")) $("nw").onclick = () => assets();
  $("sv").onclick = async () => {
    const { error } = await C.sb.rpc("ops_save_asset", { p_id: a?.id || null, p_name: $("n").value, p_location: $("l").value, p_serial: $("sn").value,
      p_vendor: $("v").value, p_vendor_phone: $("vp").value, p_last_service: $("ls").value || null, p_every: $("ev").value ? Number($("ev").value) : null, p_status: $("st").value });
    if (error) return err($("am"), error);
    await assets(); ok($("am"), "✓ Save ho gaya");
  };
}
