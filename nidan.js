// Vatte Hospital OS — Phase 6: Nidan (adaptive clinical history taking)
// Sister asks questions one by one -> doctor gets a structured history report.
// The app never diagnoses: it only lists possibilities for the doctor to consider.
let C, BANK = null;
const $ = id => document.getElementById(id);
const dt = t => new Date(t).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
const GEN_SECTIONS = ["past", "drug", "allergy", "family", "personal", "obstetric", "ice", "ros"];
const SEC_NAME = { safety: "Emergency check", hopi: "Takleef ki detail", associated: "Saath ke lakshan", redflag: "⚠️ Khatre ke nishan",
  risk: "Risk factors", past: "Purani bimari", drug: "Dawaiyan", allergy: "Allergy", family: "Parivar", personal: "Aadatein",
  obstetric: "Mahila", ice: "Patient ki soch", ros: "Baaki sharir" };
const SPECIAL = { yes: { hi: "हाँ", mr: "हो", en: "Yes" }, no: { hi: "नहीं", mr: "नाही", en: "No" },
  unknown: { hi: "पता नहीं", mr: "माहीत नाही", en: "Don't know" }, na: { hi: "लागू नहीं", mr: "लागू नाही", en: "Not applicable" },
  unable: { hi: "जवाब नहीं दे सकते", mr: "उत्तर देऊ शकत नाही", en: "Unable to answer" } };

async function loadBank() {
  if (BANK) return BANK;
  const [{ data: complaints, error: e1 }, { data: questions, error: e2 }] = await Promise.all([
    C.sb.from("hx_complaints").select("*").order("ord"),
    C.sb.from("hx_questions").select("*").order("ord")
  ]);
  if (e1 || e2) throw new Error((e1 || e2).message);
  // retired items stay loaded so old histories still show them; new histories only use active ones
  BANK = { allComplaints: complaints, complaints: complaints.filter(c => c.active),
           questions: questions.filter(q => q.active), byId: Object.fromEntries(questions.map(q => [q.id, q])) };
  return BANK;
}

export async function render(ctx, tab = "new") {
  C = ctx;
  C.app.innerHTML = `
    <button class="ghost small back" id="bk">← Wapas</button>
    <h2>❓ Nidan — History</h2>
    <div class="tabs">${[["new", "+ Nayi history"], ["list", "📋 Histories"]]
      .map(([k, v]) => `<button class="tab ${k === tab ? "on" : ""}" data-t="${k}">${v}</button>`).join("")}</div>
    <div id="pane"><div class="card">Loading…</div></div>`;
  $("bk").onclick = C.goHome;
  C.app.querySelectorAll(".tab").forEach(b => b.onclick = () => render(C, b.dataset.t));
  try { await loadBank(); } catch (e) { $("pane").innerHTML = `<div class="card msg err">${C.esc(e.message)}</div>`; return; }
  (tab === "new" ? pickPatient : showList)();
}

// ---------- list of histories ----------
async function showList() {
  const pane = $("pane");
  const { data, error } = await C.sb.from("hx_sessions")
    .select("id, status, emergency, created_at, complaints, patients(full_name, uhid)")
    .order("created_at", { ascending: false }).limit(50);
  if (error) { pane.innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const label = { in_progress: "Chal rahi", completed: "Doctor review baaki", reviewed: "✓ Review ho gayi" };
  pane.innerHTML = `<div class="card">${data.length ? `<table>${data.map(s => `<tr class="click" data-s="${s.id}" data-st="${s.status}">
    <td><b>${C.esc(s.patients.full_name)}</b> ${s.emergency ? `<span class="badge" style="background:#fee2e2;color:#dc2626">🚨</span>` : ""}<br>
      <small class="muted">${C.esc(s.patients.uhid)} · ${dt(s.created_at)}</small><br>
      <small>${(s.complaints || []).map(c => C.esc(BANK.allComplaints.find(x => x.id === c.id)?.name_en || c.id)).join(", ")}</small></td>
    <td><span class="badge ${s.status === "completed" ? "pending" : ""}">${label[s.status]}</span></td></tr>`).join("")}</table>`
    : `<p class="muted">Abhi koi history nahi.</p>`}</div>`;
  pane.querySelectorAll("[data-s]").forEach(r => r.onclick = () =>
    r.dataset.st === "in_progress" ? resume(r.dataset.s) : showReport(r.dataset.s));
}

// ---------- step 0: choose patient ----------
async function pickPatient() {
  const pane = $("pane");
  const [{ data: opd }, { data: adm }] = await Promise.all([
    C.sb.from("encounters").select("id, patients(id, uhid, full_name, age_years)").in("kind", ["opd", "emergency"]).eq("status", "open").order("started_at"),
    C.sb.from("admissions").select("encounter_id, patients(id, uhid, full_name, age_years), beds(label)").eq("status", "admitted")
  ]);
  const now = [...(opd || []).map(o => ({ ...o.patients, enc: o.id, where: "OPD" })),
                ...(adm || []).map(a => ({ ...a.patients, enc: a.encounter_id, where: "🛏️ " + (a.beds?.label || "IPD") }))];
  pane.innerHTML = `
    <div class="card"><h3>Kis patient ki history?</h3>
      ${now.length ? now.map(p => `<button class="pick" data-p="${p.id}" data-e="${p.enc || ""}">
        <b>${C.esc(p.full_name)}</b> <small class="muted">${C.esc(p.uhid)} · ${p.age_years ?? "?"} saal · ${C.esc(p.where)}</small></button>`).join("")
        : `<p class="muted">OPD line mein abhi koi nahi. Neeche search karo.</p>`}
      <div class="row" style="margin-top:10px"><input id="q" placeholder="🔍 Naam, mobile ya UHID" style="flex:1"><button id="go">Search</button></div>
      <div id="res"></div></div>`;
  const wire = root => root.querySelectorAll("[data-p]").forEach(b => b.onclick = () => startForm(b.dataset.p, b.dataset.e || null));
  wire(pane);
  const run = async () => {
    const q = $("q").value.replace(/[,()%*\\":]/g, " ").trim(); if (q.length < 2) return;
    const { data } = await C.sb.from("patients").select("id, uhid, full_name, age_years")
      .or(`full_name.ilike."%${q}%",phone.ilike."%${q}%",uhid.ilike."%${q}%"`).limit(15);
    $("res").innerHTML = (data || []).map(p => `<button class="pick" data-p="${p.id}"><b>${C.esc(p.full_name)}</b>
      <small class="muted">${C.esc(p.uhid)} · ${p.age_years ?? "?"} saal</small></button>`).join("") || `<p class="muted">Koi nahi mila.</p>`;
    wire($("res"));
  };
  $("go").onclick = run; $("q").onkeydown = e => { if (e.key === "Enter") run(); };
}

async function startForm(pid, encId) {
  const { data: p } = await C.sb.from("patients").select("id, full_name, uhid, age_years, gender, created_at").eq("id", pid).single();
  const { data: open } = await C.sb.from("hx_sessions").select("id, created_at").eq("patient_id", pid).eq("status", "in_progress")
    .order("created_at", { ascending: false }).limit(1);
  $("pane").innerHTML = `
    ${open?.length ? `<div class="card warn">Is patient ki ek history adhoori hai (${dt(open[0].created_at)}).
      <button class="full" id="res">Wahi aage badhao</button></div>` : ""}
    <div class="card"><h3>${C.esc(p.full_name)} <span class="badge">${C.esc(p.uhid)}</span></h3>
      <label>Sawaal kis bhasha mein poochhne hain?</label>
      <div class="row"><button class="langb on" data-l="hi">हिंदी</button><button class="langb" data-l="mr">मराठी</button><button class="langb" data-l="en">English</button></div>
      <label>Jawab kaun de raha hai?</label>
      <select id="inf"><option value="self">Patient khud</option><option value="relative">Rishtedaar / saath wala</option>
        <option value="parent">Mata-pita (bachcha)</option><option value="other">Koi aur (ambulance, padosi…)</option></select>
      <label>Jawab kitne bharose layak?</label>
      <select id="rel"><option value="reliable">Poora bharosa</option><option value="partly">Thoda</option><option value="unreliable">Bharosa nahi (behoshi, nasha…)</option></select>
      <button class="full" id="go">Shuru karo →</button></div>`;
  let lang = "hi";
  document.querySelectorAll(".langb").forEach(b => b.onclick = () => {
    lang = b.dataset.l; document.querySelectorAll(".langb").forEach(x => x.classList.toggle("on", x === b)); });
  if ($("res")) $("res").onclick = () => resume(open[0].id);
  $("go").onclick = async () => {
    $("go").disabled = true;
    const { data: s, error } = await C.sb.from("hx_sessions").insert({ patient_id: pid, encounter_id: encId, language: lang,
      informant: $("inf").value, reliability: $("rel").value }).select("id").single();
    if (error) { $("go").disabled = false; alert2(error.message); return; }
    resume(s.id);
  };
}

// ---------- the interview ----------
let S; // { session, patient, answers: {qid: value}, flow: [qid], idx, stage }

async function resume(sid) {
  const [{ data: session, error }, { data: ans }] = await Promise.all([
    C.sb.from("hx_sessions").select("*, patients(id, full_name, uhid, age_years, gender, created_at)").eq("id", sid).single(),
    C.sb.from("hx_answers").select("question_id, value").eq("session_id", sid)
  ]);
  if (error) return alert2(error.message);
  if (session.status !== "in_progress") return showReport(sid);
  const p = session.patients;
  S = { session, patient: p, lang: session.language,
        age: p.age_years != null ? p.age_years + new Date().getFullYear() - new Date(p.created_at).getFullYear() : null,
        answers: Object.fromEntries((ans || []).map(a => [a.question_id, a.value])) };
  const safetyDone = BANK.questions.filter(q => q.section === "safety").every(q => q.id in S.answers);
  if (!safetyDone) return safetyScreen();
  if (!(session.complaints || []).length) return complaintScreen();
  buildFlow();
  S.idx = S.flow.findIndex(id => !(id in S.answers));
  if (S.idx < 0) S.idx = S.flow.length;
  askNext();
}

const T = q => q[`text_${S.lang}`] || q.text_en;
const OT = o => o[S.lang] || o.en;
const ST = k => SPECIAL[k][S.lang] || SPECIAL[k].en;

async function saveAnswer(qid, value) {
  S.answers[qid] = value;
  const { error } = await C.sb.from("hx_answers").upsert({ session_id: S.session.id, question_id: qid, value }, { onConflict: "session_id,question_id" });
  if (error) alert2("Save nahi hua: " + error.message);
  return !error;
}

// Stage 1: safety screen (all on one page, fast)
function safetyScreen() {
  const qs = BANK.questions.filter(q => q.section === "safety");
  $("pane").innerHTML = `${header("Emergency check (sabse pehle)", 0)}
    <div class="card"><p class="muted">Lambe sawaal se pehle ye zaroori check. Koi bhi "Haan" ho toh doctor ko turant alert jayega.</p>
    ${qs.map(q => `<div class="sq"><div>${C.esc(T(q))}<br><small class="muted">${C.esc(q.text_en)}</small></div>
      <div class="row"><button class="yn" data-q="${q.id}" data-v="yes">${ST("yes")}</button>
      <button class="yn ${S.answers[q.id] === "no" ? "on" : ""}" data-q="${q.id}" data-v="no">${ST("no")}</button></div></div>`).join("")}
    <button class="full" id="allno">Aage badho → <small>(jo nahi dabaya woh "Nahi" maana jayega)</small></button></div>`;
  qs.forEach(q => { if (S.answers[q.id] === "yes") $("pane").querySelector(`[data-q="${q.id}"][data-v="yes"]`).classList.add("on", "red"); });
  $("pane").querySelectorAll(".yn").forEach(b => b.onclick = async () => {
    const row = b.parentElement; row.querySelectorAll(".yn").forEach(x => x.classList.remove("on", "red"));
    b.classList.add("on"); if (b.dataset.v === "yes") b.classList.add("red");
    await saveAnswer(b.dataset.q, b.dataset.v);
  });
  $("allno").onclick = async () => {
    for (const q of qs) if (!(q.id in S.answers)) await saveAnswer(q.id, "no");
    const yes = qs.filter(q => S.answers[q.id] === "yes");
    if (yes.length) return emergencyScreen(yes);
    complaintScreen();
  };
}

function emergencyScreen(yes) {
  $("pane").innerHTML = `<div class="card alertbox"><h3>🚨 EMERGENCY</h3>
    <p><b>${yes.map(q => C.esc(q.clinical_term || q.text_en)).join(", ")}</b></p>
    <p>Doctor ko alert bhej diya hai. <b>Lambi history baad mein — pehle doctor ko bulao aur patient ka ilaaj shuru karo.</b></p>
    <button class="full ghost" id="cont">Doctor aa gaye / patient stable — history jaari rakho</button></div>`;
  $("cont").onclick = complaintScreen;
}

// Stage 2: complaints with duration / onset / severity
function complaintScreen() {
  const chosen = new Map((S.session.complaints || []).map(c => [c.id, c]));
  $("pane").innerHTML = `${header("Mukhya takleef (chief complaints)", 1)}
    <div class="card"><p>Patient se poochho: <b>${S.lang === "mr" ? "आज कोणत्या त्रासामुळे दवाखान्यात आलात?" : S.lang === "en" ? "What problem has brought you here today?" : "आज किस तकलीफ़ की वजह से अस्पताल आए हैं?"}</b></p>
    <label>Patient ke apne shabdon mein</label><textarea id="own" rows="2">${C.esc(S.session.complaints?.[0]?.own_words || "")}</textarea>
    <label>Takleef chuno (ek se zyada ho sakti hain)</label>
    ${[...new Set(BANK.complaints.map(c => c.system))].map(sys => `<div class="sysname">${C.esc(sys)}</div>
      <div class="chips">${BANK.complaints.filter(c => c.system === sys).map(c => `<button class="chip ${chosen.has(c.id) ? "on" : ""}" data-c="${c.id}">${c.icon || ""} ${C.esc(c[`name_${S.lang}`] || c.name_en)}<br><small>${C.esc(c.name_en)}</small></button>`).join("")}</div>`).join("")}
    <div id="details"></div>
    <div class="two" style="margin-top:10px">
      <div><label>Height (cm)</label><input id="ht" type="number" inputmode="decimal" value="${S.session.height_cm ?? ""}"></div>
      <div><label>Weight (kg)</label><input id="wt" type="number" inputmode="decimal" value="${S.session.weight_kg ?? ""}"></div>
    </div><label>Blood sugar (agar check kiya)</label><input id="bs" type="number" inputmode="numeric" value="${S.session.blood_sugar ?? ""}">
    <p class="muted" style="font-size:12px">BP, pulse, SpO2 "Nursing Sister" mein daalo — alert wahi se jata hai.</p>
    <button class="full" id="go">Sawaal shuru karo →</button><p class="msg" id="cm"></p></div>`;
  const draw = () => {
    $("details").innerHTML = [...chosen.values()].map(c => {
      const k = BANK.complaints.find(x => x.id === c.id);
      return `<div class="cdet" data-c="${c.id}"><b>${k.icon || ""} ${C.esc(k.name_en)}</b>
        <div class="three"><div><label>Kab se?</label><input data-f="duration" placeholder="jaise 3 din" value="${C.esc(c.duration || "")}"></div>
        <div><label>Shuruaat</label><select data-f="onset"><option value="">–</option>${["sudden:Achanak", "gradual:Dheere-dheere", "recurrent:Baar-baar"].map(o => { const [v, l] = o.split(":"); return `<option value="${v}" ${c.onset === v ? "selected" : ""}>${l}</option>`; }).join("")}</select></div>
        <div><label>Kitna tez (1-10)</label><input data-f="severity" type="number" min="1" max="10" value="${c.severity ?? ""}"></div>
        <div><label>Abhi</label><select data-f="status">${["same:Waisa hi", "worse:Badh raha", "better:Kam ho raha"].map(o => { const [v, l] = o.split(":"); return `<option value="${v}" ${c.status === v ? "selected" : ""}>${l}</option>`; }).join("")}</select></div></div></div>`;
    }).join("");
  };
  draw();
  $("pane").querySelectorAll(".chip").forEach(b => b.onclick = () => {
    readDetails(chosen);
    if (chosen.has(b.dataset.c)) chosen.delete(b.dataset.c); else chosen.set(b.dataset.c, { id: b.dataset.c });
    b.classList.toggle("on"); draw();
  });
  $("go").onclick = async () => {
    readDetails(chosen);
    if (!chosen.size) { $("cm").textContent = "Kam se kam ek takleef chuno"; $("cm").className = "msg err"; return; }
    const own = $("own").value.trim();
    const complaints = [...chosen.values()].map((c, i) => ({ ...c, own_words: i === 0 ? own : c.own_words }));
    const num = id => $(id).value === "" ? null : Number($(id).value);
    const { error } = await C.sb.from("hx_sessions").update({ complaints, height_cm: num("ht"), weight_kg: num("wt"), blood_sugar: num("bs") }).eq("id", S.session.id);
    if (error) return alert2(error.message);
    Object.assign(S.session, { complaints, height_cm: num("ht"), weight_kg: num("wt"), blood_sugar: num("bs") });
    buildFlow(); S.idx = S.flow.findIndex(id => !(id in S.answers)); if (S.idx < 0) S.idx = S.flow.length;
    askNext();
  };
}
function readDetails(chosen) {
  document.querySelectorAll(".cdet").forEach(d => {
    const c = chosen.get(d.dataset.c); if (!c) return;
    d.querySelectorAll("[data-f]").forEach(i => { c[i.dataset.f] = i.dataset.f === "severity" ? (i.value ? Number(i.value) : null) : i.value; });
  });
}

// Which questions apply to this patient (sex/age), in clinical order
function applies(q) {
  const a = q.applies_to; if (!a) return true;
  if (a.sex && S.patient.gender && a.sex !== S.patient.gender) return false;
  if (a.sex && !S.patient.gender) return true;
  if (a.min_age != null && S.age != null && S.age < a.min_age) return false;
  if (a.max_age != null && S.age != null && S.age > a.max_age) return false;
  return true;
}
function visible(q) {
  const c = q.show_if; if (!c) return true;
  const v = S.answers[c.q];
  if (v === undefined) return false;
  if (c.eq !== undefined) return v === c.eq;
  if (c.in) return c.in.includes(v);
  if (c.has) return Array.isArray(v) && v.includes(c.has);
  if (c.in_any) return Array.isArray(v) && v.some(x => c.in_any.includes(x));
  return true;
}
const ORDER = ["hopi", "redflag", "associated", "risk"];
function buildFlow() {
  const ids = [], keys = new Set();
  const add = q => {
    if (!applies(q)) return;
    if (q.dedupe_key) { if (keys.has(q.dedupe_key)) return; keys.add(q.dedupe_key); }
    ids.push(q.id);
  };
  for (const c of S.session.complaints || [])
    BANK.questions.filter(q => q.complaint_id === c.id)
      .sort((a, b) => ORDER.indexOf(a.section) - ORDER.indexOf(b.section) || a.ord - b.ord).forEach(add);
  BANK.questions.filter(q => !q.complaint_id && GEN_SECTIONS.includes(q.section))
    .sort((a, b) => GEN_SECTIONS.indexOf(a.section) - GEN_SECTIONS.indexOf(b.section) || a.ord - b.ord).forEach(add);
  S.flow = ids;
}

function header(title, step) {
  const steps = ["Emergency", "Takleef", "Sawaal", "Report"];
  return `<div class="card"><b>${C.esc(S.patient.full_name)}</b> <small class="muted">${C.esc(S.patient.uhid)} · ${S.age ?? "?"} saal</small>
    <div class="steps">${steps.map((s, i) => `<span class="${i <= step ? "on" : ""}">${s}</span>`).join("")}</div>
    <h3 style="margin:8px 0 0">${C.esc(title)}</h3></div>`;
}

// Stage 3: one question per screen
function askNext() {
  // skip questions whose condition is not met (answers may have changed)
  while (S.idx < S.flow.length && !visible(BANK.byId[S.flow[S.idx]])) S.idx++;
  if (S.idx >= S.flow.length) return finishScreen();
  const q = BANK.byId[S.flow[S.idx]];
  const shown = S.flow.filter(id => visible(BANK.byId[id]));
  const pos = shown.indexOf(q.id) + 1;
  const comp = q.complaint_id ? BANK.complaints.find(c => c.id === q.complaint_id) : null;
  const cur = S.answers[q.id];
  let body = "";
  if (q.qtype === "yesno") {
    body = `<div class="bigbtns">${["yes", "no", "unknown"].map(k => `<button class="ans ${cur === k ? "on" : ""}" data-v="${k}">${ST(k)}</button>`).join("")}</div>`;
  } else if (q.qtype === "choice") {
    body = `<div class="opts">${q.options.map(o => `<button class="ans ${cur === o.v ? "on" : ""}" data-v="${C.esc(o.v)}">${C.esc(OT(o))}<br><small class="muted">${C.esc(o.en)}</small></button>`).join("")}
      <button class="ans ghost ${cur === "unknown" ? "on" : ""}" data-v="unknown">${ST("unknown")}</button></div>`;
  } else if (q.qtype === "multi") {
    const sel = Array.isArray(cur) ? cur : [];
    body = `<div class="opts">${q.options.map(o => `<label class="chk"><input type="checkbox" value="${C.esc(o.v)}" ${sel.includes(o.v) ? "checked" : ""}> ${C.esc(OT(o))} <small class="muted">${C.esc(o.en)}</small></label>`).join("")}</div>
      <div class="row" style="margin-top:8px"><button id="msave">Aage →</button><button class="ghost" id="mnone">${S.lang === "mr" ? "यापैकी काहीही नाही" : S.lang === "en" ? "None of these" : "इनमें से कुछ नहीं"}</button>
      <button class="ghost" id="munk">${ST("unknown")}</button></div>`;
  } else {
    body = `<${q.qtype === "text" ? "textarea rows='3'" : "input type='number' inputmode='decimal'"} id="tv">${q.qtype === "text" ? C.esc(typeof cur === "string" && !SPECIAL[cur] ? cur : "") + "</textarea>" : ""}
      <div class="row" style="margin-top:8px"><button id="tsave">Aage →</button><button class="ghost" id="tskip">${ST("unknown")}</button></div>`;
  }
  $("pane").innerHTML = `${header(SEC_NAME[q.section] + (comp ? " · " + comp.name_en : ""), 2)}
    <div class="progress"><div style="width:${Math.round(100 * (pos - 1) / shown.length)}%"></div></div>
    <p class="muted" style="margin:4px 0">Sawaal ${pos} / ${shown.length}</p>
    <div class="card qcard ${q.red_flag ? "rf" : ""}">
      ${q.red_flag ? `<span class="badge" style="background:#fee2e2;color:#dc2626">⚠️ Khatre ka nishan</span>` : ""}
      <div class="qtext">${C.esc(T(q))}</div>
      ${S.lang !== "en" ? `<div class="muted" style="font-size:13px;margin-bottom:10px">${C.esc(q.text_en)}</div>` : ""}
      ${body}
      <div class="row" style="justify-content:space-between;margin-top:14px">
        <button class="ghost small" id="prev">← Pichhla</button>
        <button class="ghost small" id="skipq">${ST("na")}</button>
        <button class="ghost small" id="pause">⏸ Baad mein</button></div>
    </div>`;
  if (q.qtype === "number" && cur != null && typeof cur === "number") $("tv").value = cur;
  const next = async v => { await saveAnswer(q.id, v); if (q.red_flag && v === "yes") flash("🚩 Doctor ko alert chala gaya"); S.idx++; askNext(); };
  $("pane").querySelectorAll(".ans").forEach(b => b.onclick = () => next(b.dataset.v));
  if ($("msave")) {
    $("msave").onclick = () => { const v = [...$("pane").querySelectorAll(".chk input:checked")].map(i => i.value); next(v); };
    $("mnone").onclick = () => next([]);
    $("munk").onclick = () => next("unknown");
  }
  if ($("tsave")) {
    $("tsave").onclick = () => { const raw = $("tv").value.trim(); if (!raw) return next("unknown"); next(q.qtype === "number" ? Number(raw) : raw); };
    $("tskip").onclick = () => next("unknown");
  }
  $("skipq").onclick = () => next("na");
  $("prev").onclick = () => {
    let i = S.idx - 1; while (i >= 0 && !visible(BANK.byId[S.flow[i]])) i--;
    if (i < 0) return complaintScreen();
    S.idx = i; askNext();
  };
  $("pause").onclick = () => render(C, "list");
}

function finishScreen() {
  const unanswered = S.flow.filter(id => visible(BANK.byId[id]) && !(id in S.answers)).length;
  $("pane").innerHTML = `${header("Ho gaya ✓", 3)}
    <div class="card"><p>Saare sawaal ho gaye${unanswered ? ` (${unanswered} chhoote)` : ""}. Ab history doctor ke paas review ke liye jayegi.</p>
    <button class="full" id="done">✓ History poori karo — doctor ko bhejo</button>
    <button class="full ghost" id="back">← Sawaal dobara dekho</button></div>`;
  $("done").onclick = async () => {
    const { error } = await C.sb.from("hx_sessions").update({ status: "completed" }).eq("id", S.session.id);
    if (error) return alert2(error.message);
    await C.sb.from("notifications").insert({ target_role: "doctor", level: "info", source: "nidan",
      title: `📋 ${S.patient.full_name} ki history taiyaar`, body: "Nidan mein review karein." });
    showReport(S.session.id);
  };
  $("back").onclick = () => { S.idx = 0; askNext(); };
}

// ---------- report for the doctor ----------
function describe(q, v) {
  const term = q.clinical_term || q.text_en;
  if (v === "unknown" || v === "na" || v === "unable") return { kind: "un", text: `${term} (${SPECIAL[v].en})` };
  if (q.qtype === "yesno") return v === "yes" ? { kind: "pos", text: term } : { kind: "neg", text: term };
  if (q.qtype === "choice") { const o = q.options.find(x => x.v === v); return { kind: "pos", text: `${term}: ${o ? o.en : v}`, ddx: o?.ddx }; }
  if (q.qtype === "multi") {
    if (!Array.isArray(v) || !v.length) return { kind: "neg", text: `${term}: none of — ${q.options.map(o => o.en).join(", ")}` };
    const os = q.options.filter(o => v.includes(o.v));
    return { kind: "pos", text: `${term}: ${os.map(o => o.en).join(", ")}`, ddx: os.flatMap(o => o.ddx || []) };
  }
  return { kind: "info", text: `${term}: ${v}` };
}

async function showReport(sid) {
  const pane = $("pane");
  pane.innerHTML = `<div class="card">Report ban raha hai…</div>`;
  const [{ data: s, error }, { data: ans }] = await Promise.all([
    C.sb.from("hx_sessions").select("*, patients(*)").eq("id", sid).single(),
    C.sb.from("hx_answers").select("question_id, value").eq("session_id", sid)
  ]);
  if (error) { pane.innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const p = s.patients, A = Object.fromEntries((ans || []).map(a => [a.question_id, a.value]));
  const age = p.age_years != null ? p.age_years + new Date().getFullYear() - new Date(p.created_at).getFullYear() : "?";
  const qOf = id => BANK.byId[id];
  const answered = Object.keys(A).map(qOf).filter(Boolean);
  const redFlags = answered.filter(q => q.red_flag && A[q.id] === "yes");

  // possibilities to consider: count supporting positive findings (never a diagnosis)
  const score = {};
  for (const q of answered) {
    const d = describe(q, A[q.id]);
    if (d.kind !== "pos") continue;
    const list = q.qtype === "yesno" ? q.differentials : (d.ddx || []);
    for (const dx of list) (score[dx] = score[dx] || []).push(q.clinical_term || q.text_en);
  }
  const top = Object.entries(score).sort((a, b) => b[1].length - a[1].length).slice(0, 6);

  const block = (qs) => {
    const pos = [], neg = [], un = [], info = [];
    qs.forEach(q => { if (!(q.id in A)) return; const d = describe(q, A[q.id]); ({ pos, neg, un, info })[d.kind].push(d.text); });
    return `${pos.length ? `<p><b>➕ Positive:</b> ${pos.map(C.esc).join("; ")}</p>` : ""}
      ${neg.length ? `<p><b>➖ Important negatives (denies):</b> ${neg.map(C.esc).join("; ")}</p>` : ""}
      ${info.length ? `<p>${info.map(C.esc).join("<br>")}</p>` : ""}
      ${un.length ? `<p class="muted"><b>Not assessed / unknown:</b> ${un.map(C.esc).join("; ")}</p>` : ""}`;
  };
  const complaintBlocks = (s.complaints || []).map((c, i) => {
    const k = BANK.allComplaints.find(x => x.id === c.id) || { name_en: c.id };
    const qs = Object.values(BANK.byId).filter(q => q.complaint_id === c.id);
    return `<h4>${i + 1}. ${C.esc(k.name_en)} — ${C.esc(c.duration || "duration ?")}${c.onset ? ", " + c.onset + " onset" : ""}${c.severity ? ", severity " + c.severity + "/10" : ""}${c.status ? ", " + ({ same: "unchanged", worse: "worsening", better: "improving" })[c.status] : ""}</h4>
      ${block(qs)}<p class="muted" style="font-size:11px">Ref: ${C.esc(k.source || "")}</p>`;
  }).join("");
  const sec = name => Object.values(BANK.byId).filter(q => !q.complaint_id && q.section === name);
  const isDoc = C.me.role === "doctor";
  const bmi = s.height_cm && s.weight_kg ? (s.weight_kg / ((s.height_cm / 100) ** 2)).toFixed(1) : null;
  const relLbl = { reliable: "reliable", partly: "partly reliable", unreliable: "unreliable" };
  const infLbl = { self: "Patient", relative: "Relative / attendant", parent: "Parent", other: "Other" };

  pane.innerHTML = `
    <div class="card report" id="rep">
      <div class="row" style="justify-content:space-between"><h3 style="margin:0">Clinical history</h3>
        <span class="badge ${s.status === "completed" ? "pending" : ""}">${({ in_progress: "In progress", completed: "Awaiting doctor review", reviewed: "Reviewed" })[s.status]}</span></div>
      <p><b>${C.esc(p.full_name)}</b> · ${C.esc(p.uhid)} · ${age} y · ${C.esc(p.gender || "")}${p.phone ? " · " + C.esc(p.phone) : ""}<br>
      <small class="muted">${dt(s.created_at)} · Informant: ${infLbl[s.informant] || s.informant} (${relLbl[s.reliability]})</small></p>
      ${p.allergies ? `<p class="msg err">⚠️ Known allergy: ${C.esc(p.allergies)}</p>` : ""}
      ${s.emergency ? `<div class="alertbox card">🚨 Emergency screen positive at start of history</div>` : ""}
      ${redFlags.length ? `<div class="card alertbox"><b>🚩 Red flags</b><br>${redFlags.map(q => "• " + C.esc(q.red_flag_note || q.text_en)).join("<br>")}</div>` : ""}

      <h4>Chief complaints</h4>
      <ol>${(s.complaints || []).map(c => `<li>${C.esc((BANK.allComplaints.find(x => x.id === c.id) || {}).name_en || c.id)} — ${C.esc(c.duration || "?")}</li>`).join("")}</ol>
      ${s.complaints?.[0]?.own_words ? `<p><i>In patient's words: “${C.esc(s.complaints[0].own_words)}”</i></p>` : ""}

      <h4>History of presenting illness</h4>${complaintBlocks || "<p class='muted'>—</p>"}
      ${(s.height_cm || s.weight_kg || s.blood_sugar) ? `<p><b>Measurements:</b> ${s.height_cm ? "Ht " + s.height_cm + " cm" : ""} ${s.weight_kg ? "· Wt " + s.weight_kg + " kg" : ""} ${bmi ? "· BMI " + bmi : ""} ${s.blood_sugar ? "· RBS " + s.blood_sugar + " mg/dl" : ""}</p>` : ""}
      <h4>Past medical & surgical history</h4>${block(sec("past"))}
      <h4>Drug history & allergies</h4>${block([...sec("drug"), ...sec("allergy")])}
      <h4>Family history</h4>${block(sec("family"))}
      <h4>Personal & social history</h4>${block(sec("personal"))}
      ${sec("obstetric").some(q => q.id in A) ? `<h4>Menstrual / obstetric</h4>${block(sec("obstetric"))}` : ""}
      <h4>Patient's ideas, concerns, expectations</h4>${block(sec("ice"))}
      <h4>Review of systems</h4>${block(sec("ros"))}

      <div class="card" style="background:#f0fdfa;border-color:#99f6e4">
        <h4 style="margin-top:0">🤔 Possibilities to consider (doctor decides)</h4>
        ${top.length ? `<ol>${top.map(([dx, why]) => `<li><b>${C.esc(dx)}</b> <small class="muted">— supported by: ${[...new Set(why)].map(C.esc).join(", ")}</small></li>`).join("")}</ol>` : "<p class='muted'>Not enough positive findings.</p>"}
        <p class="muted" style="font-size:12px">Ye diagnosis nahi hai. Sirf jawabon se bani suggestion list hai — examination aur jaanch ke baad faisla doctor ka. Ref: Hutchison's Clinical Methods 24e.</p>
      </div>
      ${s.doctor_notes ? `<h4>Doctor's notes</h4><p>${C.esc(s.doctor_notes)}</p>` : ""}
      ${s.reviewed_at ? `<p class="muted">Reviewed ${dt(s.reviewed_at)}</p>` : ""}
    </div>
    <div class="row">
      <button class="ghost" id="print">🖨️ Print</button>
      ${s.status === "in_progress" ? `<button id="cont">Sawaal jaari rakho</button>` : ""}
    </div>
    ${isDoc && s.status === "completed" ? `<div class="card"><h3>Doctor review</h3>
      <textarea id="dn" rows="3" placeholder="Aapke notes / examination / plan"></textarea>
      <button class="full" id="rev">✓ Review pakka karo</button><p class="muted" style="font-size:12px">Review ke baad history lock ho jayegi.</p></div>` : ""}`;
  $("print").onclick = () => window.print();
  if ($("cont")) $("cont").onclick = () => resume(sid);
  if ($("rev")) $("rev").onclick = async () => {
    const { error } = await C.sb.from("hx_sessions").update({ status: "reviewed", doctor_notes: $("dn").value.trim() || null }).eq("id", sid);
    if (error) alert2(error.message); else showReport(sid);
  };
}

function flash(t) { const d = document.createElement("div"); d.className = "toast"; d.textContent = t; document.body.append(d); setTimeout(() => d.remove(), 2500); }
function alert2(t) { const d = document.createElement("div"); d.className = "card msg err"; d.textContent = t; $("pane")?.prepend(d); window.scrollTo(0, 0); }
