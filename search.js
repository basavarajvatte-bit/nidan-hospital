// Vatte Hospital OS — Home search: type a patient's or an employee's name and open their full history.
// Patients → full patient file (timeline.js). Employees → full staff history (doctor / admin / HR only).
let C;
const $ = id => document.getElementById(id);
const dt = t => t ? new Date(t).toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "—";
const clean = s => s.replace(/[%,()"\\*]/g, "").trim();
const ROLE = { doctor: "Doctor", admin: "Administrator", receptionist: "Receptionist", nurse: "Nursing Sister", accountant: "Accountant",
  pharmacist: "Pharmacist", lab: "Lab Staff", hr: "HR Manager", pending: "Pending" };
const canStaff = role => ["doctor", "admin", "hr"].includes(role);

// small search bar shown at the top of the home screen
export function mountSearch(ctx, el) {
  C = ctx;
  const staffOk = canStaff(C.me.role);
  el.innerHTML = `<div class="card" style="padding:10px 12px">
    <div class="row" style="gap:6px">
      <select id="sk" style="max-width:130px">
        <option value="patient">🧑‍🦱 Patient</option>
        ${staffOk ? `<option value="staff">👩‍⚕️ Employee</option>` : ""}
      </select>
      <input id="sq" placeholder="Naam / UHID / phone likho…" autocomplete="off" style="flex:1">
    </div>
    <div id="sres"></div></div>`;
  let t;
  const go = () => { clearTimeout(t); t = setTimeout(run, 300); };
  $("sq").oninput = go;
  $("sk").onchange = () => { $("sq").placeholder = $("sk").value === "patient" ? "Naam / UHID / phone likho…" : "Employee ka naam likho…"; run(); };
}

async function run() {
  const q = clean($("sq").value), kind = $("sk").value, box = $("sres");
  if (q.length < 2) { box.innerHTML = ""; return; }
  box.innerHTML = `<p class="muted" style="margin:6px 0">Dhoondh raha hoon…</p>`;
  const tag = r => r.exact ? "" : ` <span class="badge" style="font-size:11px">≈ milta-julta ${Math.round((r.score || 0) * 100)}%</span>`;
  const head = rows => rows.some(r => !r.exact)
    ? `<p class="muted" style="margin:6px 0 0;font-size:12px">${rows.some(r => r.exact) ? "Mile hue naam, aur neeche milte-julte naam:" : `"${C.esc(q)}" bilkul is naam se koi nahi, lekin ye milte-julte naam hain:`}</p>` : "";
  if (kind === "patient") {
    const { data, error } = await C.sb.rpc("search_patients", { q });
    if (error) { box.innerHTML = `<p class="msg err">${C.esc(error.message)}</p>`; return; }
    box.innerHTML = data.length ? head(data) + data.map(p => `<button class="ghost full" style="text-align:left;margin-top:6px" data-p="${p.id}">
        🧑‍🦱 <b>${C.esc(p.full_name)}</b>${tag(p)} <small class="muted">· ${C.esc(p.uhid)} · ${C.esc(p.gender || "")} ${p.age ?? ""} ${p.phone ? "· " + C.esc(p.phone) : ""}</small></button>`).join("")
      : `<p class="muted" style="margin:6px 0">"${C.esc(q)}" ya isse milta-julta koi patient hamare yahan nahi hai.</p>`;
    box.querySelectorAll("[data-p]").forEach(b => b.onclick = () =>
      import("./timeline.js?v=" + (window.APP_VERSION || "")).then(m => m.render(C, b.dataset.p, C.goHome)));
  } else {
    const { data, error } = await C.sb.rpc("search_staff", { q });
    if (error) { box.innerHTML = `<p class="msg err">${C.esc(error.message)}</p>`; return; }
    box.innerHTML = data.length ? head(data) + data.map(x => `<button class="ghost full" style="text-align:left;margin-top:6px" data-e="${x.profile_id ? "p:" + x.profile_id : "s:" + x.staff_id}">
        👩‍⚕️ <b>${C.esc(x.full_name || "(naam nahi)")}</b>${tag(x)} <small class="muted">· ${C.esc(ROLE[x.role] || x.designation || "Staff")}</small></button>`).join("")
      : `<p class="muted" style="margin:6px 0">"${C.esc(q)}" ya isse milta-julta koi employee nahi hai.</p>`;
    box.querySelectorAll("[data-e]").forEach(b => b.onclick = () => openEmployee(b.dataset.e));
  }
}

// ---------------------------------------------------------------- employee history
const TABLE = { patients: "Patient registration", encounters: "OPD / IPD visit", appointments: "Appointment", admissions: "Admit / discharge",
  beds: "Bed", vitals: "Vitals", nursing_notes: "Sister note", doctor_orders: "Doctor order", prescriptions: "Prescription",
  medication_administrations: "Dawa di", medical_documents: "Document", lab_orders: "Lab test", medicines: "Dawa list", medicine_batches: "Dawa stock",
  purchases: "Kharidari", invoices: "Bill", payments: "Payment", expenses: "Kharcha", salaries: "Salary", staff_members: "Staff record",
  attendance: "Attendance", follow_ups: "Follow-up" };
const OP = { insert: "naya banaya", update: "badla", delete: "hataya" };
function describe(a) {
  const [op, tbl] = String(a.action).split(":");
  if (tbl && TABLE[tbl]) return `${TABLE[tbl]} — ${OP[op] || op}${a.details?.changed?.length ? " (" + a.details.changed.filter(c => c !== "id").slice(0, 4).join(", ") + ")" : ""}`;
  if (a.action === "role_changed") return `Role badla: ${ROLE[a.details?.from] || a.details?.from} → ${ROLE[a.details?.to] || a.details?.to}`;
  if (a.action === "staff_signup") return "App par account banaya";
  return a.action;
}

async function openEmployee(key) {
  const [kind, id] = key.split(":");
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button><div id="emp"><div class="card">Loading…</div></div>`;
  $("bk").onclick = C.goHome;
  let prof = null, sm = null;
  if (kind === "p") {
    ({ data: prof } = await C.sb.from("profiles").select("id, full_name, role, created_at").eq("id", id).maybeSingle());
    ({ data: sm } = await C.sb.from("staff_members").select("*, departments(name)").eq("profile_id", id).maybeSingle());
  } else {
    ({ data: sm } = await C.sb.from("staff_members").select("*, departments(name)").eq("id", id).maybeSingle());
    if (sm?.profile_id) ({ data: prof } = await C.sb.from("profiles").select("id, full_name, role, created_at").eq("id", sm.profile_id).maybeSingle());
  }
  if (!prof && !sm) { $("emp").innerHTML = `<div class="card msg err">Employee nahi mila</div>`; return; }
  const uid = prof?.id, sid = sm?.id;
  const none = Promise.resolve({ data: [] });
  const [att, sal, aud, tasks, chats] = await Promise.all([
    sid ? C.sb.from("attendance").select("day, status, shift, check_in, check_out, overtime_hours").eq("staff_id", sid).order("day", { ascending: false }).limit(60) : none,
    sid ? C.sb.from("salaries").select("month, amount, method, paid_at, reverses_id").eq("staff_id", sid).order("month", { ascending: false }).limit(24) : none,
    uid ? C.sb.from("audit_logs").select("action, details, created_at").eq("actor_id", uid).order("created_at", { ascending: false }).limit(200) : none,
    uid ? C.sb.from("agent_tasks").select("action, status, summary, created_at").eq("requested_by", uid).is("parent_task_id", null).order("created_at", { ascending: false }).limit(30) : none,
    uid ? C.sb.from("ai_conversations").select("id, agent_id, title, updated_at").eq("user_id", uid).order("updated_at", { ascending: false }).limit(30) : none
  ]);
  const A = att.data || [], S = sal.data || [], L = aud.data || [], T = tasks.data || [], H = chats.data || [];
  const counts = {};
  L.forEach(a => { const t = String(a.action).split(":")[1]; if (TABLE[t]) counts[TABLE[t]] = (counts[TABLE[t]] || 0) + 1; });
  const present = A.filter(a => a.status === "present").length;
  const name = prof?.full_name || sm?.full_name || "(naam nahi)";
  const sec = (title, inner) => `<div class="card"><h3 style="margin:0 0 6px">${title}</h3>${inner}</div>`;
  const empty = "<p class='muted' style='margin:0'>Kuch nahi / aapko ye hissa nahi dikhta.</p>";
  $("emp").innerHTML = `
    <div class="card"><h2 style="margin:0">👩‍⚕️ ${C.esc(name)}</h2>
      <p class="muted" style="margin:4px 0">${prof ? C.esc(ROLE[prof.role] || prof.role) + " · app par " + dt(prof.created_at) + " se" : "App account nahi"}
      ${sm ? `<br>${C.esc(sm.designation || "")} ${sm.departments?.name ? "· " + C.esc(sm.departments.name) : ""} ${sm.phone ? "· 📞 " + C.esc(sm.phone) : ""}
      ${sm.joined_on ? "· Joined " + C.esc(sm.joined_on) : ""} ${sm.active === false ? "· ❌ Ab kaam par nahi" : ""}` : ""}</p></div>
    ${sec("📊 Kaam ka hisaab (aakhri 200 entries)", Object.keys(counts).length ? `<p style="margin:0">${Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${C.esc(k)}: <b>${v}</b>`).join(" · ")}</p>` : empty)}
    ${sec(`🗓️ Attendance (aakhri ${A.length} din${A.length ? ", haazir " + present : ""})`, A.length ? `<div style="overflow-x:auto"><table><tr><th>Din</th><th>Status</th><th>Shift</th><th>In / Out</th></tr>${A.map(a =>
      `<tr><td>${C.esc(a.day)}</td><td>${C.esc(a.status)}</td><td>${C.esc(a.shift || "")}</td><td>${a.check_in ? new Date(a.check_in).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }) : "—"} / ${a.check_out ? new Date(a.check_out).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }) : "—"}</td></tr>`).join("")}</table></div>` : empty)}
    ${sec("💰 Salary", S.length ? `<div style="overflow-x:auto"><table><tr><th>Mahina</th><th>Rakam</th><th>Kaise</th><th>Kab</th></tr>${S.map(s =>
      `<tr><td>${C.esc(String(s.month).slice(0, 7))}</td><td>${s.reverses_id ? "↩️ " : ""}₹${Number(s.amount).toLocaleString("en-IN")}</td><td>${C.esc(s.method || "")}</td><td>${dt(s.paid_at)}</td></tr>`).join("")}</table></div>` : empty)}
    ${sec("🤖 AI se karwaye kaam", T.length ? T.map(t => `<div style="margin:3px 0"><small class="muted">${dt(t.created_at)}</small> · ${C.esc(t.action)} — ${C.esc(t.summary || t.status)}</div>`).join("") : empty)}
    ${sec("💬 AI chats", H.length ? H.map(h => `<div style="margin:3px 0"><small class="muted">${dt(h.updated_at)}</small> · ${C.esc(h.agent_id)}: ${C.esc(h.title)}</div>`).join("") : empty)}
    ${sec("📜 App mein kya kya kiya (naya pehle)", L.length ? L.map(a => `<div style="margin:3px 0"><small class="muted">${dt(a.created_at)}</small> · ${C.esc(describe(a))}</div>`).join("") : empty)}`;
}
