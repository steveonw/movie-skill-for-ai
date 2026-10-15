# `narration.json` — `filmkit/narration@1.0` (provisional)

Written by every Narration Studio mode next to `narration.wav`. This is the
first implemented version of the sidecar sketched in `ARCHITECTURE.md`.
**Provisional:** field names may change after Story Director and Movie Builder
consume it (see issue #2). Additive fields will not bump the major version.

## Conventions

- Unit: integer sample frames of the master WAV at `audio.sample_rate`.
- Start inclusive, end exclusive. `*_seconds` fields are derived conveniences.
- `segments` and `silences` together tile `[0, total_samples)` with no gaps or
  overlaps (`verify` enforces this). `order` lists their IDs in time order.
- Segment and silence IDs are distinct namespaces from shot/asset IDs.

## Top level

| Field | Notes |
|---|---|
| `schema` | `"filmkit/narration@1.0"` |
| `mode` | `generated`, `assembled_clips` or `imported_readaloud` |
| `audio` | `file`, `sha256` (use to detect stale timing), `sample_rate`, `channels`, `sample_format`, `total_samples`, `duration_seconds` |
| `source` | input file name + sha256; how IDs were produced |
| `build` | `generated` mode only: engine identity, pause settings, cache stats (`hits`, `misses`, `synthesized` IDs, `rejected_entries`) |
| `segments[]` | speech clips, see below |
| `silences[]` | `id`, `start_sample`, `end_sample`, `frames`, `kind` (`inserted` = literal zeros added by this tool; `inferred_from_labels` = gap found in imported audio), `reason` (`sentence`, `paragraph`, `speaker_change`, `heading`, `explicit_pause`, `explicit_beat`, `explicit_scene_break`, `lead_in`, `tail`, `gap`, …), `requested_seconds` |
| `word_timing` | `{"available": false, "reason": …}` in M1 |
| `warnings[]` | human-readable; surface them to the user |

## Segment

| Field | Notes |
|---|---|
| `id` | from `script.json` if given, else positional `s001…` |
| `speaker`, `kind` (`line`/`heading`), `paragraph` | |
| `source_text` | exact text from the author's file |
| `display_text` | Markdown removed; use for captions |
| `spoken_text` | what the engine was given (after pronunciations); `null` when unknown (Read Aloud import) |
| `substitutions[]` | `{from, to, count}` pronunciation replacements applied |
| `start_sample`, `end_sample` | **clip** boundaries (exact, include engine padding) |
| `speech_start_sample`, `speech_end_sample` | measured audible speech, 10 ms resolution; `null` if none detected |
| `speech_bounds_source` | `energy_threshold_10ms` or `not_detected` |
| `voice` | engine, model, sid, speed, settings (generated mode) |
| `cache` | `{key, hit}` (generated mode) |
| `clip_source` | supplied file + sha256 (assemble mode) |
| `processing[]` | conversions applied (resampling, decoding) |
| `word_times[]` | always empty in M1 |

## Which boundary to use

| Purpose | Use |
|---|---|
| Cut to a new image when a line starts | `speech_start_sample`, rounded **up** to the next video frame |
| Caption on/off | `speech_start_sample` / `speech_end_sample` |
| Splice or re-order audio | `start_sample` / `end_sample` |
| Reveal on a word inside a line | not available yet; needs word timing |
