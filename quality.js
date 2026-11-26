// Vatte Hospital OS — Phase 14: Quality (daily checklists, incident reporting & review, monthly quality numbers)
let C, TAB;
const $ = id => document.getElementById(id);
const ist = () => new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Kolkata" }));
const ymd = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const dt = t => t ? new Date(t).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }) : "";
const clean = s => String(s || "").replace(/[%,()"\\*]/g, "").trim();
const err = (el, e) => { if (el) { el.className = "msg err"; el.textContent = "❌ " + (e.message || e); } };
const ok = (el, t) => { if (el) { el.className = "msg ok"; el.textContent = t; } };
const can = r => r.includes(C.me.role);
const KIND = { fall: "🧍 Gir gaya (fall)", medication_error: "💊 Dawa mein galti", needle_stick: "💉 Sui chubh gayi (staff)", near_miss: "⚠️ Bach gaye (near miss)",
  equipment: "🔧 Machine ki galti", infection: "🦠 Infection", complaint: "🗣️ Patient ki shikayat", violence: "✋ Maar-peet / dhamki", other: "📎 Other" };
const SEV = { no_harm: "Koi nuksaan nahi", minor: "Thoda", moderate: "Madhyam", severe: "Gambhir", death: "Maut" };
const SHIFT = { morning: "Subah", evening: "Shaam", night: "Raat" };

export function render(ctx) {
  C = ctx;
  const tabs = [["check", "✅ Aaj ki checklist"], ["inc", "⚠️ Ghatna batao"], can(["doctor", "admin"]) && ["review", "🔍 Ghatna review"], can(["doctor", "admin"]) && ["nums", "📈 Quality numbers"]].filter(Boolean);
  TAB = tabs[0][0];
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button><h2 style="margin:0 0 6px">✅ Quality & Safety</h2>
    <div class="row" id="tabs" style="gap:6px;margin-bottom:10px">${tabs.map(([k, l]) => `<button class="small ${k === TAB ? "" : "ghost"}" data-t="${k}">${l}</button>`).join("")}</div>
    <div id="body"><div class="card">Loading…</div></div>`;
  $("bk").onclick = C.goHome;
  C.app.querySelectorAll("#tabs [data-t]").forEach(b => b.onclick = () => {
    TAB = b.dataset.t; C.app.querySelectorAll("#tabs [data-t]").forEach(x => x.classList.toggle("ghost", x !== b)); show();
  });
  show();
}
function show() { ({ check, inc, review, nums })[TAB](); }

// ---------------------------------------------------------------- checklists
async function check() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const [{ data: T }, { data: done }] = await Promise.all([
    C.sb.from("quality_templates").select("*").order("ord"),
    C.sb.from("quality_checks").select("template_id, shift, failed, checked_by, created_at").eq("day", ymd(ist()))]);
  const mine = (T || []).filter(t => t.roles.includes(C.me.role));
  if (!mine.length) { $("body").innerHTML = `<div class="card"><p class="muted">Aapke role ke liye koi checklist nahi.</p></div>`; return; }
  $("body").innerHTML = mine.map(t => {
    const d = (done || []).filter(x => x.template_id === t.id);
    const left = t.per_shift ? Object.keys(SHIFT).filter(s => !d.some(x => x.shift === s)) : (d.length ? [] : ["day"]);
    return `<div class="card"><div class="row" style="justify-content:space-between"><b>${C.esc(t.name)}</b>
      <span>${left.length ? `🟡 ${t.per_shift ? left.map(s => SHIFT[s]).join(", ") + " baaki" : "Baaki"}` : "🟢 Ho gayi"}</span></div>
      ${d.map(x => `<small class="muted">${x.shift !== "day" ? SHIFT[x.shift] + ": " : ""}${x.failed ? `⚠️ ${x.failed} kami` : "sab theek ✓"} · ${dt(x.created_at)}</small><br>`).join("")}
      ${left.length ? `<button class="small" data-t="${t.id}" style="margin-top:6px">✍️ Bharo</button>` : ""}<div id="f_${t.id}"></div></div>`;
  }).join("");
  $("body").querySelectorAll("[data-t]").forEach(b => b.onclick = () => {
    const t = mine.find(x => x.id === b.dataset.t), d = (done || []).filter(x => x.template_id === t.id);
    const left = Object.keys(SHIFT).filter(s => !d.some(x => x.shift === s));
    const h = ist().getHours(), guess = h < 14 ? "morning" : h < 20 ? "evening" : "night";
    b.remove();
    $("f_" + t.id).innerHTML = `${t.per_shift ? `<label>Shift</label><select id="sh_${t.id}">${left.map(s => `<option value="${s}" ${s === guess ? "selected" : ""}>${SHIFT[s]}</option>`).join("")}</select>` : ""}
      ${t.items.map((it, i) => `<div class="row" style="justify-content:space-between;border-top:1px solid var(--line);padding:6px 0;gap:6px">
        <span style="flex:1">${C.esc(it)}</span><span class="row" style="gap:4px">
        <label class="row" style="gap:2px"><input type="radio" name="${t.id}_${i}" value="1" style="width:auto">✅</label>
        <label class="row" style="gap:2px"><input type="radio" name="${t.id}_${i}" value="0" style="width:auto">❌</label></span></div>`).join("")}
      <label>Kami ho to kya kiya / kya karna hai</label><input id="rm_${t.id}">
      <button class="full" id="sv_${t.id}">💾 Save</button><p class="msg" id="m_${t.id}"></p>`;
    $("sv_" + t.id).onclick = async () => {
      const ans = {};
      for (let i = 0; i < t.items.length; i++) {
        const r = C.app.querySelector(`[name="${t.id}_${i}"]:checked`);
        if (!r) return err($("m_" + t.id), "Har line par ✅ ya ❌ chunein");
        ans[t.items[i]] = r.value === "1";
      }
      const { error } = await C.sb.rpc("q_save_check", { p_template: t.id, p_shift: $("sh_" + t.id)?.value || null, p_answers: ans, p_remarks: $("rm_" + t.id).value });
      if (error) return err($("m_" + t.id), error);
      check();
    };
  });
}

// ---------------------------------------------------------------- report incident
function inc() {
  const now = new Date(Date.now() - new Date().getTimezoneOffset() * 6e4).toISOString().slice(0, 16);
  let pid = null;
  $("body").innerHTML = `<div class="card">
      <p class="muted" style="margin:0 0 6px">Galti chhupane se dobara hoti hai. Batane par saza nahi — sirf aage se rokne ka kaam hota hai.</p>
      <label>Kya hua</label><select id="k">${Object.entries(KIND).map(([k, v]) => `<option value="${k}">${v}</option>`).join("")}</select>
      <label>Kitna nuksaan</label><select id="s">${Object.entries(SEV).map(([k, v]) => `<option value="${k}">${v}</option>`).join("")}</select>
      <div class="row" style="gap:6px"><div style="flex:1"><label>Kab</label><input type="datetime-local" id="w" value="${now}" max="${now}"></div>
        <div style="flex:1"><label>Kahan</label><input id="l" placeholder="Ward 1"></div></div>
      <label>Patient (agar hai)</label><input id="pq" autocomplete="off" placeholder="Naam / UHID"><div id="pres"></div>
      <label>Poori baat</label><textarea id="d" rows="3"></textarea>
      <label>Turant kya kiya</label><input id="a">
      <label class="row" style="gap:6px"><input type="checkbox" id="an" style="width:auto"> Mera naam doctor ko na dikhe</label>
      <button class="full" id="go">📨 Bhejo</button><p class="msg" id="im"></p></div><div id="mine"></div>`;
  let t;
  $("pq").oninput = () => { clearTimeout(t); pid = null; t = setTimeout(async () => {
    const q = clean($("pq").value);
    if (q.length < 2) { $("pres").innerHTML = ""; return; }
    const { data } = await C.sb.rpc("search_patients", { q });
    $("pres").innerHTML = (data || []).slice(0, 5).map(p => `<button class="small ghost" style="margin:3px" data-p="${p.id}" data-n="${C.esc(p.full_name)}">${C.esc(p.full_name)} · ${C.esc(p.uhid)}</button>`).join("");
    $("pres").querySelectorAll("[data-p]").forEach(b => b.onclick = () => { pid = b.dataset.p; $("pq").value = b.dataset.n; $("pres").innerHTML = ""; });
  }, 300); };
  $("go").onclick = async () => {
    const { data: n, error } = await C.sb.rpc("q_report_incident", { p_kind: $("k").value, p_severity: $("s").value, p_when: new Date($("w").value).toISOString(),
      p_location: $("l").value, p_patient: pid, p_description: $("d").value, p_action: $("a").value, p_anonymous: $("an").checked });
    if (error) return err($("im"), error);
    inc(); setTimeout(() => ok($("im"), `✓ Ghatna #${n} doctor ko chali gayi. Dhanyavaad — isse sab surakshit rahenge.`), 200);
  };
  C.sb.from("incidents_view").select("incident_no, kind, status, corrective_action, created_at").eq("reported_by", C.me.id).order("created_at", { ascending: false }).limit(10)
    .then(({ data }) => { if (data?.length && $("mine")) $("mine").innerHTML = `<div class="card"><h4 style="margin:0 0 6px">Meri batayi ghatnayein</h4>${data.map(i => `<div style="margin:4px 0;font-size:13px">#${i.incident_no} ${KIND[i.kind]} · ${i.status}${i.corrective_action ? " · ✓ " + C.esc(i.corrective_action) : ""}</div>`).join("")}</div>`; });
}

// ---------------------------------------------------------------- review
async function review() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const [{ data }, { data: staff }] = await Promise.all([
    C.sb.from("incidents_view").select("*").order("created_at", { ascending: false }).limit(60),
    C.sb.from("profiles").select("id, full_name")]);
  const pids = [...new Set((data || []).map(i => i.patient_id).filter(Boolean))];
  const { data: pts } = pids.length ? await C.sb.from("patients").select("id, full_name, uhid").in("id", pids) : { data: [] };
  (data || []).forEach(i => { i.patients = pts?.find(p => p.id === i.patient_id); });
  const nm = id => id ? (staff?.find(s => s.id === id)?.full_name || "staff") : "🙈 naam chhupaya";
  const ST = { open: "🔴 Khula", reviewed: "🟡 Review hua", closed: "🟢 Band" };
  $("body").innerHTML = (data || []).map(i => `<div class="card" ${["severe", "death", "moderate"].includes(i.severity) && i.status === "open" ? `style="border-color:#fca5a5"` : ""}>
      <div class="row" style="justify-content:space-between"><b>#${i.incident_no} ${KIND[i.kind]}</b><span>${ST[i.status]}</span></div>
      <small class="muted">${SEV[i.severity]} · ${dt(i.happened_at)}${i.location ? " · " + C.esc(i.location) : ""}${i.patients ? " · " + C.esc(i.patients.full_name) : ""} · batane wala: ${C.esc(nm(i.reported_by))}</small>
      <p style="margin:6px 0">${C.esc(i.description)}</p>${i.immediate_action ? `<small>Turant: ${C.esc(i.immediate_action)}</small>` : ""}
      ${i.root_cause || i.corrective_action ? `<p style="margin:6px 0;font-size:13px">🔍 Kaaran: ${C.esc(i.root_cause || "—")}<br>🛡️ Aage se: ${C.esc(i.corrective_action || "—")}</p>` : ""}
      ${i.status !== "closed" ? `<div id="r_${i.id}"><button class="small" data-r="${i.id}">🔍 Review karo</button></div>` : ""}</div>`).join("")
    || `<div class="card"><p class="muted">Koi ghatna nahi.</p></div>`;
  $("body").querySelectorAll("[data-r]").forEach(b => b.onclick = () => {
    const id = b.dataset.r, box = $("r_" + id);
    box.innerHTML = `<label>Asli kaaran (root cause)</label><input id="rc_${id}"><label>Aage se rokne ke liye kya karenge</label><input id="ca_${id}">
      <div class="row" style="gap:6px;margin-top:6px"><button class="small ghost" data-s="0">Save (khula rakho)</button><button class="small" data-s="1">✅ Save + band karo</button></div><p class="msg" id="m_${id}"></p>`;
    box.querySelectorAll("[data-s]").forEach(x => x.onclick = async () => {
      const { error } = await C.sb.rpc("q_review_incident", { p_id: id, p_root: $("rc_" + id).value, p_action: $("ca_" + id).value, p_close: x.dataset.s === "1" });
      if (error) return err($("m_" + id), error);
      review();
    });
  });
}

// ---------------------------------------------------------------- numbers
async function nums(from = null, to = null) {
  const t = ist(); from = from || ymd(new Date(t.getFullYear(), t.getMonth(), 1)); to = to || ymd(t);
  $("body").innerHTML = `<div class="card row" style="gap:6px"><input type="date" id="f" value="${from}" style="width:auto"> se <input type="date" id="t" value="${to}" style="width:auto"><button class="small" id="go">Dekho</button></div><div id="nb">Loading…</div>`;
  $("go").onclick = () => nums($("f").value, $("t").value);
  const { data: q, error } = await C.sb.rpc("q_numbers", { p_from: from, p_to: to });
  if (error) { $("nb").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const v = (x, u = "") => x == null ? "—" : x + u;
  const row = (label, val, good, hint) => `<tr><td>${label}${hint ? `<br><small class="muted">${hint}</small>` : ""}</td><td style="text-align:right"><b ${good === false ? `style="color:var(--red)"` : ""}>${val}</b></td></tr>`;
  $("nb").innerHTML = `<div class="card"><table style="width:100%">
    ${row("OPD visit", v(q.opd_visits))}
    ${row("OPD mein avg intezaar", v(q.avg_opd_wait_min, " min"), q.avg_opd_wait_min == null || q.avg_opd_wait_min <= 30, "30 min se kam achha")}
    ${row("Visit jinka doctor note likha", v(q.visit_notes_pct, "%"), q.visit_notes_pct == null || q.visit_notes_pct >= 90, "90% se upar achha")}
    ${row("Admit", v(q.admissions))}
    ${row("Avg ruke (din)", v(q.avg_stay_days))}
    ${row("Discharge summary bani", v(q.discharge_summary_pct, "%"), q.discharge_summary_pct == null || q.discharge_summary_pct >= 95, "har discharge par zaroori")}
    ${row("30 din mein dobara admit", v(q.readmit_30d), !q.readmit_30d)}
    ${row("Maut / LAMA", `${v(q.deaths)} / ${v(q.lama)}`)}
    ${row("Lab report mein avg samay", v(q.lab_avg_tat_min, " min"))}
    ${row("Critical report dekhne mein avg samay", v(q.critical_ack_avg_min, " min"), q.critical_ack_avg_min == null || q.critical_ack_avg_min <= 30, "30 min se kam")}
    ${row("Critical jo kisi ne nahi dekha", v(q.critical_not_ack), !q.critical_not_ack)}
    ${row("Follow-up mein patient aaya", v(q.followup_done_pct, "%"))}
    ${row("Ghatna (gambhir)", `${v(q.incidents)} (${v(q.incidents_serious)})`, !q.incidents_serious)}
    ${row("Ghatna review baaki", v(q.incidents_open), !q.incidents_open)}
    ${row("Checklist bhari / kami", `${v(q.checklists_done)} / ${v(q.checklist_fail_lines)}`)}
    ${row("Allergy ke bawajood dawa", v(q.allergy_overrides), !q.allergy_overrides)}
    </table><p class="muted" style="font-size:12px">Laal = dhyan dein. Ye numbers NABH jaisi quality report mein kaam aate hain.</p></div>`;
}
