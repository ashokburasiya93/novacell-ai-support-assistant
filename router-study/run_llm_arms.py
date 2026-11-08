"""Collect the prompted-LLM arms by calling a preview deployment's /api/router_eval endpoint.

Usage: python3 router-study/run_llm_arms.py <preview base URL> <arm: 120b|20b> [split ...]
Writes results/llm-<arm>_<split>.json in the same format as the local arms.
The endpoint holds the Groq key (Vercel environment variable); this script never sees it.
"""
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))


def fetch(url):
    with urllib.request.urlopen(url, timeout=320) as r:
        return json.loads(r.read())


def main():
    base, arm = sys.argv[1].rstrip("/"), sys.argv[2]
    splits = sys.argv[3:] or ["test", "hard"]
    for split in splits:
        rows, start, total = [], 0, None
        while total is None or start < total:
            data = fetch(f"{base}/api/router_eval?arm={arm}&split={split}&from={start}&n=40&gap_ms=4800")
            total = data["total"]
            rows += data["rows"]
            print(f"{arm} {split}: {data['next']}/{total} {data['stopReason'] or ''}", flush=True)
            if data["next"] == start:  # no progress: wait out a rate limit, then retry
                time.sleep(60)
            start = data["next"]
        out = [{"id": r[0], "pred": r[1], "latency_ms": r[2], "in_tokens": r[3], "out_tokens": r[4], "model": data["model"]}
               for r in rows]
        os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
        with open(os.path.join(HERE, "results", f"llm-{arm}_{split}.json"), "w") as f:
            json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
