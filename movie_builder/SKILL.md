---
name: movie-builder
description: Create narrated MP4 movies and animatics from supplied still images and WAV or MP3 narration. Use when asked to assemble video scenes, still-image documentary films, timed visual reveals, contact sheets, or video rendering and QA. Operates independently of Story Director and Narration Studio, while accepting their outputs once timings are compiled to shot durations.
---

# Movie Builder

Create real playable narrated videos from supplied images and audio. Never represent placeholder illustrations or synthetic audio as a finished narrated film.

## Inputs
- Required: WAV/MP3 narration, at least one still image, and a short timing plan (or enough information to create one).
- Optional: script, storyboard, `filmkit` timing sidecars, user-created image cards.
- Work standalone; do not require other Skills. Shared `filmkit/*@1.0` schemas remain provisional and must not be silently redefined here.

## Workflow
1. Probe the audio and inspect supplied media. Respect the user's story text; do not invent measured word timing or rewrite text silently.
2. Create `project.json` with `audio`, `shots:[{"image":"...","duration":1.5}]`, and optional `fps`, `width`, `height`. Resolve all file paths relative to the JSON file. Images can be reused for several shots.
3. For exact statistics, titles or math, draw text cards deterministically in an image tool. Any missing media means the render must be labeled incomplete; optionally make an explicitly labeled placeholder animatic.
4. Convert deliberate reveals to **frame boundaries no earlier than the measured spoken anchor**. Convert anchor time to frame using a ceiling, not nearest-frame rounding. If word timing is not measured, ask for timing or mark the reveal approximate; do not claim word-perfect sync.
5. Use the bundled `scripts/renderer.py` with FFmpeg, ffprobe and Pillow: `python scripts/renderer.py project.json movie.mp4`. Fail on mismatched audio/shot lengths rather than silently trimming narration. Keep sidecar QA and a labeled input-shot contact sheet.
6. Where exact cuts matter, use `python scripts/verify_cuts.py project.json movie.mp4` to inspect decoded output frames adjacent to cuts, not merely the original image previews. Distinctive source images are needed for automated similarity checks; inspect visually when pictures are similar.
7. Return MP4, QA JSON, contact sheet, and test evidence. Explain missing features or uncertain timing.

## Limits
This initial version does not synthesize voice, align raw speech to words, generate AI images automatically, or implement intelligent creative direction. The source-image contact sheet is not proof of encoded cut accuracy. Do not use paid APIs or upload private media without the user's authorization. Preserve source assets and never rewrite them in place.

## Local integration
When used inside the upstream GitHub repository, `movie_builder/renderer.py` and `movie_builder/make_demo.py` are the development sources. A packaged Skill also needs these scripts inside its `scripts/` directory.
