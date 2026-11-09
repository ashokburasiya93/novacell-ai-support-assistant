"""Write the router dataset to JSON files and check that no message appears in more than one split.

Usage: python3 router-study/data/build_dataset.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from train_raw import TRAIN  # noqa: E402
from test_raw import TEST, HARD  # noqa: E402

LABELS = ["data", "billing", "sim", "roaming", "calls", "account", "agent_action", "out_of_scope"]


def norm(text):
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def rows(split, prefix):
    out = []
    for label in LABELS:
        for i, text in enumerate(split[label], 1):
            out.append({"id": f"{prefix}-{label}-{i:02d}", "text": text, "label": label})
    return out


def main():
    splits = {"train": rows(TRAIN, "TR"), "test": rows(TEST, "TE"), "hard": rows(HARD, "HD")}
    seen = {}
    for name, items in splits.items():
        for r in items:
            key = norm(r["text"])
            if key in seen:
                raise SystemExit(f"duplicate message in {seen[key]} and {name}: {r['text']}")
            seen[key] = name
    for name, items in splits.items():
        with open(os.path.join(HERE, f"{name}.json"), "w") as f:
            json.dump(items, f, indent=1)
        counts = {l: sum(r["label"] == l for r in items) for l in LABELS}
        print(name, len(items), counts)


if __name__ == "__main__":
    main()
