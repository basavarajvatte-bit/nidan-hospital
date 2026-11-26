// Vatte Hospital OS — Phase 13: HR (staff list, daily attendance, leave approvals, salary sheet + payment)
// Salary is calculated by the server from attendance; every payment also goes into the day book as an expense.
let C, TAB;
const $ = id => document.getElementById(id);
const rs = n => "₹" + Number(n || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 });
const ist = () => new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Kolkata" }));
const ymd = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const dmy = d => d ? new Date(d).toLocaleDateString("en-IN", { day: "2-digit", month: "short" }) : "";
const err = (el, e) => { if (el) { el.className = "msg err"; el.textContent = "❌ " + (e.message || e); } };
const ok = (el, t) => { if (el) { el.className = "msg ok"; el.textContent = t; } };
const can = r => r.includes(C.me.role);
const ATT = [["present", "✅ Haazir"], ["half_day", "🌓 Aadha din"], ["absent", "❌ Gair-haazir"], ["leave", "🏖️ Chhutti"], ["off", "💤 Weekly off"]];
const SHIFT = { morning: "Subah", evening: "Shaam", night: "Raat", general: "General" };
const LK = { casual: "Casual", sick: "Beemari", earned: "Earned", unpaid: "Bina salary", other: "Other" };

export function render(ctx) {
  C = ctx;
  const tabs = [can(["doctor", "admin", "hr"]) && ["att", "🕘 Hazri"], can(["doctor", "admin", "hr"]) && ["leave", "🏖️ Chhutti"],
                can(["doctor", "admin", "hr"]) && ["staff", "👥 Staff"], ["sal", "💵 Salary"]].filter(Boolean);
  TAB = tabs[0][0];
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button><h2 style="margin:0 0 6px">👥 HR</h2>
    <div class="row" id="tabs" style="gap:6px;margin-bottom:10px">${tabs.map(([k, l]) => `<button class="small ${k === TAB ? "" : "ghost"}" data-t="${k}">${l}</button>`).join("")}</div>
    <div id="body"><div class="card">Loading…</div></div>`;
  $("bk").onclick = C.goHome;
  C.app.querySelectorAll("#tabs [data-t]").forEach(b => b.onclick = () => {
    TAB = b.dataset.t; C.app.querySelectorAll("#tabs [data-t]").forEach(x => x.classList.toggle("ghost", x !== b)); show();
  });
  show();
}
function show() { ({ att, leave, staff, sal })[TAB](); }
const staffList = async (all = false) => {
  let q = C.sb.from("staff_members").select("*, departments(name)").order("full_name");
  if (!all) q = q.eq("active", true);
  const { data } = await q; return data || [];
};

// ---------------------------------------------------------------- attendance
async function att(day = ymd(ist())) {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const [list, { data: rows }] = await Promise.all([staffList(), C.sb.from("attendance").select("*").eq("day", day)]);
  const by = Object.fromEntries((rows || []).map(r => [r.staff_id, r]));
  const tm = t => t ? new Date(t).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }) : "";
  $("body").innerHTML = `<div class="card row" style="gap:6px"><label style="margin:0">Din</label>
      <input type="date" id="dd" value="${day}" max="${ymd(ist())}" style="width:auto">
      <button class="small ghost" id="allp">Sab ko ✅ Haazir</button></div>
    ${list.length ? `<div class="card" style="overflow-x:auto"><table><tr><th>Staff</th><th>Hazri</th><th>OT ghante</th></tr>${list.map(s => { const a = by[s.id]; return `<tr>
      <td><b>${C.esc(s.full_name)}</b><br><small class="muted">${C.esc(s.designation)}${s.shift ? " · " + SHIFT[s.shift] : ""}${a?.check_in ? ` · in ${tm(a.check_in)}` : ""}${a?.check_out ? ` · out ${tm(a.check_out)}` : ""}</small></td>
      <td><select data-s="${s.id}"><option value="">— nahi lagi —</option>${ATT.map(([k, l]) => `<option value="${k}" ${a?.status === k ? "selected" : ""}>${l}</option>`).join("")}</select></td>
      <td><input type="number" min="0" max="16" step="0.5" data-o="${s.id}" value="${a?.overtime_hours || 0}" style="width:60px"></td></tr>`; }).join("")}</table>
      <button class="full" id="sv" style="margin-top:8px">💾 Hazri save karo</button><p class="msg" id="am"></p></div>`
      : `<div class="card"><p class="muted">Pehle 👥 Staff mein staff jodein.</p></div>`}`;
  $("dd").onchange = () => att($("dd").value);
  $("allp").onclick = () => $("body").querySelectorAll("[data-s]").forEach(s => { if (!s.value) s.value = "present"; });
  if ($("sv")) $("sv").onclick = async () => {
    const rowsOut = [...$("body").querySelectorAll("[data-s]")].filter(s => s.value).map(s => ({ staff_id: s.dataset.s, status: s.value,
      overtime_hours: Number($("body").querySelector(`[data-o="${s.dataset.s}"]`).value) || 0 }));
    if (!rowsOut.length) return err($("am"), "Kisi ki hazri nahi chuni");
    const { data, error } = await C.sb.rpc("hr_mark_attendance", { p_day: day, p_rows: rowsOut });
    if (error) return err($("am"), error);
    ok($("am"), `✓ ${data} staff ki hazri save`);
  };
}

// ---------------------------------------------------------------- leave
async function leave() {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const [{ data }, list] = await Promise.all([
    C.sb.from("leave_requests").select("*, staff_members(full_name, designation)").order("created_at", { ascending: false }).limit(60), staffList()]);
  const pend = (data || []).filter(l => l.status === "pending"), rest = (data || []).filter(l => l.status !== "pending");
  const ST = { approved: "✅ Mili", rejected: "❌ Nahi mili", cancelled: "✖️ Cancel" };
  $("body").innerHTML = `<div class="card"><h3 style="margin:0 0 6px">Manzoori baaki (${pend.length})</h3>
      ${pend.map(l => `<div style="border-top:1px solid var(--line);padding:6px 0"><b>${C.esc(l.staff_members?.full_name)}</b> · ${dmy(l.from_day)} – ${dmy(l.to_day)}
        (${(new Date(l.to_day) - new Date(l.from_day)) / 864e5 + 1} din, ${LK[l.kind]})${l.reason ? `<br><small>${C.esc(l.reason)}</small>` : ""}
        <div class="row" style="gap:6px;margin-top:4px"><button class="small" data-y="${l.id}">✅ Manzoor</button><button class="small ghost" data-n="${l.id}">❌ Mana</button></div></div>`).join("") || "<p class='muted'>Koi arzi baaki nahi ✓</p>"}
      <p class="msg" id="lm"></p></div>
    <div class="card"><h3 style="margin:0 0 6px">Kisi staff ki taraf se chhutti likho</h3>
      <select id="ls">${list.map(s => `<option value="${s.id}">${C.esc(s.full_name)}</option>`).join("")}</select>
      <div class="row" style="gap:6px"><div style="flex:1"><label>Se</label><input type="date" id="lf"></div><div style="flex:1"><label>Tak</label><input type="date" id="lt"></div></div>
      <label>Kis tarah ki</label><select id="lk">${Object.entries(LK).map(([k, v]) => `<option value="${k}">${v}</option>`).join("")}</select>
      <label>Kaaran</label><input id="lr"><button class="full" id="lgo">Arzi likho</button><p class="msg" id="lm2"></p></div>
    <div class="card"><h4 style="margin:0 0 6px">Purani</h4>${rest.slice(0, 20).map(l => `<div style="margin:4px 0">${ST[l.status]} ${C.esc(l.staff_members?.full_name)} · ${dmy(l.from_day)} – ${dmy(l.to_day)} <small class="muted">${LK[l.kind]}</small></div>`).join("") || "<p class='muted'>—</p>"}</div>`;
  const dec = (sel, yes) => $("body").querySelectorAll(sel).forEach(b => b.onclick = async () => {
    const note = yes ? "" : (prompt("Mana karne ka kaaran (staff ko dikhega)?") || "");
    const { error } = await C.sb.rpc("hr_decide_leave", { p_id: b.dataset.y || b.dataset.n, p_approve: yes, p_note: note });
    if (error) return err($("lm"), error);
    leave();
  });
  dec("[data-y]", true); dec("[data-n]", false);
  $("lgo").onclick = async () => {
    const { error } = await C.sb.rpc("hr_request_leave", { p_staff: $("ls").value, p_from: $("lf").value || null, p_to: $("lt").value || null, p_kind: $("lk").value, p_reason: $("lr").value });
    if (error) return err($("lm2"), error);
    leave();
  };
}

// ---------------------------------------------------------------- staff list
async function staff(edit = null) {
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const [list, { data: profs }] = await Promise.all([staffList(true), C.sb.from("profiles").select("id, full_name, role").neq("role", "pending").order("full_name")]);
  const s = edit ? list.find(x => x.id === edit) : null;
  const used = new Set(list.filter(x => x.profile_id && x.id !== s?.id).map(x => x.profile_id));
  $("body").innerHTML = `<div class="card"><h3 style="margin:0 0 6px">${s ? "✏️ Staff badlo" : "＋ Naya staff"}</h3>
      <label>Poora naam</label><input id="n" value="${C.esc(s?.full_name || "")}">
      <div class="row" style="gap:6px"><div style="flex:1"><label>Pad (designation)</label><input id="d" value="${C.esc(s?.designation || "")}" placeholder="Staff nurse / Ward boy"></div>
        <div style="flex:1"><label>Department</label><input id="dp" value="${C.esc(s?.departments?.name || "")}" placeholder="Nursing"></div></div>
      <div class="row" style="gap:6px"><div style="flex:1"><label>Phone</label><input id="ph" value="${C.esc(s?.phone || "")}"></div>
        <div style="flex:1"><label>Ghar ka emergency phone</label><input id="eph" value="${C.esc(s?.emergency_phone || "")}"></div></div>
      <div class="row" style="gap:6px"><div style="flex:1"><label>Joining date</label><input type="date" id="j" value="${s?.joined_on || ""}"></div>
        <div style="flex:1"><label>Mahine ki salary ₹</label><input type="number" min="0" id="sl" value="${s?.monthly_salary ?? ""}"></div>
        <div style="flex:1"><label>Shift</label><select id="sh"><option value="">—</option>${Object.entries(SHIFT).map(([k, v]) => `<option value="${k}" ${s?.shift === k ? "selected" : ""}>${v}</option>`).join("")}</select></div></div>
      <label>App login (isse staff khud check-in / chhutti maang sakega)</label>
      <select id="pf"><option value="">— koi login nahi —</option>${(profs || []).filter(p => !used.has(p.id)).map(p => `<option value="${p.id}" ${s?.profile_id === p.id ? "selected" : ""}>${C.esc(p.full_name || "(naam nahi)")} · ${C.esc(p.role)}</option>`).join("")}</select>
      ${s ? `<label class="row" style="gap:6px"><input type="checkbox" id="ac" style="width:auto" ${s.active ? "checked" : ""}> Kaam par hai (hatao to tick hatao)</label>` : ""}
      <button class="full" id="sv">💾 Save</button>${s ? `<button class="ghost full" id="nw">Naya staff jodo</button>` : ""}<p class="msg" id="sm"></p></div>
    <div class="card" style="overflow-x:auto"><table><tr><th>Naam</th><th>Pad</th><th>Salary</th></tr>${list.map(x => `<tr data-e="${x.id}" style="cursor:pointer;${x.active ? "" : "opacity:.5"}">
      <td>${C.esc(x.full_name)}${x.profile_id ? " 📱" : ""}<br><small class="muted">${C.esc(x.departments?.name || "")}${x.shift ? " · " + SHIFT[x.shift] : ""}${x.active ? "" : " · chhod diya " + dmy(x.left_on)}</small></td>
      <td>${C.esc(x.designation)}</td><td>${x.monthly_salary != null ? rs(x.monthly_salary) : "—"}</td></tr>`).join("") || "<tr><td colspan=3 class='muted'>Abhi koi staff nahi</td></tr>"}</table>
      <p class="muted" style="font-size:12px">📱 = app login juda hai. Badalne ke liye naam par tap karo.</p></div>`;
  $("body").querySelectorAll("[data-e]").forEach(r => r.onclick = () => staff(r.dataset.e));
  if ($("nw")) $("nw").onclick = () => staff();
  $("sv").onclick = async () => {
    const { error } = await C.sb.rpc("hr_save_staff", { p_id: s?.id || null, p_name: $("n").value, p_designation: $("d").value, p_department: $("dp").value,
      p_phone: $("ph").value, p_joined: $("j").value || null, p_salary: $("sl").value === "" ? null : Number($("sl").value), p_shift: $("sh").value || null,
      p_profile: $("pf").value || null, p_active: $("ac") ? $("ac").checked : true, p_emergency: $("eph").value });
    if (error) return err($("sm"), error);
    await staff(); ok($("sm"), "✓ Save ho gaya");
  };
}

// ---------------------------------------------------------------- salary
async function sal(month = null) {
  const now = ist();
  month = month || ymd(new Date(now.getFullYear(), now.getMonth(), 1));
  $("body").innerHTML = `<div class="card">Loading…</div>`;
  const { data, error } = await C.sb.rpc("hr_salary_sheet", { p_month: month });
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  const payer = can(["doctor", "admin", "accountant"]);
  const tot = k => (data || []).reduce((s, r) => s + Number(r[k] || 0), 0);
  $("body").innerHTML = `<div class="card row" style="gap:6px"><label style="margin:0">Mahina</label><input type="month" id="mm" value="${month.slice(0, 7)}" style="width:auto"></div>
    <div class="card"><b>Banti ${rs(tot("payable"))} · Di ${rs(tot("paid"))} · Baaki ${rs(tot("due"))}</b>
      <p class="muted" style="font-size:12px;margin:4px 0">Salary = (mahine ki salary ÷ din) × (haazir + chhutti + weekly off + ½ aadha din) + overtime. Gair-haazir aur "bina salary" chhutti ka paisa nahi.</p></div>
    ${(data || []).map(r => `<div class="card">
      <div class="row" style="justify-content:space-between"><b>${C.esc(r.name)}</b><span>${Number(r.due) > 0 ? "🔴 Baaki " + rs(r.due) : "🟢 Poori di"}</span></div>
      <small class="muted">${C.esc(r.designation)} · ${rs(r.monthly)}/mahina</small>
      <div style="font-size:13px;margin-top:4px">✅ ${r.present} · 🌓 ${r.half_day} · 🏖️ ${r.leave}${r.unpaid_leave ? ` (+${r.unpaid_leave} bina salary)` : ""} · 💤 ${r.off} · ❌ ${r.absent} · OT ${r.overtime} ghante
        ${r.not_marked ? `<br><span style="color:#b45309">⚠️ ${r.not_marked} din ki hazri nahi lagi (in ka paisa nahi juda)</span>` : ""}
        <br>Paid din <b>${r.paid_days}</b> / ${r.days} → banti <b>${rs(r.payable)}</b> · di ${rs(r.paid)}</div>
      ${payer && Number(r.due) > 0 ? `<div class="row" style="gap:6px;margin-top:6px"><input type="number" min="1" value="${Math.max(0, r.due)}" data-a="${r.staff_id}" style="width:110px">
        <select data-m="${r.staff_id}" style="width:auto"><option value="bank">🏦 Bank</option><option value="upi">📱 UPI</option><option value="cash">💵 Cash</option></select>
        <button class="small" data-p="${r.staff_id}">Salary do</button></div>` : ""}
      <p class="msg" id="m${r.staff_id}"></p></div>`).join("") || `<div class="card"><p class="muted">Is mahine koi staff nahi.</p></div>`}`;
  $("mm").onchange = () => sal($("mm").value + "-01");
  $("body").querySelectorAll("[data-p]").forEach(b => b.onclick = async () => {
    const id = b.dataset.p, amt = Number($("body").querySelector(`[data-a="${id}"]`).value);
    const r = data.find(x => x.staff_id === id);
    const note = amt > Number(r.due) ? (prompt("Ye banti salary se zyada (advance) hai. Kaaran?") || "") : "";
    if (amt > Number(r.due) && !note.trim()) return;
    if (!confirm(`${r.name} ko ${rs(amt)} salary dena pakka? (Day book mein kharcha likha jayega)`)) return;
    b.disabled = true;
    const { error } = await C.sb.rpc("hr_pay_salary", { p_staff: id, p_month: month, p_amount: amt, p_method: $("body").querySelector(`[data-m="${id}"]`).value, p_note: note });
    if (error) { b.disabled = false; return err($("m" + id), error); }
    sal(month);
  });
}
