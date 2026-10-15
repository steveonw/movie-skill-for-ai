---
name: narration-studio
description: Narrate a story, script or lesson into a WAV with exact timing using a free local voice, or time a narration someone recorded themselves against its script, down to individual words. Also joins supplied voice clips and imports Read Aloud exports. Use when someone asks to narrate, voice, read aloud or make an audiobook/voiceover from text, to sync a recording with a script, to find when a word is spoken, or to produce narration timing (narration.json, SRT, label track) for a video. Works on its own; Story Director and Movie Builder are optional.
---

# Narration Studio

Turns text into narration audio plus a timing file that says, to the exact
sample, where every sentence and every pause sits. Useful alone (audiobook,
lesson audio, proofreading by ear) and as the timing source for Movie Builder.

**Status: M2 (provisional).** Built and tested: text/Markdown parsing, speaker
casting, pronunciation map, one local TTS engine (sherpa-onnx + Piper/VITS
voices), persistent clip cache, sample-exact assembly, clip import, Read Aloud
import, SRT/label export, verification, **word-level timing**, and **aligning a
recording made outside this tool** to its script. Word timing accuracy was
validated on synthetic speech only; on a human recording, say it is unvalidated
and ask the user to spot-check the words that matter.

## Pick the mode

| The user has… | Mode | Command |
|---|---|---|
| Text, wants it narrated | **build** | `narrate.py build story.md --model-dir VOICE --out OUT` |
| Separate recorded/generated clips | **assemble** | `narrate.py assemble clips.json --out OUT` |
| A Read Aloud export (WAV/MP3 + label track) | **import-readaloud** | `narrate.py import-readaloud narration.wav labels.txt --out OUT` |
| A recording they made (or another TTS) + its script | **align** | `narrate.py align recording.mp3 story.md --asr-model ASR --out OUT` |
| Needs to know when specific words are said | **words** | `narrate.py words OUT --asr-model ASR --find bang,fourteen` |
| An output folder to re-check | **verify** | `narrate.py verify OUT` |

Scripts live in `scripts/`. Run them with Python 3.10+; `numpy` is required,
`sherpa-onnx` for `build`, `words` and `align`, FFmpeg only when audio needs converting.

**Speech-recognition model** (for `words` and `align`; once, 112 MB, Apache-2.0):
```bash
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-small-en-2023-06-26.tar.bz2
tar xjf sherpa-onnx-zipformer-small-en-2023-06-26.tar.bz2
```
Any sherpa-onnx offline transducer folder (`encoder*/decoder*/joiner*.onnx` + `tokens.txt`) works.

## Workflow: build (text → narration)

1. **Get a voice** (once). Default: the same voice Read-Aloud-Main ships.
   ```bash
   pip install sherpa-onnx numpy
   curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-amy-medium.tar.bz2
   tar xjf vits-piper-en_US-amy-medium.tar.bz2
   ```
   Any sherpa-onnx VITS/Piper folder (`*.onnx` + `tokens.txt` + `espeak-ng-data/`)
   works. Check the voice's MODEL_CARD/licence before commercial use and tell
   the user it is their call; do not state a licence you have not read.
2. **Prepare the text** without rewriting the author's words. The parser understands:
   - blank line = new paragraph (longer pause)
   - `Name: words` = a line spoken by that character (1–3 capitalised words)
   - `[pause]`, `[pause 1.5s]`, `[beat]` on their own line = deliberate pause
   - `---` = scene break; `# Heading` = spoken heading with a pause after
   - Markdown emphasis/links are removed from captions and speech
3. **Optional config** (`references/config.md`): `cast` (voice per speaker:
   `sid`, `speed`, optional `model_dir`), `pronunciations` (what is *said*
   instead of what is *written*, e.g. `"2026": "twenty twenty-six"`), `pauses`
   (seconds), `detect_speakers`.
4. **Run** `python scripts/narrate.py build story.md --config cfg.json --model-dir VOICE --out OUT`.
5. **Read the report.** It states duration, segments, cache reuse, warnings
   and the verify result. Relay warnings plainly (e.g. a speaker with no voice).
6. **Let the user listen**, then fix what they flag:
   - mispronounced word → add a `pronunciations` entry, rebuild
   - wrong pacing → change `pauses` (no re-synthesis needed; only assembly changes)
   - one bad line → edit that line, rebuild; only changed lines are re-synthesized

## Outputs (all modes)

`OUT/narration.wav` (16-bit PCM master), `narration.json`, `narration.srt`
(captions timed to measured speech), `narration-labels.txt` (Audacity /
Read-Aloud format). Hand `narration.json` + WAV to Movie Builder or an editor.

## Timing rules you must keep straight

- Positions are integer **samples** of the master WAV. Start inclusive, end exclusive.
- `start_sample`/`end_sample` = **clip boundaries**: exact, but they include the
  engine's own silence padding (measured 30–60 ms before and ~50–200 ms after speech for the Amy voice).
- `speech_start_sample`/`speech_end_sample` = **measured audible speech**, 10 ms
  resolution. Use these for cuts and captions that should land "when the line starts".
- `word_times[].start_sample` = **refined audible start of a word**. Use it for
  reveals, rounded **up** to the next video frame. Skip entries with
  `low_confidence: true` for reveals and tell the user which words those were.
  Word `end_sample` is only the next word's start (approximate).
- `word_times` stays empty until `words` (or `build --asr-model`, or `align`) runs.
  Never invent word timestamps.
- VITS voices are random: re-synthesizing the same line gives different audio and
  a different length. The cache is what keeps timing stable. Never delete
  `cache/` between a narration and a video edit that depends on it.

## Assemble mode (supplied clips)

`clips.json`:
```json
{"items": [{"id": "s001", "clip": "clips/one.wav", "text": "Line one.", "speaker": "narrator"},
           {"pause": 0.8},
           {"id": "s002", "clip": "clips/two.mp3", "text": "Line two."}],
 "lead_in": 0.0, "tail": 0.5, "default_gap": 0.0}
```
Clips are joined exactly as given; only listed pauses are added (or `default_gap`).
Other formats or sample rates are converted with FFmpeg and recorded under `processing`.

## Import mode (Read-Aloud-Main)

In Read Aloud: Render / Update → tick the label option → Export WAV (preferred) or MP3.
Import the audio with its `read-aloud-narration-labels.txt`. Timing is sample-exact
from WAV. From MP3, warn that encoder padding may shift every label slightly.
`spoken_text` is null because Read Aloud's pronunciation dictionary is not exported.

## Word timing (`words`)

Run after `build`, `assemble` or `import-readaloud`. `--find bang,fourteen` times
only the lines containing those words (cheapest); `--only s004,s007` picks lines by
ID; no option times every line. Audio is never changed. How it works: a local speech
recognizer hears each line, its letters are fuzzy-matched to the script's spoken
words (so "staple" heard as "STABLE", or "41" spoken as "forty one", still match),
then each word start is refined against the audio, because raw recognizer times run
early (measured 63–785 ms). Measured on 60 known word onsets in synthetic speech:
mean error about −1 ms, none more than one 30 fps frame early, one case 97 ms late
(a soft "z").

## Align mode (outside recording)

For narration recorded outside this tool: one WAV/MP3 plus the script it was read
from (same text formats and config as `build`). The recording stays the timing
authority and is kept bit-exact; each line's start and end come from its aligned
words. Report every warning to the user, they mean:
- *only partly matches*: the reading differs from the script (ad-lib, edit, misread)
- *not found in the recording*: the line was skipped or cut; it is left out of the timing
- *speech … isn't in the script*: an extra take, ad-lib, or a line missing from the script
Fix the script or the recording and re-run; never paper over these.

## Cooperation (optional)

- Given a Story Director `script.json` (`filmkit/script@1.x`), use it as input:
  its segment IDs are kept, so plans that reference them keep working.
- Plain-text input gets positional IDs (`s001`…). They shift if lines are added or
  removed; say so if the user plans to edit after a video plan was made.
- Movie Builder reads `narration.json`. It owns captions styling and frame rounding.

## Failure handling

- Missing voice files, empty text, unreadable audio → stop with the error; do not
  produce a partial master and call it complete.
- Damaged cache entries are detected by checksum and regenerated automatically.
- `verify` must print OK before handing outputs on. If it fails, report the exact line.

## References

- `references/narration-schema.md`: every field of `narration.json`
- `references/config.md`: config options and defaults
- `tests/`: acceptance tests (`python -m unittest discover -s narration_studio/tests`;
  set `NS_TEST_MODEL_DIR` and `NS_TEST_ASR_DIR` to include the real-model tests)
