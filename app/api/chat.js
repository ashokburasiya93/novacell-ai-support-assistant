import { answer } from "../lib/assistant.js";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "POST only" });
  }
  const body = typeof req.body === "string" ? JSON.parse(req.body || "{}") : req.body || {};
  const history = Array.isArray(body.history)
    ? body.history.filter((h) => h && ["user", "assistant"].includes(h.role) && typeof h.content === "string").slice(-4)
    : [];
  const result = await answer(String(body.message || ""), history);
  // No message text is logged: only the outcome, for monitoring.
  console.log(JSON.stringify({ evt: "chat", status: result.status, model: result.modelUsed?.model, ms: result.latencyMs, tokens: result.usage }));
  res.status(200).json(result);
}
