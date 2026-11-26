// Vatte Hospital OS — Phase 14: Medical Records (visit note + prescription, discharge summary, documents) and Follow-up
// Notes are never edited: "Badlo" makes a new version with a reason. The server checks the prescription against the patient's allergy.
let C, TAB, MEDS = [];
const $ = id => document.getElementById(id);
const ist = () => new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Kolkata" }));
const ymd = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const addDays = n => ymd(new Date(ist().getTime() + n * 864e5));
const dmy = d => d ? new Date(d).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "";
const dt = t => t ? new Date(t).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }) : "";
const clean = s => String(s || "").replace(/[%,()"\\*]/g, "").trim();
const err = (el, e) => { if (el) { el.className = "msg err"; el.textContent = "❌ " + (e.message || e); } };
const ok = (el, t) => { if (el) { el.className = "msg ok"; el.textContent = t; } };
const can = r => r.includes(C.me.role);
const FREQ = ["1-0-1", "1-1-1", "1-0-0", "0-0-1", "0-1-0", "1-1-1-1", "SOS (zaroorat par)", "Ek baar (stat)", "Hafte mein ek baar"];
const INSTR = ["Khane ke baad", "Khane se pehle", "Khaali pet", "Sone se pehle", "—"];
const DK = { report: "📄 Report", discharge_summary: "🛏️ Discharge", prescription: "💊 Parchi", image: "🖼️ Photo / X-ray", consent: "✍️ Consent", other: "📎 Other" };

export function render(ctx) {
  C = ctx;
  const tabs = [can(["doctor"]) && ["visit", "🩺 Visit note + Parchi"], can(["doctor", "admin", "nurse", "receptionist"]) && ["dis", "🛏️ Discharge summary"],
                can(["doctor", "admin", "nurse", "lab"]) && ["docs", "📎 Documents"], can(["doctor", "admin", "nurse", "receptionist"]) && ["fu", "📞 Follow-up"]].filter(Boolean);
  TAB = tabs[0][0];
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button><h2 style="margin:0 0 6px">🗂️ Medical Records</h2>
    <div class="row" id="tabs" style="gap:6px;margin-bottom:10px">${tabs.map(([k, l]) => `<button class="small ${k === TAB ? "" : "ghost"}" data-t="${k}">${l}</button>`).join("")}</div>
    <div id="body"><div class="card">Loading…</div></div><div id="receipt"></div>`;
  $("bk").onclick = C.goHome;
  C.app.querySelectorAll("#tabs [data-t]").forEach(b => b.onclick = () => go(b.dataset.t));
  C.sb.from("medicines").select("id, name, strength, generic_name").eq("active", true).order("name").then(r => { MEDS = r.data || []; show(); });
}
function go(t) { TAB = t; C.app.querySelectorAll("#tabs [data-t]").forEach(x => x.classList.toggle("ghost", x.dataset.t !== t)); $("receipt").innerHTML = ""; show(); }
function show() { ({ visit, dis, docs, fu })[TAB](); }
const printIt = () => { document.body.classList.add("printing"); window.print(); setTimeout(() => document.body.classList.remove("printing"), 500); };

// ---------------------------------------------------------------- visit list
async function visit() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const since = new Date(addDays(-2) + "T00:00:00+05:30").toISOString();
  const { data } = await C.sb.from("encounters").select("id, kind, status, started_at, chief_complaint, patient_id, patients(full_name, uhid, gender, age_years, allergies), clinical_notes(id, supersedes_id)")
    .neq("status", "cancelled").or(`status.eq.open,started_at.gte.${since}`).order("started_at", { ascending: false }).limit(80);
  const rows = (data || []);
  $("body").innerHTML = `<div class="card"><p class="muted" style="margin:0">Khule visit aur pichhle 2 din ke visit. Patient par tap karo → note + parchi likho.</p></div>` +
    (rows.map(e => `<div class="card" style="cursor:pointer" data-e="${e.id}">
      <div class="row" style="justify-content:space-between"><b>${C.esc(e.patients?.full_name)}</b><span>${e.clinical_notes?.length ? "✅ Note likha" : "✍️ Note baaki"}</span></div>
      <small class="muted">${C.esc(e.patients?.uhid)} · ${e.kind.toUpperCase()} · ${dt(e.started_at)}${e.status === "open" ? " · khula" : ""}${e.chief_complaint ? " · " + C.esc(e.chief_complaint) : ""}</small>
      ${e.patients?.allergies ? `<br><small style="color:var(--red)">⚠️ Allergy: ${C.esc(e.patients.allergies)}</small>` : ""}</div>`).join("") || `<div class="card"><p class="muted">Koi visit nahi. Reception se OPD visit kholein.</p></div>`);
  $("body").querySelectorAll("[data-e]").forEach(c => c.onclick = () => visitForm(c.dataset.e));
}

async function latestNote(encId) {
  const { data } = await C.sb.from("clinical_notes").select("*, prescriptions(items, advice)").eq("encounter_id", encId).order("created_at", { ascending: false });
  const sup = new Set((data || []).map(n => n.supersedes_id).filter(Boolean));
  return { latest: (data || []).find(n => !sup.has(n.id)), all: data || [] };
}

async function visitForm(encId, editing = false) {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const { data: e } = await C.sb.from("encounters").select("*, patients(*)").eq("id", encId).single();
  const [{ latest, all }, { data: v }, { data: hx }] = await Promise.all([
    latestNote(encId),
    C.sb.from("vitals").select("bp_systolic, bp_diastolic, pulse, temperature_f, spo2, resp_rate, recorded_at").eq("patient_id", e.patient_id).order("recorded_at", { ascending: false }).limit(1),
    C.sb.from("hx_sessions").select("doctor_notes, completed_at, status").eq("patient_id", e.patient_id).order("created_at", { ascending: false }).limit(1)]);
  const P = e.patients, lv = v?.[0];
  if (latest && !editing) return noteView(e, latest, all.length);
  const base = editing ? latest : null;
  let RX = base?.prescriptions?.items?.map(i => ({ ...i })) || [];
  $("body").innerHTML = `<button class="ghost small" id="bk2">← Visit list</button>
    <div class="card"><b>${C.esc(P.full_name)}</b> <small class="muted">${C.esc(P.uhid)} · ${C.esc(P.gender || "")} ${P.age_years ? P.age_years + " yr" : ""}</small>
      ${P.allergies ? `<p class="msg err" style="margin:4px 0">⚠️ Allergy: ${C.esc(P.allergies)}</p>` : `<p class="muted" style="margin:4px 0;font-size:12px">Allergy: likhi nahi (Reception mein bharwayein)</p>`}
      ${lv ? `<small>Aakhri vitals ${dt(lv.recorded_at)}: BP ${lv.bp_systolic ?? "–"}/${lv.bp_diastolic ?? "–"} · Pulse ${lv.pulse ?? "–"} · Temp ${lv.temperature_f ?? "–"}°F · SpO2 ${lv.spo2 ?? "–"}%</small>` : ""}
      ${hx?.[0] ? `<br><small class="muted">❓ Nidan history: ${C.esc(hx[0].status)}${hx[0].doctor_notes ? " · " + C.esc(hx[0].doctor_notes) : ""} (Nidan History tile mein poori report)</small>` : ""}</div>
    <div class="card">${editing ? `<p class="msg err" style="margin:0 0 6px">✏️ Naya version ban raha hai — purana bhi record mein rahega.</p>` : ""}
      <label>Shikayat (complaints)</label><textarea id="cc" rows="2">${C.esc(base?.complaints || e.chief_complaint || "")}</textarea>
      <label>History (optional)</label><textarea id="hi" rows="2">${C.esc(base?.history || "")}</textarea>
      <label>Jaanch (examination)</label><textarea id="ex" rows="2">${C.esc(base?.examination || "")}</textarea>
      <div class="row" style="gap:6px"><div style="flex:1"><label>Provisional diagnosis</label><input id="pd" value="${C.esc(base?.provisional_dx || "")}"></div>
        <div style="flex:1"><label>Final diagnosis</label><input id="fd" value="${C.esc(base?.final_dx || "")}"></div></div></div>
    <div class="card"><h3 style="margin:0 0 6px">℞ Parchi</h3><div id="rx"></div>
      <datalist id="meds">${MEDS.map(m => `<option value="${C.esc(`${m.name} ${m.strength || ""}`.trim())}">`).join("")}</datalist>
      <button class="small ghost" id="addrx">＋ Dawa jodo</button>
      <label>Salah (advice)</label><textarea id="ad" rows="2">${C.esc(base?.advice || "")}</textarea>
      <label>Follow-up</label><div class="row" style="gap:6px">${[3, 5, 7, 15, 30].map(n => `<button class="small ghost" data-fu="${n}">${n} din</button>`).join("")}
        <input type="date" id="fu" min="${addDays(1)}" value="${base?.follow_up_on || ""}" style="width:auto"></div>
      ${editing ? `<label>Badalne ka kaaran (zaroori)</label><input id="why">` : ""}
      <button class="full" id="sv" style="margin-top:10px">💾 Save + 🖨️ Parchi</button><p class="msg" id="vm"></p>
      <p class="muted" style="font-size:12px">Save hote hi parchi Pharmacy ko dikhegi aur follow-up list mein judega.</p></div>`;
  $("bk2").onclick = visit;
  const draw = () => {
    $("rx").innerHTML = RX.map((r, i) => `<div style="border-top:1px solid var(--line);padding:6px 0" data-i="${i}">
      <div class="row" style="gap:6px"><input list="meds" data-k="medicine" value="${C.esc(r.medicine || "")}" placeholder="Dawa ka naam" style="flex:3">
        <button class="small ghost" data-del="${i}">✖</button></div>
      <div class="row" style="gap:6px"><input data-k="dose" value="${C.esc(r.dose || "")}" placeholder="Kitna (1 tab / 5 ml)" style="flex:2">
        <select data-k="frequency" style="flex:2">${FREQ.map(f => `<option ${r.frequency === f ? "selected" : ""}>${f}</option>`).join("")}</select>
        <input data-k="days" type="number" min="1" max="365" value="${r.days || ""}" placeholder="Din" style="flex:1"></div>
      <select data-k="instructions">${INSTR.map(f => `<option ${r.instructions === f ? "selected" : ""}>${f}</option>`).join("")}</select></div>`).join("") || "<p class='muted'>Abhi koi dawa nahi.</p>";
    $("rx").querySelectorAll("[data-k]").forEach(el => el.onchange = el.oninput = () => { RX[+el.closest("[data-i]").dataset.i][el.dataset.k] = el.value; });
    $("rx").querySelectorAll("[data-del]").forEach(b => b.onclick = () => { RX.splice(+b.dataset.del, 1); draw(); });
  };
  draw();
  $("addrx").onclick = () => { RX.push({ frequency: "1-0-1", instructions: "Khane ke baad" }); draw(); };
  $("body").querySelectorAll("[data-fu]").forEach(b => b.onclick = () => { $("fu").value = addDays(+b.dataset.fu); });
  const save = async override => {
    const items = RX.filter(r => (r.medicine || "").trim()).map(r => {
      const m = MEDS.find(x => `${x.name} ${x.strength || ""}`.trim().toLowerCase() === r.medicine.trim().toLowerCase());
      return { ...r, medicine_id: m?.id || null, instructions: r.instructions === "—" ? null : r.instructions, days: r.days ? Number(r.days) : null };
    });
    $("sv").disabled = true;
    const { data: n, error } = await C.sb.rpc("rec_save_visit", { p_encounter: encId,
      p_note: { complaints: $("cc").value, history: $("hi").value, examination: $("ex").value, provisional_dx: $("pd").value, final_dx: $("fd").value, advice: $("ad").value },
      p_rx: items, p_follow_up: $("fu").value || null, p_allergy_override: override || null,
      p_supersedes: editing ? latest.id : null, p_amend_reason: $("why")?.value || null });
    $("sv").disabled = false;
    if (error) {
      if (/ALLERGY/.test(error.message)) {
        const why = prompt("⚠️ " + error.message + "\n\nPhir bhi likhni hai to kaaran likhein (warna Cancel):");
        if (why && why.trim()) return save(why);
      }
      return err($("vm"), error);
    }
    visitForm(encId); setTimeout(() => rxPrint(encId), 300);
  };
  $("sv").onclick = () => save(null);
}

async function noteView(e, n, versions) {
  const P = e.patients, items = n.prescriptions?.items || [];
  $("body").innerHTML = `<button class="ghost small" id="bk2">← Visit list</button><div class="card">
    <div class="row" style="justify-content:space-between"><b>${C.esc(P.full_name)}</b><small class="muted">${dt(n.created_at)}${versions > 1 ? ` · version ${versions}` : ""}</small></div>
    ${n.amend_reason ? `<p class="msg err" style="margin:4px 0">✏️ Badla: ${C.esc(n.amend_reason)}</p>` : ""}
    ${n.complaints ? `<p><b>Shikayat:</b> ${C.esc(n.complaints)}</p>` : ""}${n.examination ? `<p><b>Jaanch:</b> ${C.esc(n.examination)}</p>` : ""}
    ${n.provisional_dx ? `<p><b>Provisional Dx:</b> ${C.esc(n.provisional_dx)}</p>` : ""}${n.final_dx ? `<p><b>Final Dx:</b> ${C.esc(n.final_dx)}</p>` : ""}
    ${items.length ? `<p><b>℞</b><br>${items.map((r, i) => `${i + 1}. ${C.esc(r.medicine)} ${C.esc(r.dose || "")} · ${C.esc(r.frequency)}${r.days ? " · " + r.days + " din" : ""}${r.instructions ? " · " + C.esc(r.instructions) : ""}`).join("<br>")}</p>` : ""}
    ${n.advice ? `<p><b>Salah:</b> ${C.esc(n.advice)}</p>` : ""}${n.follow_up_on ? `<p><b>Follow-up:</b> ${dmy(n.follow_up_on)}</p>` : ""}
    ${n.allergy_override ? `<p class="msg err">⚠️ Allergy override: ${C.esc(n.allergy_override)}</p>` : ""}
    <div class="row" style="gap:6px"><button id="pr">🖨️ Parchi print</button><button class="ghost" id="ed">✏️ Badlo (naya version)</button></div></div>`;
  $("bk2").onclick = visit;
  $("pr").onclick = () => rxPrint(e.id);
  $("ed").onclick = () => visitForm(e.id, true);
}

async function rxPrint(encId) {
  const [{ data: e }, { latest: n }, { data: h }, { data: doc }] = await Promise.all([
    C.sb.from("encounters").select("*, patients(*)").eq("id", encId).single(), latestNote(encId),
    C.sb.from("hospitals").select("name").maybeSingle(), C.sb.from("profiles").select("full_name").eq("id", C.me.id).maybeSingle()]);
  if (!n) return;
  const P = e.patients, items = n.prescriptions?.items || [], v = n.vitals_snapshot;
  $("receipt").innerHTML = `<div class="card" id="rcpt" style="max-width:600px;margin:10px auto;font-size:14px">
    <div style="text-align:center"><b style="font-size:19px">${C.esc(h?.name || "Hospital")}</b><br><small>Dr. ${C.esc((doc?.full_name || C.me.full_name || "").replace(/^dr\.?\s*/i, ""))}</small></div><hr>
    <div class="row" style="justify-content:space-between"><span><b>${C.esc(P.full_name)}</b> · ${C.esc(P.gender || "")} ${P.age_years ? P.age_years + " yr" : ""} · ${C.esc(P.uhid)}</span><span>${dmy(n.created_at)}</span></div>
    ${P.allergies ? `<div style="color:#dc2626">Allergy: ${C.esc(P.allergies)}</div>` : ""}
    ${v ? `<small>BP ${v.bp_systolic ?? "–"}/${v.bp_diastolic ?? "–"} · Pulse ${v.pulse ?? "–"} · Temp ${v.temperature_f ?? "–"}°F · SpO2 ${v.spo2 ?? "–"}%</small>` : ""}<hr>
    ${n.complaints ? `<div><b>C/O:</b> ${C.esc(n.complaints)}</div>` : ""}${n.examination ? `<div><b>O/E:</b> ${C.esc(n.examination)}</div>` : ""}
    ${n.final_dx || n.provisional_dx ? `<div><b>Dx:</b> ${C.esc(n.final_dx || n.provisional_dx)}</div>` : ""}
    <div style="font-size:22px;margin-top:8px">℞</div>
    <table style="width:100%">${items.map((r, i) => `<tr><td style="vertical-align:top">${i + 1}.</td><td><b>${C.esc(r.medicine)}</b> ${C.esc(r.dose || "")}<br>
      <small>${C.esc(r.frequency)}${r.days ? " × " + r.days + " din" : ""}${r.instructions ? " · " + C.esc(r.instructions) : ""}</small></td></tr>`).join("") || "<tr><td>—</td></tr>"}</table>
    ${n.advice ? `<div style="margin-top:8px"><b>Salah:</b> ${C.esc(n.advice)}</div>` : ""}
    ${n.follow_up_on ? `<div style="margin-top:6px"><b>Dobara dikhayein:</b> ${dmy(n.follow_up_on)}</div>` : ""}
    <div style="text-align:right;margin-top:30px">______________________<br><small>Doctor ke hastakshar</small></div></div>
    <div class="row noprint" style="gap:6px;justify-content:center"><button id="rp">🖨️ Print / PDF</button><button class="ghost" id="rc">Band karo</button></div>`;
  $("rp").onclick = printIt; $("rc").onclick = () => { $("receipt").innerHTML = ""; };
  $("receipt").scrollIntoView({ behavior: "smooth" });
}

// ---------------------------------------------------------------- discharge summary
async function dis() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const since = new Date(Date.now() - 30 * 864e5).toISOString();
  const { data } = await C.sb.from("admissions").select("id, status, admitted_at, discharged_at, patient_id, patients(full_name, uhid), beds(label), discharge_summaries(id)")
    .or(`status.eq.admitted,discharged_at.gte.${since}`).order("admitted_at", { ascending: false }).limit(60);
  $("body").innerHTML = (data || []).map(a => `<div class="card" style="cursor:pointer" data-a="${a.id}">
      <div class="row" style="justify-content:space-between"><b>${C.esc(a.patients?.full_name)}</b><span>${a.discharge_summaries?.length ? "✅ Summary bani" : a.status === "admitted" ? "🛏️ Admit" : "✍️ Summary baaki"}</span></div>
      <small class="muted">${C.esc(a.patients?.uhid)} · bed ${C.esc(a.beds?.label || "")} · ${dmy(a.admitted_at)}${a.discharged_at ? " → " + dmy(a.discharged_at) + " (" + a.status + ")" : ""}</small></div>`).join("")
    || `<div class="card"><p class="muted">Koi admit / haal ka discharge nahi.</p></div>`;
  $("body").querySelectorAll("[data-a]").forEach(c => c.onclick = () => disForm(c.dataset.a));
}
async function disForm(admId, editing = false) {
  const { data: a } = await C.sb.from("admissions").select("*, patients(*), beds(label, rooms(name))").eq("id", admId).single();
  const [{ data: list }, { data: labs }] = await Promise.all([
    C.sb.from("discharge_summaries").select("*").eq("admission_id", admId).order("created_at", { ascending: false }),
    C.sb.from("lab_orders").select("result, reported_at, lab_tests(name)").eq("patient_id", a.patient_id).eq("status", "reported").gte("reported_at", a.admitted_at).order("reported_at").limit(40)]);
  const sup = new Set((list || []).map(d => d.supersedes_id).filter(Boolean));
  const cur = (list || []).find(d => !sup.has(d.id));
  if (cur && !editing) return disView(a, cur, list.length);
  if (!can(["doctor"])) { $("body").innerHTML = `<button class="ghost small" id="bk2">← List</button><div class="card"><p class="muted">Summary abhi nahi bani — Doctor likhenge.</p></div>`; $("bk2").onclick = dis; return; }
  const b = editing ? cur : null;
  let MED = (b?.medicines || []).map(x => ({ ...x }));
  const labTxt = (labs || []).filter(l => l.result).map(l => `${l.lab_tests?.name}: ${l.result}`).join("\n");
  $("body").innerHTML = `<button class="ghost small" id="bk2">← List</button><div class="card">
    <b>${C.esc(a.patients.full_name)}</b> <small class="muted">${C.esc(a.patients.uhid)} · admit ${dmy(a.admitted_at)}${a.discharged_at ? " · discharge " + dmy(a.discharged_at) : ""}</small>
    ${a.patients.allergies ? `<p class="msg err" style="margin:4px 0">⚠️ Allergy: ${C.esc(a.patients.allergies)}</p>` : ""}
    <label>Diagnosis (zaroori)</label><input id="dg" value="${C.esc(b?.diagnosis || "")}">
    <label>Hospital mein ilaaj (course)</label><textarea id="co" rows="3">${C.esc(b?.course || "")}</textarea>
    <label>Procedure / operation</label><input id="pc" value="${C.esc(b?.procedures || "")}">
    <label>Jaanch (lab) — apne aap bhara, badal sakte ho</label><textarea id="iv" rows="3">${C.esc(b?.investigations || labTxt)}</textarea>
    <label>Chhutti ke samay haalat</label><input id="cd" value="${C.esc(b?.condition_at_discharge || "")}" placeholder="Stable, bukhar nahi">
    <h4 style="margin:8px 0 4px">Ghar ki dawa</h4><div id="dm"></div><button class="small ghost" id="adm">＋ Dawa</button>
    <datalist id="meds">${MEDS.map(m => `<option value="${C.esc(`${m.name} ${m.strength || ""}`.trim())}">`).join("")}</datalist>
    <label>Salah</label><textarea id="ad" rows="2">${C.esc(b?.advice || "")}</textarea>
    <label>Follow-up</label><input type="date" id="fu" min="${addDays(1)}" value="${b?.follow_up_on || ""}">
    ${editing ? `<label>Badalne ka kaaran</label><input id="why">` : ""}
    <button class="full" id="sv" style="margin-top:8px">💾 Save + 🖨️ Print</button><p class="msg" id="dmm"></p></div>`;
  $("bk2").onclick = dis;
  const draw = () => {
    $("dm").innerHTML = MED.map((r, i) => `<div class="row" style="gap:6px" data-i="${i}"><input list="meds" data-k="medicine" value="${C.esc(r.medicine || "")}" placeholder="Dawa" style="flex:3">
      <select data-k="frequency" style="flex:2">${FREQ.map(f => `<option ${r.frequency === f ? "selected" : ""}>${f}</option>`).join("")}</select>
      <input data-k="days" type="number" min="1" value="${r.days || ""}" placeholder="Din" style="flex:1"><button class="small ghost" data-del="${i}">✖</button></div>`).join("");
    $("dm").querySelectorAll("[data-k]").forEach(el => el.onchange = el.oninput = () => { MED[+el.closest("[data-i]").dataset.i][el.dataset.k] = el.value; });
    $("dm").querySelectorAll("[data-del]").forEach(x => x.onclick = () => { MED.splice(+x.dataset.del, 1); draw(); });
  };
  draw();
  $("adm").onclick = () => { MED.push({ frequency: "1-0-1" }); draw(); };
  const save = async override => {
    const meds = MED.filter(r => (r.medicine || "").trim()).map(r => ({ ...r, days: r.days ? Number(r.days) : null,
      medicine_id: MEDS.find(x => `${x.name} ${x.strength || ""}`.trim().toLowerCase() === r.medicine.trim().toLowerCase())?.id || null }));
    const { error } = await C.sb.rpc("rec_save_discharge", { p_admission: admId, p_data: { diagnosis: $("dg").value, course: $("co").value, procedures: $("pc").value,
      investigations: $("iv").value, condition_at_discharge: $("cd").value, medicines: meds, advice: $("ad").value, follow_up_on: $("fu").value || null, allergy_override: override || null },
      p_supersedes: editing ? cur.id : null, p_amend_reason: $("why")?.value || null });
    if (error) {
      if (/ALLERGY/.test(error.message)) { const why = prompt("⚠️ " + error.message + "\n\nKaaran:"); if (why && why.trim()) return save(why); }
      return err($("dmm"), error);
    }
    disForm(admId);
  };
  $("sv").onclick = () => save(null);
}
async function disView(a, d, versions) {
  const { data: h } = await C.sb.from("hospitals").select("name").maybeSingle();
  const P = a.patients;
  $("body").innerHTML = `<button class="ghost small" id="bk2">← List</button>`;
  $("bk2").onclick = dis;
  $("receipt").innerHTML = `<div class="card" id="rcpt" style="max-width:640px;margin:10px auto;font-size:14px">
    <div style="text-align:center"><b style="font-size:19px">${C.esc(h?.name || "Hospital")}</b><br><b>DISCHARGE SUMMARY</b>${versions > 1 ? `<br><small style="color:#b45309">Amended (version ${versions})</small>` : ""}</div><hr>
    <div><b>${C.esc(P.full_name)}</b> · ${C.esc(P.gender || "")} ${P.age_years ? P.age_years + " yr" : ""} · UHID ${C.esc(P.uhid)}</div>
    <div>Admit: ${dmy(a.admitted_at)} · Discharge: ${a.discharged_at ? dmy(a.discharged_at) : "—"} · ${C.esc(a.beds?.rooms?.name || "")} ${C.esc(a.beds?.label || "")}</div>
    ${P.allergies ? `<div style="color:#dc2626">Allergy: ${C.esc(P.allergies)}</div>` : ""}<hr>
    <p><b>Diagnosis:</b> ${C.esc(d.diagnosis)}</p>
    ${d.course ? `<p><b>Hospital mein ilaaj:</b><br>${C.esc(d.course).replace(/\n/g, "<br>")}</p>` : ""}
    ${d.procedures ? `<p><b>Procedure:</b> ${C.esc(d.procedures)}</p>` : ""}
    ${d.investigations ? `<p><b>Jaanch:</b><br><small>${C.esc(d.investigations).replace(/\n/g, "<br>")}</small></p>` : ""}
    ${d.condition_at_discharge ? `<p><b>Chhutti ke samay:</b> ${C.esc(d.condition_at_discharge)}</p>` : ""}
    ${(d.medicines || []).length ? `<p><b>Ghar ki dawa:</b><br>${d.medicines.map((r, i) => `${i + 1}. ${C.esc(r.medicine)} · ${C.esc(r.frequency || "")}${r.days ? " × " + r.days + " din" : ""}`).join("<br>")}</p>` : ""}
    ${d.advice ? `<p><b>Salah:</b> ${C.esc(d.advice).replace(/\n/g, "<br>")}</p>` : ""}
    ${d.follow_up_on ? `<p><b>Dobara dikhayein:</b> ${dmy(d.follow_up_on)}</p>` : ""}
    <p><small>Takleef badhe (tez bukhar, saans phoolna, behoshi, khoon aana) to turant hospital aayein.</small></p>
    <div style="text-align:right;margin-top:24px">______________________<br><small>Doctor ke hastakshar · ${dmy(d.created_at)}</small></div></div>
    <div class="row noprint" style="gap:6px;justify-content:center"><button id="rp">🖨️ Print / PDF</button>${can(["doctor"]) ? `<button class="ghost" id="ed">✏️ Badlo</button>` : ""}<button class="ghost" id="rc">Band karo</button></div>`;
  $("rp").onclick = printIt; $("rc").onclick = () => { $("receipt").innerHTML = ""; };
  if ($("ed")) $("ed").onclick = () => { $("receipt").innerHTML = ""; disForm(a.id, true); };
}

// ---------------------------------------------------------------- documents
function docs() {
  $("body").innerHTML = `<div class="card"><label>Patient (naam / UHID / phone)</label><input id="pq" autocomplete="off"><div id="pres"></div></div><div id="dl"></div>`;
  let t;
  $("pq").oninput = () => { clearTimeout(t); t = setTimeout(async () => {
    const q = clean($("pq").value);
    if (q.length < 2) { $("pres").innerHTML = ""; return; }
    const { data } = await C.sb.rpc("search_patients", { q });
    $("pres").innerHTML = (data || []).slice(0, 6).map(p => `<button class="small ghost" style="margin:3px" data-p='${C.esc(JSON.stringify({ id: p.id, full_name: p.full_name, uhid: p.uhid }))}'>${C.esc(p.full_name)} · ${C.esc(p.uhid)}</button>`).join("") || "<small class='muted'>Koi nahi mila</small>";
    $("pres").querySelectorAll("[data-p]").forEach(b => b.onclick = () => { $("pres").innerHTML = ""; docList(JSON.parse(b.dataset.p)); });
  }, 300); };
}
async function docList(P) {
  const { data } = await C.sb.from("medical_documents").select("*").eq("patient_id", P.id).order("created_at", { ascending: false });
  $("dl").innerHTML = `<div class="card"><b>${C.esc(P.full_name)}</b> <small class="muted">${C.esc(P.uhid)}</small>
      <label>Naam (jaise: Bahar ki CBC report 20 Nov)</label><input id="dt">
      <label>Kis tarah ka</label><select id="dk">${Object.entries(DK).map(([k, v]) => `<option value="${k}">${v}</option>`).join("")}</select>
      <label>File (photo ya PDF, 10 MB tak)</label><input type="file" id="df" accept="image/*,application/pdf">
      <button class="full" id="up">⬆️ Upload</button><p class="msg" id="um"></p></div>
    <div class="card">${(data || []).map(d => `<div class="row" style="justify-content:space-between;border-top:1px solid var(--line);padding:6px 0">
      <span>${DK[d.kind] || "📎"} ${C.esc(d.title)}<br><small class="muted">${dt(d.created_at)}</small></span><button class="small ghost" data-v="${C.esc(d.storage_path)}">👁️ Dekho</button></div>`).join("") || "<p class='muted'>Abhi koi document nahi.</p>"}</div>`;
  $("dl").querySelectorAll("[data-v]").forEach(b => b.onclick = async () => {
    const { data: s, error } = await C.sb.storage.from("medical-docs").createSignedUrl(b.dataset.v, 300);
    if (error) return alert("❌ " + error.message);
    window.open(s.signedUrl, "_blank");
  });
  $("up").onclick = async () => {
    const f = $("df").files[0];
    if (!f) return err($("um"), "File chunein");
    if (f.size > 10 * 1024 * 1024) return err($("um"), "File 10 MB se badi hai");
    if (!$("dt").value.trim()) return err($("um"), "Document ka naam likhein");
    $("up").disabled = true; $("um").className = "msg"; $("um").textContent = "Upload ho raha hai…";
    const path = `${C.me.hospital_id}/${P.id}/${Date.now()}-${f.name.replace(/[^a-zA-Z0-9._-]/g, "_").slice(-60)}`;
    const up = await C.sb.storage.from("medical-docs").upload(path, f, { contentType: f.type, upsert: false });
    if (up.error) { $("up").disabled = false; return err($("um"), up.error); }
    const { error } = await C.sb.from("medical_documents").insert({ hospital_id: C.me.hospital_id, patient_id: P.id, title: $("dt").value.trim(), kind: $("dk").value, storage_path: path, mime: f.type, size_bytes: f.size });
    if (error) { $("up").disabled = false; return err($("um"), error); }
    docList(P);
  };
}

// ---------------------------------------------------------------- follow-up
async function fu() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const today = ymd(ist());
  const { data, error } = await C.sb.from("follow_ups").select("id, due_on, reason, feedback, patients(full_name, uhid, phone)")
    .eq("status", "pending").lte("due_on", addDays(7)).order("due_on").limit(200);
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const late = data.filter(f => f.due_on < today), now = data.filter(f => f.due_on === today), soon = data.filter(f => f.due_on > today);
  const wa = (f) => {
    let p = String(f.patients?.phone || "").replace(/\D/g, ""); if (p.length === 10) p = "91" + p;
    const msg = `Namaste ${f.patients?.full_name || ""} ji, ${C.me.hospital_name || "Hospital"} se. Aapko ${dmy(f.due_on)} ko dobara dikhane aana hai${f.reason ? " (" + f.reason + ")" : ""}. Kripya samay par aayein. Dhanyavaad 🙏`;
    return p ? `https://wa.me/${p}?text=${encodeURIComponent(msg)}` : null;
  };
  const card = f => `<div class="card" ${f.due_on < today ? `style="border-color:#fca5a5"` : ""}>
      <div class="row" style="justify-content:space-between"><b>${C.esc(f.patients?.full_name)}</b><small>${dmy(f.due_on)}</small></div>
      <small class="muted">${C.esc(f.patients?.uhid)}${f.reason ? " · " + C.esc(f.reason) : ""}</small>${f.feedback ? `<br><small>${C.esc(f.feedback)}</small>` : ""}
      <div class="row" style="gap:6px;margin-top:6px">
        ${f.patients?.phone ? `<a class="small" href="tel:${C.esc(f.patients.phone)}" style="text-decoration:none"><button class="small">📞 Call</button></a>` : ""}
        ${wa(f) ? `<a href="${wa(f)}" target="_blank" rel="noopener" style="text-decoration:none"><button class="small ghost">💬 WhatsApp</button></a>` : ""}
        <button class="small ghost" data-c="${f.id}">📝 Baat hui</button><button class="small ghost" data-m="${f.id}">📅 Date badlo</button>
        <button class="small ghost" data-d="${f.id}">✅ Aa gaya</button><button class="small ghost" data-x="${f.id}">❌ Nahi aaya</button></div>
      <p class="msg" id="m${f.id}"></p></div>`;
  $("body").innerHTML = `<div class="card"><small class="muted">Patient ka naya visit khulte hi (±3 din) follow-up apne aap "✅ Aa gaya" ho jaata hai.</small></div>
    ${late.length ? `<h3>🔴 Late (${late.length})</h3>${late.map(card).join("")}` : ""}
    <h3>📅 Aaj (${now.length})</h3>${now.map(card).join("") || "<div class='card'><p class='muted'>Aaj koi nahi.</p></div>"}
    ${soon.length ? `<h3>⏭️ Agle 7 din (${soon.length})</h3>${soon.map(card).join("")}` : ""}`;
  const act = (sel, st) => $("body").querySelectorAll(sel).forEach(b => b.onclick = async () => {
    const id = b.dataset.c || b.dataset.m || b.dataset.d || b.dataset.x;
    let fb = null, nd = null;
    if (st === "called") { fb = prompt("Call par kya baat hui?") || ""; if (!fb.trim()) return; }
    if (st === "moved") { nd = prompt("Nayi date (YYYY-MM-DD)", addDays(3)) || ""; if (!/^\d{4}-\d{2}-\d{2}$/.test(nd)) return; fb = prompt("Kaaran (optional)") || ""; }
    if (st === "missed") fb = prompt("Kaaran (optional)") || "";
    const { error } = await C.sb.rpc("fu_update", { p_id: id, p_status: st, p_feedback: fb, p_new_due: nd });
    if (error) return err($("m" + id), error);
    fu();
  });
  act("[data-c]", "called"); act("[data-m]", "moved"); act("[data-d]", "done"); act("[data-x]", "missed");
}
