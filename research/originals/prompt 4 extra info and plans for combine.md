

***Gemini Pro Latest**

***Reasoning**

***This is the culmination of the architecture design. By strictly enforcing the "Standalone First, Cooperative by Design" principle, we ensure that the AI filmmaker is not a monolithic application that fails completely if one API goes down, but a resilient pipeline of three distinct specialized agents.**

***Here is the final architectural review, reconciliation, and specification for the AI Story-to-Video ecosystem.**


### ***Step 1 & 3: Review, Reconciliation, and Proposed Changes**

***Reviewing the three previous rounds revealed several overlapping responsibilities and missing links. I propose the following core changes to finalize the architecture:**

1. ***Change (Affects Story Director): Split Prompt and Style.**

   - **What:* Story Director must output `visual\_subject` and a global `visual\_style`, rather than one monolithic prompt.**

   - **Why:* Diffusion models perform better when style tags are appended programmatically. This allows Movie Builder to universally enforce a style (e.g., "Mockumentary") across all generated shots.**

2. ***Change (Affects Narration Studio): Absolute Timeline Export.**

   - **What:* Instead of just returning relative clip lengths, Narration Studio must calculate and export absolute timestamps (*T*=0.0 to *T*=*End*) for every clip, silence gap, and requested word anchor.**

   - **Why:* Movie Builder should not do audio math. It should only execute rendering commands.**

3. ***Change (Affects Movie Builder): Offload Audio Muxing to FFmpeg.**

   - **What:* If the skills are working cooperatively, Narration Studio does not* need to concatenate the master WAV file. It passes the cached clips and silence gaps to Movie Builder, which muxes them directly during the final FFmpeg render.**

   - **Why:* Prevents double-compression of audio and saves a processing step. Narration Studio only concatenates a master WAV when used in Standalone* mode.**

4. ***Change (Affects All): Universal ID Format.**

   - **What:* Enforce a strict naming convention: `L\_\#\#\#` (Script Lines), `S\_\#\#\#` (Shots), `A\_\#\#\#` (Assets).**

   - **Why:* Prevents JSON reference collisions between the three independent schemas.**


### ***Step 2: Shared Interoperability Specification (`v1\_schema`)**

***To guarantee these Skills can evolve independently, they communicate via standardized JSON schemas.**

```
***`\{`**

`  ***"version": "1.0",`**

`  ***"metadata": \{"title": "DOOM", "global\_style": "Mockumentary photography"\},`**

`  ***"assets": \{`**

`    ***"A\_001": \{"type": "character", "subject": "Exhausted 1990s computer science student"\}`**

`  ***\},`**

`  ***"script\_lines": \[`**

`    ***\{"id": "L\_001", "speaker": "Narrator", "emotion": "serious", "original\_text": "By day eight.", "spoken\_text": "By day eight."\}`**

`  ***\],`**

`  ***"shots": \[`**

`    ***\{`**

`      ***"id": "S\_001",`**

`      ***"visual\_asset": "A\_001",`**

`      ***"anchor": \{"line\_id": "L\_001", "type": "start\_of\_line"\},`**

`      ***"directive": "deadpan\_hold",`**

`      ***"camera": "zoom\_in"`**

`    ***\}`**

`  ***\]`**

***`\}`**

***`\{`**

`  ***"version": "1.0",`**

`  ***"duration\_seconds": 3.4,`**

`  ***"events": \[`**

`    ***\{`**

`      ***"type": "clip",`**

`      ***"line\_id": "L\_001",`**

`      ***"file": "cache/hash123.wav",`**

`      ***"start\_time": 0.0,`**

`      ***"end\_time": 2.1,`**

`      ***"requested\_anchors": \{\}`**

`    ***\},`**

`    ***\{`**

`      ***"type": "silence",`**

`      ***"duration": 1.3,`**

`      ***"start\_time": 2.1,`**

`      ***"end\_time": 3.4`**

`    ***\}`**

`  ***\]`**

***`\}`**
```


### ***Step 4: Revised Implementation Plans (Final Plan v1)**

- ***Standalone Purpose: Act as an AI pre-production assistant, analyzing scripts to generate storyboards, character bibles, and pacing plans.**

- ***Trigger Condition: "I need a storyboard," "Break down this script," "Generate a Narrative Manifest for..."**

- ***Inputs: Raw text, story concepts, or educational material.**

- ***Outputs: Markdown storyboard (Standalone) or `NarrativeManifest.json` (Cooperative).**

- ***Internal Workflow:**

  1. ***Chunk text into logical beats. 2. Identify speakers/emotions. 3. Define reusable assets. 4. Map shots to script anchors using the `L\_\#\#\#` and `S\_\#\#\#` ID system.**

- ***Fallback Behavior: If the script lacks clear visual cues, default to generating "B-roll" concepts based on the script's themes.**

- ***Files: `SKILL.md`, `agents/openai.yaml`, `prompts/story\_heuristics.md`, `schemas/manifest\_v1.json`.**

- ***Standalone Purpose: Generate TTS audiobooks, chunked audio files, and align provided MP3s to text for timing extraction.**

- ***Trigger Condition: "Generate narration for this script," "Align this MP3 to my text," "Create a voiceover with pauses."**

- ***Inputs: Raw text, `NarrativeManifest.json`, or user MP3.**

- ***Outputs: Master `narration.wav` + `subtitles.srt` (Standalone), or `audio\_timeline.json` + cached WAV clips (Cooperative).**

- ***Internal Workflow:**

  1. ***Parse text. 2. Apply pronunciation dictionary. 3. Hash and check cache. 4. Generate missing chunks via local TTS (Piper/Kokoro) or API. 5. Measure chunk durations. 6. Execute forced-alignment only* on chunks containing requested anchors.**

- ***Fallback Behavior: If a requested API voice fails, gracefully fallback to a local CPU TTS model and flag a warning.**

- ***Files: `SKILL.md`, `agents/openai.yaml`, `scripts/tts\_cacher.py`, `scripts/aligner.py`, `schemas/audio\_timeline\_v1.json`.**

- ***Standalone Purpose: Compile folders of images and audio into synchronized MP4s using deterministic FFmpeg commands.**

- ***Trigger Condition: "Render a video from these assets," "Compile my Narrative Manifest into an MP4."**

- ***Inputs: Images/MP3 (Standalone) OR `NarrativeManifest.json` + `audio\_timeline.json` (Cooperative).**

- ***Outputs: `final\_movie.mp4`, `contact\_sheet.jpg`, `qa\_report.json`.**

- ***Internal Workflow:**

  1. ***Ingest timelines. 2. Request missing image assets via Image Adapters (e.g., Hugging Face FLUX). 3. Generate text overlay layers natively. 4. Compile a deterministic FFmpeg `concat` and filtergraph. 5. Render. 6. Run `ffprobe` QA.**

- ***Fallback Behavior: If image generation API credits are exhausted or rate-limited, substitute a gray placeholder image with the prompt text overlaid to allow the render to finish for pacing review.**

- ***Files: `SKILL.md`, `agents/openai.yaml`, `scripts/ffmpeg\_compiler.py`, `scripts/image\_adapters.py`, `scripts/qa\_checker.py`.**


### ***Step 5: Cross-Skill Test Matrix**

- ***Test A (Story Director Alone): Input a 3-paragraph mockumentary script. Success:* Generates a valid JSON manifest that successfully deduplicates recurring characters into a single `asset\_id`.**

- ***Test B (Narration Studio Alone): Input a 5-line script and change one word on the 2nd run. Success:* Generates a master WAV. On the 2nd run, it only processes TTS for the changed line, pulling the rest from cache, and outputs a perfectly updated master WAV.**

- ***Test C (Movie Builder Alone): Input 5 placeholder JPEGs, a 10-second MP3, and a manually written timeline JSON. Success:* Outputs a 1080p 30fps MP4 using FFmpeg without MoviePy, with proper fade transitions.**

- ***Test D (Integrated Pipeline): Input the DOOM Chalkboard* excerpt.**

  - **Success Criteria:* Story Director maps a "reaction\_shot" to the word "Bang". Narration Studio finds the exact millisecond "Bang" occurs and inserts a 2-second silence after it. Movie Builder generates the chalkboard image via FLUX and executes a hard cut to Kevin exactly on the word "Bang", holding the visual through the calculated silence gap.**


### ***Step 6: Implementation Sequence & Packaging**

***Each Skill will be packaged in its own repository/directory with its own `requirements.txt`.**

1. ***Phase 1: Movie Builder (The Engine). Why:* If we cannot manually write a JSON file that FFmpeg successfully renders, the AI planning steps are useless. Build the Python → FFmpeg compiler first.**

2. ***Phase 2: Narration Studio (The Metronome). Why:* Audio dictates time. Build the chunk-and-cache TTS system next to feed accurate data to the Movie Builder.**

3. ***Phase 3: Story Director (The Brain). Why:* Once the engine and metronome exist, prompt engineer the LLM to output the exact JSON schemas they require.**


### ***Step 7: Final Decision Log**

- ***Accepted: FFmpeg as sole renderer; Sentence-chunked TTS caching; Explicit text-anchor timing over invented timestamps.**

- ***Modified: Audio concatenation. Moved final audio mixing from Narration Studio to Movie Builder for cooperative workflows to prevent double-encoding.**

- ***Rejected: Semantic QA via Vision Language Models (too slow/unreliable for V1). MoviePy as a rendering engine (too much overhead/memory leakage).**

- ***Deferred (To V2): Declarative HTML/SVG layout engines; Automatic background music ducking (sticking to dialogue/SFX for V1).**

- ***Still requiring experimental verification: How tightly `stable-ts` can isolate a single word anchor inside a 2-second generated TTS clip without hallucinating.**


### ***Final Challenge: How do they evolve independently?**

***The three Skills can evolve without breaking the pipeline because they are decoupled by the versioned JSON schemas (`v1\_schema`).**

- ***If the developer wants to swap out `stable-ts` for a new state-of-the-art aligner in Narration Studio, Movie Builder doesn't care—it just needs the absolute timestamps in `audio\_timeline\_v1.json`.**

- ***If Movie Builder adds support for Unreal Engine rendering instead of FFmpeg, Story Director doesn't need to change its prompts; it just keeps outputting `NarrativeManifest\_v1.json`.**

- ***By treating the outputs of each Skill as standard, immutable contracts, the underlying technologies (LLMs, TTS models, Diffusion models, Renderers) can be upgraded infinitely without shattering the pipeline.**

***$0.0913,788 tok**

*![](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1MTIiIGhlaWdodD0iNTEyIiBzaGFwZS1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVF1YWxpdHkiIGZpbGwtcnVsZT0iZXZlbm9kZCIgY2xpcC1ydWxlPSJldmVub2RkIiB2aWV3Qm94PSIwIDAgNTEyIDUxMiI+PHJlY3QgZmlsbD0iI0NDOUI3QSIgd2lkdGg9IjUxMiIgaGVpZ2h0PSI1MTIiIHJ4PSIxMDQuMTg3IiByeT0iMTA1LjA0MiIvPjxwYXRoIGZpbGw9IiMxRjFGMUUiIGZpbGwtcnVsZT0ibm9uemVybyIgZD0iTTMxOC42NjMgMTQ5Ljc4N2gtNDMuMzY4bDc4Ljk1MiAyMTIuNDIzIDQzLjM2OC4wMDQtNzguOTUyLTIxMi40Mjd6bS0xMjUuMzI2IDBsLTc4Ljk1MiAyMTIuNDI3aDQ0LjI1NWwxNS45MzItNDQuNjA4IDgyLjg0Ni0uMDA0IDE2LjEwNyA0NC42MTJoNDQuMjU1bC03OS4xMjYtMjEyLjQyN2gtNDUuMzE3em0tNC4yNTEgMTI4LjM0MWwyNi45MS03NC43MDEgMjcuMDgzIDc0LjcwMWgtNTMuOTkzeiIvPjwvc3ZnPgo= "Favicon for anthropic")**Claude Opus Latest**

***Reasoning**

***Searched for OpenAI skills agents/openai.yaml interface display\_name short\_description allow\_implicit\_invocation5 results**

***Reasoning**

# ***Round 4 of 4: Final architecture and Skill plans v1**

***This is still planning. Nothing has been built, run or benchmarked. Where the earlier rounds used ⏳ for provisional decisions, this round decides them or moves them to the "still needs experiment" list in the decision log (§7).**

***Verified today: the `agents/openai.yaml` format from OpenAI's own [`openai/skills` repo](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md). It has `interface` fields (`display\_name`, a `short\_description` of 25–64 characters, `default\_prompt` mentioning `$skill-name`, and icons), `policy.allow\_implicit\_invocation`, and `dependencies.tools`, which currently supports only MCP. That repo documents Codex. I haven't confirmed that ChatGPT's Skills read this file, or that they allow network access and package installs in the sandbox. Both affect what can run inside ChatGPT.**


## ***1. Review of Rounds 1–3**

### ***Conflicts and duplicate work**

| \# | Problem | Where | Resolution |
| - | - | - | - |
| 1 | **Two or three segmenters.** Story Director's **`segment\_script.py`**, Narration Studio's own segmentation, and Read-Aloud's rules | R1, R2 | One segmenter in a shared core file (§3) |
| 2 | **Three caption makers.** Narration Studio's SRT export, Movie Builder's chunking, and Story Director's spoiler rules | R2, R3 | One **`chunk\_captions()`** that accepts forced break points |
| 3 | **Two Audacity label parsers.** Narration Studio's round-trip and Movie Builder's Read-Aloud import | R2, R3 | One parser in core |
| 4 | **Anchor resolution had no owner.** R2 suggested **`anchors\_resolved.json`**; R3 put **`resolve.py`** in Movie Builder | R2, R3 | A pure function in core. **No resolved-anchors file**, because it would be one more file that goes stale |
| 5 | **Prompt assembly in two places.** R1 wrote full prompts; R3 said Movie Builder assembles them | R1, R3 | Director writes **`subject`** only. A simple template join lives in core (for Director's prompt-pack mode and for Builder); model-specific changes live in Builder's adapters |
| 6 | **The pause table was owned by Narration Studio, but Builder's QA needs it** to say a hold was too short | R1–R3 | The default table goes in the shared spec, overridable in **`style.yaml`** |
| 7 | **`overrides.json` was used by everyone and defined by no one** until R3, which only covered shots and assets | All | One file with a section per Skill (§3.7) |
| 8 | **Who adds the lead-in silence** was unclear | R2, R3 | Movie Builder. **`narration.wav`** contains speech plus the pauses between segments, nothing more |

### ***Weak designs I'm overturning**

| Earlier claim | Problem | Change |
| - | - | - |
| **R3: render each shot separately, cache it, add transition clips, then concat** | This is the most complex part of the whole design, and it exists to make re-renders fast, a problem nobody has measured. It also causes two lossy encodes and needs identical stream settings across every intermediate file | **v1 renders the whole timeline in one pass.** A frame generator pipes frames to FFmpeg, which encodes once. Caching stays at the asset level (images and cards). Per-shot caching is deferred until a benchmark shows re-rendering is too slow |
| **R3: export speech-active intervals separately** | They can be derived from each segment's voiced times | Rejected; derive them |
| **R1: validator rule "every payoff needs a hard cut"** | Too rigid. Some payoffs land better on a hold | Changed to a warning |
| **R1: no digits in image prompts** | Causes false alarms on prompts like "1990s computer lab" | Changed to a warning; quoted strings are still an error |
| **R1: `assets.\*.status: "reuse"`** | Duplicates what shared IDs already say | Removed (as R3 proposed) |
| **R2: "verified from app.js"** | It wasn't verified. Corrected in R3 | §7 lists only the facts verified in R3 |
| **R2: per-segment loudness ±1 LU** | A tolerance invented before any measurement | Kept as a measurement to make, not a requirement |

### ***Good ideas from later rounds to apply earlier**

- ***Animatics (R3) become Story Director's preview path and* the default first output of the combined workflow. They check timing for free.**

- ***Voiced-edge resolution (R3) means Story Director's anchors can simply say "segment start." Narration Studio has to supply `voiced` times; this isn't optional.**

- ***Caption break points at reveals (R3) imply that Narration Studio's standalone SRT, which doesn't know about reveals, is a draft*. Captions for a finished video come from Movie Builder.**

- ***Source tags on timings (R2) feed Movie Builder's confidence handling, and Story Director's `importance: critical` decides which segments get a second timing check.**

- ***`framing`, `overlays`, `layout` (R3) are added to Story Director's schema.**

- ***Read-Aloud's heading-gap quirk (R3, verified) becomes a Narration Studio import warning.**

### ***What's still missing**

- ***Version skew. Nobody has said what happens when the Skills are at different versions. Answered in §3.1 and the final section.**

- ***A shared error format. Each Skill invented its own warnings. One format is defined in §3.8.**

- ***A single project-folder layout, so each Skill knows where to find the others' files.**

- ***Speaker identity across files. R1 used `kevin` in the plan, R2 had `cast.json`. They must use the same `speaker\_id`.**


## ***2. Unified architecture**

```
`           ┌──────────────── ***project folder (shared spec "filmkit 1.x") ────────────────┐`**

***`story.md ─►│ script.json ── plan.json ── narration.json + narration.wav ── timeline.json │─► final.mp4`**

`           │      ▲             ▲                 ▲                          ▲          │`

`           │      │             │                 │                          │          │`

`           │  ***any Skill    Story Director   Narration Studio           Movie Builder    │`**

`           │  ***(core seg.)                                                               │`**

`           │  ***style.yaml (optional, read by all)   overrides.json (sectioned, read by all)│`**

`           │  ***reports/\*.json (shared issue format) cache/ (shared sidecar format)        │`**

`           └────────────────────────────────────────────────────────────────────────────┘`
```

***Rules that make this work:**

1. ***The Skills communicate through files only. No Skill imports another Skill's code, and none calls another directly.**

2. ***One small core file is copied into each Skill: `filmkit\_core.py`, standard library only, about 600–900 lines (estimate). It contains the segmenter, hashing, schema checks, anchor resolver, caption chunker, label I/O, prompt template join and issue reporting. No engines go in it: no TTS, no FFmpeg, no image providers.**

3. ***`script.json` is created once and never re-segmented from scratch. Later runs diff the new text against it and keep existing IDs. This one rule is what lets the core evolve without breaking old projects.**

4. ***Every timing number comes from code. The LLM writes anchors and categories only.**

5. ***Every stage has a free fallback: a manual storyboard, placeholder silence, a placeholder card. A run always finishes and reports what it substituted.**


## ***3. Shared interoperability spec: `filmkit` 1.0**

### ***3.1 Versioning**

- ***Every file has `"schema": "filmkit/\<kind\>@1.0"`.**

- ***Minor version (1.x): adds optional fields only. Readers must ignore unknown fields and must work if any optional field is missing.**

- ***Major version: a breaking change. A reader that gets a higher major version than it supports stops with a message saying what to update. It never guesses.**

- ***Each Skill declares `reads: filmkit 1.0–1.x`, `writes: 1.N`.**

- ***A conformance fixture set (the golden DOOM project, plus edge cases) ships inside every Skill's `assets/fixtures/`. Each Skill's tests check that it reads and writes those files correctly. That suite is* the contract.**

### ***3.2 Project layout**

```
***`project/`**

`├── ***story.md                 input`**

`├── ***style.yaml               optional, shared`**

`├── ***script.json              text authority`**

`├── ***plan.json                Story Director`**

`├── ***cast.json                Narration Studio`**

`├── ***narration.wav            Narration Studio (or user audio, referenced)`**

`├── ***narration.json           timing authority`**

`├── ***overrides.json           humans (sectioned)`**

`├── ***timeline.json            Movie Builder (generated, never hand-edited)`**

`├── ***cache/\{audio,images,cards\}/\<sha\>.\<ext\> + \<sha\>.json`**

`├── ***reports/\{director,narration,builder\}.json`**

`└── ***output/\{final.mp4, captions.srt, contact\_sheet.png, storyboard.md\}`**
```

### ***3.3 `script.json`: identifiers and text**

```
***`\{`**

`  ***"schema": "filmkit/script@1.0",`**

`  ***"segmenter": "filmkit\_core 1.0.0",`**

`  ***"source": \{"file": "story.md", "sha256": "…"\},`**

`  ***"speakers": \{"narrator": \{"name": "Narrator"\}, "sfx\_guy": \{"name": "Sound effects guy"\}\},`**

`  ***"segments": \[`**

`    ***\{"id": "s013", "rev": 1, "para": "p05", "speaker": "sfx\_guy",`**

`     ***"text": "Bang.", "words": \[\{"i": 1, "w": "bang", "raw": "Bang."\}\]\}`**

`  ***\]`**

***`\}`**
```

- ***IDs: `s\#\#\#` is assigned in order the first time. Inserted segments get suffixes (`s013a`). An edited segment keeps its ID and increments `rev`. IDs are opaque; nothing parses meaning from them.**

- ***Words: numbered from 1 within each segment. `raw` keeps the original text exactly as written. `w` is the normalized form used for matching.**

- ***Speakers: `speaker\_id` values here are the only identity used in `plan.json`, `cast.json` and `narration.json`.**

- ***Segmenter rules for v1: Read-Aloud's sentence and abbreviation logic (verified in R3), plus: a quote with an attribution splits into two segments, and headings become segments with `"kind": "heading"`.**

### ***3.4 Display text vs. spoken text**

- ***Display text lives only in `script.json`.**

- ***Spoken text lives only in `narration.json`: `segments.\<id\>.spoken\_text`, plus a `word\_map` of display-word ranges to spoken strings.**

- ***An anchor always names a display word. When a display word expands into several spoken words, the resolver spans all of them.**

### ***3.5 Timing (`narration.json`)**

- ***Master clock: integer samples (`s0`, `s1`) at `audio.sample\_rate`. Seconds are derived.**

- ***Per segment: clip boundaries (`exact` for generated audio), `voiced.start/end` (`measured`, required), optional `words\[\]`, and `status: ok | missing | inserted`.**

- ***Timing sources: `manual \> exact \> measured \> aligned \> model \> interpolated`. A word may be tagged `exact` only if it is the whole segment and its time is the measured voiced edge or an inserted boundary. Validators reject anything else.**

- ***Silences: `\{after, s0, s1, kind: inserted|detected, category?, requested\_s?, actual\_s\}`.**

- ***Pause categories (defaults, heard silence after trimming): `none 0.05 · short 0.15 · beat 0.4 · paragraph 0.7 · long 1.0 · deadpan 2.0` seconds, overridable in `style.yaml`. I changed R1's `beat` from 0.8 to 0.4 and added `paragraph`, so the categories rise steadily. These are untested starting values.**

### ***3.6 Plan objects (`plan.json`)**

```
***`\{`**

`  ***"schema": "filmkit/plan@1.0",`**

`  ***"script\_sha256": "…",`**

`  ***"settings": \{"style": "chalkboard\_mockumentary", "aspect": "16:9",`**

`               ***"max\_unique\_images": 8, "captions": "sentence"\},`**

`  ***"characters": \{"sfx\_guy": \{"visual\_anchor": "bored young man, grey hoodie, headphones around neck",`**

`                             ***"voice\_hint": "young male, flat, tired"\}\},`**

`  ***"beats": \[\{"id": "b\_fire", "segments": \["s012","s013","s014"\], "kind": "payoff", "setup": "b\_wait"\}\],`**

`  ***"narration": \{"s013": \{"pace": "slower", "energy": "flat", "delivery": "exhausted, zero enthusiasm",`**

`                         ***"pause\_after": "deadpan"\}\},`**

`  ***"assets": \{`**

`    ***"img\_classroom\_wide": \{"type": "image", "subject": "dim classroom, huge chalkboard with a hand-drawn first-person corridor, students at desks with paper",`**

`                           ***"caption\_safe": "bottom", "framing\_hints": \{"board": "upper middle"\}\},`**

`    ***"img\_sfx\_guy": \{"type": "image", "characters": \["sfx\_guy"\], "subject": "sitting alone at a desk staring blankly into camera, fluorescent light"\},`**

`    ***"card\_14h": \{"type": "card", "template": "chalk\_title", "layout": "fullscreen",`**

`                 ***"text\_from": \{"seg": "s004", "words": \[5, 6\]\}, "display": "14 HOURS LATER"\}`**

`  ***\},`**

`  ***"shots": \[`**

`    ***\{"id": "bang", "purpose": "reveal", "asset": "img\_sfx\_guy",`**

`     ***"start": \{"seg": "s013", "edge": "start", "nudge": -0.05\},`**

`     ***"transition": \{"type": "cut"\}, "reveal": true, "importance": "critical",`**

`     ***"camera": \{"move": "static"\}, "framing": \{"target": "face", "subject": "sfx\_guy"\}, "overlays": \[\]\}`**

`  ***\]`**

***`\}`**
```

***Changes from R1:**

- ***`subject` replaces `prompt`.**

- ***Added `voice\_hint`, `pace`, `energy`, `caption\_safe`, `framing`, `overlays`, `layout`, and `transition` as an object with an optional duration.**

- ***`reveal\_not\_before` is renamed `reveal`.**

- ***`expect` is still optional on word anchors.**

- ***`display` on cards must be the `text\_from` words, allowing only number reformatting and case changes. Here, "fourteen hours" may become "14 HOURS". Added words such as "LATER" are allowed only if the card sets `editorial: true`, which the validator reports for a human to see. Without this escape hatch, R1's rule would have blocked the demo's own title card.**

### ***3.7 `overrides.json` (sectioned)**

```
***`\{`**

`  ***"schema": "filmkit/overrides@1.0",`**

`  ***"director":  \{"lock\_shots": \["bang"\]\},`**

`  ***"narration": \{"takes": \{"s013": \{"take": 2, "spoken\_sha": "…"\}\},`**

`                ***"pauses": \{"s013": 2.4\}, "spoken\_text": \{"s021": "zero point zero …"\}\},`**

`  ***"builder":   \{"shots": \{"aftermath": \{"hold\_min": 3.0\}\},`**

`                ***"assets": \{"img\_sfx\_guy": \{"lock": true\}\},`**

`                ***"absolute": \[\{"shot": "card\_14h", "start\_t": 21.40, "valid\_for\_audio": "sha256:…"\}\]\}`**

***`\}`**
```

***Each Skill writes only its own section and reads all of them. Story Director never changes anything the others have locked.**

### ***3.8 Shared issue and cache formats**

```
***`\{"code": "anchor\_low\_conf", "severity": "warning", "skill": "movie-builder",`**

` ***"ids": \{"shot": "door\_rage", "seg": "s031", "word": 3\}, "t": 88.4,`**

` ***"msg": "word timed by interpolation", "fix": "add overrides.builder.shots.door\_rage.nudge or re-align s031"\}`**
```

- ***`severity` is `info`, `warning` or `error`. An error stops only the stage that raised it; earlier outputs stay valid.**

- ***A shared list of codes lives in `references/filmkit-spec.md`. Each Skill can add its own codes with a prefix.**

- ***Cache sidecar (`\<sha\>.json`): `\{key\_inputs, tool, tool\_version, model, model\_sha, provider, seed, created, cost\_usd, license, extra\}`. The key is the hash of the canonical JSON of `key\_inputs`.**


## ***4. Proposed changes**

| \# | Skill | What changes | Why | Breaks compatibility? | Migration |
| - | - | - | - | - | - |
| C1 | All | A shared **`filmkit\_core.py`** copy in each Skill | Removes three segmenters, two label parsers, two caption makers | No (new) | R1 and R2 scripts become thin wrappers |
| C2 | Director | **`prompt`** → **`subject`**; assembly moved to core and Builder | Model-specific prompt formats | Yes, for R1 **`plan.json`** | Core reads **`prompt`** as **`subject`** and warns: "style block may be duplicated" |
| C3 | Director | Add **`framing`**, **`overlays`**, **`layout`**, **`caption\_safe`**, **`voice\_hint`**, **`pace`**, **`energy`**, **`editorial`** | Builder and Narration Studio need them (R3 gaps 2–4, R2 §12) | No (additive) | Defaults when missing |
| C4 | Director | Remove **`status: reuse`**; rename **`reveal\_not\_before`** → **`reveal`** | Simplicity | Minor | Reader accepts the old name |
| C5 | Narration | **`voiced`** times required for every segment | Default anchor resolution depends on them | Additive but required | **`measure.py`** can fill them in for old files |
| C6 | Narration | No **`anchors\_resolved.json`** | Avoids a stale duplicate file | n/a | — |
| C7 | Narration | Standalone SRT is labeled a draft; Builder makes final captions | Spoiler-safe chunking needs reveals | No | — |
| C8 | Builder | **Single-pass render**; per-shot cache deferred | Removes the hardest code, the concat parameter matching, and one lossy encode | No (internal) | Asset cache unchanged |
| C9 | Builder | Lead-in and tail are Builder's job only | One owner | No | — |
| C10 | All | Pause table moves to the spec (with **`paragraph`**, **`beat`** = 0.4) | Builder's QA and Narration both need it | Value change | Old values work in **`style.yaml`** |
| C11 | All | Sectioned **`overrides.json`** | Defined ownership | Yes vs. R3's unsectioned draft | Top-level **`shots`**/**`assets`** read as **`builder.\*`** |
| C12 | All | Shared issue and cache formats | One report a user can read | No | — |
| C13 | Director | Payoff-without-a-hard-cut and digits-in-prompts become warnings | Fewer false alarms | No | — |
| C14 | Combined | Default flow: plan → narration → **animatic** → images → final | Free timing check before spending | No | — |


## ***5. Final plans v1**

### ***Story Director: Final Plan v1**

***Standalone purpose: turn any story or script into a beat sheet, storyboard, prompt pack and machine-readable plan, without changing the author's words.**

***Triggers (`SKILL.md` frontmatter, under 1,024 characters):**

```
***`name: story-director`**

***`description: \>`**

`  ***Plans the visual direction for a story, comedy sketch, lesson, or narrated`**

`  ***documentary. Finds beats, speakers, setups, punchlines, reveals, and reaction`**

`  ***moments; writes storyboards, shot lists, image prompts, voice performance`**

`  ***notes, and a plan.json that references the original text by stable IDs. Use`**

`  ***when asked to storyboard, direct, plan visuals or shots, decide where cuts,`**

`  ***cards, or pauses go, or to critique or revise a shot plan or QA report.`**

`  ***Does not generate audio, images, or video, and never rewrites the author's`**

`  ***text unless explicitly asked.`**
```

***Don't trigger for: writing new fiction, TTS, rendering.**

***Inputs:**

- **Required:* story text.**

- **Optional:* `style.yaml`, existing `script.json`, `plan.json`, `overrides.json`, `narration.json` (for real durations), `reports/builder.json`.**

***Outputs: `storyboard.md` (always), `script.json`, `plan.json`, `reports/director.json`, and optionally `prompts.md`.**

***Tools:**

- **Required:* none. Every mode works in plain chat, using the written self-check list.**

- **Optional:* Python 3.10+ running the core segmenter, validator and storyboard renderer.**

***Workflow:**

1. ***Segment with the core segmenter (or manually, stated as `rev: 0`, IDs not stable).**

2. ***Read the whole story: genre, characters, locations, running gags, escalations.**

3. ***Mark beats.**

4. ***Mark comedy and reveals using the R1 pattern table.**

5. ***Plan assets: list reuse candidates first, then add new images only where the visual information changes, and send every exact string to a card.**

6. ***Plan shots with anchors, purposes and intents.**

7. ***Budget pass.**

8. ***Validate, with one repair pass at most.**

9. ***Deliver the storyboard first, the JSON second.**

***Revision from QA (new): given `reports/builder.json` or `narration.json`, make one pass that only touches flagged shots: "s004–s009 runs 41 s on one image," "hold covers 0.8 s." It runs when the user asks, never automatically.**

***Interfaces:**

- **Writes:* `script.json` (via core), `plan.json`, `overrides.director`.**

- **Reads:* everything else, for information only.**

***Files:**

```
***`story-director/`**

`├── ***SKILL.md`**

`├── ***agents/openai.yaml`**

`├── ***references/ beats.md · comedy-timing.md · style-presets.md · subject-writing.md`**

`│               ***filmkit-spec.md (shared) · examples/doom.md · examples/calculus.md`**

`├── ***assets/ fixtures/doom/ (shared golden set) · schemas/ (shared) · storyboard\_template.md`**

`└── ***scripts/ filmkit\_core.py (shared copy) · plan\_tools.py (validate, storyboard, budget)`**
```

***Testing:**

- ***R1 validator rules 1–4 and 6–9, revised as in §4.**

- ***Edit tests: one-word change, sentence insertion, one-field revise diff.**

- ***Fixture conformance.**

- ***Human tests: punchline agreement, measured against your own markings as a baseline, and a storyboard read-back.**

***Fallbacks: no Python → manual segmentation, with a warning. Budget too small → merge shots and report what was merged. Unknown speaker → narrator, with a note. Long text → chunk with a story bible (unverified). Trademarks → describe, don't name.**

***Implementation order: SKILL.md + references → the core segmenter and validator → plan output → QA-driven revise.**


### ***Narration Studio: Final Plan v1**

***Standalone purpose: produce narration audio with precise, honestly labeled timings, from generated speech or the user's own recording.**

***Triggers:**

```
***`name: narration-studio`**

***`description: \>`**

`  ***Turns text into narrated audio and timing data, or times an existing`**

`  ***recording against its script. Renders speech sentence by sentence with local`**

`  ***or hosted TTS, casts multiple speakers, inserts deliberate pauses, fixes`**

`  ***pronunciation, re-renders only changed lines, and exports narration.wav,`**

`  ***narration.json (segment, word, and silence timings with confidence),`**

`  ***draft SRT/VTT, and Audacity labels. Use for audiobooks, voiceovers, dialogue,`**

`  ***read-alouds, pronunciation fixes, or syncing an MP3/WAV to a script.`**

`  ***Does not plan visuals or render video.`**
```

***Inputs:**

- **Required:* text, or audio, or both.**

- **Optional:* `script.json`, `plan.narration`, `cast.json`, `style.yaml`, `overrides.narration`, Read-Aloud WAV and labels.**

***Outputs: `narration.wav` (48 kHz mono PCM, chosen to match video audio), `narration.json`, `cast.json`, `cache/audio/`, `output/draft.srt`, `labels.txt`, `reports/narration.json`.**

***Tools:**

- **Required:* Python, `numpy`, `soundfile`, FFmpeg.**

- **Optional by mode:**

  - ***`sherpa-onnx` with Piper or Kitten voices (default local TTS)**

  - ***`kokoro` (word timings from its duration model, tagged `model`)**

  - ***`faster-whisper` (transcription)**

  - ***one forced aligner, chosen at N4 after a license check**

  - ***`soxr`, `pyloudnorm`**

***Workflow (generated audio):**

1. ***Prepare: segment, normalize numbers, apply the dictionary, build `spoken\_text` and `word\_map`, and show the user a diff of what will be said.**

2. ***Cast voices from `voice\_hint`, with license shown for each voice.**

3. ***Synthesize cache misses only.**

4. ***Measure: trim, voiced edges, loudness.**

5. ***Assemble with pause categories turned into seconds.**

6. ***Add word timing only where needed: segments with a word anchor that isn't the first word, `importance: critical` segments, or `captions: word`.**

7. ***Export.**

***Workflow (supplied audio): load → transcribe → align to the script → reconcile ad-libs and skipped lines → detect silences → compare them with the planned pause categories → export. The recording sets the timing; the script sets the text.**

***Read-Aloud import:**

- ***Labels give clip edges. Voiced edges are measured again.**

- ***Spoken label text is matched back to display text.**

- ***It warns about headings without punctuation getting only the short gap (verified behavior).**

***Interfaces:**

- **Writes:* `narration.\*`, `cast.json`, `overrides.narration`.**

- **Must provide:* `voiced` for every segment.**

***Files:**

```
***`narration-studio/`**

`├── ***SKILL.md · agents/openai.yaml`**

`├── ***references/ engines.md · timing-sources.md · pronunciation.md · pauses.md`**

`│               ***delivery-mapping.md · licenses.md · filmkit-spec.md (shared)`**

`├── ***assets/ fixtures/doom/ · schemas/ · pronunciations.default.tsv · test\_tones/`**

`└── ***scripts/ filmkit\_core.py · prepare.py · synth.py (engine adapters + cache)`**

`             ***measure.py · assemble.py · align.py · reconcile.py · export.py`**
```

***Testing:**

- ***R2 tests 1–18 still apply (cache call counts, sample-exact silences, multiple voices, rejection of `exact` on words, the "Bang" spread measured over 10 renders, `word\_map` spans, ad-lib and skip handling, Audacity round-trip).**

- ***Fixture conformance.**

- ***`assemble.py` is tested with synthetic tone clips, so it needs no TTS engine.**

***Fallbacks:**

- ***No TTS available here → say so, offer the local command, still do alignment-only and prep modes.**

- ***A segment fails → retry, then another voice, then placeholder silence flagged `missing\_audio`.**

- ***Aligner unavailable → `interpolated` times, listed.**

- ***Emotion unsupported → nearest parameters, plus `delivery\_unsupported`.**

***Implementation order: assemble/measure with WAV clips → sherpa-onnx + cache + casting → supplied-audio alignment → pronunciation and `word\_map` → Kokoro word times → selective in-clip alignment → hosted or instruct engines.**


### ***Movie Builder: Final Plan v1**

***Standalone purpose: turn images or clips plus audio into a playable, synced MP4, with cards, captions and QA. Automatic when a plan exists; honestly heuristic when it doesn't.**

***Triggers:**

```
***`name: movie-builder`**

***`description: \>`**

`  ***Builds MP4 videos from images or clips plus narration using FFmpeg: narrated`**

`  ***slideshows, explainers, and animatics with cuts, holds, zooms, pans, fades,`**

`  ***code-rendered title cards and charts, and timed captions. Syncs to`**

`  ***narration.json, SRT, Audacity labels, or detected pauses, and compiles a`**

`  ***story-director plan.json automatically. Can generate missing images through`**

`  ***hosted or local providers with cost estimates and caching. Produces contact`**

`  ***sheets and QA reports. Use to render, re-render, caption, check, or fix a`**

`  ***video. Does not write stories or synthesize narration.`**
```

***Inputs:**

- **Required:* audio plus at least one visual (images, clips, or a plan for an animatic).**

- **Optional:* `plan.json`, `narration.json`, `script.json`, `shots.yaml`, SRT, labels, `style.yaml`, `overrides.builder`.**

***Outputs: `final.mp4` (H.264 `yuv420p`, constant 30 fps, AAC 48 kHz, `+faststart`), `timeline.json`, `captions.srt`, `contact\_sheet.png`, `reports/builder.json`, `cache/images|cards/`.**

***Tools:**

- **Required:* Python, FFmpeg (with libass for burned-in captions), Pillow, `numpy`.**

- **Optional:* matplotlib (charts), `huggingface\_hub` / fal client, local ComfyUI, `imagehash`, and a vision model for advisory QA.**

***Timing sources, in priority order:**

1. ***`narration.json`**

2. ***word timings from SRT, VTT or labels (voiced edges measured again)**

3. ***quoted phrases matched against a transcript (needs Narration Studio or faster-whisper; if neither is available, say so)**

4. ***pause-aware slideshow: silence detection, cuts snapped to pauses, labeled "heuristic"**

5. ***even spacing, only when the user asks for it explicitly**

***Workflow:**

1. ***Load and check: hash chain, licenses against `commercial`, assets, fonts.**

2. ***Compile: resolve anchors with the core resolver, apply overrides, run the R3 constraint pass in order, then convert to frames (*f*=⌈*t*⋅fps⌉ for reveals, nearest frame otherwise) and run timeline QA (T1–T5, C1–C4).**

3. ***Build assets: folder → cache → providers (after a dry-run cost gate) → placeholder. Cards are rendered with Pillow. Framing boxes are centered by default; detection is optional.**

4. ***Render in one pass: a Python frame generator applies camera moves, fades and overlays and pipes the frames to a single FFmpeg encode. Captions are burned in with libass, or written as a separate SRT.**

5. ***Mix audio: narration, music envelope built from voiced intervals, sound effects at anchors, then loudness normalization.**

6. ***Output QA and contact sheet: including a punchline strip of frames at −2, 0 and +2 around each reveal.**

***Animatic mode skips the providers in step 3 entirely.**

***Interfaces:**

- **Writes:* `timeline.json`, outputs, `overrides.builder`, `reports/builder.json`.**

- **Must not:* invent creative decisions. Without a plan, the report says "heuristic."**

***Files:**

```
***`movie-builder/`**

`├── ***SKILL.md · agents/openai.yaml`**

`├── ***references/ resolver-rules.md · camera-moves.md · card-templates.md · providers.md`**

`│               ***pricing.yaml (with verified\_on) · qa-checks.md · filmkit-spec.md (shared)`**

`├── ***assets/ fixtures/doom/ · schemas/ · templates/ · fonts/ (OFL only)`**

`└── ***scripts/ filmkit\_core.py · compile.py · assets.py · providers/\{folder,placeholder,fal,hf\}.py`**

`             ***cards.py · render.py · mix.py · qa.py · contact\_sheet.py`**
```

***Testing:**

- ***R3 tests 1–9 and 12–19 still apply.**

- ***Tests 10, 11 and 13 change because of the single-pass render: they now check that replacing an image or nudging a cut makes zero other image generations and zero LLM calls, and that the whole video re-renders correctly.**

- ***New: a render-time benchmark (frames per second of the generator at 1080p) decides whether per-shot caching is ever needed.**

***Fallbacks: no FFmpeg → stop with install instructions. No libass → separate SRT plus a warning. Provider failure or budget exceeded → placeholder. Low-confidence critical anchor → render anyway, plus a QA warning and a nudge suggestion. Missing segment → move the shot to the next anchor, or stop with an error if the shot is critical.**

***Implementation order:**

1. ***Standalone static render from images, MP3 and `shots.yaml` (B1)**

2. ***Compiler + animatic (B2)**

3. ***Camera moves and fades in the generator (B3)**

4. ***Cards, overlays and spoiler-safe captions (B4)**

5. ***Providers with cost gate (B5)**

6. ***Full QA and contact sheet (B6)**

7. ***Audio polish (B7)**

8. ***Advisory semantic QA (B8)**


## ***6. Packaging and skill-creation prep**

|  | Story Director | Narration Studio | Movie Builder |
| :-: | - | - | - |
| **SKILL.md outline** | Does/doesn't; modes; 6 core rules; full-plan workflow; revise-from-QA; handoff; fallbacks | Does/doesn't; environment check; modes; 6 rules; generated and supplied workflows; word-timing policy; handoff; fallbacks | Does/doesn't; environment check; timing-source order; 6 rules; compile→assets→render→QA; fixing one thing; fallbacks |
| **scripts/** | core + **`plan\_tools.py`** (all stdlib) | core + 7 scripts; engines optional | core + 9 scripts |
| **Dependencies** | None required | numpy, soundfile, ffmpeg; optional tiers | ffmpeg+libass, Pillow, numpy; optional tiers |
| **Setup** | None | **`pip install -r scripts/requirements-core.txt`**, plus **`-tts.txt`** / **`-align.txt`** | **`requirements-core.txt`**, plus **`-providers.txt`**; API keys from environment variables only |

***`agents/openai.yaml` (format verified for Codex; ChatGPT use unverified):**

```
***`\# story-director/agents/openai.yaml`**

***`interface:`**

`  ***display\_name: "Story Director"`**

`  ***short\_description: "Plan storyboards, shots, and image prompts"`**

`  ***default\_prompt: "Use $story-director to storyboard this story as a deadpan mockumentary."`**

***`policy:`**

`  ***allow\_implicit\_invocation: true`**

***`\# narration-studio/agents/openai.yaml`**

***`interface:`**

`  ***display\_name: "Narration Studio"`**

`  ***short\_description: "Narrate text and export precise speech timings"`**

`  ***default\_prompt: "Use $narration-studio to narrate this script and export timings."`**

***`policy:`**

`  ***allow\_implicit\_invocation: true`**

***`\# movie-builder/agents/openai.yaml`**

***`interface:`**

`  ***display\_name: "Movie Builder"`**

`  ***short\_description: "Render narrated videos from images and audio"`**

`  ***default\_prompt: "Use $movie-builder to turn these images and this MP3 into a video."`**

***`policy:`**

`  ***allow\_implicit\_invocation: true`**
```

***No `dependencies.tools` entries: only MCP is supported there, and none of these Skills need an MCP server.**

***Packaging:**

- ***Develop in one repository with `shared/` (the core file, spec, schemas and fixtures) and three Skill folders.**

- ***A build step copies `shared/` into each Skill and fails if the three copies' hashes differ.**

- ***Each Skill is zipped separately.**

- ***Not bundling the three into one Skill: separate packages keep discovery accurate (three narrow descriptions trigger better than one broad one), keep dependencies small, and let each Skill be updated on its own. I don't see a strong reason to combine them.**

***Validation before release: frontmatter lint (name format, description length), `short\_description` of 25–64 characters, fixture conformance, the Skill's unit tests, and one trigger test of 5 prompts that should fire it and 5 that shouldn't.**


## ***7. Cross-Skill test matrix**

| Test | Skills | Input | Pass criteria (measurable) |
| - | - | - | - |
| **A** Director alone | SD | DOOM text, chat only, then with Python | Storyboard covers every segment; **`plan.json`** validates; ≤ 8 unique images; display text round-trips exactly; a manual-mode run states IDs aren't stable |
| **B** Narration alone | NS | DOOM **`story.md`** without **`script.json`** | WAV + **`narration.json`** validate; every segment has **`voiced`**; the inserted deadpan silence is sample-exact; editing one line makes exactly 1 synthesis call |
| **C** Builder alone | MB | 8 images + a user MP3, no script | Playable MP4 to spec; |
| **D** All three | SD → NS → MB | DOOM story only | See below |
| **E** Mixed | SD + user MP3 + MB | Story + a human recording | Alignment finds ad-libs; the plan's deadpan expectation is compared with the measured pause; render passes C-level checks |
| **F** Version skew | All | Fixture **`plan.json`** at 1.1 with unknown fields; one file at 2.0 | 1.1 is read with fields ignored; 2.0 is rejected with a clear message; no crash |
| **G** Read-Aloud | MB (+NS) | Read-Aloud WAV + labels with 200 ms padding | Segment-start cuts within 1 frame of the measured voiced onset; heading-gap warning raised |
| **H** Degraded | All | No network, no TTS, no providers | SD full output; NS prep + "TTS unavailable" + placeholder-silence animatic; MB full placeholder animatic; every substitution reported |

***Test D detail (60–90 s excerpt, minimal manual steps: run three commands or three prompts, approve one cost estimate):**

1. ***Precise spoken-word reveal: the "Bang" shot starts within 0 to +2 frames of s013's voiced onset, and the frame at *f*0​−1 belongs to the previous shot. The "14 HOURS LATER" card starts no earlier than "fourteen."**

2. ***Deliberate pause: s013 has `pause\_after: deadpan`, giving at least 2.0 s of heard silence in the WAV (sample check). The `aftermath` shot covers ≥ 95% of it, and no caption is shown during it.**

3. ***Reused asset: `img\_classroom\_wide` appears in at least two non-adjacent shots with different camera moves, and the image is generated once (from the call log).**

4. ***The animatic renders before any image is generated, and the final render costs ≤ 0.25 USD.**

5. ***Replacing one image re-renders the video with zero other image generations.**

6. ***QA report: 0 errors.**

7. ***Subjective check: one viewer who hasn't read the story can retell the premise.**


## ***8. Implementation sequence**

1. ***Shared foundation: `filmkit-spec.md`, schemas, `filmkit\_core.py` (segmenter, hashing, resolver, chunker, labels, issues), the golden DOOM fixtures written by hand, and the copy-and-hash build step.**

2. ***Movie Builder B1–B2: standalone MP4, then the animatic from fixtures. This is the first watchable output and needs no other Skill.**

3. ***Narration Studio N1–N2: assembly from clips, then Piper/Kitten voices with the cache. Then Test B.**

4. ***Story Director M1–M3: reference docs, the plan, and the validator. Then Test A.**

5. ***Test D with placeholders. The entire timing chain is tested before any image is paid for.**

6. ***Movie Builder B3–B5: motion, cards and captions, providers. Then Test D for real, and Test C.**

7. ***Narration Studio N4–N6: supplied audio, `word\_map`, selective alignment. Then Tests E and G.**

8. ***Polish and optional features: B6–B8, Kokoro/instruct engines, revise-from-QA.**


## ***9. Decision log**

***Accepted: audio sets timing and the script sets text; anchors instead of timestamps; segment IDs that survive edits; per-segment synthesis with sample-exact assembly; timing source tags; voiced-edge default; reveals rounded up to the next frame; cards for exact text; folder → cache → provider → placeholder chain; cost dry-run gate; spoiler-safe caption breaks; contact sheet with punchline strip; separate packaging; files as the only interface.**

***Modified: prompts → `subject` plus assembly in core and Builder; card text rule plus `editorial`; the pause table (moved to the spec, `beat` 0.4, `paragraph` added); overrides sectioned; payoff hard-cut and prompt-digit rules softened to warnings; Narration's SRT now a draft; automatic re-planning → user-triggered, one pass.**

***Rejected: a fourth "shared" Skill that the others depend on (breaks standalone use); `anchors\_resolved.json`; a separate speech-intervals export; one combined Skill; even spacing as a silent fallback; per-shot render caching in v1.**

***Deferred: per-shot caching (needs a benchmark); automatic pause negotiation; flag-while-watching `review.json`; overlapping dialogue; separate 9:16 re-planning; character reference editing; music generation; semantic QA on screenshots after rendering.**

***Needs experimental verification:**

- ***Whether ChatGPT Skills read `agents/openai.yaml`, run bundled scripts, and allow network access or `pip install`.**

- ***Speed of the Python frame generator at 1080p.**

- ***The spread of "Bang" timing across sources.**

- ***Accuracy of Kokoro's word timestamps.**

- ***The aligner's license for monetized use.**

- ***Per-voice licenses.**

- ***How fal bills a 1920×1080 image (0.006 or 0.009 USD).**

- ***Whether VITS output is deterministic.**

- ***The pause-category values.**

- ***Whether chunked planning with a story bible works on long stories.**

- ***Whether the punchline heuristics agree with your own markings.**


## ***10. Remaining technical risks**

1. ***The sandbox environment. If ChatGPT's sandbox can't install packages, download voice files or reach image providers, Narration Studio and Movie Builder become "prepare here, run locally" tools inside ChatGPT. Find out first, before step 2 of the sequence.**

2. ***Image quality caps the result. Every timing feature is wasted if the generated pictures don't convey the joke. The mitigations (subjects that are easy to generate, cards for the specifics, the animatic to catch problems first) reduce this risk but don't remove it.**

3. ***Timing of short words. The most important cut, "Bang," is where model and aligner timing are weakest. The energy-onset check is the plan; it hasn't been measured.**

4. ***The core file changing across three copies. It's handled by the hash check at build time and the fixtures, but a bug in the shared segmenter would affect all three Skills at once.**

5. ***Render speed and quality of the single-pass Python generator, untested.**


## ***Final challenge: how the three Skills can evolve independently**

***They stay compatible because the files and fixtures are the contract, and the code isn't. In practice:**

1. ***Tolerant reading, conservative writing. Each Skill ignores fields it doesn't know about, works without optional fields, and writes only fields in the spec version it declares. Story Director can add a `confidence` field to beats next month, and an older Movie Builder simply ignores it.**

2. ***Strict version numbers. Additive changes are 1.x; anything else is 2.0, and older readers stop with a plain message instead of misreading data. Moving to a new major version means one Skill writes both versions for a while, and an upgrade script ships with the spec.**

3. ***Hash chains catch stale files, not version checks. If narration is regenerated, the plan stays valid (anchors point to words), and only the generated timeline and any absolute overrides are invalidated, with an explanation.**

4. ***Segment IDs are never re-derived. Because `script.json` is updated by diffing and never re-segmented, a better segmenter in a newer core can't renumber an existing project.**

5. ***Each Skill owns its engines. Narration can switch to a new TTS model, and Builder can add a provider or switch renderers, without either touching the spec. Only what they output* is fixed.**

6. ***The golden fixtures are the shared test suite. All three Skills must pass the same DOOM fixture set to release. If a change breaks another Skill's fixtures, it's a breaking change by definition, whoever intended it.**

7. ***Standalone fallbacks protect the combined workflow. If one Skill is missing, outdated or broken, the others drop to their standalone modes: a manual storyboard, a heuristic slideshow, placeholder silence. You still get a video with an honest report instead of nothing.**

***When the Skills disagree, don't make them more tightly coupled. Add a fixture that captures the disagreement, decide which Skill owns the field in question, and record the decision in the spec.**

***The next step is building, not another planning round. I'd start with step 1 of the sequence (shared spec, core file and hand-written DOOM fixtures), then Movie Builder's standalone render. I can draft the hand-written fixtures and `filmkit-spec.md` first. For the first real test, I'll need the full DOOM story text and, if you have one, a recording of the excerpt.**

***5 citations**

*![](data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCABAAEADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDqfHHje7GoTaVpU7QxwnZNMhwzt3APYDpkc5/Xz53eZi8rs7HqzsST+JokdppXkc5Z2LMfUnmkAr7bD4eFCCjFf8E+Ur15VpOUmAFOAoAp4rc5mwFKKBThUtmbY6N3hYPE7Iw6MpIIrv8AwX4yujfRaXqkzTJKdsUznLK3YE9wfzz+nn4FSxM0UqSocMjBgfcVzYnDwrwcZI0oYmdCalFlECnAUAU8V1g2aOjaHf67ctb2MQYoMu7HCoO2TUWo6dcaVqE1jchRNEQG2nI5AIwfoRXbeCneDwP4jniYpKiyMrrwQRFkHNcE7vNK0krs8jHLO7Ekn3JrjpVp1K046csdPO5tWpwp0oPrLX5FjTdOn1XUIrG1CmaUkLuOBwCTk/QGp9X0S+0O6EF9EFLDKMpyrj2NUYnkilWSF2jkU5V0Ygg+xFd/41dpvB/h6aVi0zKhZm6kmME0qtacK0I6csvvuRTpQnRnL7UdfkcABTxQKUV0nE2VRS444oFOFU2bNnqGn3Gn3vw81RdHgNmY7dhOrLkswTLc55yMjNeYAV6B4GjN54S16wgKm4mVgqE4+9HgfrXEXVnPYXclpdRmKeM4dCQccZ7exrzcGowq1ad+vz2O3GSc6VOo10t5bkAFenajcafZ+AdLj1a3N20luqwBVAKt5fBznjAwM151Z2c9/dR2trEZZ5OFQEDPGe9dx45RrTwzoVlMQJ41AZQc/dQA/rRi+WdWlC/W/nsThHKFGrUS6W8tzggKcBQBThXe2eU2VpImileNxhkYqw9CKQCvQPGfgu6N/LqmlwNNHMd0sCDLK3cgdwevrn9OEeJ4WKyIyMOqspBrHD4mFeClFnfiaE6E3GSJbK8utOuBcWdw8MoGNyHHHp7ii4uZry5e4uJGlmkOWdupqIUorXlV+a2pzObty30Jba5ms7lLi2kaKZDlXXqKlu7y61C4NxeTvNKRjc5zx6ewquBThS5VfmtqZucrct9AFSRRNJKqIMszBQPc0scTysFjRnY9Aoya7fwh4Quftseo6jEYkiO6KJxhmbsSOwH55rDEYiFGDlJmuGw1TEVFCCP/2Q== "Favicon for https://jsontools.tools/schemas/codex-skill-metadata.html")![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/openai/skills/blob/82d2c5b4/skills/.system/skill-creator/scripts/generate\_openai\_yaml.py")![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/openai/skills/blob/b0401f07/skills/.system/skill-creator/scripts/generate\_openai\_yaml.py")![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai\_yaml.md")![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/reporails/cli/blob/main/framework/rules/codex/skill-openai-yaml/rule.md")**[skills/.system/skill-creator/references/openai\_yaml.md at main · openai/skills**](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md)

***[https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai\_yaml.md**](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai\_yaml.md")](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md)**[github.com**](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md)

***[\*\*/agents/openai.yaml schema — fields and validator**](https://jsontools.tools/schemas/codex-skill-metadata.html)

***[https://jsontools.tools/schemas/codex-skill-metadata.html**](https://jsontools.tools/schemas/codex-skill-metadata.html)

*[![](data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCABAAEADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDqfHHje7GoTaVpU7QxwnZNMhwzt3APYDpkc5/Xz53eZi8rs7HqzsST+JokdppXkc5Z2LMfUnmkAr7bD4eFCCjFf8E+Ur15VpOUmAFOAoAp4rc5mwFKKBThUtmbY6N3hYPE7Iw6MpIIrv8AwX4yujfRaXqkzTJKdsUznLK3YE9wfzz+nn4FSxM0UqSocMjBgfcVzYnDwrwcZI0oYmdCalFlECnAUAU8V1g2aOjaHf67ctb2MQYoMu7HCoO2TUWo6dcaVqE1jchRNEQG2nI5AIwfoRXbeCneDwP4jniYpKiyMrrwQRFkHNcE7vNK0krs8jHLO7Ekn3JrjpVp1K046csdPO5tWpwp0oPrLX5FjTdOn1XUIrG1CmaUkLuOBwCTk/QGp9X0S+0O6EF9EFLDKMpyrj2NUYnkilWSF2jkU5V0Ygg+xFd/41dpvB/h6aVi0zKhZm6kmME0qtacK0I6csvvuRTpQnRnL7UdfkcABTxQKUV0nE2VRS444oFOFU2bNnqGn3Gn3vw81RdHgNmY7dhOrLkswTLc55yMjNeYAV6B4GjN54S16wgKm4mVgqE4+9HgfrXEXVnPYXclpdRmKeM4dCQccZ7exrzcGowq1ad+vz2O3GSc6VOo10t5bkAFenajcafZ+AdLj1a3N20luqwBVAKt5fBznjAwM151Z2c9/dR2trEZZ5OFQEDPGe9dx45RrTwzoVlMQJ41AZQc/dQA/rRi+WdWlC/W/nsThHKFGrUS6W8tzggKcBQBThXe2eU2VpImileNxhkYqw9CKQCvQPGfgu6N/LqmlwNNHMd0sCDLK3cgdwevrn9OEeJ4WKyIyMOqspBrHD4mFeClFnfiaE6E3GSJbK8utOuBcWdw8MoGNyHHHp7ii4uZry5e4uJGlmkOWdupqIUorXlV+a2pzObty30Jba5ms7lLi2kaKZDlXXqKlu7y61C4NxeTvNKRjc5zx6ewquBThS5VfmtqZucrct9AFSRRNJKqIMszBQPc0scTysFjRnY9Aoya7fwh4Quftseo6jEYkiO6KJxhmbsSOwH55rDEYiFGDlJmuGw1TEVFCCP/2Q== "Favicon for https://jsontools.tools/schemas/codex-skill-metadata.html")](https://jsontools.tools/schemas/codex-skill-metadata.html)**[jsontools.tools**](https://jsontools.tools/schemas/codex-skill-metadata.html)

***[skills/.system/skill-creator/scripts/generate\_openai\_yaml.py**](https://github.com/openai/skills/blob/b0401f07/skills/.system/skill-creator/scripts/generate_openai_yaml.py)

***[https://github.com/openai/skills/blob/b0401f07/skills/.system/skill-creator/scripts/generate\_openai\_yaml.py**](https://github.com/openai/skills/blob/b0401f07/skills/.system/skill-creator/scripts/generate_openai_yaml.py)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/openai/skills/blob/b0401f07/skills/.system/skill-creator/scripts/generate\_openai\_yaml.py")](https://github.com/openai/skills/blob/b0401f07/skills/.system/skill-creator/scripts/generate_openai_yaml.py)**[github.com**](https://github.com/openai/skills/blob/b0401f07/skills/.system/skill-creator/scripts/generate_openai_yaml.py)

***[framework/rules/codex/skill-openai-yaml/rule.md**](https://github.com/reporails/cli/blob/main/framework/rules/codex/skill-openai-yaml/rule.md)

***[https://github.com/reporails/cli/blob/main/framework/rules/codex/skill-openai-yaml/rule.md**](https://github.com/reporails/cli/blob/main/framework/rules/codex/skill-openai-yaml/rule.md)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/reporails/cli/blob/main/framework/rules/codex/skill-openai-yaml/rule.md")](https://github.com/reporails/cli/blob/main/framework/rules/codex/skill-openai-yaml/rule.md)**[github.com**](https://github.com/reporails/cli/blob/main/framework/rules/codex/skill-openai-yaml/rule.md)

***[skills/.system/skill-creator/scripts/generate\_openai\_yaml.py**](https://github.com/openai/skills/blob/82d2c5b4/skills/.system/skill-creator/scripts/generate_openai_yaml.py)

***[https://github.com/openai/skills/blob/82d2c5b4/skills/.system/skill-creator/scripts/generate\_openai\_yaml.py**](https://github.com/openai/skills/blob/82d2c5b4/skills/.system/skill-creator/scripts/generate_openai_yaml.py)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/openai/skills/blob/82d2c5b4/skills/.system/skill-creator/scripts/generate\_openai\_yaml.py")](https://github.com/openai/skills/blob/82d2c5b4/skills/.system/skill-creator/scripts/generate_openai_yaml.py)**[github.com**](https://github.com/openai/skills/blob/82d2c5b4/skills/.system/skill-creator/scripts/generate_openai_yaml.py)

*![]()**$0.7719,363 tok**

*![](data:image/png;base64,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 "Favicon for x-ai")**Grok 4.7**

***Reasoning**

***Round 4 has to freeze one contract the three skills can ship against, not blend the plans into a fourth skill. I’ll check the current skill-package format, then revise all three.**

***Searched for OpenAI ChatGPT skill SKILL.md agents/openai.yaml packaging format 2026 name description5 results**

***Reasoning**

***The three provisional plans can ship as three skills. They cannot ship until six holes are closed, and one of the proposed tests is currently impossible. Nothing below is implemented.**

## ***1. Architecture**

***Three skills, one contract, no orchestrator.**

```
***`script`**

`  │`

`  ├─ ***story-director     writes intent        plan.json`**

`  ├─ ***narration-studio   writes sound         narration.wav + narration.json`**

`  └─ ***movie-builder      writes pictures      final.mp4 + qa.json`**
```

***Nobody calls anybody else. A person, or the host, runs them in that order and passes files. A fourth skill that "makes the movie" would erase the split.**

***Each skill is useful alone:**

| Skill | Alone, it finishes when it has produced | It never produces |
| - | - | - |
| Story Director | A storyboard and a plan a human could shoot | Audio, timestamps, an MP4 |
| Narration Studio | A WAV and measured timing, or an alignment of a recording the user already has | Shots, images, video |
| Movie Builder | An MP4 from images plus a timing file | A storyboard, speech, a guessed word time |

***Together they are a pipeline only because they read and write `film-contract/1`. That contract is a vendored document, not a library and not a skill. Each skill carries a copy. If the copy's version does not match, the skill stops.**

***Seconds appear in one place: Movie Builder's disposable `timeline.json`, computed from sample indexes. They are never written back into the plan.**

## ***What the review found**

***The later rounds were right, and the earlier plans were not yet renderable.**

***Holes. A missing word time had no safe failure, so a compiler could spoil a joke by using the sentence start. Silences could not be joined to reactions. Coverage of the head and tail of a file was implied. The director never listed which words had to be measured. Card layout had a name and no owner. AAC delay was being treated as if sample indexes survived the mux.**

***Conflicts. The director wanted millisecond pause ranges; Narration Studio has to own the only pause table. Both sides were growing a caption format. `800` lived in two skills. Segment ids and clip ids were one idea wearing two names. Test C, as written, asks Movie Builder to synchronize an MP3 with no timing file and no aligner. It cannot.**

***Duplicates worth deleting. A comedy-directive language. A second caption spec. A shared Python package. An aligner inside Movie Builder. A TTS engine anywhere but Narration Studio. Semantic QA.**

***Keep from the later rounds. Sample indexes, `covers`, conditional reactions, hold-previous, `timing\_requests`, `unresolved\_anchors`, provider probes, and the refusal to divide a sentence by word count.**

***Since no skill has been packaged, "migration" means: throw away the `/0` field names. There are no files to convert.**

## ***2. Shared contract**

***`film-contract/1`. Copied into each skill as `references/shared-contract.md`. Unknown fields are ignored. A missing required field is fatal. A skill that understands only this version refuses a later major version rather than guessing.**

***Script identity. SHA-256 of the UTF-8 text the user asked to have spoken. Newlines become `\\n`. One leading BOM may be removed. Nothing else is normalized: not spaces, not quotes, not punctuation. All three skills use that hash. A mismatch is a warning, not a silent retimes.**

***Segments. `seg\_` plus a zero-padded number. They are spans of the author's text, not audio files. Whoever creates the canonical index first owns the ids. If a plan is present, its ids are canonical and Narration Studio must not renumber them. If only Narration Studio has run, its ids are canonical and a later director pass must adopt them when the hash matches. Movie Builder never mints segment ids.**

***Anchor. The only required form is:**

```
***`\{"segment": "seg\_03", "text": "fourteen", "nth": 1\}`**
```

***Match the verbatim substring and occurrence. Character offsets are optional and legal only if a script computed them. If they disagree with the substring, the substring wins and the offset is ignored. Model-counted offsets are not an anchor.**

***Pause names. `sentence`, `paragraph`, `beat`, `long`. The director may request a size. It may not request a duration. Narration Studio owns the millisecond table, and that table is not part of this contract because the other two skills must not depend on it. Movie Builder never reads a requested duration. It reads measured samples.**

***Editorial threshold. A reaction may carry `if\_silence\_ms\_at\_least`. If the field is absent, the value is `800`. That number lives in this contract so the two skills cannot drift. It is a starting value, not a measured result.**

***Other frozen enums. Shot reason: `hold`, `new\_subject`, `reveal`, `reaction`, `time\_card`, `end\_card`. Camera: `static`, `slow\_zoom\_in`, `slow\_zoom\_out`, `pan\_left`, `pan\_right`. Transition: `hard\_cut`, `fade`. A fade on a shot with `not\_before` is illegal. Card template: `stat`, `title`, `comment`. Asset kind: `generate`, `card`, `file`.**

***Captions. Burned captions belong to Movie Builder. Their source is the author's text, never the pronunciation string. Any caption chunk that contains a `not\_before` word waits for that word. The director does not emit a parallel hide-list. Narration Studio may write a convenience SRT marked `caption\_safety: none`. Movie Builder must not burn that file when the plan contains a `not\_before`.**

***Warnings. One object, any skill may emit it:**

```
***`\{"code": "reveal\_unresolved", "severity": "error", "skill": "movie-builder", "anchor": \{"segment": "seg\_03", "text": "fourteen", "nth": 1\}\}`**
```

***Closed codes for v1: `reveal\_unresolved`, `script\_mismatch`, `hash\_mismatch`, `pause\_not\_honored`, `pause\_on\_reveal\_ignored`, `word\_timing\_absent`, `asset\_missing`, `provider\_fallback`, `plan\_partial`, `unsynced\_slideshow`, `mux\_delay\_unmeasured`. An error is not automatically a crash. The fatal set is narrower and lives in each skill.**

***Caches. Not shared. Narration Studio caches clips. Movie Builder caches images. Neither reads the other's cache directory. The assembled WAV and the PNG files are the handoff.**

***The integrated shape, for one joke:**

```
***`\{`**

`  ***"contract": "film-contract/1",`**

`  ***"plan": \{`**

`    ***"plan\_version": "story-director-plan/1",`**

`    ***"script\_sha256": "\<hash\>",`**

`    ***"coverage": \{"from": "seg\_03", "to": "seg\_03", "complete": false\},`**

`    ***"gap\_policy": "extend\_previous",`**

`    ***"timing\_requests": \[`**

`      ***\{"kind": "word", "anchor": \{"segment": "seg\_03", "text": "fourteen", "nth": 1\}\},`**

`      ***\{"kind": "pause", "anchor": \{"segment": "seg\_03", "text": "hours.", "nth": 1\}, "size": "beat"\}`**

`    ***\],`**

`    ***"shots": \[`**

`      ***\{`**

`        ***"id": "sh\_11",`**

`        ***"reason": "reveal",`**

`        ***"asset": "card\_14h",`**

`        ***"in": \{"segment": "seg\_03", "text": "fourteen", "nth": 1, "at": "start"\},`**

`        ***"not\_before": \{"segment": "seg\_03", "text": "fourteen", "nth": 1\},`**

`        ***"transition": "hard\_cut"`**

`      ***\}`**

`    ***\]`**

`  ***\},`**

`  ***"narration": \{`**

`    ***"narration\_version": "narration-studio/1",`**

`    ***"audio": \{"file": "narration.wav", "sample\_rate": 24000\},`**

`    ***"ready\_for\_word\_reveals": true,`**

`    ***"words": \[`**

`      ***\{"anchor": \{"segment": "seg\_03", "text": "fourteen", "nth": 1\}, "sample\_start": 465600, "method": "forced\_align"\}`**

`    ***\],`**

`    ***"unresolved\_anchors": \[\]`**

`  ***\}`**

***`\}`**
```

***Movie Builder joins those two files. It does not ask the user where to cut.**

## ***3. Changes that matter**

| Change | Skills | Why | Breaks **`/0`**? |
| - | - | - | - |
| Add **`timing\_requests`**, **`coverage`**, **`gap\_policy`** | Director, read by the other two | The renderer can no longer guess what must be measured or what fills a gap | Yes. Nothing was shipped |
| Delete caption hide-lists and millisecond ranges | Director | Two specs for one rule will diverge | Yes |
| Add **`pronunciation: literal`** | Director, read by Narration | A lexicon must not rename an anchor | Additive |
| Pause size enum only | Director writes, Narration interprets | One table of milliseconds | Yes |
| **`unresolved\_anchors`**, **`ready\_for\_word\_reveals`**, required **`after\_anchor`** | Narration, read by Movie Builder | A miss becomes a hold instead of an early card | Yes |
| Hold-previous is the only legal reveal fallback | Movie Builder | Sentence-start fallback spoils the joke | New rule |
| Convenience SRT is not burnable when a reveal exists | Narration, Movie Builder | Spoiler suppression has one owner | New rule |
| Resolve against the measured WAV, then encode | Movie Builder | Sample indexes die if anyone resamples first | Clarification |
| Test C requires an SRT or cue file | Movie Builder | An MP3 alone is not a timing source | Corrects the brief |
| No shared code package | All | Independent release | Prevents a coupling |

***Vendoring the contract text, and an identical anchor-match function of a few dozen lines inside the two code skills, is allowed. Importing another skill is not.**

## ***4. The three plans**

### ***Story Director — Final Plan v1**

***Purpose. Turn a written story into a storyboard and a shot plan. Standalone, that plan is for a person. Cooperatively, it is for the other two skills. It does not speak, measure, or render.**

***Trigger. Name: `story-director`.**

***Plan visuals for a written story: beats, a storyboard, a shot list, image prompts, title cards, and narration notes. Use for fiction, comedy, explainers, and documentaries. Anchor shots to the author's words. Do not invent timestamps. Do not use for text-to-speech, audio alignment, image-API calls, FFmpeg, caption burning, or exporting an MP4.***

***Discovery is the description. In ChatGPT the user can also invoke it with `@`. The body is not a trigger. `allow\_implicit\_invocation` stays on. The description must not say "and then render the movie."**

***Inputs. Required: the story. Optional: style, image budget, an excerpt range, locked shots, an existing plan, a script index whose hash matches. Audio is ignored except for the sentence "I will not time this."**

***Outputs. A readable storyboard, then `plan.json` at `story-director-plan/1`. No WAV, no MP4, no seconds.**

***Tools. None required. `index\_script.py` and `validate\_plan.py` are optional. If they cannot run, anchors are still substrings, and the plan says they were not machine-checked. The model does not invent offsets.**

***Workflow.**

1. ***Copy the author's words. Segment on the author's breaks. Identify speakers only where the text marks them.**

2. ***Mark payoffs before pictures. Each payoff gets a `not\_before` anchor and a `timing\_requests` entry of kind `word`.**

3. ***Holds are the default. A new sentence is not a cut.**

4. ***Request air with a pause size, never a duration. Do not request a pause that splits a reveal word.**

5. ***Exact numbers, titles, and quoted comments are cards. Atmosphere is a prompt. Prompts do not contain the payoff string.**

6. ***Reuse an asset id before spending a new image. Default budget, if unset: `max(6, round(words / 100))`, cap 24, cards free. State the assumption.**

7. ***Set `coverage` and `gap\_policy`. Validate. One repair. Then emit the storyboard, then the JSON.**

***Cooperation. It writes the plan and stops. It does not check whether the other skills exist. Delivery notes are notes; a later skill may ignore them. A missing word time is Movie Builder's hold, not a reason to run this skill again.**

***Files. `SKILL.md`, `agents/openai.yaml`, `references/schema.md`, `references/beat-rules.md`, `references/visual-modes.md`, `references/validators.md`, `references/shared-contract.md`, `assets/storyboard-template.md`, optional scripts. Modes are `chalkboard`, `documentary`, and `illustrated` only. No icons unless you supply them.**

***Tests. The DOOM sentence has a card, a `not\_before`, a conditional reaction, and no time fields. A 90-second excerpt quotes the author instead of rewriting him. "Add timestamps," "render it," and "make the jokes funnier" do not produce those artifacts. A locked shot survives a second pass.**

***Fallbacks. No story: ask. Story longer than context: direct an explicit excerpt and say what was not read. Ambiguous anchor: do not guess a reveal. Unchecked index: say so.**

***Build order. Write the contract copy and the body first. This skill can be packaged before any audio engine exists.**

### ***Narration Studio — Final Plan v1**

***Purpose. Create narration, or measure a recording the user already made. Sentence times and word times are different products. A clip boundary is not the start of a word inside that clip.**

***Trigger. Name: `narration-studio`.**

***Create or measure narration. Use to read a script aloud, assign voices, insert pauses, regenerate one sentence, or align a user-supplied MP3 or WAV to a script. Use for audiobook, narration, dialogue, and explainer reads. Export sentence timing always and word timing only when measured. Do not use for storyboarding, shot plans, image prompts, FFmpeg, or exporting an MP4.***

***Inputs. A script, or a director plan plus the same script. Optional: a voice map, a lexicon, a WAV or MP3 to align, a list of words that need times. If the plan has `timing\_requests`, that list is the request.**

***Outputs. `narration.wav`, `narration.json` at `narration-studio/1`, cached clips, optional sentence-level SRT marked unsafe for reveals. Audacity labels are a human export, not the contract.**

***Tools. Required for a generated WAV: Python and one local engine already installed, Kokoro first, Piper second. Required for a supplied recording: Python and a forced aligner. Hosted TTS is optional, after a stated cap. ffmpeg is not required. Weights are not bundled. If none of those tools exist and no recording was supplied, the skill writes a voice sheet and stops. It does not describe a file it did not create.**

***Workflow.**

1. ***Adopt the plan's segment ids when a plan is present. Otherwise mint them.**

2. ***Copy `script\_text`. Apply the lexicon only to `spoken\_text`, unless the span says `literal`.**

3. ***Synthesize one clip per utterance. Cache key is engine, model, voice, speed, sample rate, and the exact spoken string. Pauses are not in the key.**

4. ***Insert silence as samples. `beat` and `long` come from this skill's own table. A requested range from an old plan is ignored.**

5. ***Write the sidecar from the running sample count at concat time.**

6. ***Word-time a clip only if a reveal or a caption request needs it. Prefer a native token map only where the tokens match the script words one for one. Otherwise forced-align that clip. If neither is possible, leave the word out and list it in `unresolved\_anchors`.**

7. ***Set `ready\_for\_word\_reveals` true only when every requested reveal anchor has a word span.**

***Cooperation. It reads `timing\_requests`, speaker, `do\_not\_rewrite`, and `pronunciation`. It does not read cameras, prompts, or shots. It does not insert silence into a user's recording. A requested beat the speaker did not leave is `pause\_not\_honored`, not an edit. Measured silences still get ids and `after\_anchor`, with `intentional` null. Movie Builder decides whether they are long enough.**

***Files. `SKILL.md`, `agents/openai.yaml`, `references/schema.md`, `references/engines.md`, `references/pause-rules.md`, `references/alignment.md`, `references/shared-contract.md`, `scripts/synthesize.py`, `scripts/assemble.py`, `scripts/align\_script.py`, `scripts/validate\_narration.py`, `assets/lexicon.example.json`. The pause table is unverified and stays in `pause-rules.md`, not in the contract. If a sentence splitter is copied from Read-Aloud-Main, keep the MIT notice. Do not copy that app.**

***Tests. Editing one sentence resynthesizes one clip. Changing a pause resynthesizes none. A decimal survives the splitter. The `fourteen` span starts after its clip starts. A token map that cannot find `0.000002` aligns or reports the word missing. A mismatched recording produces a diff and no reveal times. A user WAV contains no inserted beat.**

***Fallbacks. No engine: stop. Aligner missing: sentence times if this skill built the clips, word status absent, no interpolation. Same anchor twice and `nth` still ambiguous: do not attach a time. Supplied audio is the performance, including its bad pauses.**

***Build order. Assembly of three already-made WAVs first. Then one local voice and the cache. Alignment and the reveal test after that. A hosted engine last.**

### ***Movie Builder — Final Plan v1**

***Purpose. Turn pictures and audio into an MP4. Standalone, the user supplies the cuts, via an SRT or a cue list. Cooperatively, a complete plan plus a sidecar means the user assigns nothing.**

***Trigger. Name: `movie-builder`.**

***Assemble a narrated MP4 from images and audio. Use to render a slideshow or explainer, apply a shot plan, burn captions, draw title cards, add slow zooms and fades, and write a contact sheet and QA report. Use when pictures and a recording are available, or a director plan plus a narration sidecar. Do not use for storyboarding, rewriting, text-to-speech, or speech alignment. Do not invent word timestamps. Do not treat one sentence as one shot unless the user asked for a plain slideshow.***

***Inputs. Required: audio, and at least one image or a card request. Timing comes from a sidecar, an SRT, or a user cue list, in that order. A plan is optional. An MP3 alone is not a timing source.**

***Outputs. `final.mp4`, `timeline.json` at `movie-builder/1`, `qa.json`, a contact sheet. Timeline seconds are disposable.**

***Tools. Required: ffmpeg on the PATH, and Python. Pillow for cards, using a font already on the machine. Image providers are optional. This skill does not contain an aligner. If ffmpeg is missing, it stops and does not describe an MP4.**

***Workflow.**

1. ***Refuse to resolve against an MP3 when a measured WAV exists. Resolve, then encode. Do not resample the authority WAV first.**

2. ***Join word anchors on segment, text, and `nth`.**

3. ***A reveal with no word time extends the previous shot. It never moves to the sentence start. `anchor\_status` records `word`, `sentence\_fallback`, `user\_time`, or `slideshow`. A reveal cannot be `sentence\_fallback`.**

4. ***Join a reaction to a silence with the same `after\_anchor`. Use it only if it is long enough. Otherwise extend the previous shot.**

5. ***`gap\_policy` fills the head, the tail, and every other hole by extending a neighbor. Black is a bug. A partial plan is not stretched over audio it does not cover.**

6. ***Draw cards in code. Generate an image only under the cap, and only if a probe shows that a route actually answers. A model you can download is not a hosted endpoint. One retry, then a card.**

7. ***Burn ASS captions from the author's words, breaking at `not\_before`. Ignore the narration SRT when any `not\_before` exists.**

8. ***Concat silent shot clips, mux AAC, set the length from the audio. Do not use `-shortest`.**

***Renderer. One preset: 1920×1080, 30 fps, H.264, AAC, yuv420p. Camera recipes live in one reference file. A zoom shorter than one second becomes static. Fades on reveals become hard cuts. No music, no sound effects, no user-supplied filtergraphs. `zoompan` is a candidate, not a fact. If the fixture jumps, replace it with a crop expression and delete the loser from the skill.**

***Cooperation. It needs `timing\_requests` honored or listed as unresolved, `after\_anchor` on silences, `coverage`, and `gap\_policy`. It does not need a second director pass. A hash mismatch means: play the sidecar's audio, warn, do not retimes against the plan's prose. Locked overrides store an asset id and an anchor, not a timestamp.**

***Files. `SKILL.md`, `agents/openai.yaml`, `references/resolve.md`, `references/cameras.md`, `references/cards.md`, `references/providers.md`, `references/shared-contract.md`, `scripts/resolve\_timeline.py`, `scripts/render\_cards.py`, `scripts/render\_video.py`, `scripts/qa\_video.py`. No bundled weights, no bundled ffmpeg.**

***Tests. See the matrix. The contract test compares the timeline with the sample index, within one sample. The MP4-frame test is separate and is not a pass condition until mux delay has been measured.**

***Fallbacks. No timing file and no confirmed slideshow: stop. Even split only after the user asks, and QA says `unsynced\_slideshow`. Missing image: a card that says `MISSING`. Provider down or over cap: a card, and the movie still exports. Unresolved reveal: hold, export, name the anchor.**

***Build order. Three stills and an SRT first, so a playable file exists before the contract is wired. The resolver against a golden sidecar second. Cards, then one capped image call.**

### ***UI metadata**

***Omit icons. `dependencies.tools` is for MCP servers only, so ffmpeg and Python are not declared there. They are setup requirements in each `SKILL.md`.**

| Skill | **`display\_name`** | **`short\_description`** | **`default\_prompt`** |
| - | - | - | - |
| **`story-director`** | Story Director | Plan shots from a written story | Use $story-director to storyboard this script without rewriting the spoken lines. |
| **`narration-studio`** | Narration Studio | Read a script or align a recording | Use $narration-studio to read this script and write timing metadata. |
| **`movie-builder`** | Movie Builder | Render a narrated MP4 from stills | Use $movie-builder to render an MP4 from these images and this audio. |

***Short descriptions are inside the 25–64 character UI limit. Quote every string in the YAML.**

***Packaging. Three zip files, one skill each. No weights, no binaries, no cache, no sample media. Do not ship a combined skill. A fixture folder may live outside the zips so the golden files can be copied; it is not installed as a skill.**

## ***5. Test matrix**

| Test | Installed | Given | Pass | Fail |
| - | - | - | - | - |
| A. Director alone | Director only | The DOOM excerpt | Storyboard plus a plan: no seconds, payoff is a card, reaction is conditional, **`timing\_requests`** lists **`fourteen`** | A rewritten joke, a timestamp, an MP4 |
| B. Narration alone | Narration only | The excerpt, one local voice | WAV whose sample count matches the sidecar; **`fourteen`** starts after the clip start; one edited sentence rebuilds one clip | Interpolated words, a pause acted by the voice |
| C. Builder alone | Builder only | Images, an MP3, and an SRT | Playable 1080p MP4, cuts on the cues, duration within a frame, contact sheet | A word-timed reveal, or an even split the user did not request |
| D. All three | All three, invoked in order | The excerpt | No human shot list. Card at or after the measured word on the timeline. One inserted beat used only if it was measured long enough. One image file used by two shots. Replacing that file does not call a provider | A sentence-start card, a new director pass after the read, black between shots |

***Test C was changed on purpose. Images plus an MP3, with no SRT and no sidecar, are a slideshow, and only after the user says so. Calling that synchronized would require this skill to grow an aligner.**

***Test D is three explicit invocations and a folder. The handoff is files. "Minimal manual intervention" means the user does not assign shots. It does not mean the skills discover and call each other. Generation is optional in this test: cards plus one reused still are enough. A provider call is a separate, capped adapter test.**

***Two checks stay out of the pass line until someone measures them. The first is the frame inside the MP4 against the WAV index, because AAC priming is real and unmeasured here. The second is any native Kokoro token map. Forced alignment is the path that the test may require. A native map is accepted only after it hits `fourteen`, `Bang`, and `0.000002` on a fixture.**

## ***6. Implementation sequence**

1. ***Write `film-contract/1` and three golden fixtures: a plan, a sidecar, and the timeline those two must produce. No skill yet.**

2. ***Package Movie Builder far enough to pass Test C. That is the first playable file, and it does not wait on the other two.**

3. ***Package Story Director and pass Test A. Instruction-only is acceptable.**

4. ***Package Narration Studio through assembly and one local voice. Pass the clip-boundary half of Test B.**

5. ***Add alignment. Pass the `fourteen` half of Test B.**

6. ***Point Movie Builder at the golden sidecar. The reveal fallback and the silence join are the whole of this step.**

7. ***Run Test D by hand, in three invocations. Do not build a wrapper that hides a failure.**

***Stop at 2 if ffmpeg is not available in the target host. Stop at 4 if no TTS engine is installed. Say so. Do not paper over either gap with a described file.**

## ***7. Decision log**

***Accepted. Three skills, no orchestrator. Audio measured by Narration Studio is the timing authority after it exists. Anchors are substring plus `nth`. Holds default. Cards carry exact text. FFmpeg is the only renderer. Caches are per skill. A missing reveal holds the previous picture. Supplied recordings are not remixed. Two voice ids, not acted emotion. Provider probe before any image call, then a card.**

***Modified. Test C now requires an SRT. Pause requests are names, not ranges. Caption spoiler rules live only on `not\_before`. The 800 ms default lives in the contract. Segment ids have an owner. The MP4-frame reveal check is no longer a v1 gate. Image generation is optional for the integrated test.**

***Rejected. A fourth orchestrator skill. A shared code package. A comedy DSL. Semantic QA as a gate. One image per sentence. Audacity labels or MP3 bytes as the contract. Director-invented timestamps. Movie Builder growing an aligner. Copying Read-Aloud's browser app. Free-GPU assumptions. Writing seconds back into the plan.**

***Deferred. Music, sound effects, a GUI, character-reference conditioning, instruction-following TTS, a 48 kHz deliverable, a second director pass, and any one-click "make the video" router.**

***Not yet verified. Kokoro token timestamps. Whether `zoompan` holds a push for a whole shot. AAC priming against a 150 ms window. The pause table. Whether a given hosted route for FLUX.1 schnell answers a probe on the day someone runs it. Downloadable weights are not evidence that it will. ChatGPT's skill format, including `@` invocation and `agents/openai.yaml`, matches the current docs. It has not been exercised with these three folders.**

## ***8. Risks still open**

1. ***A broad prompt can select the wrong skill, or more than one. Exclusive descriptions reduce that. They do not remove it. The full pipeline is three explicit invocations until a host router exists, and that router is not one of these skills.**

2. ***A later "helpful" fallback that snaps a missing word to the clip start will pass every file-integrity check and spoil the joke. The golden fixture is the protection. Keep it brutal.**

3. ***Hash drift. If one skill trims a newline and another does not, every anchor looks unmatched. The normalization rule is the whole fix, and it has to be copied verbatim.**

4. ***The two unmeasured clocks, token maps and AAC delay, will be mistaken for contract bugs. Keep them off the pass line.**

5. ***Two of the three skills do nothing useful in a host that cannot run Python or ffmpeg. That is a host limit, not a reason to invent the artifact in prose.**

## ***How they evolve without breaking the workflow**

***They break the workflow only if they share code, or if they change the meaning of a field the others already read.**

***`film-contract/1` is the only coupling. Each skill has its own artifact version and its own release. A narration release that improves caching can ship alone, provided the golden sidecar still validates. A renderer release can change the zoom recipe without a director release, because the director never knew the recipe. A director release can add an optional field. Old readers ignore it.**

***A breaking change is a new contract version, not a quiet edit. Readers of `/1` refuse `/2` rather than improvising. Additive fields do not bump the major version. Removed or redefined fields do. Keep a removed field optional for one version before deleting it.**

***Do not widen a description into another skill's job. The moment Story Director's trigger says "render," the host will stop treating them as separate, and the contract will stop being the seam. New capability goes in the skill that already owns the artifact: words in the director, samples in narration, frames in the builder.**

***The practical test of independence is small. After any one skill changes, its own tests pass, and the unchanged golden fixture still produces the same timeline. If it does, the other two do not need a release. If it does not, the change was a contract change and should have been versioned as one.**

***5 citations**

*![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md")![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai\_yaml.md")![](data:image/png;base64,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 "Favicon for https://developers.openai.com/api/docs/guides/tools-skills")![](data:image/png;base64,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 "Favicon for https://developers.openai.com/codex/skills")![](data:image/png;base64,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 "Favicon for https://learn.chatgpt.com/docs/build-skills")**[Agent Skills – Codex | OpenAI Developers**](https://developers.openai.com/codex/skills)

***[https://developers.openai.com/codex/skills**](https://developers.openai.com/codex/skills)

*[![](data:image/png;base64,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 "Favicon for https://developers.openai.com/codex/skills")](https://developers.openai.com/codex/skills)**[developers.openai.com**](https://developers.openai.com/codex/skills)

***[skills/.system/skill-creator/SKILL.md at main · openai/skills**](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)

***[https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md**](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md")](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)**[github.com**](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)

***[skills/.system/skill-creator/references/openai\_yaml.md at main · openai/skills**](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md)

***[https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai\_yaml.md**](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai\_yaml.md")](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md)**[github.com**](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md)

***[Build skills | ChatGPT Learn**](https://learn.chatgpt.com/docs/build-skills)

***[https://learn.chatgpt.com/docs/build-skills**](https://learn.chatgpt.com/docs/build-skills)

*[![](data:image/png;base64,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 "Favicon for https://learn.chatgpt.com/docs/build-skills")](https://learn.chatgpt.com/docs/build-skills)**[learn.chatgpt.com**](https://learn.chatgpt.com/docs/build-skills)

***[Skills | OpenAI API**](https://developers.openai.com/api/docs/guides/tools-skills)

***[https://developers.openai.com/api/docs/guides/tools-skills**](https://developers.openai.com/api/docs/guides/tools-skills)

*[![](data:image/png;base64,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 "Favicon for https://developers.openai.com/api/docs/guides/tools-skills")](https://developers.openai.com/api/docs/guides/tools-skills)**[developers.openai.com**](https://developers.openai.com/api/docs/guides/tools-skills)

*![]()**$0.1514,919 tok**

*![](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNzkuNSIgaGVpZ2h0PSIyNzkuNSIgcHJlc2VydmVBc3BlY3RSYXRpbz0ieE1pZFlNaWQiIHZpZXdCb3g9Ii0xMS43NSAtOS43NSAyNzkuNSAyNzkuNSI+PHBhdGggIGQ9Ik0yMzkuMTg0IDEwNi4yMDNhNjQuNzE2IDY0LjcxNiAwIDAgMC01LjU3Ni01My4xMDNDMjE5LjQ1MiAyOC40NTkgMTkxIDE1Ljc4NCAxNjMuMjEzIDIxLjc0QTY1LjU4NiA2NS41ODYgMCAwIDAgNTIuMDk2IDQ1LjIyYTY0LjcxNiA2NC43MTYgMCAwIDAtNDMuMjMgMzEuMzZjLTE0LjMxIDI0LjYwMi0xMS4wNjEgNTUuNjM0IDguMDMzIDc2Ljc0YTY0LjY2NSA2NC42NjUgMCAwIDAgNS41MjUgNTMuMTAyYzE0LjE3NCAyNC42NSA0Mi42NDQgMzcuMzI0IDcwLjQ0NiAzMS4zNmE2NC43MiA2NC43MiAwIDAgMCA0OC43NTQgMjEuNzQ0YzI4LjQ4MS4wMjUgNTMuNzE0LTE4LjM2MSA2Mi40MTQtNDUuNDgxYTY0Ljc2NyA2NC43NjcgMCAwIDAgNDMuMjI5LTMxLjM2YzE0LjEzNy0yNC41NTggMTAuODc1LTU1LjQyMy04LjA4My03Ni40ODNabS05Ny41NiAxMzYuMzM4YTQ4LjM5NyA0OC4zOTcgMCAwIDEtMzEuMTA1LTExLjI1NWwxLjUzNS0uODcgNTEuNjctMjkuODI1YTguNTk1IDguNTk1IDAgMCAwIDQuMjQ3LTcuMzY3di03Mi44NWwyMS44NDUgMTIuNjM2Yy4yMTguMTExLjM3LjMyLjQwOS41NjN2NjAuMzY3Yy0uMDU2IDI2LjgxOC0yMS43ODMgNDguNTQ1LTQ4LjYwMSA0OC42MDFabS0xMDQuNDY2LTQ0LjYxYTQ4LjM0NSA0OC4zNDUgMCAwIDEtNS43ODEtMzIuNTg5bDEuNTM0LjkyMSA1MS43MjIgMjkuODI2YTguMzM5IDguMzM5IDAgMCAwIDguNDQxIDBsNjMuMTgxLTM2LjQyNXYyNS4yMjFhLjg3Ljg3IDAgMCAxLS4zNTguNjY1bC01Mi4zMzUgMzAuMTg0Yy0yMy4yNTcgMTMuMzk4LTUyLjk3IDUuNDMxLTY2LjQwNC0xNy44MDNaTTIzLjU0OSA4NS4zOGE0OC40OTkgNDguNDk5IDAgMCAxIDI1LjU4LTIxLjMzM3Y2MS4zOWE4LjI4OCA4LjI4OCAwIDAgMCA0LjE5NSA3LjMxNmw2Mi44NzQgMzYuMjcyLTIxLjg0NSAxMi42MzZhLjgxOS44MTkgMCAwIDEtLjc2NyAwTDQxLjM1MyAxNTEuNTNjLTIzLjIxMS0xMy40NTQtMzEuMTcxLTQzLjE0NC0xNy44MDQtNjYuNDA1di4yNTZabTE3OS40NjYgNDEuNjk1LTYzLjA4LTM2LjYzTDE2MS43MyA3Ny44NmEuODE5LjgxOSAwIDAgMSAuNzY4IDBsNTIuMjMzIDMwLjE4NGE0OC42IDQ4LjYgMCAwIDEtNy4zMTYgODcuNjM1di02MS4zOTFhOC41NDQgOC41NDQgMCAwIDAtNC40LTcuMjEzWm0yMS43NDItMzIuNjktMS41MzUtLjkyMi01MS42MTktMzAuMDgxYTguMzkgOC4zOSAwIDAgMC04LjQ5MiAwTDk5Ljk4IDk5LjgwOFY3NC41ODdhLjcxNi43MTYgMCAwIDEgLjMwNy0uNjY1bDUyLjIzMy0zMC4xMzNhNDguNjUyIDQ4LjY1MiAwIDAgMSA3Mi4yMzYgNTAuMzkxdi4yMDVaTTg4LjA2MSAxMzkuMDk3bC0yMS44NDUtMTIuNTg1YS44Ny44NyAwIDAgMS0uNDEtLjYxNFY2NS42ODVhNDguNjUyIDQ4LjY1MiAwIDAgMSA3OS43NTctMzcuMzQ2bC0xLjUzNS44Ny01MS42NyAyOS44MjVhOC41OTUgOC41OTUgMCAwIDAtNC4yNDYgNy4zNjdsLS4wNTEgNzIuNjk3Wm0xMS44NjgtMjUuNTggMjguMTM4LTE2LjIxNyAyOC4xODggMTYuMjE4djMyLjQzNGwtMjguMDg2IDE2LjIxOC0yOC4xODgtMTYuMjE4LS4wNTItMzIuNDM0WiIvPjwvc3ZnPgo= "Favicon for openai")**GPT Sol Latest**

***Searched for site.github.com/openai/skills skill-creator references openai\_yaml.md agents/openai.yaml interface default\_prompt allow\_implicit\_invocation5 results**

# ***Final Architecture and Revised Skill Plans — v1**

***Status: planning complete; implementation not started. “Final Plan v1” means an agreed implementation target—not validated software.**

***The three-Skill division is sound. The revisions below address the main weaknesses: ambiguous timing boundaries, duplicate alignment responsibilities, incomplete source-to-spoken mappings, and assumptions about Skill execution.**

## ***1. Unified architecture**

### ***The governing design**

***Standalone first, cooperative through files—not through mandatory Skill-to-Skill invocation.**

| Skill | Owns | Does not own |
| - | - | - |
| **Story Director** | Narrative interpretation, visual beats, performance intent, reveal constraints | Audio measurement, synthesis, rendering |
| **Narration Studio** | Speech generation, audio assembly, transcription/alignment, measured timing | Visual direction, video rendering |
| **Movie Builder** | Asset realization, timing compilation, visual composition, rendering, video QA | Authoritative script rewriting or invented speech timestamps |

***Together:**

```
`                         ┌───────────────────┐`

***`Story ──────────────────►│  Story Director   │`**

`                         └─────────┬─────────┘`

`                                   │ ***creative plan`**

`                                   ▼`

`                         ┌───────────────────┐`

***`Story / supplied audio ─►│ Narration Studio  │`**

`                         └─────────┬─────────┘`

`                                   │ ***audio + timing`**

`                                   ▼`

`                         ┌───────────────────┐`

***`Images / video assets ──►│   Movie Builder   │`**

`                         └─────────┬─────────┘`

`                                   ▼`

`                          ***MP4 + review outputs`**
```

***This illustrates cooperation, not a mandatory production order. Supplied-audio timing can precede direction. Each Skill can also receive its inputs directly.**

### ***The important simplification**

***Separate only three kinds of production data:**

1. ***Creative intent: what should happen.**

2. ***Measured media information: what actually exists.**

3. ***Resolved execution: what will be rendered.**

***Do not build a project database, general editing graph, agent coordinator, or automatic repair loop.**


## ***2. Review findings and resolutions**

| Finding | Resolution |
| - | - |
| “Segment” sometimes means script, synthesis unit, or clip | Use separate identities and explicit relationships |
| “Segment end” ambiguously means clip end or speech end | Require an explicit boundary kind |
| Movie Builder needs standalone alignment, but Narration Studio owns alignment | Both may call the same optional timing library; neither requires the other Skill |
| Source-to-spoken mappings were required but unspecified | Define span mappings, including substitutions and expansions |
| Requested pauses could be mistaken for existing silence | Separate requests, inserted pauses, and detected silence |
| Asset prompts and actual files were mixed | Separate logical asset specifications from realizations |
| Reveal protection was descriptive rather than executable | Define required earliest-visible constraints |
| Caption ownership overlapped | Narration supplies text/timing; Director supplies protection; Builder controls presentation |
| Clip caching implied unconditional one-sentence regeneration | Context-sensitive engines may require regeneration of adjacent units |
| Equal-duration slideshows could be mislabeled synchronized | Explicitly distinguish pacing-based output from speech-synchronized output |
| Skill metadata implied universal ChatGPT support | Target the requested Skill package format; verify host support before deployment |
| Each plan proposed similar validation utilities | Share small deterministic utilities, not duplicated engines |

### ***Shared code without a fourth Skill**

***Use a small proposed Python utility package, provisionally `story\_video\_common`, for:**

- ***Contract validation.**

- ***Source-reference handling.**

- ***Time-coordinate conversion.**

- ***File integrity checks.**

- ***Optional reusable timing integration.**

***Each Skill installs only the functionality it needs. There is no dependency on another Skill package.**

***TTS and rendering implementations remain separate. Shared alignment support wraps an established library rather than duplicating it.**

***If this common package complicates the first prototype, begin with the contract and test fixtures; extract genuinely repeated utilities afterward. Do not build infrastructure in anticipation of duplication.**


## ***3. Shared interoperability specification — version 1.0**

### ***3.1 Files and common envelope**

***The cooperative contract consists of independently usable artifacts:**

| Artifact | Producer |
| - | - |
| **`source.json`** | Any entry point establishing the source |
| **`creative\_plan.json`** | Story Director |
| **`narration.json`** | Narration Studio or compatible timing producer |
| **`asset\_manifest.json`** | Movie Builder |
| **`timeline.json`** | Movie Builder |
| **`qa\_report.json`** | Narration Studio or Movie Builder |

***A small `project.json` may reference these files. It is optional, not a database.**

***Each JSON artifact declares:**

```
***`\{`**

`  ***"spec\_version": "1.0",`**

`  ***"artifact\_type": "creative\_plan",`**

`  ***"artifact\_id": "plan\_001",`**

`  ***"revision": "p1",`**

`  ***"source\_revision": "s1",`**

`  ***"required\_features": \[\],`**

`  ***"producer": \{`**

`    ***"name": "story-director",`**

`    ***"version": "1.0"`**

`  ***\}`**

***`\}`**
```

***Version policy:**

- ***Minor revisions add optional fields or features.**

- ***Major revisions change existing meanings or required structure.**

- ***Consumers may ignore unknown optional fields.**

- ***Consumers must reject unsupported `required\_features`.**

- ***Skill version, data-spec version, and artifact revision are different concepts.**

### ***3.2 Identity and source preservation**

***Use project-local stable IDs:**

- ***`script\_segment\_id`**

- ***`speaker\_id`**

- ***`unit\_id`**

- ***`clip\_id`**

- ***`event\_id`**

- ***`asset\_id`**

- ***`shot\_id`**

***IDs must not depend solely on text or timeline position.**

***`source.json` stores the original text and its revision. Script segments identify spans within it; they do not silently rewrite it.**

***Source spans use zero-based Unicode code-point offsets with an exclusive end. No text normalization may occur without preserving a mapping.**

***For edited sources:**

- ***Preserve unaffected IDs.**

- ***Assign a new source revision.**

- ***Revalidate affected references.**

- ***Flag deleted references.**

- ***Never claim stale anchors remain valid.**

### ***3.3 Original text, spoken text, and synthesis units**

***A synthesis unit references one or more script spans and carries its actual speech input.**

***Mappings support:**

- ***Unchanged wording.**

- ***Pronunciation substitutions.**

- ***Acronym or number expansion.**

- ***Omissions explicitly authorized by the user.**

***Example:**

```
***`\{`**

`  ***"unit\_id": "unit\_001",`**

`  ***"script\_segment\_ids": \["seg\_001"\],`**

`  ***"original\_text": "Read chapter IV.",`**

`  ***"spoken\_text": "Read chapter four.",`**

`  ***"text\_mappings": \[`**

`    ***\{`**

`      ***"source\_start": 13,`**

`      ***"source\_end": 15,`**

`      ***"spoken\_start": 13,`**

`      ***"spoken\_end": 17,`**

`      ***"kind": "substitution"`**

`    ***\}`**

`  ***\]`**

***`\}`**
```

***Offsets here are relative to the unit’s displayed texts. The final validator must check them.**

***Mapping an original phrase to several spoken words produces a phrase interval—not a fabricated single-word timestamp.**

### ***3.4 Speakers and performance**

***Speaker records contain:**

- ***Stable speaker ID.**

- ***Display name.**

- ***Optional narrative role.**

***Voice assignments belong to Narration Studio.**

***Performance records distinguish:**

- ***Requested delivery.**

- ***Supported controls.**

- ***Applied controls.**

- ***Status: `applied`, `partial`, `unsupported`, or `unreviewed`.**

***Acceptance of an instruction by a TTS API does not establish successful acting.**

### ***3.5 Audio timing**

***Every narration artifact identifies a timing master:**

- ***File path.**

- ***File checksum.**

- ***Audio revision.**

- ***Sample rate.**

- ***Channel count.**

- ***Total sample-frame count.**

***All audio positions reference that master.**

***Positions are integer sample-frame offsets, start inclusive and end exclusive. A stereo frame contains simultaneous samples for both channels; it is not two timeline positions.**

***Separate:**

- ***Clip placement.**

- ***Detected speech interval.**

- ***Aligned script interval.**

- ***Optional word interval.**

***Each timing result identifies its method:**

- ***`measured\_clip`**

- ***`native\_timestamp`**

- ***`forced\_alignment`**

- ***`transcription`**

- ***`speech\_detection`**

***Do not manufacture comparable confidence scores across engines. Store tool-specific quality information when available, plus a usable review status.**

### ***3.6 Anchors**

***Creative anchors specify what boundary is intended:**

```
***`\{`**

`  ***"script\_segment\_id": "seg\_001",`**

`  ***"kind": "phrase",`**

`  ***"text": "fourteen",`**

`  ***"occurrence": 1,`**

`  ***"edge": "start",`**

`  ***"offset\_ms": 0`**

***`\}`**
```

***Supported kinds:**

- ***`phrase`**

- ***`speech\_boundary`**

- ***`clip\_boundary`**

- ***`pause\_boundary`**

***Phrase anchors are checked against the declared source revision and resolved through pronunciation mappings.**

***Important constraints reference resolved audio timing, not estimated speaking duration.**

### ***3.7 Pauses**

***Three distinct records:**

1. ***Pause request: creative intent.**

2. ***Inserted silence: generated or authorized audio edit.**

3. ***Detected silence: measured recording content.**

***A request may include preferred duration, acceptable range, and fallback.**

***Realized pauses retain the request ID.**

***Detected silence is not automatically intentional. Supplied audio may not be edited unless permission is explicit.**

### ***3.8 Assets, shots, captions, and overlays**

***Asset specification:**

- ***Logical asset ID.**

- ***Kind: image, video, graphic, or provided asset.**

- ***Prompt or description.**

- ***Optional reference assets.**

- ***Required composition hints.**

- ***Exact text supplied separately.**

***Asset realization:**

- ***Logical asset ID.**

- ***Local path and checksum.**

- ***Dimensions/duration.**

- ***Provenance.**

- ***Applied generation settings.**

- ***Status.**

***Creative shot:**

- ***Shot ID.**

- ***Asset ID.**

- ***Purpose.**

- ***Timing anchors.**

- ***Camera treatment.**

- ***Required constraints.**

- ***Permitted fallbacks.**

***Compiled shot:**

- ***Resolved file.**

- ***Start/end video frames.**

- ***Crop/fit.**

- ***Concrete camera parameters.**

- ***Transition behavior.**

***Captions and overlays are separate timed objects. Required reveal constraints apply to all relevant visual layers, including captions.**

### ***3.9 Cache and errors**

***Cache metadata includes:**

- ***Content-derived key.**

- ***Inputs and settings.**

- ***Engine/model revision where available.**

- ***Output checksum.**

- ***Completion status.**

***Editorial IDs and cache keys remain separate.**

***Errors use a common shape:**

```
***`\{`**

`  ***"code": "ANCHOR\_UNRESOLVED",`**

`  ***"severity": "error",`**

`  ***"object\_id": "shot\_002",`**

`  ***"message": "No reliable timing was found for the required reveal.",`**

`  ***"recoverable": true,`**

`  ***"suggested\_actions": \[`**

`    ***"Align the relevant passage",`**

`    ***"Approve a less precise fallback"`**

`  ***\]`**

***`\}`**
```

***Required constraints cannot be silently downgraded to preferences.**


## ***4. Significant changes and migration**

| Affected Skill | Change | Benefit | Compatibility and migration |
| - | - | - | - |
| All | Replace draft formats with specification 1.0 | Consistent exchange | Draft artifacts require a conversion/validation step |
| All | Separate script, unit, clip, and event IDs | Supports reuse and flexible chunking | Split overloaded segment objects; retain original IDs as script IDs |
| Story Director | Make timing boundary kinds explicit | Removes clip/speech ambiguity | Convert old boundary fields; flag ambiguous cases |
| Story Director | Required constraints versus preferences | Prevents silent creative degradation | Convert reveal rules to required constraints |
| Narration Studio | Concrete source-to-spoken span mapping | Supports pronunciation-aware alignment | Add mappings during text preparation |
| Narration Studio | Declare checksum-backed timing master | Prevents wrong-file synchronization | Add master metadata and revalidate existing timing |
| Narration Studio | Link realized pauses to requests | Makes reaction shots resolvable | Preserve existing pause IDs where meaningful |
| Movie Builder | Frame-grid compilation rules | Reliable cuts and reveals | Recompile existing creative plans |
| Movie Builder | Standalone optional transcription/timing route | Supports images-plus-MP3 workflow | New capability; no cooperative format break |
| All | Common error vocabulary and feature declarations | Safe independent evolution | Add envelope and structured issues |
| All | File-based cooperation | Avoids host-specific invocation assumptions | No automatic chaining required |

***No implemented user data exists in this planning conversation, so these are planned migrations, not claims that conversion tools already work.**


# ***5. Story Director — Final Plan v1**

## ***Standalone purpose**

***Create a complete, usable storyboard and visual-production plan from a story while preserving the author’s writing.**

## ***Discovery metadata**

***Proposed `SKILL.md` frontmatter:**

```
***`---`**

***`name: story-director`**

***`description: "Analyze stories and scripts into storyboards, visual beats, shot plans, image prompts, speaker directions, asset-reuse plans, and protected reveals. Use when users request visual direction or a production plan for fiction, comedy, documentaries, or educational narration. Preserve source wording unless editing is requested. Does not synthesize speech or render video."`**

***`---`**
```

## ***Inputs and outputs**

***Inputs: Story; optional style, assets, budget, audio timing, and overrides.**

***Outputs:**

- ***Readable creative brief and storyboard.**

- ***`source.json` when establishing a new source.**

- ***`creative\_plan.json`.**

- ***Asset specifications.**

- ***Performance and pause requests.**

- ***Assumptions and unresolved issues.**

## ***Tools**

***Required: Language-model capability to analyze text.**

***Optional: File writing, image inspection, contract validator.**

***No synthesis, rendering, or paid provider dependency.**

## ***Internal workflow**

1. ***Establish source revision and references.**

2. ***Identify genre, purpose, speakers, and narrative beats.**

3. ***Select a restrained visual strategy.**

4. ***Allocate assets within the requested limits.**

5. ***Plan shots across—not automatically at—sentence boundaries.**

6. ***Specify performance and information-release intentions.**

7. ***Validate references, coverage, and budget.**

8. ***Deliver a complete first draft.**

***Human review is optional. Missing noncritical preferences should become recorded assumptions.**

## ***Cooperative interface**

***Consumes optional timing and existing asset information.**

***Produces specification 1.0 creative plans without inventing timestamps.**

## ***Proposed files**

- ***`SKILL.md`**

- ***`agents/openai.yaml`**

- ***`references/contract-v1.md`**

- ***`references/directing.md`**

- ***`references/timing-and-reveals.md`**

- ***Optional `scripts/validate\_plan.py`**

- ***`assets/storyboard-template.md`**

## ***Tests and fallbacks**

***Test comedy, education, documentary, and fiction.**

***Verify source preservation, valid references, cross-sentence shots, asset limits, and optional revisions.**

***When timing is absent, use anchors. When media cannot be inspected, label description-based assignments. When a requested style is infeasible under budget, explain the compromise.**

## ***Implementation order**

***Instructions and examples → source references → structured export → validator → cooperative fixtures.**


# ***6. Narration Studio — Final Plan v1**

## ***Standalone purpose**

***Generate or analyze narration, preserve reusable audio, and export trustworthy timing.**

## ***Discovery metadata**

```
***`---`**

***`name: narration-studio`**

***`description: "Generate, revise, assemble, transcribe, or align narration and dialogue. Use for local or hosted TTS, speaker assignments, pronunciation corrections, reusable audio clips, deliberate pauses, WAV export, subtitles, or script-to-recording timing. Preserve original and spoken text separately. Distinguish clip timing from word alignment. Does not direct visuals or render video."`**

***`---`**
```

## ***Inputs and outputs**

***Inputs: Script or recording; optional voices, pronunciation rules, performance requests, pause requests, and timing anchors.**

***Outputs:**

- ***`narration.wav` or a declared supplied-audio master.**

- ***`narration.json`.**

- ***Cached clips.**

- ***Optional SRT and Audacity labels.**

- ***Audio QA and mismatch report.**

## ***Tools**

***Required for generation: One working TTS backend, local storage, audio assembly support.**

***Required for recording alignment: A supported transcription/alignment backend.**

***Optional: FFmpeg for decoding, hosted TTS, additional voice engines.**

***Do not require every backend to be installed.**

## ***Internal workflow**

1. ***Inspect execution capabilities.**

2. ***Preserve source and establish speaker assignments.**

3. ***Prepare spoken text and mappings.**

4. ***Choose natural synthesis units.**

5. ***Generate or reuse validated clips.**

6. ***Apply authorized processing.**

7. ***Measure processed audio.**

8. ***Assemble clips and explicit pauses.**

9. ***Align only where metadata is insufficient.**

10. ***Export master-linked timing and QA.**

***For recordings, preserve the original and report deviations from the script.**

## ***Cooperative interface**

***Accepts performance and pause requests; returns their realization status.**

***Resolves phrase anchors through source-to-spoken mappings.**

## ***Proposed files**

- ***`SKILL.md`**

- ***`agents/openai.yaml`**

- ***`references/contract-v1.md`**

- ***`references/engine-setup.md`**

- ***`references/pronunciation.md`**

- ***`references/alignment.md`**

- ***`scripts/synthesize.py`**

- ***`scripts/assemble.py`**

- ***`scripts/align.py`**

- ***`scripts/validate\_audio.py`**

- ***`scripts/export\_labels.py`**

- ***`assets/pronunciation-template.json`**

## ***Tests and fallbacks**

***Test:**

- ***Changed sentence.**

- ***Changed pause without resynthesis.**

- ***Multiple voices.**

- ***Repeated cached clip.**

- ***Pronunciation expansion.**

- ***Mixed sample rates.**

- ***Precise inside-clip anchor.**

- ***Script/recording disagreement.**

- ***Interrupted generation.**

***No engine means setup/preparation output, not claimed audio. No reliable word timing means unresolved anchor, not duration-based interpolation.**

## ***Implementation order**

***One engine → persistent caching → sample-based assembly → speaker assignments → recording alignment → selective word anchors → optional hosted backend.**


# ***7. Movie Builder — Final Plan v1**

## ***Standalone purpose**

***Produce narrated videos from supplied or authorized generated assets, with explicit timing confidence and inspectable outputs.**

## ***Discovery metadata**

```
***`---`**

***`name: movie-builder`**

***`description: "Assemble narrated videos from images, video clips, audio, captions, and optional creative plans. Use for slideshows, educational videos, timed reveals, simple graphics, camera movement, FFmpeg MP4 rendering, contact sheets, and video QA. Accept compatible plans without manual shot assignment. Distinguish pacing-based edits from speech-synchronized edits."`**

***`---`**
```

## ***Inputs and outputs**

***Inputs: Images/video and audio; optional script, timing, creative plan, budget, graphics, and overrides.**

***Outputs:**

- ***`final\_video.mp4`**

- ***`asset\_manifest.json`**

- ***`timeline.json`**

- ***Contact sheet.**

- ***Screenshots.**

- ***`qa\_report.json`**

## ***Tools**

***Required for rendering: FFmpeg, FFprobe, Python, local storage.**

***Optional: Image library, transcription/alignment support, mathematical renderer, image provider.**

***No paid API is required for supplied-asset workflows.**

## ***Internal workflow**

1. ***Inspect media and execution capabilities.**

2. ***Determine timing mode.**

3. ***Obtain timing if necessary and available.**

4. ***Select/realize assets.**

5. ***Compile anchors and overrides.**

6. ***Quantize visual events to frames.**

7. ***Validate coverage and required constraints.**

8. ***Render.**

9. ***Inspect output.**

10. ***Produce review materials.**

### ***Standalone timing modes**

- ***Measured synchronized: supplied or derived reliable timing.**

- ***Transcription-assisted: audio transcription plus content-based asset assignment.**

- ***Pacing-based: no reliable speech correspondence.**

***Transcription-assisted planning is best effort. Supplied images may not cover the recording, so the Skill must report mismatches rather than pretend exact semantic coverage.**

## ***Cooperative interface**

***Consumes specification 1.0 plans and narration.**

***Required reveals round to a frame no earlier than the trusted anchor. Narration stays authoritative; images do not stretch the audio.**

## ***Proposed files**

- ***`SKILL.md`**

- ***`agents/openai.yaml`**

- ***`references/contract-v1.md`**

- ***`references/rendering.md`**

- ***`references/providers.md`**

- ***`references/qa.md`**

- ***`scripts/inspect\_media.py`**

- ***`scripts/prepare\_assets.py`**

- ***`scripts/compile\_timeline.py`**

- ***`scripts/render\_video.py`**

- ***`scripts/inspect\_video.py`**

- ***`scripts/create\_contact\_sheet.py`**

- ***`assets/layout-presets.json`**

## ***Tests and fallbacks**

***Test coverage, corrupt assets, stale overrides, protected reveals, captions, transitions, frame rounding, and provider failure.**

***A final video must not silently contain missing-asset placeholders. A separately labeled debug render may.**

## ***Implementation order**

***Supplied assets and hard cuts → deterministic compiler → graphics/captions → camera movement → standalone timing support → one image adapter → fades/video clips → advisory semantic QA.**


## ***8. Skill packaging and setup**

### ***Packaging decision**

***Package each Skill independently:**

```
***`skill-name/`**

`├── ***SKILL.md`**

`├── ***agents/`**

`│   └── ***openai.yaml`**

`├── ***scripts/`**

`├── ***references/`**

`└── ***assets/`**
```

***Include only needed folders and resources. Do not bundle model weights, credentials, generated project media, or the other Skills.**

### ***`agents/openai.yaml`**

***The requested structure matches OpenAI’s documented Skill-package convention. The documentation distinguishes discovery frontmatter from UI metadata: [`SKILL.md` guidance](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md) and [`openai.yaml` fields](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md).**

***These conventions should not be assumed to work in every ChatGPT interface.**

***Proposed metadata:**

```
***`\# story-director/agents/openai.yaml`**

***`interface:`**

`  ***display\_name: "Story Director"`**

`  ***short\_description: "Plan storyboards, visual beats, and reveals"`**

`  ***default\_prompt: "Use $story-director to create a visual production plan for this story."`**

***`\# narration-studio/agents/openai.yaml`**

***`interface:`**

`  ***display\_name: "Narration Studio"`**

`  ***short\_description: "Create narration and reusable audio timing"`**

`  ***default\_prompt: "Use $narration-studio to narrate this script and export timing metadata."`**

***`\# movie-builder/agents/openai.yaml`**

***`interface:`**

`  ***display\_name: "Movie Builder"`**

`  ***short\_description: "Render narrated videos and review outputs"`**

`  ***default\_prompt: "Use $movie-builder to assemble these assets and narration into an MP4."`**
```

***Do not list Python packages or FFmpeg as MCP tools. Document executable/runtime requirements separately.**

### ***Setup and validation requirements**

***Each package should include focused setup references covering:**

- ***Supported host environment.**

- ***Required executables.**

- ***Minimal install profile.**

- ***Optional features.**

- ***Model/voice installation.**

- ***Environment-variable credentials.**

- ***Licenses and redistribution limits.**

- ***A diagnostic command or checklist.**

***Validation has three levels:**

1. ***Package: metadata, paths, and referenced resources.**

2. ***Contract: JSON structure, references, revisions, and required features.**

3. ***Behavior: actual audio/video generation and playback.**

***A metadata validator cannot establish that narration or rendering works.**


## ***9. Cross-Skill test matrix**

| Test | Inputs | Required outputs | Acceptance |
| - | - | - | - |
| **A: Director alone** | Story and image limit | Storyboard, creative plan | Preserved text, complete coverage, valid anchors, respected limit |
| **B: Narration alone** | Script, voices, pause request | Audio, clips, timing | Valid master, reusable clips, correct sample accounting, realized pause |
| **C: Builder alone** | Described images and MP3 | MP4, timeline, contact sheet | Playable output; derived speech timing; appropriate asset correspondence |
| **D: All three** | Story, approved voices/style/budget | Audio, visuals, MP4, reports | Complete automated first draft, precise reveal, intentional pause, reused asset |

### ***Important qualification for Test C**

***Images and an arbitrary MP3 do not inherently contain their intended correspondence.**

***For the synchronized acceptance test:**

- ***Use clearly relevant, inspectable/described images.**

- ***Enable Movie Builder’s optional transcription/timing dependency.**

- ***Verify the inferred assignments against a known reference.**

***Without timing tools, Test C can validate a pacing-based slideshow—but must not count that as semantic synchronization.**

### ***Integrated DOOM test**

***Use a 60–90-second excerpt containing:**

- “***The first frame took fourteen hours.”**

- ***A deliberate post-punchline pause.**

- ***A reaction.**

- ***A later opportunity to reuse a classroom image.**

***Requirements:**

- ***No manually authored shot timestamps.**

- ***No manual assignment when the director plan is complete.**

- ***The statistic appears no earlier than its resolved spoken anchor.**

- ***The reaction uses realized silence.**

- ***Captions do not disclose the protected statistic early.**

- ***At least one visual asset is reused.**

- ***No unauthorized generation or unrelated regeneration.**

### ***Measurable technical criteria**

***At 30 FPS:**

- ***Frame quantization adds less than one frame of reveal delay.**

- ***Alignment uncertainty is reported separately.**

- ***No unintended visual gaps.**

- ***No unexplained primary-shot overlaps.**

- ***Master sample accounting matches written audio.**

- ***The planned video covers the audio endpoint with less than one frame of rounding extension.**

- ***Encoded duration checks use a declared, toolchain-tested tolerance.**

***Human playback remains required to judge intelligibility, pacing, pronunciation, and whether the joke lands.**


## ***10. Implementation sequence**

1. ***Freeze specification 1.0 and small test fixtures.**

   - ***Include source, creative plan, narration timing, and expected resolved timeline.**

2. ***Implement Story Director’s standalone instructions and export.**

   - ***No media backend required.**

3. ***Implement Narration Studio with one local engine.**

   - ***Persistent clips, WAV assembly, measured timing.**

4. ***Implement Movie Builder with supplied assets.**

   - ***Hard cuts, exact-text card, deterministic compilation, MP4.**

5. ***Run integrated Test D using supplied images.**

   - ***This tests direction, narration, and editing before cloud generation.**

6. ***Add recording alignment and standalone Builder timing.**

   - ***Use the same optional timing implementation.**

7. ***Add one authorized image-generation adapter.**

   - ***Then repeat Test D with generated visuals.**

8. ***Add richer effects only after observed need.**

   - ***Fades, background audio, source-video handling, semantic review.**

***The first integrated movie should precede broad provider support and sophisticated QA.**


## ***11. Final decision log**

| Category | Decisions |
| - | - |
| **Accepted** | Three independent Skills; immutable source; stable IDs; audio authority; FFmpeg; reusable assets; sample-based narration assembly; exact-text graphics |
| **Modified** | Explicit boundary kinds; concrete text mappings; required versus preferred constraints; pause realization contract; standalone Builder timing route |
| **Rejected** | Mandatory companion installation; one sentence equals one shot; invented word timestamps; unbounded regeneration; silently relaxed reveals; universal Skill-invocation assumptions |
| **Deferred** | Overlapping dialogue, cinematic character conditioning, render-segment caching, music ducking, automatic creative repair, multiple provider adapters |
| **Experimental verification required** | TTS naturalness, emotion control, alignment reliability, target-machine setup, provider availability/cost, encoded duration tolerance, host packaging behavior |


## ***12. Remaining technical risks**

1. ***Good-looking plans that produce dull films.  
Mitigation: early full-sequence playback, not just per-shot validation.**

2. ***Incorrect timing after substitutions or recording deviations.  
Mitigation: explicit mappings, provenance, and unresolved-anchor handling.**

3. ***Standalone Builder cannot infer intended imagery reliably.  
Mitigation: inspect assets, label timing modes, and report missing visual coverage.**

4. ***Voice quality or continuity disappoints.  
Mitigation: audition voices and compare synthesis-unit lengths.**

5. ***Provider or runtime instability.  
Mitigation: local persistence, bounded retries, one tested backend at a time.**

6. ***Skill discovery differs by host.  
Mitigation: validate packaging and tool execution in the actual deployment environment.**

7. ***Semantic QA “corrects” intentional irony.  
Mitigation: supply shot purpose and keep semantic findings advisory.**

### ***How the Skills evolve independently**

***The interoperability contract—not internal implementation—is the stable boundary.**

***Narration Studio can change TTS engines while preserving master-linked timing. Movie Builder can improve rendering while accepting the same creative constraints. Story Director can improve its planning without knowing either backend.**

***Independent evolution depends on:**

- ***Versioned artifacts.**

- ***Explicit required features.**

- ***Stable editorial identities.**

- ***Immutable revision references.**

- ***Compatibility fixtures tested by every release.**

- ***Small migration tools for deliberate breaking changes.**

***The final architecture is three separately useful Skills exchanging inspectable production artifacts. Their shared promise is not perfect filmmaking—it is a reproducible, repairable path from story to a watchable first draft**

