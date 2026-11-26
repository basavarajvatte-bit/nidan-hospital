// Vatte Hospital OS — Phase 12: Laboratory (write tests, sample, results, report, critical alerts, test list)
// The server checks every value against normal / critical ranges itself; results are never edited — a change after the report needs a reason.
let C, TAB = "work", TESTS = [], PAT = null;
const $ = id => document.getElementById(id);
const rs = n => "₹" + Number(n || 0).toLocaleString("en-IN", { maximumFractionDigits: 2 });
const dt = t => t ? new Date(t).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }) : "";
const clean = s => String(s || "").replace(/[%,()"\\*]/g, "").trim();
const err = (el, e) => { if (el) { el.className = "msg err"; el.textContent = "❌ " + (e.message || e); } };
const ok = (el, t) => { if (el) { el.className = "msg ok"; el.textContent = t; } };
const ST = { ordered: "🩸 Sample lena hai", sample_collected: "🧪 Sample aa gaya", processing: "⚙️ Chal raha hai", reported: "✅ Report", cancelled: "✖️ Cancel" };
const FLAG = { low: ["L", "#b45309"], high: ["H", "#b45309"], crit_low: ["CRITICAL L", "#dc2626"], crit_high: ["CRITICAL H", "#dc2626"], abnormal: ["!", "#b45309"] };
const can = roles => roles.includes(C.me.role);

export function render(ctx) {
  C = ctx; PAT = null;
  const tabs = [["work", "🧪 Kaam"], can(["doctor", "nurse", "lab"]) && ["order", "➕ Test likho"], ["crit", "⚠️ Critical"], ["reports", "📄 Reports"],
                can(["doctor", "admin", "lab"]) && ["tests", "⚙️ Test list"]].filter(Boolean);
  TAB = tabs[0][0];
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button>
    <h2 style="margin:0 0 6px">🧪 Laboratory</h2>
    <div class="row" id="tabs" style="gap:6px;margin-bottom:10px">${tabs.map(([k, l]) => `<button class="small ${k === TAB ? "" : "ghost"}" data-t="${k}">${l}</button>`).join("")}</div>
    <div id="body"><div class="card">Loading…</div></div><div id="receipt"></div>`;
  $("bk").onclick = C.goHome;
  C.app.querySelectorAll("#tabs [data-t]").forEach(b => b.onclick = () => go(b.dataset.t));
  loadTests().then(show);
}
function go(t) {
  TAB = t; C.app.querySelectorAll("#tabs [data-t]").forEach(x => x.classList.toggle("ghost", x.dataset.t !== t));
  $("receipt").innerHTML = ""; show();
}
async function loadTests() {
  const { data } = await C.sb.from("lab_tests").select("*, lab_test_params(*)").order("ord").order("name");
  TESTS = data || [];
}
function show() { ({ work, order, crit, reports, tests: testList })[TAB](); }

// ---------------------------------------------------------------- worklist
async function work() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const { data, error } = await C.sb.from("lab_orders")
    .select("id, status, urgent, note, sample_no, ordered_at, sample_collected_at, patient_id, test_id, patients(full_name, uhid, gender, age_years), lab_tests(name, sample_type, tat_hours)")
    .in("status", ["ordered", "sample_collected", "processing"]).order("urgent", { ascending: false }).order("ordered_at").limit(200);
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  if (!data.length) { $("body").innerHTML = `<div class="card"><p class="muted">Koi test baaki nahi ✓</p></div>`; return; }
  // group by patient
  const byP = {};
  for (const o of data) (byP[o.patient_id] ||= { p: o.patients, list: [] }).list.push(o);
  const late = o => (Date.now() - new Date(o.ordered_at)) / 36e5 > (o.lab_tests?.tat_hours || 24);
  $("body").innerHTML = Object.entries(byP).map(([pid, g]) => `<div class="card">
      <b>${C.esc(g.p?.full_name)}</b> <small class="muted">${C.esc(g.p?.uhid)} · ${C.esc(g.p?.gender || "")} ${g.p?.age_years ? g.p.age_years + " yr" : ""}</small>
      <table style="margin-top:6px">${g.list.map(o => `<tr>
        <td>${o.urgent ? "🚨 " : ""}<b>${C.esc(o.lab_tests?.name)}</b><br><small class="muted">${C.esc(o.lab_tests?.sample_type || "")} · likha ${dt(o.ordered_at)}${o.sample_no ? " · " + C.esc(o.sample_no) : ""}${late(o) ? " · <span style='color:var(--red)'>late</span>" : ""}${o.note ? "<br>📝 " + C.esc(o.note) : ""}</small></td>
        <td>${ST[o.status]}</td>
        <td>${o.status === "ordered" && can(["doctor", "nurse", "lab"]) ? `<input type="checkbox" data-s="${o.id}" data-p="${pid}" style="width:auto">` : ""}
            ${o.status !== "ordered" && can(["doctor", "lab"]) ? `<button class="small" data-r="${o.id}">✍️ Result</button>` : ""}
            ${can(["doctor", "lab"]) ? `<button class="small ghost" data-x="${o.id}">✖</button>` : ""}</td></tr>`).join("")}</table>
      ${g.list.some(o => o.status === "ordered") && can(["doctor", "nurse", "lab"]) ? `<button class="small" data-col="${pid}" style="margin-top:6px">🩸 Tick kiye test ka sample liya</button>` : ""}
      <p class="msg" id="m${pid}"></p></div>`).join("");
  $("body").querySelectorAll("[data-col]").forEach(b => {
    const pid = b.dataset.col;
    $("body").querySelectorAll(`[data-s][data-p="${pid}"]`).forEach(c => c.checked = true);
    b.onclick = async () => {
      const ids = [...$("body").querySelectorAll(`[data-s][data-p="${pid}"]:checked`)].map(c => c.dataset.s);
      if (!ids.length) return err($("m" + pid), "Kam se kam ek test tick karein");
      const { data: sn, error } = await C.sb.rpc("lab_collect", { p_orders: ids });
      if (error) return err($("m" + pid), error);
      work(); setTimeout(() => alert(`Sample number: ${sn}\nTube par ye number likhein.`), 200);
    };
  });
  $("body").querySelectorAll("[data-r]").forEach(b => b.onclick = () => resultForm(b.dataset.r));
  $("body").querySelectorAll("[data-x]").forEach(b => b.onclick = async () => {
    const why = prompt("Test cancel karne ka kaaran?") || "";
    if (!why.trim()) return;
    const { error } = await C.sb.rpc("lab_cancel", { p_order: b.dataset.x, p_reason: why });
    if (error) return alert("❌ " + error.message);
    work();
  });
}

function rangeText(p, g) {
  if (p.kind === "choice") return p.ref_text || (p.abnormal_choices?.length ? "Normal: " + p.choices.filter(c => !p.abnormal_choices.includes(c)).join(" / ") : "");
  if (p.kind === "text") return p.ref_text || "";
  const f = g === "female";
  const lo = f && p.ref_low_f != null ? p.ref_low_f : p.ref_low, hi = f && p.ref_high_f != null ? p.ref_high_f : p.ref_high;
  return p.ref_text || (lo != null && hi != null ? `${lo} – ${hi}` : lo != null ? `≥ ${lo}` : hi != null ? `≤ ${hi}` : "");
}
// same rule as the server (only to show colour while typing; the server decides)
function localFlag(p, g, v) {
  if (v === "" || p.kind === "text") return "";
  if (p.kind === "choice") return p.abnormal_choices?.includes(v) ? "abnormal" : "";
  const n = Number(String(v).replace(/,/g, "")); if (isNaN(n)) return "bad";
  const f = g === "female";
  const lo = f && p.ref_low_f != null ? p.ref_low_f : p.ref_low, hi = f && p.ref_high_f != null ? p.ref_high_f : p.ref_high;
  if (p.crit_low != null && n < p.crit_low) return "crit_low";
  if (p.crit_high != null && n > p.crit_high) return "crit_high";
  if (lo != null && n < lo) return "low";
  if (hi != null && n > hi) return "high";
  return "";
}
const badge = f => f === "bad" ? `<b style="color:#dc2626">number?</b>` : FLAG[f] ? `<b style="color:${FLAG[f][1]}">${FLAG[f][0]}</b>` : "";

async function resultForm(id) {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const [{ data: o }, { data: cur }] = await Promise.all([
    C.sb.from("lab_orders").select("*, patients(full_name, uhid, gender, age_years), lab_tests(name)").eq("id", id).single(),
    C.sb.from("lab_current").select("param_id, value_text, flag").eq("order_id", id)]);
  const t = TESTS.find(x => x.id === o.test_id);
  const params = (t?.lab_test_params || []).filter(p => p.active).sort((a, b) => a.ord - b.ord);
  const val = Object.fromEntries((cur || []).map(c => [c.param_id, c.value_text]));
  const g = o.patients?.gender, done = o.status === "reported";
  $("body").innerHTML = `<button class="ghost small" id="bk2">← Kaam list</button><div class="card">
    <h3 style="margin:0">${C.esc(o.lab_tests?.name)}</h3>
    <small class="muted">${C.esc(o.patients?.full_name)} · ${C.esc(o.patients?.uhid)} · ${C.esc(g || "")} ${o.patients?.age_years ? o.patients.age_years + " yr" : ""} · Sample ${C.esc(o.sample_no || "")}</small>
    ${done ? `<p class="msg err">⚠️ Report ho chuki hai. Badlav karoge to kaaran likhna padega aur report par "Amended" likha aayega.</p>` : ""}
    <table style="margin-top:8px"><tr><th>Jaanch</th><th>Result</th><th>Normal</th><th></th></tr>${params.map(p => `<tr>
      <td>${C.esc(p.name)}${p.unit ? ` <small class="muted">${C.esc(p.unit)}</small>` : ""}</td>
      <td>${p.kind === "choice" ? `<select data-p="${p.id}"><option value="">—</option>${p.choices.map(c => `<option ${val[p.id] === c ? "selected" : ""}>${C.esc(c)}</option>`).join("")}</select>`
          : `<input data-p="${p.id}" ${p.kind === "number" ? `inputmode="decimal"` : ""} value="${C.esc(val[p.id] || "")}" style="width:110px">`}</td>
      <td><small>${C.esc(rangeText(p, g))}</small></td><td id="f${p.id}">${badge(localFlag(p, g, val[p.id] || ""))}</td></tr>`).join("")}</table>
    ${done ? `<label>Badalne ka kaaran</label><input id="why">` : ""}
    <div class="row" style="gap:6px;margin-top:10px">
      ${done ? "" : `<button class="ghost" id="draft">💾 Abhi save (adhoora)</button>`}
      <button id="fin">${done ? "✅ Badlav save karo" : "✅ Final report"}</button></div>
    <p class="msg" id="rmsg"></p></div>`;
  $("bk2").onclick = work;
  $("body").querySelectorAll("[data-p]").forEach(el => (el.oninput = el.onchange = () => {
    const p = params.find(x => x.id === el.dataset.p); $("f" + p.id).innerHTML = badge(localFlag(p, g, el.value.trim()));
  }));
  const save = async final => {
    const rows = [...$("body").querySelectorAll("[data-p]")].map(el => ({ param_id: el.dataset.p, value: el.value.trim() }));
    if (final && rows.some(r => ["crit_low", "crit_high"].includes(localFlag(params.find(p => p.id === r.param_id), g, r.value)))
        && !confirm("⚠️ CRITICAL value hai. Machine / sample dobara check kar liya? Final karte hi Doctor aur Sister ko alert jayega.")) return;
    const { data: r, error } = await C.sb.rpc("lab_save_results", { p_order: id, p_results: rows, p_final: final, p_reason: $("why")?.value || null });
    if (error) return err($("rmsg"), error);
    if (final || done) { reportView(id); if (r.is_critical) alert("🚨 Critical report — Doctor aur Sister ko alert chala gaya. Phone par bhi doctor ko batayein."); }
    else ok($("rmsg"), "✓ Save ho gaya (report abhi final nahi)");
  };
  if ($("draft")) $("draft").onclick = () => save(false);
  $("fin").onclick = () => save(true);
}

// ---------------------------------------------------------------- write tests
function order() {
  const cats = [...new Set(TESTS.filter(t => t.active).map(t => t.category))];
  $("body").innerHTML = `<div class="card">
      <label>Patient (naam / UHID / phone)</label><input id="pq" autocomplete="off" placeholder="Kam se kam 2 akshar" value="${PAT ? C.esc(PAT.full_name) : ""}">
      <div id="pres"></div><div id="pchip" style="margin-top:6px">${PAT ? `✅ <b>${C.esc(PAT.full_name)}</b> · ${C.esc(PAT.uhid)}` : ""}</div></div>
    <div class="card">${cats.map(c => `<h4 style="margin:8px 0 4px">${C.esc(c)}</h4>${TESTS.filter(t => t.active && t.category === c).map(t => `
        <label class="row" style="gap:6px;margin:3px 0"><input type="checkbox" data-t="${t.id}" style="width:auto">${C.esc(t.name)} <small class="muted">${rs(t.price)}</small></label>`).join("")}`).join("")}</div>
    <div class="card"><label class="row" style="gap:6px"><input type="checkbox" id="urg" style="width:auto"> 🚨 Urgent (lab ko turant alert)</label>
      <label>Note (jaise: fasting, fever 3 din)</label><input id="nt">
      <h3 id="tot" style="margin:8px 0 4px"></h3><button class="full" id="go">Test likho</button><p class="msg" id="omsg"></p></div>`;
  let t;
  $("pq").oninput = () => { clearTimeout(t); t = setTimeout(async () => {
    const q = clean($("pq").value);
    if (q.length < 2) { $("pres").innerHTML = ""; return; }
    const { data } = await C.sb.rpc("search_patients", { q });
    $("pres").innerHTML = (data || []).slice(0, 6).map(p => `<button class="small ghost" style="margin:3px" data-p='${C.esc(JSON.stringify({ id: p.id, full_name: p.full_name, uhid: p.uhid }))}'>${C.esc(p.full_name)} · ${C.esc(p.uhid)}${p.exact ? "" : " ≈"}</button>`).join("") || "<small class='muted'>Koi nahi mila</small>";
    $("pres").querySelectorAll("[data-p]").forEach(b => b.onclick = () => {
      PAT = JSON.parse(b.dataset.p); $("pres").innerHTML = ""; $("pq").value = PAT.full_name; $("pchip").innerHTML = `✅ <b>${C.esc(PAT.full_name)}</b> · ${C.esc(PAT.uhid)}`;
    });
  }, 300); };
  const sum = () => { const ids = [...$("body").querySelectorAll("[data-t]:checked")].map(c => c.dataset.t);
    $("tot").textContent = ids.length ? `${ids.length} test · ${rs(ids.reduce((s, i) => s + Number(TESTS.find(x => x.id === i)?.price || 0), 0))}` : ""; };
  $("body").querySelectorAll("[data-t]").forEach(c => c.onchange = sum);
  $("go").onclick = async () => {
    if (!PAT) return err($("omsg"), "Pehle patient chunein");
    const ids = [...$("body").querySelectorAll("[data-t]:checked")].map(c => c.dataset.t);
    $("go").disabled = true;
    const { data, error } = await C.sb.rpc("lab_order_tests", { p_patient: PAT.id, p_tests: ids, p_urgent: $("urg").checked, p_note: $("nt").value });
    $("go").disabled = false;
    if (error) return err($("omsg"), error);
    PAT = null; order(); setTimeout(() => ok($("omsg"), `✓ ${data.length} test likh diye — lab ki Kaam list mein aa gaye. Bill Accounts mein apne aap judega.`), 200);
  };
}

// ---------------------------------------------------------------- critical
async function crit() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const { data, error } = await C.sb.from("lab_orders").select("id, result, reported_at, critical_ack_at, patients(full_name, uhid), lab_tests(name)")
    .eq("is_critical", true).eq("status", "reported").order("reported_at", { ascending: false }).limit(50);
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const open = data.filter(o => !o.critical_ack_at), seen = data.filter(o => o.critical_ack_at);
  $("body").innerHTML = (open.length ? open.map(o => `<div class="card" style="border-color:#fca5a5;background:#fff7f7">
      <b>🚨 ${C.esc(o.patients?.full_name)}</b> <small>${C.esc(o.patients?.uhid)}</small> — ${C.esc(o.lab_tests?.name)}<br>
      <small>${C.esc(o.result)}</small><br><small class="muted">Report ${dt(o.reported_at)}</small>
      <div class="row" style="gap:6px;margin-top:6px"><button class="small ghost" data-v="${o.id}">📄 Report</button>
      ${can(["doctor", "nurse"]) ? `<button class="small" data-a="${o.id}">👁️ Dekh liya, kaam shuru</button>` : `<small class="muted">Doctor / Sister ko phone karke batayein</small>`}</div></div>`).join("")
    : `<div class="card"><p class="muted">Koi bina dekha critical report nahi ✓</p></div>`)
    + (seen.length ? `<div class="card"><h4 style="margin:0 0 6px">Dekhe gaye (aakhri)</h4>${seen.slice(0, 10).map(o => `<div style="margin:4px 0">✓ ${C.esc(o.patients?.full_name)} — ${C.esc(o.lab_tests?.name)} <small class="muted">dekha ${dt(o.critical_ack_at)}</small></div>`).join("")}</div>` : "");
  $("body").querySelectorAll("[data-v]").forEach(b => b.onclick = () => reportView(b.dataset.v));
  $("body").querySelectorAll("[data-a]").forEach(b => b.onclick = async () => {
    const { error } = await C.sb.rpc("lab_ack_critical", { p_order: b.dataset.a });
    if (error) return alert("❌ " + error.message);
    crit();
  });
}

// ---------------------------------------------------------------- reports
function reports() {
  $("body").innerHTML = `<div class="card"><label>Patient (naam / UHID / phone)</label><input id="pq" autocomplete="off"><div id="pres"></div></div><div id="rl"></div>`;
  let t;
  $("pq").oninput = () => { clearTimeout(t); t = setTimeout(async () => {
    const q = clean($("pq").value);
    if (q.length < 2) { $("pres").innerHTML = ""; return; }
    const { data } = await C.sb.rpc("search_patients", { q });
    $("pres").innerHTML = (data || []).slice(0, 6).map(p => `<button class="small ghost" style="margin:3px" data-p="${p.id}">${C.esc(p.full_name)} · ${C.esc(p.uhid)}</button>`).join("") || "<small class='muted'>Koi nahi mila</small>";
    $("pres").querySelectorAll("[data-p]").forEach(b => b.onclick = () => patientReports(b.dataset.p));
  }, 300); };
  recent();
}
async function recent() {
  const { data } = await C.sb.from("lab_orders").select("id, result, reported_at, is_critical, amended_at, patients(full_name, uhid), lab_tests(name)")
    .eq("status", "reported").order("reported_at", { ascending: false }).limit(20);
  $("rl").innerHTML = `<div class="card"><h4 style="margin:0 0 6px">Aakhri reports</h4>${(data || []).map(o => `<div style="margin:6px 0;cursor:pointer" data-v="${o.id}">
      ${o.is_critical ? "🚨" : "📄"} <b>${C.esc(o.patients?.full_name)}</b> — ${C.esc(o.lab_tests?.name)} <small class="muted">${dt(o.reported_at)}${o.amended_at ? " · amended" : ""}</small></div>`).join("") || "<p class='muted'>Abhi koi report nahi.</p>"}</div>`;
  $("rl").querySelectorAll("[data-v]").forEach(b => b.onclick = () => reportView(b.dataset.v));
}
async function patientReports(pid) {
  $("pres").innerHTML = "";
  const { data } = await C.sb.from("lab_orders").select("id, status, result, ordered_at, reported_at, is_critical, lab_tests(name)")
    .eq("patient_id", pid).neq("status", "cancelled").order("ordered_at", { ascending: false }).limit(50);
  $("rl").innerHTML = `<div class="card">${(data || []).map(o => `<div style="margin:6px 0;${o.status === "reported" ? "cursor:pointer" : ""}" ${o.status === "reported" ? `data-v="${o.id}"` : ""}>
      ${o.is_critical ? "🚨" : ST[o.status].split(" ")[0]} <b>${C.esc(o.lab_tests?.name)}</b> <small class="muted">${dt(o.reported_at || o.ordered_at)}</small>
      ${o.result ? `<br><small>${C.esc(o.result)}</small>` : ""}</div>`).join("") || "<p class='muted'>Is patient ka koi test nahi.</p>"}</div>`;
  $("rl").querySelectorAll("[data-v]").forEach(b => b.onclick = () => reportView(b.dataset.v));
}

async function reportView(id) {
  const [{ data: o }, { data: cur }, { data: h }, { data: staff }] = await Promise.all([
    C.sb.from("lab_orders").select("*, patients(full_name, uhid, gender, age_years), lab_tests(name, sample_type)").eq("id", id).single(),
    C.sb.from("lab_current").select("param_id, value_text, flag").eq("order_id", id),
    C.sb.from("hospitals").select("name").maybeSingle(),
    C.sb.from("profiles").select("id, full_name")]);
  if (!o) return;
  const t = TESTS.find(x => x.id === o.test_id), g = o.patients?.gender;
  const val = Object.fromEntries((cur || []).map(c => [c.param_id, c]));
  const nm = uid => staff?.find(s => s.id === uid)?.full_name || "";
  $("receipt").innerHTML = `<div class="card" id="rcpt" style="max-width:560px;margin:10px auto;font-size:14px">
    <div style="text-align:center"><b style="font-size:18px">${C.esc(h?.name || "Hospital")} — Laboratory</b><br><small>Lab Report</small></div><hr>
    <div class="row" style="justify-content:space-between;align-items:flex-start">
      <div>Patient: <b>${C.esc(o.patients?.full_name)}</b><br>UHID: ${C.esc(o.patients?.uhid)} · ${C.esc(g || "")} ${o.patients?.age_years ? o.patients.age_years + " yr" : ""}</div>
      <div style="text-align:right"><small>Sample: ${C.esc(o.sample_no || "")} (${C.esc(o.lab_tests?.sample_type || "")})<br>Liya: ${dt(o.sample_collected_at)}<br>Report: ${dt(o.reported_at)}</small></div></div>
    ${o.amended_at ? `<p style="color:#b45309"><b>AMENDED</b> ${dt(o.amended_at)}</p>` : ""}
    <hr><b>${C.esc(o.lab_tests?.name)}</b>
    <table style="width:100%;margin-top:6px"><tr><th style="text-align:left">Jaanch</th><th style="text-align:left">Result</th><th style="text-align:left">Unit</th><th style="text-align:left">Normal</th></tr>
      ${(t?.lab_test_params || []).filter(p => p.active).sort((a, b) => a.ord - b.ord).map(p => { const v = val[p.id]; const f = FLAG[v?.flag];
        return `<tr><td>${C.esc(p.name)}</td><td style="${f ? `color:${f[1]};font-weight:700` : ""}">${C.esc(v?.value_text || "—")}${f ? " " + f[0] : ""}</td>
          <td>${C.esc(p.unit || "")}</td><td><small>${C.esc(rangeText(p, g))}</small></td></tr>`; }).join("")}</table>
    <hr><small>Report kiya: ${C.esc(nm(o.reported_by))}${o.is_critical ? ` · <b style="color:#dc2626">CRITICAL</b>${o.critical_ack_at ? " · dekha: " + C.esc(nm(o.critical_ack_by)) + " " + dt(o.critical_ack_at) : ""}` : ""}</small>
    <p style="text-align:center;margin-top:8px"><small>Report ka matlab doctor hi samjhayenge.</small></p></div>
    <div class="row noprint" style="gap:6px;justify-content:center">
      <button id="rp">🖨️ Print / PDF</button>${can(["doctor", "lab"]) ? `<button class="ghost" id="re">✏️ Badlo</button>` : ""}<button class="ghost" id="rc">Band karo</button></div>`;
  $("rp").onclick = () => { document.body.classList.add("printing"); window.print(); setTimeout(() => document.body.classList.remove("printing"), 500); };
  $("rc").onclick = () => { $("receipt").innerHTML = ""; };
  if ($("re")) $("re").onclick = () => { $("receipt").innerHTML = ""; resultForm(id); };
  $("receipt").scrollIntoView({ behavior: "smooth" });
}

// ---------------------------------------------------------------- test list
async function testList(edit = null) {
  await loadTests();
  const t = edit ? TESTS.find(x => x.id === edit) : null;
  $("body").innerHTML = `<div class="card"><h3 style="margin:0 0 6px">${t ? "✏️ Test badlo" : "＋ Naya test (ek result wala)"}</h3>
      <label>Naam</label><input id="n" value="${C.esc(t?.name || "")}">
      <div class="row" style="gap:6px"><div style="flex:1"><label>Category</label><input id="c" value="${C.esc(t?.category || "")}" placeholder="Biochemistry"></div>
        <div style="flex:1"><label>Sample</label><input id="s" value="${C.esc(t?.sample_type || "Blood")}"></div></div>
      <div class="row" style="gap:6px"><div style="flex:1"><label>Rate ₹</label><input id="p" type="number" min="0" value="${t?.price ?? ""}"></div>
        <div style="flex:1"><label>Report kitne ghante mein</label><input id="h" type="number" min="1" max="240" value="${t?.tat_hours ?? 24}"></div></div>
      ${t ? `<label class="row" style="gap:6px"><input type="checkbox" id="ac" style="width:auto" ${t.active ? "checked" : ""}> Chalu</label>
        <p class="muted" style="font-size:12px">Normal range: ${t.lab_test_params.sort((a, b) => a.ord - b.ord).map(p => C.esc(p.name + " " + (rangeText(p, "male") || "—") + " " + (p.unit || ""))).join(" · ")}</p>`
      : `<div class="row" style="gap:6px"><div style="flex:1"><label>Unit</label><input id="u" placeholder="mg/dL"></div>
          <div style="flex:1"><label>Normal kam se kam</label><input id="lo" type="number" step="any"></div><div style="flex:1"><label>Normal zyada se zyada</label><input id="hi" type="number" step="any"></div></div>
        <div class="row" style="gap:6px"><div style="flex:1"><label>Critical neeche</label><input id="clo" type="number" step="any"></div><div style="flex:1"><label>Critical upar</label><input id="chi" type="number" step="any"></div></div>
        <p class="muted" style="font-size:12px">Range khaali chhodoge to result likh kar (text) bharna hoga.</p>`}
      <button class="full" id="sv">💾 Save</button>${t ? `<button class="ghost full" id="nw">Naya test jodo</button>` : ""}<p class="msg" id="tm"></p>
      <p class="muted" style="font-size:12px">⚠️ Normal range apni lab ki machine / kit ke hisaab se check karwa lein.</p></div>
    <div class="card" style="overflow-x:auto"><table><tr><th>Test</th><th>Rate</th><th>Ghante</th></tr>${TESTS.map(x => `<tr data-e="${x.id}" style="cursor:pointer;${x.active ? "" : "opacity:.5"}">
      <td>${C.esc(x.name)}<br><small class="muted">${C.esc(x.category)} · ${x.lab_test_params.length} jaanch</small></td><td>${rs(x.price)}</td><td>${x.tat_hours}</td></tr>`).join("")}</table></div>`;
  $("body").querySelectorAll("[data-e]").forEach(r => r.onclick = () => testList(r.dataset.e));
  if ($("nw")) $("nw").onclick = () => testList();
  const num = id => $(id) && $(id).value !== "" ? Number($(id).value) : null;
  $("sv").onclick = async () => {
    const { error } = await C.sb.rpc("lab_save_test", { p_id: t?.id || null, p_name: $("n").value, p_category: $("c").value, p_sample: $("s").value,
      p_price: num("p"), p_tat: num("h"), p_active: $("ac") ? $("ac").checked : true,
      p_unit: $("u")?.value || null, p_ref_low: num("lo"), p_ref_high: num("hi"), p_crit_low: num("clo"), p_crit_high: num("chi") });
    if (error) return err($("tm"), error);
    await testList(); ok($("tm"), "✓ Save ho gaya");
  };
}
