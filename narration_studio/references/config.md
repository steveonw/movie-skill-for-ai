# Narration Studio config (`--config cfg.json`)

All keys optional. Example: [`examples/sample_config.json`](../examples/sample_config.json).

```json
{
  "model_dir": "voices/vits-piper-en_US-amy-medium",
  "cast": {
    "narrator": {"sid": 0, "speed": 1.0},
    "Kevin":    {"sid": 0, "speed": 0.9},
    "Bang Guy": {"sid": 0, "speed": 0.8, "model_dir": "voices/other-voice"}
  },
  "pronunciations": {"0.000002": "zero point zero zero zero zero zero two", "FPS": "frames per second"},
  "pauses": {"sentence": 0.35, "paragraph": 0.75, "tail": 0.5},
  "detect_speakers": true
}
```

| Key | Meaning |
|---|---|
| `model_dir` | Default voice folder (relative to the config file). `--model-dir` overrides it. |
| `cast` | Voice per speaker name as written before the colon. `narrator` is the default for everything else. `sid` = speaker id inside a multi-speaker model; `speed` > 1 is faster. A per-speaker `model_dir` loads a second voice; clips at another sample rate are resampled with FFmpeg. Unknown speakers fall back to `narrator` with a warning. |
| `pronunciations` | Whole-word replacements applied to the *spoken* text only. Captions keep the author's text. Object form `{"written": "spoken"}` or list form `[{"match": "Kevin", "say": "Kev", "ignore_case": true}]`. Longest match wins. |
| `pauses` | Seconds. Defaults below. An explicit `[pause]` replaces the natural gap instead of adding to it. |
| `detect_speakers` | `false` treats `Name: text` as narration. |

## Pause defaults

| Key | Default | When |
|---|---|---|
| `sentence` | 0.35 | between sentences in a paragraph (Read Aloud default) |
| `paragraph` | 0.75 | across a blank line (Read Aloud uses gap + 0.4) |
| `speaker_change` | 0.45 | new speaker within the same paragraph |
| `heading` | 0.9 | after a `#` heading |
| `pause` | 0.8 | `[pause]` without a length |
| `beat` | 0.6 | `[beat]` |
| `scene_break` | 1.5 | `---` |
| `lead_in` | 0.0 | silence before the first line |
| `tail` | 0.5 | silence after the last line |

Changing pauses never re-synthesizes speech; only assembly changes.
