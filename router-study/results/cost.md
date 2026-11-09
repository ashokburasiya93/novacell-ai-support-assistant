# Router cost model

Volume: 150,000 messages a month (assumption). People cost $25/hour (assumption).

| Option | Per 1,000 messages | Running / month | Upkeep / month | One-off | 12-month total | Break-even volume vs this option |
|---|---|---|---|---|---|---|
| llm-120b | $0.1052 | $15.79 | $8.33 | $0 | $289.43 | 684,595 / month |
| llm-120b (cached prompt) | $0.0607 | $9.11 | $8.33 | $0 | $209.32 | 1,199,741 / month |
| llm-20b | $0.0540 | $8.10 | $8.33 | $0 | $197.15 | 1,353,033 / month |
| llm-20b (cached prompt) | $0.0317 | $4.76 | $8.33 | $0 | $157.10 | 2,354,199 / month |
| finetuned-minilm | $0.0023 | $0.35 | $33.33 | $550 | $954.21 | - |

Break-even = monthly volume at which the fine-tuned router's 12-month total (build + upkeep + hosting) equals the prompted option's. Token sources: llm-120b full run, llm-20b full run.
