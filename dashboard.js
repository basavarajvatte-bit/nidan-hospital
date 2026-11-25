// Nidan Hospital OS — Phase 4: Doctor Command Center (dashboard)
let C, timer;
const $ = id => document.getElementById(id);
const rs = n => "₹" + Number(n || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 });
const mins = t => Math.max(0, Math.round((Date.now() - new Date(t)) / 60000));

export function render(ctx) {
  C = ctx;
  clearInterval(timer);
  C.app.innerHTML = `
    <button class="ghost small back" id="bk">← Wapas</button>
    <div class="row" style="justify-content:space-between">
      <h2 style="margin:0">📊 Aaj ka hospital</h2>
      <button class="ghost small" id="rf">↻ Refresh</button>
    </div>
    <p class="muted" id="asof" style="margin:4px 0 12px"></p>
    <div id="dash"><div class="card">Loading…</div></div>`;
  $("bk").onclick = () => { clearInterval(timer); C.goHome(); };
  $("rf").onclick = load;
  load();
  timer = setInterval(() => { if ($("dash")) load(); else clearInterval(timer); }, 60000);
}

async function load() {
  const [{ data: s, error }, { data: queue }, { data: alerts }] = await Promise.all([
    C.sb.rpc("dashboard_summary"),
    C.sb.from("encounters").select("id, kind, started_at, chief_complaint, patients(id, uhid, full_name, gender, age_years, allergies)")
      .in("kind", ["opd", "emergency"]).eq("status", "open").order("started_at"),
    C.sb.from("notifications").select("id, level, title, body, created_at").is("read_at", null)
      .in("level", ["critical", "warning"]).order("created_at", { ascending: false }).limit(5)
  ]);
  const dash = $("dash");
  if (!dash) return;
  if (error) { dash.innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  $("asof").textContent = "Last update: " + new Date(s.as_of).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }) + " (har 1 minute mein apne aap)";

  const tile = (label, value, opt = {}) => `
    <div class="kpi ${opt.alert ? "alert" : ""} ${opt.go ? "click" : ""}" ${opt.go ? `data-go="${opt.go}"` : ""}>
      <b>${value}</b><span>${label}</span></div>`;

  dash.innerHTML = `
    ${s.critical_alerts ? `<div class="card alertbox">🚨 <b>${s.critical_alerts} zaroori alert</b> — neeche dekho</div>` : ""}

    <h3>👥 Patient</h3>
    <div class="kpis">
      ${tile("Aaj ke patient", s.patients_today, { go: "reception" })}
      ${tile("Naye patient", s.new_patients, { go: "reception" })}
      ${tile("OPD aaj", s.opd_today, { go: "reception" })}
      ${tile("OPD mein wait", s.opd_waiting, { alert: s.opd_waiting > 10 })}
      ${tile("IPD admit", s.ipd_now, { go: "reception" })}
      ${tile("Khali bed", `${s.beds_free}<small>/${s.beds_total}</small>`, { alert: s.beds_total && s.beds_free === 0, go: "reception" })}
    </div>

    <h3>📅 Appointment</h3>
    <div class="kpis">
      ${tile("Aaj ke", s.appointments_today)}
      ${tile("Abhi aane baaki", s.appointments_pending)}
    </div>

    <h3>💰 Paisa (aaj)</h3>
    <div class="kpis">
      ${tile("Kamai", rs(s.revenue_today))}
      ${tile("Kharcha", rs(s.expenses_today))}
      ${tile("Logon se lena baaki", rs(s.outstanding), { alert: s.outstanding > 0 })}
    </div>

    <h3>⚠️ Dhyan dene wali baatein</h3>
    <div class="kpis">
      ${tile("Dawai kam stock", s.low_stock, { alert: s.low_stock > 0 })}
      ${tile("30 din mein expiry", s.expiring_soon, { alert: s.expiring_soon > 0 })}
      ${tile("Lab report baaki", s.lab_pending, { alert: s.lab_pending > 0 })}
      ${tile("Lab critical", s.lab_critical, { alert: s.lab_critical > 0 })}
      ${tile("Staff aaj present", `${s.staff_present}<small>/${s.staff_total}</small>`)}
      ${tile("AI kaam baaki", s.tasks_pending)}
      ${tile("Aapki approval chahiye", s.tasks_approval, { alert: s.tasks_approval > 0 })}
      ${tile("Zaroori alert", s.critical_alerts, { alert: s.critical_alerts > 0 })}
    </div>

    <div class="card" style="margin-top:14px"><h3>🩺 OPD line (wait kar rahe patient)</h3>
      ${queue?.length ? `<table>${queue.map((q, i) => `<tr>
        <td><b>${i + 1}</b></td>
        <td><a href="#" data-p="${q.patients.id}">${C.esc(q.patients.full_name)}</a>
          ${q.kind === "emergency" ? ` <span class="badge pending">Emergency</span>` : ""}<br>
          <small class="muted">${C.esc(q.patients.uhid)} · ${q.patients.age_years ?? "?"} saal · ${C.esc(q.patients.gender || "")}</small>
          ${q.patients.allergies ? `<br><small class="msg err">⚠️ ${C.esc(q.patients.allergies)}</small>` : ""}</td>
        <td>${C.esc(q.chief_complaint || "")}</td>
        <td><small class="${mins(q.started_at) > 30 ? "msg err" : "muted"}">${mins(q.started_at)} min</small></td>
      </tr>`).join("")}</table>` : `<p class="muted">Abhi koi patient wait nahi kar raha.</p>`}
    </div>

    <div class="card"><h3>🔔 Alerts</h3>
      ${alerts?.length ? alerts.map(a => `<div class="note ${a.level}">
        <b>${C.esc(a.title)}</b><br><small>${C.esc(a.body || "")}</small>
        <button class="small ghost" data-read="${a.id}">Dekh liya</button></div>`).join("")
        : `<p class="muted">Koi naya alert nahi.</p>`}
    </div>`;

  dash.querySelectorAll("[data-go]").forEach(t => t.onclick = () => openModule(t.dataset.go));
  dash.querySelectorAll("[data-p]").forEach(a => a.onclick = async e => {
    e.preventDefault(); clearInterval(timer);
    const mod = await import("./reception.js"); mod.openPatient(C, a.dataset.p);
  });
  dash.querySelectorAll("[data-read]").forEach(b => b.onclick = async () => {
    b.disabled = true;
    await C.sb.from("notifications").update({ read_at: new Date().toISOString() }).eq("id", b.dataset.read);
    load();
  });
}

async function openModule(id) {
  clearInterval(timer);
  if (id === "reception") (await import("./reception.js")).render(C);
}
