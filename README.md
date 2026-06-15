# TCF transcripts prototype

A small static website with transcripts for TV5MONDE TCF training audio files.

## What is included

- `docs/` — buildless static site for GitHub Pages.
- `docs/data/transcripts.json` — UI data: tests, tasks, transcripts, and source links.
- `scripts/transcribe_openrouter.py` — transcription script using the OpenRouter STT endpoint and the `openai/whisper-large-v3` model.
- `data/tcf1-openrouter.json` — raw OpenRouter response for TCF entraînement n°1.

## Local development

```bash
cd docs
python3 -m http.server 8080
# open http://localhost:8080
```

## Transcribing another audio file

The script expects `OPENROUTER_API_KEY` in the environment or in `~/.hermes/.env`.

```bash
python3 scripts/transcribe_openrouter.py audio/tcf2-podcast.mp3 data/tcf2-openrouter.json
```

The script creates two files:

- `data/tcf2-openrouter.json` — the full OpenRouter JSON response;
- `data/tcf2-openrouter.json.txt` — transcript text only.

After that, add the new test to `docs/data/transcripts.json` and review the automatic task splitting if needed.

## Source

TV5MONDE: https://apprendre.tv5monde.com/fr/article/les-livrets-dentrainement-au-tcf-r-avec-tv5monde
