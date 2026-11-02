# NovaCell AI Support Assistant

An AI self-serve chat assistant for NovaCell (a ~4M-subscriber mobile operator) that answers Tier-1 customer questions in plain language, **grounded only in NovaCell's verified knowledge**: the public FAQ, resolved support tickets, the customer-safe parts of the technical guide and the plan catalogue. Every answer shows its sources. When it can't verify an answer, it says so and hands off to 611 / live chat.

- **Live app:** https://novacell-support-assistant.vercel.app (no sign-in; the header shows the primary and fallback models)
- **AI opportunity map (Miro, public view):** https://miro.com/app/board/uXjVESvQ1ow=/
- **Models:** `openai/gpt-oss-120b` on Groq (primary) → `openai/gpt-oss-20b` on Groq (secondary, separate quota) → `google/gemma-4-31b-it` on OpenRouter (fallback)

## The problem in one line

NovaCell doesn't lack answers, it lacks one place customers can trust: the fixes exist, but they're split across a 25-entry FAQ, an internal PDF guide and agent-only ticket history, and the sources contradict each other (EU roaming is $15/day in the FAQ and $10/day in the plan catalogue).

## Deliverables in this repo

| # | Deliverable | File |
|---|---|---|
| 1 | Problem discovery and user research worksheet | [docs/1. Problem Discovery and User Research - NovaCell.xlsx](docs/) |
| 2 | AI opportunity map (Excel + Miro import CSV; board linked above) | [docs/2. AI Opportunity Map - NovaCell.xlsx](docs/) |
| 3 | AI PRD with North Star and Metrics section | [docs/3. AI PRD - NovaCell Support Assistant.docx](docs/) |
| 4 | Cost estimation (measured tokens, labelled assumptions) | [docs/4. Cost Estimation - NovaCell.xlsx](docs/) |
| 5 | Working prototype + README | [app/](app/) · [app/README.md](app/README.md) |
| 6 | Presentation | [docs/6. Presentation - NovaCell Support Assistant.pptx](docs/) |

Eval results: [dev](app/evals/results/dev.md) · [held-out v2](app/evals/results/holdout.md) · [held-out v1](app/evals/results/holdout_v1.md) · [safety regression](app/evals/results/safety_regression.md).

Not in this repo by design: the demo video script and client meeting prep (deliverables 7-8), templates, and any API keys or `.env` files.

## Eval summary

| Set | Cases | Key facts | Citations | Retrieval | Abstention | Safety | Grounding | Models used |
|---|---|---|---|---|---|---|---|---|
| Dev (tuning) | 44 | 100% | 100% | 100% | 100% | 100% | 100% | gpt-oss-120b 36, gpt-oss-20b 6 |
| Held-out v1 → regression | 30 | 95% | 90% | 100% | 100% | 100% | 100% | gpt-oss-20b 25, gpt-oss-120b 2 |
| **Held-out v2 (final gate)** | 30 | 82% | 77% | 77% | 100% | 100% | 100% | gpt-oss-20b 25, gpt-oss-120b 2 |
| Safety regression | 27 | – | – | – | – | 100% | 100% | gpt-oss-20b 21, gpt-oss-120b 1 |

Targets (PRD section 11): key facts ≥ 85%, citations ≥ 90%, retrieval ≥ 90%, abstention ≥ 90%, safety and grounding 100%.

**Status (2 Nov 2026):** every safety and grounding gate passes on every set. The fresh held-out v2 set is **below target on answer coverage** (key facts, citations, retrieval): keyword search misses everyday phrasing such as "extra data" for add-on packs. Every miss failed safe ("I don't have verified information" plus a handoff), never an invented answer. Next step: a query-rewrite step before retrieval, then a new held-out v3, run on the primary model once its daily quota resets. Most v2 answers came from `gpt-oss-20b` because the evals had used up the primary's free 200k-token daily cap.

What the evals caught and we fixed along the way: an escalated account-compromise ticket missing from the knowledge base; a model inventing an APN and settings path (now every web address and settings path must appear in a cited source); and a backup model claiming "we have already processed a refund" (now a broader promise filter, and refund/credit/cancel requests always go to an agent).

## Run it

See [app/README.md](app/README.md). In short: put `GROQ_API_KEY` and `OPENROUTER_API_KEY` in `app/.env`, then `node app/server.js`.

## Data note

The NovaCell dataset is synthetic. We added 4 FAQ entries (eSIM and travel gaps) and 111 eval questions, all labelled synthetic. Persona quotes, contact volumes and agent costs in the documents are assumptions, not real research.
