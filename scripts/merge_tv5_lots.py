#!/usr/bin/env python3
"""Merge processed per-lot TV5MONDE TCF data into the static site dataset."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDER = [58, 57, 56, 45, 52, 53, 47, 42, 43, 44, 50, 55, 60, 66, 68, 69, 70]

lots = []
for display_number, lot_id in enumerate(ORDER, start=1):
    path = ROOT / "data" / f"tv5monde-{lot_id}" / "lot.json"
    if not path.exists():
        raise FileNotFoundError(path)
    lot = json.loads(path.read_text(encoding="utf-8"))
    lot["displayNumber"] = display_number
    lot["title"] = f"Test {display_number}"
    lot["id"] = f"tv5monde-tcf-{lot_id}"
    lot["lotId"] = lot_id
    lot["sourceUrl"] = f"https://apprendre.tv5monde.com/fr/tcf/test-dentrainement-au-tcf?tcf_lot_id={lot_id}&competence=CO#tcf_header"
    lots.append(lot)

payload = {
    "version": 3,
    "source": "tv5monde-tcf",
    "description": "TV5MONDE TCF listening-practice lots with extracted answers and OpenRouter transcripts.",
    "lots": lots,
}

out = ROOT / "docs" / "data" / "tcf-lots.json"
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {out} with {len(lots)} lots / {sum(len(l['questions']) for l in lots)} questions")
