// Prompted intent router used by the build-vs-fine-tune study (router-study/).
// It is NOT wired into the live assistant: answer() in assistant.js is unchanged.

export const ROUTER_LABELS = ["data", "billing", "sim", "roaming", "calls", "account", "agent_action", "out_of_scope"];

export const ROUTER_PROMPT = `You route NovaCell mobile customer messages. Reply with JSON only: {"label":"<one label>"}.

Labels:
- data: mobile data, speed, balance, add-on data packs, hotspot/tethering, APN, 4G/5G
- billing: how bills, prices, fees, taxes, payments and autopay work in general
- sim: SIM or eSIM activation, PIN/PUK, lost or stolen phone blocking, unlocking, porting a number in, compatibility
- roaming: using the phone abroad, travel passes, roaming charges and settings
- calls: voice calls, voicemail, wifi calling, VoLTE, call quality, international calling rates
- account: MyTelecom app and online account: login, passwords, profile details, authorised users
- agent_action: the customer wants something DONE to or LOOKED UP on their own account (refund, credit, waive, cancel, change their plan, unblock, send a SIM, check their specific bill or usage, dispute a charge), or reports changes, charges or logins they did not make
- out_of_scope: anything not about NovaCell mobile service

Rules: a general "how/what/why" question is a topic label; a request to act on or inspect their own account is agent_action. Possible account compromise is always agent_action.

Examples:
"How do I check how much data I have left?" -> data
"my laptop won't connect to my phone hotspot" -> data
"How do I set up autopay?" -> billing
"What are premium SMS charges?" -> billing
"I lost my phone, how do I block my SIM?" -> sim
"how do I set up eSIM on iPhone" -> sim
"How much is the international day pass?" -> roaming
"My phone doesn't work since I landed in Spain" -> roaming
"Calls go straight to voicemail" -> calls
"How much do international calls cost?" -> calls
"I forgot my MyTelecom app password" -> account
"How do I add an authorised user?" -> account
"Please refund the $40 roaming charge on my bill" -> agent_action
"Someone changed my password and I didn't do it" -> agent_action
"What's the best Samsung phone to buy?" -> out_of_scope
"How do I fix a Python error?" -> out_of_scope`;

export const ROUTER_MODELS = { "120b": "openai/gpt-oss-120b", "20b": "openai/gpt-oss-20b" };

export async function routeWithLLM(text, model, { timeoutMs = 20000 } = {}) {
  const key = process.env.GROQ_API_KEY;
  if (!key) throw new Error("GROQ_API_KEY is not configured");
  const body = {
    model,
    messages: [
      { role: "system", content: ROUTER_PROMPT },
      { role: "user", content: String(text).slice(0, 500) },
    ],
    temperature: 0,
    max_tokens: 300,
    response_format: { type: "json_object" },
    reasoning_effort: "low",
  };
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  const t0 = Date.now();
  try {
    const send = () =>
      fetch("https://api.groq.com/openai/v1/chat/completions", {
        method: "POST",
        signal: ctrl.signal,
        headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    let res = await send();
    const wait = Number(res.headers.get("retry-after"));
    if (res.status === 429 && wait > 0 && wait <= 15) {
      await new Promise((r) => setTimeout(r, wait * 1000));
      res = await send();
    }
    if (!res.ok) {
      const err = new Error(`Groq HTTP ${res.status}: ${(await res.text()).slice(0, 200)}`);
      err.status = res.status;
      throw err;
    }
    const data = await res.json();
    const latencyMs = Date.now() - t0;
    let label = "invalid";
    try {
      const parsed = JSON.parse(data.choices?.[0]?.message?.content || "{}");
      if (ROUTER_LABELS.includes(parsed.label)) label = parsed.label;
    } catch {
      /* keep "invalid" */
    }
    return {
      label,
      latencyMs,
      inTokens: data.usage?.prompt_tokens ?? 0,
      outTokens: data.usage?.completion_tokens ?? 0,
    };
  } finally {
    clearTimeout(timer);
  }
}
