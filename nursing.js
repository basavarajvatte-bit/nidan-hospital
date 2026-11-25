// Vatte Hospital OS — Phase 5: Nursing Sister (vitals, alerts, orders, medication, notes, handover)
let C;
const $ = id => document.getElementById(id);
const dt = t => new Date(t).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
const ago = t => { const m = Math.round((Date.now() - new Date(t)) / 60000); return m < 60 ? `${m} min pehle` : m < 1440 ? `${Math.round(m / 60)} ghante pehle` : `${Math.round(m / 1440)} din pehle`; };
const cleanErr = e => (e?.message || String(e)).replace(/^.*?exception:?\s*/i, "");

// Same safety limits as the database alert (vital_flags). Not a diagnosis.
const LIMITS = {
  bp_systolic: v => v >= 180 || v < 90, bp_diastolic: v => v >= 120, pulse: v => v > 130 || v < 50,
  spo2: v => v < 92, temperature_f: v => v >= 103 || v < 95, resp_rate: v => v > 28 || v < 10
};
const bad = (k, v) => v != null && LIMITS[k] && LIMITS[k](Number(v));
const cell = (k, v, suffix = "") => v == null ? "–" : `<span class="${bad(k, v) ? "abn" : ""}">${v}${suffix}</span>`;

export function render(ctx, tab = "patients") {
  C = ctx;
  C.app.innerHTML = `
    <button class="ghost small back" id="bk">← Wapas</button>
    <h2>🩺 Nursing Sister</h2>
    <div class="tabs">${[["patients", "Mere patient"], ["handover", "🔁 Shift handover"], ["alerts", "🔔 Alerts"]]
      .map(([k, v]) => `<button class="tab ${k === tab ? "on" : ""}" data-t="${k}">${v}</button>`).join("")}</div>
    <div id="pane"></div>`;
  $("bk").onclick = C.goHome;
  C.app.querySelectorAll(".tab").forEach(b => b.onclick = () => render(C, b.dataset.t));
  ({ patients: showPatients, handover: showHandover, alerts: showAlerts })[tab]();
}

// Admitted patients + OPD patients currently in the hospital
async function currentPatients() {
  const [{ data: adm }, { data: opd }] = await Promise.all([
    C.sb.from("admissions").select("encounter_id, admitted_at, beds(label), patients(id, uhid, full_name, age_years, gender, allergies)")
      .eq("status", "admitted").order("admitted_at"),
    C.sb.from("encounters").select("id, kind, started_at, chief_complaint, patients(id, uhid, full_name, age_years, gender, allergies)")
      .in("kind", ["opd", "emergency"]).eq("status", "open").order("started_at")
  ]);
  return [
    ...(adm || []).map(a => ({ ...a.patients, where: "🛏️ " + (a.beds?.label || "IPD"), encounter_id: a.encounter_id, ipd: true })),
    ...(opd || []).map(o => ({ ...o.patients, where: o.kind === "emergency" ? "🚑 Emergency" : "OPD", encounter_id: o.id, note: o.chief_complaint }))
  ];
}

async function showPatients() {
  const pane = $("pane");
  pane.innerHTML = `<div class="card">Loading…</div>`;
  const list = await currentPatients();
  const searchBox = `<div class="card"><div class="row"><input id="nq" placeholder="🔍 Koi bhi patient dhundo (naam, mobile, UHID)" style="flex:1">
    <button id="ngo">Search</button></div><div id="nres"></div></div>`;
  if (!list.length) {
    pane.innerHTML = searchBox + `<div class="card"><b>Abhi koi patient admit ya OPD line mein nahi hai.</b>
      <p class="muted">Yahan sirf wahi patient apne aap dikhte hain jinka Reception par <b>OPD visit</b> shuru hua ho ya jo <b>admit</b> hon.
      Kisi aur patient ke vitals lene ho toh upar search karo.</p></div>`;
    wireSearch();
    return;
  }
  const ids = list.map(p => p.id);
  const [{ data: vit }, { data: ord }] = await Promise.all([
    C.sb.from("vitals").select("patient_id, recorded_at, bp_systolic, bp_diastolic, pulse, spo2, temperature_f, resp_rate")
      .in("patient_id", ids).order("recorded_at", { ascending: false }).limit(300),
    C.sb.from("doctor_orders").select("patient_id").in("patient_id", ids).eq("status", "active")
  ]);
  const last = {}; (vit || []).forEach(v => { if (!last[v.patient_id]) last[v.patient_id] = v; });
  const orders = {}; (ord || []).forEach(o => orders[o.patient_id] = (orders[o.patient_id] || 0) + 1);
  pane.innerHTML = searchBox + list.map(p => {
    const v = last[p.id];
    const abn = v && Object.keys(LIMITS).some(k => bad(k, v[k]));
    return `<div class="card pcard ${abn ? "abncard" : ""}" data-p="${p.id}" data-e="${p.encounter_id || ""}">
      <div class="row" style="justify-content:space-between"><b>${C.esc(p.full_name)}</b><span class="badge">${C.esc(p.where)}</span></div>
      <small class="muted">${C.esc(p.uhid)} · ${p.age_years ?? "?"} saal${p.note ? " · " + C.esc(p.note) : ""}</small>
      ${p.allergies ? `<div class="msg err">⚠️ Allergy: ${C.esc(p.allergies)}</div>` : ""}
      <div style="margin-top:6px;font-size:14px">${v ? `BP ${cell("bp_systolic", v.bp_systolic)}/${cell("bp_diastolic", v.bp_diastolic)} · Pulse ${cell("pulse", v.pulse)} · SpO2 ${cell("spo2", v.spo2, "%")} · Temp ${cell("temperature_f", v.temperature_f)}
        <br><small class="muted">${ago(v.recorded_at)}</small>` : `<span class="msg err">Abhi tak vitals nahi liye</span>`}
        ${orders[p.id] ? `<br><span class="badge pending">${orders[p.id]} doctor order baaki</span>` : ""}</div>
    </div>`;
  }).join("");
  pane.querySelectorAll(".pcard").forEach(c => c.onclick = () => showPatient(c.dataset.p, c.dataset.e || null));
  wireSearch();
}

function wireSearch() {
  const run = async () => {
    const q = $("nq").value.replace(/[,()%*\\":]/g, " ").trim();
    if (q.length < 2) return;
    $("nres").textContent = "Dhundh raha hoon…";
    const { data, error } = await C.sb.from("patients").select("id, uhid, full_name, age_years, phone")
      .or(`full_name.ilike."%${q}%",phone.ilike."%${q}%",uhid.ilike."%${q}%"`).order("created_at", { ascending: false }).limit(20);
    if (error) { $("nres").textContent = error.message; return; }
    $("nres").innerHTML = data.length ? `<table style="margin-top:8px">${data.map(p => `<tr><td>
      <a href="#" data-sp="${p.id}">${C.esc(p.full_name)}</a><br><small class="muted">${C.esc(p.uhid)} · ${p.age_years ?? "?"} saal</small></td>
      <td>${C.esc(p.phone || "")}</td></tr>`).join("")}</table>` : `<p class="muted">Koi nahi mila.</p>`;
    $("nres").querySelectorAll("[data-sp]").forEach(a => a.onclick = e => { e.preventDefault(); showPatient(a.dataset.sp, null); });
  };
  $("ngo").onclick = run;
  $("nq").onkeydown = e => { if (e.key === "Enter") run(); };
}

// ---------- One patient ----------
async function showPatient(pid, encId, note = "", correct = null) {
  C.app.querySelectorAll(".tab").forEach(t => t.classList.remove("on"));
  const pane = $("pane");
  pane.innerHTML = `<div class="card">Loading…</div>`;
  const [{ data: p }, { data: vit }, { data: ord }, { data: meds }, { data: notes }] = await Promise.all([
    C.sb.from("patients").select("id, uhid, full_name, age_years, gender, allergies, blood_group").eq("id", pid).single(),
    C.sb.from("vitals").select("*").eq("patient_id", pid).order("recorded_at", { ascending: false }).limit(12),
    C.sb.from("doctor_orders").select("*").eq("patient_id", pid).order("created_at", { ascending: false }).limit(20),
    C.sb.from("medication_administrations").select("*").eq("patient_id", pid).order("given_at", { ascending: false }).limit(10),
    C.sb.from("nursing_notes").select("*").eq("patient_id", pid).order("created_at", { ascending: false }).limit(10)
  ]);
  const corrected = new Set((vit || []).map(v => v.corrects_id).filter(Boolean));
  const isDoc = C.me.role === "doctor";
  const active = (ord || []).filter(o => o.status === "active");
  const f = correct || {};
  pane.innerHTML = `
    ${note ? `<div class="card ${note.startsWith("🚨") ? "alertbox" : "msg ok"}">${C.esc(note)}</div>` : ""}
    <div class="card"><h3>${C.esc(p.full_name)} <span class="badge">${C.esc(p.uhid)}</span></h3>
      <small class="muted">${p.age_years ?? "?"} saal · ${C.esc(p.gender || "")}${p.blood_group ? " · " + C.esc(p.blood_group) : ""}</small>
      ${p.allergies ? `<div class="msg err">⚠️ Allergy: ${C.esc(p.allergies)}</div>` : ""}</div>

    <div class="card"><h3>${correct ? "✏️ Galti sudharo (nayi sahi entry)" : "➕ Vitals daalo"}</h3>
      <form id="vf">
        <div class="three">
          <div><label>BP upar</label><input id="sys" type="number" inputmode="numeric" placeholder="120" value="${f.bp_systolic ?? ""}"></div>
          <div><label>BP neeche</label><input id="dia" type="number" inputmode="numeric" placeholder="80" value="${f.bp_diastolic ?? ""}"></div>
          <div><label>Pulse</label><input id="pul" type="number" inputmode="numeric" placeholder="80" value="${f.pulse ?? ""}"></div>
          <div><label>SpO2 %</label><input id="spo" type="number" inputmode="numeric" placeholder="98" value="${f.spo2 ?? ""}"></div>
          <div><label>Temp °F</label><input id="tmp" type="number" step="0.1" inputmode="decimal" placeholder="98.6" value="${f.temperature_f ?? ""}"></div>
          <div><label>Saans/min</label><input id="rr" type="number" inputmode="numeric" placeholder="18" value="${f.resp_rate ?? ""}"></div>
          <div><label>Intake ml</label><input id="in" type="number" inputmode="numeric" value="${f.intake_ml ?? ""}"></div>
          <div><label>Output ml</label><input id="out" type="number" inputmode="numeric" value="${f.output_ml ?? ""}"></div>
        </div>
        <button class="full">${correct ? "Sahi entry save karo" : "Save karo"}</button>
        ${correct ? `<button type="button" class="ghost full" id="cancelfix">Rehne do</button>` : ""}
        <p class="msg" id="vm"></p>
      </form></div>

    <div class="card"><h3>📈 Vitals history</h3>
      ${vit?.length ? `<div class="scroll"><table><tr><th>Samay</th><th>BP</th><th>Pulse</th><th>SpO2</th><th>Temp</th><th>RR</th><th>I/O</th><th></th></tr>
        ${vit.map(v => `<tr class="${corrected.has(v.id) ? "struck" : ""}">
          <td><small>${dt(v.recorded_at)}</small>${v.corrects_id ? `<br><small class="muted">sudhara hua</small>` : ""}</td>
          <td>${cell("bp_systolic", v.bp_systolic)}/${cell("bp_diastolic", v.bp_diastolic)}</td><td>${cell("pulse", v.pulse)}</td>
          <td>${cell("spo2", v.spo2)}</td><td>${cell("temperature_f", v.temperature_f)}</td><td>${cell("resp_rate", v.resp_rate)}</td>
          <td><small>${v.intake_ml ?? "–"}/${v.output_ml ?? "–"}</small></td>
          <td>${corrected.has(v.id) ? "" : `<button class="small ghost" data-fix="${v.id}">Sudharo</button>`}</td></tr>`).join("")}</table></div>
        <p class="muted" style="font-size:12px">Laal = safety limit se bahar. Kati hui line = galat entry (sudhar di gayi).</p>`
        : `<p class="muted">Abhi tak koi vitals nahi.</p>`}</div>

    <div class="card"><h3>📋 Doctor ke order</h3>
      ${isDoc ? `<form id="of" class="row"><input id="ot" placeholder="Naya order, jaise: Inj. Pantoprazole 40mg IV OD" style="flex:1" required><button>Order do</button></form>` : ""}
      ${active.length ? active.map(o => `<div class="order">
          <div><b>${C.esc(o.order_text)}</b><br><small class="muted">${dt(o.created_at)}</small></div>
          <div class="row">
            <button class="small" data-give="${o.id}" data-txt="${C.esc(o.order_text)}">💉 Dawai di</button>
            <button class="small ghost" data-done="${o.id}">✓ Ho gaya</button>
            ${isDoc ? `<button class="small ghost" data-stop="${o.id}">✕ Band karo</button>` : ""}
          </div><div id="give-${o.id}"></div></div>`).join("")
        : `<p class="muted">Koi chalu order nahi.</p>`}
      ${(ord || []).filter(o => o.status !== "active").length ? `<details><summary class="muted">Purane order</summary>
        ${(ord || []).filter(o => o.status !== "active").map(o => `<div class="muted" style="font-size:14px;padding:4px 0">${o.status === "done" ? "✓" : "✕"} ${C.esc(o.order_text)}</div>`).join("")}</details>` : ""}
      ${!isDoc ? `<p class="muted" style="font-size:12px">Sister order badal nahi sakti, naya order sirf doctor de sakte hain.</p>` : ""}
    </div>

    <div class="card"><h3>💊 Di gayi dawaiyan</h3>
      ${meds?.length ? `<table>${meds.map(m => `<tr><td><small>${dt(m.given_at)}</small></td><td>${C.esc(m.medicine_name)} ${C.esc(m.dose)} ${C.esc(m.route || "")}</td>
        <td><span class="badge ${m.status === "given" ? "" : "pending"}">${({ given: "Di", held: "Roki", refused: "Mana kiya", missed: "Chhoot gayi" })[m.status]}</span></td></tr>`).join("")}</table>`
        : `<p class="muted">Abhi koi record nahi.</p>`}</div>

    <div class="card"><h3>📝 Nursing notes</h3>
      <form id="nf"><textarea id="nt" rows="2" placeholder="Jo dekha woh likho (jaise: patient ne khana khaya, ulti hui…)" required></textarea>
        <div class="row" style="margin-top:6px"><select id="nk" style="width:auto"><option value="note">Note</option><option value="incident">⚠️ Incident</option></select>
        <button>Note save karo</button></div></form>
      ${(notes || []).map(n => `<div class="note ${n.kind === "incident" ? "critical" : ""}" style="margin-top:8px">
        <small class="muted">${dt(n.created_at)} · ${({ note: "Note", handover: "Handover", incident: "Incident" })[n.kind]}</small><br>${C.esc(n.note)}</div>`).join("")}
    </div>`;

  // Vitals save
  $("vf").onsubmit = async e => {
    e.preventDefault();
    const num = id => $(id).value === "" ? null : Number($(id).value);
    const row = { patient_id: pid, encounter_id: encId, corrects_id: correct?.id || null,
      bp_systolic: num("sys"), bp_diastolic: num("dia"), pulse: num("pul"), spo2: num("spo"),
      temperature_f: num("tmp"), resp_rate: num("rr"), intake_ml: num("in"), output_ml: num("out") };
    if (["bp_systolic", "pulse", "spo2", "temperature_f", "resp_rate", "intake_ml", "output_ml"].every(k => row[k] == null))
      return msg("vm", "Kam se kam ek value daalo", true);
    if ((row.bp_systolic == null) !== (row.bp_diastolic == null)) return msg("vm", "BP ke dono number daalo (upar aur neeche)", true);
    const { error } = await C.sb.from("vitals").insert(row);
    if (error) return msg("vm", error.message.includes("check") ? "Koi value galat lag rahi hai, dobara dekho" : error.message, true);
    const flags = Object.keys(LIMITS).filter(k => bad(k, row[k]));
    showPatient(pid, encId, flags.length ? "🚨 Ye value safety limit se bahar hai. Doctor ko turant alert bhej diya gaya hai." : "✓ Vitals save ho gaye");
  };
  if ($("cancelfix")) $("cancelfix").onclick = () => showPatient(pid, encId);
  pane.querySelectorAll("[data-fix]").forEach(b => b.onclick = () => {
    const v = vit.find(x => x.id === b.dataset.fix);
    showPatient(pid, encId, "", v);
    window.scrollTo(0, 0);
  });

  // Orders
  if ($("of")) $("of").onsubmit = async e => {
    e.preventDefault();
    const { error } = await C.sb.from("doctor_orders").insert({ patient_id: pid, encounter_id: encId, order_text: $("ot").value.trim() });
    if (error) alert2(pane, error.message); else showPatient(pid, encId, "✓ Order de diya. Sister ki list mein dikh raha hai.");
  };
  const setStatus = async (id, status) => {
    const { error } = await C.sb.from("doctor_orders").update({ status }).eq("id", id);
    if (error) alert2(pane, cleanErr(error)); else showPatient(pid, encId);
  };
  pane.querySelectorAll("[data-done]").forEach(b => b.onclick = () => setStatus(b.dataset.done, "done"));
  pane.querySelectorAll("[data-stop]").forEach(b => b.onclick = () => setStatus(b.dataset.stop, "stopped"));
  pane.querySelectorAll("[data-give]").forEach(b => b.onclick = () => {
    const box = $("give-" + b.dataset.give);
    box.innerHTML = `<form class="giveform"><div class="three">
      <div><label>Dawai</label><input name="m" required value="${C.esc(b.dataset.txt)}"></div>
      <div><label>Dose</label><input name="d" required placeholder="1g"></div>
      <div><label>Route</label><select name="r"><option>IV</option><option>IM</option><option>Oral</option><option>SC</option><option>Other</option></select></div>
      <div><label>Kya hua?</label><select name="s"><option value="given">Di</option><option value="held">Roki</option><option value="refused">Patient ne mana kiya</option><option value="missed">Chhoot gayi</option></select></div>
      </div><input name="k" placeholder="Remark (optional)" style="margin-top:6px"><button class="full">Record karo</button></form>`;
    box.querySelector("form").onsubmit = async e => {
      e.preventDefault();
      const fd = new FormData(e.target);
      const { error } = await C.sb.from("medication_administrations").insert({ patient_id: pid, order_id: b.dataset.give,
        medicine_name: fd.get("m").trim(), dose: fd.get("d").trim(), route: fd.get("r"), status: fd.get("s"), remarks: fd.get("k").trim() || null });
      if (error) alert2(pane, error.message); else showPatient(pid, encId, "✓ Dawai record ho gayi");
    };
  });

  // Notes
  $("nf").onsubmit = async e => {
    e.preventDefault();
    const { error } = await C.sb.from("nursing_notes").insert({ patient_id: pid, encounter_id: encId, kind: $("nk").value, note: $("nt").value.trim() });
    if (error) alert2(pane, error.message); else showPatient(pid, encId, "✓ Note save ho gaya");
  };
}

// ---------- Shift handover ----------
async function showHandover() {
  const pane = $("pane");
  pane.innerHTML = `<div class="card">Loading…</div>`;
  const list = (await currentPatients()).filter(p => p.ipd);
  if (!list.length) { pane.innerHTML = `<div class="card muted">Koi admit patient nahi, handover ki zaroorat nahi.</div>`; return; }
  const ids = list.map(p => p.id);
  const since = new Date(Date.now() - 12 * 3600e3).toISOString();
  const [{ data: vit }, { data: ord }, { data: notes }, { data: meds }] = await Promise.all([
    C.sb.from("vitals").select("*").in("patient_id", ids).order("recorded_at", { ascending: false }).limit(300),
    C.sb.from("doctor_orders").select("patient_id, order_text").in("patient_id", ids).eq("status", "active"),
    C.sb.from("nursing_notes").select("patient_id, kind, note, created_at").in("patient_id", ids).gte("created_at", since).order("created_at", { ascending: false }),
    C.sb.from("medication_administrations").select("patient_id, medicine_name, dose, status, given_at").in("patient_id", ids).gte("given_at", since)
  ]);
  const by = (arr, id) => (arr || []).filter(x => x.patient_id === id);
  pane.innerHTML = `<p class="muted">Pichhle 12 ghante ka saar. Har patient ke liye agli sister ko note likho.</p>` + list.map(p => {
    const v = by(vit, p.id)[0];
    return `<div class="card"><div class="row" style="justify-content:space-between"><b>${C.esc(p.full_name)}</b><span class="badge">${C.esc(p.where)}</span></div>
      ${p.allergies ? `<div class="msg err">⚠️ ${C.esc(p.allergies)}</div>` : ""}
      <p style="font-size:14px"><b>Last vitals:</b> ${v ? `BP ${cell("bp_systolic", v.bp_systolic)}/${cell("bp_diastolic", v.bp_diastolic)}, Pulse ${cell("pulse", v.pulse)}, SpO2 ${cell("spo2", v.spo2)}, Temp ${cell("temperature_f", v.temperature_f)} <small class="muted">(${ago(v.recorded_at)})</small>` : `<span class="msg err">nahi liye</span>`}<br>
      <b>Chalu order:</b> ${by(ord, p.id).map(o => C.esc(o.order_text)).join("; ") || "koi nahi"}<br>
      <b>Di gayi dawai:</b> ${by(meds, p.id).map(m => `${C.esc(m.medicine_name)} ${C.esc(m.dose)}${m.status !== "given" ? " (" + m.status + ")" : ""}`).join("; ") || "koi nahi"}<br>
      <b>Notes:</b> ${by(notes, p.id).map(n => C.esc(n.note)).join(" | ") || "koi nahi"}</p>
      <form data-ho="${p.id}" data-e="${p.encounter_id || ""}" class="row"><input placeholder="Agli sister ke liye handover note" style="flex:1" required><button class="small">Save</button></form>
    </div>`;
  }).join("");
  pane.querySelectorAll("[data-ho]").forEach(f => f.onsubmit = async e => {
    e.preventDefault();
    const inp = f.querySelector("input");
    const { error } = await C.sb.from("nursing_notes").insert({ patient_id: f.dataset.ho, encounter_id: f.dataset.e || null, kind: "handover", note: inp.value.trim() });
    if (error) alert2(pane, error.message); else { inp.value = ""; inp.placeholder = "✓ Save ho gaya"; }
  });
}

// ---------- Alerts ----------
async function showAlerts() {
  const pane = $("pane");
  const { data } = await C.sb.from("notifications").select("*").order("created_at", { ascending: false }).limit(30);
  pane.innerHTML = `<div class="card"><h3>🔔 Alerts</h3>${data?.length ? data.map(a => `
    <div class="note ${a.level}" style="${a.read_at ? "opacity:.5" : ""}"><b>${C.esc(a.title)}</b><br><small>${C.esc(a.body || "")} · ${dt(a.created_at)}</small>
    ${a.read_at ? "" : `<br><button class="small ghost" data-read="${a.id}">Dekh liya</button>`}</div>`).join("")
    : `<p class="muted">Koi alert nahi.</p>`}</div>`;
  pane.querySelectorAll("[data-read]").forEach(b => b.onclick = async () => {
    await C.sb.from("notifications").update({ read_at: new Date().toISOString() }).eq("id", b.dataset.read);
    showAlerts();
  });
}

function msg(id, t, err) { const m = $(id); m.textContent = t; m.className = "msg " + (err ? "err" : "ok"); }
function alert2(root, t) { const d = document.createElement("div"); d.className = "card msg err"; d.textContent = t; root.prepend(d); window.scrollTo(0, 0); }
