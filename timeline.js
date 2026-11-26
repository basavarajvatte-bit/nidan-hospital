// Vatte Hospital OS — Patient timeline: everything about one patient, from registration to today.
// Each section is read with the user's own login, so every role sees only what it is allowed to see.
const tel = ph => { const d = String(ph || "").replace(/\D/g, ""); return d.length === 10 ? "+91" + d : d ? "+" + d.replace(/^0+/, "") : ""; };
const callBtn = ph => tel(ph) ? `<a class="callbtn" href="tel:${tel(ph)}" onclick="event.stopPropagation()">📞 Call</a>` : "";
let C, P, ITEMS = [], FILTER = "all", BACK = null;
const $ = id => document.getElementById(id);
const dt = t => t ? new Date(t).toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "—";
const KINDS = {
  reg: ["🆕", "Registration"], visit: ["🏥", "Visit"], admit: ["🛏️", "Admit / Discharge"], vitals: ["🩺", "Vitals"],
  order: ["📝", "Doctor order"], rx: ["💊", "Prescription"], med: ["💉", "Dawa di gayi"], note: ["🗒️", "Sister note"],
  lab: ["🧪", "Lab"], hx: ["❓", "Nidan history"], fu: ["📞", "Follow-up"], bill: ["💰", "Bill"], doc: ["📎", "Document"], appt: ["📅", "Appointment"]
};
const FILTERS = [["all", "Sab"], ["vitals", "Vitals"], ["med", "Dawa"], ["order", "Orders"], ["note", "Notes"], ["lab", "Lab"], ["hx", "History"], ["bill", "Bill"]];
const GROUP = { med: ["rx", "med"], order: ["order"], note: ["note"], vitals: ["vitals"], lab: ["lab"], hx: ["hx"], bill: ["bill"] };

export async function render(ctx, key, back = null) {
  C = ctx; BACK = back; FILTER = "all"; ITEMS = [];
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button><div id="tl"><div class="card">Loading…</div></div>`;
  $("bk").onclick = () => (BACK ? BACK() : C.goHome());
  const isId = /^[0-9a-f-]{36}$/i.test(key);
  const { data: p, error } = await C.sb.from("patients").select("*").eq(isId ? "id" : "uhid", key).maybeSingle();
  if (error || !p) { $("tl").innerHTML = `<div class="card msg err">Patient nahi mila${error ? ": " + C.esc(error.message) : ""}</div>`; return; }
  P = p;
  await load();
}

async function load() {
  const id = P.id;
  const q = (t, cols, order) => C.sb.from(t).select(cols).eq("patient_id", id).order(order, { ascending: true }).limit(500);
  const res = await Promise.all([
    q("encounters", "id, kind, status, chief_complaint, started_at, ended_at, doctor_id", "started_at"),
    q("admissions", "id, admitted_at, discharged_at, status, discharge_summary, beds(label, rooms(name))", "admitted_at"),
    q("vitals", "bp_systolic, bp_diastolic, pulse, temperature_f, spo2, resp_rate, intake_ml, output_ml, recorded_at, recorded_by, corrects_id", "recorded_at"),
    q("doctor_orders", "order_text, status, ordered_by, created_at", "created_at"),
    q("prescriptions", "items, advice, prescribed_by, created_at", "created_at"),
    q("medication_administrations", "medicine_name, dose, route, status, remarks, given_by, given_at", "given_at"),
    q("nursing_notes", "kind, note, created_by, created_at, corrects_id", "created_at"),
    q("lab_orders", "status, result, is_critical, ordered_at, reported_at, lab_tests(name)", "ordered_at"),
    q("hx_sessions", "id, status, complaints, emergency, doctor_notes, created_at, completed_at, created_by", "created_at"),
    q("follow_ups", "due_on, reason, status, feedback, created_at", "created_at"),
    q("invoices", "invoice_no, category, total, discount, status, created_at", "created_at"),
    q("medical_documents", "title, kind, created_at", "created_at"),
    q("appointments", "starts_at, status, reason", "starts_at"),
    q("clinical_notes", "complaints, examination, provisional_dx, final_dx, advice, amend_reason, written_by, created_at", "created_at"),
    q("discharge_summaries", "diagnosis, condition_at_discharge, amend_reason, written_by, created_at", "created_at"),
    C.sb.from("profiles").select("id, full_name"),
    C.sb.from("hx_complaints").select("id, name_en")
  ]);
  const [enc, adm, vit, ord, rx, med, notes, lab, hx, fu, inv, docs, appt, cn, ds, staff, hxc] = res.map(r => r.data || []);
  const hidden = ["encounters", "admissions", "vitals", "orders", "prescriptions", "dawa", "notes", "lab", "history", "follow-up", "bills", "documents", "appointments", "doctor notes", "discharge summary"]
    .filter((_, i) => res[i].error);
  const who = uid => uid ? (staff.find(s => s.id === uid)?.full_name || "staff") : "";
  const cname = cid => hxc.find(c => c.id === cid)?.name_en || cid;
  const add = (k, at, title, body = "", by = "", flag = false) => at && ITEMS.push({ k, at, title, body, by, flag });

  ITEMS = [];
  add("reg", P.created_at, "Hospital mein registration", `UHID ${P.uhid}`, who(P.created_by));
  enc.forEach(e => add("visit", e.started_at, `${e.kind.toUpperCase()} visit shuru`, e.chief_complaint || "", who(e.doctor_id)));
  enc.filter(e => e.ended_at).forEach(e => add("visit", e.ended_at, `${e.kind.toUpperCase()} visit band (${e.status})`));
  adm.forEach(a => {
    add("admit", a.admitted_at, `Admit — ${a.beds?.rooms?.name || ""} ${a.beds?.label || ""}`.trim());
    if (a.discharged_at) add("admit", a.discharged_at, `Discharge (${a.status})`, a.discharge_summary || "");
  });
  vit.forEach(v => {
    const parts = [v.bp_systolic && `BP ${v.bp_systolic}/${v.bp_diastolic ?? "?"}`, v.pulse && `Pulse ${v.pulse}`, v.temperature_f && `Temp ${v.temperature_f}°F`,
      v.spo2 && `SpO2 ${v.spo2}%`, v.resp_rate && `Saans ${v.resp_rate}`, v.intake_ml && `Intake ${v.intake_ml} ml`, v.output_ml && `Output ${v.output_ml} ml`].filter(Boolean);
    const bad = (v.bp_systolic >= 180 || (v.bp_systolic && v.bp_systolic < 90) || (v.spo2 && v.spo2 < 92) || v.pulse > 130 || (v.pulse && v.pulse < 50) || v.temperature_f >= 103);
    add("vitals", v.recorded_at, v.corrects_id ? "Vitals (sudhaar)" : "Vitals", parts.join(" · "), who(v.recorded_by), bad);
  });
  ord.forEach(o => add("order", o.created_at, `Doctor order (${o.status})`, o.order_text, who(o.ordered_by)));
  rx.forEach(r => {
    const items = Array.isArray(r.items) ? r.items.map(i => typeof i === "string" ? i :
      [i.name || i.medicine || i.drug, i.dose || i.strength, i.frequency || i.freq, i.days && `${i.days} din`].filter(Boolean).join(" ")).join("\n") : "";
    add("rx", r.created_at, "Prescription", [items, r.advice && "Salah: " + r.advice].filter(Boolean).join("\n"), who(r.prescribed_by));
  });
  med.forEach(m => add("med", m.given_at, `${m.medicine_name} ${m.dose || ""} ${m.route || ""}`.trim(), [m.status !== "given" ? m.status : "", m.remarks].filter(Boolean).join(" · "), who(m.given_by), m.status !== "given"));
  notes.forEach(n => add("note", n.created_at, n.corrects_id ? `Note sudhaar (${n.kind})` : `Note (${n.kind})`, n.note, who(n.created_by)));
  lab.forEach(l => {
    add("lab", l.ordered_at, `Test order: ${l.lab_tests?.name || "test"}`, l.status);
    if (l.reported_at) add("lab", l.reported_at, `Report: ${l.lab_tests?.name || "test"}${l.is_critical ? " ⚠️ CRITICAL" : ""}`, l.result || "", "", l.is_critical);
  });
  hx.forEach(h => add("hx", h.completed_at || h.created_at, `Nidan history (${h.status})${h.emergency ? " 🚨" : ""}`,
    [(h.complaints || []).map(c => `${cname(c.id)}${c.duration ? " — " + c.duration : ""}`).join(", "), h.doctor_notes && "Doctor: " + h.doctor_notes].filter(Boolean).join("\n"), who(h.created_by), h.emergency));
  fu.forEach(f => add("fu", f.created_at, `Follow-up ${f.due_on} (${f.status})`, [f.reason, f.feedback].filter(Boolean).join(" · ")));
  inv.forEach(i => add("bill", i.created_at, `Bill ${i.invoice_no || ""} — ${i.category}`, `₹${Number(i.total - (i.discount || 0)).toLocaleString("en-IN")} · ${i.status}`));
  docs.forEach(d => add("doc", d.created_at, `Document: ${d.title}`, d.kind || ""));
  appt.forEach(a => add("appt", a.starts_at, `Appointment (${a.status})`, a.reason || ""));
  cn.forEach(n => add("note", n.created_at, n.amend_reason ? "🩺 Doctor note (badla)" : "🩺 Doctor note",
    [n.complaints && "C/O: " + n.complaints, n.examination && "O/E: " + n.examination, (n.final_dx || n.provisional_dx) && "Dx: " + (n.final_dx || n.provisional_dx), n.advice && "Salah: " + n.advice, n.amend_reason && "Kaaran: " + n.amend_reason].filter(Boolean).join("\n"), who(n.written_by)));
  ds.forEach(d => add("admit", d.created_at, d.amend_reason ? "🛏️ Discharge summary (badli)" : "🛏️ Discharge summary", [d.diagnosis, d.condition_at_discharge].filter(Boolean).join(" · "), who(d.written_by)));
  ITEMS.sort((a, b) => new Date(a.at) - new Date(b.at));

  const now = adm.find(a => a.status === "admitted");
  const lastV = [...vit].reverse()[0];
  const age = P.age_years != null ? P.age_years + " saal" : "";
  $("tl").innerHTML = `
    <div class="card">
      <div class="row" style="justify-content:space-between;gap:6px"><h2 style="margin:0">${C.esc(P.full_name)}</h2>${callBtn(P.phone)}</div>
      <p class="muted" style="margin:4px 0">${C.esc(P.uhid)} · ${C.esc(P.gender || "")} ${age ? "· " + age : ""} ${P.phone ? "· " + C.esc(P.phone) : ""} ${P.blood_group ? "· 🩸 " + C.esc(P.blood_group) : ""}</p>
      ${P.allergies ? `<p class="msg err" style="margin:4px 0">⚠️ Allergy: ${C.esc(P.allergies)}</p>` : ""}
      <p style="margin:4px 0">${now ? `🛏️ <b>Abhi admit</b> — ${C.esc(now.beds?.rooms?.name || "")} ${C.esc(now.beds?.label || "")} (${dt(now.admitted_at)} se)` : "Abhi admit nahi"}</p>
      ${lastV ? `<p class="muted" style="margin:4px 0">Aakhri vitals: ${dt(lastV.recorded_at)}</p>` : ""}
      <p class="muted" style="margin:4px 0;font-size:12px">Hospital mein pehli entry se aaj tak — ${ITEMS.length} cheezein, purani se nayi.</p>
      ${hidden.length ? `<p class="muted" style="font-size:12px">🔒 Aapke role ko ye hisse nahi dikhte: ${hidden.join(", ")}</p>` : ""}
    </div>
    <div class="row" id="flt" style="gap:6px;flex-wrap:wrap;margin:8px 0">${FILTERS.map(([k, l]) =>
      `<button class="small ${k === FILTER ? "" : "ghost"}" data-f="${k}">${l}</button>`).join("")}
      <button class="small ghost" id="newest">⬇ Sabse naya</button></div>
    <div id="items"></div>`;
  $("flt").querySelectorAll("[data-f]").forEach(b => b.onclick = () => {
    FILTER = b.dataset.f;
    $("flt").querySelectorAll("[data-f]").forEach(x => x.classList.toggle("ghost", x !== b));
    draw();
  });
  $("newest").onclick = () => $("items").lastElementChild?.scrollIntoView({ behavior: "smooth" });
  draw();
}

function draw() {
  const list = FILTER === "all" ? ITEMS : ITEMS.filter(i => (GROUP[FILTER] || []).includes(i.k));
  let lastDay = "";
  $("items").innerHTML = list.length ? list.map(i => {
    const day = new Date(i.at).toLocaleDateString("en-IN", { weekday: "short", day: "2-digit", month: "short", year: "numeric" });
    const head = day !== lastDay ? `<div style="margin:12px 0 4px;font-weight:600;color:#0f766e">📅 ${day}</div>` : "";
    lastDay = day;
    const [ico, label] = KINDS[i.k];
    return head + `<div class="card" style="padding:8px 12px;margin:4px 0;${i.flag ? "border-color:#fca5a5;background:#fff7f7" : ""}">
      <div class="row" style="justify-content:space-between;gap:6px"><b>${ico} ${C.esc(i.title)}</b>
      <small class="muted">${new Date(i.at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}</small></div>
      ${i.body ? `<div style="white-space:pre-wrap;margin-top:2px">${C.esc(i.body)}</div>` : ""}
      <small class="muted">${C.esc(label)}${i.by ? " · " + C.esc(i.by) : ""}</small></div>`;
  }).join("") : `<div class="card"><p class="muted" style="margin:0">Is hisse mein abhi kuch nahi.</p></div>`;
}
