// Vatte Hospital OS — Phase 9: Appointments + OPD token line
let C, TAB = "line", DAY = null, timer = null, PICK = null, MOVE = null;
const $ = id => document.getElementById(id);
const ist = () => new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Kolkata" }));
const ymd = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const hm = t => new Date(t).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", timeZone: "Asia/Kolkata" });
const tel = ph => { const d = String(ph || "").replace(/\D/g, ""); return d.length === 10 ? "+91" + d : d ? "+" + d : ""; };
const callBtn = ph => tel(ph) ? `<a class="callbtn" href="tel:${tel(ph)}" onclick="event.stopPropagation()">📞</a>` : "";
const PRI = { emergency: ["🚨", "Emergency", "#fee2e2"], senior: ["👴", "65+", "#fef3c7"], normal: ["", "", "#fff"] };
const QS = { waiting: "⏳ Intezaar", called: "📢 Bulaya", in_consult: "🩺 Doctor ke paas", done: "✅ Ho gaya", no_show: "🚫 Nahi aaya", left: "🚪 Chala gaya" };
const AS = { booked: "📅 Aane wala", checked_in: "✅ Aa gaya", completed: "✔️ Ho gaya", cancelled: "✖️ Cancel", missed: "🚫 Nahi aaya" };
const canBook = () => ["doctor", "admin", "receptionist"].includes(C.me.role);

export function render(ctx) {
  C = ctx; TAB = "line"; DAY = ymd(ist()); PICK = null; MOVE = null;
  clearInterval(timer);
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button>
    <h2 style="margin:0 0 6px">📅 Appointments & OPD line</h2>
    <div class="row" id="tabs" style="gap:6px;margin-bottom:10px;flex-wrap:wrap">
      <button class="small" data-t="line">🎫 OPD line</button>
      ${canBook() ? `<button class="small ghost" data-t="appt">📅 Appointments</button>` : ""}
      ${["doctor", "admin"].includes(C.me.role) ? `<button class="small ghost" data-t="set">⚙️ OPD time</button>` : ""}
      <button class="small ghost" id="tv">📺 Token screen</button>
    </div>
    <div id="body"><div class="card">Loading…</div></div>`;
  $("bk").onclick = () => { clearInterval(timer); C.goHome(); };
  $("tv").onclick = tokenScreen;
  C.app.querySelectorAll("#tabs [data-t]").forEach(b => b.onclick = () => {
    TAB = b.dataset.t; C.app.querySelectorAll("#tabs [data-t]").forEach(x => x.classList.toggle("ghost", x !== b)); show();
  });
  show();
}

function show() {
  clearInterval(timer);
  if (TAB === "line") { line(); timer = setInterval(() => { if ($("qlist")) line(true); else clearInterval(timer); }, 15000); }
  else if (TAB === "appt") appts();
  else settings();
}

const err = (el, e) => { el.innerHTML = `<p class="msg err">❌ ${C.esc(e.message || e)}</p>`; };

// ---------------------------------------------------------------- OPD token line
async function line(quiet = false, note = "") {
  const today = ymd(ist());
  const { data, error } = await C.sb.from("opd_queue").select("id, token_no, status, priority, created_at, called_at, started_at, done_at, patients(id, full_name, uhid, phone, age_years, gender), appointment_id")
    .eq("day", today).order("token_no");
  if (!$("body")) return;
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const active = data.filter(q => ["waiting", "called", "in_consult"].includes(q.status))
    .sort((a, b) => (a.status === "in_consult" ? -2 : a.status === "called" ? -1 : 0) - (b.status === "in_consult" ? -2 : b.status === "called" ? -1 : 0)
      || ({ emergency: 0, senior: 1, normal: 2 }[a.priority] - { emergency: 0, senior: 1, normal: 2 }[b.priority]) || a.token_no - b.token_no);
  const done = data.filter(q => !["waiting", "called", "in_consult"].includes(q.status));
  const waiting = active.filter(q => q.status === "waiting").length;
  const mins = t => Math.max(0, Math.round((Date.now() - new Date(t)) / 60000));
  const started = data.filter(q => q.started_at);
  const avg = started.length ? Math.round(started.reduce((s, q) => s + (new Date(q.started_at) - new Date(q.created_at)), 0) / started.length / 60000) : null;
  $("body").innerHTML = `
    <div class="card" style="display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap">
      <div><b style="font-size:22px">${waiting}</b> intezaar mein · ${done.filter(q => q.status === "done").length} ho gaye${avg != null ? ` · avg intezaar ${avg} min` : ""}
        <br><small class="muted">Naya token: Reception mein patient ka OPD shuru karte hi apne aap milta hai. Har 15 sec mein apne aap refresh.</small></div>
      <button id="next" ${waiting ? "" : "disabled"}>📢 Agla patient bulao</button>
    </div>
    <p class="msg ${note ? "ok" : ""}" id="qmsg">${C.esc(note)}</p>
    <div id="qlist">${active.length ? active.map(q => {
      const p = q.patients || {}; const [pi, pl, bg] = PRI[q.priority];
      return `<div class="card" style="padding:10px 12px;margin:6px 0;background:${q.status === "in_consult" ? "#ecfdf5" : q.status === "called" ? "#eff6ff" : bg}">
        <div class="row" style="gap:10px;align-items:center">
          <div style="font-size:26px;font-weight:800;min-width:54px;text-align:center;color:#0f766e">#${q.token_no}</div>
          <div style="flex:1">
            <a href="#" data-pt="${p.id}" style="font-weight:700">${C.esc(p.full_name || "")}</a> ${pi ? `<span class="badge">${pi} ${pl}</span>` : ""} ${q.appointment_id ? `<span class="badge">📅 Appt</span>` : ""}
            <br><small class="muted">${C.esc(p.uhid || "")} · ${p.age_years ?? "?"} saal · ${QS[q.status]} · ${mins(q.created_at)} min se</small></div>
          ${callBtn(p.phone)}
        </div>
        <div class="row" style="gap:6px;margin-top:8px;flex-wrap:wrap">
          ${q.status === "waiting" ? `<button class="small" data-q="${q.id}" data-s="called">📢 Bulao</button>` : ""}
          ${q.status !== "in_consult" ? `<button class="small ghost" data-q="${q.id}" data-s="in_consult">🩺 Andar bhejo</button>` : ""}
          <button class="small ghost" data-q="${q.id}" data-s="done">✅ Ho gaya</button>
          <button class="small ghost" data-q="${q.id}" data-s="no_show">🚫 Nahi aaya</button>
        </div></div>`;
    }).join("") : `<div class="card"><p class="muted" style="margin:0">Abhi line mein koi patient nahi ✓</p></div>`}</div>
    ${done.length ? `<details class="card"><summary>Aaj ke poore hue tokens (${done.length})</summary>${done.map(q =>
      `<div style="margin:4px 0">#${q.token_no} · ${C.esc(q.patients?.full_name || "")} · ${QS[q.status]} ${q.done_at ? "· " + hm(q.done_at) : ""}</div>`).join("")}</details>` : ""}`;
  $("next").onclick = async () => {
    $("next").disabled = true;
    const { data: q, error } = await C.sb.rpc("queue_call_next");
    if (error) { err($("qmsg"), error); $("next").disabled = false; return; }
    const p = data.find(x => x.id === q.id)?.patients;
    line(true, `📢 Token #${q.token_no}${p ? " — " + p.full_name : ""} ko bulaya`);
  };
  $("qlist").querySelectorAll("[data-q]").forEach(b => b.onclick = async () => {
    b.disabled = true;
    const { error } = await C.sb.rpc("queue_set", { p_id: b.dataset.q, p_status: b.dataset.s });
    if (error) { err($("qmsg"), error); b.disabled = false; return; }
    line(true);
  });
  wirePatients($("qlist"));
}

function wirePatients(el) {
  el.querySelectorAll("[data-pt]").forEach(a => a.onclick = e => {
    e.preventDefault(); clearInterval(timer);
    import("./timeline.js?v=" + (window.APP_VERSION || "")).then(m => m.render(C, a.dataset.pt, () => render(C)));
  });
}

// big token display for a TV / second screen
async function tokenScreen() {
  clearInterval(timer);
  const draw = async () => {
    const { data } = await C.sb.from("opd_queue").select("token_no, status, priority, patients(full_name)").eq("day", ymd(ist()))
      .in("status", ["waiting", "called", "in_consult"]).order("token_no");
    if (!$("tvbox")) return clearInterval(timer);
    const now = (data || []).filter(q => q.status === "in_consult" || q.status === "called");
    const nextQ = (data || []).filter(q => q.status === "waiting")
      .sort((a, b) => ({ emergency: 0, senior: 1, normal: 2 }[a.priority] - { emergency: 0, senior: 1, normal: 2 }[b.priority]) || a.token_no - b.token_no).slice(0, 6);
    $("tvbox").innerHTML = `
      <div style="font-size:22px;opacity:.8">Ab andar / bulaya gaya</div>
      <div style="font-size:96px;font-weight:900;line-height:1.1">${now.length ? now.map(q => "#" + q.token_no).join("  ") : "—"}</div>
      <div style="font-size:22px;margin-top:24px;opacity:.8">Agle tokens</div>
      <div style="font-size:48px;font-weight:700">${nextQ.length ? nextQ.map(q => "#" + q.token_no).join("  ") : "—"}</div>
      <div style="margin-top:30px;font-size:16px;opacity:.7">${new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })} · har 10 sec mein badalta hai</div>`;
  };
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button>
    <div id="tvbox" style="background:#0f766e;color:#fff;border-radius:16px;padding:30px 16px;text-align:center;min-height:70vh">Loading…</div>`;
  $("bk").onclick = () => { clearInterval(timer); render(C); };
  await draw();
  timer = setInterval(draw, 10000);
  try { document.documentElement.requestFullscreen?.(); } catch { /* not allowed — fine */ }
}

// ---------------------------------------------------------------- appointments by day + free slots + booking
async function appts(note = "") {
  const { data: list, error } = await C.sb.from("appointments").select("id, starts_at, status, reason, patients(id, full_name, uhid, phone)")
    .gte("starts_at", new Date(DAY + "T00:00:00+05:30").toISOString()).lt("starts_at", new Date(DAY + "T23:59:59+05:30").toISOString()).order("starts_at");
  const { data: slots, error: e2 } = await C.sb.rpc("opd_free_slots", { p_day: DAY });
  if (!$("body")) return;
  if (error || e2) { $("body").innerHTML = `<div class="card msg err">${C.esc((error || e2).message)}</div>`; return; }
  const shown = list.filter(a => a.status !== "cancelled");
  const free = (slots || []).filter(s => s.free);
  const d = new Date(DAY + "T00:00:00+05:30");
  $("body").innerHTML = `
    <div class="card row" style="gap:8px;align-items:center;flex-wrap:wrap">
      <button class="small ghost" id="prev">◀</button>
      <input type="date" id="day" value="${DAY}" style="max-width:170px">
      <button class="small ghost" id="nxt">▶</button>
      <b>${d.toLocaleDateString("en-IN", { weekday: "long", day: "2-digit", month: "short" })}</b>
    </div>
    ${note ? `<div class="card msg ok">${C.esc(note)}</div>` : ""}
    <p class="msg" id="amsg"></p>
    <div class="card"><h3 style="margin:0 0 6px">Is din ki appointments (${shown.length})</h3>
      ${shown.length ? shown.map(a => `<div class="row" style="gap:8px;align-items:center;padding:6px 0;border-bottom:1px solid #eef2f2">
        <b style="min-width:70px">${hm(a.starts_at)}</b>
        <div style="flex:1"><a href="#" data-pt="${a.patients?.id}">${C.esc(a.patients?.full_name || "")}</a>
          <br><small class="muted">${C.esc(a.patients?.uhid || "")} · ${AS[a.status]}${a.reason ? " · " + C.esc(a.reason) : ""}</small></div>
        ${callBtn(a.patients?.phone)}
        ${a.status === "booked" ? `<button class="small ghost" data-mv="${a.id}">🔁 Badlo</button><button class="small ghost" data-cx="${a.id}">✖️</button>` : ""}
      </div>`).join("") : `<p class="muted" style="margin:0">Koi appointment nahi.</p>`}
    </div>
    <div class="card"><h3 style="margin:0 0 6px">${MOVE ? "🔁 Naya samay chuno" : "Khali slot"} (${free.length})</h3>
      ${MOVE ? `<p class="muted" style="margin:0 0 6px">Jis appointment ko badalna hai uska naya slot dabao. <a href="#" id="mvx">Rehne do</a></p>` : `<p class="muted" style="margin:0 0 6px">Slot dabao → patient chuno → appointment lag jayegi.</p>`}
      ${(slots || []).length ? `<div class="row" style="gap:6px;flex-wrap:wrap">${slots.map(s =>
        `<button class="small ${s.free ? "" : "ghost"}" ${s.free ? `data-sl="${s.slot_start}"` : "disabled"} style="${s.free ? "" : "opacity:.45;text-decoration:line-through"}">${C.esc(s.label)}</button>`).join("")}</div>`
        : `<p class="muted" style="margin:0">Is din OPD band hai.</p>`}
      <div id="bookbox"></div>
    </div>`;
  const go = dd => { DAY = dd; PICK = null; appts(); };
  $("day").onchange = e => e.target.value && go(e.target.value);
  $("prev").onclick = () => { const x = new Date(DAY + "T12:00:00+05:30"); x.setDate(x.getDate() - 1); go(ymd(x)); };
  $("nxt").onclick = () => { const x = new Date(DAY + "T12:00:00+05:30"); x.setDate(x.getDate() + 1); go(ymd(x)); };
  if ($("mvx")) $("mvx").onclick = e => { e.preventDefault(); MOVE = null; appts(); };
  wirePatients($("body"));
  $("body").querySelectorAll("[data-mv]").forEach(b => b.onclick = () => { MOVE = b.dataset.mv; appts(); });
  $("body").querySelectorAll("[data-cx]").forEach(b => b.onclick = () => {
    const box = document.createElement("div");
    box.className = "row"; box.style.cssText = "gap:6px;margin:6px 0";
    box.innerHTML = `<input placeholder="Cancel ka kaaran" style="flex:1"><button class="small">Cancel karo</button>`;
    b.closest(".row").after(box);
    box.querySelector("button").onclick = async () => {
      const { error } = await C.sb.rpc("cancel_appointment", { p_id: b.dataset.cx, p_reason: box.querySelector("input").value });
      if (error) return err($("amsg"), error);
      appts("Appointment cancel ho gayi");
    };
  });
  $("body").querySelectorAll("[data-sl]").forEach(b => b.onclick = async () => {
    if (MOVE) {
      const { error } = await C.sb.rpc("reschedule_appointment", { p_id: MOVE, p_start: b.dataset.sl });
      if (error) return err($("amsg"), error);
      MOVE = null; return appts("Appointment ka samay badal diya ✓");
    }
    PICK = b.dataset.sl;
    $("body").querySelectorAll("[data-sl]").forEach(x => x.classList.toggle("ghost", x !== b));
    bookForm();
  });
}

function bookForm() {
  const box = $("bookbox");
  box.innerHTML = `<div class="card" style="background:#f0fdfa;margin-top:10px">
    <b>📅 ${hm(PICK)} ki appointment</b>
    <label>Patient (naam / UHID / phone — galat spelling bhi chalegi)</label><input id="bq" autocomplete="off" placeholder="Kam se kam 2 akshar">
    <div id="bres"></div>
    <label>Kaaran (optional)</label><input id="br" placeholder="Jaise: BP check, report dikhana">
    <button class="full" id="bgo" disabled>Appointment lagao</button>
    <small class="muted">Naya patient hai? Pehle Reception mein registration karein.</small></div>`;
  let pid = null, t;
  $("bq").oninput = () => { clearTimeout(t); t = setTimeout(async () => {
    const q = $("bq").value.replace(/[%,()"\\*]/g, "").trim(); pid = null; $("bgo").disabled = true;
    if (q.length < 2) { $("bres").innerHTML = ""; return; }
    const { data } = await C.sb.rpc("search_patients", { q });
    $("bres").innerHTML = (data || []).slice(0, 6).map(p => `<button class="small ghost" style="margin:3px" data-bp="${p.id}">${C.esc(p.full_name)} · ${C.esc(p.uhid)}${p.exact ? "" : " ≈"}</button>`).join("")
      || "<small class='muted'>Koi nahi mila</small>";
    $("bres").querySelectorAll("[data-bp]").forEach(b => b.onclick = () => {
      pid = b.dataset.bp; $("bres").querySelectorAll("[data-bp]").forEach(x => x.classList.toggle("ghost", x !== b)); $("bgo").disabled = false;
    });
  }, 300); };
  $("bgo").onclick = async () => {
    $("bgo").disabled = true;
    const { data: a, error } = await C.sb.rpc("book_appointment", { p_patient: pid, p_start: PICK, p_reason: $("br").value.trim() || null });
    if (error) { err($("amsg"), error); $("bgo").disabled = false; return; }
    PICK = null; appts(`✓ Appointment lag gayi — ${hm(a.starts_at)}`);
  };
}

// ---------------------------------------------------------------- OPD timings (doctor / admin)
async function settings(note = "") {
  const { data: s, error } = await C.sb.from("opd_settings").select("*").maybeSingle();
  if (!$("body")) return;
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const v = s || { morning_start: "10:00", morning_end: "14:00", evening_start: "17:00", evening_end: "20:00", slot_minutes: 10, weekly_off: [0] };
  const t = x => (x || "").slice(0, 5);
  const days = ["Ravi", "Som", "Mangal", "Budh", "Guru", "Shukra", "Shani"];
  $("body").innerHTML = `<div class="card">
    ${note ? `<p class="msg ok">${C.esc(note)}</p>` : ""}
    <h3 style="margin-top:0">⚙️ OPD ka samay</h3>
    <div class="row" style="gap:8px"><div style="flex:1"><label>Subah shuru</label><input type="time" id="ms" value="${t(v.morning_start)}"></div>
      <div style="flex:1"><label>Subah band</label><input type="time" id="me" value="${t(v.morning_end)}"></div></div>
    <div class="row" style="gap:8px"><div style="flex:1"><label>Shaam shuru (khaali = shaam OPD nahi)</label><input type="time" id="es" value="${t(v.evening_start)}"></div>
      <div style="flex:1"><label>Shaam band</label><input type="time" id="ee" value="${t(v.evening_end)}"></div></div>
    <label>Ek patient ka slot (minute)</label><input type="number" id="sm" min="5" max="60" value="${v.slot_minutes}">
    <label>Chhutti ka din</label><div class="row" style="gap:6px;flex-wrap:wrap">${days.map((d, i) =>
      `<label style="display:flex;gap:4px;align-items:center"><input type="checkbox" data-off="${i}" ${v.weekly_off.includes(i) ? "checked" : ""}> ${d}</label>`).join("")}</div>
    <p class="msg" id="smsg"></p>
    <button class="full" id="ssave">Save karo</button></div>`;
  $("ssave").onclick = async () => {
    const row = { morning_start: $("ms").value, morning_end: $("me").value, evening_start: $("es").value || null, evening_end: $("es").value ? $("ee").value : null,
      slot_minutes: Number($("sm").value), weekly_off: [...document.querySelectorAll("[data-off]:checked")].map(x => Number(x.dataset.off)), updated_at: new Date().toISOString() };
    const { error } = s ? await C.sb.from("opd_settings").update(row).eq("hospital_id", s.hospital_id) : await C.sb.from("opd_settings").insert(row);
    if (error) return err($("smsg"), error);
    settings("✓ OPD ka samay save ho gaya");
  };
}
