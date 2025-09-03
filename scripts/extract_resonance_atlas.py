#!/usr/bin/env python3
import re
import csv
from pathlib import Path

CAPS_DIR = Path("capsules")
OUT_CSV = Path("data/atlas/resonance_atlas.csv")

SCHEMA = ["id", "band", "center_Hz", "instrument", "conditions", "source_path", "notes"]


def parse_markdown(md_text: str):
    # Very light heuristic parser; adapt to your capsule format.
    # Looks for lines like: Band: alpha, Center: 123.45 Hz, Instrument: coil-probe
    band = None
    center = None
    instrument = None
    conditions = None
    notes = []

    for line in md_text.splitlines():
        m = re.search(r"\b[Bb]and\s*[:=]\s*([A-Za-z0-9_\-]+)", line)
        if m:
            band = m.group(1)
        m = re.search(r"\b[Cc]enter\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*Hz", line)
        if m:
            center = m.group(1)
        m = re.search(r"\b[Ii]nstrument\s*[:=]\s*([^,;]+)", line)
        if m:
            instrument = m.group(1).strip()
        m = re.search(r"\b[Cc]onditions\s*[:=]\s*(.+)$", line)
        if m:
            conditions = m.group(1).strip()
        if line.strip().startswith("Notes:"):
            notes.append(line.strip()[6:].strip())

    return band, center, instrument, conditions, "; ".join([n for n in notes if n])


def main():
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    if CAPS_DIR.exists():
        for md in CAPS_DIR.rglob("*.md"):
            text = md.read_text(errors="ignore")
            band, center, instrument, conditions, notes = parse_markdown(text)
            rows.append({
                "id": md.stem,
                "band": band or "",
                "center_Hz": center or "",
                "instrument": instrument or "",
                "conditions": conditions or "",
                "source_path": str(md),
                "notes": notes or "TODO: manual review"
            })

    # Write header and any extracted rows after the two example rows if the file already exists
    existing = []
    if OUT_CSV.exists():
        existing = OUT_CSV.read_text().splitlines()
        # If file has header and examples, we won't duplicate; we will append new rows.

    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA)
        w.writeheader()
        # Preserve the two example rows from spec
        w.writerow({"id": "EXAMPLE-001", "band": "alpha", "center_Hz": "123.45", "instrument": "contact-mic", "conditions": "room-temp, quiet", "source_path": "capsules/example.md", "notes": "Example row; replace with curated value"})
        w.writerow({"id": "EXAMPLE-002", "band": "beta", "center_Hz": "678.90", "instrument": "coil-probe", "conditions": "ambient, low EM noise", "source_path": "capsules/example2.md", "notes": "Example row; replace with curated value"})
        for r in rows:
            w.writerow(r)

    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()