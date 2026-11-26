// Vatte Hospital OS — Phase 8: AI chat (Sister AI / Reception AI)
// The AI can only use tools that go through the user's own login (RLS + agent_submit role/risk checks).
// Patient names / phones / UHIDs from tool results are replaced with codes (P1, P2…) before going to the AI,
// and put back in the reply, so the free AI model never sees them in tool data.
// The AI never diagnoses, prescribes or approves; record-changing jobs go to the approval queue.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const json = (b: unknown, s = 200) => new Response(JSON.stringify(b), { status: s, headers: { ...CORS, "Content-Type": "application/json" } });
const MODELS = [Deno.env.get("GEMINI_MODEL"), "gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.1-flash-lite"].filter(Boolean) as string[];

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
        if (typeof v === "string" && ["patient", "full_name", "name_of_patient"].includes(k)) o[k] = this.code(v, "P");
        else if (typeof v === "string" && k === "phone") o[k] = this.code(v, "PH");
        else if (typeof v === "string" && k === "uhid") o[k] = this.code(v, "U");
        else o[k] = this.deep(v);
      }
      return o;
    }
    return x;
  }
  text(s: string) { // names the user typed that we already know are masked
    let t = s;
    for (const [v, c] of [...this.map.entries()].sort((a, b) => b[0].length - a[0].length)) t = t.split(v).join(c);
    return t;
  }
  unmask(s: string) {
    return s.replace(/\b(PH|P|U)\d+\b/g, (c) => this.back.get(c) ?? c);
  }
}

// ---------- tools ----------
function toolDefs(ctx: any) {
  const T: any[] = [];
  const has = (t: string) => ctx.tools.includes(t);
  if (has("find_patient")) T.push({ name: "find_patient", description: "Patient ko naam, UHID ya phone se dhoondo. Patient ka id (patient_id) milta hai.",
    parameters: { type: "object", properties: { query: { type: "string", description: "naam / UHID / phone ka hissa" } }, required: ["query"] } });
  if (has("latest_vitals")) T.push({ name: "latest_vitals", description: "Ek patient ke aakhri 5 vitals (BP, pulse, temp, SpO2, saans). Pehle find_patient se patient_id lo.",
    parameters: { type: "object", properties: { patient_id: { type: "string" } }, required: ["patient_id"] } });
  if (has("list_beds")) T.push({ name: "list_beds", description: "Saare bed aur unka status (bed_id ke saath).", parameters: { type: "object", properties: {} } });
  for (const a of ctx.actions || []) {
    const id = a.id.replace(".", "__");
    if (a.id === "followup.schedule") T.push({ name: id, description: `${a.title}: ${a.description}. Approval queue mein jaata hai.`,
      parameters: { type: "object", properties: { patient_id: { type: "string" }, due_on: { type: "string", description: "YYYY-MM-DD" }, reason: { type: "string" } }, required: ["patient_id", "due_on"] } });
    else if (a.id === "operations.bed_status") T.push({ name: id, description: `${a.title}. Approval queue mein jaata hai.`,
      parameters: { type: "object", properties: { bed_id: { type: "string" }, status: { type: "string", enum: ["available", "cleaning", "blocked"] } }, required: ["bed_id", "status"] } });
    else if (a.kind === "check") T.push({ name: id, description: `${a.title}: ${a.description}`, parameters: { type: "object", properties: {} } });
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
  const who = agentId === "nurse" ? "Vatte Hospital ki AI Sister (nursing madadgaar)" : "Vatte Hospital ki AI Receptionist";
  const today = new Date().toLocaleDateString("en-CA", { timeZone: "Asia/Kolkata" });
  return `Aap ${who} ho. Aap staff (${ctx.role}) se baat kar rahe ho. Aaj ki date ${today} hai (India).
NIYAM:
- Jawab chhota, saaf, Hinglish (Roman Hindi) mein do. Agar staff Marathi ya English mein likhe to usi bhasha mein.
- Hospital ka koi bhi data sirf tools se lo. Andaaza ya banaya hua number kabhi mat do. Tool fail ho to saaf batao.
- Aap diagnosis nahi karte, dawa / dose nahi batate, doctor ka order nahi badalte. Aisa pooche to bolo "ye doctor tay karenge" aur zaroorat ho to doctor ko batane ko kaho.
- Khatarnaak vitals (BP 180+ ya 90 se kam, SpO2 92 se kam, pulse 130+ ya 50 se kam, temp 103F+) dikhe to turant doctor ko batane ko kaho.
- Record badalne wale kaam (follow-up lagana, bed status) sirf approval queue mein jaate hain — aap kabhi approve nahi karte, aur "ho gaya" tab tak mat bolo jab tak tool status "done" na de.
- Patient ka naam / phone codes (P1, PH1, U1) jaisa dikhega — wahi code jawab mein likho, app asli naam dikha dega. Code ka matlab mat batao.
- Kisi kaam ke liye patient_id ya bed_id chahiye to pehle find_patient / list_beds chalao; ek se zyada patient mile to staff se poochho kaun sa.
- Apne bare mein: aap ek AI ho, galti ho sakti hai; zaroori baat doctor se confirm karein.`;
}

async function gemini(key: string, body: any) {
  let last = "";
  for (const m of MODELS) {
    const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${m}:generateContent`, {
      method: "POST", headers: { "Content-Type": "application/json", "x-goog-api-key": key }, body: JSON.stringify(body),
    });
    if (r.ok) return await r.json();
    last = `${r.status} ${(await r.text()).slice(0, 300)}`;
    if (r.status === 404 || r.status === 400 && last.includes("not found")) continue; // model name not available → try next
    if (r.status === 429) throw new Error("AI ki muft seema abhi poori ho gayi (429). 1-2 minute baad phir poochein.");
    throw new Error("AI se jawab nahi aaya: " + last);
  }
  throw new Error("Koi AI model nahi mila: " + last);
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return json({ error: "POST only" }, 405);
  const auth = req.headers.get("Authorization") || "";
  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_ANON_KEY")!, { global: { headers: { Authorization: auth } } });
  let agent = "", used: string[] = [];
  try {
    const body = await req.json();
    agent = String(body.agent || "");
    const history: { role: string; text: string }[] = (body.messages || []).slice(-12);
    if (!history.length || history[history.length - 1].role !== "user") return json({ error: "Sawaal khaali hai" }, 400);
    if (history.some((m) => String(m.text || "").length > 2000)) return json({ error: "Sawaal bahut lamba hai (2000 akshar tak)" }, 400);

    const { data: ctx, error: e1 } = await sb.rpc("ai_chat_begin", { p_agent: agent });
    if (e1) return json({ error: e1.message }, 403);
    const key = Deno.env.get("GEMINI_API_KEY");
    if (!key) return json({ error: "AI key abhi nahi lagi. Doctor: Supabase → Edge Functions → Secrets mein GEMINI_API_KEY daalein.", setup: true }, 503);

    const mask = new Mask();
    const tools = toolDefs(ctx);
    const contents: any[] = history.map((m) => ({ role: m.role === "user" ? "user" : "model", parts: [{ text: mask.text(String(m.text || "")) }] }));
    const base = { systemInstruction: { parts: [{ text: systemPrompt(ctx, agent) }] }, tools: tools.length ? [{ functionDeclarations: tools }] : undefined,
                   generationConfig: { temperature: 0.2, maxOutputTokens: 800 } };
    let reply = "";
    for (let step = 0; step < 5; step++) {
      const out = await gemini(key, { ...base, contents });
      const parts = out?.candidates?.[0]?.content?.parts || [];
      const calls = parts.filter((p: any) => p.functionCall);
      if (!calls.length) { reply = parts.map((p: any) => p.text || "").join("").trim(); break; }
      contents.push({ role: "model", parts });
      const responses = [];
      for (const c of calls) {
        const name = c.functionCall.name; used.push(name);
        // the AI only ever sees codes, so turn codes back into real ids/names before running the tool
        const args = JSON.parse(mask.unmask(JSON.stringify(c.functionCall.args || {})));
        const res = await runTool(sb, ctx, name, args);
        responses.push({ functionResponse: { name, response: { content: mask.deep(res) } } });
      }
      contents.push({ role: "user", parts: responses });
    }
    if (!reply) reply = "Maaf kijiye, abhi jawab nahi bana paaya. Sawaal thoda saaf karke phir poochein.";
    await sb.rpc("ai_chat_end", { p_agent: agent, p_tools: used, p_ok: true });
    return json({ reply: mask.unmask(reply), tools: [...new Set(used)] });
  } catch (e) {
    if (agent) await sb.rpc("ai_chat_end", { p_agent: agent, p_tools: used, p_ok: false });
    return json({ error: String((e as Error).message || e) }, 500);
  }
});
