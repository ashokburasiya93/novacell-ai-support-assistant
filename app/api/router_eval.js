// Runs the prompted-router arms of the build-vs-fine-tune study on the bundled eval messages.
// Disabled unless this is a preview deployment or ROUTER_EVAL_ENABLED=true, so production never exposes it.
// GET /api/router_eval?arm=120b|20b&split=test|hard&from=0&n=40&gap_ms=5000
// Response rows are compact: [id, predicted label, latency ms, input tokens, output tokens].
import { routeWithLLM, ROUTER_MODELS } from "../lib/router.js";
import MESSAGES from "../lib/router_eval_messages.js";

export const config = { maxDuration: 300 };

export default async function handler(req, res) {
  if (process.env.VERCEL_ENV !== "preview" && process.env.ROUTER_EVAL_ENABLED !== "true") {
    return res.status(404).json({ error: "not found" });
  }
  const { arm = "20b", split = "test" } = req.query || {};
  const model = ROUTER_MODELS[arm];
  const items = MESSAGES[split];
  if (!model || !items) return res.status(400).json({ error: "bad arm or split" });
  const from = Math.max(0, Number(req.query.from) || 0);
  const n = Math.min(80, Math.max(1, Number(req.query.n) || 10));
  // Free tier allows 8,000 tokens a minute; at ~620 tokens a call, a 5 s gap stays under it.
  const gapMs = Math.min(10000, Math.max(0, Number(req.query.gap_ms) || 0));
  const started = Date.now();
  const rows = [];
  let stopReason = null;
  for (const item of items.slice(from, from + n)) {
    if (Date.now() - started > 270000) {
      stopReason = "time budget";
      break;
    }
    const callStart = Date.now();
    try {
      const r = await routeWithLLM(item.text, model);
      rows.push([item.id, r.label, r.latencyMs, r.inTokens, r.outTokens]);
    } catch (e) {
      stopReason = String(e.message).slice(0, 160);
      break;
    }
    const spare = gapMs - (Date.now() - callStart);
    if (spare > 0) await new Promise((r) => setTimeout(r, spare));
  }
  console.log(JSON.stringify({ evt: "router_eval", arm, split, from, done: rows.length, stopReason }));
  res.status(200).json({ arm, model, split, from, next: from + rows.length, total: items.length, stopReason, rows });
}
