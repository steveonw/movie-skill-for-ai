# Architecture — Provisional Skill Interoperability v0

## Goal
Three independent Skills exchange optional files, not direct calls. Standalone capabilities are first-class.

```text
Story/script --[Story Director]--> script.json + plan.json
Story/script --[Narration Studio]--> narration.wav + narration.json
User MP3 ----[Narration Studio]--> narration.json (aligned)
plan + audio timing + visuals --[Movie Builder]--> timeline.json + final.mp4 + QA
User images + audio ----------[Movie Builder]--> final.mp4 (standalone)
```

## Responsibilities

**Story Director** owns creative direction: script decomposition, visual beats, reveals, speakers/delivery suggestions, shot intent and assets. No TTS, no image generation requirement, no FFmpeg. When only asked for a storyboard, respond in human-readable text.

**Narration Studio** owns audio: TTS clips, cache, pronunciation normalization, speaker casting, actual sample-based assembly, silence events, alignment of supplied MP3, optional selective word timing, exports. Must remain useful for audiobooks.

**Movie Builder** owns rendered media: source image intake, optional image generation adapters, text cards/typography, anchor-to-frame compilation, FFmpeg, captions in final layout, contact sheets and technical QA. Without plan uses clearly labeled simple slideshow timing rather than pretending AI direction occurred.

## Shared minimum JSON contract (not yet frozen)

All examples are *illustrative*, and contain shortened fields.

```json
{"schema":"filmkit/script@1.0","segments":[
 {"id":"s001","speaker":"narrator","text":"The first frame took fourteen hours.",
  "words":[{"id":"w1","raw":"The"},{"id":"w2","raw":"first"},{"id":"w3","raw":"frame"},{"id":"w4","raw":"took"},{"id":"w5","raw":"fourteen"},{"id":"w6","raw":"hours."}]}
]}
```

```json
{"schema":"filmkit/plan@1.0","script_hash":"<sha256>","assets":{
 "board":{"kind":"image","subject":"Students laboring in front of a chalkboard"},
 "hours":{"kind":"card","display":"14 HOURS"}},
 "shots":[
 {"id":"setup","asset":"board","start":{"segment":"s001","word":"w1"},"purpose":"setup"},
 {"id":"reveal","asset":"hours","start":{"segment":"s001","word":"w5"},
  "not_before":{"segment":"s001","word":"w5"},"purpose":"reveal","transition":"cut"}]}
```

```json
{"schema":"filmkit/narration@1.0","audio":{"file":"narration.wav",
 "sample_rate":24000,"total_samples":105600},"segments":[
 {"id":"s001","start_sample":0,"end_sample":72000,
  "spoken_text":"The first frame took fourteen hours.",
  "word_times":[{"word_id":"w5","start_sample":44500,"source":"aligned"}]}],
 "silences":[{"id":"pause1","start_sample":72000,"end_sample":105600,"kind":"inserted"}]}
```

```json
{"schema":"filmkit/timeline@1.0","fps":30,"total_frames":132,
 "shots":[{"id":"setup","asset":"board","start_frame":0,"end_frame":56},
          {"id":"reveal","asset":"hours","start_frame":56,"end_frame":132}]}
```

Timing values and cuts in the examples above do **not** represent measured DOOM narration. Canonical time units for generated audio should be integer samples; seconds and frames are compiler-derived. Generated clip start/end are exact file boundaries, not guaranteed spoken-word boundaries. With external audio, timing confidence depends on alignment.

## Invariants

1. A Skill is functional without the other two installed; supplied compatible files merely enhance it.
2. Only the original-script source owns display text. Spoken substitutions and word maps are separate.
3. Creative anchors are script references, not guessed absolute timestamps. Recompile after audio changes.
4. Any reveal image, overlay or caption must start no earlier than the reveal anchor (round up to next video frame).
5. A shot's ID and an asset's ID are distinct; multiple shots may reuse one asset.
6. Failure must be surfaced: previews may contain explicit placeholders; final output must be marked incomplete if media missing.
7. Keep an audit trail of generated files, cache hits, model/provider identity, costs and unresolved timing uncertainty.
8. Only deterministic validations should decide technical compliance; subjective humor/visual taste require review.

## Draft project layout

```text
project/
  story.md
  script.json
  plan.json
  narration.wav
  narration.json
  overrides.json            # optional
  timeline.json             # Movie Builder generated
  assets/images/
  cache/audio/
  reports/
  output/final.mp4
  output/contact_sheet.png
```

## Dependencies

- Story Director: can produce human-readable storyboards without external tools; scripts for segmentation/validation optional.
- Narration Studio: local audio tooling for complete synthesis/alignment modes; TTS models, licenses and packages must be evaluated. Alternate hosted adapters optional.
- Movie Builder: FFmpeg and suitable Python imaging tooling for rendering; provider credentials optional for AI images.

## Versioning

Schema families `filmkit/<kind>@MAJOR.MINOR` are proposed. Additive optional fields may be backward compatible. Breaking changes require a major bump and migration utility if projects exist. Maintain golden fixtures; avoid making copied multi-hundred-line shared core a prerequisite in v1.

## Quality bar

A fresh AI should be able to use these four files to understand the project, but no claim of rendered working video is made by this documentation.
