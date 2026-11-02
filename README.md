# NovaCell AI Support Assistant

An AI self-serve chat assistant for NovaCell (a ~4M-subscriber mobile operator) that answers Tier-1 customer questions in plain language, **grounded only in NovaCell's verified knowledge**: the public FAQ, resolved support tickets, the customer-safe parts of the technical guide and the plan catalogue. Every answer shows its sources. When it can't verify an answer, it says so and hands off to 611 / live chat.

- **Live app:** __LIVE_URL__ (no sign-in; the header shows the primary and fallback models)
- **AI opportunity map (Miro, public view):** https://miro.com/app/board/uXjVESvQ1ow=/
- **Models:** `openai/gpt-oss-120b` on Groq (primary), `google/gemma-4-31b-it` on OpenRouter (automatic fallback)

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

Eval results: [app/evals/results/dev.md](app/evals/results/dev.md) and [app/evals/results/holdout.md](app/evals/results/holdout.md).

## Eval summary

__EVAL_TABLE__

## Run it

See [app/README.md](app/README.md). In short: put `GROQ_API_KEY` and `OPENROUTER_API_KEY` in `app/.env`, then `node app/server.js`.

## Data note

The NovaCell dataset is synthetic. We added 4 FAQ entries (eSIM and travel gaps) and 74 eval questions, all labelled synthetic. Persona quotes, contact volumes and agent costs in the documents are assumptions, not real research.
