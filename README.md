# TCF practice with transcripts

A small static website that improves the TV5MONDE TCF practice-test experience by adding automatic transcripts to the listening questions.

Published site: https://romanfbot.github.io/tcf-transcripts/

## What is included

- `docs/` — buildless static site for GitHub Pages.
- `docs/data/tcf-lots.json` — extracted TV5MONDE TCF lot data: questions, audio URLs, answer choices, correct answers, and transcripts.
- `docs/EXTRACTION.md` — repeatable extraction workflow for future swarm/parallel agents.
- `scripts/transcribe_openrouter.py` — transcription script using the OpenRouter STT endpoint.
- `scripts/build_lot58_dataset.py` — builds the current prototype dataset from extracted metadata and transcript files.
- `data/tv5monde-58/` — raw OpenRouter responses and transcript text files for the `tcf_lot_id=58` listening section.

## Current prototype

The current deployed version includes the `Compréhension orale` section for this TV5MONDE test:

```text
https://apprendre.tv5monde.com/fr/tcf/test-dentrainement-au-tcf?tcf_lot_id=58#tcf_header
```

The 15 listening questions use audio files extracted from the TV5MONDE per-question pages and transcripts generated with:

```text
nvidia/parakeet-tdt-0.6b-v3
```

## Local development

```bash
cd docs
python3 -m http.server 8080
# open http://localhost:8080
```

## Transcribing another audio file

The script expects `OPENROUTER_API_KEY` in the environment or in `~/.hermes/.env`.

```bash
python3 scripts/transcribe_openrouter.py audio/tv5monde-58/159-2.mp3 data/tv5monde-58/q02-parakeet.json --model nvidia/parakeet-tdt-0.6b-v3
```

The script creates two files:

- `*.json` — the full OpenRouter JSON response;
- `*.json.txt` — transcript text only.

## Adding more TV5MONDE lots

Follow `docs/EXTRACTION.md` for the browser/result-page extraction flow and the expected JSON shape. The short version:

1. Open the TV5MONDE TCF lot URL.
2. Stop the test and open results.
3. Extract correct answers from the `tcf_questions` cookie.
4. Visit each `entrainement-frame?question=<n>&tcf_lot_id=<LOT_ID>` page.
5. Extract audio URLs, prompts, answer choices, images, and correct answer codes.
6. Transcribe every audio URL through OpenRouter.
7. Merge the lot into `docs/data/tcf-lots.json`.

## Source

TV5MONDE: https://apprendre.tv5monde.com/fr/tcf/test-dentrainement-au-tcf?tcf_lot_id=58#tcf_header
