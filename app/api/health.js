import { MODELS, kbStats } from "../lib/assistant.js";

export default function handler(_req, res) {
  res.status(200).json({
    ok: true,
    models: MODELS,
    keys: { groq: !!process.env.GROQ_API_KEY, openrouter: !!process.env.OPENROUTER_API_KEY },
    kb: kbStats(),
  });
}
