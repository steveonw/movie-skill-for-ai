***  
Gemini Pro Latest**

***Reasoning**

***Here is the Movie Builder Skill Implementation Plan. This design acts as the final compilation engine, taking the creative intent and measured audio from the previous steps and translating them into deterministic, highly optimized video rendering commands.**


### ***1. Skill Name and Triggering Description**

***Name: AI Movie Builder  
Description / System Trigger:  
"I am the Video Editor, Compositor, and VFX Supervisor. I compile visual and audio assets into finished movies. I manage image generation budgets, create programmatic text overlays, calculate absolute timelines, and write complex FFmpeg rendering commands. I can assemble a video from a folder of provided assets, or ingest structured manifests from Story Director and Narration Studio to fully automate visual generation and editing."**

### ***2. Standalone Use Cases**

***Without the other Skills, Movie Builder is a highly efficient programmatic video assembler:**

- ***Audio-Driven Slideshow: The user provides a folder of images and an MP3. Movie Builder evenly distributes the images across the audio duration, adding random slow Ken Burns effects and crossfades.**

- ***Exact Sync Editing: The user provides an MP3, an SRT file, and named images. Movie Builder creates a video where images change precisely when specific words appear in the SRT.**

- ***Placeholder Drafts: The user provides an audio track and a timing JSON. Movie Builder generates a video using colored rectangles with text labels ("Shot 1: Kevin at desk") to verify pacing before any images are actually generated or sourced.**

### ***3. Cooperative Workflow**

***When integrated with the full pipeline:**

1. ***Ingest: Receives `NarrativeManifest.json` (Story) and `audio\_timeline.json` (Narration).**

2. ***Asset Procurement: Checks local cache for required visual assets. For missing assets, it invokes the Image Generation Adapter (e.g., FLUX on Hugging Face). It generates code-based graphics (SVG/Drawtext) for statistics or title cards.**

3. ***Compilation: The deterministic Python compiler merges the abstract visual anchors with the concrete audio timestamps, producing a final absolute `RenderTimeline`.**

4. ***Rendering: Translates the `RenderTimeline` into an FFmpeg filtergraph.**

5. ***Quality Assurance (QA): Evaluates the rendered MP4, extracts a contact sheet, and produces a validation report.**

### ***4. Recommended `SKILL.md` and Supporting Files**

```
***`\# AI Movie Builder`**


***`\#\# Role`**

***`You are the final execution engine. You do not make creative story decisions; you enforce them accurately. `**


***`\#\# Core Directives`**

***`1. \*\*Math over Guessing:\*\* Never guess timestamps. Compile the timeline by linking Story constraints to Narration measurements.`**

***`2. \*\*Code Text, Don't Draw It:\*\* If a shot requires a statistic, equation, or title card, use FFmpeg \`drawtext\` or HTML-to-image. Do not ask a diffusion model to spell.`**

***`3. \*\*Guard the Budget:\*\* Always check the image cache before generating. If generation fails or budget is exceeded, fallback to a placeholder graphic; do not crash the render.`**

***`4. \*\*Python wraps FFmpeg:\*\* Do not write raw shell FFmpeg commands directly. Output JSON, and let the deterministic Python compiler build the filtergraph.`**
```

***Supporting Files:**

- ***`compiler.py`: Merges abstract intents + audio durations into absolute timestamps.**

- ***`image\_adapters.py`: Standardized interface for calling Hugging Face, local ComfyUI, or Fal.ai.**

- ***`ffmpeg\_renderer.py`: Wraps `ffmpeg-python` to construct the actual video.**

- ***`qa\_checker.py`: Runs `ffprobe` and extracts contact sheet grids.**

### ***5. FFmpeg Rendering Architecture**

***The rendering pipeline will avoid heavy libraries like `MoviePy`, relying entirely on `ffmpeg-python` to build a filtergraph.**

- ***Pass 1 (Visuals): A `concat` demuxer file is generated to sequence images. A complex filtergraph applies `zoompan` (Ken Burns), `scale` (forcing 16:9 1080p), and `fade` transitions.**

- ***Pass 2 (Overlays & Audio): Text overlays (`drawtext`), subtitles (`subtitles=file.srt`), and the master audio track are muxed into the video stream.**

- **Why?* FFmpeg handles this natively in C, rendering minutes of video in seconds with minimal RAM, whereas Python-based frame arrays would crash or take hours.**

### ***6. Timeline and Shot-Manifest Formats**

***Movie Builder outputs a Compiled Render Timeline. This is what the Python script actually executes. Notice how all abstract concepts are now raw math:**

```
***`\{`**

`  ***"output\_settings": \{"resolution": "1920x1080", "fps": 30\},`**

`  ***"render\_events": \[`**

`    ***\{`**

`      ***"type": "visual",`**

`      ***"file": "cache/img\_chalkboard\_hash.png",`**

`      ***"start\_time": 0.0,`**

`      ***"end\_time": 4.9,`**

`      ***"filter": "zoompan=z='min(zoom+0.0015,1.5)':d=147",`**

`      ***"transition\_out": "fade"`**

`    ***\},`**

`    ***\{`**

`      ***"type": "overlay\_text",`**

`      ***"text": "14 HOURS LATER",`**

`      ***"font": "Courier New",`**

`      ***"start\_time": 4.9,`**

`      ***"end\_time": 7.4`**

`    ***\}`**

`  ***\]`**

***`\}`**
```

### ***7. AI Image Generation Adapters**

***The system uses a strictly provider-independent interface: `generate\_image(prompt, width, height, style\_reference)`**

- ***Primary Hosted (V1): Hugging Face Serverless Inference API using `FLUX.1-schnell`. (Fast, highly capable with text/chalkboard textures, often available on free/low-cost tiers).**

- ***Fallback Hosted: Hugging Face Dedicated Endpoints (if the user provides a paid token).**

- ***Local Backend: Standard ComfyUI API or `diffusers` script.**

- ***Mock Backend: Instantly generates a gray 1920x1080 JPEG with the prompt written on it (crucial for rapid iteration/testing before spending API credits).**

### ***8. Cost Controls, Caching, and Fallback Behavior**

- ***Caching Hash: `hash(prompt + style\_modifier + aspect\_ratio)`. Checks `assets/images/cache/` before requesting generation.**

- ***Budgeting: The API wrapper tracks a local variable `images\_generated\_this\_run`. If it exceeds a user-defined config (e.g., `max\_images: 10`), it gracefully falls back to the Mock Backend.**

- ***Asset Reuse: Enforces Story Director's `asset\_id` references to literally copy/paste the same file path into the timeline.**

### ***9. QA Methodology**

- ***Deterministic QA (Fast):**

  - ***Compare `ffprobe` output duration to `audio\_timeline.json` duration. If delta \> 0.5s, flag a warning.**

  - ***Run FFmpeg `blackdetect` filter to catch accidental gaps in the `concat` file.**

- ***Visual QA (Advisory):**

  - ***Extract frames exactly at the midpoint of every shot.**

  - ***Stitch them into a 3×3 grid image (`contact\_sheet.jpg`).**

  - ***Save a JSON report mapping shot IDs to timestamps so the user can visually verify pacing without watching the whole video.**

### ***10. Implementation Milestones**

- ***M1 (The Assembly): Build the Python compiler to take static folder of images + MP3 + JSON timestamps -\> valid FFmpeg MP4.**

- ***M2 (The Generator): Implement the Image Adapter interface and the caching system. Plug in FLUX.1 via Hugging Face.**

- ***M3 (The Typographer): Implement code-driven overlays (`drawtext`) for precise title cards and subtitle rendering.**

- ***M4 (The QA Check): Add automated `ffprobe` validation and contact sheet generation.**

### ***11. Concrete Test Cases**

1. ***The Over-Budget Test: Set `max\_images = 2`. Pass a script requiring 4 images. Acceptance Criteria:* The video renders successfully with 2 AI-generated images and 2 gray placeholder images.**

2. ***The Title Card Test: Request a hard cut to a black screen with the text "BANG" in white Arial font, tied to an audio anchor. Acceptance Criteria:* Text is cleanly rendered via FFmpeg `drawtext`, not hallucinated as an image by FLUX.**

3. ***The Missing Anchor Test: Pass a timing manifest where a requested anchor word is missing from the audio file. Acceptance Criteria:* The compiler catches the missing anchor, throws a warning, and defaults the cut to the end of the nearest audio segment.**

### ***12. Recommendations for Improving Previous Skills (Architectural Challenge)**

***The current designs for Skills 1 and 2 are strong, but they lack a few specific bridges needed by Movie Builder:**

- ***Change to Story Director (Skill 1): Separation of Prompt and Style.  
The Story Director must output `visual\_subject` ("A student sleeping") and a global `visual\_style` ("Mockumentary photography, cinematic lighting"). If combined, the LLM often forgets to enforce the style on shot 5. Movie Builder's Adapter needs to concatenate them programmatically: `prompt = subject + ", " + global\_style`.**

- ***Change to Narration Studio (Skill 2): Absolute Total Timeline.  
Narration Studio must not only* provide internal clip timestamps. The `audio\_timeline.json` must provide an absolute *T*=0 to *T*=*X* master timeline so the Movie Builder's compiler doesn't have to recalculate silence gaps on the fly.**

- ***Change to Story Director (Skill 1): Default Fallback Intent.  
If an anchor word is completely mispronounced and `stable-ts` misses it, what should the visuals do? Story Director needs a `fallback\_behavior` key (e.g., `fallback: "cut\_at\_segment\_end"`).**


### ***Ideas Worth Revisiting in Round 4**

- ***Dynamic Background Music (BGM): We haven't established who picks the music. Does Story Director request "tense ambient music"? Does Movie Builder source it from a free library and apply automatic FFmpeg volume ducking when characters speak?**

- ***Aspect Ratios & Platform Export: Should Movie Builder automatically compile two versions (16:9 for YouTube, 9:16 padded/cropped for Shorts) from the exact same JSON manifest?**

- ***Regeneration UI: If the visual QA reveals one bad image (e.g., Kevin has 6 fingers), what is the exact command the user types to tell Movie Builder: "Regenerate just shot 4, and re-render the MP4"* without running the whole pipeline?**

***$0.0843,820 tok**

*![](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1MTIiIGhlaWdodD0iNTEyIiBzaGFwZS1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVF1YWxpdHkiIGZpbGwtcnVsZT0iZXZlbm9kZCIgY2xpcC1ydWxlPSJldmVub2RkIiB2aWV3Qm94PSIwIDAgNTEyIDUxMiI+PHJlY3QgZmlsbD0iI0NDOUI3QSIgd2lkdGg9IjUxMiIgaGVpZ2h0PSI1MTIiIHJ4PSIxMDQuMTg3IiByeT0iMTA1LjA0MiIvPjxwYXRoIGZpbGw9IiMxRjFGMUUiIGZpbGwtcnVsZT0ibm9uemVybyIgZD0iTTMxOC42NjMgMTQ5Ljc4N2gtNDMuMzY4bDc4Ljk1MiAyMTIuNDIzIDQzLjM2OC4wMDQtNzguOTUyLTIxMi40Mjd6bS0xMjUuMzI2IDBsLTc4Ljk1MiAyMTIuNDI3aDQ0LjI1NWwxNS45MzItNDQuNjA4IDgyLjg0Ni0uMDA0IDE2LjEwNyA0NC42MTJoNDQuMjU1bC03OS4xMjYtMjEyLjQyN2gtNDUuMzE3em0tNC4yNTEgMTI4LjM0MWwyNi45MS03NC43MDEgMjcuMDgzIDc0LjcwMWgtNTMuOTkzeiIvPjwvc3ZnPgo= "Favicon for anthropic")**Claude Opus Latest**

***Reasoning**

***[https://raw.githubusercontent.com/steveonw/Read-Aloud-Main/main/web/app.js](https://raw.githubusercontent.com/steveonw/Read-Aloud-Main/main/web/app.js)Auto**

***Reasoning**

***Searched for fal.ai FLUX.1 schnell price per megapixel 20265 results**

***Reasoning**

# ***Movie Builder Skill: Implementation Plan (Round 3 of 4)**

***This is a design only. Nothing has been built or rendered. ⏳ Provisional marks decisions to settle in Round 4.**

**⚠️ *Correction to Round 2 first. In Round 2 I said the Read-Aloud-Main table was "verified from `web/app.js` (checked today)." That wasn't true: the fetch had timed out, so those claims rested on the README and my assumptions. I've now actually read `app.js`. Most of the claims hold. These corrections and additions are now verified:***

> - ***MP3 encoder: The code posts PCM to `mp3-worker.js` at 64 kbps. I called it LAME, but I haven't checked which library it uses.***

> - ***New finding on gaps. The gap rule first checks the previous sentence's last character. Any line that doesn't end in `. ! ? … : ; ,` gets the short continuation gap (at most 0.12 s), and that check runs before the paragraph check. So a heading or title line with no punctuation never gets a paragraph pause, even when a blank line follows it. That matters if the user narrates title cards in Read-Aloud.***

> - ***Cache clearing: Switching speaker or delivery preset keeps the cache, because both are part of the cache key. Only switching voice clears it.***

> - ***Sample rate: Assembly uses the first clip's sample rate for every clip. Pitch is clamped to 0.85–1.15.***

> - ***Labels: They run from clip start to clip end and include the engine's padding, with the spoken text after pronunciation substitution. Confirmed.***


## ***Core design decisions**

1. ***The timeline is counted in frames. Seconds from `narration.json` are converted to integer frame numbers once, in one place. Ordinary cuts round to the nearest frame. Reveal cuts round up (*f*=⌈*t*⋅fps⌉), so rounding can never show a punchline early.**

2. ***The audio sets the length. The video has \\lceil \\text\{audio\_seconds\} \\cdot \\text\{fps\} \\rceil frames, plus a configured tail. If the visuals come out short, the last shot is held longer. Visuals can never cut the audio short.**

3. ***Movie Builder makes no creative decisions. With a plan, it compiles. Without one, it falls back to a clearly labeled pause-aware slideshow heuristic. It never claims that heuristic is creative direction.**

4. ***Each shot is a cached render unit. A shot clip's cache key covers everything that affects its pixels. Replacing one image re-renders that shot, its neighboring transitions and the final pass. Nothing else is redone.**

5. ***Visuals have two layers. A shot is a base asset plus optional overlays (cards, labels, captions). Text is never baked into a generated image.**


## ***Can the earlier plans support reliable rendering? Not yet.**

***Rounds 1 and 2 cover what* to show and when* speech happens. They don't settle several things the renderer needs. I'm recording these as proposed changes for Round 4, not editing the earlier plans.**

| \# | Gap | Why rendering needs it | Proposed fix | Owner |
| - | - | - | - | - |
| 1 | **Ambiguous anchor edges.** **`edge: end`** could mean clip end (exact) or voiced end (measured). Round 2 provides both. | Clip edges include engine padding (confirmed in Read-Aloud), so a cut on "clip end" lands 100–400 ms late | A fixed resolution order (see §6). Segment edges resolve to **voiced** times by default | Shared resolver |
| 2 | **No framing data.** Round 1 has camera names like **`slow\_zoom\_in`**, but nothing about *where in the image* the subject is | A zoom "to Kevin's face" needs a point to zoom toward. The Director can't know where a generated image put the face | The Director adds \`framing: \{target: "face | subject |
| 3 | **No overlays.** Each Round 1 shot has exactly one asset | The layered approach (an image with a stat on top) is impossible without them | **`overlays: \[\{asset, layout, start?, end?\}\]`** on each shot | Director |
| 4 | **Card layout.** Only template names exist | Is a card full-screen, a lower third, or on top of the image? | \`layout: fullscreen | lower\_third |
| 5 | **Transition length and placement** are undefined | A fade takes time from somewhere, and a fade into a reveal must not start before the anchor | **`transition: \{type, dur?\}`**, with placement rules in §6 | Builder |
| 6 | **Lead-in, tail and sound effects are missing.** The original handoff had sound effects and music ducking; neither Round 1 nor Round 2 models them | What plays before the first word? What plays after the last? | Settings **`lead\_in`** and **`tail`**, plus \`sfx: \[\{file | tag, at: anchor, gain\}\]\` on the plan |
| 7 | **Caption mode isn't shared.** Word-level captions need word timing for *every* segment, but Round 2 only times words when asked | Without it, karaoke-style captions are impossible | \`settings.captions: none | sentence |
| 8 | **Captions can spoil punchlines.** Neither earlier plan mentions this | A caption chunk showing "…pressed the fire button. Bang." gives the joke away before "Bang" is spoken | Caption chunks **must break at every reveal anchor**. Validator rule C3 | Builder |
| 9 | **No rule for segments missing from the recording.** Round 2 marks skipped sentences **`status: missing`** | A shot anchored to an absent sentence has nowhere to go | Move the shot to the next available anchor and flag it. If it's critical, raise an error | Builder |
| 10 | **No resolution needs for motion.** Round 1 doesn't say how far shots zoom | A 1024 px generated image zoomed 1.3× looks soft at 1080p | **`max\_zoom`** limited by source resolution; Movie Builder requests a larger size or an upscale | Builder |
| 11 | **`status: "reuse"` on assets** (Round 1) is redundant | Reuse is just two shots pointing at the same asset ID. The extra field can drift out of sync | Drop it | Director |
| 12 | **No shared overrides format** | All three Skills mention **`overrides.json`**, but none defines it | Proposal in §6 | Shared |

***My answer: with fixes 1–5 and 8, the earlier plans are enough for a reliable first render. Fixes 6, 7, 9 and 10 can wait until after the first watchable video.**


## ***1. Name and triggering description**

```
***`---`**

***`name: movie-builder`**

***`description: \>`**

`  ***Assembles finished MP4 videos from images, video clips, narration audio,`**

`  ***and timing data using FFmpeg. Builds narrated slideshows, explainers, and`**

`  ***storyboard animatics with cuts, holds, zooms, pans, fades, code-rendered`**

`  ***title cards and charts, and timed captions. Syncs visuals to speech using`**

`  ***narration.json, SRT, Audacity labels, or detected pauses. Compiles a`**

`  ***story-director plan.json into a frame-accurate timeline automatically.`**

`  ***Optionally generates missing images through hosted or local providers with`**

`  ***cost estimates and caching. Produces contact sheets and QA reports`**

`  ***(duration, black frames, gaps, captions, format). Use to render, re-render,`**

`  ***check, or fix a video. Does not write stories, plan creative direction, or`**

`  ***synthesize narration.`**

***`---`**
```


## ***2. Standalone use cases**

| Use case | Inputs | How timing is decided |
| - | - | - |
| **Pause-aware slideshow** | A folder of images and an MP3 | Silence detection finds pauses of at least 0.35 s ⏳. Images are spread in filename order, each cut snapped to the pause nearest an even-length target. **It's a fallback, not direction, and the report says so** |
| **Quote-anchored slideshow** | Images, audio, a script or SRT, and a simple **`shots.yaml`** | The user writes **`at: "fourteen hours"`**. The phrase is fuzzy-matched against word or caption timings |
| **Read-Aloud handoff** | Read-Aloud WAV plus its label file | Labels give segment boundaries. **Voiced onset is detected again**, because labels include padding. Spoken label text is matched back to display text by fuzzy matching |
| **Explainer with cards** | Audio, timing, a card list | Cards are code-rendered from templates |
| **Mixed media** | Images and short video clips | Clips are trimmed and scaled to cover the frame; their original audio is muted by default. No speed ramps |
| **Captions only** | An existing MP4 plus SRT or **`narration.json`** | Burned-in or sidecar captions |
| **QA only** | Any MP4, optionally with a timeline | Technical report and contact sheet |
| **Animatic** | Only **`plan.json`** and **`narration.json`**, no images yet | Every asset becomes a **placeholder card** showing its prompt. A full-length, correctly timed preview costs nothing |

***The animatic mode is the most useful thing to build first. It tests the whole timing chain before any money is spent on images.**

***Example `shots.yaml` for standalone use (no IDs required):**

```
***`fps: 30`**

***`captions: sentence`**

***`shots:`**

`  ***- image: 01\_classroom.png`**

`  ***- image: 02\_board.png      ; at: "The first frame took"   ; camera: slow\_zoom\_in`**

`  ***- card:  "14 HOURS LATER"  ; at: "fourteen hours"         ; reveal: true`**

`  ***- image: 05\_sfx\_guy.png    ; at: "Bang"                   ; reveal: true ; transition: cut`**

`  ***- image: 06\_paperwork.png  ; after: "Bang"                ; hold: through\_pause`**
```


## ***3. Working with the other Skills**

```
***`script.json ─┐`**

***`plan.json ───┼─► \[load + hash check\] ─► \[resolve anchors\] ─► \[apply overrides\]`**

***`narration.json┘                                  │`**

***`overrides.json ─────────────────────────────────┘`**

`                                                 ▼`

`                        ***\[constraint pass + frame quantize\] ─► timeline.json`**

`                                                 │                │`

`                         ***\[asset builder: cache → provider → placeholder\]`**

`                                                 ▼`

`                ***\[per-shot render\] ─► \[concat\] ─► \[captions + audio mix + loudness\] ─► final.mp4`**

`                                                 ▼`

`                              ***qa\_report.json + contact\_sheet.png`**
```

- ***No manual shot assignment. If `plan.json` covers every segment and validates, the user runs one command.**

- ***Hash chain: `plan.script.sha256` must equal `narration.script.sha256`, and `narration.audio.sha256` must equal the hash of the WAV on disk. A mismatch is a hard error with a plain explanation, such as "narration was regenerated after this plan; re-run resolve."**

- ***Partial plans are fine. Segments no shot covers get the previous shot held over them. If the gap is longer than about 8 s ⏳, a warning is raised.**


## ***4. `SKILL.md` and supporting files**

```
***`\# Movie Builder`**

***`\#\# What it does / does not do`**

***`\#\# Detect environment     → ffmpeg present? version? libass? fonts? network for providers?`**

***`\#\# Choose a mode          → table from §2`**

***`\#\# Core rules`**

`   ***1. Audio length is authoritative; video never shorter.`**

`   ***2. Never move a critical or reveal anchor earlier. Ever.`**

`   ***3. No creative choices; without a plan, say "heuristic slideshow".`**

`   ***4. Estimate cost and get approval before paid generation over the threshold.`**

`   ***5. A failed asset becomes a labeled placeholder; the render never blocks.`**

`   ***6. Report what was dropped, moved, or substituted.`**

***`\#\# Workflow: compile → build assets → render → QA`**

***`\#\# Fixing one thing       → how overrides target a shot/asset`**

***`\#\# When things go wrong`**

***`movie-builder/`**

`├── ***SKILL.md`**

`├── ***references/`**

`│   ├── ***timeline-schema.md       \# timeline.json, overrides.json`**

`│   ├── ***resolver-rules.md        \# anchor precedence, constraint order (§6)`**

`│   ├── ***render-profiles.md       \# 16:9 1080p30, 9:16, draft 540p`**

`│   ├── ***camera-moves.md          \# exact math for each move`**

`│   ├── ***card-templates.md        \# template params`**

`│   ├── ***providers.md             \# capability matrix, setup, licenses`**

`│   ├── ***pricing.yaml             \# prices WITH verified\_on dates`**

`│   └── ***qa-checks.md             \# every check, threshold, rationale`**

`├── ***assets/`**

`│   ├── ***templates/               \# chalk\_title, stat, quote, chart, lower\_third (JSON + fonts)`**

`│   ├── ***fonts/                   \# OFL-licensed only`**

`│   └── ***schemas/                 \# timeline, overrides, shots.yaml`**

`└── ***scripts/`**

`    ├── ***compile.py               \# plan/shots.yaml + timing → timeline.json`**

`    ├── ***resolve.py               \# anchor resolution (candidate shared module)`**

`    ├── ***assets.py                \# cache, provider chain, placeholders, framing boxes`**

`    ├── ***providers/               \# folder, placeholder, hf, fal, comfyui, diffusers`**

`    ├── ***cards.py                 \# Pillow templates; matplotlib for charts`**

`    ├── ***render\_shot.py           \# one shot → clip`**

`    ├── ***render.py                \# orchestration, concat, final pass`**

`    ├── ***captions.py              \# chunking, ASS/SRT, safe zones`**

`    ├── ***mix.py                   \# narration + music envelope + sfx`**

`    ├── ***qa.py                    \# all deterministic checks`**

`    └── ***contact\_sheet.py`**
```


## ***5. FFmpeg rendering architecture**

### ***Per-shot rendering, then concatenation, then one final pass**

| Stage | How | Why |
| - | - | - |
| **Asset prep** | Images are scaled to *cover* a working canvas: 1920×1080 for static shots, larger for motion within the **`max\_zoom`** limit. Cards are rendered as RGBA PNGs with Pillow | Gives the same input to every later stage |
| **Static shot** | **`ffmpeg -loop 1 -i img -t N`**, with overlays added through the **`overlay`** filter | Fastest path |
| **Moving shot** | A Python frame generator crops each frame at sub-pixel positions (Pillow affine transform with bicubic sampling) and pipes raw frames to FFmpeg | Avoids **`zoompan`**'s integer-rounding jitter. The math is ours, so it's testable. Fallback: **`zoompan`** on a 4× upscaled source |
| **Transitions** | Cuts need nothing. A fade becomes a **transition clip** covering only the fade window, blending the last frames of one shot with the first frames of the next | Shot clips stay independent and cacheable. A changed shot re-renders its body plus at most two transition clips |
| **Concat** | The concat demuxer with stream copy. All intermediates share codec, pixel format (**`yuv420p`**), frame rate (constant), resolution and timebase | No re-encoding. The parameters are pinned in the render profile |
| **Final pass** | Concatenated video → burned ASS captions (libass) → mux with the mixed audio → H.264 + AAC 48 kHz → **`+faststart`** | Video is re-encoded once in total |

***The cost of this design: the intermediates are encoded once (CRF about 14 ⏳) and then re-encoded in the final pass (CRF about 18–20 ⏳). That's two lossy generations. If captions are off, the final pass copies the video stream instead and there's no second generation. I haven't measured the quality loss.**

***Shot cache key: `sha256(asset file hashes + overlay hashes + camera params + framing box + duration in frames + profile + renderer version)`.**

### ***Camera moves (`camera-moves.md`)**

- ***The vocabulary from Round 1: `static`, `slow\_zoom\_in`, `slow\_zoom\_out`, `slow\_push`, `pan\_left`, `pan\_right`, plus `drift`, a slow random-walk pan with a fixed seed.**

- ***Every move is defined as a crop rectangle over time, using ease-in-out, and aims at the asset's framing box.**

- ***Defaults: zoom from 1.0 to 1.12 over the shot, capped by `max\_zoom = source\_width / output\_width × 0.9` ⏳. Pans move at most 8% of the frame width.**

- ***Reveal shots default to `static` for the first 0.5 s, so the joke lands on a stable image.**

### ***Audio**

- ***The narration WAV is the base track and is never time-stretched.**

- ***Music ducking without sidechain detection: speech intervals are known from `narration.json`, so a volume envelope is built ahead of time, at −18 dB ⏳ under speech with 250 ms ramps. It's deterministic and easy to test.**

- ***Sound effects are placed at resolved anchors.**

- ***The final mix is normalized to an integrated loudness target, about −14 LUFS for YouTube with true peak ≤ −1 dBTP ⏳. This is the commonly cited YouTube reference, not something I've verified.**


## ***6. Timeline and shot-manifest formats**

### ***Anchor resolution (`resolver-rules.md`)**

| Anchor | Resolves to, in order of preference |
| - | - |
| Word **`start`** / **`end`** | Word time by source: **`manual`** \> **`exact`** \> **`measured`** \> **`aligned`** \> **`model`** \> **`interpolated`** |
| Segment **`start`** | **`voiced.start`**, falling back to clip **`s0`** |
| Segment **`end`** | **`voiced.end`**, falling back to clip **`s1`** |
| **`into\_pause`** | Start of the silence after that segment |
| Quoted phrase (standalone) | Fuzzy match over timed words or captions; best score ≥ 0.8 ⏳, otherwise unresolved |

***Every resolved time records `resolved\_src` and a `confidence` of `high`, `medium` or `low`. If a critical anchor resolves with low confidence, a QA warning is raised.**

### ***Constraint pass (deterministic and ordered)**

1. ***Resolve all starts, then apply nudges and overrides.**

2. ***Sort by start. Two shots resolving to the same frame is an error, reported with both IDs.**

3. ***Each shot's end is the next shot's start, unless it has an explicit `end` or `hold`.**

4. ***Holds: `through\_pause` extends the shot to the end of the silence. If the next shot is anchored inside that pause, the hold wins, unless the next shot is `critical`. Either way it's reported.**

5. ***Minimum duration is 1.0 s ⏳. A too-short non-critical shot may have its start pushed later by up to 0.5 s; if it's still too short, it's dropped and reported. A critical shot is never moved, so the previous* shot gets shortened instead.**

6. ***Fades: default 0.4 s, capped at 25% of either neighboring shot. Normal fades are centered on the cut. A fade into a reveal shot starts at the anchor frame, so the incoming image's first visible frame is never before the anchor.**

7. ***The first shot starts at frame 0 (it covers the lead-in). The last shot runs to the end of the audio plus the tail (default 1.0 s ⏳, hold then fade to black).**

8. ***Convert to frames: reveals round up, everything else rounds to nearest.**

9. ***Coverage is complete by construction. Any gap or overlap is a bug and stops the run.**

### ***`timeline.json` (example; values are illustrative)**

```
***`\{`**

`  ***"schema": "movie-builder/timeline@0.1",`**

`  ***"profile": \{"w": 1920, "h": 1080, "fps": 30, "pix\_fmt": "yuv420p"\},`**

`  ***"inputs": \{"plan": "sha256:…", "narration": "sha256:…", "audio": "sha256:7c1e…",`**

`             ***"overrides": "sha256:…"\},`**

`  ***"total\_frames": 2041,`**

`  ***"shots": \[`**

`    ***\{"id": "fire\_board", "asset": "img\_classroom\_wide", "f0": 1786, "f1": 1913,`**

`     ***"camera": \{"move": "slow\_zoom\_in", "from": 1.0, "to": 1.10,`**

`                ***"target\_box": \[0.38, 0.22, 0.62, 0.58\]\},`**

`     ***"transition\_in": \{"type": "fade", "f0": 1780, "f1": 1792\},`**

`     ***"start\_from": \{"seg": "s012", "word": 4, "t": 60.95, "src": "model", "conf": "medium"\}\},`**

`    ***\{"id": "bang", "asset": "img\_sfx\_guy", "f0": 1913, "f1": 1946,`**

`     ***"camera": \{"move": "static"\}, "transition\_in": \{"type": "cut"\}, "reveal": true,`**

`     ***"start\_from": \{"seg": "s013", "word": 1, "t": 63.762, "nudge": -0.05,`**

`                    ***"t\_final": 63.712, "rounding": "ceil", "src": "measured", "conf": "high"\}\},`**

`    ***\{"id": "aftermath", "asset": "img\_aftermath", "f0": 1946, "f1": 2041,`**

`     ***"camera": \{"move": "slow\_push", "to": 1.06, "target\_box": \[0.30, 0.20, 0.55, 0.70\]\},`**

`     ***"overlays": \[\],`**

`     ***"hold": \{"kind": "through\_pause", "until\_t": 66.315\},`**

`     ***"intent": "deadpan: hold longer than comfortable"\}`**

`  ***\],`**

`  ***"captions": \[`**

`    ***\{"f0": 1786, "f1": 1913, "text": "By day eight, Kevin finally pressed the fire button.",`**

`     ***"pos": "bottom"\},`**

`    ***\{"f0": 1913, "f1": 1946, "text": "Bang.", "pos": "bottom", "split\_reason": "reveal\_anchor"\}`**

`  ***\],`**

`  ***"audio": \{"narration": "narration.wav", "music": null, "sfx": \[\]\},`**

`  ***"decisions": \[`**

`    ***\{"shot": "aftermath", "msg": "hold extended 0.42 s to cover deadpan pause"\}`**

`  ***\]`**

***`\}`**
```

***Here "Bang." gets its own caption chunk because of rule C3: captions must break at every reveal anchor. Everything resolved to seconds or frames is generated output, and nobody edits it by hand. Humans edit `overrides.json`.**

### ***`overrides.json` (proposed shared format)**

```
***`\{`**

`  ***"schema": "shared/overrides@0.1",`**

`  ***"shots": \{`**

`    ***"bang":      \{"nudge": -0.10, "transition": "cut"\},`**

`    ***"aftermath": \{"camera": "static", "hold\_min": 3.0\}`**

`  ***\},`**

`  ***"assets": \{`**

`    ***"img\_sfx\_guy": \{"lock": true\},`**

`    ***"img\_aftermath": \{"replace\_with": "assets/user/kevin\_paperwork.jpg"\}`**

`  ***\},`**

`  ***"absolute": \[`**

`    ***\{"shot": "fire\_card", "start\_t": 58.40, "valid\_for\_audio": "sha256:7c1e…"\}`**

`  ***\]`**

***`\}`**
```

***An absolute time applies only to the audio file whose hash it names. If the audio changes, the override is ignored with a warning, as proposed in earlier rounds.**


## ***7. AI image generation adapters**

### ***Interface**

```
***`class ImageProvider(Protocol):`**

`    ***name: str`**

`    ***def capabilities(self) -\> Caps: ...`**

`        ***\# sizes (multiple-of rule, max MP), seed support, seed determinism,`**

`        ***\# negative prompts, reference images, license of model, price unit`**

`    ***def available(self) -\> Availability: ...     \# cheap check; no billable call`**

`    ***def estimate(self, req: ImageRequest) -\> Cost: ...   \# amount, unit, verified\_on`**

`    ***def generate(self, req: ImageRequest) -\> ImageResult: ...`**
```

***`ImageRequest` = `\{asset\_id, prompt (fully assembled), style\_block, character\_refs\[\], seed, w, h, negative?\}`. Movie Builder assembles the final prompt from the Director's prompt, the style preset and character anchors, because prompt syntax differs between models (provisional in Round 1; I'm proposing Movie Builder owns assembly).**

### ***Providers**

| Provider | Version | Notes |
| - | - | - |
| **`folder`** | v1 | User-supplied images matched by asset ID or filename. Always first in the chain |
| **`placeholder`** | v1 | A styled card showing the asset ID and a short prompt. Always last in the chain |
| **`hf`** (Inference Providers through **`huggingface\_hub`**) | v1 or v2 | A model being on the Hub doesn't mean anyone hosts it. The adapter must check which providers actually serve that model (I believe the Hub API can return a model's inference-provider mapping, but I haven't verified the exact call) |
| **`fal`** | v1 or v2 | Direct API. Pricing below |
| **`replicate`**, others | later | Same interface |
| **`comfyui`** (local HTTP API) | later | For users with GPUs. Workflow JSON lives in config |
| **`diffusers`** (local) | later | Schnell needs a large GPU; quantized versions need less. I haven't measured either |

***"Downloadable" and "hosted" are separate facts in config:**

```
***`models:`**

`  ***flux-schnell:`**

`    ***hub\_id: black-forest-labs/FLUX.1-schnell`**

`    ***license: apache-2.0            \# recorded per model; checked against settings.commercial`**

`    ***hosted\_via: \[fal, hf:auto\]     \# where an endpoint was confirmed to exist`**

`    ***local\_via: \[comfyui, diffusers\]`**
```

***If `settings.commercial: true` and a model's license is non-commercial or unknown, Movie Builder refuses to use it, and says why. FLUX.1 \[dev\] is the obvious example to watch for.**

***Character consistency, cheapest first: reuse and crop an existing character image → text anchors from the Director → reference-image editing models, only when the provider reports `supports\_references` and the style preset needs consistency (e.g., `illustrated\_story`).**


## ***8. Cost controls, caching and fallbacks**

### ***Prices**

| Item | Status |
| - | - |
| fal FLUX.1 \[schnell\]: **0.003 USD per megapixel, billed by rounding up to the nearest megapixel** | **Verified today** on fal's model page |
| A full 1920×1080 image (2.07 MP): 0.006 or 0.009 USD | **Uncertain.** It depends on how fal defines a megapixel. A third-party tracker lists it at 0.006 USD; I haven't confirmed which applies |
| Replicate about 0.003 USD per image, Together about 0.0027 USD/MP, Runware lower | Third-party tracker, not checked on the vendors' own pages |
| Hugging Face PRO pricing and included credits | Reported in an earlier round. **Recheck at build time** |

***Recommendation: generate at 1024×576 (about 0.59 MP, billed as 1 MP on fal) and upscale. Estimate: a 3-minute DOOM video with about 15–20 unique images plus about 30% retries costs roughly 0.06–0.08 USD.**

***`pricing.yaml` stores a `verified\_on` date for every price. If a price is more than 60 days old ⏳, the estimate is labeled stale.**

### ***Controls**

- ***Dry run by default for paid providers. It reports cached assets, assets to generate, the provider, and the estimated cost range.**

- ***`budget.max\_usd`, `budget.max\_new\_images` and `auto\_approve\_under\_usd` (default 0.25 USD ⏳). Anything above that needs the user's confirmation.**

- ***Retry caps: at most 2 regenerations per asset and a 30% retry budget for the whole run ⏳. When either runs out, the asset becomes a placeholder with a QA error. There are no unbounded loops.**

### ***Caching**

- ***`assets/images/\<sha\>.png`, plus a sidecar file recording the request, provider, model, model revision, seed, cost, license, creation time and framing box.**

- ***The key is the hash of the request, including provider and model. Hosted seeds may not be deterministic, so the cache is what makes results repeatable, not the seed.**

- ***`lock: true` in overrides pins an accepted image even if the Director rewrites its prompt later.**

- ***Cached files never need the provider to stay online.**

### ***Fallback chain**

***`folder → cache → primary provider → secondary provider → placeholder`. Each step records why it moved on, and the render always finishes.**


## ***9. QA methodology**

***A. Input checks (before anything is spent)**

- ***The hash chain is consistent. Every asset file opens and has the expected aspect ratio. Resolution is high enough for the planned zoom.**

- ***Licenses fit the `commercial` setting. Fonts are present. Prompts contain no exact text (the Round 1 heuristic).**

***B. Timeline checks (deterministic, before rendering)**

| ID | Check | Threshold |
| - | - | - |
| T1 | Coverage | Frames 0…N−1 each belong to exactly one shot |
| T2 | Reveal integrity | For every reveal: **`f0 ≥ ceil(anchor·fps)`**, including fades |
| T3 | Payoff asset first use | The asset doesn't appear in any shot before its payoff beat |
| T4 | Hold coverage | Shots marked **`through\_pause`** cover at least 95% of their silence ⏳ |
| T5 | Shot length | 1.0 s ≤ length ≤ 12 s ⏳, unless it's a hold or explicitly allowed |
| C1 | Caption sync | No caption starts before its first word. It may lag by up to 2 frames |
| C2 | Readability | At most 42 characters per line, at most 2 lines, 0.8–7 s on screen, at most about 20 characters per second (common subtitle conventions, not standards) |
| C3 | Caption spoilers | No caption contains a word from a later reveal anchor before that anchor's frame |
| C4 | Safe zones | Captions move to the top when a shot's overlay or **`caption\_safe`** marks the bottom as occupied |

***C. Output checks (deterministic, after rendering)**

- ***Format via `ffprobe`: H.264, `yuv420p`, 1920×1080, constant 30 fps, AAC at 48 kHz, `faststart`.**

- ***Duration: the difference between video and audio is ≤ 1 frame plus the AAC priming delay. Total budget ≤ 50 ms ⏳.**

- ***Black frames: `blackdetect` (d=0.1, pix\_th=0.10 ⏳), ignoring intentionally dark intervals such as the tail fade and dark cards.**

- ***Silence: `silencedetect` compared against `narration.json`'s silences, to catch muxing or offset errors.**

- ***Loudness: `ebur128` against the target.**

- ***Conformance: extract the midpoint frame of every shot and compare its perceptual hash against the expected frame from that shot's clip. This shows the concatenation order and offsets are right.**

- ***Reveal frames: the frame at `f0 − 1` of each reveal hashes to the previous shot.**

***D. Semantic QA (optional, advisory, limited)**

- ***It runs on assets before rendering, not on screenshots afterward, so N assets get checked rather than N×K frames.**

- ***A vision model gets the image, the Director's prompt, `purpose`, `intent` and the beat note, and answers `ok`, `doubtful` or `wrong` with one sentence.**

- ***Shots tagged `intent: ironic\_contrast` are told that a mismatch is intended.**

- ***It never regenerates on its own beyond the retry caps and budget. A `wrong` verdict proposes a fix, which needs approval if it would cost money.**

***Contact sheet (always produced). A grid with one row per shot: thumbnails at start and middle, the shot ID, start time, caption text and colored QA flags. There's also a punchline strip for each reveal, showing frames at −2, 0 and +2 frames around the anchor, plus one frame halfway through any following hold.**

```
***`\{"summary": \{"errors": 0, "warnings": 2, "placeholders": 0, "cost\_usd": 0.054\},`**

` ***"issues": \[`**

`   ***\{"code": "anchor\_low\_conf", "shot": "door\_rage", "t": 88.4,`**

`    ***"msg": "word 'door' timed by interpolation; verify cut"\},`**

`   ***\{"code": "hold\_short", "shot": "aftermath", "t": 64.3,`**

`    ***"msg": "hold covers 0.8 s of a 'deadpan' pause; plan expected ≥1.5 s"\}\]\}`**
```


## ***10. Implementation milestones**

| \# | Scope | Proves |
| - | - | - |
| **B0** | Timeline and overrides schemas, resolver rules, DOOM fixture files (**`plan.json`**, **`narration.json`**) | The interface between the Skills |
| **B1** | **Standalone static render:** images, audio and **`shots.yaml`** with seconds or quoted phrases; hard cuts; SRT captions; format and duration QA | First playable MP4 |
| **B2** | **Compiler + animatic:** **`plan.json`** + **`narration.json`** → **`timeline.json`** → MP4 made entirely of placeholder cards | The full timing chain with **no image spending** |
| **B3** | Camera moves (frame generator), fades as transition clips, per-shot cache | Motion quality and re-rendering one shot |
| **B4** | Card templates, overlays, caption chunking with spoiler breaks, safe zones | Layered composition and C1–C4 |
| **B5** | Image providers: folder, placeholder and one hosted; cost estimator; asset cache | Automatic visuals within a budget |
| **B6** | Full deterministic QA, contact sheet, punchline strip | The checks in §9 |
| **B7** | Music envelope, sound effects, loudness target | Audio polish |
| **B8** | Advisory semantic QA, pre-render | Catching irrelevant images |

***The first real demo is B2 + B5 together: the 60–90 s DOOM excerpt. The original challenge only asked for a 60–90 s excerpt with 8–12 images; B3 polish can follow.**


## ***11. Test cases and acceptance criteria**

1. ***Reveal rounding: an anchor at 63.712 s at 30 fps lands at frame 1912 (63.733 s), never 1911. Check this for a hundred random anchors.**

2. ***Fade into a reveal: the incoming image's first non-zero blend frame is ≥ the anchor frame.**

3. ***Padding: with Read-Aloud-style labels and 200 ms of synthetic lead padding, a segment-start cut lands within 1 frame of the true voiced onset, not at the label start.**

4. ***Hold conflict: a non-critical shot anchored inside a deadpan pause is pushed past the pause and reported. A critical one isn't moved, and that's reported.**

5. ***Minimum-duration drop: two shots 0.4 s apart become one, and the report names the dropped shot.**

6. ***Missing segment: a shot anchored to a `status: missing` segment moves to the next anchor (warning). If it's critical, the run errors.**

7. ***Stale override: an absolute-time override for a different audio hash is ignored with a warning.**

8. ***Determinism: the same inputs produce a byte-identical `timeline.json`.**

9. ***Duration: for 5 test audio lengths (including ones that aren't whole frames), |video − audio| ≤ 50 ms and the video is never shorter.**

10. ***Replace one image: swapping one asset re-renders exactly 1 shot clip, at most 2 transition clips and the final pass. Verified from the render log.**

11. ***Change one nudge: at most 2 shot clips (the neighbors whose lengths change) plus the final pass. Zero image generations and zero LLM calls.**

12. ***Motion smoothness: for a 10 s `slow\_zoom\_in`, the crop rectangle changes monotonically every frame with no repeated positions. Tested on the generator's output, not by eye.**

13. ***Concat compatibility: every intermediate's `ffprobe` stream parameters are identical.**

14. ***Spoiler caption: a planted caption chunk that spans a reveal fails C3. The compiler's own output passes.**

15. ***Cost gate: with `auto\_approve\_under\_usd: 0.10` and an estimate of 0.20 USD, nothing is generated until the user confirms.**

16. ***Provider failure: a provider that always fails produces placeholders, a finished render and QA errors listing those assets. Total calls ≤ the retry cap.**

17. ***License gate: `commercial: true` with a model whose license is non-commercial means the model is refused before any call.**

18. ***Black-frame plant: an accidental 0.5 s black asset is detected at the correct time. The intended tail fade isn't flagged.**

19. ***Animatic: the DOOM fixture renders with zero image calls, and its contact sheet shows every planned shot.**

***Acceptance for the DOOM demo:**

- ***All tests above pass.**

- ***The "14 HOURS LATER" card and the "Bang" shot start within 0 to +2 frames of their anchors.**

- ***The aftermath hold covers the deadpan pause.**

- ***Spending is ≤ 0.25 USD.**

- ***One viewer who hasn't read the story can retell the premise. That last one is the only subjective criterion.**


## ***12. Recommendations for Rounds 1 and 2**

***Story Director (Round 1)**

1. ***Add `framing`, `overlays`, `layout` and `sfx` (gaps 2, 3, 4, 6).**

2. ***Drop `assets.\*.status: "reuse"`; reuse is implied by shared IDs.**

3. ***Stop writing fully assembled prompts. Write a `subject` prompt; Movie Builder adds the style block and character anchors for each model.**

4. ***Add `caption\_safe: bottom | top | none` on images, replacing the free-text composition note.**

5. ***Use a small transition vocabulary with optional durations: `cut`, `fade`, `fade\_black`.**

6. ***Plan-only animatics: Story Director's standalone output could include a "preview with Movie Builder" path, because placeholder animatics cost nothing.**

***Narration Studio (Round 2)**

1. ***Write down that segment edges resolve to `voiced` times by default.**

2. ***Use `settings.captions` to decide which segments need word timing.**

3. ***Export speech-active intervals directly, since the music envelope needs them.**

4. ***If audio comes from Read-Aloud, warn about headings without punctuation getting only the short gap (verified above). Suggest a period or a pronunciation-dictionary trick.**

5. ***Add `lead\_in` to `narration.wav` (or leave it to Movie Builder, but not both). ⏳ I lean toward Movie Builder, so narration audio stays reusable on its own.**


## ***Top three risks**

1. ***Render speed of the Python frame generator. Piping Pillow-transformed 1080p frames could be slow for long videos. I haven't measured it. The fallback is `zoompan` on an upscaled source, and B3 has to benchmark both.**

2. ***Two lossy encodes (intermediates plus burned captions) may visibly soften chalk textures. Measure at B3. The fix is higher-quality intermediates, at the cost of disk space.**

3. ***Hosted image availability and seed behavior can change without notice. The cache and `lock` protect finished projects, but new projects may get a different visual style from the same prompts.**


## ***Ideas Worth Revisiting in Round 4**

1. ***Shared resolver module. `resolve.py` is needed by Movie Builder and could be shipped by Narration Studio as `anchors\_resolved.json`. Decide on one implementation to avoid two that drift apart. It's the twin of the shared `scriptkit.py` question.**

2. ***One `style.yaml` for all three Skills: visual preset, voices, pacing energy, card templates, caption mode, fonts, aspect ratio.**

3. ***The animatic as the default first output. Plan → narration → placeholder animatic → approve → generate images. It's free, catches most timing and direction errors, and keeps the "start with a working movie" principle.**

4. ***Duration-aware re-planning loop. Movie Builder's `decisions` and QA issues (dropped shots, short holds, 30 s on one image) are exactly what a Director revision pass needs. Decide whether it's one automatic pass, user-triggered, or off.**

5. ***Pause negotiation. A `hold\_short` warning in generated-audio mode could ask Narration Studio for a longer silence. Only assembly reruns; nothing is re-synthesized. Who has the authority to do that?**

6. ***Prompt assembly ownership. I've proposed Movie Builder. Confirm, and define the `subject`, `style\_block` and `character\_anchor` split.**

7. ***Caption ownership. Narration owns timing, Movie Builder owns chunking and layout. Confirm. The spoiler rule needs both reveal anchors and word times, so it naturally lives in Movie Builder.**

8. ***Vertical (9:16). A separate render profile is easy. Real reframing needs `framing` boxes, which this design already stores. Decide whether the Director plans for vertical separately.**

9. ***Flag-while-watching. A review file of `\{shot\_id, t, note\}` entries, built on Read-Aloud's verified anchoring approach (sentence text plus context, re-bound by similarity), could feed revise modes in all three Skills.**

10. ***Minimum viable trio. My answer after three rounds: `script.json`, `plan.shots` + `plan.assets`, `narration.json` (segments with voiced times, silences) and `overrides.json`. Everything else is optional.**

***Ready for Round 4 when you are.**

***5 citations**

*![](data:image/jpeg;base64,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 "Favicon for https://genspend.io/model/flux-1-schnell")![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAsTAAALEwEAmpwYAAAClUlEQVRYhb2XT1IaQRjF3+tYMDGboSrsJycIOYG4G92EnCDmBOoJgBPEnCB6gpiV7BhPIDlBWActZkWhFftlIX9GoIcepPKtX/f3657ufm8Iz7orH5xI+uqjFXlavb8689EaXwBBH321RvjsrfUVQqx5S4FoqwCDIK4DCn0nBRQ+jdkSAK3/ls7GCE0v3TrBMIijR4vfRQEAQAb71XEn2RhgGMSRtehmvynBVEBC4lpWKQDQMJSwR6omZbXom93gQyW9TAsDDMNGaEf3XUG1aWMLfdvZDc7yJrwN4iMKzSkIwZ4x+lQZd/reAIMgrhuL79OVk+gbYt81yRJ8EEfW8sccHn1jVo9/BjAI4jqFJoT6TFCw+QwCjdCW5js4qXMZXGTPBe/Kh8eQjiBE4vJVe2XwrmjzGUQQR4+WN4tXmGIqox5hLnlbiuWaQEC7+tBpbdJ8WoNS3CLcVzL3HdgxOH9JcwDYeQjOADoPrRuASDbd+mxVcJla6GdxAPDXS5vPZiJ7hQEE9LcGMHmwCgH8r3ICsIClrisZOp00Zwf0flsABPaKAwj1YdgokAFyKvOy+gMA+Dsan7y091358DgvzBiRpyASrngsCDT/vDn0jmKLNQziCLJLiyCYEuyJPF0yI1kcGcwTUJ6T5TYPG6EdjW+e5UMiEdF+ZkYucit0555eDGLJjom+Jb6sSkfuQLIwyUTcMgYXLpDJqo8hnkydlWTPvC7vu0JMfiRDI7Tl8U02Zk1GJRKuqafXUkREYo+Wtayl+2SJtaF0EMR1WnTX6VaVT5ZY+xRXx50ERLJB/3OfM+PlBSLaRbvL4MJHt/YTTOu2dDD0/zti+vbhquKj9HZDFrFnyun/GwOAflsKAAKdCWix/gF/liXN1kq9AQAAAABJRU5ErkJggg== "Favicon for https://fal.ai/models/fal-ai/flux-1/schnell/llms.txt")![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAsTAAALEwEAmpwYAAAClUlEQVRYhb2XT1IaQRjF3+tYMDGboSrsJycIOYG4G92EnCDmBOoJgBPEnCB6gpiV7BhPIDlBWActZkWhFftlIX9GoIcepPKtX/f3657ufm8Iz7orH5xI+uqjFXlavb8689EaXwBBH321RvjsrfUVQqx5S4FoqwCDIK4DCn0nBRQ+jdkSAK3/ls7GCE0v3TrBMIijR4vfRQEAQAb71XEn2RhgGMSRtehmvynBVEBC4lpWKQDQMJSwR6omZbXom93gQyW9TAsDDMNGaEf3XUG1aWMLfdvZDc7yJrwN4iMKzSkIwZ4x+lQZd/reAIMgrhuL79OVk+gbYt81yRJ8EEfW8sccHn1jVo9/BjAI4jqFJoT6TFCw+QwCjdCW5js4qXMZXGTPBe/Kh8eQjiBE4vJVe2XwrmjzGUQQR4+WN4tXmGIqox5hLnlbiuWaQEC7+tBpbdJ8WoNS3CLcVzL3HdgxOH9JcwDYeQjOADoPrRuASDbd+mxVcJla6GdxAPDXS5vPZiJ7hQEE9LcGMHmwCgH8r3ICsIClrisZOp00Zwf0flsABPaKAwj1YdgokAFyKvOy+gMA+Dsan7y091358DgvzBiRpyASrngsCDT/vDn0jmKLNQziCLJLiyCYEuyJPF0yI1kcGcwTUJ6T5TYPG6EdjW+e5UMiEdF+ZkYucit0555eDGLJjom+Jb6sSkfuQLIwyUTcMgYXLpDJqo8hnkydlWTPvC7vu0JMfiRDI7Tl8U02Zk1GJRKuqafXUkREYo+Wtayl+2SJtaF0EMR1WnTX6VaVT5ZY+xRXx50ERLJB/3OfM+PlBSLaRbvL4MJHt/YTTOu2dDD0/zti+vbhquKj9HZDFrFnyun/GwOAflsKAAKdCWix/gF/liXN1kq9AQAAAABJRU5ErkJggg== "Favicon for https://fal.ai/models/fal-ai/flux/schnell/llms.txt")![](data:image/png;base64,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 "Favicon for https://fal.ai/models/fal-ai/flux-1/schnell")![](data:image/png;base64,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 "Favicon for https://fal.ai/models/fal-ai/flux/schnell")**[FLUX.1 \[schnell\] (Text to Image) API on fal**](https://fal.ai/models/fal-ai/flux-1/schnell)

***[https://fal.ai/models/fal-ai/flux-1/schnell**](https://fal.ai/models/fal-ai/flux-1/schnell)

*[![](data:image/png;base64,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 "Favicon for https://fal.ai/models/fal-ai/flux-1/schnell")](https://fal.ai/models/fal-ai/flux-1/schnell)**[fal.ai**](https://fal.ai/models/fal-ai/flux-1/schnell)

***[FLUX.1 \[schnell\]: Ultra-Fast Text-to-Image AI Generator | fal**](https://fal.ai/models/fal-ai/flux/schnell)

***[https://fal.ai/models/fal-ai/flux/schnell**](https://fal.ai/models/fal-ai/flux/schnell)

*[![](data:image/png;base64,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 "Favicon for https://fal.ai/models/fal-ai/flux/schnell")](https://fal.ai/models/fal-ai/flux/schnell)**[fal.ai**](https://fal.ai/models/fal-ai/flux/schnell)

***[https://fal.ai/models/fal-ai/flux-1/schnell/llms.txt**](https://fal.ai/models/fal-ai/flux-1/schnell/llms.txt)

***[https://fal.ai/models/fal-ai/flux-1/schnell/llms.txt**](https://fal.ai/models/fal-ai/flux-1/schnell/llms.txt)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAsTAAALEwEAmpwYAAAClUlEQVRYhb2XT1IaQRjF3+tYMDGboSrsJycIOYG4G92EnCDmBOoJgBPEnCB6gpiV7BhPIDlBWActZkWhFftlIX9GoIcepPKtX/f3657ufm8Iz7orH5xI+uqjFXlavb8689EaXwBBH321RvjsrfUVQqx5S4FoqwCDIK4DCn0nBRQ+jdkSAK3/ls7GCE0v3TrBMIijR4vfRQEAQAb71XEn2RhgGMSRtehmvynBVEBC4lpWKQDQMJSwR6omZbXom93gQyW9TAsDDMNGaEf3XUG1aWMLfdvZDc7yJrwN4iMKzSkIwZ4x+lQZd/reAIMgrhuL79OVk+gbYt81yRJ8EEfW8sccHn1jVo9/BjAI4jqFJoT6TFCw+QwCjdCW5js4qXMZXGTPBe/Kh8eQjiBE4vJVe2XwrmjzGUQQR4+WN4tXmGIqox5hLnlbiuWaQEC7+tBpbdJ8WoNS3CLcVzL3HdgxOH9JcwDYeQjOADoPrRuASDbd+mxVcJla6GdxAPDXS5vPZiJ7hQEE9LcGMHmwCgH8r3ICsIClrisZOp00Zwf0flsABPaKAwj1YdgokAFyKvOy+gMA+Dsan7y091358DgvzBiRpyASrngsCDT/vDn0jmKLNQziCLJLiyCYEuyJPF0yI1kcGcwTUJ6T5TYPG6EdjW+e5UMiEdF+ZkYucit0555eDGLJjom+Jb6sSkfuQLIwyUTcMgYXLpDJqo8hnkydlWTPvC7vu0JMfiRDI7Tl8U02Zk1GJRKuqafXUkREYo+Wtayl+2SJtaF0EMR1WnTX6VaVT5ZY+xRXx50ERLJB/3OfM+PlBSLaRbvL4MJHt/YTTOu2dDD0/zti+vbhquKj9HZDFrFnyun/GwOAflsKAAKdCWix/gF/liXN1kq9AQAAAABJRU5ErkJggg== "Favicon for https://fal.ai/models/fal-ai/flux-1/schnell/llms.txt")](https://fal.ai/models/fal-ai/flux-1/schnell/llms.txt)**[fal.ai**](https://fal.ai/models/fal-ai/flux-1/schnell/llms.txt)

***[https://fal.ai/models/fal-ai/flux/schnell/llms.txt**](https://fal.ai/models/fal-ai/flux/schnell/llms.txt)

***[https://fal.ai/models/fal-ai/flux/schnell/llms.txt**](https://fal.ai/models/fal-ai/flux/schnell/llms.txt)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAsTAAALEwEAmpwYAAAClUlEQVRYhb2XT1IaQRjF3+tYMDGboSrsJycIOYG4G92EnCDmBOoJgBPEnCB6gpiV7BhPIDlBWActZkWhFftlIX9GoIcepPKtX/f3657ufm8Iz7orH5xI+uqjFXlavb8689EaXwBBH321RvjsrfUVQqx5S4FoqwCDIK4DCn0nBRQ+jdkSAK3/ls7GCE0v3TrBMIijR4vfRQEAQAb71XEn2RhgGMSRtehmvynBVEBC4lpWKQDQMJSwR6omZbXom93gQyW9TAsDDMNGaEf3XUG1aWMLfdvZDc7yJrwN4iMKzSkIwZ4x+lQZd/reAIMgrhuL79OVk+gbYt81yRJ8EEfW8sccHn1jVo9/BjAI4jqFJoT6TFCw+QwCjdCW5js4qXMZXGTPBe/Kh8eQjiBE4vJVe2XwrmjzGUQQR4+WN4tXmGIqox5hLnlbiuWaQEC7+tBpbdJ8WoNS3CLcVzL3HdgxOH9JcwDYeQjOADoPrRuASDbd+mxVcJla6GdxAPDXS5vPZiJ7hQEE9LcGMHmwCgH8r3ICsIClrisZOp00Zwf0flsABPaKAwj1YdgokAFyKvOy+gMA+Dsan7y091358DgvzBiRpyASrngsCDT/vDn0jmKLNQziCLJLiyCYEuyJPF0yI1kcGcwTUJ6T5TYPG6EdjW+e5UMiEdF+ZkYucit0555eDGLJjom+Jb6sSkfuQLIwyUTcMgYXLpDJqo8hnkydlWTPvC7vu0JMfiRDI7Tl8U02Zk1GJRKuqafXUkREYo+Wtayl+2SJtaF0EMR1WnTX6VaVT5ZY+xRXx50ERLJB/3OfM+PlBSLaRbvL4MJHt/YTTOu2dDD0/zti+vbhquKj9HZDFrFnyun/GwOAflsKAAKdCWix/gF/liXN1kq9AQAAAABJRU5ErkJggg== "Favicon for https://fal.ai/models/fal-ai/flux/schnell/llms.txt")](https://fal.ai/models/fal-ai/flux/schnell/llms.txt)**[fal.ai**](https://fal.ai/models/fal-ai/flux/schnell/llms.txt)

***[FLUX.1 \[schnell\] API pricing | GenSpend**](https://genspend.io/model/flux-1-schnell)

***[https://genspend.io/model/flux-1-schnell**](https://genspend.io/model/flux-1-schnell)

*[![](data:image/jpeg;base64,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 "Favicon for https://genspend.io/model/flux-1-schnell")](https://genspend.io/model/flux-1-schnell)**[genspend.io**](https://genspend.io/model/flux-1-schnell)

*![]()**$0.9525,140 tok**

*![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAACXBIWXMAAAsTAAALEwEAmpwYAAAQ0ElEQVR4nO3dMYwTxx7H8b+tV+SyvuKKO4RCcXR0RorESSmSiNcGQmcEJdVrQUrle0VChQRtpEiUPpEugVc/hUiJdJYihQLJCKS74iJ05+IK7+BX3b6CW2IO27e2Z2f+s/P9SNvAnW9s7/zmP7PjdU0U6vV6l1dWVi4eHR19sry8/KmISL/f/3x1dfV/SZIs+W4fMIkxZtjv9z9aXV39VURkMBj8Ua/X/zo8PPzzwoUL//XdvpNqvhsgIrK/v387SZKrInKJDo4qM8YMRaRrjHl85syZB77b4y0AXr9+fX95eflfdHjEzBgzHAwG3589e/aOj7/vNAB6vd7lc+fO/TtJki9c/l0gBMaYp3t7e9+6nCo4CYDjEv8uoz1wOmPM0BjTdjFFKDUA6PjA/FwEQSkBcFzq/4eODyzOGDPc29v7qoypgfUASNP0F+b4gH3GmKeNRuNLm49Zt/VAvV7vcpqmb+j8QDmSJPkiTdM3vV7vsq3HtFIB7O/v315bW7tv47EAnO7g4OCOjbWBhQOAkh/ww8aUYKEAOC75WegDPDHGDBuNxsfz/v7cAUDnB3RYJATmCgA6P6DLvCEwcwDQ+QGd5gmBmQKAzg/oNmsIFN4HcLzaT+cHFEuSZClN01+K/nyhADje08+lPiAASZJ8sb+/f7vIz54aAL1e7zKbfICwrK2t3S+yY/DUNQDm/UCYiqwHTK0AmPcD4SqyHjAxAHq93mXm/UDYkiT5YtpUYOIUgNIfqIZpU4GxFcDxqj+dH6iAJEmWJl0VGFsBMPoD1TKpCvigAmD0B6pnUhXwQQXA6A9U07gq4L0K4Hjln84PVFCSJEsnrwi8VwFwdx+g2k7eRei9AMiyLHPeIgBO1Wq1d/3+3RTg9evX7PcHIjDa198lAYt/QBxGFwPfBQDlPxCPfBpQF3l77d9vcwC4lPf5uohIkiRX/TYHgEt5n88XAS95bAsA9y6JHK8BMP8H4lOr1Wp1m180CCAcvV7vcn1lZeWi74YAcG9lZeVi/ejo6BPfDQHg3tHR0Sf15eXlT303BIB7y8vLnxb+YhAA1VPv9/uf+24EAPf6/f7nNT4DAMTJGDOssQcAiBdrAEDECAAgYgQAEDECAIgYAQBEjAAAIkYAABEjAICIEQBAoIwxw93d3YU28hEAQEC63a5sbm7KxYsXpdFoLF27dm3sN3wXxVZgQLHd3d3s999/rz1+/Fh+/PHHsT+Tpulw3s/z/GOh1gGwyhgzfP78+dKTJ0/k7t27ImO+wfuk58+fL126NN99fQkAwLNutyuvXr2Se/fuybNnz2YeyZ88eSIEABAIY8zw559/XppW1s/i5cuXc/8uawCAA/lc/niUt/7483ZjKgCgJN1uV2aZyy9id3c3W19fn/lvEACAJbZL+1kcHBzU1tfXZ/49AgBYwInLdN5urffq1au5FgIJAGBGJ+bzpZb20zSbTfnmm2/ks88+m6v8FyEAgELy+fyTJ0+8dnoRkXa7Lbdu3Rrt9HO3hwAAJjixiOdVu92WK1eujJb5VkKIAABGaOr0rVZLrl69Kjdu3CjtbxAAiN7u7m728OHDmoZOn8/rv/7667n398+CjUCIkqZOLzJ2Xu8EFQCioWX1PtdqteT27dvW5/WzIABQafnmHC2dXkSk0+ksdOnOJqYAqKRutysPHjxwviNvkjGjvQpUAKgMTSv4uU6n42xBbx5UAAha2Z+ym4fW0X4cKgAEaaTE9z6Pzmkf7cehAkAwtF26EwlrtB+HCgCqaVzFF/F33d42KgCopHFBL9+lV+bWXNeoAKDGidHed3PeCb3Mn4YKAN5pHO1FqlPmT0MFAG+2trZE22gv8sFqfmU7vwgVABzTuJIv8nZ+/8MPP1SyzJ+GCgBOaLxuL1Lt+X0RTgOg2+3K2tqa94qjynM6bbSW+THM7wvJHGq325mIeD9arVaWpukbl889Jjs7O0da3uuTR7vd5r0f4TQAsizLtre3vZ8E+bG9ve366Vfa9vZ21mq1vL+v445Op0PHH8N5AGRZlqVp+kbLidJut328BJXS6XSyZrPp/b2c1PExmZcAyHU6He8niIhkzWaT0WFGaZq+0fL+jXs/6fjFeA2ALNM1JeCkOZ3m+X2z2WRaNyPvAZBjSqDbzs7OkZb3iI5vj5oAyDI9UwIRyXZ2do58vx4aaF7Yo+MvTlUAZNnbkUbLglLMU4Lt7W21C3t0fHvUBUBOyzwztj0Dmlf06fj2qQ2ALNO1QFj1E0/T9IuO747qAMgy9gyUTXvHj3ka5oL6AMhpOVGbzWYlFgi1vJ6TDjq+G8EEQJbpmhKEeoLS8TEqqADIMSWYnfaOH9JrWSVBBkCW6TqhNU8JNL1Okzp+TFdZtAk2ALKMPQPTaO/4rVZLdXDGIugAyLFn4G/aOz6X9HSpRABkma4FQh8nuOadez5fF0xXmQDIsjj3DITQ8bVNj/C3ulRIkiRLjx49kk6n47sp8vLlSzHGDMt6/G63K9evX5eNjQ1199vLtdttSdN0WKVv0qkc3wlUFl9TgrLnuJo/lpsfLPCFo7IBkHPZWcosddM0faNlsdNX+MG+ygdAlpW/Ml726r/2lf2yww/liSIAsqycPQNlj3ghdHw28oQtmgDI2SqjyxzxQljZp9yvhugCIMsWWyAsc4FL02VMX+EHt6IMgCybr7OVeeJrX+ATodyvomgDIFdknl3miR/CPJ9yv7r4enB5u6lmY2Nj7P9tb2+X8s2xu7u72bVr12paN/HkOp2OsJGnuiq1E3Bely5dkizLpNVqvfu3drstWZZZ7/zGmOHm5qacP39ededvtVrs4ouB3wJEn06nU1q5G0K5L1Luh3bynYzsFNSBAHAghMt6IuV/gOnkQidXE/wjAEoUwvZdcbDIN63yabVapf1dnI4AKEko5X6Zo/4slQ9XGfwgACzTdJuy00Z9bRuauDGoewSARSGU+yLlzr0XrXyazSabjRwiACzQdDsyX6O+7YVOpgRuEAALCmHvfpmjfpmfX2BKUD4CYE6hLPKVOeq7eA2q8lVsWhEAMwrlE3tljvo+9jWwZ6AcBMAMYh/1fe9rYM+AfQRAASHciDM/ypw3+35u+cECoT0EwClCGfVFyv+OQk3THxYI7SAAJkjT9E0IG3p8dAYtociegcVxP4Axtra25ObNm76bUUhZ9ys4ze7ubnb+/Pma8z88hq/XoAq4H8AIY8zw+vXrQXT+/PP6vk789fX1WnbiHgq+bGxsyObmpu9mhMlzBaKGlrK2yKHtkpiW1449A7MjALJwdvOJlL/QNy9NH4LSFpCaRR0AoezhFylnoW97e9t6oGj5QBR7BoqJNgC0nKi+RrTR52/78TUFK3sGposuADSVqqcdZcxpJz1/2xUGewbCEFUAaFms8nXSnvb8ywgcLa85ewbGiyYAtIxGRQ7bJfmsVU+VpwQsEL6v8gGg6eQrMkppGYHL+MpzLSHMlOBvlQ6AkBb6tM7BbS+iaZkSiOi9pOpSJQNA0wJUkUN7yW07nDQtxMY+JahcAIRU8ovYH4XKqnrKWETTUqGVMd0JRaUCQMsJVfSks8nVqGp7SqApsGPcM1CJAAit5LddUrueV2tdr9D43LQLPgA0jSBFDtujjK+Oo+mKRRnPLZYpQdABoOWEKXrY7DA7OztHvp+PiP4FTE3PTaNgA0BLyVjkKOODKZrK5jKen5bnVvUpQXABoOkSkoYTSFMVxJ6B8AQVAJrKwyKHqxJSUyiyZyAswQSAptGgyOHjkpKWy6DsGQhHEAGgZT7o6+SfhaYqiT0D+qkOgJBuzS2i5y40mhYI2TOgm9oA0JT2oZ4MWqZNVd8zEPICocoA0PLmFj00Lw5pClL2DOijLgC0LPYUPUKZC2opm9kzoIuqANDyRhY9Qiv9NFVW7BnQQUUAhLbY53ulfxGaXmv2DPjn/bsBNX3HXBGtVksePXpk5bG2trasPM487t27J8+ePfP293PNZlN+++23YZIkS7Yec3NzU+7evWvr4ebWarXk4cOHVp+bdT7TR9MiTpHD5ogV2nSn7IM9A354CwBNc7Yih63Or6kE13awZ8A9LwEQWue3NZ/T8hFezQd7BtxyHgCxXubTVJKGcLBnwA2nAaClHCt62Or8Wkag0A72DJTPWQBoeeGLHrZKtdAqHo0HewbKU3oAhLjoZetNCS30NB/sGShHqQGQpukb3y/uLIetDT4hhl4IRxmfxddSofm6z0BpARDairetzh/a8w7xYM+APaUEQGidoNlsWnnemk6kqh/sGbDD+lbgbrcrGxsbNh+yVDa39na7XSuPo92rV6/k5s2bvpshzWZTfvrpp2x9fd3aVvKtra3KPrexbKZJaCOgljv4hEhTlceegflZCwBNLxqd3x0tZXOV9wyUea5aCQA6f9w0XVdnz8BsFg6A0Dq/lh1YVVPl6+pVfm4LBQCdHydpua7OdxMUM3cA0PkxiaZzgz0D0811GTC/1NdsNmf9VS+uXLki3333ne9mRMUYM7x169ZSr9fz2o5nz55Jp9ORGzduWHvMKj0377cEA+BP3XcDAPhDAAARIwCAiBEAQMQIACBiBAAQMQIAiBgBAESMAAAiRgAAESMAgIgRAEDECAAgYgQAEDECAIgYAQBEjAAAIkYAABEjAICIEQBAxAgAIGIEABAxAgCIGAEARIwAACJGAAARIwCAiBEAQMQIACBiBAAQMQIAiBgBAESMAAAiRgAAESMAgIgRAEDE6saYoe9GAHDPGDOs9/v9j3w3BIB7/X7/o/rq6uqvvhsCwL3V1dVfWQMAIlYfDAZ/+G4EAPcGg8Ef9Xq9/pfvhgBwr16v/1U/PDz803dDALh3eHj4Z01EJMuyzHdjALhVq9VqdZG31wN9NwaAO3mfz68CdD22BYB7XZHjADDGPPbbFgAu5X2+lv8D6wBAPGq1Wk1k5MNArAMAcRjt6+8CYDAYfO+nOQBcGu3rtdH/YBoAVF9e/oucuB+AMeap++YAcOVkH38vAPb29r512xwALp284lc7+QNpmr5JkmTJXZMAuGCMGTYajY9H/+2DjwMbY9rumgTAlXF9+4MKQIQqAKiacaO/yISbglIFANUyqU+PrQBEqAKAqpg0+otMuS343t7eV+U1CYAr0/ryxApARCRN01+SJPnCfpMAuGCMedpoNL6c9P9TA0CEqQAQqmmlf+7UuwIzFQDCVKTvnloBiIjs7+/fXltbu794kwC4cHBwcOfMmTMPTvu5QgEgwnoAEIrT5v2jCgeACOsBgHZF5v2jZgoAEUIA0GrWzi8yRwCIEAKANvN0fpE5A0CEEAC0mLfziywQACKEAODbIp1fpMA+gGkajcbH3EUI8ON4tX/uzi+yYACIiDQajS8PDg7uLPo4AIo7ODi4U/RS3zQLTQFG9Xq9y+fOnfsPUwKgPMaY4d7e3lcXLlz4r43HsxYAOTYMAeWYZYNPUQtPAU5qNBpfvnjx4p980QhghzFm+OLFi3/a7vwiJVQAo/b3928nSXKXaQEwO2PM0BjTLrKnf16lBkCOIACKc9Hxc04CIHe8UPhv1giADxljnu7t7X1ra4GvCKcBMOr169f3l5eX/0VVgJgZY4aDweD7s2fPermU7i0ARh1PEa6KyCUCAVV2vDjeNcY8dlHin0ZFAJzU6/Uur6ysXDw6OvpkeXn5UxGRfr//+erq6v8ICGhmjBn2+/2PVldXfxURGQwGf9Tr9b8ODw//dFnaF/V/nMHKmHvh3U4AAAAASUVORK5CYII= "Favicon for x-ai")**Grok 4.7**

***Reasoning**

***The renderer is the piece that has to turn both earlier plans into a movie. I’ll check which image endpoints are actually callable, then say plainly whether those plans are enough.**

***Searched for Hugging Face Inference Providers FLUX.1 schnell image generation endpoint 2026 pricing availability vs downloadable model5 results**

***Reasoning**

***Movie Builder is the compiler and the renderer. It does not direct, and it does not time speech. The earlier plans are enough to design that compiler. They are not yet enough to render a reveal without a few fields Round 4 has to freeze.**

## ***Verdict**

***`movie-builder` turns files it can already see into an MP4. A director plan is optional. A narration sidecar is optional. If both are present and complete, it assigns no shots. If they are absent, it makes a slideshow from the order the user gave it. It does not invent a storyboard to fill that hole.**

***The executable artifact is a resolved timeline with seconds in it. Those seconds are a cache, written by this skill after it reads sample indexes. They are never written back into the director plan.**

***Nothing here is implemented. Filter recipes, card layouts, and the 150 ms tolerance are proposals, version `movie-builder/0`.**

## ***Are the other two plans sufficient?**

***Sufficient for intent and for measurement. Not sufficient for a reliable compile. Six holes:**

1. ***A missing word time has no safe failure. Narration Studio correctly leaves `words` empty rather than interpolating. If this skill then places a "14 HOURS" card at the sentence start, the joke is spoiled by the fallback. The safe failure is to keep the previous image and record the miss. That rule exists in neither plan.**

2. ***Silence cannot be joined. The director asks for a reaction after an anchor. Narration Studio emits silences with `after\_anchor`. Nobody has said that this is a join on that anchor, or what happens when two silences match, or when the silence sits inside the sentence rather than after it.**

3. ***Coverage is implied, not declared. "Every word sits in a shot" does not say what covers the pause between paragraphs, the head of the file, or the tail after the last word. Without an extend-previous rule, the compiler invents a gap and ffmpeg invents black.**

4. ***Requested timings are not a list. This skill should not scrape `not\_before` out of shots to learn what Narration Studio was supposed to measure. Round 2 already asked for `timing\_requests`. It is still a proposal. A render also needs the inverse: anchors that were requested and came back untimed.**

5. ***Cards have a name and no owner for layout. `template: stat` and `text: 14 HOURS` are enough to ask for a card. They are not enough to draw one. Layout, the caption band, and the font stay here. The director must not start specifying pixels.**

6. ***Nobody owns the container delay. Sample indexes in a WAV are exact. AAC in an MP4 is not. A reveal test that ignores encoder priming will fail a correct compile, or pass an early card. This skill muxes. It owns that error.**

***Everything else can be compiled from what Rounds 1 and 2 already describe: verbatim anchors, `nth`, `not\_before`, conditional reactions, clip spans, silence durations, and the refusal to divide a sentence by word count.**

## ***1. Name and trigger**

***Name: `movie-builder`  
Folder: `movie-builder/`**

***Description:**

***Assemble a narrated MP4 from images and audio. Use to render a slideshow or explainer, apply a shot plan, burn captions, make title cards, add slow zooms and fades, render stills with FFmpeg, and write a contact sheet and a QA report. Use when the user has pictures and a recording, or a director plan plus a narration sidecar. Do not use for storyboarding, rewriting a script, text-to-speech, or speech alignment. Do not invent word timestamps. Do not treat one sentence as one shot unless the user asked for a plain slideshow.***

***"Render the video" and "make a slideshow" have to be in the description. So does the refusal to align speech, or this skill will swallow Narration Studio.**

## ***2. Standalone**

***This skill is finished when the other two are not installed. It assembles. It does not direct.**

| Request | It does | It does not |
| - | - | - |
| "Here are 12 images and a WAV. Cut on this SRT." | One shot per cue, in order, Ken Burns, captions from the SRT | Word-accurate reveals |
| "Images and an MP3. Just a slideshow." | Even split, only after the user confirms, QA says **`unsynced`** | A fake beat sync |
| "Hold image 3 until 0:42, then cut." | A user manifest with times | A new storyboard |
| "Make a title card that says 14 HOURS and hold it for 3 seconds." | A Pillow card, then ffmpeg | Diffusion text |
| "Replace shot 4's picture and rerender." | Swap the file, no model call | Regenerating the others |
| "Add a gunshot and music." | The picture cut only | A sound-design pass |
| "Storyboard this first." | One line, out of scope | A plan.json |

***No plan and no timing file means the user is the editor. That is the standalone product. It is not a failure of the cooperative path.**

***Two questions at most: which timing source, and draft or final size. Do not ask for a codec. The preset is the codec.**

## ***3. Cooperative workflow**

***This skill calls neither of the others. It reads a folder.**

```
***`plan.json          optional, intent, no seconds`**

***`narration.wav`**

***`narration.json     optional, sample indexes`**

***`images/            optional, already made`**

`        │`

`        ▼`

***`resolve anchors → timeline.json → cards and stills → ffmpeg → mp4`**

`        │`

`        ▼`

***`qa.json + contact sheet`**
```

***A complete plan means all of these:**

- ***Every shot has an anchor, or is a user override with times.**

- ***Every `not\_before` is in `timing\_requests` and comes back as a word span or an entry in `unresolved\_anchors`.**

- ***Every asset is a file, a card, or a prompt.**

- ***`coverage` says whether the plan covers the whole script.**

- ***The audio file named in the sidecar exists and is the WAV that was measured.**

***If that is true, the user assigns nothing. If a reveal is unresolved, this skill still renders: it holds the previous picture across that sentence, writes the miss into `qa.json`, and does not stop to ask for a shot list. One hole is not a reason to hand the movie back to a person.**

***It does not write seconds back into `plan.json`. A retake is a new sidecar and a recompile. Locked overrides store an asset id and an anchor, not a timestamp, so they survive the retake.**

## ***4. Files**

***Under 500 lines in the body. The scripts compile. The body is not allowed to estimate a frame time the script did not print.**

```
***`movie-builder/`**

`├── ***SKILL.md`**

`├── ***agents/openai.yaml`**

`├── ***references/`**

`│   ├── ***resolve.md`**

`│   ├── ***cameras.md`**

`│   ├── ***cards.md`**

`│   ├── ***providers.md`**

`│   └── ***shared-contract.md      \# provisional until Round 4`**

`├── ***scripts/`**

`│   ├── ***resolve\_timeline.py     \# proposed`**

`│   ├── ***render\_cards.py         \# proposed`**

`│   ├── ***render\_video.py         \# proposed`**

`│   └── ***qa\_video.py             \# proposed`**

`└── ***assets/`**

`    └── ***card-templates/         \# layout only, no story text`**
```

***`SKILL.md`, in order:**

1. ***Boundaries. No storyboard, no TTS, no forced alignment, no invented word times, no music, no sound effects, no arbitrary filtergraphs from the user.**

2. ***Find the timing source. Sidecar, then SRT, then a user manifest, then an explicit slideshow. Never guess a fourth.**

3. ***Resolve. Read `references/resolve.md`. Write `timeline.json` before spending money or calling ffmpeg.**

4. ***Assets. Reuse a file. Draw a card. Generate only under the cap. Read `references/providers.md` only if a prompt has no file.**

5. ***Render. Read `references/cameras.md`. One preset.**

6. ***QA. Contact sheet always. Vision never in the default path.**

***Load `references/cards.md` only when a shot asks for a card. Do not load a worked DOOM timeline on a calculus slideshow.**

***Proposed project layout, not yet a contract:**

```
***`project/`**

`├── ***plan.json`**

`├── ***narration.wav`**

`├── ***narration.json`**

`├── ***images/`**

`├── ***timeline.json`**

`├── ***overrides.json`**

`└── ***output/`**

`    ├── ***final.mp4`**

`    ├── ***contact.jpg`**

`    └── ***qa.json`**
```

## ***5. Renderer**

***FFmpeg is the renderer. MoviePy is not a fallback.**

***One preset. Final: 1920×1080, 30 fps, H.264, AAC, yuv420p, 16:9, faststart. Draft: the same at 1280×720, for looking at a cut without paying the full encode. No other sizes in v1.**

***The compile is per shot, then a concat demuxer, then the audio. Each shot becomes a short silent video. Concat. Mux the WAV's audio as AAC. Set the output length from the audio's measured duration, not from `-shortest`. `-shortest` will eat the tail of a read if a shot was a frame short.**

***Camera is a closed set, implemented once:**

| Camera | Implementation | Forbidden on |
| - | - | - |
| **`static`** | Scale and pad the still, loop | Nothing |
| **`slow\_zoom\_in`**, **`slow\_zoom\_out`**, **`pan\_left`**, **`pan\_right`** | One pinned recipe in **`references/cameras.md`** | A shot shorter than 1 second; use static |
| **`hard\_cut`** | Concat, no xfade | Nothing |
| **`fade`** | 12 frames, about 0.4 s | Any shot with **`not\_before`** |

***`zoompan` is the likely recipe and a known footgun. It needs the still scaled up before the zoom, `d` is frames, and the zoom expression resets if it is written wrong. The recipe is not real until a fixture shows a push that lasts the shot and does not jump on frame 2. If that fixture fails, a crop expression with a time variable replaces it. No third camera engine.**

***Fades into a reveal are how a card appears early. The compiler forces a hard cut when `not\_before` is set, whatever the plan requested.**

***Captions are ASS, burned with the subtitles filter. They live in the bottom 140 pixels. Card text lives above that band. This skill does not auto-place captions around faces. It does not have a face detector.**

***Audio is passthrough aside from the AAC encode. No ducking, no added "Bang," no music bed. If the recording already says bang, the picture cuts and the waveform is left alone.**

***AAC priming is this skill's problem. A correct WAV index can land early or late in the MP4 by a few tens of milliseconds. The QA script measures the muxed file. It does not assume the container matches the WAV. The reveal tolerance has to be wider than that error, or the test muxes audio in a way that does not add delay. Pick one in Round 4. Do not claim sample accuracy inside the MP4.**

## ***6. Timeline**

***`timeline.json` is the only file with seconds. It is disposable.**

```
***`\{`**

`  ***"timeline\_version": "movie-builder/0",`**

`  ***"audio": "narration.wav",`**

`  ***"sample\_rate": 24000,`**

`  ***"fps": 30,`**

`  ***"size": \[1920, 1080\],`**

`  ***"shots": \[`**

`    ***\{`**

`      ***"id": "sh\_11",`**

`      ***"asset\_file": "output/cards/card\_14h.png",`**

`      ***"t0": 19.40,`**

`      ***"t1": 20.48,`**

`      ***"camera": "static",`**

`      ***"transition": "hard\_cut",`**

`      ***"anchor\_status": "word",`**

`      ***"not\_before\_sample": 465600`**

`    ***\}`**

`  ***\]`**

***`\}`**
```

***`anchor\_status` is `word`, `sentence\_fallback`, `user\_time`, or `slideshow`. A reveal may not have `sentence\_fallback`. That status is how a later reader can see the card was not timed by dividing the line.**

***Resolver, in order:**

1. ***Prefer the WAV named in the sidecar. Do not time against the user's MP3 if a measured WAV exists.**

2. ***Join a word anchor on `segment`, exact `text`, and `nth`. `at: start` is `sample\_start`. `at: end` is `sample\_end`. Seconds are samples divided by the sidecar's rate.**

3. ***If the word is missing and the shot is a reveal or has `not\_before`: do not use the clip start. Extend the previous shot over that span. Record `reveal\_unresolved`.**

4. ***If the word is missing and the shot is a hold: clip bounds from `covers` are allowed, labeled `sentence\_fallback`.**

5. ***Join a reaction to a silence with the same `after\_anchor`. Use it only if its measured duration is at least the shot's `if\_silence\_ms\_at\_least`. Otherwise extend the previous shot. No gap.**

6. ***If two silences match, use the one that starts at the anchor's word end. If none start there, drop the reaction and say so.**

7. ***Any remaining gap, including the head and the tail, extends the neighboring shot. The last shot ends at the audio duration. Black is a bug.**

8. ***Delay any shot whose card text, or whose caption, would be visible before its `not\_before` sample. Derive caption breaks from `not\_before`. An explicit `hide\_until` that hides less is ignored.**

***A director sentence split across three clips still resolves, because the join is the word anchor, not "one segment equals one file." A plan that covers an excerpt does not get stretched over the rest of the recording. The uncovered head or tail holds the first or last image, and QA says the plan was partial.**

***Overrides live in `overrides.json`. A locked shot keeps its asset file and its anchor. A time override is standalone-only. On a cooperative retake, a stored timestamp is dropped and the anchor is resolved again.**

## ***7. Images**

***One function, three adapters:**

```
***`generate(prompt, seed, width, height, model) -\> png`**
```

| Adapter | When | Not |
| - | - | - |
| A file already in **`images/`** | First, always | A regeneration |
| Local weights already on disk | User asked, and a GPU is already there | A silent 12B download |
| Hosted route that answers a probe | Under the cap | A repo page treated as an endpoint |

***Downloadable is not hosted. FLUX.1 schnell's weights are Apache-2.0 and published for local use. That does not mean a free GPU is waiting. A dedicated Hugging Face endpoint for that model is listed at $1.80 per hour on an L40S. That is the wrong default for ten stills. `hf-inference` has been mostly CPU since July 2025. A July 2026 forum report says schnell specifically returned HTTP 410 there. I did not probe it. The skill must probe, and a model card's list of vendors is not a probe.**

***Hugging Face Inference Providers, as fetched for this round, bill at the provider's rate with no markup. Free accounts show $0.10 of monthly credits, subject to change. PRO shows $2. Those numbers are not something the skill should hardcode. `provider=auto` can fail over. Spaces that sleep are not an adapter.**

***Cache key: model id, size, seed, prompt hash. Store the PNG and the prompt beside it. A replaced file with the same asset id is a lock. The next render must not call a provider for it.**

***Before a call, print `count × price` if the price is known, or "price unknown, cap is N calls." Refuse to exceed the cap. One retry on a transport failure or an image that is the wrong size. Then a card. A card is a successful frame, not a crash.**

***If the prompt contains the payoff string from a card in the same plan, strip that string and record it. Diffusion does not get the punchline text. If the adapter cannot take a reference image, reuse the existing file and crop. Do not pretend an identity model is installed.**

***Style text in the director prompt is sent as written. This skill does not add a second style prefix on top.**

## ***8. Cost, cache, fallback**

***The cheap path is the default. User images, then cards, then cached PNGs, then a hosted call.**

| Failure | Result |
| - | - |
| No ffmpeg | Stop. Say so. Do not describe an MP4. |
| No timing, and the user did not confirm a slideshow | Stop. Do not evenly divide. |
| Reveal word missing | Hold the previous image. QA names the anchor. |
| Image call over cap, or the provider is down | Card. Movie still exports. |
| Provider returns a picture with baked-in text | One retry with the text clause removed. Then a card. |
| Asset file missing | Card reading **`MISSING`**, and a QA error. Not a black frame. |
| Plan and sidecar disagree on the script hash | Render the sidecar's audio. Do not retimes against the plan's prose. Warn. |
| User asks for music, SFX, or a pan that is not in the enum | Ignore that part. Render the rest. |

***Generation cache and render cache are separate. Changing a zoom does not regenerate a PNG. Changing a prompt does not re-encode the shots whose hash is unchanged.**

## ***9. QA**

***Deterministic checks are the gate. A contact sheet is the review tool. A vision model is not in the default path.**

***Required before calling the render done:**

- ***Output exists, and ffprobe reports 1920×1080 or the draft size, 30 fps, H.264, AAC.**

- ***Video duration within one frame of the audio after the mux, not merely on the timeline.**

- ***No gaps, no overlaps, last shot ends on the audio.**

- ***Every shot file exists and is a decodable image.**

- ***`blackdetect` finds nothing longer than two frames.**

- ***No caption cue starts before its `not\_before` sample, converted with the same delay the mux actually had.**

- ***A reveal shot's first frame is at or after the word, and no more than 150 ms after it. This number is a proposal. It has to clear AAC priming or the test is void.**

- ***No reveal carries `sentence\_fallback` or `slideshow`.**

- ***A replaced image did not change any other asset hash and did not call a provider.**

***The contact sheet is one frame per shot, about 100 ms after the cut, with the shot id, the spoken span, and `anchor\_status` under it. That is the human review. It is not optional.**

***Semantic QA, if the user turns it on: one yes-or-no check at generation time, one retry, then a card. It may ask whether the file is a picture at all. It may not ask whether a deadpan chart "matches" the joke. Irony is not a defect. No post-render loop.**

## ***10. Milestones**

***Prompt tests and fixture tests. No claim that a script already passes them.**

- ***M1. Three stills, one WAV, one SRT. A slideshow with no other skill installed. Duration matches. Contact sheet exists.**

- ***M2. Hand-written anchors plus a fake sidecar. The resolver writes `timeline.json`. A reveal with a missing word does not move to the sentence start.**

- ***M3. ffmpeg preset. A static shot and one zoom. The zoom fixture lasts the whole shot. A fade is rejected on a reveal.**

- ***M4. Pillow card for `14 HOURS`, caption in the bottom band, card text above it.**

- ***M5. The retake. Same plan, longer WAV, no edited timeline. The card still lands on the word.**

- ***M6. One hosted or local image, cap at two calls, third shot falls back to a card. Cache hit on the second render.**

- ***M7. Full folder: director plan, narration sidecar, no human shot list. QA green on the three events in the next section.**

***M2 is the contract. M7 is the product. A skill that can only pass M1 is a slideshow tool, and that is a legitimate standalone result. It is not the cooperative skill done.**

## ***11. Acceptance**

***Measurable, on a 60–90 second excerpt, once the scripts exist:**

1. ***With a complete plan and sidecar, the run asks the user no shot questions.**

2. ***The "14 HOURS" card's first frame is at or after `fourteen`, and within 150 ms. The caption on screen before that word does not contain the payoff.**

3. ***At least one shot covers more than one sentence. The resolver did not insert a cut at the period.**

4. ***A reaction whose measured silence is under the shot's threshold is gone, and the timeline has no hole there.**

5. ***An unresolved reveal holds the previous image. It does not show the card early.**

6. ***Swapping one PNG and rerendering changes no other asset hash and makes no provider call.**

7. ***Duration matches within one frame. No black frames. Contact sheet has one cell per shot.**

8. ***The same plan against a slower read, without an edited timeline, still passes 2 and 4.**

9. ***A standalone run with images and an SRT, and no other skill, still exports. Its QA says `sentence` or `srt`, not `word`.**

10. ***An even split occurs only when the user asked for a slideshow, and QA says `unsynced`.**

***"Watchable" is a note on the contact sheet. It is not a number, and it is not the gate.**

## ***12. Changes to record for Round 4**

***Do not edit the earlier plans in place. These are the fields that would make them sufficient.**

***Story Director**

- ***Add `timing\_requests`: every `not\_before`, plus any other anchor this skill must not approximate.**

- ***Add `coverage`: first anchor, last anchor, and whether the plan covers the whole script.**

- ***Add `gap\_policy: extend\_previous`. One line. It is currently an assumption.**

- ***Keep card payloads to `template` and `text`. No coordinates.**

- ***Add an optional `file` on an asset so a user image maps to an id without a prompt.**

- ***Keep reactions conditional on an anchor, never on a silence id this skill has not seen.**

- ***Say that a missing word time means "hold," and that this skill is allowed to do that without a new director pass.**

***Narration Studio**

- ***Add `unresolved\_anchors` for every requested anchor it could not time.**

- ***Require `after\_anchor` on silences that touch a word, so the join is mechanical.**

- ***Keep `audio.file` as the measured WAV. State that indexes die if anyone resamples it.**

- ***Add `ready\_for\_word\_reveals`: true only if every requested reveal anchor has a word span. False is not a crash. It is how this skill knows to hold.**

***Neither skill should grow**

- ***A second millisecond table. The shot's `if\_silence\_ms\_at\_least` wins. This skill's default, if the field is absent, is 800 ms, and that default moves to one line in `references/resolve.md`.**

- ***Caption writing that applies spoiler breaks. This skill derives those from `not\_before`.**

- ***Renderer fields. Cameras stay the enum they already have.**

## ***Ideas Worth Revisiting in Round 4**

1. ***The reveal fallback. Hold-previous is the proposal. Confirm the other two skills will not also "helpfully" snap a missing word to the clip start.**

2. ***AAC delay versus the 150 ms test. Either the tolerance swallows priming, or the acceptance render avoids AAC. Do not leave both skills asserting sample accuracy.**

3. ***SRT ownership. This skill can burn ASS from word spans. Narration Studio can emit a convenience SRT. One writer should apply `not\_before`, and it has to be this one.**

4. ***Project layout and version strings. Freeze the folder names when the host that loads all three skills is known. Until then, paths in the schemas are examples.**

5. ***Who may align. This skill must not grow a copy of the aligner just to be standalone. If users constantly arrive with an MP3 and no sidecar, the host routes them to Narration Studio first. That is a routing rule, not a second aligner.**

6. ***Card enum. `stat`, `title`, and `comment` are enough for the DOOM excerpt. Freeze them only after one real card is drawn and the caption band still fits.**

7. ***Zoom recipe. `zoompan` or a crop expression, chosen by the fixture, not by preference. Delete the loser from the skill so the model cannot pick it.**

8. ***Draft preset. 1280×720 is a time saver. Drop it if it becomes a second layout bug for cards.**

9. ***Identity references. Crop-and-reuse is the v1 consistency tool. A reference-image adapter waits until a story needs a new pose of the same face, and until a provider on the machine actually accepts one.**

10. ***Routing. "Make me a video" is a host decision. This skill's description should not claim the other two, and it should not call them.**

***5 citations**

*![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAADh0lEQVR4nO2aPU9TURiAn8NH0VgMITExJrBZq5XApIluxMRQB1HjgInEzbi5mDLIYFxAB/wJpkadRMAIMTFs4IqaVoUNFxeUiAnQRI7DbVMt97a957y9WnufpMu59/3s+X4vhISENDKqRnqjwCugS0jfBnAS+CGkr+ZMAFrwNxGs+3b0A2vIBZ/B6VF1wwKy/34qWPftSNHAXT+K012lgt8EYoFGYIlk8Jo6Cz6GbPCZYN23I4bsrF93XV96zQ901pfYCWoBHQW2gL2C+irSZCEbBWakHMEJ/pygvprT0Gt+DGeykpz4Gnq7Oxys+3YMIxv8QrDu29Hw2926XvNtkT7nz/APTHx+NkKbwJ6/ZLtmtFT5XgrZ4B/YKtCJ5BA7uhelLgKH880raD1JEy9obcuopan1Snqq+RdiwBug08Lf39kCeoFlE2GdGDiNVreA8xVenVbZ2cFK+qpJQAY4Vo1zVXIE4+CTQ2ie+BJSXFGZ2afej8sTAz75MlieLJAwEdTxZA9NvDMQ3SAS6fYaDuUOQzHgrYFBL7I4d/u+0X2DHTTxzNBuO7ncN6+H5RJwA9mJL41pYWN7e4TiRGeETiSH3Nq9EjAM3LQxWMIiMG4srVTc2gPNHd032FHa7JaAKHDd2mCRz8CoqbCOJ3twNmH2bOV2lercEnAIsM94kX1W0s16P9Au4MfBvK4/cEvAMnBZwGCBTuCuubjqFvPEBa85YB5n3EpxCuNurFdxqsP2/FTfS5vKrQKjOLs2KR5icvRtbcsAXwTsu+ool4B5ZCfDLuC2X6H8BiZrbV3rSfVx9n1pc6Vb4bSI8SJXMekFSt+3tqzVY7fmaq7FLwBfrR0o8hqf9wAqM7cATBtb1Hrc7d+H6hKwDNwzNr6bLkxWhUjkGrBiYG9FfZgb8XpYbWFkHNlV4SY+VwW1NLVOJHICfz1hOi/jrdeHsn7gJXLng0XgLAbnA310YKzkImQ3FY7Bxdf8kQLGfMqU4xEWNQEdT/bQzHF2dG+hrVx3d8PkXu6/uhs0KY5KFzDr6mOIAmkauDQGzjouWRzVwbovg3SNMB2s+zKEQ4EG/04AwqEAhEOBKLIJCGwoNAvpyeHcHp0R0teCc2p8LqQvMGaQ7Qky1+EB0o9sAtaCdV8G6c9o6m5ViAKryCVglTr7kArq6PP5Wp7FJ4BLQroO4BzD54X0hYSEhADwC0RY10F3B9rMAAAAAElFTkSuQmCC "Favicon for https://endpoints.huggingface.co/new?accelerator=gpu&catalog\_id=300&instance\_id=aws-us-east-1-nvidia-l40s-x1&no\_suggested\_compute=true&repository=black-forest-labs%2FFLUX.1-schnell&task=text-to-image&vendor=aws")![](data:image/png;base64,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 "Favicon for https://discuss.huggingface.co/t/urgent-help-unusable-inference-credits-after-flux-1-schnell-removal/177901")![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAP5klEQVR4nOVbb2wcx3X/7c4d746i7o70ERJ14h/TxwiKQ8vWUUJkKq0boXZdVAFk+IPtKgpSwC2QooCBRkFgf0k/pEZkIOiHwEhbI21s2REKowLiIkJTKG1j0xIknhxWdQWFNOXjP5E++kieeDySdzObD29nZ3Zvj7yjKDdAHkAcd3d23rzfvHnz/swCv+NkfBZMLMtqmI9hGNa9GEsVn3vVsS70VoXZjj42o8B2dlZrwMvLy0+EQqGHTNN8yDTNHgD7ALR7Xs8BuCmE+Jhz/h+zs7NDhmF8tFnfvxVkWZbhVfP19fVTlmW9a90lcc7fWFxcHPDy2sqy8qO76sQ7K6Ojo+29vb3fN03zpKth4TZw67+B+evAwnVg9ZdAqQBweyJbYkD494DWfiDRD8R7gO4vetnlyuXyN5uaml73471VGbYMgByAYRhWOp0OXrly5UcuwbOXgbF3gNG/pWvWACtuARUG7P5j4NCLVWCUy+WveYHYKggNA+BFfn19/VQwGPyx02DkHDD8HFC2SGgTgNA6iESBSLm641KQtEKSfE9qyZGfAAee0d94b2xs7Km+vr7c3YDQEABeRpZlvQvgKACa8Z8/SgMOGmrwLTEg2QQeaQKLss2ZrApgaQ3IF4F8ie6ZIECBKiCkNmwVhLoB0BmMjo62p1KpDyEt+dtfAebfUYIDwN44sGsHEDbpmjcwKokTBzBfAsbnqV8JREsM+MoNINoBABBCnGWMfXUrdqEuAHThFxcXB2Kx2FUANOsXjrhVfW8c6N6pBLhbkmDMeYAomcCXzura8J5hGF9qVBM2BaCm8CPngHdPAhFBg2qLAJ9L0IC3Q3AvSSCyd4DsAmlb2QL6XgSOfVe2ahiEDQHwUftPALiFL1vAvnZgV+TeCO4lBvACB7s+o5ZE4jjw9E9li4ZAMOvla6/5qpnnDyc/O+EBgIOMaTpJ10GD7M/Fl2SLo2XOz2iGesNJrvlQR9Cx9tnLwDtHlfD9e2gwn5XwfnRlkn7LlmuHKBaLf9TS0vLvm2mCLwD6S84+X7gNvLXHWXv84eT/v/CSLk8qw3j8Pd1xcjS8FgAbLgHLsgzHyfn5X5C1FwD2tf/2CA/SRJQt0swLR5z7QojXN1sKVQDosy+EeB0Arfv5d6hBW+SzXfN1EIsyoLuVJocZjj0wTfPkxMTEAxu9W4WKBGBsbCzhWP0fGsrJ+WLndo9/e4gBuLYErBVoKZyalI7ShruCSwN0Nenp7T0NgGZfqn4qofbjjSgkwIscvMiBkNi8vZ8wdh+yv02JAzzVQkshJGjJEh3dSAuqlsDAwEDAMAwrYJoEwKVnqZWJzVWfAbzI8ezpLoSPpxA+nsKzp7uAcgMghASGPmhBcPABhI+nEPzy/Tjz2u66QGBRBrQ301hnf0ZhOIBkMvmdWragCoBMJlNeX18/BYBmH6DZ701sPviAwKG/6sWl8QD6ewT6ewQujQfw7N901TeLIYGhq1E89kK7835/j8BL/7QDQ1ejm2sfB3jStgUhAVz9AQlph+kDAwNVGTAHAB2ZYDD4PABg9C0Vx9eafaZ+h65GkV810BZWy6wtbOHt94PA9Fpdy2dopBnJ3e4dq79H4Af/EgcCHhB9+mNRRiG3CZWLAKXlMplMVRzu0gANIQpxZ39GLdoi/qOdLwHZO2qteii/aiC/agO4WvHvQ6eKGo7znk03ZzzS2rx9l1eySUWl2csAgEgkcrK6oQeATCZTdvJv2ctAgNuBzg737DMAU3coZl9ZA5teAFYFBh9axvSs4Qjw5rfn8Y0nV9DfIyhCrGPrHDywgrawhTe/PY99e7gD4jN/UPLljVt5NwgcQCxEuQhmAIsfk6Cm+YRs4gqb9ZuGYVjlcvl0IBA4g4svAeMvU0eDXe5RMgA35t332nYAuyIY+qAFj73Qjv/6uxwGD2kZnrU6ww4Gl6of/NP7sW8Px09eniLhfHjzZCvYDubu49IkTV7rnziB0sDAQBMADA8PV6RRDHgRMU3zIQCUvARo//eGuNwWOF9U92IhgAODjyyj/ItleqdeoV3SAODqvWs/zhIgel/NIZp9KW+Tj5MXjwCLJeXAAbh48eKBWCyW0Zs5VtFe/2U7bw8s/JvqyI92afdjISDoyfxsl6foAQQctJzmAtW8dWoOUUqtwmg7jHagubn584ZhDOsT7lcY2QeAEA8J6qjWwBI1wLnXVA/vsC1aQM2EYRi7vM38dNRbsdk61eM13ov3vdq3kKVf03Rkk1rgv0htD+quiAFDH7SQhW7EHdbc4KEPWrYMAo801XymO0RbsFJ1DqDA8dgL7Qg+8QDOvLZbxQW1BJKCFzjOvLYb4eMpPPbC9imjTsPDw45T4gdATqabt4P6ewRevdCM8PEUzry2W81qSKg/W1tkDPHqhWbyHYBq769OYqX1utrVrg4HOADD3m52Nj6ANsNxadvCFtp6LLx6oRmvXmjG9Gw7nn5UeaVvvx9EcreFtrClBAdcbRpj7rlu7aZfIXLepn4acBMAFR8AKlnpnTIfBjXoG0+uuFzatrAS8uYMw6XxAG7OMPT3CFf8AJAn+ci+dZd7XJP0Mclf6XpXmFNAWVtb+x9vXqCq94oQlwAAHX9JN0oFKlddWwKGJoBfTpAnVvasZwb3QComBg+sOK6xVzgJiH6t0/Ssgb9+6ray6AzVPOT97B3y/IYmgKFJuv5UkHTxFsU3nx/zRoRVAKyVShcBUJlatshMU6YlaGeGFkvAlSmq1jBQYHJtiZhfW6JrAIOHCnj60bIjYH7VwGnDwi3DwmnD8r2W7b779SJYmwbMjXnqf2hSucIyCzS1aF/bFaqpRRqvgJpIAF1dXVUHLgyf4se/AjjqygIDqvoDkIdlavfktSS9WLIq0PO1XgDAyxGBZ7TZPhe2XNcAcL9F4fS1N2+RMyaFLBUUD1kei3t474nTzK8VVLvDbzmpciHEWdM0T0lehmFYzrC1ys9R50CDXtM3AfS3AfsTlBorW3RvUQMjHqHfoAHczNHSCZv46B8/qhIeQNW1BOnaj7JK+OwdJXwoSn9y1JJ3KAoc7iQXWQ+FATqUYYfEdmJkTs8OGTIKtCzrEwDtTuUnJNyzKgAMdqqILHuHVE0Kn0rQjM+VgDFbRfVCKQD8YhrWPzxaJbQzI3/+PvB4hwp8GEjl5TiO2AlZmfyUdLhTtdfHJcctQ+PnCRm9mmwAdJ7HKX683qkKnpK8lV8JghxIWQuZZSgq6Uin25AFBGWHptdpZiNRmrVkiCy+3lYHUwIMTUhuF2j0UPiKxlsKLzPaWmg8OTmZ6uzsHDcBgDH2hwAohxZSZS+kkyS0XHPZBfACV+Hx53cqoPSkxB77HQFlKGG/s2ZSIHMwRhp1MEaCrZnVPvz4vJrJhE9Krr1ZHbpgAEaWlOChKIE22EVL05Mo7ejoeMqxAU4IrBGLMgozu3cSEKEowAyw6zMKhLBJTABgrqiAkWpvgmbQLzTmnj8Xc9AsSxD3xt1b34xt9T+XcCdJSgW1HA/GCDQGyl0IuCJDGRiZACCE+JhQ7lcNbswrgYImdbg3DnBLgQDQ7LXESCVXNd8glVCa8+v5hoIaXuB0BkCm4/Vld2OelpysUch7cjdIa9VqBhrTmKZJtlNkcf6/DgAuDeC2dc/be7t0eOyZ5Q9TWZpdn6HOYRckuAVcmaLBcxuYSJT6zNsJzDpBYB/OqCLsg3vcNidfIsClPbgxD+RWaDs+0kmTpRvqzLQSXnq3AAzGvgAA5ujoaDvk1vfuSfcBp1KBHB45eG9tPjMNrApVkADAxpYVYAdiSgumFusDQRoxAaC7Va3xVQEsLpPhS9neXfYOCd/dStuzLTgvcreDJA9YlQpO3VAWfgxnBxg5B1x5jhqmErR+5ktkrZeXCJjehLs+MLJER972kx3gBe62yABpkJyFso/VlqTvKtLBkkLZz3mBU/4vbBIg798GHmxzj+nXtkaAAOStzcRvROvb3g6XlpYOBfzSRDzSBMZAIOyKAHNNZJFv5oB8MxkfgOyCZsR8BQubdJDiV9NA0CD11rdGSXMl5fBEosD+WFUi1ulf2qUvJ9Xjon1shlukjfZ5JSaXQ6QMrEGdOwQQCATuMy3LmgMA3P/7zvpnH864t7uEvb66Wwldqab1JD7lspHla7k16sRAmib9jQOxuvsGp/7Y8CwQiZKN2q+V8aQtyJeo774XnUf5fH7MzGazFwCQdWTK72e/mgauLdF6khPbvRM4vBeIR2pWg2oOdK/mEeaLblvAQcvMb8vbjBgo9H2wDTgYcx/GzN6xo8MFzZ9QO11XV9dHgY6OjoPU+LKtHgawN05rZ2GFgGB0D3t30vrbnyDVaoQY1CBkjsEmXuRgEvxwgyf4pd9hj4cXOFWqbq9RKJxK0JL+cIYajKrgKJ1OBwNNTU1VNgDhACEZ3UlCT9ln87ILtY1YPSR3BM9ZYdZkKH+9nhqilzQfgeVWgJYY+IDaQVhAkCNXKtBJdZvOnz/fFVhZWfm/WCxGB4sqDAjajgM037tbA2KLxAucNFugutYQNlUs/6kAurfIpDkE7KMSnaOhHMCNPFCy7Y6WHzhx4sSEAQCWZZFp9J7+jETBUy3udbWVio93i0slqKKj0608hbd3c/zOa1emPBEr4GyBsI/OuKNBAFXhsA0Ekk006EYPP28UojptjOrc1CNJ4tUIH2g2wHvS3H2aFEtLS4eOHTs2YqTT6WAmkylzzt9wPngo3KbI8Mb33EDI4+/3mcrB2MgcrAqaWemnS4/M7+MJrj3TcwwyoNmIh9/xej0PoGWFAKBSqXwrGAy+kk6ng0Y6nQ4CdDbAKY1LkkDoX33o6iRj7ZD9EYRetbXV2TWYJy+pgdt1e4fiPZS+lvz0o/d+H1nIDyykkPq41syaX5vIE6TpdDo4PDxcMSzLMmSmNJPJlCcmJh7o7Oz8Z8hTIpLkJzDjL6vCqSTvVyE6ycE8/veou+Ayco4OZwHVaTk/PvonNn3PkVPn4SWEOHv48OE/0+85AADuepkEIplMfqfqAyjA/yOo5SX1nBmUffEZTKVS+ZZlWXOGYexyipVC5CzLmjMY+4JzOg1QoC9cd9X5nf43/siK+Anxysfj46/09fXlpLZL4Z1G+qdo6XQ6KP/k8236BO4TeV4vnU4HdZ6SL0CHme6Sj8U5f2N5efkJKZsuk84T8ByRkf/7HSfLZDJly7KMYrH4eCgSORYwzSPwLhMfEkKcLZVKZ+W626y95GXvTM/XwSMH4GalUvlpsVj8z3g8PgwQyHoj14xDVYZqHpWV5AeGfsYmnU4Hz58/3xWNRlsDgcB9AFCpVD7N5XLZvr6+nN9g/AZUC3SAUvbt7e3dev+FQmHhxIkTE7KNpdmyegR3rr0vSKoHiEap1mC2m9dmQrue1dOhd4CS6hloI4Px47UVHvXwkfQb2La7LAH+e9AAAAAASUVORK5CYII= "Favicon for https://huggingface.co/black-forest-labs/FLUX.1-schnell")![](data:image/png;base64,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 "Favicon for https://huggingface.co/docs/inference-providers/en/pricing")![](data:image/png;base64,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 "Favicon for https://huggingface.co/inference/models")**[Deploy black-forest-labs/FLUX.1-schnell | Inference Endpoints by Hugging Face**](https://endpoints.huggingface.co/new?accelerator=gpu&catalog_id=300&instance_id=aws-us-east-1-nvidia-l40s-x1&no_suggested_compute=true&repository=black-forest-labs%2FFLUX.1-schnell&task=text-to-image&vendor=aws)

***[https://endpoints.huggingface.co/new?accelerator=gpu&catalog\_id=300&instance\_id=aws-us-east-1-nvidia-l40s-x1&no\_suggested\_compute=true&repository=black-forest-labs%2FFLUX.1-schnell&task=text-to-image&vendor=aws**](https://endpoints.huggingface.co/new?accelerator=gpu&catalog_id=300&instance_id=aws-us-east-1-nvidia-l40s-x1&no_suggested_compute=true&repository=black-forest-labs%2FFLUX.1-schnell&task=text-to-image&vendor=aws)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAADh0lEQVR4nO2aPU9TURiAn8NH0VgMITExJrBZq5XApIluxMRQB1HjgInEzbi5mDLIYFxAB/wJpkadRMAIMTFs4IqaVoUNFxeUiAnQRI7DbVMt97a957y9WnufpMu59/3s+X4vhISENDKqRnqjwCugS0jfBnAS+CGkr+ZMAFrwNxGs+3b0A2vIBZ/B6VF1wwKy/34qWPftSNHAXT+K012lgt8EYoFGYIlk8Jo6Cz6GbPCZYN23I4bsrF93XV96zQ901pfYCWoBHQW2gL2C+irSZCEbBWakHMEJ/pygvprT0Gt+DGeykpz4Gnq7Oxys+3YMIxv8QrDu29Hw2926XvNtkT7nz/APTHx+NkKbwJ6/ZLtmtFT5XgrZ4B/YKtCJ5BA7uhelLgKH880raD1JEy9obcuopan1Snqq+RdiwBug08Lf39kCeoFlE2GdGDiNVreA8xVenVbZ2cFK+qpJQAY4Vo1zVXIE4+CTQ2ie+BJSXFGZ2afej8sTAz75MlieLJAwEdTxZA9NvDMQ3SAS6fYaDuUOQzHgrYFBL7I4d/u+0X2DHTTxzNBuO7ncN6+H5RJwA9mJL41pYWN7e4TiRGeETiSH3Nq9EjAM3LQxWMIiMG4srVTc2gPNHd032FHa7JaAKHDd2mCRz8CoqbCOJ3twNmH2bOV2lercEnAIsM94kX1W0s16P9Au4MfBvK4/cEvAMnBZwGCBTuCuubjqFvPEBa85YB5n3EpxCuNurFdxqsP2/FTfS5vKrQKjOLs2KR5icvRtbcsAXwTsu+ool4B5ZCfDLuC2X6H8BiZrbV3rSfVx9n1pc6Vb4bSI8SJXMekFSt+3tqzVY7fmaq7FLwBfrR0o8hqf9wAqM7cATBtb1Hrc7d+H6hKwDNwzNr6bLkxWhUjkGrBiYG9FfZgb8XpYbWFkHNlV4SY+VwW1NLVOJHICfz1hOi/jrdeHsn7gJXLng0XgLAbnA310YKzkImQ3FY7Bxdf8kQLGfMqU4xEWNQEdT/bQzHF2dG+hrVx3d8PkXu6/uhs0KY5KFzDr6mOIAmkauDQGzjouWRzVwbovg3SNMB2s+zKEQ4EG/04AwqEAhEOBKLIJCGwoNAvpyeHcHp0R0teCc2p8LqQvMGaQ7Qky1+EB0o9sAtaCdV8G6c9o6m5ViAKryCVglTr7kArq6PP5Wp7FJ4BLQroO4BzD54X0hYSEhADwC0RY10F3B9rMAAAAAElFTkSuQmCC "Favicon for https://endpoints.huggingface.co/new?accelerator=gpu&catalog\_id=300&instance\_id=aws-us-east-1-nvidia-l40s-x1&no\_suggested\_compute=true&repository=black-forest-labs%2FFLUX.1-schnell&task=text-to-image&vendor=aws")](https://endpoints.huggingface.co/new?accelerator=gpu&catalog_id=300&instance_id=aws-us-east-1-nvidia-l40s-x1&no_suggested_compute=true&repository=black-forest-labs%2FFLUX.1-schnell&task=text-to-image&vendor=aws)**[endpoints.huggingface.co**](https://endpoints.huggingface.co/new?accelerator=gpu&catalog_id=300&instance_id=aws-us-east-1-nvidia-l40s-x1&no_suggested_compute=true&repository=black-forest-labs%2FFLUX.1-schnell&task=text-to-image&vendor=aws)

***[Pricing and Billing**](https://huggingface.co/docs/inference-providers/en/pricing)

***[https://huggingface.co/docs/inference-providers/en/pricing**](https://huggingface.co/docs/inference-providers/en/pricing)

*[![](data:image/png;base64,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 "Favicon for https://huggingface.co/docs/inference-providers/en/pricing")](https://huggingface.co/docs/inference-providers/en/pricing)**[huggingface.co**](https://huggingface.co/docs/inference-providers/en/pricing)

***[black-forest-labs/FLUX.1-schnell · Hugging Face**](https://huggingface.co/black-forest-labs/FLUX.1-schnell)

***[https://huggingface.co/black-forest-labs/FLUX.1-schnell**](https://huggingface.co/black-forest-labs/FLUX.1-schnell)

*[![](data:image/png;base64,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 "Favicon for https://huggingface.co/black-forest-labs/FLUX.1-schnell")](https://huggingface.co/black-forest-labs/FLUX.1-schnell)**[huggingface.co**](https://huggingface.co/black-forest-labs/FLUX.1-schnell)

***[URGENT — HELP — Unusable inference credits after FLUX.1-schnell removal - Beginners - Hugging Face Forums**](https://discuss.huggingface.co/t/urgent-help-unusable-inference-credits-after-flux-1-schnell-removal/177901)

***[https://discuss.huggingface.co/t/urgent-help-unusable-inference-credits-after-flux-1-schnell-removal/177901**](https://discuss.huggingface.co/t/urgent-help-unusable-inference-credits-after-flux-1-schnell-removal/177901)

*[![](data:image/png;base64,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 "Favicon for https://discuss.huggingface.co/t/urgent-help-unusable-inference-credits-after-flux-1-schnell-removal/177901")](https://discuss.huggingface.co/t/urgent-help-unusable-inference-credits-after-flux-1-schnell-removal/177901)**[discuss.huggingface.co**](https://discuss.huggingface.co/t/urgent-help-unusable-inference-credits-after-flux-1-schnell-removal/177901)

***[Hugging Face Inference Providers · Supported Models**](https://huggingface.co/inference/models)

***[https://huggingface.co/inference/models**](https://huggingface.co/inference/models)

*[![](data:image/png;base64,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 "Favicon for https://huggingface.co/inference/models")](https://huggingface.co/inference/models)**[huggingface.co**](https://huggingface.co/inference/models)

*![]()**$0.1611,802 tok**

*![](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNzkuNSIgaGVpZ2h0PSIyNzkuNSIgcHJlc2VydmVBc3BlY3RSYXRpbz0ieE1pZFlNaWQiIHZpZXdCb3g9Ii0xMS43NSAtOS43NSAyNzkuNSAyNzkuNSI+PHBhdGggIGQ9Ik0yMzkuMTg0IDEwNi4yMDNhNjQuNzE2IDY0LjcxNiAwIDAgMC01LjU3Ni01My4xMDNDMjE5LjQ1MiAyOC40NTkgMTkxIDE1Ljc4NCAxNjMuMjEzIDIxLjc0QTY1LjU4NiA2NS41ODYgMCAwIDAgNTIuMDk2IDQ1LjIyYTY0LjcxNiA2NC43MTYgMCAwIDAtNDMuMjMgMzEuMzZjLTE0LjMxIDI0LjYwMi0xMS4wNjEgNTUuNjM0IDguMDMzIDc2Ljc0YTY0LjY2NSA2NC42NjUgMCAwIDAgNS41MjUgNTMuMTAyYzE0LjE3NCAyNC42NSA0Mi42NDQgMzcuMzI0IDcwLjQ0NiAzMS4zNmE2NC43MiA2NC43MiAwIDAgMCA0OC43NTQgMjEuNzQ0YzI4LjQ4MS4wMjUgNTMuNzE0LTE4LjM2MSA2Mi40MTQtNDUuNDgxYTY0Ljc2NyA2NC43NjcgMCAwIDAgNDMuMjI5LTMxLjM2YzE0LjEzNy0yNC41NTggMTAuODc1LTU1LjQyMy04LjA4My03Ni40ODNabS05Ny41NiAxMzYuMzM4YTQ4LjM5NyA0OC4zOTcgMCAwIDEtMzEuMTA1LTExLjI1NWwxLjUzNS0uODcgNTEuNjctMjkuODI1YTguNTk1IDguNTk1IDAgMCAwIDQuMjQ3LTcuMzY3di03Mi44NWwyMS44NDUgMTIuNjM2Yy4yMTguMTExLjM3LjMyLjQwOS41NjN2NjAuMzY3Yy0uMDU2IDI2LjgxOC0yMS43ODMgNDguNTQ1LTQ4LjYwMSA0OC42MDFabS0xMDQuNDY2LTQ0LjYxYTQ4LjM0NSA0OC4zNDUgMCAwIDEtNS43ODEtMzIuNTg5bDEuNTM0LjkyMSA1MS43MjIgMjkuODI2YTguMzM5IDguMzM5IDAgMCAwIDguNDQxIDBsNjMuMTgxLTM2LjQyNXYyNS4yMjFhLjg3Ljg3IDAgMCAxLS4zNTguNjY1bC01Mi4zMzUgMzAuMTg0Yy0yMy4yNTcgMTMuMzk4LTUyLjk3IDUuNDMxLTY2LjQwNC0xNy44MDNaTTIzLjU0OSA4NS4zOGE0OC40OTkgNDguNDk5IDAgMCAxIDI1LjU4LTIxLjMzM3Y2MS4zOWE4LjI4OCA4LjI4OCAwIDAgMCA0LjE5NSA3LjMxNmw2Mi44NzQgMzYuMjcyLTIxLjg0NSAxMi42MzZhLjgxOS44MTkgMCAwIDEtLjc2NyAwTDQxLjM1MyAxNTEuNTNjLTIzLjIxMS0xMy40NTQtMzEuMTcxLTQzLjE0NC0xNy44MDQtNjYuNDA1di4yNTZabTE3OS40NjYgNDEuNjk1LTYzLjA4LTM2LjYzTDE2MS43MyA3Ny44NmEuODE5LjgxOSAwIDAgMSAuNzY4IDBsNTIuMjMzIDMwLjE4NGE0OC42IDQ4LjYgMCAwIDEtNy4zMTYgODcuNjM1di02MS4zOTFhOC41NDQgOC41NDQgMCAwIDAtNC40LTcuMjEzWm0yMS43NDItMzIuNjktMS41MzUtLjkyMi01MS42MTktMzAuMDgxYTguMzkgOC4zOSAwIDAgMC04LjQ5MiAwTDk5Ljk4IDk5LjgwOFY3NC41ODdhLjcxNi43MTYgMCAwIDEgLjMwNy0uNjY1bDUyLjIzMy0zMC4xMzNhNDguNjUyIDQ4LjY1MiAwIDAgMSA3Mi4yMzYgNTAuMzkxdi4yMDVaTTg4LjA2MSAxMzkuMDk3bC0yMS44NDUtMTIuNTg1YS44Ny44NyAwIDAgMS0uNDEtLjYxNFY2NS42ODVhNDguNjUyIDQ4LjY1MiAwIDAgMSA3OS43NTctMzcuMzQ2bC0xLjUzNS44Ny01MS42NyAyOS44MjVhOC41OTUgOC41OTUgMCAwIDAtNC4yNDYgNy4zNjdsLS4wNTEgNzIuNjk3Wm0xMS44NjgtMjUuNTggMjguMTM4LTE2LjIxNyAyOC4xODggMTYuMjE4djMyLjQzNGwtMjguMDg2IDE2LjIxOC0yOC4xODgtMTYuMjE4LS4wNTItMzIuNDM0WiIvPjwvc3ZnPgo= "Favicon for openai")**GPT Sol Latest**

# ***Movie Builder Skill Implementation Plan**

***Status: Design proposal only. No Skill, renderer, image adapter, or QA scripts are being implemented in this round.**

***Core responsibility:**

***Movie Builder turns assets, audio, and editing intentions into a playable video through deterministic timeline compilation, media generation where authorized, FFmpeg rendering, and bounded quality checks.***

***It should work independently for ordinary narrated videos, while accepting complete plans from Story Director and measured timing from Narration Studio.**

***Scope boundary: Build a small production pipeline—not a general-purpose editor, agent framework, or animation system.**


## ***1. Skill name and triggering description**

### ***Proposed name**

***Movie Builder**

***Suggested package identifier: `movie-builder`.**

### ***Proposed triggering description**

***Assemble narrated videos from images, video clips, audio, captions, and optional creative plans. Use for narrated slideshows, educational videos, timed visual reveals, simple graphics, image generation, cuts, holds, zooms, pans, fades, MP4 rendering, contact sheets, and video QA. Resolve available speech timing into a deterministic timeline and render with FFmpeg when execution tools are available. Support supplied assets without paid services. Do not claim accurate speech synchronization when timing data is unavailable.***

### ***Example requests**

- “***Make a narrated video from these pictures and this MP3.”**

- “***Render this director plan using the attached narration manifest.”**

- “***Show this statistic when the narrator says ‘fourteen.’”**

- “***Replace this image without regenerating the others.”**

- “***Make a contact sheet and check this video for timing problems.”**

- “***Generate the missing illustrations, but stay within this budget.”**

### ***Execution boundary**

***The Skill must inspect available tools, files, storage, and credentials before promising execution.**

***If FFmpeg or executable tools are unavailable, it may prepare a validated production package and setup instructions. It must clearly state that no movie was rendered.**


## ***2. Standalone use cases**

### ***A. Supplied images and narration**

***Accept images and an MP3/WAV, with optional script or timestamps.**

***Choose among three explicit timing modes:**

| Available information | Behavior |
| - | - |
| Complete shot timing | Compile and render |
| Script plus usable speech timing | Plan a modest edit and resolve against timing |
| Audio and images only | Create a clearly labeled pacing-based slideshow |

***A pacing-based slideshow is useful, but must not be described as semantically synchronized.**

***If a script exists but timestamps do not, Movie Builder may use an optional alignment dependency without requiring the Narration Studio Skill. Otherwise, offer timing preparation or proceed with the simpler mode.**

### ***B. Educational video**

***Combine supplied illustrations with programmatically rendered:**

- ***Title cards.**

- ***Statistics.**

- ***Tables.**

- ***Simple charts.**

- ***Equations, when a supported mathematical renderer is available.**

***Generated imagery can provide atmosphere; exact labels and mathematics should remain separate layers.**

### ***C. Existing image and video assembly**

***Support a limited combination of:**

- ***Still-image shots.**

- ***Trimmed video clips.**

- ***Primary narration.**

- ***Optional source-clip audio.**

***By default, imported video audio should be muted when narration is the master. Keeping it requires an explicit instruction.**

### ***D. Captioning and graphics**

***Add SRT or structured captions, simple text overlays, and graphic cards.**

***Support readable styling and safe margins without requiring a full layout engine.**

### ***E. Inspection and repair**

***Accept an existing video or saved project to:**

- ***Extract screenshots.**

- ***Create a contact sheet.**

- ***Run technical QA.**

- ***Replace an asset.**

- ***Adjust a cut.**

- ***Rerender.**

***Replacing one image should avoid regenerating unrelated assets. It need not avoid re-encoding the complete video.**


## ***3. Cooperative workflow**

### ***Inputs from Story Director**

- ***Script references and source revision.**

- ***Creative shots and their purposes.**

- ***Asset specifications and reuse instructions.**

- ***Script-relative timing anchors.**

- ***Reveal constraints.**

- ***Requested pauses and fallbacks.**

- ***Visual style and generation budget.**

### ***Inputs from Narration Studio**

- ***Declared audio master and audio revision.**

- ***Sample rate and duration.**

- ***Actual clip placements.**

- ***Sentence, phrase, or word timing where available.**

- ***Realized silence events.**

- ***Source-to-spoken mappings.**

- ***Unresolved anchors and timing provenance.**

- ***Optional caption candidates.**

### ***Movie Builder process**

1. ***Validate compatible inputs.**

2. ***Resolve asset availability.**

3. ***Generate authorized missing assets.**

4. ***Resolve timing anchors.**

5. ***Apply optional overrides.**

6. ***Compile a concrete timeline.**

7. ***Validate the timeline.**

8. ***Render.**

9. ***Generate contact sheets and QA reports.**

***A complete compatible plan must not require manual shot assignment.**

***If realization fails, return a narrow issue:**

“***The requested reaction pause is absent. The plan permits omitting the reaction hold.”***

***Do not silently rewrite the story or replace a protected reveal with a materially different edit.**

### ***Ownership**

***Movie Builder owns the realized visual timeline. Story Director remains responsible for creative intent; Narration Studio remains responsible for audio measurements.**

***A missing word timestamp is an audio-timing problem, not something the renderer should guess.**


## ***4. Recommended `SKILL.md` and supporting files**

### ***`SKILL.md` outline**

1. ***Metadata and scope.**

2. ***Check execution environment.**

3. ***Identify standalone or cooperative workflow.**

4. ***Inspect and normalize media.**

5. ***Resolve missing assets and spending authorization.**

6. ***Compile timing and apply overrides.**

7. ***Validate before rendering.**

8. ***Render with supported operations.**

9. ***Run QA and create review outputs.**

10. ***Handle failures and targeted revisions.**

11. ***State exactly what was produced.**

### ***Proposed package**

```
***`movie-builder/`**

`├── ***SKILL.md`**

`├── ***references/`**

`│   ├── ***input-contract.md`**

`│   ├── ***timeline-format.md`**

`│   ├── ***rendering-rules.md`**

`│   ├── ***image-providers.md`**

`│   └── ***qa-and-tests.md`**

`├── ***scripts/`**

`│   ├── ***inspect\_media.py`**

`│   ├── ***compile\_timeline.py`**

`│   ├── ***prepare\_assets.py`**

`│   ├── ***render\_video.py`**

`│   ├── ***inspect\_video.py`**

`│   └── ***create\_contact\_sheet.py`**

`└── ***examples/`**

`    ├── ***supplied\_assets\_project.json`**

`    └── ***cooperative\_project.json`**
```

***These are proposed files, not existing implementations.**

### ***Dependencies**

***Initial baseline:**

- ***Python.**

- ***FFmpeg and FFprobe.**

- ***One lightweight image library for graphics and contact sheets.**

***Optional dependencies:**

- ***Alignment tooling.**

- ***An image-provider SDK or HTTP client.**

- ***A mathematical rendering tool.**

- ***A local image-generation endpoint.**

***Do not require all optional stacks to be installed.**


## ***5. FFmpeg rendering architecture**

### ***A. Inspect and normalize**

***Use FFprobe and image inspection to establish:**

- ***Duration.**

- ***Dimensions.**

- ***Frame rate.**

- ***Audio properties.**

- ***Rotation metadata.**

- ***Supported decoding.**

- ***File integrity.**

***Prepare assets consistently:**

- ***Fit or crop images.**

- ***Respect orientation.**

- ***Produce adequate dimensions for camera movement.**

- ***Render exact-text overlays.**

- ***Handle transparency explicitly.**

***Default to fit/pad rather than cropping away important content when composition is uncertain.**

### ***B. Compile the timeline**

***The compiler is deterministic given the same saved inputs and overrides.**

***It should:**

1. ***Resolve references.**

2. ***Convert audio timing into render coordinates.**

3. ***Resolve pause-based shots.**

4. ***Apply reveal constraints.**

5. ***Apply overrides.**

6. ***Allocate frame boundaries.**

7. ***Check coverage and transitions.**

8. ***Produce `timeline.json`.**

***No LLM should be needed inside this compiler. Creative choices occur before compilation.**

### ***C. Render a small operation set**

***Initial support:**

- ***Static holds.**

- ***Hard cuts.**

- ***Slow zooms.**

- ***Simple pans.**

- ***Text and image overlays.**

- ***Burned-in captions.**

- ***Trimmed video shots.**

***Add fades only after hard-cut timing is reliable.**

***Use normalized shot clips or a controlled filtergraph, depending on what proves simpler in the first implementation. Avoid building a universal graph abstraction.**

### ***D. Preserve the audio master**

***Do not stretch narration to fit images.**

***The video follows the declared audio duration. The final image may be extended to cover a small frame-rounding remainder.**

***Recommended default export:**

- ***MP4.**

- ***H.264.**

- ***AAC.**

- ***1920 × 1080.**

- ***30 FPS.**

- ***Broadly compatible pixel format such as `yuv420p`.**

***Audio encoding and container behavior can introduce small duration differences. QA should use explicit tolerances, not demand identical reported stream durations.**

### ***E. Handle transitions without drift**

***A fade must have explicit semantics:**

- ***Whether it overlaps adjacent shots.**

- ***Which intended cut time it surrounds.**

- ***How much neighboring material is needed.**

***Do not subtract transition durations repeatedly and shift all subsequent reveals.**

***For a protected reveal, avoid an incoming dissolve that exposes the new image early. Default to a hard cut unless the plan explicitly permits otherwise.**


## ***6. Timeline and manifest formats**

***Use two distinct artifacts:**

| Artifact | Purpose |
| - | - |
| Creative input | Script anchors and visual intentions |
| **`timeline.json`** | Resolved media, frame positions, and rendering operations |

***A small `project.json` can reference the inputs and output settings.**

### ***Timing convention**

***For video rendering, use integer frame boundaries.**

***For audio, retain Narration Studio’s sample-frame timing.**

***At 30 FPS, a cut cannot occur at every possible audio sample. The compiler must record how it rounded the requested event.**

***For protected reveals, choose a frame not earlier than the resolved anchor.**

### ***Abbreviated compiled example**

```
***`\{`**

`  ***"schema\_version": "0.1-draft",`**

`  ***"source\_revision": "r1",`**

`  ***"audio\_revision": "a1",`**

`  ***"output": \{`**

`    ***"path": "output/final\_video.mp4",`**

`    ***"width": 1920,`**

`    ***"height": 1080,`**

`    ***"fps\_num": 30,`**

`    ***"fps\_den": 1`**

`  ***\},`**

`  ***"audio": \{`**

`    ***"path": "narration.wav",`**

`    ***"sample\_rate\_hz": 48000,`**

`    ***"total\_frames": 216000`**

`  ***\},`**

`  ***"video\_total\_frames": 135,`**

`  ***"shots": \[`**

`    ***\{`**

`      ***"id": "shot\_001",`**

`      ***"asset\_path": "assets/board.png",`**

`      ***"start\_frame": 0,`**

`      ***"end\_frame": 60,`**

`      ***"fit": "contain",`**

`      ***"camera": \{`**

`        ***"type": "slow\_zoom",`**

`        ***"start\_scale": 1.0,`**

`        ***"end\_scale": 1.05`**

`      ***\}`**

`    ***\},`**

`    ***\{`**

`      ***"id": "shot\_002",`**

`      ***"asset\_path": "assets/board.png",`**

`      ***"start\_frame": 60,`**

`      ***"end\_frame": 90,`**

`      ***"fit": "contain",`**

`      ***"camera": \{`**

`        ***"type": "static"`**

`      ***\}`**

`    ***\},`**

`    ***\{`**

`      ***"id": "shot\_003",`**

`      ***"asset\_path": "assets/reaction.png",`**

`      ***"start\_frame": 90,`**

`      ***"end\_frame": 135,`**

`      ***"fit": "contain",`**

`      ***"camera": \{`**

`        ***"type": "static"`**

`      ***\}`**

`    ***\}`**

`  ***\],`**

`  ***"overlays": \[`**

`    ***\{`**

`      ***"id": "overlay\_001",`**

`      ***"text": "14 HOURS",`**

`      ***"layout": "center\_card",`**

`      ***"start\_frame": 60,`**

`      ***"end\_frame": 90`**

`    ***\}`**

`  ***\],`**

`  ***"resolved\_constraints": \[`**

`    ***\{`**

`      ***"shot\_id": "shot\_002",`**

`      ***"type": "not\_before",`**

`      ***"audio\_anchor\_frame": 96000,`**

`      ***"resolved\_video\_frame": 60,`**

`      ***"status": "satisfied"`**

`    ***\}`**

`  ***\],`**

`  ***"issues": \[\]`**

***`\}`**
```

***Values are illustrative. Start boundaries are inclusive and end boundaries exclusive.**

### ***Manual overrides**

***Keep optional overrides separate from generated inputs.**

***Examples:**

- ***Replace an asset.**

- ***Change fit mode.**

- ***Lock a crop.**

- ***Move a cut relative to an anchor.**

- ***Change caption styling.**

***An absolute-frame override must identify the audio/timeline revision it applies to. Stale overrides should be flagged rather than silently carried forward.**


## ***7. AI image generation adapters**

### ***Minimal proposed interface**

***`generate\_image(request) -\> asset\_result`**

***The request may include:**

- ***Prompt.**

- ***Desired dimensions.**

- ***Optional references.**

- ***Optional seed.**

- ***Provider/model selection.**

- ***Generation settings.**

***The result should include:**

- ***Local file path.**

- ***Actual dimensions.**

- ***Provider and model provenance.**

- ***Supported settings actually applied.**

- ***Request identifier.**

- ***Usage/cost information when available.**

***Do not assume every provider supports references, seeds, negative prompts, or identical dimensions.**

### ***Options to evaluate**

| Option | Proposed role | Important limitation |
| - | - | - |
| Hugging Face Inference Providers | Hosted generation where a suitable routed service exists | A repository listing does not guarantee hosted inference |
| Dedicated Hugging Face endpoint | Controlled deployment | Provisioned compute may cost money while idle |
| Hugging Face Spaces | Possible integration with a suitable API | Public demos are not automatically reliable production services |
| Other hosted services | Alternative image backend | Capabilities, prices, and terms vary |
| Local image endpoint | Existing user-managed GPU workflow | Requires local setup and adequate hardware |
| Supplied images | First prototype and offline mode | Asset relevance and usage rights still matter |

***FLUX-compatible generation is a candidate, not a requirement.**

***No current endpoint availability, prices, or model licensing claims are verified in this plan. Check them during adapter selection.**

***Start with supplied assets, then one hosted or local adapter.**

### ***Exact graphics**

***Use code-rendered assets for numbers, comments, labels, and charts.**

***For equations, require a supported renderer and validated expression. If unavailable, accept a supplied graphic or report the limitation rather than inventing a visually plausible equation.**


## ***8. Cost controls, caching, and fallback behavior**

### ***Cost authorization**

***Before cloud generation, show:**

- ***Number of new assets.**

- ***Provider/model.**

- ***Current rate source, if verified.**

- ***Estimated generation cost.**

- ***Retry allowance.**

- ***Spending cap.**

***Distinguish an estimate from an enforceable provider charge limit.**

***If pricing is unknown, do not describe generation as inexpensive or free.**

### ***Caching**

***Separate:**

1. ***Original supplied/generated assets.**

2. ***Derived crops and graphics.**

3. ***Prepared render media.**

4. ***Compiled timeline.**

5. ***Final output and reports.**

***Image cache keys include prompts, references, model settings, and provider/model revision where available.**

***Store returned images locally. Reuse should not depend on the provider remaining online.**

### ***Fallback rules**

- ***Provider fails: bounded retry, then report or use an authorized alternative.**

- ***Missing image: reuse an approved asset or graphic only when allowed.**

- ***Required reveal timing unresolved: stop that precise operation or use an explicit fallback.**

- ***Unsupported camera move: static shot with a reported substitution.**

- ***Insufficient resolution: warn, reduce movement, or request replacement.**

***A debug render may contain labeled placeholders. A normal final render should not silently contain them.**


## ***9. QA methodology**

### ***Required deterministic QA**

***Before rendering:**

- ***Required assets exist and decode.**

- ***IDs and timing references resolve.**

- ***Shot durations are positive.**

- ***Primary visual coverage is complete.**

- ***Overlaps are intentional transitions.**

- ***Captions fit within the timeline.**

- ***Reveal constraints are satisfied.**

- ***Dimensions and output settings are valid.**

***After rendering:**

- ***Output decodes.**

- ***Video/audio duration is within defined tolerance.**

- ***Expected dimensions, frame rate, codecs, and streams are present.**

- ***No unexpected truncation.**

- ***Black-frame candidates are detected.**

- ***Representative screenshots can be extracted.**

***Black detection is not proof of an error: an intentional dark shot or fade may trigger it. Match detections against declared transitions and flag unexplained intervals.**

### ***Contact sheets**

***Include:**

- ***Shot ID.**

- ***Timestamp.**

- ***Representative frame.**

- ***Corresponding script excerpt.**

- ***Intended shot purpose.**

***Sample midpoints and frames immediately around important cuts. A beginning/midpoint sheet alone can miss premature reveals.**

### ***Optional semantic QA**

***Compare selected assets or screenshots against:**

- ***Script context.**

- ***Intended visual purpose.**

- ***Asset prompt.**

- ***Reveal constraints.**

***Use pre-render asset checks to catch obvious bad generations; use post-render screenshots to inspect cropping and overlays.**

***Semantic QA remains advisory. It must account for intentional contrast and irony.**

***No endless repair loop: define a review budget and retry limit.**


### ***Milestone 1 — Supplied assets, hard cuts, MP4**

***Implement a short narrated slideshow with explicit timing, contact sheet, and technical QA.**

***Acceptance:**

- ***Output decodes.**

- ***All planned shots appear.**

- ***No unintended gaps.**

- ***Narration is not stretched or truncated.**

- ***One asset can be replaced without regenerating others.**

### ***Milestone 2 — Cooperative timing compiler**

***Accept Story Director and Narration Studio fixtures.**

***Acceptance:**

- ***Resolve sentence and word anchors.**

- ***Use a realized pause.**

- ***Reject unresolved required anchors.**

- ***Preserve stable shot IDs.**

- ***Record frame rounding.**

### ***Milestone 3 — Graphics, captions, camera movement**

***Acceptance:**

- ***Exact statistic text is rendered correctly.**

- ***Captions remain within bounds.**

- ***Pan/zoom stays within image coverage.**

- ***Caption presentation does not violate a protected reveal.**

### ***Milestone 4 — Missing-image generation**

***Add one adapter with authorization, caching, and bounded retries.**

***Acceptance:**

- ***Repeated requests reuse completed local assets.**

- ***Failed requests do not lose completed work.**

- ***Provider limitations are reported.**

- ***No unauthorized generation occurs.**

### ***Milestone 5 — Video clips, fades, advisory semantic QA**

***Add only after the basic path is reliable.**

### ***Concrete timing criteria**

***For a 30 FPS test:**

- ***A protected reveal must never precede its trusted anchor.**

- ***Its delay from frame quantization should be less than one frame, excluding alignment uncertainty.**

- ***The planned video endpoint should cover the audio endpoint by less than one frame before encoding.**

- ***Post-encoding stream-duration tolerances must be declared and tested for the selected toolchain.**

- ***Overlapping captions and transitions must be explicitly permitted, not mistaken for primary-shot errors.**

### ***Required failure tests**

- ***Repeated phrase creates ambiguous anchor.**

- ***Audio revision changes.**

- ***Requested pause is absent.**

- ***Image is corrupt.**

- ***Wrong aspect ratio.**

- ***Fade would expose a reveal early.**

- ***Supplied video has unexpected audio.**

- ***Caption is too long for its allotted interval.**

- ***Cloud provider times out.**

- ***Stale override conflicts with the new timeline.**

### ***Integrated demonstration**

***Use the same 60–90-second DOOM excerpt.**

***Demonstrate:**

1. ***An explanatory chalkboard hold.**

2. ***A precise “14 HOURS” reveal.**

3. ***A reaction during an actual pause.**

4. ***A reusable image with a second composition.**

5. ***Contact sheet and QA report.**

***A human viewer should understand the story without reading the source. That is a playback test, not a deterministic certification.**


## ***11. Are the earlier plans sufficient?**

***They provide the right conceptual boundaries, but not yet a complete rendering contract.**

***The missing pieces are specific and manageable.**

| Missing or ambiguous item | Proposed owner/change |
| - | - |
| Audio analysis copy versus actual playback master | Narration Studio must declare which file all timing references describe |
| Source-to-spoken mapping | Narration Studio needs a concrete mapping representation |
| Timing for scripts split/merged into synthesis units | Narration Studio must link source spans to realized timing |
| Meaning of segment start/end | Shared vocabulary must distinguish clip, speech, and script-aligned boundaries |
| Realized pause and creative request linkage | Narration Studio returns request IDs and availability status |
| Asset identity and supplied-file location | Story Director supplies logical IDs; Movie Builder maintains local realizations |
| Crop/fit intent | Story Director may request focal region or preservation; Movie Builder chooses safe defaults |
| Overlay layout | Add a few supported presets rather than unrestricted layout instructions |
| Transition semantics | Define overlap and reveal behavior in Movie Builder’s contract |
| Caption spoiler handling | Story Director defines protection; Narration Studio supplies timing; Movie Builder enforces presentation |
| Supplied video trimming/audio policy | Add explicit trim and audio-handling fields |
| Unsupported required instruction | Shared distinction between required constraints and optional preferences |

### ***Recommended Round 1 revisions**

- ***Add required versus preferred visual instructions.**

- ***Allow focal-region and “do not crop” hints.**

- ***Use operational reveal constraints, not only descriptive labels.**

- ***Supply permitted fallback choices.**

- ***Keep asset prompts independent of generated file paths.**

### ***Recommended Round 2 revisions**

- ***Identify one authoritative timing reference.**

- ***Link realized pauses to requested pauses.**

- ***Define how phrase timings map through pronunciation substitutions.**

- ***Mark complete, partial, and unresolved alignment results.**

- ***Identify whether caption timings are clip-based, speech-based, or word-aligned.**

***These are proposals for Round 4, not silent amendments to earlier plans.**


## ***Ideas Worth Revisiting in Round 4**

1. ***Finalize the smallest shared contract: logical assets, script references, realized audio timing, and compiled shots.**

2. ***Choose anchor semantics: phrase occurrence, source spans, and downstream word IDs.**

3. ***Separate constraints from preferences: required reveals must not be silently relaxed.**

4. ***Declare the authoritative audio master: especially for imported compressed recordings.**

5. ***Define pause fallback behavior: unavailable silence must not create unapproved audio edits.**

6. ***Agree on caption reveal protection: include text as well as imagery.**

7. ***Specify frame rounding and duration tolerance: avoid promises finer than the render frame grid.**

8. ***Decide standalone alignment scope: optional dependency versus handoff to Narration Studio.**

9. ***Choose one image adapter only after verification: availability, cost, capability, and licensing.**

10. ***Keep rerendering simple: independent asset reuse first; segment-level render caching later.**

11. ***Use one end-to-end DOOM test: require an automatically planned, actually rendered movie—not three individually elegant plans.**

***Build the first watchable movie with supplied assets and reliable cuts. Add generation and richer effects only when they address demonstrated shortcomings.**

