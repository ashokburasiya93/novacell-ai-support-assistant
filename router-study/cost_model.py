"""12-month cost of each router option, and the monthly volume at which fine-tuning pays for itself.

Usage: python3 router-study/cost_model.py   (writes results/cost.json and results/cost.md)

Token counts are measured: averaged from results/llm-*_test.json when present, otherwise from the
provisional live calls listed in PROVISIONAL_TOKENS. Everything marked ASSUMPTION is synthetic.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# Groq list prices per 1M tokens, Oct 2026 (morphllm.com/groq-pricing, citing the GroqCloud model docs).
PRICES = {"llm-120b": (0.15, 0.60), "llm-20b": (0.075, 0.30)}
CACHED_INPUT_DISCOUNT = 0.5  # Groq lists a 50% discount on cached input tokens; the router prompt is static.

# Measured on live preview calls, 8 Nov 2026 (24 calls on 120b, 5 on 20b) - replaced by full-run averages.
PROVISIONAL_TOKENS = {"llm-120b": (594.6, 22.5), "llm-20b": (594.0, 25.4)}

# Vercel Fluid compute list prices (vercel.com/pricing, 2026).
ACTIVE_CPU_PER_HOUR = 0.128
MEMORY_PER_GB_HOUR = 0.0106
INVOCATIONS_PER_MILLION = 0.60

A = {  # ASSUMPTIONS (synthetic, for the course project)
    "messages_per_month": 150_000,        # NovaCell cost sheet: 5,000 Tier-1 queries a day x 30
    "people_cost_per_hour": 25,           # blended PM / engineer cost, USD
    "labelling_hours": 6,                 # write and check ~560 labelled messages
    "build_hours": 16,                    # training script, export, hosting, eval gate in CI
    "retrain_hours_per_change": 4,        # new or changed intent: label ~40 messages, retrain, re-run evals
    "intent_changes_per_year": 4,
    "prompt_change_hours": 1,             # same change on the prompted router: edit prompt, re-run evals
    "cpu_seconds_per_message": 0.025,     # fine-tuned MiniLM on one vCPU (measured 6-7 ms on 4 threads)
    "function_memory_gb": 1.0,
    "cold_starts_per_day": 50,
    "cold_start_seconds": 2.0,            # load the ~90 MB model
    "training_compute_usd": 0.01,         # measured: 209 s active CPU for the whole sandbox run
}


def avg_tokens(arm):
    path = os.path.join(HERE, "results", f"{arm}_test.json")
    if os.path.exists(path):
        rows = [r for r in json.load(open(path)) if r.get("in_tokens")]
        if rows:
            return (sum(r["in_tokens"] for r in rows) / len(rows), sum(r["out_tokens"] for r in rows) / len(rows), "full run")
    i, o = PROVISIONAL_TOKENS[arm]
    return i, o, "provisional"


def llm_cost_per_message(arm, cached=False):
    pin, pout = PRICES[arm]
    tin, tout, _ = avg_tokens(arm)
    if cached:
        pin *= 1 - CACHED_INPUT_DISCOUNT
    return (tin * pin + tout * pout) / 1e6


def finetuned_running_per_month(volume):
    cpu_h = volume * A["cpu_seconds_per_message"] / 3600 + 30 * A["cold_starts_per_day"] * A["cold_start_seconds"] / 3600
    mem_gbh = cpu_h * A["function_memory_gb"]
    return cpu_h * ACTIVE_CPU_PER_HOUR + mem_gbh * MEMORY_PER_GB_HOUR + volume / 1e6 * INVOCATIONS_PER_MILLION


def main():
    v = A["messages_per_month"]
    rate = A["people_cost_per_hour"]
    ft_one_off = (A["labelling_hours"] + A["build_hours"]) * rate + A["training_compute_usd"]
    ft_maint_month = A["retrain_hours_per_change"] * A["intent_changes_per_year"] * rate / 12
    prompt_maint_month = A["prompt_change_hours"] * A["intent_changes_per_year"] * rate / 12
    ft_run = finetuned_running_per_month(v)

    rows = []
    for arm in ("llm-120b", "llm-20b"):
        for cached in (False, True):
            per = llm_cost_per_message(arm, cached)
            run = per * v
            rows.append({
                "option": arm + (" (cached prompt)" if cached else ""),
                "tokens_source": avg_tokens(arm)[2],
                "cost_per_1k_messages": round(per * 1000, 4),
                "running_per_month": round(run, 2),
                "maintenance_per_month": round(prompt_maint_month, 2),
                "one_off": 0,
                "total_12_months": round(12 * (run + prompt_maint_month), 2),
            })
    rows.append({
        "option": "finetuned-minilm",
        "tokens_source": "n/a",
        "cost_per_1k_messages": round(ft_run / v * 1000, 4),
        "running_per_month": round(ft_run, 2),
        "maintenance_per_month": round(ft_maint_month, 2),
        "one_off": round(ft_one_off, 2),
        "total_12_months": round(ft_one_off + 12 * (ft_run + ft_maint_month), 2),
    })

    # Break-even: monthly volume where fine-tuning's 12-month total equals each prompted option's.
    breakeven = {}
    for r in rows[:-1]:
        per_llm = r["cost_per_1k_messages"] / 1000
        per_ft = A["cpu_seconds_per_message"] / 3600 * (ACTIVE_CPU_PER_HOUR + A["function_memory_gb"] * MEMORY_PER_GB_HOUR) + INVOCATIONS_PER_MILLION / 1e6
        fixed_ft = ft_one_off + 12 * (ft_maint_month + finetuned_running_per_month(0))
        fixed_llm = 12 * prompt_maint_month
        saving_per_msg = per_llm - per_ft
        breakeven[r["option"]] = round((fixed_ft - fixed_llm) / (12 * saving_per_msg)) if saving_per_msg > 0 else None

    out = {"assumptions": A, "prices": PRICES, "rows": rows, "breakeven_messages_per_month": breakeven}
    json.dump(out, open(os.path.join(HERE, "results", "cost.json"), "w"), indent=1)

    md = ["# Router cost model", "",
          f"Volume: {v:,} messages a month (assumption). People cost ${rate}/hour (assumption).", "",
          "| Option | Per 1,000 messages | Running / month | Upkeep / month | One-off | 12-month total | Break-even volume vs this option |",
          "|---|---|---|---|---|---|---|"]
    for r in rows:
        be = breakeven.get(r["option"])
        md.append(f"| {r['option']} | ${r['cost_per_1k_messages']:.4f} | ${r['running_per_month']:.2f} | "
                  f"${r['maintenance_per_month']:.2f} | ${r['one_off']:.0f} | ${r['total_12_months']:.2f} | "
                  f"{'-' if r['option'] == 'finetuned-minilm' else (f'{be:,} / month' if be else 'never')} |")
    md += ["", "Break-even = monthly volume at which the fine-tuned router's 12-month total (build + upkeep + hosting) "
           "equals the prompted option's. Token sources: " + ", ".join(f"{a} {avg_tokens(a)[2]}" for a in PRICES) + "."]
    open(os.path.join(HERE, "results", "cost.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
