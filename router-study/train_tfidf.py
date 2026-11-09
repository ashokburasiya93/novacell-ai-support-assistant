"""Arm D: TF-IDF (word + character n-grams) + logistic regression. Trains in under a second on CPU.

Usage: python3 router-study/train_tfidf.py
Writes results/tfidf-logreg_test.json and results/tfidf-logreg_hard.json.
"""
import json
import os
import time

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline, make_union

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(HERE, "data", f"{name}.json")) as f:
        return json.load(f)


def main():
    train = load("train")
    model = make_pipeline(
        make_union(
            TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, lowercase=True),
            TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True, lowercase=True),
        ),
        LogisticRegression(C=10, max_iter=2000),
    )
    t0 = time.perf_counter()
    model.fit([r["text"] for r in train], [r["label"] for r in train])
    print(f"trained in {time.perf_counter() - t0:.2f}s")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    for split in ("test", "hard"):
        out = []
        for r in load(split):
            t = time.perf_counter()
            pred = model.predict([r["text"]])[0]
            out.append({"id": r["id"], "pred": pred, "latency_ms": round((time.perf_counter() - t) * 1000, 2),
                        "in_tokens": 0, "out_tokens": 0})
        with open(os.path.join(HERE, "results", f"tfidf-logreg_{split}.json"), "w") as f:
            json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
