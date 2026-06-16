#!/usr/bin/env python3
"""Choose the better STT transcript between existing Parakeet and Whisper Large outputs.

This is intentionally text-only: it does not claim to listen to audio. It scores the
transcripts for common STT failure modes seen in this dataset (English artifacts,
missing answer-option labels, very short/missing output), keeps the better-looking
text, then applies the shared display formatter from merge_tv5_lots.py.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from merge_tv5_lots import format_transcript

ROOT = Path(__file__).resolve().parents[1]
WHISPER_MODEL = "openai/whisper-large-v3"

# Human-audited cases where Whisper is visibly cleaner despite the heuristic score.
# Keys are (lotId, questionNumber).
WHISPER_OVERRIDES = {
    (58, 11),
    (58, 14),
    (57, 10),
    (56, 13),
    (52, 9),
    (52, 14),
    (53, 10),
    (43, 7),
    (43, 10),
    (50, 10),
    (55, 10),
    (60, 8),
    (66, 5),
    (66, 11),
    (69, 2),
    (69, 10),
    (69, 15),
    (70, 9),
    (70, 12),
}

ENGLISH_ARTIFACT_WORDS = {
    "about",
    "after",
    "again",
    "also",
    "answer",
    "because",
    "before",
    "channel",
    "copyright",
    "could",
    "create",
    "english",
    "first",
    "foreign",
    "from",
    "good",
    "have",
    "here",
    "just",
    "like",
    "make",
    "missing",
    "mode",
    "morning",
    "music",
    "organized",
    "people",
    "please",
    "possibility",
    "second",
    "should",
    "subscribe",
    "subtitles",
    "thanks",
    "thank",
    "that",
    "their",
    "there",
    "these",
    "they",
    "third",
    "this",
    "those",
    "were",
    "what",
    "when",
    "where",
    "which",
    "with",
    "would",
    "years",
    "your",
}

ARTIFACT_PHRASES = (
    "sous-titrage st",
    "sous-titrage société",
    "tv gelderland",
    "mère de dieu",
    "ming pao",
    "amara.org",
    "abonnez-vous",
    "copyright",
    "thank you",
    "thanks for watching",
    "good morning",
    "good afternoon",
    "please subscribe",
    "subtitles",
)

FRENCH_SIGNAL_WORDS = {
    "écoutez",
    "choisissez",
    "question",
    "réponse",
    "bonjour",
    "madame",
    "monsieur",
    "pourquoi",
    "comment",
    "quand",
    "quelle",
    "travail",
    "personne",
    "document",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def clean_known_artifacts(text: str) -> str:
    """Remove repeated non-audio subtitle/channel tails from STT output."""
    cleaned = text.strip()
    cleaned = re.sub(r"\s*Sous-titrage\s+Société\s+Radio-Canada\s*\.?\s*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*Sous-titrage\s+ST['’]?\s*501\s*\.?\s*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*Merci d'avoir regardé cette vidéo\s*\.?\s*$", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def english_artifact_count(text: str) -> int:
    words = re.findall(r"[A-Za-z][A-Za-z']+", text.lower())
    return sum(word in ENGLISH_ARTIFACT_WORDS for word in words)


def artifact_phrase_count(text: str) -> int:
    low = text.lower()
    return sum(low.count(phrase) for phrase in ARTIFACT_PHRASES)


def french_signal_count(text: str) -> int:
    low = text.lower()
    return sum(1 for word in FRENCH_SIGNAL_WORDS if word in low)


def option_labels(text: str) -> set[str]:
    labels: set[str] = set()
    for match in re.finditer(r"(?:^|[\n\s])([ABCD])(?:[\.?]|\s)", text):
        labels.add(match.group(1))
    return labels


def score(text: str, other_text: str) -> tuple[float, dict[str, Any]]:
    ntext = normalize(text)
    other = normalize(other_text)
    labels = option_labels(text)
    eng = english_artifact_count(text)
    phrase_artifacts = artifact_phrase_count(text)
    french_signals = french_signal_count(text)
    length = len(ntext)
    other_length = len(other)

    value = 0.0
    value += min(length, 1200) / 80.0
    value += french_signals * 2.0
    value += len(labels) * 3.0
    value -= eng * 6.0
    value -= phrase_artifacts * 20.0
    if length < 40:
        value -= 40
    if other_length and length < other_length * 0.65:
        value -= 18
    if "quatre propositions" in ntext.lower() and len(labels) < 3:
        value -= (3 - len(labels)) * 7
    if re.search(r"\b[A-Z][a-z]+land\b", text):
        value -= 5

    details = {
        "score": round(value, 3),
        "length": length,
        "englishArtifacts": eng,
        "artifactPhrases": phrase_artifacts,
        "frenchSignals": french_signals,
        "optionLabels": "".join(sorted(labels)),
    }
    return value, details


def read_parakeet_text(lot_id: int, question_number: int) -> str:
    path = ROOT / "data" / f"tv5monde-{lot_id}" / f"q{question_number:02d}-parakeet.json.txt"
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8").strip()


def read_whisper_text(lot_id: int, question_number: int) -> str:
    path = ROOT / "data" / f"tv5monde-{lot_id}" / f"q{question_number:02d}-whisper-large-v3.json.txt"
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Update docs/data/tcf-lots.json with selected transcripts")
    parser.add_argument("--report", default="data/transcript-selection-report.json")
    args = parser.parse_args()

    data_path = ROOT / "docs/data/tcf-lots.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    report: list[dict[str, Any]] = []
    counts = {"parakeet": 0, "whisper": 0}

    for lot in data["lots"]:
        lot_id = int(lot["lotId"])
        for question in lot["questions"]:
            qn = int(question["number"])
            current_tx = question["transcription"]
            parakeet_text = clean_known_artifacts(read_parakeet_text(lot_id, qn))
            whisper_text = clean_known_artifacts(read_whisper_text(lot_id, qn))
            parakeet_score, parakeet_details = score(parakeet_text, whisper_text)
            whisper_score, whisper_details = score(whisper_text, parakeet_text)
            choice = "whisper" if whisper_score > parakeet_score + 1.0 else "parakeet"
            if (lot_id, qn) in WHISPER_OVERRIDES:
                choice = "whisper"
            counts[choice] += 1

            selected_text = whisper_text if choice == "whisper" else parakeet_text
            formatted = format_transcript(selected_text)
            if args.apply:
                current_tx["model"] = WHISPER_MODEL if choice == "whisper" else current_tx.get("model", "nvidia/parakeet-tdt-0.6b-v3")
                current_tx["text"] = formatted
                if choice == "whisper":
                    current_tx["rawFile"] = f"data/tv5monde-{lot_id}/q{qn:02d}-whisper-large-v3.json"

            report.append(
                {
                    "displayNumber": lot["displayNumber"],
                    "lotId": lot_id,
                    "question": qn,
                    "choice": choice,
                    "parakeet": parakeet_details,
                    "whisper": whisper_details,
                    "delta": round(whisper_score - parakeet_score, 3),
                    "override": (lot_id, qn) in WHISPER_OVERRIDES,
                }
            )

    report_path = ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps({"counts": counts, "items": report}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.apply:
        data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"counts": counts, "report": str(report_path.relative_to(ROOT)), "applied": args.apply}, ensure_ascii=False))


if __name__ == "__main__":
    main()
