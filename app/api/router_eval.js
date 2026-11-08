// Runs the prompted-router arms of the build-vs-fine-tune study on the bundled eval messages.
// Disabled unless this is a preview deployment or ROUTER_EVAL_ENABLED=true, so production never exposes it.
// GET /api/router_eval?arm=120b|20b&split=test|hard&from=0&n=10
import { routeWithLLM, ROUTER_MODELS } from "../lib/router.js";
import MESSAGES from "../lib/router_eval_messages.js";

export default async function handler(req, res) {
  if (process.env.VERCEL_ENV !== "preview" && process.env.ROUTER_EVAL_ENABLED !== "true") {
    return res.status(404).json({ error: "not found" });
  }
  const { arm = "20b", split = "test" } = req.query || {};
  const model = ROUTER_MODELS[arm];
  const items = MESSAGES[split];
  if (!model || !items) return res.status(400).json({ error: "bad arm or split" });
  const from = Math.max(0, Number(req.query.from) || 0);
  const n = Math.min(25, Math.max(1, Number(req.query.n) || 10));
  const started = Date.now();
  const out = [];
  let stopReason = null;
  for (const item of items.slice(from, from + n)) {
    if (Date.now() - started > 45000) {
      stopReason = "time budget";
      break;
    }
    try {
      const r = await routeWithLLM(item.text, model);
      out.push({ id: item.id, pred: r.label, latency_ms: r.latencyMs, in_tokens: r.inTokens, out_tokens: r.outTokens, model });
    } catch (e) {
      stopReason = String(e.message).slice(0, 200);
      break;
    }
  }
  console.log(JSON.stringify({ evt: "router_eval", arm, split, from, done: out.length, stopReason }));
  res.status(200).json({ arm, split, from, next: from + out.length, total: items.length, stopReason, results: out });
}
