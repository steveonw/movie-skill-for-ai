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
| `mode` | `generated`, `assembled_clips`, `imported_readaloud` or `aligned_recording` |
| `audio` | `file`, `sha256` (use to detect stale timing), `sample_rate`, `channels`, `sample_format`, `total_samples`, `duration_seconds` |
| `source` | input file name + sha256; how IDs were produced |
| `build` | `generated` mode only: engine identity, pause settings, cache stats (`hits`, `misses`, `synthesized` IDs, `rejected_entries`) |
| `segments[]` | speech clips, see below |
| `silences[]` | `id`, `start_sample`, `end_sample`, `frames`, `kind` (`inserted` = literal zeros added by this tool; `inferred_from_labels` = gap found in imported audio; `gap_in_recording` = audio between aligned lines, kept as recorded; may contain breaths, noise or unscripted speech), `reason` (`sentence`, `paragraph`, `speaker_change`, `heading`, `explicit_pause`, `explicit_beat`, `explicit_scene_break`, `lead_in`, `tail`, `gap`, …), `requested_seconds` |
| `word_timing` | `available` (bool), `segments` (IDs that have word times), `method`, `recognizer` (model + checksum), `early_bias_seconds`, `validation` (measured accuracy and its conditions), `low_confidence_below`, `note`. `{"available": false, …}` until word timing runs |
| `heard_text` | `aligned_recording` only: what the recognizer heard, for debugging |
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
| `words[]` | `{id, text, spoken}` per display word. `id` = `w1…` or the IDs from `script.json`; `spoken` = what is actually said (after pronunciations); `spoken_with_previous: true` when a multi-word phrase was spoken on the word before |
| `heard_text` | what the recognizer heard for this line (after `words`) |
| `start_sample`, `end_sample` | **clip** boundaries (exact, include engine padding) |
| `speech_start_sample`, `speech_end_sample` | measured audible speech, 10 ms resolution; `null` if none detected |
| `speech_bounds_source` | `energy_threshold_10ms`, `asr_alignment` (aligned recording: bounds come from words) or `not_detected` |
| `voice` | engine, model, sid, speed, settings (generated mode) |
| `cache` | `{key, hit}` (generated mode) |
| `clip_source` | supplied file + sha256 (assemble mode) |
| `processing[]` | conversions applied (resampling, decoding) |
| `word_times[]` | empty until word timing runs; then one entry per word, see below |

## Word time entry

| Field | Notes |
|---|---|
| `word_id`, `text` | matches `words[]` |
| `start_sample`, `start_seconds` | refined audible start of the word; `null` if the word could not be matched |
| `end_sample` | next word's start, or the line's speech end: approximate |
| `confidence` | 0–1, share of the word's letters matched to what was heard |
| `low_confidence` | `true` when confidence < 0.5: don't use for reveals |
| `how` | `refined` (energy dip near the expected onset), `end_of_pause` (word follows a pause), `raw+bias` (fallback), `clamped_after_previous`, `unmatched` |
| `raw_asr_sample` | recognizer's own (early) time, kept for auditing |
| `source` | method name; `covered_by_previous_word` with `spoken_with` for phrase words |

## Which boundary to use

| Purpose | Use |
|---|---|
| Cut to a new image when a line starts | `speech_start_sample`, rounded **up** to the next video frame |
| Caption on/off | `speech_start_sample` / `speech_end_sample` |
| Splice or re-order audio | `start_sample` / `end_sample` |
| Reveal on a word inside a line | `word_times[].start_sample`, rounded **up** to the next frame; skip `low_confidence` |
