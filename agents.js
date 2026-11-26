// Vatte Hospital OS — Phase 7: AI Agent Engine screen
// Staff ask an agent to do a job. Checks run at once; jobs that change records wait for approval.
let C, TAB = "agents", AGENTS = [], ACTIONS = [], CHAT = new Set();
const $ = id => document.getElementById(id);
const dt = t => t ? new Date(t).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }) : "—";
const RISK = { low: ["🟢", "Turant chalta hai"], controlled: ["🟡", "Doctor / Admin ki approval"], high: ["🔴", "Sirf Doctor ki approval"] };
const STATUS = { queued: "⏳ Line mein", running: "⚙️ Chal raha", waiting_approval: "✋ Approval baaki", approved: "👍 Approve",
  rejected: "🚫 Mana kiya", done: "✅ Ho gaya", failed: "❌ Fail" };
const KEYS = { patient: "Patient", uhid: "UHID", bed: "Bed", last: "Aakhri vitals", medicine: "Dawa", batch: "Batch", expiry: "Expiry",
  qty: "Qty", expired: "Expire ho gaya", stock: "Stock", reorder_level: "Reorder level", test: "Test", status: "Status", ordered: "Order",
  phone: "Phone", due_on: "Date", reason: "Kaaran", title: "Agent kaam", summary: "Nateeja", alert: "Dhyan", new_patients: "Naye patient",
  opd_open: "OPD khule", ipd_admitted: "IPD admit", bills: "Bill", amount: "Rakam", available: "Khali", occupied: "Bhara",
  cleaning: "Safai", blocked: "Band", expiring: "Expire hone wale batch", low_stock: "Kam stock wali dawa" };
const HIDE = new Set(["batch_id", "follow_up_id", "agent"]);
const isBoss = () => ["doctor", "admin"].includes(C.me.role);

export function render(ctx) {
  C = ctx; TAB = "agents";
  C.app.innerHTML = `
    <button class="ghost small back" id="bk">← Wapas</button>
    <h2 style="margin:0 0 4px">🤖 AI Agents</h2>
    <p class="muted" style="margin:0 0 10px">Har department ka ek madadgaar. Check turant chalte hain; record badalne wale kaam approval ke baad hi hote hain. Agent kabhi diagnosis ya dawa nahi deta.</p>
    <div class="row" id="tabs" style="gap:6px;margin-bottom:10px">
      <button class="small" data-t="agents">Agents</button>
      ${isBoss() ? `<button class="small ghost" data-t="approve">✋ Approval <span id="napp"></span></button>` : ""}
      <button class="small ghost" data-t="history">Itihaas</button>
    </div>
    <div id="body"><div class="card">Loading…</div></div>`;
  $("bk").onclick = C.goHome;
  C.app.querySelectorAll("#tabs [data-t]").forEach(b => b.onclick = () => {
    TAB = b.dataset.t;
    C.app.querySelectorAll("#tabs [data-t]").forEach(x => x.classList.toggle("ghost", x !== b));
    show();
  });
  boot();
}

async function boot() {
  const [{ data: a, error }, { data: ac }, { data: ch }] = await Promise.all([
    C.sb.from("agents").select("*").order("id"),
    C.sb.from("agent_actions").select("*").order("ord"),
    C.sb.from("ai_chat_agents").select("agent_id, roles")
  ]);
  CHAT = new Set((ch || []).filter(x => x.roles.includes(C.me.role)).map(x => x.agent_id));
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  AGENTS = a; ACTIONS = ac || [];
  show();
  countApprovals();
}

async function countApprovals() {
  if (!isBoss() || !$("napp")) return;
  const { count } = await C.sb.from("agent_tasks").select("id", { count: "exact", head: true }).eq("status", "waiting_approval");
  $("napp").textContent = count ? `(${count})` : "";
}

function show() {
  if (TAB === "agents") return showAgents();
  if (TAB === "approve") return showApprovals();
  return showHistory();
}

// ---------------------------------------------------------------- agents list
function showAgents() {
  const mine = ACTIONS.filter(x => x.requester_roles.includes(C.me.role));
  const ids = [...new Set(mine.map(x => x.agent_id))];
  const order = ["boss", ...AGENTS.map(a => a.id).filter(i => i !== "boss")];
  const list = order.filter(i => ids.includes(i)).map(i => AGENTS.find(a => a.id === i));
  const later = AGENTS.filter(a => !ACTIONS.some(x => x.agent_id === a.id));
  $("body").innerHTML = list.map(a => `
    <div class="card" id="ag_${a.id}">
      <div class="row" style="justify-content:space-between">
        <h3 style="margin:0">${a.icon || "🤖"} ${C.esc(a.name)}</h3>
        <span class="badge ${a.status === "paused" ? "pending" : ""}">${a.status === "paused" ? "⏸ Band" : "● Chalu"}</span>
      </div>
      <p class="muted" style="margin:4px 0">${C.esc(a.responsibilities)}</p>
      <p style="margin:4px 0"><small class="muted">Aakhri kaam: ${dt(a.last_run_at)}</small>${a.last_summary ? `<br><small>${C.esc(a.last_summary)}</small>` : ""}</p>
      <div class="row" style="gap:6px;flex-wrap:wrap">${mine.filter(x => x.agent_id === a.id).map(x => `
        <button class="small ${x.kind === "act" ? "ghost" : ""}" data-act="${x.id}" ${a.status === "paused" ? "disabled" : ""}
          title="${C.esc(x.description)}">${x.kind === "check" ? "▶" : RISK[x.risk][0]} ${C.esc(x.title)}</button>`).join("")}
        ${CHAT.has(a.id) ? `<button class="small ghost" data-chat="${a.id}">💬 Baat karo</button>` : ""}
        ${C.me.role === "doctor" && a.id !== "boss" ? `<button class="small ghost" data-pause="${a.id}" data-to="${a.status === "paused" ? "active" : "paused"}">
          ${a.status === "paused" ? "▶ Chalu karo" : "⏸ Band karo"}</button>` : ""}
      </div>
      <div id="out_${a.id}"></div>
    </div>`).join("") + (later.length ? `<div class="card"><p class="muted" style="margin:0">Aane wale agents: ${later.map(a => `${a.icon || ""} ${C.esc(a.name)}`).join(", ")} — inke kaam agle phases mein judenge.</p></div>` : "")
    + `<div class="card"><small class="muted">⏰ Apne aap: Boss AI report roz subah 8:30 aur raat 8:00 baje · Sister agent har ghante vitals check karta hai.<br>
       🟢 turant · 🟡 Doctor/Admin approval · 🔴 sirf Doctor approval</small></div>`;
  $("body").querySelectorAll("[data-act]").forEach(b => b.onclick = () => startAction(b.dataset.act));
  $("body").querySelectorAll("[data-chat]").forEach(b => b.onclick = () =>
    import("./chat.js?v=" + (window.APP_VERSION || "")).then(m => m.render(C, b.dataset.chat)));
  $("body").querySelectorAll("[data-pause]").forEach(b => b.onclick = async () => {
    b.disabled = true;
    const { error } = await C.sb.rpc("agent_set_status", { p_agent: b.dataset.pause, p_status: b.dataset.to });
    if (error) { b.disabled = false; return alertIn(b.dataset.pause, error.message); }
    boot();
  });
}

function alertIn(agentId, msg, ok = false) {
  const o = $("out_" + agentId);
  if (o) o.innerHTML = `<p class="msg ${ok ? "ok" : "err"}">${C.esc(msg)}</p>`;
}

async function startAction(id) {
  const x = ACTIONS.find(a => a.id === id);
  if (x.kind === "check") return submit(x, {});
  const o = $("out_" + x.agent_id);
  o.innerHTML = `<div class="card" style="background:#fffbeb;border-color:#fde68a;margin-top:8px">
    <b>${RISK[x.risk][0]} ${C.esc(x.title)}</b><br><small class="muted">${C.esc(x.description)} · ${RISK[x.risk][1]}</small>
    <div id="form_${x.agent_id}" style="margin-top:8px">Loading…</div></div>`;
  const f = $("form_" + x.agent_id);
  if (id === "followup.schedule") {
    f.innerHTML = `<label>Patient (naam / UHID / phone)</label><input id="fq" placeholder="Kam se kam 2 akshar">
      <div id="fres"></div>
      <label>Follow-up date</label><input id="fd" type="date" min="${new Date().toISOString().slice(0, 10)}">
      <label>Kaaran</label><input id="fr" placeholder="Jaise: BP check, tanke kholne">
      <button class="full" id="fgo" disabled>Approval ke liye bhejo</button>`;
    let pid = null;
    $("fq").oninput = async e => {
      const q = e.target.value.trim(); pid = null; $("fgo").disabled = true;
      if (q.length < 2) { $("fres").innerHTML = ""; return; }
      const s = q.replace(/[%,()"\\*]/g, "");
      const { data } = await C.sb.from("patients").select("id, uhid, full_name, phone")
        .or(`full_name.ilike."%${s}%",uhid.ilike."%${s}%",phone.ilike."%${s}%"`).limit(6);
      $("fres").innerHTML = (data || []).map(p => `<button class="small ghost" data-p="${p.id}">${C.esc(p.full_name)} · ${C.esc(p.uhid)}</button>`).join(" ") || "<small class='muted'>Koi nahi mila</small>";
      $("fres").querySelectorAll("[data-p]").forEach(b => b.onclick = () => {
        pid = b.dataset.p; $("fres").querySelectorAll("[data-p]").forEach(z => z.classList.toggle("ghost", z !== b)); check();
      });
    };
    const check = () => { $("fgo").disabled = !(pid && $("fd").value); };
    $("fd").onchange = check;
    $("fgo").onclick = () => submit(x, { patient_id: pid, due_on: $("fd").value, reason: $("fr").value.trim() });
  } else if (id === "operations.bed_status") {
    const { data } = await C.sb.from("beds").select("id, label, status, rooms(name)").neq("status", "occupied").order("label");
    f.innerHTML = (data || []).length ? `<label>Bed</label><select id="bb">${data.map(b =>
        `<option value="${b.id}">${C.esc(b.label)} — abhi: ${C.esc(KEYS[b.status] || b.status)}</option>`).join("")}</select>
      <label>Naya status</label><select id="bs"><option value="cleaning">Safai (cleaning)</option><option value="blocked">Band (blocked)</option><option value="available">Khali (available)</option></select>
      <button class="full" id="bgo">Approval ke liye bhejo</button>` : "<p class='muted'>Koi khali / safai wala bed nahi. (Bhare bed ka status agent nahi badalta.)</p>";
    if ($("bgo")) $("bgo").onclick = () => submit(x, { bed_id: $("bb").value, status: $("bs").value });
  } else if (id === "pharmacy.writeoff_expired") {
    const { data } = await C.sb.from("medicine_batches").select("id, batch_no, expiry_date, quantity, medicines(name)")
      .lt("expiry_date", new Date().toISOString().slice(0, 10)).gt("quantity", 0).order("expiry_date");
    f.innerHTML = (data || []).length ? `<label>Expire ho chuka batch</label><select id="wb">${data.map(b =>
        `<option value="${b.id}">${C.esc(b.medicines?.name)} · ${C.esc(b.batch_no)} · exp ${b.expiry_date} · ${b.quantity} pcs</option>`).join("")}</select>
      <button class="full" id="wgo">Doctor ki approval ke liye bhejo</button>` : "<p class='muted'>Koi expired batch stock mein nahi ✓</p>";
    if ($("wgo")) $("wgo").onclick = () => submit(x, { batch_id: $("wb").value });
  }
}

async function submit(x, input) {
  const o = $("out_" + x.agent_id);
  o.innerHTML = `<p class="muted">⚙️ ${C.esc(x.title)}…</p>`;
  const { data: t, error } = await C.sb.rpc("agent_submit", { p_action: x.id, p_input: input });
  if (error) return alertIn(x.agent_id, "❌ " + error.message);
  if (t.status === "waiting_approval") {
    alertIn(x.agent_id, x.risk === "high" ? "✋ Doctor ke paas approval ke liye bhej diya. Faisla hone par aapko notification milega."
                                          : "✋ Approval ke liye bhej diya. Faisla hone par aapko notification milega.", true);
    if (isBoss()) countApprovals();
    return;
  }
  o.innerHTML = resultCard(t);
  const a = AGENTS.find(z => z.id === x.agent_id);
  if (a && t.status === "done") { a.last_run_at = new Date().toISOString(); a.last_summary = t.summary; }
}

function resultCard(t) {
  const r = t.result || {};
  const bad = t.status === "failed";
  return `<div class="card" style="margin-top:8px;${bad || r.alert ? "border-color:#fca5a5;background:#fff7f7" : "border-color:#99f6e4;background:#f0fdfa"}">
    <b>${STATUS[t.status] || t.status}</b> — ${C.esc(t.summary || t.error || "")}
    ${r.items ? items(r.items) : ""}
    <br><small class="muted">${dt(t.updated_at || t.created_at)}</small></div>`;
}

function items(v) {
  if (Array.isArray(v)) {
    if (!v.length) return "";
    if (typeof v[0] !== "object") return `<p>${v.map(C.esc).join(", ")}</p>`;
    if (v.length === 1 && !v[0].patient && !v[0].medicine && !v[0].title) return kv(v[0]);
    const cols = [...new Set(v.flatMap(o => Object.keys(o)))].filter(k => !HIDE.has(k));
    return `<div style="overflow-x:auto"><table><tr>${cols.map(k => `<th>${C.esc(KEYS[k] || k)}</th>`).join("")}</tr>${v.map(o =>
      `<tr>${cols.map(k => `<td>${k === "status" ? (STATUS[o[k]] || cell(o[k])) : k === "phone" && tel(o[k]) ? `<a class="callbtn" href="tel:${tel(o[k])}">📞 ${C.esc(o[k])}</a>` : cell(o[k])}</td>`).join("")}</tr>`).join("")}</table></div>`;
  }
  if (v && typeof v === "object") return Object.entries(v).map(([k, x]) =>
    `<div style="margin-top:6px"><b>${C.esc(KEYS[k] || k.replace(/_/g, " "))}</b>${items(x) || " <small class='muted'>— kuch nahi</small>"}</div>`).join("");
  return "";
}
const kv = o => { const e = Object.entries(o).filter(([k]) => !HIDE.has(k)); return e.length ? `<p>${e.map(([k, x]) => `${C.esc(KEYS[k] || k)}: <b>${cell(x)}</b>`).join(" · ")}</p>` : ""; };
const cell = x => x === true ? "⚠️ Haan" : x === false ? "✓" : x == null ? "—" : C.esc(String(x));
const tel = ph => { const d = String(ph || "").replace(/\D/g, ""); return d.length === 10 ? "+91" + d : d ? "+" + d.replace(/^0+/, "") : ""; };

// ---------------------------------------------------------------- approvals (doctor / admin)
async function showApprovals() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const [{ data, error }, { data: staff }] = await Promise.all([
    C.sb.from("agent_tasks").select("*").eq("status", "waiting_approval").order("created_at"),
    C.sb.from("profiles").select("id, full_name")
  ]);
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const nm = id => C.esc(staff?.find(s => s.id === id)?.full_name || "Schedule");
  const names = await describeInputs(data);
  $("body").innerHTML = data.length ? data.map(t => {
    const x = ACTIONS.find(a => a.id === t.action) || {};
    const can = (x.approver_roles || []).includes(C.me.role);
    return `<div class="card" id="ap_${t.id}">
      <b>${RISK[t.risk]?.[0] || ""} ${C.esc(x.title || t.action)}</b> <small class="muted">· ${C.esc(AGENTS.find(a => a.id === t.agent_id)?.name || "")}</small>
      <p style="margin:4px 0">${names[t.id] || ""}</p>
      <small class="muted">Maanga: ${nm(t.requested_by)} · ${dt(t.created_at)} · ${RISK[t.risk]?.[1] || ""}</small>
      ${can ? `<div class="row" style="gap:6px;margin-top:8px">
        <button class="small" data-ok="${t.id}">✓ Approve</button>
        <input id="why_${t.id}" placeholder="Mana karne ka kaaran" style="flex:1;min-width:140px">
        <button class="small ghost" data-no="${t.id}">✗ Mana karo</button></div>` : `<p class="muted"><small>Ise sirf ${C.esc((x.approver_roles || []).join(" / "))} approve kar sakte hain.</small></p>`}
      <div id="apout_${t.id}"></div></div>`;
  }).join("") : `<div class="card"><p class="muted" style="margin:0">Koi kaam approval ke liye baaki nahi ✓</p></div>`;
  const decide = async (id, ok) => {
    const note = $("why_" + id)?.value.trim() || null;
    const out = $("apout_" + id);
    if (!ok && !note) { out.innerHTML = `<p class="msg err">Mana karne ka kaaran likhein</p>`; return; }
    $("ap_" + id).querySelectorAll("button").forEach(b => b.disabled = true);
    const { data: t, error } = await C.sb.rpc("agent_decide", { p_task: id, p_approve: ok, p_note: note });
    if (error) { out.innerHTML = `<p class="msg err">❌ ${C.esc(error.message)}</p>`; $("ap_" + id).querySelectorAll("button").forEach(b => b.disabled = false); return; }
    out.innerHTML = resultCard(t);
    countApprovals();
  };
  $("body").querySelectorAll("[data-ok]").forEach(b => b.onclick = () => decide(b.dataset.ok, true));
  $("body").querySelectorAll("[data-no]").forEach(b => b.onclick = () => decide(b.dataset.no, false));
}

// human-readable description of what an act task will change
async function describeInputs(tasks) {
  const out = {};
  const pids = tasks.map(t => t.input?.patient_id).filter(Boolean);
  const bids = tasks.map(t => t.input?.bed_id).filter(Boolean);
  const mids = tasks.map(t => t.input?.batch_id).filter(Boolean);
  const [p, b, m] = await Promise.all([
    pids.length ? C.sb.from("patients").select("id, full_name, uhid").in("id", pids) : { data: [] },
    bids.length ? C.sb.from("beds").select("id, label, status").in("id", bids) : { data: [] },
    mids.length ? C.sb.from("medicine_batches").select("id, batch_no, expiry_date, quantity, medicines(name)").in("id", mids) : { data: [] }
  ]);
  for (const t of tasks) {
    const i = t.input || {};
    if (t.action === "followup.schedule") {
      const x = p.data?.find(z => z.id === i.patient_id);
      out[t.id] = `👤 ${C.esc(x?.full_name || "?")} (${C.esc(x?.uhid || "")}) → follow-up <b>${C.esc(i.due_on)}</b>${i.reason ? " · " + C.esc(i.reason) : ""}`;
    } else if (t.action === "operations.bed_status") {
      const x = b.data?.find(z => z.id === i.bed_id);
      out[t.id] = `🛏️ Bed <b>${C.esc(x?.label || "?")}</b>: ${C.esc(KEYS[x?.status] || x?.status || "?")} → <b>${C.esc(KEYS[i.status] || i.status)}</b>`;
    } else if (t.action === "pharmacy.writeoff_expired") {
      const x = m.data?.find(z => z.id === i.batch_id);
      out[t.id] = `💊 <b>${C.esc(x?.medicines?.name || "?")}</b> batch ${C.esc(x?.batch_no || "?")} (exp ${C.esc(x?.expiry_date || "?")}) · ${x?.quantity ?? "?"} pcs → <b>0</b>`;
    }
  }
  return out;
}

// ---------------------------------------------------------------- history + logs
async function showHistory() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const [{ data, error }, { data: staff }] = await Promise.all([
    C.sb.from("agent_tasks").select("id, agent_id, action, status, risk, summary, error, requested_by, approved_by, decision_note, created_at, updated_at, result")
      .is("parent_task_id", null).order("created_at", { ascending: false }).limit(40),
    C.sb.from("profiles").select("id, full_name")
  ]);
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const nm = id => id ? C.esc(staff?.find(s => s.id === id)?.full_name || "staff") : "⏰ Schedule";
  $("body").innerHTML = `<div class="card"><p class="muted" style="margin-top:0">${isBoss() ? "Sab agents ke aakhri 40 kaam." : "Aapke maange hue kaam."} Kisi par click karo to poori jaankari aur log.</p>
    ${data.length ? `<div style="overflow-x:auto"><table><tr><th>Samay</th><th>Kaam</th><th>Status</th><th>Kisne</th></tr>${data.map(t => {
      const x = ACTIONS.find(a => a.id === t.action) || {};
      const a = AGENTS.find(z => z.id === t.agent_id) || {};
      return `<tr class="click" data-h="${t.id}"><td>${dt(t.created_at)}</td><td>${a.icon || ""} ${C.esc(x.title || t.action)}<br><small class="muted">${C.esc(t.summary || t.error || t.decision_note || "")}</small></td>
        <td>${STATUS[t.status] || t.status}</td><td>${nm(t.requested_by)}</td></tr>
        <tr id="hx_${t.id}" style="display:none"><td colspan="4"></td></tr>`;
    }).join("")}</table></div>` : "<p class='muted'>Abhi kuch nahi.</p>"}</div>`;
  $("body").querySelectorAll("[data-h]").forEach(r => r.onclick = async () => {
    const row = $("hx_" + r.dataset.h);
    if (row.style.display !== "none") { row.style.display = "none"; return; }
    row.style.display = "";
    const t = data.find(z => z.id === r.dataset.h);
    const { data: logs } = await C.sb.from("agent_logs").select("level, message, created_at").eq("task_id", t.id).order("id");
    row.firstElementChild.innerHTML = resultCard(t) + `<small class="muted">${(logs || []).map(l =>
      `${l.level === "error" ? "❌" : l.level === "warning" ? "⚠️" : "•"} ${new Date(l.created_at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })} ${C.esc(l.message)}`).join("<br>")}</small>`;
  });
}
