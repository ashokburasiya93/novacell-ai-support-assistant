"""Build kb/knowledge.json from NovaCell's three knowledge sources plus the plan catalogue.

Run:  python scripts/build_kb.py
Needs `pdftotext` (poppler) on PATH for the PDF guide. The output is committed, so the
deployed app never parses the PDF at runtime.

Product decisions encoded here:
- Every chunk keeps a stable id (FAQ-07, TK-009, GUIDE-4.3, PLAN-POST-UNLIMITED) so answers can cite it.
- Each chunk carries a `priority` used to break conflicts: the plan catalogue is the pricing
  source of truth (last updated 2026-06-01), then the guide, then the FAQ, then past tickets.
- The PDF guide is marked "Internal Use Only". Paragraphs that describe agent-only tooling or
  fraud-team procedures are excluded so the customer assistant cannot leak them.
- Past tickets describe one customer's case. They are kept as "how similar issues were fixed",
  but goodwill credits and compensation amounts are stripped so the bot cannot promise them.
"""
import csv
import json
import re
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "kb" / "knowledge.json"

PRIORITY = {"plan": 4, "guide": 3, "faq": 2, "ticket": 1}

# Guide paragraphs that are agent-only or security-sensitive. Matched on the paragraph label.
GUIDE_EXCLUDE_LABELS = {
    "SS7 and Diameter Vulnerabilities",   # attack surface detail
    "International Revenue Share Fraud (IRSF)",  # fraud-team unbarring procedure
    "SIM Security",                       # Ki / MILENAGE internals
    "Data Privacy",                       # agent ID-verification checklist (social-engineering risk)
    "Account Takeover",                   # attacker playbook
    "Step 7 - Escalate",                  # internal ticketing procedure
    "Steering of Roaming",                # internal SIM priority lists
    "Event-Based Billing",                # mediation/billing-engine internals
}
# Sentences removed from otherwise customer-safe guide paragraphs.
GUIDE_DROP_SENTENCE = re.compile(
    r"(Agents? (can|should|must|play)|agent must|subscriber management system|fraud team)", re.I
)
# Ticket resolution sentences about one-off goodwill gestures.
TICKET_DROP_SENTENCE = re.compile(r"(goodwill|compensation|offered \d|Offered \d|data compensation)", re.I)


def clean(s: str) -> str:
    s = s.replace("–", "-").replace("—", "-").replace("’", "'").replace("�", "-")
    return re.sub(r"\s+", " ", s).strip()


def split_sentences(text: str):
    return re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(])", text)


def faq_chunks():
    out = []
    for fname, synthetic in (("faq.csv", False), ("faq_extended.csv", True)):
        path = DATA / fname
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                out.append({
                    "id": f"FAQ-{int(row['id']):02d}",
                    "type": "faq",
                    "title": clean(row["question"]),
                    "text": f"Q: {clean(row['question'])}\nA: {clean(row['answer'])}",
                    "category": row["category"],
                    "source": f"Public FAQ{' (synthetic extension)' if synthetic else ''}",
                    "synthetic": synthetic,
                })
    return out


def ticket_chunks():
    con = sqlite3.connect(DATA / "tickets.db")
    out = []
    for tid, cat, issue, desc, res in con.execute(
        "select ticket_id, category, issue_type, description, resolution from tickets where status='resolved'"
    ):
        kept = [s for s in split_sentences(clean(res)) if not TICKET_DROP_SENTENCE.search(s)]
        out.append({
            "id": tid,
            "type": "ticket",
            "title": clean(issue),
            "text": f"Past resolved case ({cat}): {clean(issue)}.\nSymptom: {clean(desc)}\nHow it was resolved: {' '.join(kept)}",
            "category": cat,
            "source": "Resolved support ticket",
            "synthetic": False,
        })
    return out


def guide_chunks():
    raw = subprocess.run(
        ["pdftotext", str(DATA / "telecom_guide.pdf"), "-"], capture_output=True, text=True, encoding="utf-8"
    ).stdout
    # Collect (section_no, title, page, text) from the page stream.
    sections = []
    for pno, page in enumerate(raw.split("\f"), start=1):
        for line in page.splitlines():
            line = line.strip()
            if not line or line.startswith("Telecom Technical Reference Guide") or re.fullmatch(r"Page \d+", line):
                continue
            m = re.match(r"^(\d)\. (.+)$", line)
            if m and len(line) < 70:
                sections.append([m.group(1), m.group(2).strip(), pno, []])
            elif sections:
                sections[-1][3].append(line)

    # A paragraph label is a short Title Case phrase followed by a colon, or "Step N - Title.",
    # appearing at the start of a sentence.
    word = r"(?:[A-Z][A-Za-z0-9'\-]*|\([A-Za-z\- ]+\)|and|of|vs|for|to|the|a|in)"
    label_re = re.compile(rf"(?:(?<=^)|(?<=[.!?)] ))((?:Step \d+ - [A-Z][^.]{{3,60}}\.)|(?:eSIM|iSIM):|(?:[A-Z][A-Za-z0-9'\-]*(?: {word}){{0,6}}:))\s")
    out = []
    for no, title, pno, lines in sections:
        text = clean(" ".join(lines))
        cuts = [m.start(1) for m in label_re.finditer(text)]
        parts = []
        bounds = [0] + cuts + [len(text)]
        for a, b in zip(bounds, bounds[1:]):
            seg = text[a:b].strip()
            if not seg:
                continue
            m = label_re.match(seg)
            label = m.group(1).rstrip(":.") if m else "Overview"
            parts.append((label, seg))
        n = 0
        for label, seg in parts:
            if label in GUIDE_EXCLUDE_LABELS or label.startswith("Step 7"):
                continue
            seg = " ".join(s for s in split_sentences(seg) if not GUIDE_DROP_SENTENCE.search(s))
            if len(seg) < 40:
                continue
            n += 1
            out.append({
                "id": f"GUIDE-{no}.{n}",
                "type": "guide",
                "title": f"{title} - {label}",
                "text": seg,
                "category": title,
                "source": f"Technical Reference Guide v3.2, p.{pno}",
                "synthetic": False,
            })
    return out


def money(v):
    return f"${v:,.2f}".replace(".00", "")


def plan_chunks():
    d = json.loads((DATA / "plans.json").read_text(encoding="utf-8"))
    out = []
    for p in d["plans"]:
        lines = [f"NovaCell {p['name']} ({p['type']}, plan id {p['id']})."]
        if "monthly_price" in p:
            lines.append(f"Price: {money(p['monthly_price'])} per month.")
        if "price" in p:
            lines.append(f"Price: {money(p['price'])} {p.get('price_unit', '')}.")
        if p.get("price_per_line"):
            lines.append(f"Price per line: {money(p['price_per_line'])}; lines included: {p.get('lines_included')}.")
        elif p.get("lines_included"):
            lines.append(f"Lines included: {p['lines_included']}.")
        if p.get("data_unlimited"):
            lines.append("Data: unlimited.")
        elif p.get("data_gb") is not None:
            v = p["data_gb"]
            lines.append(f"Data: {v} GB." if isinstance(v, (int, float)) else f"Data: {v}.")
        for k, label in (("talk_minutes", "Talk"), ("texts", "Texts"), ("hotspot_gb", "Hotspot (GB)"),
                         ("network", "Network"), ("coverage", "Coverage"), ("contract", "Contract"),
                         ("eligibility", "Eligibility"), ("intro_offer", "Intro offer")):
            if p.get(k) not in (None, ""):
                lines.append(f"{label}: {p[k]}.")
        lines.append("Features: " + "; ".join(p.get("features", [])) + ".")
        lines.append(f"Best for: {p.get('best_for', '')}.")
        out.append({
            "id": f"PLAN-{p['id']}",
            "type": "plan",
            "title": f"{p['name']} ({p['type']})",
            "text": " ".join(lines),
            "category": p.get("category", p["type"]),
            "source": f"Plan catalogue (last updated {d['last_updated']})",
            "synthetic": False,
        })
    return out


def main():
    chunks = faq_chunks() + ticket_chunks() + guide_chunks() + plan_chunks()
    for c in chunks:
        c["priority"] = PRIORITY[c["type"]]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"version": 1, "chunks": chunks}, indent=1, ensure_ascii=False), encoding="utf-8")
    counts = {}
    for c in chunks:
        counts[c["type"]] = counts.get(c["type"], 0) + 1
    words = sum(len(c["text"].split()) for c in chunks)
    print(f"Wrote {len(chunks)} chunks {counts}, {words} words -> {OUT}")


if __name__ == "__main__":
    main()
