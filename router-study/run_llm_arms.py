"""Collect the prompted-LLM arms by calling a preview deployment's /api/router_eval endpoint.

Usage: python3 router-study/run_llm_arms.py <preview base URL> <arm: 120b|20b> [split ...]
Writes results/llm-<arm>_<split>.json in the same format as the local arms. Progress is saved after every
batch, so a run stopped by the free tier's daily token cap resumes where it left off.
The endpoint holds the Groq key (Vercel environment variable); this script never sees it.
"""
import json
import os
import re
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
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    for split in splits:
        path = os.path.join(HERE, "results", f"llm-{arm}_{split}.json")
        partial = path + ".partial"
        out = json.load(open(partial)) if os.path.exists(partial) else []
        start, total = len(out), None
        while total is None or start < total:
            data = fetch(f"{base}/api/router_eval?arm={arm}&split={split}&from={start}&n=40&gap_ms=4800")
            total = data["total"]
            out += [{"id": r[0], "pred": r[1], "latency_ms": r[2], "in_tokens": r[3], "out_tokens": r[4],
                     "json_repair": bool(r[5]), "model": data["model"]} for r in data["rows"]]
            json.dump(out, open(partial, "w"))
            print(f"{time.strftime('%H:%M:%S')} {arm} {split}: {data['next']}/{total} {(data['stopReason'] or '')[:200]}", flush=True)
            if data["next"] == start:  # rate-limited: wait as long as Groq asks (daily cap can mean minutes)
                m = re.search(r"try again in (?:(\d+)h)?(?:(\d+)m)?([\d.]+)s", data["stopReason"] or "")
                wait = (int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + float(m.group(3))) if m else 60
                time.sleep(min(max(wait + 2, 10), 1800))
            start = len(out)
        json.dump(out, open(path, "w"), indent=1)
        os.remove(partial)


if __name__ == "__main__":
    main()
