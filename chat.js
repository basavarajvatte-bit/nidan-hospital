// Vatte Hospital OS — Phase 8: AI Chat (Sister AI / Reception AI)
// Talks to the 'agent-chat' server function. The AI only sees hospital data through tools that use
// this user's own login; patient names are hidden from the AI as codes. Every chat is saved (ai_conversations / ai_messages).
let C, AG = null, CONV = null, BUSY = false, LIST = [];
const $ = id => document.getElementById(id);
const TOOL = { find_patient: "🔎 patient dhoonda", latest_vitals: "🩺 vitals dekhe", list_beds: "🛏️ bed list",
  "nurse__overdue_vitals": "⏰ baaki vitals", "operations__beds": "🛏️ bed sthiti", "followup__due": "📞 follow-up list",
  "followup__schedule": "✋ follow-up approval ko bheja", "operations__bed_status": "✋ bed badlav approval ko bheja",
  "reception__today": "🧾 aaj ka hisaab", "appointment__today": "📅 appointments", "lab__pending": "🧪 lab baaki", "lab__today": "🧪 aaj ka lab", "hr__today": "👥 aaj ki hazri", "records__pending": "🗂️ records baaki", "quality__today": "✅ aaj ki quality", "quality__numbers": "📈 quality numbers", "hr__salary_due": "💵 salary baaki",
  "operations__tickets": "🛠️ repair / service", "procurement__pending": "🛒 kharid baaki", "lab__patient_reports": "🧪 patient ki reports",
  "pharmacy__stock": "💊 stock / expiry", "pharmacy__find_medicine": "💊 dawa dhoondi", "pharmacy__sales_today": "💊 aaj ki bikri",
  "pharmacy__reorder": "📦 kya mangwana hai", "pharmacy__order_draft": "✋ order list approval ko bheji", "accountant__dues": "💰 baaki bill", "boss__daily_report": "🤖 poori report", "boss__priorities": "🎯 zaroori kaam", "ipd__admitted": "🛏️ admit patient list", "opd__list": "🧑‍⚕️ OPD list", "ipd__movements": "🔁 admit / discharge list", "patient__summary": "📋 patient ki jhalak", "boss__numbers": "📊 aankde" };
const HINTS = {
  nurse: ["Kis patient ke vitals baaki hain?", "Kitne bed khali hain?", "Aaj ke follow-up batao", "Dummy Ramesh ke aakhri vitals"],
  reception: ["Aaj ka hisaab batao", "Kitne bed khali hain?", "Aaj ki appointments", "Aaj ke follow-up kaun se hain?"],
  boss: ["Abhi admit saare patient ki list do", "Aaj ke OPD patient kaun hain?", "Abhi kya zaroori hai?", "Aaj ke aankde kal se kaise hain?", "Aaj hospital ka haal batao", "Baaki bill kitne hain?"],
  appointment: ["Aaj ki appointments batao"],
  lab: ["Kaun se test baaki hain?", "Aaj lab mein kitna kaam hua?", "Koi critical report hai?"],
  pharmacy: ["Paracetamol kitni bachi hai?", "Kaunsi dawa expire hone wali hai?", "Kya mangwana hai?", "Aaj kitni bikri hui?"],
  accountant: ["Kitne bill baaki hain?"],
  followup: ["Aaj ke follow-up batao", "Kaun se follow-up late hain?"],
  operations: ["Kitne bed khali hain?", "Kaun se repair baaki hain?", "Kis machine ki service due hai?"],
  records: ["Kaun se note / discharge summary baaki hain?", "Aaj ke follow-up batao"],
  quality: ["Aaj ki checklist ka haal?", "Is mahine ke quality numbers batao"],
  hr: ["Aaj kaun haazir hai?", "Pichhle mahine ki salary kitni baaki hai?"],
  procurement: ["Kaun si kharid manzoori ke liye baaki hai?", "Kaun si dawa mangwani hai?"]
};
let ICON = {};

export async function render(ctx, pick = null) {
  C = ctx; CONV = null; AG = null;
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button>
    <h2 style="margin:0 0 4px">💬 AI se baat</h2><div id="body"><div class="card">Loading…</div></div>`;
  $("bk").onclick = C.goHome;
  const [{ data, error }, { data: ag }] = await Promise.all([
    C.sb.from("ai_chat_agents").select("*"),
    C.sb.from("agents").select("id, icon, responsibilities, status")
  ]);
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  ICON = Object.fromEntries((ag || []).map(x => [x.id, x]));
  const order = ["boss", "nurse", "reception", "appointment", "lab", "pharmacy", "accountant", "followup", "operations", "hr", "procurement", "records", "quality"];
  LIST = (data || []).filter(a => a.roles.includes(C.me.role)).sort((x, y) => order.indexOf(x.agent_id) - order.indexOf(y.agent_id));
  if (!LIST.length) { $("body").innerHTML = `<div class="card"><p class="muted">Aapke role ke liye abhi koi AI chat nahi hai.</p></div>`; return; }
  const chosen = pick && LIST.find(a => a.agent_id === pick);
  if (chosen) return open(chosen);
  if (LIST.length === 1) return open(LIST[0]);
  $("body").innerHTML = `<p class="muted">Kis AI se baat karni hai? Har baat-cheet hamesha save rehti hai.</p><div class="grid">${LIST.map(a => `
    <button class="tile" data-a="${a.agent_id}"><span class="ico">${ICON[a.agent_id]?.icon || "🤖"}</span>${C.esc(a.title)}
    <small>${C.esc((ICON[a.agent_id]?.responsibilities || "").split(",").slice(0, 3).join(","))}</small></button>`).join("")}</div>`;
  $("body").querySelectorAll("[data-a]").forEach(b => b.onclick = () => open(LIST.find(a => a.agent_id === b.dataset.a)));
}

function open(a, conv = null) {
  AG = a; CONV = conv;
  $("body").innerHTML = `
    <div class="row" style="justify-content:space-between;margin-bottom:6px;gap:6px">
      <b>${ICON[a.agent_id]?.icon || "🤖"} ${C.esc(a.title)}</b>
      <span class="row" style="gap:6px">
        <button class="small ghost" id="old">🕘 Purani baatein</button>
        <button class="small ghost" id="new">＋ Nayi</button>
        ${LIST.length > 1 ? `<button class="small ghost" id="sw">Badlo</button>` : ""}
      </span>
    </div>
    <div id="oldlist"></div>
    <div class="card" style="background:#fffbeb;border-color:#fde68a;padding:8px 10px;font-size:13px">
      ⚠️ Ye AI hai — galti ho sakti hai. Diagnosis / dawa nahi deta, kuch approve nahi karta. Abhi sirf <b>dummy (nakli) patient</b> ke saath use karein. Saari baat-cheet hamesha save rehti hai (koi delete nahi kar sakta).</div>
    <div id="chat" style="display:flex;flex-direction:column;gap:8px;margin:10px 0;min-height:200px"></div>
    <div class="row" id="hints" style="gap:6px;flex-wrap:wrap;margin-bottom:8px">${(HINTS[a.agent_id] || []).map(h =>
      `<button class="small ghost" data-h="${C.esc(h)}">${C.esc(h)}</button>`).join("")}</div>
    <form id="f" class="row" style="gap:6px;position:sticky;bottom:0;background:var(--bg,#f6f8f8);padding:6px 0">
      <input id="q" placeholder="Poochiye… (Hinglish / मराठी / English)" maxlength="2000" autocomplete="off" style="flex:1">
      <button id="send">Bhejo</button>
    </form>`;
  if ($("sw")) $("sw").onclick = () => render(C);
  $("new").onclick = () => open(a, null);
  $("old").onclick = showOld;
  $("hints").querySelectorAll("[data-h]").forEach(b => b.onclick = () => { $("q").value = b.dataset.h; send(); });
  $("f").onsubmit = e => { e.preventDefault(); send(); };
  $("chat").addEventListener("click", e => {
    const l = e.target.closest("[data-uhid]");
    if (!l) return;
    e.preventDefault();
    const agentNow = AG, convNow = CONV;
    import("./timeline.js?v=" + (window.APP_VERSION || "")).then(m => m.render(C, l.dataset.uhid, () => {
      C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button><h2 style="margin:0 0 4px">💬 AI se baat</h2><div id="body"></div>`;
      $("bk").onclick = () => render(C);
      open(agentNow, convNow);
    }));
  });
  if (conv) loadConv(conv); else
    bubble("model", `Namaste${C.me.full_name ? " " + C.me.full_name : ""} 🙏 Main ${a.title} hoon. Aap mujhse hospital ke kaam ke baare mein pooch sakte hain.`);
}

async function showOld() {
  const box = $("oldlist");
  if (box.innerHTML) { box.innerHTML = ""; return; }
  box.innerHTML = `<div class="card">Loading…</div>`;
  const { data, error } = await C.sb.from("ai_conversations").select("id, title, updated_at, user_id")
    .eq("agent_id", AG.agent_id).eq("user_id", C.me.id).order("updated_at", { ascending: false }).limit(30);
  if (error) { box.innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  box.innerHTML = `<div class="card" style="max-height:260px;overflow:auto">${data.length ? data.map(c => `
    <button class="ghost full" style="text-align:left;margin:3px 0" data-c="${c.id}">💬 ${C.esc(c.title)}
      <small class="muted"> · ${new Date(c.updated_at).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</small></button>`).join("")
    : "<p class='muted' style='margin:0'>Abhi koi purani baat nahi.</p>"}</div>`;
  box.querySelectorAll("[data-c]").forEach(b => b.onclick = () => open(AG, b.dataset.c));
}

async function loadConv(id) {
  if ($("hints")) $("hints").style.display = "none";
  const { data, error } = await C.sb.from("ai_messages").select("role, content, provider, ms, tools, created_at")
    .eq("conversation_id", id).order("id");
  if (error) { bubble("model", "❌ " + error.message); return; }
  for (const m of data) bubble(m.role === "user" ? "user" : "model", m.content, m.role === "user" ? "" : meta(m.tools, m.provider, m.ms));
}

const meta = (tools, provider, ms) => {
  const chips = (tools || []).map(t => `<span class="badge" style="font-size:11px;margin:2px">${C.esc(TOOL[t] || t)}</span>`).join("");
  const who = provider ? `<span class="muted" style="font-size:11px;margin-left:4px">⚡ ${C.esc(provider)}${ms ? " · " + (ms / 1000).toFixed(1) + " sec" : ""}</span>` : "";
  return chips || who ? `<div style="margin-top:6px">${chips}${who}</div>` : "";
};

// patient names / UHIDs in AI answers become links that open the full patient timeline
function linkify(html, people = []) {
  const map = new Map();
  for (const p of people) { if (p.name) map.set(C.esc(p.name), p.uhid); if (p.uhid) map.set(C.esc(p.uhid), p.uhid); }
  const names = [...map.keys()].sort((x, y) => y.length - x.length).map(s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const re = new RegExp([...names, "\\b[A-Z]{2}\\d{8}\\b"].join("|"), "g");
  return html.replace(re, m => `<a href="#" data-uhid="${map.get(m) || m}" style="color:#0f766e;font-weight:600;text-decoration:underline">${m}</a>`)
    .replace(/(^|[^\w>])([6-9]\d{9})\b/g, (_, pre, ph) => `${pre}<a class="callbtn" style="padding:2px 8px;font-size:13px" href="tel:+91${ph}">📞 ${ph}</a>`);
}

function bubble(role, text, extra = "", people = []) {
  const me = role === "user";
  const d = document.createElement("div");
  d.style.cssText = `align-self:${me ? "flex-end" : "flex-start"};max-width:88%;padding:8px 12px;border-radius:14px;white-space:pre-wrap;line-height:1.4;` +
    (me ? "background:#0f766e;color:#fff;border-bottom-right-radius:4px" : "background:#fff;border:1px solid #e2e8f0;border-bottom-left-radius:4px");
  const body = C.esc(text).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
  d.innerHTML = (me ? body : linkify(body, people)) + extra;
  $("chat").appendChild(d);
  d.scrollIntoView({ behavior: "smooth", block: "end" });
  return d;
}

async function send() {
  const q = $("q").value.trim();
  if (!q || BUSY) return;
  BUSY = true; $("send").disabled = true; $("q").value = "";
  if ($("hints")) $("hints").style.display = "none";
  bubble("user", q);
  const wait = bubble("model", "⏳ Soch raha hoon…");
  const t0 = Date.now();
  const tick = setInterval(() => { wait.textContent = "⏳ Soch raha hoon… " + Math.round((Date.now() - t0) / 1000) + " sec"; }, 1000);
  try {
    const { data, error } = await C.sb.functions.invoke("agent-chat", { body: { agent: AG.agent_id, text: q, conversation_id: CONV } });
    let msg = error ? null : data;
    if (error) {
      try { msg = await error.context.json(); } catch { msg = { error: error.message }; }
    }
    clearInterval(tick); wait.remove();
    if (!msg || msg.error) {
      bubble("model", "❌ " + (msg?.error || "Kuch gadbad hui"));
      if (msg?.setup) bubble("model", "Doctor sahab: AI chalu karne ke liye Supabase mein AI key lagani hai.");
    } else {
      CONV = msg.conversation_id || CONV;
      bubble("model", msg.reply, meta(msg.tools, msg.provider, msg.ms), msg.patients || []);
    }
  } catch (e) {
    clearInterval(tick); wait.remove();
    bubble("model", "❌ Internet / server se baat nahi hui: " + e.message);
  }
  BUSY = false; $("send").disabled = false; $("q").focus();
}
