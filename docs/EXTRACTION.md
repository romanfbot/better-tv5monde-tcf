# TV5MONDE TCF extraction workflow

This document describes the repeatable workflow used for the `tcf_lot_id=58` prototype. It is written so future swarm/parallel agents can process other TV5MONDE TCF links in the same format.

## Input

A TV5MONDE TCF training-test URL, for example:

```text
https://apprendre.tv5monde.com/fr/tcf/test-dentrainement-au-tcf?tcf_lot_id=58#tcf_header
```

The important variable is `tcf_lot_id`.

## Browser workflow

1. Open the test URL in a real browser session.
2. If the cookie consent modal appears, click **Continue without agreeing**.
3. Click **Arrêter le test**.
4. Click **Arrêter et voir mes résultats**.
5. The result page now exposes the answer key in a cookie named `tcf_questions`.
   - Example shape after URL-decoding:

```json
{
  "1": {"id": "441", "or": "B"},
  "2": {"id": "442", "or": "A"}
}
```

6. For each question number `n`, load the frame URL:

```text
https://apprendre.tv5monde.com/fr/tcf/entrainement-frame?question=<n>&tcf_lot_id=<LOT_ID>&competence=
```

7. Extract from the frame HTML:
   - `.tcf-skill` → section name, e.g. `Compréhension orale`.
   - `.tcf-consigne` → instruction.
   - `.tcf-question-wrapper` → prompt/question text.
   - `.tcf-choix-item` → answer options.
   - `.tcf-response-code` → option code (`A`, `B`, `C`, `D`).
   - `.tcf-response-text` → option text.
   - `audio` source or an MP3 URL regex → audio URL, if present.
   - `.tcf-media img` or `img.img-responsive` → image URL, if present.
   - `tcf_questions[n].or` → correct answer code.
   - `tcf_questions[n].id` → TV5MONDE question id.

## Audio URL extraction note

The frame HTML may contain escaped MP3 URLs such as:

```text
https:\/\/apprendre.tv5monde.com\/sites\/apprendre.tv5monde.com\/files\/tcf_question\/159-2.mp3
```

Normalize escaped slashes before storing:

```js
url.replaceAll('\\/', '/')
```

For `tcf_lot_id=58`, the comprehension-orale questions use:

```text
https://apprendre.tv5monde.com/sites/apprendre.tv5monde.com/files/tcf_question/159-<QUESTION_NUMBER>.mp3
```

Do not assume this pattern for other lots; extract the URL from the page.

## Transcription workflow

For each question with an `audioUrl`:

1. Download the MP3 file.
2. Send the raw audio bytes as base64 to OpenRouter's STT endpoint:

```http
POST https://openrouter.ai/api/v1/audio/transcriptions
```

3. Use this payload shape:

```json
{
  "model": "nvidia/parakeet-tdt-0.6b-v3",
  "input_audio": {
    "data": "<BASE64_AUDIO>",
    "format": "mp3"
  },
  "language": "fr",
  "temperature": 0
}
```

4. Store both:
   - the raw OpenRouter JSON response;
   - the extracted transcript text.

This repo's helper script supports the model parameter:

```bash
python3 scripts/transcribe_openrouter.py audio/tv5monde-58/159-2.mp3 data/tv5monde-58/q02-parakeet.json --model nvidia/parakeet-tdt-0.6b-v3
```

## Output JSON shape

Future agents should append lots to `docs/data/tcf-lots.json` using this shape:

```json
{
  "version": 2,
  "source": "tv5monde-tcf",
  "lots": [
    {
      "id": "tv5monde-tcf-58",
      "lotId": 58,
      "title": "TV5MONDE TCF training test — lot 58",
      "sourceUrl": "https://apprendre.tv5monde.com/fr/tcf/test-dentrainement-au-tcf?tcf_lot_id=58#tcf_header",
      "transcriptionModel": "nvidia/parakeet-tdt-0.6b-v3",
      "questions": [
        {
          "number": 2,
          "questionId": "442",
          "skill": "Compréhension orale",
          "instruction": "...",
          "prompt": "...",
          "audioUrl": "https://.../159-2.mp3",
          "imageUrl": "https://...jpeg",
          "correctAnswer": "A",
          "answers": [
            {"code": "A", "text": "Réponse A", "correct": true}
          ],
          "transcription": {
            "model": "nvidia/parakeet-tdt-0.6b-v3",
            "language": "fr",
            "text": "...",
            "rawFile": "data/tv5monde-58/q02-parakeet.json"
          }
        }
      ]
    }
  ]
}
```

## Parallelization plan

For swarm agents:

- Assign one `tcf_lot_id` per agent.
- Each agent extracts page data and transcribes only the audio files for that lot.
- Write per-lot output to `data/tv5monde-<LOT_ID>/` first.
- Merge reviewed lots into `docs/data/tcf-lots.json` in a final coordinator pass.
- Verify every merged lot has:
  - question numbers;
  - correct answers;
  - answer options;
  - audio URLs for `Compréhension orale` questions;
  - transcript text for every audio URL.
