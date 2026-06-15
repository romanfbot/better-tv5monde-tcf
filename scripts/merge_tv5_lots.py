#!/usr/bin/env python3
"""Merge processed per-lot TV5MONDE TCF data into the static site dataset."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDER = [58, 57, 56, 45, 52, 53, 47, 42, 43, 44, 50, 55, 60, 66, 68, 69, 70]

QUESTION_STARTS = (
    "Quand",
    "Que",
    "Quel",
    "Quelle",
    "Quels",
    "Quelles",
    "Pourquoi",
    "Où",
    "Ou",
    "Comment",
    "Combien",
    "De quoi",
    "À quoi",
    "A quoi",
    "Selon",
    "D'après",
    "D’après",
    "Le document",
    "La personne",
    "Les personnes",
    "Cet extrait",
    "Cette annonce",
    "Cette conversation",
    "Dans ce document",
    "Dans cet extrait",
    "Dans la conversation",
    "Dans l'extrait",
    "Dans l’extrait",
)

INSTRUCTION_PHRASES = (
    "Écoutez les quatre propositions.",
    "Écoutez l'extrait sonore et les quatre propositions.",
    "Écoutez l’extrait sonore et les quatre propositions.",
    "Écoutez le document sonore et la question.",
    "Écoutez le document sonore et les questions.",
    "Écoutez la question et les quatre réponses.",
    "Écoutez le message et la question.",
    "Écoutez la conversation et la question.",
    "Écoutez l'extrait et la question.",
    "Écoutez l’extrait et la question.",
    "Choisissez celle qui correspond à l'image.",
    "Choisissez celle qui correspond à l’image.",
    "Choisissez la bonne réponse.",
    "Choisissez votre réponse.",
)

QUESTION_RE = re.compile(r"\s+(?=(?:" + "|".join(re.escape(s) for s in QUESTION_STARTS) + r")\b)")
OPTION_RE = re.compile(r"\s+(?=([ABCD])(?:[\.?]|\s))")


def format_transcript(text: str) -> str:
    """Format STT output for display without changing non-whitespace content."""
    if not text:
        return text
    formatted = re.sub(r"\s+", " ", text).strip()
    for phrase in INSTRUCTION_PHRASES:
        formatted = formatted.replace(phrase + " ", phrase + "\n\n")
    formatted = OPTION_RE.sub("\n", formatted)
    formatted = QUESTION_RE.sub("\n\n", formatted)
    formatted = re.sub(r"[ \t]*\n[ \t]*", "\n", formatted)
    formatted = re.sub(r"\n{3,}", "\n\n", formatted)
    return formatted.strip()


def format_lot_transcripts(lot: dict) -> None:
    for question in lot.get("questions", []):
        transcription = question.get("transcription") or {}
        text = transcription.get("text")
        if isinstance(text, str):
            transcription["text"] = format_transcript(text)

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
    format_lot_transcripts(lot)
    lots.append(lot)

payload = {
    "version": 3,
    "source": "tv5monde-tcf",
    "description": "Better TV5MONDE TCF listening-practice data with extracted answers and OpenRouter transcripts.",
    "lots": lots,
}

out = ROOT / "docs" / "data" / "tcf-lots.json"
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {out} with {len(lots)} lots / {sum(len(l['questions']) for l in lots)} questions")
