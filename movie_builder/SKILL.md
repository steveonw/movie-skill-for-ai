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
2. Create `project.json` with `audio`, `shots:[{"image":"...","duration":1.5}]`, and optional `fps`, `width`, `height`. For *already compiled* exact frame cuts, use `shots:[{"image":"...","end_frame":45}, ...]` with strictly increasing exclusive end frames. Do not mix duration and end_frame within a project. Resolve paths relative to the JSON file; reuse images as appropriate.
3. For exact statistics, titles or math, draw text cards deterministically in an image tool. Any missing media means the render must be labeled incomplete; optionally make an explicitly labeled placeholder animatic.
4. Compile deliberate reveals into **absolute frame boundaries no earlier than their measured spoken anchors**: use `ceil(anchor_sample * fps / sample_rate)` for measured sample timing, or `ceil(anchor_seconds * fps)` for a measured time in seconds. The preceding shot's `end_frame` is the first frame of the reveal shot. For ordinary duration plans, the renderer rounds *cumulative* shot times to frames (not each duration separately). If word timing was not measured, label the cut approximate; do not claim word-perfect sync.
5. Use bundled `scripts/renderer.py` with FFmpeg, ffprobe and Pillow: `python scripts/renderer.py project.json movie.mp4`. It measures decoded audio samples (important for MP3 encoder padding), rejects a mismatch over one frame, pads slightly short audio and extends the final still up to a frame when audio is slightly long. It avoids `-shortest` to preserve final AAC audio packets. Inspect the QA sidecar and labeled source-image contact sheet.
6. Where exact cuts matter, use `python scripts/verify_cuts.py project.json movie.mp4` to inspect decoded output frames adjacent to cuts, not merely the original image previews. Distinctive source images are needed for automated similarity checks; inspect visually when pictures are similar.
7. Return MP4, QA JSON, contact sheet, and test evidence. Explain missing features or uncertain timing.

## Limits
This initial version does not synthesize voice, align raw speech to words, generate AI images automatically, or implement intelligent creative direction. The source-image contact sheet is not proof of encoded cut accuracy. Do not use paid APIs or upload private media without the user's authorization. Preserve source assets and never rewrite them in place.

## Input timing examples

- **Durations:** `{"fps":30,"audio":"voice.wav","shots":[{"image":"intro.png","duration":1.5},{"image":"reveal.png","duration":1.5}]}`. Shot boundaries derive from cumulative time; each shot must still occupy at least one frame.
- **Exact cuts:** `{"fps":30,"audio":"voice.wav","shots":[{"image":"intro.png","end_frame":45},{"image":"reveal.png","end_frame":90}]}`. Frame 45 is the first frame of the reveal. `end_frame` values are exclusive, absolute and integer.

These are local Movie Builder input modes, **not** an approved `filmkit/*` cross-Skill schema. Exact-frame reveal cuts require *measured* audio anchors from another source; segment clip boundaries are not word-onset times. Automatic word alignment, images and narration synthesis remain out of scope.

## Local integration
When used inside the upstream GitHub repository, `movie_builder/renderer.py` and `movie_builder/make_demo.py` are the development sources. A packaged Skill also needs these scripts inside its `scripts/` directory.
