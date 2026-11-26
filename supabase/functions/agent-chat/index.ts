// Vatte Hospital OS — Phase 8: AI chat with every department agent (Sister, Reception, Lab, Pharmacy, Accounts, Boss…)
// • Up to 3 free AIs race each other: AI-1 starts at once; if no answer in 4 s, AI-2 also starts; 4 s later AI-3.
//   The first good answer wins and the others are stopped. If one fails, the next starts immediately.
// • The AI can only use tools that go through the user's own login (RLS + agent_submit role/risk checks).
// • Patient names / phones / UHIDs in tool results are replaced with codes (P1, PH1, U1) before going to any AI,
//   and put back in the reply.
// • Every question + answer is saved in ai_conversations / ai_messages (the hospital's own database).
// • The AI never diagnoses, prescribes or approves; record-changing jobs go to the approval queue.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const json = (b: unknown, s = 200) => new Response(JSON.stringify(b), { status: s, headers: { ...CORS, "Content-Type": "application/json" } });
const env = (n: string) => {
  const all = Deno.env.toObject();
  const k = Object.keys(all).find((x) => x.trim().toUpperCase() === n);
  return k ? all[k].trim() : "";
};
const HEDGE_MS = 4000, STEP_TIMEOUT_MS = 30000;

// ---------- neutral message format ----------
type Call = { id: string; name: string; args: any; sig?: string };
type Msg = { role: "user" | "assistant" | "tool"; text?: string; calls?: Call[]; id?: string; name?: string; result?: any };
const newId = () => Array.from(crypto.getRandomValues(new Uint8Array(9)), (b) => "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"[b % 62]).join("");

// ---------- pseudonymisation ----------
class Mask {
  map = new Map<string, string>(); back = new Map<string, string>(); n = 0;
  code(v: string, kind: string) {
    if (!v) return v;
    if (!this.map.has(v)) { const c = `${kind}${++this.n}`; this.map.set(v, c); this.back.set(c, v); }
    return this.map.get(v)!;
  }
  deep(x: any): any {
    if (Array.isArray(x)) return x.map((y) => this.deep(y));
    if (x && typeof x === "object") {
      const o: any = {};
      for (const [k, v] of Object.entries(x)) {
        if (typeof v === "string" && ["patient", "full_name"].includes(k)) o[k] = this.code(v, "P");
        else if (typeof v === "string" && k === "phone") o[k] = this.code(v, "PH");
        else if (typeof v === "string" && k === "uhid") o[k] = this.code(v, "U");
        else o[k] = this.deep(v);
      }
      return o;
    }
    return x;
  }
  text(s: string) {
    let t = s;
    for (const [v, c] of [...this.map.entries()].sort((a, b) => b[0].length - a[0].length)) t = t.split(v).join(c);
    return t;
  }
  unmask(s: string) { return s.replace(/\b(PH|P|U)\d+\b/g, (c) => this.back.get(c) ?? c); }
}

// ---------- tools ----------
function toolDefs(ctx: any) {
  const T: any[] = [];
  const has = (t: string) => ctx.tools.includes(t);
  const obj = (props: any = {}, req: string[] = []) => ({ type: "object", properties: props, ...(req.length ? { required: req } : {}) });
  if (has("find_patient")) T.push({ name: "find_patient", description: "Patient ko naam, UHID ya phone se dhoondo. patient_id milta hai.", parameters: obj({ query: { type: "string", description: "naam / UHID / phone ka hissa" } }, ["query"]) });
  if (has("latest_vitals")) T.push({ name: "latest_vitals", description: "Ek patient ke aakhri 5 vitals. Pehle find_patient se patient_id lo.", parameters: obj({ patient_id: { type: "string" } }, ["patient_id"]) });
  if (has("list_beds")) T.push({ name: "list_beds", description: "Saare bed aur unka status (bed_id ke saath).", parameters: obj() });
  for (const a of ctx.actions || []) {
    const id = a.id.replace(".", "__");
    if (a.id === "followup.schedule") T.push({ name: id, description: `${a.title}: ${a.description}. Approval queue mein jaata hai.`,
      parameters: obj({ patient_id: { type: "string" }, due_on: { type: "string", description: "YYYY-MM-DD" }, reason: { type: "string" } }, ["patient_id", "due_on"]) });
    else if (a.id === "operations.bed_status") T.push({ name: id, description: `${a.title}. Approval queue mein jaata hai.`,
      parameters: obj({ bed_id: { type: "string" }, status: { type: "string", enum: ["available", "cleaning", "blocked"] } }, ["bed_id", "status"]) });
    else if (a.kind === "check") T.push({ name: id, description: `${a.title}: ${a.description}`, parameters: obj() });
  }
  return T;
}

async function runTool(sb: any, ctx: any, name: string, args: any) {
  if (name === "find_patient") {
    const q = String(args.query || "").replace(/[%,()"\\*]/g, "").trim();
    if (q.length < 2) return { error: "Kam se kam 2 akshar do" };
    const { data, error } = await sb.from("patients").select("id, uhid, full_name, gender, age_years, phone")
      .or(`full_name.ilike."%${q}%",uhid.ilike."%${q}%",phone.ilike."%${q}%"`).limit(5);
    if (error) return { error: error.message };
    return { patients: (data || []).map((p: any) => ({ patient_id: p.id, patient: p.full_name, uhid: p.uhid, phone: p.phone, gender: p.gender, age: p.age_years })) };
  }
  if (name === "latest_vitals") {
    const { data, error } = await sb.from("vitals").select("bp_systolic, bp_diastolic, pulse, temperature_f, spo2, resp_rate, recorded_at")
      .eq("patient_id", args.patient_id).order("recorded_at", { ascending: false }).limit(5);
    if (error) return { error: error.message };
    return { vitals: data };
  }
  if (name === "list_beds") {
    const { data, error } = await sb.from("beds").select("id, label, status, rooms(name)").order("label");
    if (error) return { error: error.message };
    return { beds: (data || []).map((b: any) => ({ bed_id: b.id, bed: b.label, room: b.rooms?.name, status: b.status })) };
  }
  const action = name.replace("__", ".");
  if (!(ctx.actions || []).some((a: any) => a.id === action)) return { error: "Ye kaam aapke role ke liye nahi" };
  const { data, error } = await sb.rpc("agent_submit", { p_action: action, p_input: args || {} });
  if (error) return { error: error.message };
  return { status: data.status, summary: data.summary ?? (data.status === "waiting_approval" ? "Approval ke liye bhej diya (Doctor/Admin dekhenge)" : null),
           error: data.error, result: data.result?.items };
}

function systemPrompt(ctx: any, agentId: string) {
  const who = `Vatte Hospital ka "${ctx.title}" (${ctx.department} department ka AI madadgaar; kaam: ${ctx.about})`;
  const today = new Date().toLocaleDateString("en-CA", { timeZone: "Asia/Kolkata" });
  const extra = agentId === "boss"
    ? "\n- Aap Boss AI ho: doctor ko poore hospital ki sthiti batate ho. Zaroorat ho to boss__daily_report ya alag department ke check chalao, aur sabse zaroori baat pehle batao."
    : "";
  return `Aap ${who} ho. Aap staff (${ctx.role}) se baat kar rahe ho. Aaj ki date ${today} hai (India).
NIYAM:
- Jawab chhota, saaf, Hinglish (Roman Hindi) mein do. Staff Marathi ya English mein likhe to usi bhasha mein.
- Hospital ka koi bhi data sirf tools se lo. Andaaza ya banaya hua number kabhi mat do. Tool fail ho to saaf batao.
- Jo kaam aapke tools mein nahi hai, uske liye saaf bolo ki ye abhi aapke paas nahi hai (aage ke phases mein aayega) — kuch banao mat.
- Aap diagnosis nahi karte, dawa / dose nahi batate, doctor ka order nahi badalte. Aisa pooche to bolo "ye doctor tay karenge".
- Khatarnaak vitals (BP 180+ ya 90 se kam, SpO2 92 se kam, pulse 130+ ya 50 se kam, temp 103F+) dikhe to turant doctor ko batane ko kaho.
- Record badalne wale kaam sirf approval queue mein jaate hain — aap approve nahi karte; "ho gaya" tabhi bolo jab tool status "done" ho.
- Patient ka naam / phone / UHID codes (P1, PH1, U1) mein dikhega — jawab mein wahi code likho, app asli naam dikha dega.
- patient_id ya bed_id chahiye to pehle find_patient / list_beds chalao; ek se zyada patient mile to staff se poochho kaun sa.
- Aap AI ho, galti ho sakti hai; zaroori baat doctor se confirm karwayein.${extra}`;
}

// ---------- providers ----------
function toOpenAI(sys: string, msgs: Msg[]) {
  const out: any[] = [{ role: "system", content: sys }];
  for (const m of msgs) {
    if (m.role === "user") out.push({ role: "user", content: m.text || "" });
    else if (m.role === "assistant") out.push(m.calls?.length
      ? { role: "assistant", content: m.text || "", tool_calls: m.calls.map((c) => ({ id: c.id, type: "function", function: { name: c.name, arguments: JSON.stringify(c.args || {}) } })) }
      : { role: "assistant", content: m.text || "" });
    else out.push({ role: "tool", tool_call_id: m.id, name: m.name, content: JSON.stringify(m.result) });
  }
  return out;
}
function toGemini(msgs: Msg[]) {
  const out: any[] = [];
  for (const m of msgs) {
    if (m.role === "user") out.push({ role: "user", parts: [{ text: m.text || "" }] });
    else if (m.role === "assistant") {
      const parts: any[] = [];
      if (m.text) parts.push({ text: m.text });
      for (const c of m.calls || []) parts.push({ functionCall: { name: c.name, args: c.args || {} }, thoughtSignature: c.sig || "skip_thought_signature_validator" });
      out.push({ role: "model", parts });
    } else {
      const part = { functionResponse: { name: m.name, response: { content: m.result } } };
      const last = out[out.length - 1];
      if (last && last.role === "user" && last.parts[0]?.functionResponse) last.parts.push(part); else out.push({ role: "user", parts: [part] });
    }
  }
  return out;
}

async function openAICompat(url: string, key: string, model: string, extra: any, sys: string, msgs: Msg[], tools: any[], signal: AbortSignal) {
  const r = await fetch(url, {
    method: "POST", signal, headers: { "Content-Type": "application/json", Authorization: `Bearer ${key}` },
    body: JSON.stringify({ model, messages: toOpenAI(sys, msgs), temperature: 0.2, max_tokens: 800, ...extra,
      ...(tools.length ? { tools: tools.map((t) => ({ type: "function", function: t })), tool_choice: "auto" } : {}) }),
  });
  if (!r.ok) throw new Error(`${r.status} ${(await r.text()).slice(0, 160)}`);
  const d = await r.json();
  const m = d.choices?.[0]?.message || {};
  const calls: Call[] = (m.tool_calls || []).map((c: any) => {
    let args = {}; try { args = JSON.parse(c.function?.arguments || "{}"); } catch { /* keep {} */ }
    return { id: newId(), name: c.function?.name, args };
  });
  return { text: String(m.content || "").trim(), calls };
}

async function geminiCall(key: string, sys: string, msgs: Msg[], tools: any[], signal: AbortSignal) {
  const models = [env("GEMINI_MODEL"), "gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.1-flash-lite"].filter(Boolean);
  let last = "";
  for (const model of models) {
    const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
      method: "POST", signal, headers: { "Content-Type": "application/json", "x-goog-api-key": key },
      body: JSON.stringify({ systemInstruction: { parts: [{ text: sys }] }, contents: toGemini(msgs),
        ...(tools.length ? { tools: [{ functionDeclarations: tools }] } : {}), generationConfig: { temperature: 0.2, maxOutputTokens: 800 } }),
    });
    if (r.ok) {
      const d = await r.json();
      const parts = d?.candidates?.[0]?.content?.parts || [];
      return {
        text: parts.filter((p: any) => p.text && !p.thought).map((p: any) => p.text).join("").trim(),
        calls: parts.filter((p: any) => p.functionCall).map((p: any) => ({ id: newId(), name: p.functionCall.name, args: p.functionCall.args || {}, sig: p.thoughtSignature })),
      };
    }
    last = `${r.status} ${(await r.text()).slice(0, 160)}`;
    if (r.status === 404) continue;
    throw new Error(last);
  }
  throw new Error("model nahi mila: " + last);
}

type Provider = { name: string; call: (sys: string, msgs: Msg[], tools: any[], s: AbortSignal) => Promise<{ text: string; calls: Call[] }> };
function providers(): Provider[] {
  const P: Provider[] = [];
  const groq = env("GROQ_API_KEY"), gem = env("GEMINI_API_KEY"), mis = env("MISTRAL_API_KEY");
  if (groq) P.push({ name: "Groq", call: (s, m, t, sig) => {
    const model = env("GROQ_MODEL") || "openai/gpt-oss-120b";
    return openAICompat("https://api.groq.com/openai/v1/chat/completions", groq, model, model.includes("gpt-oss") ? { reasoning_effort: "low" } : {}, s, m, t, sig);
  } });
  if (gem) P.push({ name: "Gemini", call: (s, m, t, sig) => geminiCall(gem, s, m, t, sig) });
  if (mis) P.push({ name: "Mistral", call: (s, m, t, sig) =>
    openAICompat("https://api.mistral.ai/v1/chat/completions", mis, env("MISTRAL_MODEL") || "mistral-small-latest", {}, s, m, t, sig) });
  return P;
}

// staggered race: AI-1 now, AI-2 after 4 s (or at once if AI-1 fails), AI-3 after 8 s…; first good answer wins
function race(P: Provider[], sys: string, msgs: Msg[], tools: any[]) {
  return new Promise<{ text: string; calls: Call[]; provider: string }>((resolve, reject) => {
    const ctrls: AbortController[] = []; const errs: string[] = [];
    let next = 0, failed = 0, done = false;
    let timer = 0, cap = 0;
    const finish = () => { done = true; clearInterval(timer); clearTimeout(cap); ctrls.forEach((c) => c.abort()); };
    const start = () => {
      if (done || next >= P.length) return;
      const p = P[next++]; const ac = new AbortController(); ctrls.push(ac);
      p.call(sys, msgs, tools, ac.signal).then((r) => {
        if (done) return;
        if (!r.text && !r.calls.length) throw new Error("khaali jawab");
        finish(); resolve({ ...r, provider: p.name });
      }).catch((e) => {
        if (done) return;
        errs.push(`${p.name}: ${String(e?.message || e).slice(0, 120)}`);
        if (++failed >= P.length) { finish(); reject(new Error(errs.join(" | "))); } else start();
      });
    };
    timer = setInterval(start, HEDGE_MS);
    cap = setTimeout(() => { if (!done) { finish(); reject(new Error("Sab AI bahut der laga rahe (30 sec). " + errs.join(" | "))); } }, STEP_TIMEOUT_MS);
    start();
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return json({ error: "POST only" }, 405);
  const auth = req.headers.get("Authorization") || "";
  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_ANON_KEY")!, { global: { headers: { Authorization: auth } } });
  let agent = "";
  const used: string[] = [];
  try {
    const body = await req.json();
    agent = String(body.agent || "");
    const question = String(body.text || "").trim();
    let convId: string | null = body.conversation_id || null;
    if (!question) return json({ error: "Sawaal khaali hai" }, 400);
    if (question.length > 2000) return json({ error: "Sawaal bahut lamba hai (2000 akshar tak)" }, 400);

    const { data: ctx, error: e1 } = await sb.rpc("ai_chat_begin", { p_agent: agent });
    if (e1) return json({ error: e1.message }, 403);
    const P = providers();
    if (!P.length) return json({ error: "Koi AI key nahi lagi. Doctor: Supabase → Edge Functions → Secrets mein GEMINI_API_KEY / GROQ_API_KEY daalein.", setup: true }, 503);
    const { data: u } = await sb.auth.getUser();
    const uid = u?.user?.id;

    // previous conversation (only the caller's own) → last 12 messages as memory
    let history: Msg[] = [];
    if (convId) {
      const { data: c } = await sb.from("ai_conversations").select("id, user_id, agent_id").eq("id", convId).maybeSingle();
      if (!c || c.user_id !== uid || c.agent_id !== agent) convId = null;
      else {
        const { data: old } = await sb.from("ai_messages").select("role, content").eq("conversation_id", convId).order("id", { ascending: false }).limit(12);
        history = (old || []).reverse().map((m: any) => ({ role: m.role, text: m.content }));
      }
    }

    const mask = new Mask();
    const sys = systemPrompt(ctx, agent);
    const tools = toolDefs(ctx);
    const msgs: Msg[] = [...history, { role: "user" as const, text: question }].map((m) => ({ ...m, text: mask.text(m.text || "") }));
    let reply = "", provider = "";
    const tStart = Date.now();
    for (let step = 0; step < 5; step++) {
      const r = await race(P, sys, msgs, tools);
      provider = r.provider;
      if (!r.calls.length) { reply = r.text; break; }
      msgs.push({ role: "assistant", text: r.text, calls: r.calls });
      for (const c of r.calls) {
        used.push(c.name);
        const args = JSON.parse(mask.unmask(JSON.stringify(c.args || {})));
        const res = await runTool(sb, ctx, c.name, args);
        msgs.push({ role: "tool", id: c.id, name: c.name, result: mask.deep(res) });
      }
    }
    const totalMs = Date.now() - tStart;
    if (!reply) reply = "Maaf kijiye, abhi jawab nahi bana paaya. Sawaal thoda saaf karke phir poochein.";
    reply = mask.unmask(reply).slice(0, 7900);

    // save the conversation
    if (!convId) {
      const { data: c, error: ec } = await sb.from("ai_conversations").insert({ agent_id: agent, title: question.slice(0, 60) }).select("id").single();
      if (ec) throw new Error("Chat save nahi hui: " + ec.message);
      convId = c.id;
    } else {
      await sb.from("ai_conversations").update({ updated_at: new Date().toISOString() }).eq("id", convId);
    }
    const { error: em } = await sb.from("ai_messages").insert([
      { conversation_id: convId, role: "user", content: question, provider: null, ms: null, tools: [] },
      { conversation_id: convId, role: "assistant", content: reply, provider, ms: totalMs, tools: [...new Set(used)].slice(0, 10) },
    ]);
    if (em) throw new Error("Chat save nahi hui: " + em.message);

    await sb.rpc("ai_chat_end", { p_agent: agent, p_tools: used, p_ok: true });
    return json({ reply, tools: [...new Set(used)], provider, ms: totalMs, conversation_id: convId });
  } catch (e) {
    if (agent) await sb.rpc("ai_chat_end", { p_agent: agent, p_tools: used, p_ok: false });
    return json({ error: String((e as Error).message || e) }, 500);
  }
});
