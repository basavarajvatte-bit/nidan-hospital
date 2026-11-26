// Vatte Hospital OS — Phase 15: Boss AI (Doctor's control room)
// One screen: what needs you now, today's numbers vs yesterday / 7-day average, month vs target, 30-day trend, full AI report, Boss AI chat.
// Boss AI only reads; every change still goes through the department screen or the approval queue.
let C, O = null, METRIC = "opd";
const $ = id => document.getElementById(id);
const rs = n => "₹" + Number(n || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 });
const num = n => Number(n || 0).toLocaleString("en-IN", { maximumFractionDigits: 1 });
const LV = { 1: ["🔴", "Abhi turant", "#fff1f2", "#fca5a5"], 2: ["🟡", "Aaj", "#fffbeb", "#fde68a"], 3: ["⚪", "Dhyan mein rakhein", "#f8fafc", "#e2e8f0"] };
const M = {
  opd: ["🧑‍⚕️ OPD patient", num], new_patients: ["🆕 Naye patient", num], admissions: ["🛏️ Admit", num], discharges: ["🏠 Discharge", num],
  collection: ["💰 Paisa aaya", rs], expenses: ["💸 Kharcha", rs], pharmacy_sale: ["💊 Pharmacy bikri", rs], lab_tests: ["🧪 Lab test", num],
  avg_wait_min: ["⏱️ OPD intezaar (min)", num], incidents: ["⚠️ Ghatna", num]
};
const TG = { opd: "OPD patient / mahina", new_patients: "Naye patient / mahina", admissions: "Admit / mahina", collection: "Paisa aaya ₹ / mahina",
  pharmacy_sale: "Pharmacy bikri ₹ / mahina", lab_tests: "Lab test / mahina", expenses_max: "Kharcha zyada se zyada ₹ / mahina", avg_wait_max: "OPD intezaar zyada se zyada (min)" };

export async function render(ctx) {
  C = ctx;
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button>
    <div class="row" style="justify-content:space-between;align-items:center"><h2 style="margin:0">🤖 Boss AI</h2>
      <div class="row" style="gap:6px"><button class="small" id="ask">💬 Boss AI se poochho</button><button class="small ghost" id="rf">🔄</button></div></div>
    <div id="body"><div class="card">Loading…</div></div>`;
  $("bk").onclick = C.goHome;
  $("ask").onclick = () => import("./chat.js?v=" + window.APP_VERSION).then(m => m.render(C, "boss"));
  $("rf").onclick = load;
  load();
}

function open(id) {
  C.goHome();
  setTimeout(() => document.querySelector(`.tile[data-id="${id}"]`)?.click(), 50);
}

async function load() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const { data, error } = await C.sb.rpc("boss_overview");
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  O = data;
  const P = O.priorities || [];
  const h = new Date().toLocaleString("en-US", { timeZone: "Asia/Kolkata", hour: "numeric", hour12: false });
  const hi = h < 12 ? "Suprabhat" : h < 17 ? "Namaste" : "Shubh sandhya";
  $("body").innerHTML = `
    <div class="card" style="background:#f0fdfa;border-color:#99f6e4">
      <b>${hi}${C.me.full_name ? ", " + C.esc(C.me.full_name) : ""} 🙏</b><br>
      <span>${P.filter(p => p.level === 1).length ? `🔴 <b>${P.filter(p => p.level === 1).length} cheez turant dekhni hai.</b>` : P.length ? "Koi turant khatra nahi. Neeche aaj ke kaam." : "✅ Sab theek chal raha hai — koi zaroori kaam baaki nahi."}</span><br>
      <small class="muted">Abhi admit: ${O.ipd_now} · Bed khali: ${O.beds_free}/${O.beds_total}</small></div>
    <h3 style="margin:12px 0 6px">🎯 Abhi kya zaroori hai</h3>
    ${P.map(p => `<div class="card" style="background:${LV[p.level][2]};border-color:${LV[p.level][3]};padding:12px">
        <div class="row" style="justify-content:space-between;gap:6px"><span>${LV[p.level][0]} <b>${C.esc(p.title)}</b><br><small class="muted">${C.esc(p.area)}${p.detail ? " · " + C.esc(p.detail) : ""}</small></span>
        <button class="small" data-m="${C.esc(p.module)}">Kholo →</button></div></div>`).join("") || `<div class="card"><p class="muted">Kuch baaki nahi ✓</p></div>`}
    <h3 style="margin:12px 0 6px">📊 Aaj</h3><div class="grid" id="tiles"></div>
    <h3 style="margin:12px 0 6px">🗓️ Is mahine (kal tak) vs target</h3><div class="card" id="month"></div>
    <h3 style="margin:12px 0 6px">📈 Pichhle 30 din</h3><div class="card"><select id="ms">${Object.entries(M).map(([k, v]) => `<option value="${k}" ${k === METRIC ? "selected" : ""}>${v[0]}</option>`).join("")}</select><div id="chart"></div></div>
    <div class="card"><button class="full" id="rep">🤖 Poori report abhi banao (sab department check)</button><div id="repout"></div></div>
    ${C.me.role === "doctor" ? `<div class="card"><h3 style="margin:0 0 6px">🎯 Mahine ke target</h3><div id="tg"></div><p class="msg" id="tgm"></p></div>` : ""}`;
  $("body").querySelectorAll("[data-m]").forEach(b => b.onclick = () => open(b.dataset.m));
  tiles(); month(); chart();
  $("ms").onchange = () => { METRIC = $("ms").value; chart(); };
  $("rep").onclick = report;
  if ($("tg")) targets();
}

function tiles() {
  const t = O.today || {}, y = O.yesterday || {}, a = O.avg7 || {};
  const keys = ["opd", "new_patients", "admissions", "collection", "expenses", "pharmacy_sale", "lab_tests", "avg_wait_min"];
  $("tiles").innerHTML = keys.map(k => {
    const [label, fmt] = M[k], v = t[k], av = a[k];
    const good = k === "expenses" || k === "avg_wait_min" ? -1 : 1;
    const arrow = v == null || av == null || Number(av) === 0 ? "" : Number(v) > Number(av) ? (good > 0 ? "🟢▲" : "🔴▲") : Number(v) < Number(av) ? (good > 0 ? "🟠▼" : "🟢▼") : "＝";
    return `<div class="tile" style="cursor:default"><span style="font-size:13px">${label}</span><b style="font-size:22px;display:block">${v == null ? "—" : fmt(v)}</b>
      <small>kal ${y[k] == null ? "—" : fmt(y[k])} · 7 din avg ${av == null ? "—" : fmt(av)} ${arrow}</small></div>`;
  }).join("");
}

function month() {
  const m = O.mtd || {}, tg = O.targets || {}, done = Math.max(1, O.day_of_month - 1), days = O.month_days;
  const rows = [["opd", "opd"], ["new_patients", "new_patients"], ["admissions", "admissions"], ["collection", "collection"], ["pharmacy_sale", "pharmacy_sale"], ["lab_tests", "lab_tests"], ["expenses", "expenses_max"]];
  $("month").innerHTML = rows.map(([k, tk]) => {
    const v = Number(m[k] || 0), target = tg[tk], fmt = M[k][1];
    if (target == null) return `<div style="margin:6px 0">${M[k][0]}: <b>${fmt(v)}</b> <small class="muted">· mahine ke ant tak andaazan ${fmt(v / done * days)}</small></div>`;
    const pct = Math.min(100, Math.round(100 * v / Number(target || 1))), should = Math.round(100 * done / days);
    const ok = tk === "expenses_max" ? pct <= should : pct >= should;
    return `<div style="margin:8px 0">${M[k][0]}: <b>${fmt(v)}</b> / ${fmt(target)} <small class="muted">(${pct}% · aaj tak ${should}% hona chahiye)</small>
      <div style="background:#e2e8f0;border-radius:6px;height:10px;position:relative;margin-top:3px"><div style="width:${pct}%;background:${ok ? "#0f766e" : "#f59e0b"};height:10px;border-radius:6px"></div>
      <div style="position:absolute;left:${should}%;top:-3px;width:2px;height:16px;background:#334155"></div></div></div>`;
  }).join("") + `<p class="muted" style="font-size:12px;margin:6px 0 0">Kaali line = aaj tak kitna hona chahiye. Hara = theek, peela = peeche.</p>`;
}

function chart() {
  const S = O.series || [], fmt = M[METRIC][1];
  const vals = S.map(s => Number(s.m?.[METRIC] || 0)), max = Math.max(1, ...vals);
  const W = 600, H = 140, bw = W / Math.max(1, S.length);
  $("chart").innerHTML = S.length ? `<svg viewBox="0 0 ${W} ${H + 18}" style="width:100%;height:auto">
      ${S.map((s, i) => { const h = Math.round(vals[i] / max * H); const d = new Date(s.day); const wk = d.getDay() === 0;
        return `<rect x="${i * bw + 2}" y="${H - h}" width="${bw - 4}" height="${h}" rx="2" fill="${wk ? "#94a3b8" : "#0f766e"}"><title>${s.day}: ${fmt(vals[i])}</title></rect>
          ${i % 5 === 0 ? `<text x="${i * bw + bw / 2}" y="${H + 14}" font-size="10" text-anchor="middle" fill="#64748b">${d.getDate()}/${d.getMonth() + 1}</text>` : ""}`; }).join("")}
    </svg><small class="muted">Sabse zyada: ${fmt(max)} · Kul: ${fmt(vals.reduce((a, b) => a + b, 0))} · Grey = Ravivar</small>` : "<p class='muted'>Abhi data nahi.</p>";
}

async function report() {
  $("rep").disabled = true; $("repout").innerHTML = `<p class="muted">⚙️ Sab department check ho rahe hain…</p>`;
  const { data: t, error } = await C.sb.rpc("agent_submit", { p_action: "boss.daily_report", p_input: {} });
  $("rep").disabled = false;
  if (error) { $("repout").innerHTML = `<p class="msg err">❌ ${C.esc(error.message)}</p>`; return; }
  const items = t.result?.items || [];
  $("repout").innerHTML = `<p><b>${C.esc(t.summary || t.error || "")}</b></p>${items.map(x => `<div style="margin:5px 0;font-size:14px">${x.alert || x.status === "failed" ? "⚠️" : "✓"} <b>${C.esc(x.title)}</b>: ${C.esc(x.summary || "")}</div>`).join("")}`;
}

function targets() {
  const tg = O.targets || {};
  $("tg").innerHTML = Object.entries(TG).map(([k, l]) => `<div class="row" style="gap:6px;margin:4px 0"><span style="flex:2">${l}</span>
      <input type="number" min="0" data-k="${k}" value="${tg[k] ?? ""}" placeholder="—" style="flex:1"></div>`).join("") + `<button class="full" id="tgs">💾 Target save</button>`;
  $("tgs").onclick = async () => {
    for (const el of $("tg").querySelectorAll("[data-k]")) {
      const v = el.value === "" ? null : Number(el.value);
      if ((tg[el.dataset.k] ?? null) === v) continue;
      const { error } = await C.sb.rpc("boss_set_target", { p_metric: el.dataset.k, p_value: v });
      if (error) { $("tgm").className = "msg err"; $("tgm").textContent = "❌ " + error.message; return; }
    }
    await load(); const m = $("tgm"); if (m) { m.className = "msg ok"; m.textContent = "✓ Target save"; }
  };
}
