# NovaCell Support Assistant (prototype)

A self-serve chat assistant that answers NovaCell's Tier-1 customer questions (slow or dropped data, unexpected charges, SIM/eSIM activation, roaming before travel, voice-call issues, account and app) in plain language, **grounded only in NovaCell's verified knowledge**: the public FAQ, resolved support tickets, the customer-safe parts of the technical guide, and the plan catalogue. When it cannot verify an answer it says so and hands off to 611 / live chat.

## How it works

```
question ─► input guardrails ─► BM25 retrieval ─► LLM (JSON) ─► output validators ─► answer + sources
            (emergency,          (103 chunks,      1. Groq gpt-oss-120b   (citations exist; numbers,
             injection, PII)      score < 3 =       2. Groq gpt-oss-20b    addresses and settings paths
                                  "I don't know")   3. OpenRouter Gemma 4  in cited sources; no promises,
                                                                           no internal terms)
```

| Piece | File | Notes |
|---|---|---|
| Knowledge base builder | `scripts/build_kb.py` | Chunks FAQ, tickets, PDF guide, plans into `kb/knowledge.json` with stable ids (FAQ-07, TK-009, GUIDE-4.3, PLAN-…). Drops agent-only guide sections and goodwill-credit sentences. |
| Retrieval | `lib/retrieval.js` | BM25 + telecom synonym list, max 3 chunks per source type, plan entries forced in for price questions. No embeddings: $0, deterministic. |
| Guardrails | `lib/guardrails.js` | Emergency reply, prompt-injection block, PII redaction (Luhn card check, passwords, PINs, IDs, emails), number grounding, promise and internal-term filters. |
| Orchestration | `lib/assistant.js` | Prompt, model chain (primary → secondary → fallback), one repair attempt, safe abstain. |
| API | `api/chat.js`, `api/health.js` | Vercel serverless functions. `/api/health` feeds the model badge. |
| UI | `public/index.html` | Single static page, mobile-friendly, light/dark. |
| Evals | `evals/` | `dev.json` (44 cases, used for tuning), `holdout.json` (v2, 30 cases, final gate, never tuned on), `holdout_v1.json` (first held-out set; it exposed vocabulary gaps, so it is now a regression set), `run.js`, results in `evals/results/`. |

Source priority when sources conflict: **Plan catalogue > Technical guide > FAQ > Past ticket**.

## Run locally

Requires Node 20+ (no npm dependencies) and, only to rebuild the knowledge base, Python 3 with `pdftotext` (poppler).

```bash
cp .env.example .env        # then put your GROQ_API_KEY and OPENROUTER_API_KEY in .env
node server.js              # http://localhost:3000
```

Rebuild the knowledge base after editing anything in `data/`:

```bash
python scripts/build_kb.py
```

Run the evals (calls the real models; paced for Groq's free tier, a full set takes ~15 minutes):

```bash
node evals/run.js dev
node evals/run.js holdout
```

The runner exits non-zero if any safety gate is below 100% or a quality target from the PRD is missed.

## Deploy to Vercel (free tier)

1. Import the repository in Vercel and set **Root Directory** to `app`. Framework preset: *Other*. No build command.
2. Add environment variables `GROQ_API_KEY` and `OPENROUTER_API_KEY` (optionally `PRIMARY_MODEL`, `SECONDARY_MODEL`, `FALLBACK_MODEL`).
3. Deploy. The page is public, needs no sign-in, and the header badge shows the live primary and fallback models.

Keys live only in Vercel's environment variables, never in the repo.

## Data: what we used and what we added

| Source | Records | Notes |
|---|---|---|
| `data/faq.csv` | 25 | Original public FAQ. |
| `data/faq_extended.csv` | 4 | **Synthetic, added by us**: eSIM activation, eSIM + physical SIM, pre-travel checklist, roaming bundle charges. Written only from facts already in the guide, tickets and FAQ. |
| `data/tickets.db` | 20 | 19 resolved + 1 escalated (TK-020, suspected account compromise; first missed by a `status='resolved'` filter, caught by the held-out eval). Encoding errors fixed; goodwill-credit / compensation sentences removed. |
| `data/telecom_guide.pdf` | 9 pages → 40 chunks | Marked "Internal Use Only". Excluded: SS7/Diameter, IRSF unbarring, SIM security keys, agent ID-verification checklist, account takeover, internal escalation, steering of roaming, billing internals; sentences describing agent tooling dropped. |
| `data/plans.json` | 14 | Plan catalogue (last updated 2026-06-01); pricing source of truth. |
| `evals/*.json` | 73 | **Synthetic** customer questions written by the PM. |

Data-quality findings (logged for the knowledge owner): the FAQ prices the EU roaming bundle at $15/day while the catalogue lists a $10/day International Day Pass; sources use "MyTelecom" and telecom.example.com rather than NovaCell; the FAQ has no eSIM entry.

All data is synthetic. Persona quotes, volumes and agent costs in the docs are assumptions and labelled as such.

## Model chain and free-tier limits

Groq's free tier caps `gpt-oss-120b` at 200k tokens a day (about 110 answers at ~1.8k tokens each). Running the evals hit that cap on 2 Nov 2026, and OpenRouter's free models were rate-limited upstream at the same moment, so the app briefly showed only the handoff message. The fix was a second Groq model with its own quota (`gpt-oss-20b`). Production needs a paid Groq tier; the cost sheet prices that.

## Privacy

Personal data is redacted before any model call. Chat text is never stored; the function logs only status, model, latency and token counts.
