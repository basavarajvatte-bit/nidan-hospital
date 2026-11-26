// Vatte Hospital OS — Phase 8: AI Chat (Sister AI / Reception AI)
// Talks to the 'agent-chat' server function. The AI only sees hospital data through tools that use
// this user's own login; patient names are hidden from the AI as codes. Chat is not saved on the server.
let C, AG = null, MSGS = [], BUSY = false, LIST = [];
const $ = id => document.getElementById(id);
const TOOL = { find_patient: "🔎 patient dhoonda", latest_vitals: "🩺 vitals dekhe", list_beds: "🛏️ bed list",
  "nurse__overdue_vitals": "⏰ baaki vitals", "operations__beds": "🛏️ bed sthiti", "followup__due": "📞 follow-up list",
  "followup__schedule": "✋ follow-up approval ko bheja", "operations__bed_status": "✋ bed badlav approval ko bheja",
  "reception__today": "🧾 aaj ka hisaab", "appointment__today": "📅 appointments" };
const HINTS = {
  nurse: ["Kis patient ke vitals baaki hain?", "Kitne bed khali hain?", "Aaj ke follow-up batao", "Dummy Ramesh ke aakhri vitals"],
  reception: ["Aaj ka hisaab batao", "Kitne bed khali hain?", "Aaj ki appointments", "Aaj ke follow-up kaun se hain?"]
};

export async function render(ctx) {
  C = ctx; MSGS = []; AG = null;
  C.app.innerHTML = `<button class="ghost small back" id="bk">← Wapas</button>
    <h2 style="margin:0 0 4px">💬 AI Chat</h2><div id="body"><div class="card">Loading…</div></div>`;
  $("bk").onclick = C.goHome;
  const { data, error } = await C.sb.from("ai_chat_agents").select("*");
  if (error) { $("body").innerHTML = `<div class="card msg err">${C.esc(error.message)}</div>`; return; }
  LIST = (data || []).filter(a => a.roles.includes(C.me.role));
  if (!LIST.length) { $("body").innerHTML = `<div class="card"><p class="muted">Aapke role ke liye abhi koi AI chat nahi hai. Agle phases mein aayegi.</p></div>`; return; }
  if (LIST.length === 1) return open(LIST[0]);
  $("body").innerHTML = `<p class="muted">Kisse baat karni hai?</p><div class="grid">${LIST.map(a => `
    <button class="tile" data-a="${a.agent_id}"><span class="ico">${a.agent_id === "nurse" ? "🩺" : "🧾"}</span>${C.esc(a.title)}
    <small>${a.agent_id === "nurse" ? "Vitals, bed, follow-up" : "Aaj ka hisaab, appointments, follow-up"}</small></button>`).join("")}</div>`;
  $("body").querySelectorAll("[data-a]").forEach(b => b.onclick = () => open(LIST.find(a => a.agent_id === b.dataset.a)));
}

function open(a) {
  AG = a; MSGS = [];
  $("body").innerHTML = `
    <div class="row" style="justify-content:space-between;margin-bottom:6px">
      <b>${a.agent_id === "nurse" ? "🩺" : "🧾"} ${C.esc(a.title)}</b>
      ${LIST.length > 1 ? `<button class="small ghost" id="sw">Badlo</button>` : ""}
    </div>
    <div class="card" style="background:#fffbeb;border-color:#fde68a;padding:8px 10px;font-size:13px">
      ⚠️ Ye AI hai — galti ho sakti hai. Diagnosis / dawa nahi deta, kuch approve nahi karta. Abhi sirf <b>dummy (nakli) patient</b> ke saath use karein.</div>
    <div id="chat" style="display:flex;flex-direction:column;gap:8px;margin:10px 0;min-height:200px"></div>
    <div class="row" id="hints" style="gap:6px;flex-wrap:wrap;margin-bottom:8px">${(HINTS[a.agent_id] || []).map(h =>
      `<button class="small ghost" data-h="${C.esc(h)}">${C.esc(h)}</button>`).join("")}</div>
    <form id="f" class="row" style="gap:6px;position:sticky;bottom:0;background:var(--bg,#f6f8f8);padding:6px 0">
      <input id="q" placeholder="Poochiye… (Hinglish / मराठी / English)" maxlength="2000" autocomplete="off" style="flex:1">
      <button id="send">Bhejo</button>
    </form>`;
  if ($("sw")) $("sw").onclick = () => render(C);
  $("hints").querySelectorAll("[data-h]").forEach(b => b.onclick = () => { $("q").value = b.dataset.h; send(); });
  $("f").onsubmit = e => { e.preventDefault(); send(); };
  bubble("model", `Namaste${C.me.full_name ? " " + C.me.full_name : ""} 🙏 Main ${a.title} hoon. Aap mujhse hospital ke kaam ke baare mein pooch sakte hain.`);
}

function bubble(role, text, extra = "") {
  const me = role === "user";
  const d = document.createElement("div");
  d.style.cssText = `align-self:${me ? "flex-end" : "flex-start"};max-width:88%;padding:8px 12px;border-radius:14px;white-space:pre-wrap;line-height:1.4;` +
    (me ? "background:#0f766e;color:#fff;border-bottom-right-radius:4px" : "background:#fff;border:1px solid #e2e8f0;border-bottom-left-radius:4px");
  d.innerHTML = C.esc(text).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>") + extra;
  $("chat").appendChild(d);
  d.scrollIntoView({ behavior: "smooth", block: "end" });
  return d;
}

async function send() {
  const q = $("q").value.trim();
  if (!q || BUSY) return;
  BUSY = true; $("send").disabled = true; $("q").value = "";
  if ($("hints")) $("hints").style.display = "none";
  MSGS.push({ role: "user", text: q });
  bubble("user", q);
  const wait = bubble("model", "⏳ Soch raha hoon…");
  try {
    const { data, error } = await C.sb.functions.invoke("agent-chat", { body: { agent: AG.agent_id, messages: MSGS.slice(-12) } });
    let msg = error ? null : data;
    if (error) {
      try { msg = await error.context.json(); } catch { msg = { error: error.message }; }
    }
    wait.remove();
    if (!msg || msg.error) {
      MSGS.pop();
      bubble("model", "❌ " + (msg?.error || "Kuch gadbad hui"));
      if (msg?.setup) bubble("model", "Doctor sahab: AI chalu karne ke liye ek baar Gemini key lagani hai (setup steps chat mein Claude ne diye hain).");
    } else {
      MSGS.push({ role: "model", text: msg.reply });
      const chips = (msg.tools || []).length ? `<div style="margin-top:6px">${msg.tools.map(t =>
        `<span class="badge" style="font-size:11px;margin:2px">${C.esc(TOOL[t] || t)}</span>`).join("")}</div>` : "";
      bubble("model", msg.reply, chips);
    }
  } catch (e) {
    wait.remove(); MSGS.pop();
    bubble("model", "❌ Internet / server se baat nahi hui: " + e.message);
  }
  BUSY = false; $("send").disabled = false; $("q").focus();
}
