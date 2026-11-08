"""Score every arm's predictions on the test and hard sets and write results/summary.json + results/summary.md.

Prediction files: router-study/results/<arm>_<split>.json, a list of
{"id", "pred", "latency_ms", "in_tokens", "out_tokens"} (tokens 0 for local models).

Usage: python3 router-study/score.py
"""
import glob
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
LABELS = ["data", "billing", "sim", "roaming", "calls", "account", "agent_action", "out_of_scope"]
ARM_ORDER = ["llm-120b", "llm-20b", "finetuned-minilm", "tfidf-logreg"]


def load(name):
    with open(os.path.join(HERE, "data", f"{name}.json")) as f:
        return {r["id"]: r for r in json.load(f)}


def pct(x):
    return round(100 * x, 1)


def percentile(values, p):
    if not values:
        return None
    v = sorted(values)
    k = max(0, min(len(v) - 1, int(round(p / 100 * (len(v) - 1)))))
    return v[k]


def score(gold, preds):
    by_id = {p["id"]: p for p in preds}
    missing = [i for i in gold if i not in by_id]
    if missing:
        raise SystemExit(f"{len(missing)} predictions missing, e.g. {missing[:3]}")
    y = [gold[i]["label"] for i in gold]
    p = [by_id[i]["pred"] for i in gold]
    acc = sum(a == b for a, b in zip(y, p)) / len(y)
    f1s = []
    per = {}
    for l in LABELS:
        tp = sum(a == l and b == l for a, b in zip(y, p))
        fp = sum(a != l and b == l for a, b in zip(y, p))
        fn = sum(a == l and b != l for a, b in zip(y, p))
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        f1s.append(f1)
        per[l] = {"precision": pct(prec), "recall": pct(rec), "f1": pct(f1)}
    lat = [by_id[i]["latency_ms"] for i in gold if by_id[i].get("latency_ms") is not None]
    errors = [{"id": i, "text": gold[i]["text"], "gold": gold[i]["label"], "pred": by_id[i]["pred"]}
              for i in gold if gold[i]["label"] != by_id[i]["pred"]]
    return {
        "n": len(y),
        "accuracy": pct(acc),
        "macro_f1": pct(sum(f1s) / len(f1s)),
        "agent_action_recall": per["agent_action"]["recall"],
        "agent_action_missed": [e for e in errors if e["gold"] == "agent_action"],
        "invalid_outputs": sum(by_id[i]["pred"] not in LABELS for i in gold),
        "latency_p50_ms": percentile(lat, 50),
        "latency_p95_ms": percentile(lat, 95),
        "avg_in_tokens": round(sum(by_id[i].get("in_tokens", 0) for i in gold) / len(y)),
        "avg_out_tokens": round(sum(by_id[i].get("out_tokens", 0) for i in gold) / len(y)),
        "per_label": per,
        "confusions": Counter(f"{e['gold']} -> {e['pred']}" for e in errors).most_common(8),
        "errors": errors,
    }


def main():
    gold = {"test": load("test"), "hard": load("hard")}
    summary = {}
    for path in sorted(glob.glob(os.path.join(HERE, "results", "*_*.json"))):
        base = os.path.basename(path)[:-5]
        if base.startswith("summary"):
            continue
        arm, split = base.rsplit("_", 1)
        if split not in gold:
            continue
        with open(path) as f:
            summary.setdefault(arm, {})[split] = score(gold[split], json.load(f))
    with open(os.path.join(HERE, "results", "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)

    arms = [a for a in ARM_ORDER if a in summary] + [a for a in summary if a not in ARM_ORDER]
    lines = ["# Router study results", "",
             "| Arm | Test acc | Test macro-F1 | Hard acc | Hard macro-F1 | Agent-action recall (test / hard) | p95 latency | Avg tokens in / out |",
             "|---|---|---|---|---|---|---|---|"]
    for a in arms:
        t, h = summary[a].get("test"), summary[a].get("hard")
        if not t or not h:
            continue
        lines.append(f"| {a} | {t['accuracy']}% | {t['macro_f1']}% | {h['accuracy']}% | {h['macro_f1']}% | "
                     f"{t['agent_action_recall']}% / {h['agent_action_recall']}% | {t['latency_p95_ms']} ms | "
                     f"{t['avg_in_tokens']} / {t['avg_out_tokens']} |")
    for a in arms:
        lines += ["", f"## {a}: errors"]
        for split in ("test", "hard"):
            s = summary[a].get(split)
            if not s:
                continue
            lines.append(f"\n**{split}** ({len(s['errors'])} errors; top confusions: "
                         + ", ".join(f"{c} ×{n}" for c, n in s["confusions"]) + ")\n")
            for e in s["errors"]:
                lines.append(f"- `{e['id']}` {e['text']!r}: gold {e['gold']}, predicted {e['pred']}")
    with open(os.path.join(HERE, "results", "summary.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:3 + len(arms) + 1]))


if __name__ == "__main__":
    main()
