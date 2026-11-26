// Vatte Hospital OS — Phase 3: Reception (registration, duplicate check, search, OPD, IPD, beds)
const tel = ph => { const d = String(ph || "").replace(/\D/g, ""); return d.length === 10 ? "+91" + d : d ? "+" + d.replace(/^0+/, "") : ""; };
const callBtn = ph => tel(ph) ? `<a class="callbtn" href="tel:${tel(ph)}" onclick="event.stopPropagation()">📞 Call</a>` : "";
let C; // context: { sb, me, app, esc, goHome }

const KIND = { opd: "OPD", ipd: "IPD (Admit)", emergency: "Emergency" };
const BED_COLOR = { available: "#16a34a", occupied: "#dc2626", cleaning: "#d97706", blocked: "#64748b" };
const BED_TEXT = { available: "Khali", occupied: "Bhara", cleaning: "Safai", blocked: "Band" };

const $ = id => document.getElementById(id);
const time = t => new Date(t).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
const date = t => new Date(t).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
const cleanErr = e => (e?.message || String(e)).replace(/^.*?exception:?\s*/i, "");

export function render(ctx, tab = "today") {
  C = ctx;
  C.app.innerHTML = `
    <button class="ghost small back" id="bk">← Wapas</button>
    <h2>🧾 Reception</h2>
    <div class="tabs">
      ${[["today", "Aaj ke patient"], ["new", "+ Naya patient"], ["search", "🔍 Search"], ["beds", "🛏️ Beds"]]
        .map(([k, v]) => `<button class="tab ${k === tab ? "on" : ""}" data-t="${k}">${v}</button>`).join("")}
    </div>
    <div id="pane"></div>`;
  $("bk").onclick = C.goHome;
  C.app.querySelectorAll(".tab").forEach(b => b.onclick = () => render(C, b.dataset.t));
  ({ today: showToday, new: showNew, search: showSearch, beds: showBeds })[tab]();
}

// ---------- Aaj ke patient ----------
async function showToday() {
  const pane = $("pane");
  pane.innerHTML = `<div class="card">Loading…</div>`;
  const start = new Date(); start.setHours(0, 0, 0, 0);
  const [{ data: visits, error }, { data: admitted }] = await Promise.all([
    C.sb.from("encounters").select("id, kind, status, started_at, chief_complaint, patients(id, uhid, full_name)")
      .gte("started_at", start.toISOString()).order("started_at", { ascending: false }),
    C.sb.from("admissions").select("id, admitted_at, patients(id, uhid, full_name), beds(label)")
      .eq("status", "admitted").order("admitted_at")
  ]);
  if (error) { pane.innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const opdOpen = visits.filter(v => v.kind !== "ipd" && v.status === "open").length;
  pane.innerHTML = `
    <div class="stats">
      <div class="stat"><b>${visits.length}</b><span>Aaj ke visit</span></div>
      <div class="stat"><b>${opdOpen}</b><span>OPD mein ruke</span></div>
      <div class="stat"><b>${admitted?.length || 0}</b><span>Admit (IPD)</span></div>
    </div>
    <div class="card"><h3>Aaj ke visit</h3>
      ${visits.length ? `<table><tr><th>Samay</th><th>Patient</th><th>Type</th><th></th></tr>
        ${visits.map(v => `<tr>
          <td>${time(v.started_at)}</td>
          <td><a href="#" data-p="${v.patients.id}">${C.esc(v.patients.full_name)}</a><br><small class="muted">${C.esc(v.patients.uhid)}</small></td>
          <td>${KIND[v.kind]}<br><small class="muted">${v.status === "open" ? "Chalu" : "Ho gaya"}</small></td>
          <td>${v.kind !== "ipd" && v.status === "open" ? `<button class="small" data-co="${v.id}">Check-out</button>` : ""}</td>
        </tr>`).join("")}</table>` : `<p class="muted">Aaj abhi koi patient nahi aaya.</p>`}
    </div>
    <div class="card"><h3>Abhi admit patient</h3>
      ${admitted?.length ? `<table>${admitted.map(a => `<tr>
          <td><a href="#" data-p="${a.patients.id}">${C.esc(a.patients.full_name)}</a><br><small class="muted">${C.esc(a.patients.uhid)}</small></td>
          <td>🛏️ ${C.esc(a.beds?.label || "-")}</td><td><small class="muted">${date(a.admitted_at)}</small></td></tr>`).join("")}</table>`
        : `<p class="muted">Koi admit nahi hai.</p>`}
    </div>`;
  wirePatientLinks(pane);
  pane.querySelectorAll("[data-co]").forEach(b => b.onclick = async () => {
    b.disabled = true;
    const { error } = await C.sb.from("encounters").update({ status: "closed", ended_at: new Date().toISOString() }).eq("id", b.dataset.co);
    if (error) { alertCard(pane, error.message); b.disabled = false; } else showToday();
  });
}

// ---------- Naya patient ----------
function showNew() {
  $("pane").innerHTML = `<div class="card"><h3>Naya patient register karo</h3>
    <form id="f">
      <label>Poora naam *</label><input id="n" required>
      <div class="two">
        <div><label>Gender *</label><select id="g" required><option value="">Chuno</option>
          <option value="male">Purush (Male)</option><option value="female">Mahila (Female)</option><option value="other">Other</option></select></div>
        <div><label>Umar (saal) *</label><input id="a" type="number" min="0" max="130" required inputmode="numeric"></div>
      </div>
      <label>Mobile number</label><input id="ph" inputmode="numeric" maxlength="10" placeholder="10 digit">
      <label>Pata (address)</label><input id="ad">
      <div class="two">
        <div><label>Blood group</label><select id="bg"><option value="">Pata nahi</option>
          ${["A+","A-","B+","B-","AB+","AB-","O+","O-"].map(x => `<option>${x}</option>`).join("")}</select></div>
        <div><label>ABHA ID</label><input id="ab" placeholder="Optional"></div>
      </div>
      <label>Allergy (agar koi ho)</label><input id="al" placeholder="Jaise: Penicillin">
      <button class="full" id="go">Aage badho</button>
    </form><p class="msg" id="msg"></p><div id="dups"></div></div>`;
  $("f").onsubmit = async e => {
    e.preventDefault();
    const form = readForm();
    if (form.phone && !/^\d{10}$/.test(form.phone)) return setMsg("Mobile number 10 digit ka hona chahiye", true);
    $("go").disabled = true; setMsg("Pehle se register to nahi, check kar raha hoon…");
    const { data: dups, error } = await C.sb.rpc("find_duplicate_patients",
      { p_name: form.full_name, p_phone: form.phone, p_age: form.age_years, p_abha: form.abha_id });
    if (error) { $("go").disabled = false; return setMsg(error.message, true); }
    if (!dups.length) return save(form);
    setMsg("");
    $("dups").innerHTML = `<div class="card warn"><h3>⚠️ Ye patient shayad pehle se register hai</h3>
      <table>${dups.map(d => `<tr><td><b>${C.esc(d.full_name)}</b> (${C.esc(d.uhid)})<br>
        <small class="muted">${C.esc(d.gender || "")} · ${d.age ?? "?"} saal · ${C.esc(d.phone || "no phone")} · ${C.esc(d.reason)}</small></td>
        <td><button class="small" data-p="${d.id}">Yahi hai, kholo</button></td></tr>`).join("")}</table>
      <button class="ghost full" id="force">Nahi, ye alag patient hai — naya banao</button></div>`;
    $("dups").querySelectorAll("[data-p]").forEach(b => b.onclick = () => showPatient(b.dataset.p));
    $("force").onclick = () => save(form);
  };
}
function readForm() {
  const v = id => $(id).value.trim() || null;
  return { full_name: v("n"), gender: v("g"), age_years: Number($("a").value), phone: v("ph"),
           address: v("ad"), blood_group: v("bg"), abha_id: v("ab"), allergies: v("al") };
}
async function save(form) {
  setMsg("Save ho raha hai…");
  const { data, error } = await C.sb.from("patients").insert(form).select("id, uhid").single();
  if (error) { $("go").disabled = false; return setMsg(error.message, true); }
  showPatient(data.id, `✓ Patient register ho gaya. UHID: ${data.uhid}`);
}
function setMsg(t, err = false) { const m = $("msg"); if (m) { m.textContent = t; m.className = "msg " + (err ? "err" : "ok"); } }

// ---------- Search ----------
function showSearch() {
  $("pane").innerHTML = `<div class="card"><h3>Patient dhundo</h3>
    <div class="row"><input id="q" placeholder="Naam, mobile ya UHID" style="flex:1">
    <button id="go">Search</button></div><div id="res" style="margin-top:12px"></div></div>`;
  const run = async () => {
    const q = $("q").value.replace(/[,()%*\\":]/g, " ").trim();
    if (q.length < 2) return;
    $("res").textContent = "Dhundh raha hoon…";
    const { data, error } = await C.sb.from("patients").select("id, uhid, full_name, gender, phone, age_years, created_at")
      .or(`full_name.ilike."%${q}%",phone.ilike."%${q}%",uhid.ilike."%${q}%"`).order("created_at", { ascending: false }).limit(30);
    if (error) { $("res").textContent = error.message; return; }
    $("res").innerHTML = data.length ? `<table>${data.map(p => `<tr>
      <td><a href="#" data-p="${p.id}">${C.esc(p.full_name)}</a><br><small class="muted">${C.esc(p.uhid)} · ${C.esc(p.gender || "")}</small></td>
      <td>${C.esc(p.phone || "")} ${callBtn(p.phone)}</td></tr>`).join("")}</table>` : `<p class="muted">Koi nahi mila.</p>`;
    wirePatientLinks($("res"));
  };
  $("go").onclick = run;
  $("q").onkeydown = e => { if (e.key === "Enter") run(); };
  $("q").focus();
}

// ---------- Patient page ----------
async function showPatient(id, note = "") {
  const pane = $("pane");
  C.app.querySelectorAll(".tab").forEach(t => t.classList.remove("on"));
  pane.innerHTML = `<div class="card">Loading…</div>`;
  const [{ data: p, error }, { data: visits }, { data: adm }, { data: doctors }] = await Promise.all([
    C.sb.from("patients").select("*").eq("id", id).single(),
    C.sb.from("encounters").select("id, kind, status, started_at, ended_at, chief_complaint").eq("patient_id", id)
      .order("started_at", { ascending: false }).limit(15),
    C.sb.from("admissions").select("id, admitted_at, beds(label)").eq("patient_id", id).eq("status", "admitted").maybeSingle(),
    C.sb.from("profiles").select("id, full_name").eq("role", "doctor")
  ]);
  if (error) { pane.innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const age = p.age_years != null ? p.age_years + new Date().getFullYear() - new Date(p.created_at).getFullYear() : "?";
  const openOpd = visits.find(v => v.kind !== "ipd" && v.status === "open");
  const docOpts = (doctors || []).map(d => `<option value="${d.id}">Dr. ${C.esc(d.full_name || "Doctor")}</option>`).join("");
  pane.innerHTML = `
    ${note ? `<div class="card msg ok">${C.esc(note)}</div>` : ""}
    <div class="card">
      <h3>${C.esc(p.full_name)} <span class="badge">${C.esc(p.uhid)}</span> ${callBtn(p.phone)}</h3>
      <p>${C.esc(p.gender || "")} · ${age} saal · ${C.esc(p.phone || "mobile nahi")}${p.blood_group ? " · " + C.esc(p.blood_group) : ""}</p>
      ${p.allergies ? `<p class="msg err">⚠️ Allergy: ${C.esc(p.allergies)}</p>` : ""}
      ${p.address ? `<p class="muted">${C.esc(p.address)}</p>` : ""}
      ${adm ? `<p class="badge pending">🛏️ Admit hai — Bed ${C.esc(adm.beds?.label || "")} (${date(adm.admitted_at)} se)</p>` : ""}
    </div>
    <div class="card"><h3>Kya karna hai?</h3>
      <div class="row">
        ${openOpd ? `<button id="co">✓ OPD Check-out</button>` : `<button id="opd">OPD visit shuru karo</button>`}
        ${adm ? `<button class="ghost" id="dis">Discharge karo</button>` : `<button class="ghost" id="ad">IPD Admit karo</button>`}
      </div><div id="act"></div>
    </div>
    <div class="card"><h3>Purane visit</h3>
      ${visits.length ? `<table>${visits.map(v => `<tr><td>${date(v.started_at)}</td><td>${KIND[v.kind]}</td>
        <td>${C.esc(v.chief_complaint || "")}</td><td><small class="muted">${v.status === "open" ? "Chalu" : "Ho gaya"}</small></td></tr>`).join("")}</table>`
        : `<p class="muted">Abhi koi visit nahi.</p>`}
    </div>`;

  const act = $("act");
  if ($("opd")) $("opd").onclick = () => {
    act.innerHTML = `<form id="vf"><label>Kya takleef hai? (chief complaint)</label><input id="cc" required>
      <label>Doctor</label><select id="dr">${docOpts}</select>
      <button class="full">OPD visit shuru karo</button><p class="msg" id="vm"></p></form>`;
    $("vf").onsubmit = async e => {
      e.preventDefault();
      const { error } = await C.sb.from("encounters").insert({ patient_id: id, kind: "opd",
        doctor_id: $("dr").value || null, chief_complaint: $("cc").value.trim() });
      if (error) { $("vm").textContent = error.message; $("vm").className = "msg err"; }
      else showPatient(id, "✓ OPD visit shuru ho gaya. Patient doctor ki list mein aa gaya.");
    };
  };
  if ($("co")) $("co").onclick = async () => {
    const { error } = await C.sb.from("encounters").update({ status: "closed", ended_at: new Date().toISOString() }).eq("id", openOpd.id);
    if (error) alertCard(act, error.message); else showPatient(id, "✓ OPD check-out ho gaya");
  };
  if ($("ad")) $("ad").onclick = async () => {
    const { data: beds } = await C.sb.from("beds").select("id, label, rooms(name)").eq("status", "available").order("label");
    if (!beds?.length) {
      const { count } = await C.sb.from("beds").select("id", { count: "exact", head: true });
      act.innerHTML = `<p class="msg err">${count ? "Abhi saare bed bhare hain ya safai mein hain." :
        "Abhi tak koi ward/bed bana hi nahi hai."}</p><button class="full" id="gobeds">🛏️ Beds kholo</button>`;
      $("gobeds").onclick = () => render(C, "beds");
      return;
    }
    act.innerHTML = `<form id="af"><label>Bed chuno</label><select id="bd">${beds.map(b =>
        `<option value="${b.id}">${C.esc(b.label)} (${C.esc(b.rooms?.name || "")})</option>`).join("")}</select>
      <label>Doctor</label><select id="dr">${docOpts}</select>
      <label>Admit kyon? (reason)</label><input id="cc" required>
      <button class="full">Admit karo</button><p class="msg" id="am"></p></form>`;
    $("af").onsubmit = async e => {
      e.preventDefault();
      const { error } = await C.sb.rpc("admit_patient", { p_patient: id, p_bed: $("bd").value,
        p_doctor: $("dr").value || null, p_complaint: $("cc").value.trim() });
      if (error) { $("am").textContent = cleanErr(error); $("am").className = "msg err"; }
      else showPatient(id, "✓ Patient admit ho gaya");
    };
  };
  if ($("dis")) $("dis").onclick = () => {
    act.innerHTML = `<form id="df"><label>Discharge note (doctor ne jo bataya, optional)</label>
      <textarea id="sm" rows="3"></textarea>
      <button class="full">Discharge pakka karo</button><p class="msg" id="dm"></p></form>`;
    $("df").onsubmit = async e => {
      e.preventDefault();
      if (!confirmInline($("df"))) return;
      const { error } = await C.sb.rpc("discharge_patient", { p_admission: adm.id, p_summary: $("sm").value });
      if (error) { $("dm").textContent = cleanErr(error); $("dm").className = "msg err"; }
      else showPatient(id, "✓ Discharge ho gaya. Bed safai ke liye chala gaya.");
    };
  };
}

// Two-tap confirm without browser popups
function confirmInline(form) {
  if (form.dataset.sure) return true;
  form.dataset.sure = "1";
  const b = form.querySelector("button"); b.textContent = "Pakka? Dobara dabao"; b.style.background = "#dc2626";
  return false;
}

// ---------- Beds ----------
async function showBeds() {
  const pane = $("pane");
  pane.innerHTML = `<div class="card">Loading…</div>`;
  const { data: rooms, error } = await C.sb.from("rooms").select("id, name, kind, beds(id, label, status)").order("name");
  if (error) { pane.innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const all = rooms.flatMap(r => r.beds);
  const count = s => all.filter(b => b.status === s).length;
  const canSetup = ["doctor", "admin"].includes(C.me.role);
  pane.innerHTML = `
    <div class="stats">
      <div class="stat"><b style="color:${BED_COLOR.available}">${count("available")}</b><span>Khali</span></div>
      <div class="stat"><b style="color:${BED_COLOR.occupied}">${count("occupied")}</b><span>Bhare</span></div>
      <div class="stat"><b style="color:${BED_COLOR.cleaning}">${count("cleaning")}</b><span>Safai</span></div>
    </div>
    ${rooms.map(r => `<div class="card"><h3>${C.esc(r.name)} <small class="muted">${C.esc(r.kind)}</small></h3>
      <div class="beds">${r.beds.sort((a, b) => a.label.localeCompare(b.label, undefined, { numeric: true })).map(b => `
        <div class="bed" style="border-color:${BED_COLOR[b.status]}">
          <b>${C.esc(b.label)}</b><span style="color:${BED_COLOR[b.status]}">${BED_TEXT[b.status]}</span>
          ${b.status === "cleaning" ? `<button class="small" data-clean="${b.id}">Saaf ho gaya</button>` : ""}
        </div>`).join("")}</div></div>`).join("") || `<div class="card muted">Abhi koi room/bed nahi bana.${canSetup ? " Neeche se banao." : " Doctor se banwao."}</div>`}
    ${canSetup ? `<div class="card"><h3>+ Naya room / ward</h3><form id="rf">
      <label>Naam</label><input id="rn" required placeholder="Jaise: General Ward">
      <div class="two"><div><label>Type</label><select id="rk">
        <option value="ward">Ward</option><option value="private">Private</option><option value="icu">ICU</option><option value="other">Other</option></select></div>
      <div><label>Kitne bed?</label><input id="rb" type="number" min="1" max="100" value="5" required></div></div>
      <button class="full">Room banao</button><p class="msg" id="rm"></p></form></div>` : ""}`;
  pane.querySelectorAll("[data-clean]").forEach(b => b.onclick = async () => {
    b.disabled = true;
    const { error } = await C.sb.from("beds").update({ status: "available" }).eq("id", b.dataset.clean);
    if (error) alertCard(pane, error.message); else showBeds();
  });
  if ($("rf")) $("rf").onsubmit = async e => {
    e.preventDefault();
    const { error } = await C.sb.rpc("add_room_with_beds", { p_name: $("rn").value, p_kind: $("rk").value, p_beds: Number($("rb").value) });
    if (error) { $("rm").textContent = cleanErr(error); $("rm").className = "msg err"; } else showBeds();
  };
}

// ---------- helpers ----------
function wirePatientLinks(root) {
  root.querySelectorAll("[data-p]").forEach(a => a.onclick = e => { e.preventDefault(); showPatient(a.dataset.p); });
}
function alertCard(root, text) {
  const d = document.createElement("div"); d.className = "card msg err"; d.textContent = text; root.prepend(d);
}

// Open a patient's page directly (used by other modules, e.g. dashboard)
export function openPatient(ctx, id) { render(ctx, "search"); showPatient(id); }
