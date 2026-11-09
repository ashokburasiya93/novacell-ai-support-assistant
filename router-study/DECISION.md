# Decision: keep the prompted router, do not fine-tune (yet)

**Question.** NovaCell's support assistant sorts each message into one of 8 intents (data, billing, SIM, roaming, calls, account, agent action, out of scope) before it answers. Today a prompted LLM does this. Would a small fine-tuned classifier be cheaper and as accurate?

**Decision.** Keep the prompted `gpt-oss-120b` router. Revisit fine-tuning if volume passes about 700,000 messages a month, or if the routing step must answer in under 100 ms.

## What we compared

All four routers were scored on the same two sets, which none of them saw in training or in their prompt:

- **Test (160):** clean, typical questions, 20 per intent.
- **Hard (80):** real-world style: typos, slang, long rambling messages, and questions that sit between two intents.

The prompted routers ran live on Groq through a preview deployment on 9 Nov 2026. The fine-tuned MiniLM (all-MiniLM-L6-v2, 320 training messages, 12 epochs, 35 s on 4 CPU threads) and the TF-IDF baseline ran in a Vercel Sandbox.

| Router | Test accuracy | Hard accuracy | Agent-action recall (test / hard) | Typical / slow response | 12-month cost at 150k messages a month |
|---|---|---|---|---|---|
| Prompted gpt-oss-120b | 93.8% | **98.8%** | 95% / **100%** | 0.4 s / 1.8 s | **$289** ($209 with prompt caching) |
| Prompted gpt-oss-20b | 88.8% | 85.0% | 100% / 100% | 0.4 s / 1.9 s | $197 ($157 with caching) |
| Fine-tuned MiniLM | **95.6%** | 88.8% | 95% / 90% | **6 ms / 7 ms** | $954 |
| TF-IDF + logistic regression | 83.8% | 75.0% | 80% / 70% | 2 ms | not costed (accuracy too low) |

Agent-action recall matters most: a missed agent-action message is a customer who asked for a refund, cancellation or SIM block and got an FAQ answer instead.

## Why the prompted router wins

1. **It holds up on messy messages.** Fine-tuning won by 1.8 points on clean questions but lost by 10 points on the hard set. The fine-tuned model learned the wording of 320 tidy examples; the LLM understands "my sim is blocked, unblock it" as an action, not a SIM question. Real chat traffic looks more like the hard set.
2. **It is cheaper at NovaCell's volume.** The fine-tuned model costs almost nothing to run ($0.35 a month) but about $550 to build and label, and $33 a month to retrain for each intent change. The prompted router's change is a prompt edit. Fine-tuning only becomes cheaper above about 685,000 messages a month against 120b, and about 1.35 million against 20b.
3. **Latency is not the bottleneck.** Routing adds about 0.4 s to a reply that already takes 1–3 s to generate. The fine-tuned model's 6 ms only matters if routing must happen on every keystroke or on-device.

## Why not the cheaper 20b model

It never missed an agent action, but it got there by over-routing: 9 account questions and several billing and SIM questions went to the human-agent queue. At 150,000 messages a month, its 88.8% accuracy means about 17,000 misrouted chats a month, many of them landing on agents. That costs far more in agent time than the $90 a year it saves.

## Errors worth knowing

- **Prompted 120b (10 test errors, 1 hard error):** 5 of the 10 test errors were account questions sent to agent action, which is the safe direction. It missed one agent action: "how much data did I use last Tuesday on my line" was routed as a data question. The fine-tuned model missed the same message, so the intent definition needs a clearer example.
- **Fine-tuned MiniLM (7 test, 9 hard):** it missed "my sim is blocked, unblock it" (routed to SIM) and confused calls, roaming and data on short or slangy messages ("my phone only says SOS", "how much to ring my mum in Kerala").

Full error lists are in `results/summary.md`; costs and assumptions are in `results/cost.md`.

## What would change the decision

- **Volume above ~700k messages a month:** at that point the fine-tuned router is cheaper. Before switching, add 100–200 messy training examples and re-run the hard set; it must reach at least 95% hard accuracy and 100% agent-action recall.
- **A routing budget under 100 ms:** try a hybrid. The fine-tuned model routes when it is confident, and low-confidence messages go to the LLM. This was not tested here.
- **Groq price or quota changes:** re-run `cost_model.py` with the new prices.

## Limits of this study

- The messages are synthetic, written to mirror NovaCell's FAQ and tickets. The hard set is the closest thing to real traffic, but it is only 80 messages, so one error moves its accuracy by 1.25 points.
- Each prompted router ran once. LLM output can vary between runs.
- Costs include people time at an assumed $25 an hour. Every assumption is labelled in `cost_model.py`.

## Reproduce

```bash
python3 router-study/train_tfidf.py
python3 router-study/finetune_minilm.py          # CPU, about 1 minute
python3 router-study/run_llm_arms.py <preview URL> 120b
python3 router-study/run_llm_arms.py <preview URL> 20b
python3 router-study/score.py
python3 router-study/cost_model.py
```
