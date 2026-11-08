# Router cost model

Volume: 150,000 messages a month (assumption). People cost $25/hour (assumption).

| Option | Per 1,000 messages | Running / month | Upkeep / month | One-off | 12-month total | Break-even volume vs this option |
|---|---|---|---|---|---|---|
| llm-120b | $0.1027 | $15.40 | $8.33 | $0 | $284.84 | 701,517 / month |
| llm-120b (cached prompt) | $0.0581 | $8.71 | $8.33 | $0 | $204.57 | 1,254,913 / month |
| llm-20b | $0.0522 | $7.83 | $8.33 | $0 | $193.91 | 1,401,129 / month |
| llm-20b (cached prompt) | $0.0299 | $4.48 | $8.33 | $0 | $153.81 | 2,503,738 / month |
| finetuned-minilm | $0.0023 | $0.35 | $33.33 | $550 | $954.21 | - |

Break-even = monthly volume at which the fine-tuned router's 12-month total (build + upkeep + hosting) equals the prompted option's. Token sources: llm-120b provisional, llm-20b provisional.
