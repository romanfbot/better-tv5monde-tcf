#!/usr/bin/env python3
"""Transcribe existing TV5MONDE audio files with OpenRouter Whisper Large.

Writes per-question files next to existing parakeet outputs:
  data/tv5monde-<LOT_ID>/qNN-whisper-large-v3.json
  data/tv5monde-<LOT_ID>/qNN-whisper-large-v3.json.txt
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import time
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
OPENROUTER_URL = "https://openrouter.ai/api/v1/audio/transcriptions"
MODEL = "openai/whisper-large-v3"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def request_transcription(audio_path: Path, *, api_key: str) -> dict[str, Any]:
    audio_b64 = base64.b64encode(audio_path.read_bytes()).decode("ascii")
    payload = {
        "model": MODEL,
        "input_audio": {"data": audio_b64, "format": "mp3"},
        "language": "fr",
        "temperature": 0,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/romanfbot/better-tv5monde-tcf",
        "X-Title": "Better TV5MONDE TCF",
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=600)
    if not response.ok:
        raise RuntimeError(f"OpenRouter STT failed for {audio_path}: {response.status_code} {response.text[:1000]}")
    return response.json()


def transcribe_question(lot: dict[str, Any], question: dict[str, Any], *, api_key: str, force: bool) -> bool:
    lot_id = int(lot["lotId"])
    number = int(question["number"])
    out_path = ROOT / "data" / f"tv5monde-{lot_id}" / f"q{number:02d}-whisper-large-v3.json"
    txt_path = Path(str(out_path) + ".txt")
    if txt_path.exists() and txt_path.read_text(encoding="utf-8").strip() and not force:
        return False

    audio_url = question.get("audioUrl")
    if not audio_url:
        raise RuntimeError(f"No audioUrl for lot {lot_id} q{number}")
    audio_path = ROOT / "audio" / f"tv5monde-{lot_id}" / audio_url.rsplit("/", 1)[-1]
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    print(f"[lot {lot_id}] q{number:02d} whisper-large", flush=True)
    data = request_transcription(audio_path, api_key=api_key)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    txt_path.write_text(data.get("text", "").strip(), encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lots", nargs="*", type=int, help="Lot IDs to transcribe. Default: all lots in docs/data/tcf-lots.json")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.0, help="Optional delay between requests")
    args = parser.parse_args()

    load_env(Path.home() / ".hermes/.env")
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not found in environment or ~/.hermes/.env")

    data = json.loads((ROOT / "docs/data/tcf-lots.json").read_text(encoding="utf-8"))
    wanted = set(args.lots)
    lots = [lot for lot in data["lots"] if not wanted or int(lot["lotId"]) in wanted]
    done = skipped = 0
    for lot in lots:
        for question in lot["questions"]:
            wrote = transcribe_question(lot, question, api_key=api_key, force=args.force)
            if wrote:
                done += 1
                if args.sleep:
                    time.sleep(args.sleep)
            else:
                skipped += 1
    print(json.dumps({"model": MODEL, "done": done, "skipped": skipped, "lots": [lot["lotId"] for lot in lots]}))


if __name__ == "__main__":
    main()
