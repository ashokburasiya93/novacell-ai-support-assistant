"""Arm C: fine-tune a small encoder (all-MiniLM-L6-v2, 22M parameters) as an 8-way classifier.

Full fine-tune of the encoder plus a linear head on the 320 training messages, CPU only.
Ran in a 2-vCPU Vercel Sandbox (Hugging Face is not reachable from the authoring workspace).

Usage: python3 router-study/finetune_minilm.py
Writes results/finetuned-minilm_test.json, results/finetuned-minilm_hard.json and results/finetune_log.json.
"""
import json
import os
import random
import time

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

HERE = os.path.dirname(os.path.abspath(__file__))
LABELS = ["data", "billing", "sim", "roaming", "calls", "account", "agent_action", "out_of_scope"]
BASE = "sentence-transformers/all-MiniLM-L6-v2"
EPOCHS, BATCH, LR, SEED = 12, 16, 5e-5, 42


def load(name):
    with open(os.path.join(HERE, "data", f"{name}.json")) as f:
        return json.load(f)


class Classifier(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(BASE)
        self.head = torch.nn.Linear(self.encoder.config.hidden_size, len(LABELS))

    def forward(self, enc):
        out = self.encoder(**enc).last_hidden_state
        mask = enc["attention_mask"].unsqueeze(-1).float()
        pooled = (out * mask).sum(1) / mask.sum(1).clamp(min=1e-9)  # mean pooling
        return self.head(pooled)


def main():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    tok = AutoTokenizer.from_pretrained(BASE)
    model = Classifier()
    train = load("train")
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    steps = EPOCHS * ((len(train) + BATCH - 1) // BATCH)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: max(0.0, 1 - s / steps))
    loss_fn = torch.nn.CrossEntropyLoss(label_smoothing=0.05)
    log = {"base_model": BASE, "epochs": EPOCHS, "batch": BATCH, "lr": LR, "train_size": len(train), "epoch_loss": []}
    t0 = time.perf_counter()
    model.train()
    for epoch in range(EPOCHS):
        random.shuffle(train)
        total = 0.0
        for i in range(0, len(train), BATCH):
            batch = train[i:i + BATCH]
            enc = tok([r["text"] for r in batch], padding=True, truncation=True, max_length=64, return_tensors="pt")
            y = torch.tensor([LABELS.index(r["label"]) for r in batch])
            loss = loss_fn(model(enc), y)
            opt.zero_grad()
            loss.backward()
            opt.step()
            sched.step()
            total += loss.item() * len(batch)
        log["epoch_loss"].append(round(total / len(train), 4))
        print(f"epoch {epoch + 1}: loss {log['epoch_loss'][-1]}", flush=True)
    log["train_seconds"] = round(time.perf_counter() - t0, 1)
    log["cpu_threads"] = torch.get_num_threads()

    model.eval()
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with torch.no_grad():
        for split in ("test", "hard"):
            out = []
            for r in load(split):
                t = time.perf_counter()
                enc = tok([r["text"]], truncation=True, max_length=64, return_tensors="pt")
                pred = LABELS[int(model(enc).argmax(-1)[0])]
                out.append({"id": r["id"], "pred": pred, "latency_ms": round((time.perf_counter() - t) * 1000, 2),
                            "in_tokens": 0, "out_tokens": 0})
            with open(os.path.join(HERE, "results", f"finetuned-minilm_{split}.json"), "w") as f:
                json.dump(out, f, indent=1)
    with open(os.path.join(HERE, "results", "finetune_log.json"), "w") as f:
        json.dump(log, f, indent=1)
    print(json.dumps(log))


if __name__ == "__main__":
    main()
