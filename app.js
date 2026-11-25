// Nidan Hospital OS — Phase 1: login, roles, role-based home screen, staff management.
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm";

const app = document.getElementById("app");
const who = document.getElementById("who");
const cfg = window.NIDAN_CONFIG || {};

const ROLES = {
  doctor: "Doctor", admin: "Administrator", receptionist: "Receptionist",
  nurse: "Nursing Sister", accountant: "Accountant", pharmacist: "Pharmacist",
  lab: "Lab Staff", hr: "HR Manager", pending: "Pending (role nahi mila)"
};

// Every module, who can see it, and which phase builds it.
const MODULES = [
  { id: "dashboard",  ico: "📊", name: "Doctor Dashboard", roles: ["doctor", "admin"], phase: 4 },
  { id: "reception",  ico: "🧾", name: "Reception",        roles: ["doctor", "admin", "receptionist"], phase: 3 },
  { id: "nursing",    ico: "🩺", name: "Nursing Sister",   roles: ["doctor", "admin", "nurse"], phase: 5 },
  { id: "nidan",      ico: "❓", name: "Nidan Questions",  roles: ["doctor", "nurse"], phase: 6 },
  { id: "appointments", ico: "📅", name: "Appointments",   roles: ["doctor", "admin", "receptionist"], phase: 9 },
  { id: "accounts",   ico: "💰", name: "Accounts",         roles: ["doctor", "admin", "accountant"], phase: 10 },
  { id: "pharmacy",   ico: "💊", name: "Pharmacy",         roles: ["doctor", "admin", "pharmacist"], phase: 11 },
  { id: "lab",        ico: "🧪", name: "Laboratory",       roles: ["doctor", "admin", "lab"], phase: 12 },
  { id: "hr",         ico: "👥", name: "HR",               roles: ["doctor", "admin", "hr"], phase: 13 },
  { id: "boss",       ico: "🤖", name: "Boss AI",          roles: ["doctor", "admin"], phase: 15 },
  { id: "staff",      ico: "🔐", name: "Staff & Roles",    roles: ["doctor", "admin"], ready: true },
  { id: "audit",      ico: "📜", name: "Audit Log",        roles: ["doctor", "admin"], ready: true }
];

const esc = s => String(s ?? "").replace(/[&<>"']/g, c =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});

// ---------- Setup check ----------
const configured = cfg.SUPABASE_URL && cfg.SUPABASE_URL.startsWith("https://") &&
                   cfg.SUPABASE_ANON_KEY && !cfg.SUPABASE_ANON_KEY.startsWith("PASTE");
if (!configured) {
  app.innerHTML = `<div class="card narrow warn"><h2>Setup baaki hai</h2>
    <p>App ban gaya hai, bas database jodna baaki hai.</p>
    <p class="muted">GitHub par <b>config.js</b> file mein Supabase ka Project URL aur anon key daalo.</p></div>`;
  throw new Error("Not configured");
}

const sb = createClient(cfg.SUPABASE_URL, cfg.SUPABASE_ANON_KEY);
let me = null; // { id, full_name, role, hospital_id, hospital_name, email }

// ---------- Auth screens ----------
function showLogin(mode = "login", note = "") {
  who.innerHTML = "";
  const signup = mode === "signup";
  app.innerHTML = `<div class="card narrow">
    <h2>${signup ? "Naya account banao" : "Login"}</h2>
    <form id="f">
      ${signup ? `<label>Poora naam</label><input id="name" required autocomplete="name">` : ""}
      <label>Email</label><input id="email" type="email" required autocomplete="email">
      <label>Password ${signup ? "(kam se kam 8 akshar)" : ""}</label>
      <input id="pass" type="password" required minlength="${signup ? 8 : 1}"
             autocomplete="${signup ? "new-password" : "current-password"}">
      <button class="full" id="go">${signup ? "Account banao" : "Login karo"}</button>
    </form>
    <p class="msg ${note.startsWith("✓") ? "ok" : "err"}" id="msg">${esc(note)}</p>
    <button class="ghost full" id="switch">${signup ? "Pehle se account hai? Login" : "Naya staff? Account banao"}</button>
  </div>`;
  document.getElementById("switch").onclick = () => showLogin(signup ? "login" : "signup");
  document.getElementById("f").onsubmit = async e => {
    e.preventDefault();
    const btn = document.getElementById("go"), msg = document.getElementById("msg");
    btn.disabled = true; msg.textContent = "Ruko…"; msg.className = "msg";
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("pass").value;
    let res;
    if (signup) {
      res = await sb.auth.signUp({ email, password,
        options: { data: { full_name: document.getElementById("name").value.trim() },
                   emailRedirectTo: location.href.split("#")[0] } });
      if (!res.error && !res.data.session) {
        return showLogin("login", "✓ Account ban gaya. Email check karo, link dabao, phir login karo.");
      }
    } else {
      res = await sb.auth.signInWithPassword({ email, password });
    }
    if (res.error) {
      btn.disabled = false; msg.className = "msg err";
      msg.textContent = res.error.message.includes("Invalid login") ? "Email ya password galat hai." : res.error.message;
    }
  };
}

// ---------- Load my profile ----------
async function loadMe(session) {
  const { data, error } = await sb.from("profiles")
    .select("id, full_name, role, hospital_id, hospitals(name)")
    .eq("id", session.user.id).single();
  if (error || !data) {
    app.innerHTML = `<div class="card narrow warn"><h2>Profile nahi mili</h2>
      <p class="muted">Database setup (phase1.sql) chala hai? Error: ${esc(error?.message)}</p>
      <button class="full" id="lo">Logout</button></div>`;
    document.getElementById("lo").onclick = () => sb.auth.signOut();
    return;
  }
  me = { ...data, hospital_name: data.hospitals?.name, email: session.user.email };
  who.innerHTML = `${esc(me.full_name || me.email)}<br><b>${esc(ROLES[me.role])}</b> ·
    <a href="#" id="logout" style="color:#fff">Logout</a>`;
  document.getElementById("logout").onclick = e => { e.preventDefault(); sb.auth.signOut(); };
  showHome();
}

// ---------- Home (only allowed modules) ----------
function showHome() {
  if (me.role === "pending") {
    app.innerHTML = `<div class="card narrow warn"><h2>Ruko 🙏</h2>
      <p>Aapka account ban gaya hai. Doctor aapko role denge (jaise Sister ya Receptionist), tab aapke modules dikhenge.</p>
      <button class="full" id="re">Dobara check karo</button></div>`;
    document.getElementById("re").onclick = async () => loadMe((await sb.auth.getSession()).data.session);
    return;
  }
  const mine = MODULES.filter(m => m.roles.includes(me.role));
  app.innerHTML = `<h2>Namaste${me.full_name ? ", " + esc(me.full_name) : ""} 👋</h2>
    <p class="muted">${esc(me.hospital_name)} · ${esc(ROLES[me.role])}</p>
    <div class="grid">${mine.map(m => `
      <button class="tile ${m.ready ? "" : "soon"}" data-id="${m.id}">
        <span class="ico">${m.ico}</span>${esc(m.name)}
        <small>${m.ready ? "Taiyaar" : "Phase " + m.phase + " mein aayega"}</small>
      </button>`).join("")}</div>`;
  app.querySelectorAll(".tile").forEach(t => t.onclick = () => openModule(t.dataset.id));
}

function openModule(id) {
  const m = MODULES.find(x => x.id === id);
  if (!m || !m.roles.includes(me.role)) return showHome();
  if (id === "staff") return showStaff();
  if (id === "audit") return showAudit();
  app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button>
    <div class="card"><h2>${m.ico} ${esc(m.name)}</h2>
    <p class="muted">Ye module Phase ${m.phase} mein banega.</p></div>`;
  document.getElementById("bk").onclick = showHome;
}

// ---------- Staff & Roles ----------
async function showStaff(note = "") {
  app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button>
    <div class="card"><h2>🔐 Staff & Roles</h2>
    <p class="muted">Naya staff app khol kar "Account banao" karega. Phir yahan aap uska role chunoge.</p>
    <p class="msg" id="msg">${esc(note)}</p><div id="list">Loading…</div></div>`;
  document.getElementById("bk").onclick = showHome;
  const { data, error } = await sb.from("profiles")
    .select("id, full_name, role, created_at").order("created_at");
  const list = document.getElementById("list");
  if (error) { list.textContent = "Error: " + error.message; return; }
  const options = Object.keys(ROLES)
    .filter(r => me.role === "doctor" || r !== "doctor");
  list.innerHTML = `<table><tr><th>Naam</th><th>Role</th><th></th></tr>${data.map(p => `
    <tr><td>${esc(p.full_name || "(naam nahi)")}${p.id === me.id ? " <small class='muted'>(aap)</small>" : ""}</td>
    <td><span class="badge ${p.role === "pending" ? "pending" : ""}">${esc(ROLES[p.role])}</span></td>
    <td>${p.id === me.id || (p.role === "doctor" && me.role !== "doctor") ? "" : `
      <div class="row"><select data-id="${p.id}">${options.map(r =>
        `<option value="${r}" ${r === p.role ? "selected" : ""}>${esc(ROLES[r])}</option>`).join("")}</select>
      <button class="small" data-save="${p.id}">Save</button></div>`}</td></tr>`).join("")}</table>`;
  list.querySelectorAll("[data-save]").forEach(b => b.onclick = async () => {
    const id = b.dataset.save;
    const role = list.querySelector(`select[data-id="${id}"]`).value;
    b.disabled = true;
    const { error } = await sb.rpc("set_staff_role", { target: id, new_role: role });
    showStaff(error ? "❌ " + error.message : "✓ Role badal diya");
  });
}

// ---------- Audit Log ----------
async function showAudit() {
  app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button>
    <div class="card"><h2>📜 Audit Log</h2><p class="muted">Kisne kya kiya — ye record koi mita nahi sakta.</p>
    <div id="list">Loading…</div></div>`;
  document.getElementById("bk").onclick = showHome;
  const [{ data: logs, error }, { data: staff }] = await Promise.all([
    sb.from("audit_logs").select("*").order("created_at", { ascending: false }).limit(100),
    sb.from("profiles").select("id, full_name")
  ]);
  const list = document.getElementById("list");
  if (error) { list.textContent = "Error: " + error.message; return; }
  const name = id => esc(staff?.find(s => s.id === id)?.full_name || "—");
  list.innerHTML = logs.length ? `<table><tr><th>Samay</th><th>Kisne</th><th>Kya</th></tr>${logs.map(l => `
    <tr><td>${new Date(l.created_at).toLocaleString("en-IN")}</td><td>${name(l.actor_id)}</td>
    <td>${esc(l.action)} <small class="muted">${esc(describe(l, name))}</small></td></tr>`).join("")}</table>`
    : "<p class='muted'>Abhi kuch nahi.</p>";
}
function describe(l, name) {
  const d = l.details || {};
  if (l.action === "role_changed") return `${ROLES[d.from] || d.from} → ${ROLES[d.to] || d.to}`;
  if (l.action === "staff_signup") return ROLES[d.role] || "";
  return "";
}

// ---------- Start ----------
sb.auth.onAuthStateChange((_event, session) => {
  if (!session) { me = null; return showLogin(); }
  if (me && me.id === session.user.id) return; // token refresh: stay on current screen
  setTimeout(() => loadMe(session), 0);
});
