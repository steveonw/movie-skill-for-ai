***Gemini Pro Latest**

***Reasoning**

***Here is the Narration Studio Skill Implementation Plan. This design bridges the gap between the creative intent of the Story Director and the final mechanical assembly required by the Movie Builder, using a highly efficient chunk-and-cache approach inspired by `Read-Aloud-Main`.**


### ***1. Skill Name and Triggering Description**

***Name: AI Narration Studio  
Description / System Trigger:  
"I am an audio engineer and TTS director. I manage dialogue, narration, and speech synchronization. I can convert scripts into cached, sentence-level audio clips, synthesize multiple voices, insert deliberate pauses, and output precise timing data. I can also ingest user-supplied voiceovers and align them to a script. I output standardized audio tracks and JSON timing manifests for standalone use or automated video assembly."**

### ***2. Standalone Workflows**

***As a standalone tool, the Skill functions as a highly efficient audiobook/podcast generator and timing extractor.**

***Workflows:**

- ***Audiobook Generation: Ingest a text file, chunk it into sentences, synthesize using a local/hosted TTS, and stitch it into a master WAV with a companion `.srt` subtitle file.**

- ***Iterative Dialogue Editing: A user updates one line in a 50-line script. The Skill re-synthesizes only* the changed line using the cache and re-exports the master track instantly.**

- ***Speech-to-Text Alignment: The user uploads a script and a pre-recorded MP3. The Skill runs forced alignment and returns an Audacity label track or JSON file mapping sentences to exact millisecond timestamps.**

### ***3. Cooperation with Story Director and Movie Builder**

- ***Ingestion: Narration Studio ingests the `NarrativeManifest.json` from the Story Director. It reads the `script\_lines` array, including speaker assignments and emotion tags.**

- ***Processing: It generates (or aligns) the audio, creating a library of cached WAV files and resolving abstract timing anchors (e.g., cut after "Bang"*) into absolute timestamps (e.g., *t*=14.2*s*).**

- ***Handoff: It outputs an `audio\_timeline.json` and optionally a pre-mixed master `narration.wav`. The Movie Builder will use this timeline as the absolute rigid backbone for video rendering.**

### ***4. Recommended `SKILL.md` Structure**

```
***`\# AI Narration Studio`**


***`\#\# Role`**

***`You are the Audio Supervisor. Your goal is to produce high-quality, perfectly timed speech assets while minimizing compute costs through aggressive caching.`**


***`\#\# Core Directives`**

***`1. \*\*Chunk and Cache:\*\* Never generate a monolithic audio file directly. Break text into logical segments (sentences/beats), generate individual WAVs, and cache them by text/speaker hash.`**

***`2. \*\*Measure, Don't Guess:\*\* To find segment timings, measure the exact byte duration of the generated WAV files.`**

***`3. \*\*Handle Gaps Explicitly:\*\* Treat silence as an explicit, measurable audio clip in the timeline.`**

***`4. \*\*Selective Word Alignment:\*\* Only run expensive word-level forced alignment on a segment if a specific visual anchor requires it.`**


***`\#\# Output Modes`**

***`- Mode 1: Master \`audio.wav\` + \`subtitles.srt\`.`**

***`- Mode 2: \`audio\_timeline.json\` + individual cached WAVs.`**
```

### ***5. Scripts, Reference Files, and Optional Assets**

- ***`cache\_manager.py`: Handles hashing, saving, and retrieving WAV clips.**

- ***`tts\_wrapper.py`: A unified interface for local (Piper/Kokoro) and hosted (OpenAI/ElevenLabs) generation.**

- ***`aligner.py`: A script utilizing `stable-ts` for forced alignment of user-supplied audio.**

- ***`pronunciation\_dict.json`: A mapping of text substitutions (e.g., `"MTH263": "Math two sixty three"`) applied before* TTS generation to fix robotic mispronunciations.**

- ***`voices.json`: A directory of available speakers and their corresponding TTS model IDs.**

### ***6. TTS Engine and Alignment Options**

- ***Local TTS (Preferred V1): `Piper VITS` or `Kokoro 82M`. These are fast, CPU-friendly, and perfect for the chunk-by-chunk method pioneered by `Read-Aloud-Main`.**

- ***Hosted TTS: API integration for OpenAI TTS or CosyVoice when high emotional expressivity is demanded.**

- ***Aligner: `stable-ts` (wrapping `faster-whisper`). Critical for Workflow A (user-supplied audio) and for finding exact word locations inside generated clips.**

### ***7. A Robust Caching Strategy**

***Borrowing heavily from `Read-Aloud-Main`, caching is the heart of this Skill.**

- ***The Hash: `hash(speaker\_id + voice\_settings + raw\_text + pronunciation\_dict\_version)`**

- ***Storage: Saves as `cache/hash.wav` and `cache/hash.json`.**

- ***Benefit: If the user changes one typo in sentence 40 of a 100-sentence script, only sentence 40 is regenerated. The master timeline is re-assembled instantly by measuring the lengths of the WAVs.**

### ***8. Proposed Audio Timing JSON Schema**

***This schema resolves the abstract intents from Story Director into concrete, measurable audio data for Movie Builder.**

```
***`\{`**

`  ***"project\_duration": 45.2,`**

`  ***"timeline": \[`**

`    ***\{`**

`      ***"type": "speech",`**

`      ***"id": "line\_01",`**

`      ***"speaker": "Narrator",`**

`      ***"original\_text": "By day eight, Kevin finally pressed the fire button.",`**

`      ***"spoken\_text": "By day eight, Kevin finally pressed the fire button.",`**

`      ***"file": "cache/abc123hash.wav",`**

`      ***"start": 0.0,`**

`      ***"duration": 3.4,`**

`      ***"word\_anchors": \{`**

`        ***"eight": 0.85`**

`      ***\}`**

`    ***\},`**

`    ***\{`**

`      ***"type": "silence",`**

`      ***"id": "gap\_01",`**

`      ***"duration": 1.5,`**

`      ***"start": 3.4`**

`    ***\},`**

`    ***\{`**

`      ***"type": "speech",`**

`      ***"id": "line\_02",`**

`      ***"speaker": "SFX Guy",`**

`      ***"original\_text": "Bang.",`**

`      ***"file": "cache/xyz789hash.wav",`**

`      ***"start": 4.9,`**

`      ***"duration": 0.4`**

`    ***\}`**

`  ***\]`**

***`\}`**
```

### ***9. Performance, Pronunciation, and Emotion-Control Limitations**

- ***Word-Level Fallacy: Verified Read-Aloud-Main behavior* proves that clipping text into sentences gives perfect sentence-level timestamps natively (by measuring the clip). However, it does not give word-level timestamps natively.* If Story Director demands a cut on the word "eight" inside a 4-second clip, Narration Studio must* run `stable-ts` on that specific clip to find the word.**

- ***Pronunciation: TTS engines will botch acronyms, math symbols, and usernames. The `pronunciation\_dict.json` substitution step is mandatory before hashing.**

- ***Emotion vs. Consistency: Lightweight local models (Piper) have limited emotional range. If emotion is required, hosted models (CosyVoice) must be used, which introduces network latency and API costs to the caching system.**

### ***10. Test Cases**

1. ***The Typo Test: Submit a 10-line script. Change a word in line 5. Verify that only line 5 generates a new API call/TTS process, and the timeline shifts downstream timestamps automatically.**

2. ***The Comedic Pause: Pass a directive requesting a 3-second gap between two speakers. Verify `audio\_timeline.json` inserts a `"type": "silence"` block and offsets the start time of the next clip by exactly 3.0s.**

3. ***The Multi-Voice Test: Pass a script alternating between "Narrator" and "SFX Guy". Verify the stitched master WAV correctly switches TTS models without overlapping.**

4. ***Exact Word Reveal: Request an anchor on a specific word in the middle of a sentence. Verify the Skill runs alignment on that chunk and populates the `"word\_anchors"` array in the JSON.**

### ***11. Failure Handling, Dependencies, and Milestones**

- ***Failures:**

  - **TTS API Timeout:* Fallback to local Piper TTS if ElevenLabs/OpenAI is down, appending a warning to the output.**

  - **Alignment Mismatch:* If the user-supplied MP3 completely deviates from the script, `stable-ts` will hallucinate. The Skill must detect low confidence scores and flag the segment for manual review.**

- ***Milestones:**

  - **M1:* Sentence chunking, local Piper generation, caching, and WAV concatenation.**

  - **M2:* Ingesting user MP3s and aligning them to a script.**

  - **M3:* Exposing word-level anchors on demand inside generated clips.**

### ***12. Improvements Recommended for the Round 1 Plan**

1. ***Anchor Flagging: The Story Director must explicitly flag which* words are visual anchors. Narration Studio shouldn't run word-level alignment on every word in the script—only the ones the Director needs for cuts/reveals.**

2. ***Pronunciation Hints: Story Director should output a separate field for `spoken\_text` if it detects complex terms (e.g., `original: "FPS"`, `spoken: "frames per second"`). Narration Studio will cache based on `spoken\_text` but subtitle based on `original`.**

3. ***Silence Directives: Story Director should provide estimated durations for pauses (e.g., `deadpan\_hold: 2.5s`) so Narration Studio knows how much mathematical silence to insert between clips.**


### ***Ideas Worth Revisiting in Round 4**

- ***Audio Ducking: Should Narration Studio handle background music and volume ducking, or is that strictly the domain of Movie Builder via FFmpeg?**

- ***Sound Effects (SFX): Who is responsible for sourcing the literal "Bang" sound effect if we want a real sound instead of a guy saying it? Does Narration Studio handle SFX libraries, or does Movie Builder composite them?**

- ***Overlapping Dialogue: The chunk-and-stitch method is linear. How do we handle two characters interrupting each other or talking simultaneously in a more advanced V2?**

***$0.0773,744 tok**

*![](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1MTIiIGhlaWdodD0iNTEyIiBzaGFwZS1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVF1YWxpdHkiIGZpbGwtcnVsZT0iZXZlbm9kZCIgY2xpcC1ydWxlPSJldmVub2RkIiB2aWV3Qm94PSIwIDAgNTEyIDUxMiI+PHJlY3QgZmlsbD0iI0NDOUI3QSIgd2lkdGg9IjUxMiIgaGVpZ2h0PSI1MTIiIHJ4PSIxMDQuMTg3IiByeT0iMTA1LjA0MiIvPjxwYXRoIGZpbGw9IiMxRjFGMUUiIGZpbGwtcnVsZT0ibm9uemVybyIgZD0iTTMxOC42NjMgMTQ5Ljc4N2gtNDMuMzY4bDc4Ljk1MiAyMTIuNDIzIDQzLjM2OC4wMDQtNzguOTUyLTIxMi40Mjd6bS0xMjUuMzI2IDBsLTc4Ljk1MiAyMTIuNDI3aDQ0LjI1NWwxNS45MzItNDQuNjA4IDgyLjg0Ni0uMDA0IDE2LjEwNyA0NC42MTJoNDQuMjU1bC03OS4xMjYtMjEyLjQyN2gtNDUuMzE3em0tNC4yNTEgMTI4LjM0MWwyNi45MS03NC43MDEgMjcuMDgzIDc0LjcwMWgtNTMuOTkzeiIvPjwvc3ZnPgo= "Favicon for anthropic")**Claude Opus Latest**

***Reasoning**

***[https://github.com/steveonw/Read-Aloud-Main](https://github.com/steveonw/Read-Aloud-Main)Auto**

***Reasoning**

***[https://api.github.com/repos/steveonw/Read-Aloud-Main/git/trees/main?recursive=1](https://api.github.com/repos/steveonw/Read-Aloud-Main/git/trees/main?recursive=1)Auto**

***Reasoning**

***shellcd /tmp && curl -sL https://raw.githubusercontent.com/steveonw/Read-Aloud-Main/main/web/app.js -o app.js && curl -sL https://raw.githubusercontent.com/steveonw/Read-Aloud-Main/main/SPEC-1.1.md -o spec.md && wc -c app.js spec.md 2 commands**

***timeout**

***Sandbox has no network; I'll fetch the source directly.**

***[https://raw.githubusercontent.com/steveonw/Read-Aloud-Main/main/web/app.js](https://raw.githubusercontent.com/steveonw/Read-Aloud-Main/main/web/app.js)Auto**

***Reasoning**

***Searched for kokoro python KPipeline tokens start\_ts end\_ts word timestamps5 results**

***Reasoning**

***Searched for piper1-gpl OHF-Voice GPL license piper voices model card dataset license commercial use5 results**

***Reasoning**

# ***Narration Studio Skill: Implementation Plan (Round 2 of 4)**

***This is a design only. Nothing has been built or run. ⏳ Provisional marks decisions to settle in Round 4. For Read-Aloud-Main, I read the source this time (`web/app.js`), not just the README, so §0 separates what the code actually does from what I'm proposing to add.**


## ***0. Read-Aloud-Main: verified behavior vs. proposed extensions**

### ***Verified from `web/app.js` (checked today)**

| Feature | What the code actually does |
| - | - |
| **Segmentation** | Splits on **`. ! ? …`** and on **every newline**. Handles closing quotes and brackets, and skips a built-in list of abbreviations (Mr, Dr, etc…), single-letter initials and numbered-list markers ("1." at line start). Sentences over 600 characters are cut at whitespace. |
| **Pronunciation** | **`\[pattern, replacement\]`** pairs, applied longest first, as word-bounded regex on the **spoken string only**. The editor text never changes. |
| **Cache key** | **`voiceId \# speaker \# deliveryPreset | speed(2 dp) | spokenText`**. Because the key uses the text *after* pronunciation, changing a dictionary entry re-renders only the affected sentences. |
| **Cache storage** | **In-memory only**, an 800 MB soft cap with oldest-first eviction, never evicted during a render. **Switching voice clears the whole cache.** Nothing persists after the tab closes. |
| **Gaps** | Sentence gap = the slider value. Paragraph gap (blank line) = slider **+ 0.4 s**. Continuation of a split long sentence = **min(0.12 s, slider)**. Gaps are literal zero samples. |
| **Label timing** | **`t0/t1`** come from **running sample counts** after pitch resampling, written to 6 decimals. Each label covers the **whole synthesized clip, including the engine's own leading and trailing silence**. Nothing is trimmed. |
| **Label text** | The label contains the **spoken** text (after pronunciation), not the original text. |
| **Voices** | **One voice and one speaker for the whole document.** No per-sentence casting. |
| **Delivery** | Piper/VITS "natural" vs. "steady" presets just change **`noiseScale`**/**`noiseScaleW`** (0.667/0.8 vs. 0.25/0.35). Pitch is a post-synthesis linear resample, with engine speed compensated to keep the pace. |
| **Export** | Mono 16-bit PCM WAV, or 64 kbps MP3 (LAME in a worker). |
| **Flags** | Anchored by sentence text plus 40 characters of context on each side. They re-bind after edits by word-overlap similarity (thresholds 0.4 / 0.55 / 0.8). |

### ***Proposed extensions (not in Read-Aloud)**

- ***Per-segment speakers and voices (casting).**

- ***A persistent disk cache that survives voice switches.**

- ***Trimming engine silence so a requested pause is the actual* silence heard.**

- ***Pause lengths per segment instead of one global slider.**

- ***Word-level timing from native TTS durations or selective alignment.**

- ***Labels with segment IDs and display text, round-tripped back from Audacity.**

- ***Aligning user-supplied recordings.**

***Two consequences for this design:**

1. ***Read-Aloud's labels are exact clip* boundaries, not speech boundaries. A clip with 150 ms of engine lead-in silence starts 150 ms before the voice does. For cut-on-word timing, that difference matters.**

2. ***Read-Aloud's segmenter and Round 1's `segment\_script.py` would produce different segments for the same text. The project needs one segmenter, not two (see §12).**


## ***Core design decisions**

1. ***Narration Studio owns the spoken layer; Story Director owns the display layer. `script.json` holds what the author wrote. `narration.json` adds what was actually said (`spoken\_text`) plus a word map linking the two.**

2. ***Every timestamp carries its source. Timing is never just a number. It's tagged `exact`, `measured`, `model`, `aligned`, `interpolated` or `manual`, so downstream tools know how far to trust it.**

3. ***Sample counts are the master clock. Exact boundaries are stored as integer sample positions, with seconds derived from them. Float drift can't build up over a 30-minute audiobook.**

4. ***The cache is the source of determinism, not the engine. VITS-family engines inject random noise, so the same text may not produce byte-identical audio twice (unverified per engine). Once rendered, a clip is reused until its inputs change.**

5. ***Ask for word timing only when it's needed. Most cuts land on segment boundaries. Word timing is produced only for segments with a mid-segment anchor, `importance: critical` or word-level captions.**


## ***1. Name and triggering description**

***Name: `narration-studio`**

```
***`---`**

***`name: narration-studio`**

***`description: \>`**

`  ***Turns text into narrated audio and produces precise timing data. Generates`**

`  ***speech sentence by sentence with local or hosted TTS, assigns voices to`**

`  ***multiple speakers, inserts deliberate pauses, applies pronunciation fixes,`**

`  ***and re-renders only changed sentences. Also aligns a user-supplied MP3/WAV`**

`  ***to its script, transcribes audio when no script exists, and exports`**

`  ***narration.wav, narration.json (segment, word, and silence timings with`**

`  ***confidence), SRT/VTT subtitles, and Audacity label tracks. Use for`**

`  ***audiobooks, narration, voiceovers, dialogue, read-alouds, subtitle timing,`**

`  ***or syncing a recording to text. Does not plan visuals or render video.`**

***`---`**
```

***Should not trigger for music generation, sound-effect libraries, voice cloning of real people without consent, or video rendering.**


## ***2. Standalone workflows**

| Mode | Example request | Output |
| - | - | - |
| **Speak** | "Read this chapter aloud in a calm voice." | **`narration.wav`** + **`narration.json`** + labels |
| **Cast** | "Narrator is deep and slow; Kevin is younger and annoyed." | **`cast.json`** + a short preview clip per voice |
| **Update** | "I changed paragraph 3, re-record it." | New WAV; report shows "2 re-rendered, 41 reused" |
| **Fix pronunciation** | "It's saying FPS wrong." | Dictionary entry + re-render of affected segments only |
| **Align** | "Here's my MP3 and the script; give me timings." | **`narration.json`** with aligned times + a mismatch report |
| **Transcribe** | "Make subtitles for this recording." (no script) | Transcript + SRT; offered as a draft script |
| **Subtitles** | "SRT, max 2 lines, 42 characters per line." | **`subtitles.srt`** / **`.vtt`** |
| **Audit** | "Are the pauses where I wanted them?" | List of silences: requested vs. measured |
| **Round-trip** | "I moved labels in Audacity; use those." | Imported manual timings or pause adjustments |

***Execution environments. Two cases need to be separated:**

- ***In the chat sandbox: probably no GPU and possibly no network for model downloads. Real TTS there depends on whether model weights can be bundled or fetched. Piper medium voices are tens of MB; Kokoro needs PyTorch. This is unverified and could decide whether the TTS modes work inside ChatGPT at all.**

- ***On the user's machine: the Skill hands over `scripts/` plus a single command. Every mode works this way.**

***The Skill must detect which case it's in and say so, not fail silently.**


## ***3. Working with Story Director and Movie Builder**

```
***`script.json ─┐                          ┌─► narration.wav ──────────────┐`**

***`plan.narration┼─► \[Narration Studio\] ───┼─► narration.json ────────────┼─► \[Movie Builder\]`**

***`cast.json ───┘   (or: story.md alone)   ├─► subtitles.srt (optional)    │   resolves plan anchors`**

***`user.mp3 ────────┘                      └─► labels.txt (Audacity)       │   against narration.json`**

`                                                                        ┘`
```

***Reads (all optional except the text):**

- ***`script.json` from Story Director. If it's absent, Narration Studio segments the text itself, using the same segmenter (§12).**

- ***`plan.narration`: `speaker`, `delivery`, `pause\_after`, `importance`, and which segments need word timing.**

- ***`plan.shots` anchors. Used only to decide which* segments need word timing; Narration Studio doesn't interpret shots.**

- ***A user recording.**

***Writes:**

- ***`narration.json`: the timing source of truth for everything downstream.**

- ***`narration.wav`: the master track, at 48 kHz mono ⏳ (a common video audio rate; Movie Builder may prefer something else).**

- ***Clips in `cache/`, subtitles and labels.**

***Contract rules:**

- ***All timing is keyed by `script.json` segment ID and display-word index, never by spoken-word index.**

- ***`narration.json` records the `sha256` of both `script.json` and `narration.wav`. If either changes, downstream timing is stale.**

- ***Silence is explicit data, so Movie Builder never has to infer it from gaps.**


## ***4. Recommended `SKILL.md` structure (aim for under about 300 lines)**

```
***`---`**

***`(frontmatter)`**

***`---`**

***`\# Narration Studio`**

***`\#\# What this skill does / does not do`**

***`\#\# Detect environment          → can we synthesize here? which engines are installed?`**

***`\#\# Choose a mode               → table from §2`**

***`\#\# Core rules`**

`   ***1. Never change display text. Spoken changes go in spoken\_text + word\_map.`**

`   ***2. Every time value carries a source tag. Never present model/aligned`**

`      ***timing as exact.`**

`   ***3. Pauses are written as silence after trimming engine padding.`**

`   ***4. Re-render only cache misses; report reused vs. new.`**

`   ***5. Unsupported delivery directions are reported, never silently dropped.`**

`   ***6. User audio is the timing authority; the script is the text authority.`**

***`\#\# Workflow: generated audio   → prepare → cast → synthesize → measure → assemble → export`**

***`\#\# Workflow: supplied audio    → load → transcribe/align → reconcile → export`**

***`\#\# Word timing: when and how   → references/timing-tiers.md`**

***`\#\# Handoff                     → references/narration-schema.md`**

***`\#\# When things go wrong        → condensed §11`**
```


## ***5. Files**

```
***`narration-studio/`**

`├── ***SKILL.md`**

`├── ***references/`**

`│   ├── ***narration-schema.md     \# narration.json, cast.json field spec`**

`│   ├── ***timing-tiers.md         \# exact/measured/model/aligned/interpolated rules`**

`│   ├── ***engines.md              \# capability matrix, install notes, licenses`**

`│   ├── ***pronunciation.md        \# number/unit normalization, dictionary format`**

`│   ├── ***pauses.md               \# category → seconds table, trim policy`**

`│   ├── ***delivery-mapping.md     \# how free-text directions map per engine`**

`│   └── ***examples/doom-excerpt/  \# golden script.json, narration.json, labels`**

`├── ***assets/`**

`│   ├── ***narration.schema.json`**

`│   ├── ***cast.schema.json`**

`│   └── ***pronunciations.default.tsv`**

`└── ***scripts/`**

`    ├── ***scriptkit.py            \# SHARED segmenter (identical copy in Story Director)`**

`    ├── ***prepare.py              \# display → spoken\_text + word\_map; render units`**

`    ├── ***synth.py                \# engine adapters + content-addressed cache`**

`    ├── ***measure.py              \# trim, voiced onset/offset, loudness`**

`    ├── ***assemble.py             \# concat + inserted silences → wav + narration.json`**

`    ├── ***align.py                \# user audio or selective in-clip alignment`**

`    ├── ***reconcile.py            \# transcript ↔ script diff (ad-libs, skips)`**

`    ├── ***export\_subs.py          \# SRT/VTT from display words`**

`    ├── ***labels.py               \# Audacity export AND import`**

`    └── ***audit.py                \# pause/level/duration checks`**
```

***`assemble.py` is the core. It's plain NumPy and needs no TTS engine, so Milestone N1 can be tested with any WAV clips.**


## ***6. TTS engines and alignment options**

### ***TTS capability matrix (⏳ needs install testing; nothing here has been benchmarked)**

| Engine | Runs on | Native word timing | Delivery control | Notes |
| - | - | - | - | - |
| **Piper voices via sherpa-onnx** | CPU, small | None | Speed; **`noise\_scale`** (Read-Aloud's "steady") | Same engine family as Read-Aloud. Each voice's license is in its own MODEL\_CARD |
| **KittenTTS via sherpa-onnx** | CPU, tiny | None | Speaker ID, speed | Several speakers per file (verified in Read-Aloud) |
| **Kokoro 82M** (**`kokoro`** Python package) | CPU workable, GPU faster | **Yes, for English**: **`result.tokens\[\*\].start\_ts/end\_ts`**, derived from predicted phoneme durations (verified in source) | Voice choice, speed, voice blending | The source has a **`TODO: Is -3 an appropriate offset?`**, and the author says the timestamps "might not be perfect." Treat them as **`model`**, not **`exact`**. Pulls in PyTorch |
| **CosyVoice (instruct variants)** | Realistically a GPU | Unknown | Natural-language instructions ("frustrated, faster") | The only candidate for real emotional direction. Heavy |
| **Hosted (HF providers, others)** | Remote | Varies | Varies | Availability and prices change; check at runtime. I haven't verified any current TTS prices for this plan |

***Default casting rule: use the cheapest engine that can follow the direction. Flat or deadpan → Piper or Kokoro. "Increasingly frustrated" → an instruct engine if one is available; otherwise Kokoro with a speed change and a warning that the emotion couldn't be produced.**

### ***Alignment options**

| Need | Tool | Notes |
| - | - | - |
| Transcript from user audio | **faster-whisper** with word timestamps | Approximate; works as a first pass and for detecting ad-libs |
| Script to user audio (word level) | **WhisperX** or **ctc-forced-aligner** | ⚠️ **Licensing:** ctc-forced-aligner's default model is derived from Meta's MMS, and I believe MMS weights are CC-BY-NC. **Unverified, and it matters for monetized videos.** WhisperX's default English aligner uses a different wav2vec2 model; its license also needs checking |
| Word timing inside a TTS clip | The same aligner, on a 2–10 s clip with known text | Short, clean, known text: the easiest case for an aligner |
| Critical short words ("Bang") | **Energy onset** within the aligned or model window | Cheap, deterministic, and a sanity check on the aligner |


## ***7. Caching strategy**

***Key = `sha256` of a canonical JSON object containing:**

```
***`\{`**

`  ***"engine": "kokoro", "engine\_version": "x.y.z", "model\_sha256": "…",`**

`  ***"voice": "am\_michael", "speaker\_id": null,`**

`  ***"params": \{"speed": 0.95, "noise\_scale": null, "instruct": null\},`**

`  ***"spoken\_text": "By day eight, Kevin finally pressed the fire button.",`**

`  ***"postprocess\_version": 2, "take": 1`**

***`\}`**
```

***What changes compared with Read-Aloud:**

- ***It lives on disk: `cache/ab/abcdef….wav` plus a sidecar `abcdef….json` holding sample count, native word timings, trim offsets and loudness. Cached measurements mean re-assembling never re-analyzes the audio.**

- ***Caches survive voice switches because the voice is part of the key. Switching back is free, whereas Read-Aloud clears everything.**

- ***The model file hash is part of the key, so updating a voice can't silently mix old and new renders.**

- ***Takes: `take` lets a user ask for another reading of one line ("try Bang again") without touching anything else. A chosen take is locked in `narration\_overrides.json` by `segment\_id + spoken\_text hash`. If the text changes, the lock is dropped with a warning.**

- ***Raw and processed audio are kept separately. Raw engine output is cached once. Trimming and loudness processing are recomputed when `postprocess\_version` changes, without re-synthesizing.**

- ***The assembled track is never cached as an authority. Assembly is cheap and is always rebuilt from clips plus the pause table.**

- ***Alignment cache key = `sha256(audio) + sha256(text) + aligner + version`.**

- ***No eviction in v1. A `cache prune --unused-by narration.json` command handles cleanup.**


## ***8. Timing schema: `narration.json`**

***Timing source tags:**

| Tag | Meaning | Typical use |
| - | - | - |
| **`exact`** | Sample-counted boundary of audio we inserted | Clip edges, inserted silences |
| **`measured`** | Detected by deterministic signal analysis | Voiced onset/offset, silences in user audio |
| **`model`** | The TTS engine's predicted durations | Kokoro word times |
| **`aligned`** | Forced alignment, with a score | User audio; words inside a clip |
| **`interpolated`** | Estimated between neighbors | Low-confidence words |
| **`manual`** | Imported from Audacity or an override | Human fixes |

***Clip-boundary timing is exact only for clip edges. It says nothing exact about any word inside the clip, or even about when the voice starts. That's why `voiced\_start` is a separate `measured` value.**

***Example (DOOM s012–s014, generated mode):**

```
***`\{`**

`  ***"schema": "narration-studio/narration@0.1",`**

`  ***"mode": "generated",`**

`  ***"script": \{"file": "script.json", "sha256": "41ab…"\},`**

`  ***"audio": \{"file": "narration.wav", "sha256": "7c1e…",`**

`            ***"sample\_rate": 48000, "channels": 1, "samples": 4310400\},`**

`  ***"cast": \{`**

`    ***"narrator": \{"engine": "kokoro", "voice": "am\_michael", "speed": 0.95\},`**

`    ***"sfx\_guy":  \{"engine": "piper-sherpa", "voice": "en\_US-joe-medium", "speed": 0.9\}`**

`  ***\},`**

`  ***"segments": \{`**

`    ***"s012": \{`**

`      ***"speaker": "narrator", "unit": "u012", "clip": "cache/3f/3fa9….wav",`**

`      ***"spoken\_text": "By day eight, Kevin finally pressed the fire button.",`**

`      ***"s0": 2880000, "s1": 3016800, "boundary\_src": "exact",`**

`      ***"voiced": \{"start": 60.012, "end": 62.818, "src": "measured"\},`**

`      ***"words\_src": "model",`**

`      ***"words": \[`**

`        ***\{"i": 2, "start": 60.20, "end": 60.41, "src": "model"\},`**

`        ***\{"i": 3, "start": 60.41, "end": 60.80, "src": "model"\},`**

`        ***\{"i": 4, "start": 60.95, "end": 61.31, "src": "model"\}`**

`      ***\]`**

`    ***\},`**

`    ***"s013": \{`**

`      ***"speaker": "sfx\_guy", "unit": "u013", "clip": "cache/91/91d0….wav",`**

`      ***"spoken\_text": "Bang.",`**

`      ***"s0": 3060000, "s1": 3086400, "boundary\_src": "exact",`**

`      ***"voiced": \{"start": 63.762, "end": 64.255, "src": "measured"\},`**

`      ***"critical": true,`**

`      ***"words": \[\{"i": 1, "start": 63.762, "end": 64.255, "src": "measured",`**

`                 ***"check": \{"aligned\_start": 63.79, "delta": 0.028\}\}\]`**

`    ***\},`**

`    ***"s014": \{`**

`      ***"speaker": "narrator", "unit": "u014", "clip": "cache/c2/c2b7….wav",`**

`      ***"spoken\_text": "Everyone stared at him.",`**

`      ***"s0": 3182400, "s1": 3268800, "boundary\_src": "exact",`**

`      ***"voiced": \{"start": 66.315, "end": 67.952, "src": "measured"\},`**

`      ***"words\_src": "none"`**

`    ***\}`**

`  ***\},`**

`  ***"silences": \[`**

`    ***\{"after": "s012", "s0": 3016800, "s1": 3060000, "kind": "inserted",`**

`     ***"category": "beat", "requested\_s": 0.8, "actual\_s": 0.9, "src": "exact"\},`**

`    ***\{"after": "s013", "s0": 3086400, "s1": 3182400, "kind": "inserted",`**

`     ***"category": "deadpan", "requested\_s": 2.0, "actual\_s": 2.06, "src": "exact"\}`**

`  ***\],`**

`  ***"word\_map": \{`**

`    ***"s021": \[\{"display": \[4\], "spoken": "zero point zero zero zero zero zero two"\},`**

`             ***\{"display": \[5\], "spoken": "frames per second"\}\]`**

`  ***\},`**

`  ***"warnings": \[`**

`    ***\{"seg": "s009", "code": "delivery\_unsupported",`**

`     ***"msg": "'increasingly frustrated' not supported by kokoro; used speed 1.05"\}`**

`  ***\]`**

***`\}`**
```

***The values are illustrative.**

***Notes on the schema:**

- ***Segment and silence boundaries are integer samples (`s0/s1`). Seconds are derived from them.**

- ***`actual\_s` can exceed `requested\_s` because the trim policy keeps a fixed tail (~30–60 ms ⏳) for natural decay. The audit compares the two.**

- ***`words` lists only the words that were timed. Omitted words are untimed, not zero.**

- ***`word\_map` handles expansions. Display word 4 ("0.000002") is spoken as eight words. Captions show "0.000002"; an anchor on display word 4 resolves to the span of all eight spoken words.**

- ***In supplied mode, silences have `kind: "detected"` with `src: "measured"`. If the plan expected a pause there, they carry `expected\_category` and an audit result.**


## ***9. Performance, pronunciation and emotion limits**

- ***Piper-class voices are commonly reported as faster than real time on CPU. Kokoro on CPU is slower and needs PyTorch.**

- ***Sentence-at-a-time synthesis parallelizes trivially. Updates after edits cost only the changed sentences.**

- ***Forced alignment of a long user recording is the most expensive local step; segment-level chunking keeps memory bounded.**

- ***Sample-rate conversion (Piper 22.05 kHz and Kokoro 24 kHz both going to 48 kHz) needs a proper resampler, `soxr` or FFmpeg, not linear interpolation.**

***Pronunciation:**

- ***A design change from Read-Aloud: substitutions apply per display token, not as regex over the whole string. That's what makes `word\_map` possible. Multi-word entries ("New York" → "Noo York") are allowed but must map to a contiguous run of display words.**

- ***Layers, applied in order: built-in number/unit normalizer → project dictionary → per-segment `spoken\_text` override.**

- ***The normalizer is where most quality issues hide ("563-hour," "0.000002 FPS," "MTH263," "x²"). Every change is listed in a diff report so the user can see what will actually be said.**

- ***Engine-specific phoneme markup (for example, Kokoro/misaki's inline phoneme syntax, which I believe exists but haven't verified) is optional and stays out of the shared format.**

***Emotion:**

- ***Piper and KittenTTS: speed and prosody variance only. "Steady" vs. "natural" is the whole range.**

- ***Kokoro: voice choice, speed and blends. It has no emotion parameter.**

- ***Instruct engines: natural-language direction, at GPU cost.**

- ***The honest default: deadpan and documentary narration work well on cheap engines. Dramatic acting needs CosyVoice-class models or a human recording.**

- ***Sentence-by-sentence synthesis resets prosody at every boundary. Optional flow groups (several segments in one unit) give smoother speech, at the cost of losing exact boundaries inside the group, which then need alignment. The default is one segment per unit.**


## ***10. Test cases**

1. ***Render 20 segments, edit one word in s012, re-render: exactly 1 synthesis call; the other 19 are cache hits (from the call log).**

2. ***Add a dictionary entry affecting 3 segments: exactly 3 calls.**

3. ***Switch the narrator voice and switch back: the second switch makes zero calls.**

4. ***Bump `postprocess\_version`: zero synthesis calls; all clips are re-trimmed.**

5. ***Lock take 2 of s013, then edit s014: s013 still uses take 2. Edit s013's text: the lock is dropped and a warning issued.**

6. ***Each pause category produces a run of exactly zero-valued samples of the configured length, plus the trim tail.**

7. ***Inserted silence boundaries in `narration.json` match the zero runs in the WAV to the sample.**

8. ***Supplied-audio audit: a recording with a 0.3 s pause where the plan said `deadpan` gets an `expected\_vs\_measured` warning, not an error.**

9. ***A trailing-silence test clip (engine padding of 400 ms) gets trimmed; the requested pause is what you hear.**

10. ***A three-speaker script assigns each segment to its cast voice; mixed-rate clips assemble into one 48 kHz track whose total length equals the sum of resampled clips plus silences.**

11. ***Loudness: each speaker's clips land within ±1 LU of the target ⏳ (target and tolerance to be agreed).**

12. ***A missing voice falls back to the narrator voice with a warning, never a crash.**

13. ***Clip-boundary claim test: the schema validator rejects any word with `src: exact` unless the word is* the whole segment and its time equals `voiced` (or an inserted boundary).**

14. ***Bang test: for s013, native/aligned/energy-onset starts are all reported. No fixed tolerance yet: record the spread on 10 renders, then set the threshold. (Inventing one now would be fake precision.)**

15. ***Word-map test: an anchor on "0.000002" resolves to the start of "zero" and the end of "two."**

16. ***Supplied audio with an ad-lib: the narrator adds "uh, anyway" — reported as `inserted`, and the surrounding script words still align.**

17. ***Supplied audio with a skipped sentence: the segment gets `status: missing` with no times, and downstream tools are warned.**

18. ***Audacity round-trip: export labels, nudge one by 120 ms, import. Exactly that segment's boundary becomes `src: manual`.**


## ***11. Failure handling, dependencies, licensing and milestones**

### ***Failure handling**

| Situation | Behavior |
| - | - |
| No TTS engine available here | Say so; offer the local command, or switch to supplied-audio/alignment-only modes |
| Engine error on one segment | Retry once, then a different voice from the same engine, then leave a **placeholder silence** of estimated length flagged **`missing\_audio`**, so assembly never blocks |
| Hosted provider down or over quota | Fall back to the local engine; record **`engine`** per segment, so mixed renders are visible |
| Aligner fails or scores low | Interpolate from segment boundaries and voiced edges; tag **`interpolated`**; list affected words |
| Transcript disagrees with the script | Reconcile: matched / substituted / inserted / deleted. The script stays the text authority; the audio stays the timing authority; disagreements go in the report |
| Clipping or wrong sample rate in user audio | Convert and warn; never silently change the duration |
| Delivery direction unsupported | Nearest supported parameters, plus a **`delivery\_unsupported`** warning |

### ***Dependencies**

- ***Core (required): Python 3.10+, `numpy`, `soundfile`, FFmpeg.**

- ***Local TTS: `sherpa-onnx` (I believe Apache-2.0; verify) with Piper/Kitten voices.**

- ***Optional: `kokoro` (+ PyTorch, misaki, espeak-ng), `faster-whisper`, `whisperx` or `ctc-forced-aligner`, `soxr`, `pyloudnorm`.**

- ***Everything heavy stays optional, so the core works on a plain CPU machine.**

### ***Licensing (separate rights per item)**

- ***Engine/runtime: sherpa-onnx (believed Apache-2.0). Note: the actively maintained Piper fork, `piper1-gpl`, is GPL-3.0. Using sherpa-onnx to run Piper voices avoids bundling that runtime.**

- ***Voice weights and training data: Piper's docs say each voice's MODEL\_CARD is authoritative, and they vary. Several are CC0; others reportedly carry restrictive terms (Lessac is reported to have a "Blizzard" research license). Kokoro is Apache-2.0 per its model card, as I understand it. The Skill should show each voice's license in `cast.json` and warn on non-commercial or unknown terms.**

- ***Aligner weights: see the MMS warning in §6.**

- ***Consent: the Skill doesn't clone a real person's voice without explicit confirmation that they consented.**

### ***Milestones**

| \# | Scope | Done when |
| - | - | - |
| **N0** | **`narration.json`** schema + golden DOOM fixtures + **`scriptkit.py`** shared with Round 1 | Story Director and Movie Builder designs can reference it |
| **N1** | **`assemble.py`** + **`measure.py`** + labels, from **any supplied WAV clips** (no TTS) | Tests 6, 7, 9, 10, 13 pass |
| **N2** | sherpa-onnx Piper/Kitten + disk cache + casting | Tests 1–5, 11, 12 pass |
| **N3** | Kokoro adapter with **`model`** word times | Tests 14 (recorded spread), 15 |
| **N4** | Supplied audio: transcribe, align, reconcile | Tests 8, 16, 17 |
| **N5** | Pronunciation normalizer + **`word\_map`** + diff report | DOOM numbers spoken correctly; captions keep digits |
| **N6** | Selective in-clip alignment + critical-word onset check | **`importance: critical`** segments always get a second timing opinion |
| **N7** | SRT/VTT + Audacity import | Test 18 |
| **N8** | Instruct/hosted adapters (CosyVoice, HF) | One emotional line rendered with a recorded comparison |


## ***12. Recommended changes to the Round 1 plan**

***These should cause Round 1 to be revised:**

1. ***One segmenter, shipped twice. Put the segmenter in `scriptkit.py` with a version string and golden test files. Identical copies go in Story Director and Narration Studio. Otherwise the same story produces different segment IDs depending on which Skill ran first. Read-Aloud's newline, abbreviation and 600-character rules are a sound starting point.**

2. ***Split attribution from dialogue mid-sentence. `"Bang," said the sound effects guy.` is two speakers in one sentence. Round 1 has to emit two segments; Narration Studio renders them with a tight join (`pause\_after: none`).**

3. ***Move `spoken\_text` out of Round 1's provisional list and into Narration Studio. Story Director only flags `needs\_spoken\_form: true`. Round 1's anchors stay on display words, and `word\_map` resolves them.**

4. ***Give delivery notes some structure. Free text can't drive Piper. Add `pace: slower|normal|faster` and `energy: flat|normal|high` alongside the free text, which instruct engines use.**

5. ***Add voice hints to characters. Round 1 characters have `visual\_anchor`; add `voice\_hint` (register, age range, accent). Narration Studio turns that into `cast.json`.**

6. ***Define pause categories after trimming, and add `paragraph`. Round 1's 0.15/0.4/0.8/1.5/2.0 s values hold up. "Pause" means heard silence, not the gap between clip files.**

7. ***Derive `needs\_word\_timing` automatically. Any shot anchored to a word other than word 1 at `edge: start`, or any `importance: critical`, marks that segment. Narration Studio does no word timing for the rest.**

8. ***Adjust Round 1's text-preservation test to check display text only. Spoken text is allowed to differ.**

9. ***Add an optional `flow\_with\_next` hint for prose where prosody across sentences matters more than exact boundaries.**


## ***Top three risks**

1. ***The chat sandbox may not run TTS at all (no weights, no network, no GPU). If so, inside ChatGPT this Skill is mainly a preparation and alignment tool, and synthesis happens locally. That changes the user experience a lot. Find out first.**

2. ***Short and non-lexical utterances ("Bang," "Hm," sound effects said aloud) are where `model` and `aligned` timing are least reliable, and they're the most important for comedy. The energy-onset check helps, but needs real measurements.**

3. ***Aligner model licensing could rule out the best aligner for monetized content. Check before N4.**


## ***Ideas Worth Revisiting in Round 4**

1. ***Who owns `scriptkit.py`? A shared file in each Skill, a fourth tiny "shared contract" package, or Story Director as the owner with Narration Studio as a consumer.**

2. ***Pause negotiation loop. In generated mode, Movie Builder could request "make the deadpan after s013 0.5 s longer" and only the assembly reruns, with no synthesis. Who is allowed to change pause lengths: the plan, overrides, or Movie Builder?**

3. ***Who resolves anchors to seconds? Narration Studio now has everything needed: segments, words, `word\_map` and silences. It could export a ready-made `anchors\_resolved.json`, which would keep Movie Builder simpler.**

4. ***Who owns captions? Narration Studio can make standalone SRTs, but burned-in caption styling, line breaks around visuals, and safe zones belong to Movie Builder. Possibly: Narration owns caption timing*, Movie Builder owns layout*.**

5. ***Flag-while-watching. Read-Aloud's F9 anchor model (text plus context, fuzzy re-binding) could become the shared review format across all three Skills.**

6. ***Read-Aloud as a front-end. If you own the repo: add a "pipeline export" that writes `narration.json`-compatible segment timings (with trim info and segment IDs) alongside its WAV. Then proofreading and voice-tuning can happen in that UI.**

7. ***Takes as a creative tool. Should Story Director be able to ask for three takes of a punchline and let Movie Builder or the user choose?**

8. ***Music and sound effects. Does ducking metadata (`speech\_active` intervals) come from Narration Studio? It already knows exactly where speech is.**

9. ***Overlapping dialogue and interruptions. v1 forbids overlaps. Decide whether v2 supports a negative `pause\_after` (overlap) and how captions show it.**

10. ***Engine-agnostic delivery vocabulary. If `pace`/`energy` work, the same small vocabulary could drive camera pacing in Movie Builder (low energy → slower pushes), making `style.yaml` the one place tone is set.**

***Ready for Round 3 when you are.**

***10 citations**

*![]()![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py")![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/hexgrad/kokoro/issues/150")![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/remsky/Kokoro-FastAPI/blob/master/api/src/inference/kokoro\_v1.py")**···**

***[kokoro/pipeline.py**](https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py)

***[https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py**](https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py")](https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py)**[github.com**](https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py)

***[api/src/inference/kokoro\_v1.py**](https://github.com/remsky/Kokoro-FastAPI/blob/master/api/src/inference/kokoro_v1.py)

***[https://github.com/remsky/Kokoro-FastAPI/blob/master/api/src/inference/kokoro\_v1.py**](https://github.com/remsky/Kokoro-FastAPI/blob/master/api/src/inference/kokoro_v1.py)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/remsky/Kokoro-FastAPI/blob/master/api/src/inference/kokoro\_v1.py")](https://github.com/remsky/Kokoro-FastAPI/blob/master/api/src/inference/kokoro_v1.py)**[github.com**](https://github.com/remsky/Kokoro-FastAPI/blob/master/api/src/inference/kokoro_v1.py)

***[Is it possible to get word timings along with the results?**](https://github.com/hexgrad/kokoro/issues/150)

***[https://github.com/hexgrad/kokoro/issues/150**](https://github.com/hexgrad/kokoro/issues/150)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/hexgrad/kokoro/issues/150")](https://github.com/hexgrad/kokoro/issues/150)**[github.com**](https://github.com/hexgrad/kokoro/issues/150)

***[Captioned Speech & Word Timestamps | remsky/Kokoro-FastAPI | DeepWiki**](https://deepwiki.com/remsky/Kokoro-FastAPI/7.4-captioned-speech-and-word-timestamps)

***[https://deepwiki.com/remsky/Kokoro-FastAPI/7.4-captioned-speech-and-word-timestamps**](https://deepwiki.com/remsky/Kokoro-FastAPI/7.4-captioned-speech-and-word-timestamps)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAIAAAAlC+aJAAAACXBIWXMAAAsTAAALEwEAmpwYAAADDUlEQVRoge2aUUhTURiAjy3uVTfGcN6wVi56MO+wmlDZQ07otSKclCTqUzXnkz05qjc3V1FPBjLUlwo0NyWqh0Ax0iC1B3vIDQpDazPitnW93Svc2aCHS2Mk9z50fj0I53sa5+z+//l2dv5zuPcWWW0c2snsIj0AXKgAaagAaagAaagAaagAaagAaagAaagAaagAaXYDxpJEBaF1hBBCpVabGTCyAWAzIIlCvacuHk8sLLw/cfKoJApQkY0BEJBEoZhlnz1/Mf16iuer3e5j83NvY2PjWhd+fGNwBSRR8Pn8X78snT93trC9ydsofE+2trVLooiZwhiAGWho8DAMs7mdYRiPx4PQBn4KAwAEcrmcXpeqqvjxjYGsQpthWTb/uaBGIcDbgVu7D3i9jQghSRTyNUpV1Rs3b0miALU2AATEtTW9LntZ2Y90OjY2PjPzRqtRDMOEgj3xeMLrvQBSo0xsMdaOwxabn45HN37nTtXVFS5lRVGWlj5zXHlpSYmL5ysrKwuv4rjy5uZLjv0HYtERzAEAzIDVxvWGghbLnuHhEa1lYHDIYrG4XHzVYZeiKHoXHqmpwc8OswasNs5qM7e0XPY0nHHXHr929YrVxllt3KePib6+ByAp9ACuQjPTc/lSo/FLlmFT/APMDGh1Jhy+rao/ZVn+W2cEhFCn3w+SQg+Ys1BrW3symQoEuhmGMZvNoWBPMpmamJiUZdnh2Kd3YWp1FT97Eeaeov3wgUC33hey2ez8/Du73c7z1fnGdCYTDt+5f+8u/o4GMANOp1OvK5vNHjxUVV9/2uXiOzo605kMQmhgcKjcbgcZPQJZxAZnodHR6LfUijbQSKQ/Eunf63DmW0DY2rNQ4SatDVpR1mGfiwL8hUwmE36Q/wZA4MPiol7X8vIKfnxjAM5CkxMvp15N19a6Kyoq8u2zs3Pepoux6JOtfpCOW0Y1tLO+z+cP9QYRQl1d1x8/erg99yZgBDQKj8fb9gYDpAARdvydOSpAGipAGipAGipAGipAGipAGipAGipAGipAmj/OSAiFyDzwdgAAAABJRU5ErkJggg== "Favicon for https://deepwiki.com/remsky/Kokoro-FastAPI/7.4-captioned-speech-and-word-timestamps")](https://deepwiki.com/remsky/Kokoro-FastAPI/7.4-captioned-speech-and-word-timestamps)**[deepwiki.com**](https://deepwiki.com/remsky/Kokoro-FastAPI/7.4-captioned-speech-and-word-timestamps)

***[Word level timestamps**](https://github.com/hexgrad/kokoro/pull/46)

***[https://github.com/hexgrad/kokoro/pull/46**](https://github.com/hexgrad/kokoro/pull/46)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/hexgrad/kokoro/pull/46")](https://github.com/hexgrad/kokoro/pull/46)**[github.com**](https://github.com/hexgrad/kokoro/pull/46)

***[docs/VOICES.md**](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md)

***[https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md**](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md")](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md)**[github.com**](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md)

***[docs/VoiceLicenseReview.md**](https://github.com/Sufiyan-S7/Zen/blob/main/docs/VoiceLicenseReview.md)

***[https://github.com/Sufiyan-S7/Zen/blob/main/docs/VoiceLicenseReview.md**](https://github.com/Sufiyan-S7/Zen/blob/main/docs/VoiceLicenseReview.md)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/Sufiyan-S7/Zen/blob/main/docs/VoiceLicenseReview.md")](https://github.com/Sufiyan-S7/Zen/blob/main/docs/VoiceLicenseReview.md)**[github.com**](https://github.com/Sufiyan-S7/Zen/blob/main/docs/VoiceLicenseReview.md)

***[Update URLs in model cards · rhasspy/piper-voices at e9ef9dd**](https://huggingface.co/rhasspy/piper-voices/commit/e9ef9dd26adb6a40a9b47198817cd8e96d01e7cb)

***[https://huggingface.co/rhasspy/piper-voices/commit/e9ef9dd26adb6a40a9b47198817cd8e96d01e7cb**](https://huggingface.co/rhasspy/piper-voices/commit/e9ef9dd26adb6a40a9b47198817cd8e96d01e7cb)

*[![](data:image/png;base64,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 "Favicon for https://huggingface.co/rhasspy/piper-voices/commit/e9ef9dd26adb6a40a9b47198817cd8e96d01e7cb")](https://huggingface.co/rhasspy/piper-voices/commit/e9ef9dd26adb6a40a9b47198817cd8e96d01e7cb)**[huggingface.co**](https://huggingface.co/rhasspy/piper-voices/commit/e9ef9dd26adb6a40a9b47198817cd8e96d01e7cb)

***[Issues · OHF-Voice/piper1-gpl · GitHub**](https://github.com/OHF-Voice/piper1-gpl/issues)

***[https://github.com/OHF-Voice/piper1-gpl/issues**](https://github.com/OHF-Voice/piper1-gpl/issues)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/OHF-Voice/piper1-gpl/issues")](https://github.com/OHF-Voice/piper1-gpl/issues)**[github.com**](https://github.com/OHF-Voice/piper1-gpl/issues)

***[TTS Dataset Licensing and Voice Consent | Mahimai**](https://mahimai.ca/learn/100x/tts/tts-dataset-licensing)

***[https://mahimai.ca/learn/100x/tts/tts-dataset-licensing**](https://mahimai.ca/learn/100x/tts/tts-dataset-licensing)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAFS0lEQVR4nO2bMU8jVxDH59l5s1BEwkhp7ySofYoUHU2KKIeOMlCkSAqo0h18A6iC8gXOriNxUqBIkWuxTHRNClCkE7TB0qWNdOaSwnrz2J0Ufose6919u/au1yT+SRReZpeZ2Xmz/3leAObMmTPn/wwR7VbtQ1UQ0TEQERPRadXOTJPBYPCIiK6JiMMEMBG9V0o1q3aubIho24r5XgKYiFhrvV+1k2VBRMfReAURcYztBSKuTd3DkhgMBo/q9fpbAGhEf1dLOOepqYZn5bpWPkS0W6/X30FM8ADJCQAAAGbuElGrFM+mgGnuL9NskpZAlJ7v+18uLi7+WYxr5aKUagoh3kDCXQ8RQqynVoDFSr1ef0dE25O7Vy5a630hxCWkB9+TUjaklGdZExByRETHE/hXGsy8RESnzPy9w7SNiKtCiBuA7EsgSt/3/U9nZUlorZ8xc9dlx8xbnue9to/lrYCQhlkSlctoImplCL4npWxEgyei1rgVYNNBxI0Jr5EbZl7SWp8CwFOH6QkifmsfsJvkuBVg85yI3k9TMyilNrXWfXAHvxMNnohadpMsIgEAAA1m7k5DRpsAfnGY9Xzff4yIr8IDSqkmEV0DwAvbsIglEKUUGW1K/ncAWHGYjpS81no/6elQRgKGFxZiXUp5VsS1lFKbGe46wLDk7911c15S0jpFLYERipLRRHScIfh+tOQtQRQbvBDiABE3SqsAi7FktJngfoWcJZ/hvD4zf+F53hVAcU0wjdwymoi2zQTnCn7PDl5rve84r4OIy2HwACX2gARGGlQUI7W/cVzn3l3MUi1CiAMp5aF9TCm1Oe0EAESct5zJNMFBRHildfi0v2f604tcS0AIcSCEOMhzTgwNIcSlLaOJaDfDBAcwLPkNgKH+J6LrSPAXAHBifR4peTM03emB3D1ASnnIzFt5z4vhJRGdZtm0gOFdfIKILSvwLtwv+TYirjHzD+bzXlSiWwry7ryxmqDnea99338MAL1xzrd4bn7S6CDiMgAAEZ3HBA7MvIWIu8a3qzBZtk2SgvxoXM/NY201Y9Malz1mfkNE5xCv+3tSys/C2T4kWvIpCrKdqwKY+SZ6zHT1vTzXyUAfAHYA4CvTG+KCP7E3NuKIK3lDW0rZQMTdQnQAIraY+YlxfFL6APAHABxB8vIYmfKiJCjIu8DDxI29BKKYsls2Tc21rtNoQPKY61SVCZqgLaXcj6uWwpUgIm4U8KiM4wQRV9OCj1GQI3fcRinVLEUKSykPhRDrBV5yL6OCPDIfUwM39i0hxGVhSyCKlPKMmRsZZ/gkYlWcTeRrr8RSDzGj9Y8w5o7QhzzGQogbRFyF++osKyMqLor1tddPrjtuFOC5aYx3inMa02D4qNzJah/O6mk2ptl+7gocYDgvJO0hlrYEoiDiK6XUW8fA0xdCfJ22k6SUatZqtc3b29vvXHsM5vuCn5k5ccaYSgWEeJ53ZWRtJ+bXF1LKlbTgmXkpCIIPUsrDtOCtb4m64BiwppqAkJhHZRsR19LKGGDYU1x3XSnVNOWeSYvkWgLM/Hce+zSklIda69+CIPg4+o3NJNRqtU+Ys29xTK0HxFHUrvEkVLIEyiQIgr/y2P/nEpCXeQKqdqBqciWgVqv9U5YjVTGvgBy2J7Pw2HIRBEGugS1rApxbUA8VlxByzuMPnIu0CnDO4w+cHURci01Alnl8VllYWHDNK21EFOG7BCNLoMg3O2aMju/7o3sI1rvz18y8VJFzhWH2Auz/CUh/g80YzeTrr+NgJyDTW2uz8LZnkVi7QQ++mufMmTOndP4F/PRETA8o4d8AAAAASUVORK5CYII= "Favicon for https://mahimai.ca/learn/100x/tts/tts-dataset-licensing")](https://mahimai.ca/learn/100x/tts/tts-dataset-licensing)**[mahimai.ca**](https://mahimai.ca/learn/100x/tts/tts-dataset-licensing)

*![]()**$0.9319,837 tok**

*![](data:image/png;base64,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 "Favicon for x-ai")**Grok 4.7**

***Reasoning**

***Narration Studio is the skill that either builds the audio or measures it. I’ll check which timing claims are still true before writing the plan, so clip-boundary timing does not get described as word timing.**

***Searched for Kokoro TTS Python word timestamps start\_ts end\_ts 2026 sherpa-onnx OfflineTts word-level timestamps5 results**

***Reasoning**

***Narration Studio owns the sound and the measurements. It does not direct, and it does not render. Clip boundaries are not word times.**

## ***Verdict**

***`narration-studio` is the timing authority after audio exists, and only then. Standalone, it reads a text aloud, or aligns a recording the user already has. With the other skills present, it still does only that, and writes one sidecar they can trust.**

***Steal four ideas from [Read-Aloud-Main](https://github.com/steveonw/Read-Aloud-Main): cache the clip, insert silence as samples, record offsets while concatenating, and keep a pronunciation string separate from the script. Do not fork the app. Its own spec puts word timing and emotional delivery out of scope, and the cooperative format is not an Audacity label track.**

***Nothing below is implemented. Schema names, pause lengths, and the engine order are proposals, version `narration-studio/0`.**

## ***1. Name and trigger**

***Name: `narration-studio`  
Folder: `narration-studio/`**

***Description:**

***Create or measure narration audio. Use to read a script aloud, assign voices, insert pauses, regenerate one sentence, align a user-supplied MP3 or WAV to a script, or export sentence and word timing. Use for audiobook, narration, dialogue, and explainer reads. Do not use for storyboarding, shot plans, image prompts, FFmpeg, caption burning, or exporting an MP4. Sentence timing is not word timing.***

***The negative list is what keeps this skill from swallowing the other two. "Align this MP3" and "read this aloud" have to be in the description, or the host will not select it.**

## ***2. Standalone workflows**

***This skill is done when no other skill is installed. A person gets a WAV, a sidecar, and a straight answer about what was not timed.**

| Request | Result | Refusal |
| - | - | - |
| "Read this." | **`narration.wav`**, sentence timings, cached clips | A shot list |
| "Two voices. Narrator, and Kevin for the Bang lines." | Voice table, one clip per utterance | Invented emotion acting |
| "Leave a beat after Bang." | Silence inserted and measured | A pause "performed" by the voice |
| "Here is my MP3 and the script." | Alignment sidecar, no resynthesis | New pauses edited into their recording |
| "Time the word fourteen." | A word span inside the sentence, or an explicit failure | The sentence's start time pretending to be the word |
| "Change one sentence." | One clip regenerated, the rest reused | A full resynthesis |
| "Export labels." | Optional Audacity labels, marked sentence-level | Those labels as the contract |
| "Now storyboard it." | The audio job only, plus one line that direction is out of scope | A plan.json |

***If the host cannot run a TTS engine and the user did not supply audio, the skill stops. It may write a voice sheet and a lexicon. It must not describe a WAV it did not write.**

***Two questions, maximum: which voice map, and whether a supplied file is the master recording or a scratch read. Do not ask for a codec.**

## ***3. Cooperation**

***This skill calls neither of the others. It reads an optional plan and writes files either of them can ignore.**

```
***`script, or a director plan`**

`        │`

`        ├─ ***generate: clips + inserted silence + measure`**

`        └─ ***align:    user audio + script, measure only`**

`                │`

`                ▼`

`        ***narration.wav + narration.json`**

`                │`

`                ├─ ***Movie Builder resolves anchors against this file`**

`                └─ ***Story Director is not called back`**
```

***A slower retake does not need a new director pass. The director's anchors stay. This sidecar is replaced.**

***What it will read from a Story Director plan, if one is offered**

- ***Verbatim segment text, speaker, and `do\_not\_rewrite`.**

- ***A pronunciation flag, if Round 1 adds one. Absent means the lexicon may apply.**

- ***Pause requests. They are requests. They are not proof that silence exists.**

- ***A list of anchors that need word times. It should not have to parse shots to discover them.**

***What it will not read**

- ***Camera, prompts, budgets, or the essay about why a beat is funny.**

- ***Seconds, if a previous tool wrote them back into the plan. Those are stale on sight.**

***What Movie Builder may rely on**

- ***The WAV this skill names, at the sample rate it names. Not the user's MP3. Not an Audacity file.**

- ***Clip sample spans, for anything that only needs a sentence boundary.**

- ***Silence events with ids, durations, and `intentional`.**

- ***Word spans, when `word\_timing` is `native` or `aligned`.**

- ***The absence of word spans. Absence means "not measured." It does not mean "divide the clip by word count."**

***What a retake guarantees**

- ***Unchanged clips keep their sample counts.**

- ***Changed pauses do not resynthesize speech.**

- ***Word offsets inside a clip stay valid for that clip file. Absolute positions in the movie move, and the sidecar is rewritten at concat time.**

## ***4. `SKILL.md` structure**

***Under 500 lines. The scripts do the measuring. The body is not allowed to estimate a duration the script did not print.**

```
***`narration-studio/`**

`├── ***SKILL.md`**

`├── ***agents/openai.yaml`**

`├── ***references/`**

`│   ├── ***schema.md`**

`│   ├── ***engines.md`**

`│   ├── ***pause-rules.md`**

`│   ├── ***alignment.md`**

`│   └── ***shared-contract.md      \# provisional until Round 4`**

`├── ***scripts/`**

`│   ├── ***synthesize.py           \# proposed`**

`│   ├── ***assemble.py             \# proposed`**

`│   ├── ***align\_script.py         \# proposed`**

`│   └── ***validate\_narration.py   \# proposed`**

`└── ***assets/`**

`    └── ***lexicon.example.json`**
```

***Body, in order:**

1. ***Boundaries. Never invent timestamps. Never treat a clip start as a word start. Never insert silence into supplied audio. Never rewrite the script. Never storyboard. Never render video.**

2. ***Capability check. Engine present, aligner present, or user audio present. If none, stop.**

3. ***Pick the mode. Generate, align, regenerate one clip, or add a lexicon entry.**

4. ***Build the spoken string. Lexicon after the script is copied. Script text stays untouched.**

5. ***Synthesize or align. Read `references/engines.md` or `references/alignment.md`, not both.**

6. ***Assemble and write the sidecar from sample counts. Read `references/pause-rules.md` only in generate mode.**

7. ***Word times, only if asked. A reveal list, a captions request, or an explicit "time this word." Otherwise leave `words` empty.**

8. ***Validate. No word span may fall outside its clip. No supplied-audio job may contain `requested\_beat`.**

***Load the schema only when writing or checking JSON. Do not load a DOOM example on an ordinary audiobook run.**

## ***5. Scripts and references**

***Instruction-only is a failed narration skill. The product is the measured file.**

| Script | Job | Does not |
| - | - | - |
| **`synthesize.py`** | One clip, cache lookup, engine call | Concatenate, insert pauses |
| **`assemble.py`** | Concatenate cached WAVs and silence, write sidecar from the running sample count | Call an engine |
| **`align\_script.py`** | Forced-align known text, emit words and measured silences, halt on mismatch | Transcribe and hope |
| **`validate\_narration.py`** | Reject interpolated words, MP3-as-authority, and reveals whose time equals the clip start | Judge the performance |

***`references/engines.md` holds the engine order and the emotion limitation. `references/alignment.md` holds the mismatch rule. `references/pause-rules.md` owns the only millisecond table in the project. `references/shared-contract.md` starts with "Provisional until Round 4."**

***No model weights in the skill folder. No ffmpeg binary. WAV writing does not need ffmpeg. An MP3 preview is optional and disposable.**

***If code cannot run, say so, and do not emit a sidecar full of guessed times.**

## ***6. Engines and alignment**

***Generate, in this order**

1. ***Local Kokoro, Python pipeline, if the import and the voice file are already there.**

2. ***Local Piper, if Kokoro is not.**

3. ***A hosted engine only after the user accepts a cost cap. Same cache, same assembler. Measure the file that came back. Do not trust a vendor duration header.**

***Do not download weights silently. Do not bundle them. Kokoro-82M is Apache-2.0; check each voice pack at install. Piper's code is MIT; voice licenses differ. Confirm before shipping a voice.**

***Do not use the Read-Aloud browser build. Verified from that repo, not proposed: it synthesizes a sentence, caches it, concatenates, and inserts a known number of silent samples. Labels are the running sample count. The pronunciation dictionary rewrites what is spoken. MP3 export is 64 kbps, and labels are computed before that encode. Pitch is a resample. `SPEC.md` says word-level timing and emotional delivery are out of scope. Its Kokoro notes say that path was not exercised past the WASM boundary. The launcher and the browser worker stay there.**

***Word times, a different layer**

***Sherpa-onnx's TTS API still does not return them. Issue [\#3705](https://github.com/k2-fsa/sherpa-onnx/issues/3705) was open as of its last update on 9 July 2026. That was a search result, not a claim that nobody has merged anything since.**

***Kokoro's Python pipeline is reported to expose token `start\_ts` and `end\_ts`, and a public gist derives those from `pred\_dur` with an explicit uncertain frame offset. That is third-party documentation. It has not been run here. Treat those fields as a candidate.**

***A candidate is accepted only if the token strings map onto the script words one for one. `fourteen` may pass. `0.000002`, `DOOM`, and a lexicon substitution often will not. On a failed map, align that clip. Do not repair the map by hand inside the model.**

***Align**

***Forced alignment of the known script. WhisperX or stable-ts. Raw Whisper timestamps, then fuzzy matching, are the drift path, especially on numbers and on `Bang`.**

***Align a clip when a reveal falls inside it, or when the user asked for word captions. Align a supplied recording always. Sentence-only generate jobs do not need an aligner at all.**

***Free transcription is only the mismatch report. It is not the timing path.**

## ***7. Caching**

***The cache stores speech, not the movie.**

***Key: engine, model id, model-file hash if local, voice, speed, sample rate, and the exact `spoken\_text`.**

***Not in the key: the pause after the clip, the output filename, the director's shot id.**

***So a one-word edit resynthesizes one clip. A longer beat resynthesizes nothing. A voice change misses every clip for that speaker. A lexicon change changes `spoken\_text`, so it misses too. Store the script text beside the clip so a human can see why the key differs.**

***Pitch is not a cache field because pitch is out of v1. Read-Aloud's pitch control changes duration. Leaving it out is the point.**

***The final WAV is rebuildable from clips plus the silence list. It does not need its own intelligence. Write it at 24 kHz mono if that is what the engine emitted. Do not resample to 48 kHz in this skill. If a later skill resamples, it owns the new file and must not reuse these sample indexes as if they still applied.**

## ***8. Timing schema**

***Two layers, and the file must say which one a consumer is looking at.**

- ***Clips are sentence or utterance spans. On a generated job their sample counts are exact, because `assemble.py` counted them. They say when the sentence started. They do not say when `fourteen` started.**

- ***Words exist only after a native map was checked or an aligner ran. If neither ran, `words` is `\[\]` and `word\_timing` is `absent`. Nobody fills the gap by division.**

- ***Silences are events with ids. Generated beats are intentional. Gaps found in a user recording are measured, and `intentional` is null. This skill does not guess which of the user's pauses were artistic.**

```
***`\{`**

`  ***"narration\_version": "narration-studio/0",`**

`  ***"mode": "generated",`**

`  ***"audio": \{`**

`    ***"file": "narration.wav",`**

`    ***"sample\_rate": 24000,`**

`    ***"channels": 1,`**

`    ***"sample\_count": 1780800,`**

`    ***"derived\_from": null`**

`  ***\},`**

`  ***"script\_sha256": "\<hash of unmodified script, or null\>",`**

`  ***"voices": \[`**

`    ***\{"id": "narrator", "engine": "kokoro", "voice": "af\_heart", "speed": 1.0, "emotion\_applied": false\}`**

`  ***\],`**

`  ***"clips": \[`**

`    ***\{`**

`      ***"id": "clip\_03",`**

`      ***"speaker": "narrator",`**

`      ***"script\_text": "The first frame took fourteen hours.",`**

`      ***"spoken\_text": "The first frame took fourteen hours.",`**

`      ***"sample\_start": 434400,`**

`      ***"sample\_end": 491520,`**

`      ***"word\_timing": "aligned",`**

`      ***"covers": \[\{"segment": "seg\_03", "text": "The first frame took fourteen hours.", "nth": 1\}\]`**

`    ***\}`**

`  ***\],`**

`  ***"silences": \[`**

`    ***\{`**

`      ***"id": "sil\_9",`**

`      ***"kind": "requested\_beat",`**

`      ***"intentional": true,`**

`      ***"after\_clip": "clip\_03",`**

`      ***"after\_anchor": \{"segment": "seg\_03", "text": "hours.", "nth": 1\},`**

`      ***"sample\_start": 491520,`**

`      ***"sample\_end": 517920,`**

`      ***"duration\_ms": 1100`**

`    ***\}`**

`  ***\],`**

`  ***"words": \[`**

`    ***\{`**

`      ***"text": "fourteen",`**

`      ***"script\_text": "fourteen",`**

`      ***"clip\_id": "clip\_03",`**

`      ***"sample\_start": 465600,`**

`      ***"sample\_end": 481200,`**

`      ***"method": "forced\_align",`**

`      ***"anchor": \{"segment": "seg\_03", "text": "fourteen", "nth": 1\}`**

`    ***\}`**

`  ***\],`**

`  ***"pause\_requests": \[`**

`    ***\{"anchor": \{"segment": "seg\_03", "text": "hours.", "nth": 1\}, "honored": true\}`**

`  ***\],`**

`  ***"warnings": \[\]`**

***`\}`**
```

***Seconds are a derived view. Sample indexes into `narration.wav` are the authority. On a supplied MP3, decode once, set `derived\_from` to the original filename, and never claim those indexes apply to the MP3 bytes.**

***`covers` is how a director segment survives a different split. A director paragraph may become three clips. A clip may cover one director segment. The link is the verbatim span, not an assumption that `seg\_03` is one WAV.**

***Optional SRT is a convenience export. Sentence cues if words are absent, and the file should say so. Word cues only from `words`. Spoiler suppression is not applied here. A "comedy-safe" subtitle would require this skill to interpret the shot plan.**

***Optional Audacity labels are the same sentence spans, for a human. They are not what Movie Builder reads.**

## ***9. Performance, pronunciation, emotion**

***Pauses. Insert samples. Do not ask the voice to leave air. A request that lands on a clip boundary becomes silence after that clip. A request that lands in the middle of a sentence splits the clip there, because a pause is a break in delivery by definition. A reveal is not a break. Do not split a sentence just so `fourteen` gets its own file.**

***Proposed lengths, owned only by `references/pause-rules.md`: a sentence gap of 250 ms, a paragraph gap of 500 ms, `beat` of 900 ms, `long` of 1400 ms. A director range is a hint and is clamped to 400–2000 ms. These numbers are untested.**

***Pronunciation. `script\_text` is what the author wrote and what anchors match. `spoken\_text` is what the engine received. The lexicon may turn `0.000002` into words. It must not change the script copy. Cache the spoken form. A span marked literal gets no substitution. Decimals must survive the sentence splitter. A split inside `0.000002` is a broken clip, not a style choice.**

***Emotion. Store the director's delivery note. Kokoro and Piper will ignore it. Set `emotion\_applied` to false and put that in `warnings` once, not once per line. Two voice ids are the v1 performance plan: a documentary narrator, and a second speaker for lines the script actually assigns. "Increasingly frustrated Kevin" will not be synthesized. CosyVoice-style instruction voices are a later engine, not a dependency and not a promise.**

***Supplied audio. The recording is the performance, including its bad pauses. Do not insert, delete, or duck. If the director asked for a beat the speaker did not leave, `honored` is false and the reason is `supplied\_audio`. Measured silences still go in the sidecar, with `intentional` null, so a later shot can use one if it is long enough. This skill does not decide that. It only reports the duration.**

## ***10. Tests that would have to pass**

***These are fixture tests for scripts that do not exist yet. No claim that they pass.**

1. ***One edited sentence. Only that clip's hash changes. Earlier clip bytes are identical. Later clips keep their durations and move their `sample\_start`.**

2. ***Pause edit only. No engine call. The silence event's sample count changes. Word offsets relative to their clip do not.**

3. ***Two voices. Different cache keys. Speaker ids survive assembly. An unlabeled line stays narrator rather than being cast.**

4. ***Lexicon. Script and anchor remain `0.000002`. Spoken text differs. The sentence splitter does not cut the number.**

5. ***The reveal. The `fourteen` span starts after the clip starts. A sidecar where that word's time equals the clip start fails, even if the sentence time is perfect.**

6. ***Native-timestamp miss. A token map that cannot find `0.000002` either aligns that clip or marks the word absent. It does not guess an offset.**

7. ***Supplied mismatch. An ad-lib or an old draft produces a diff and no word times on the mismatched span. Reveals are not snapped onto whatever was recognized.**

8. ***Supplied purity. A user WAV yields no `requested\_beat`, and no clip with an engine field.**

9. ***Empty words. A generate run with no reveal list has `words: \[\]`. It does not contain evenly spaced fake words.**

10. ***MP3 authority. A preview MP3 exists only if requested, and `validate\_narration.py` rejects it as `audio.file`.**

## ***11. Failures, dependencies, milestones**

| Situation | Behavior |
| - | - |
| No engine, no user audio | Stop. Voice sheet only. No invented file. |
| Weights not downloaded | Ask, state that they are not bundled, wait. |
| Hosted call would exceed the cap | Do not call. Local engine or stop. |
| Script and recording disagree | Diff the spans. Time only the spans that match. Do not time a reveal across a mismatch. |
| Aligner missing, reveal requested | Sentence times if this skill generated them. Word status **`absent`**. Do not interpolate. |
| Pause requested on supplied audio | Record **`honored: false`**. Do not edit the waveform. |
| Same anchor text twice | Require **`nth`**. If still ambiguous, do not attach a word time. |
| User asks for timestamps before audio exists | Refuse. A pause request is not a timestamp. |

***Dependencies, in order of need: Python, a WAV writer, one TTS engine or a user file, an aligner only for the word-level and supplied-audio paths. ffmpeg is unnecessary here. Read-Aloud is MIT if a sentence splitter is copied; keep the notice, and do not copy the UI.**

***Milestones**

- ***M1. Assemble three already-made WAVs with one inserted beat. Sidecar sample counts must reconstruct the file length exactly.**

- ***M2. One local voice, cache on, the edited-sentence test.**

- ***M3. Lexicon and a second voice. The decimal-split test.**

- ***M4. Supplied recording. Mismatch halt. No inserted beats.**

- ***M5. The `fourteen` test, native candidate first, aligner if the map fails.**

- ***M6. One hosted engine behind the same assembler, cap on, measured after download.**

***M1 is the contract. M5 is the one that protects the joke. A skill that passes M2 and fails M5 is a good audiobook tool and an unfit partner for this movie.**

## ***12. Changes to the Round 1 plan**

***Round 1 is right that anchors beat invented seconds, and that a reaction is conditional. Narration Studio cannot implement that plan as written without guessing. Seven revisions:**

1. ***Director segments are not audio clips. Keep creative segments. Add the rule that another skill may split or merge them. The link is a verbatim span, not "one segment, one file."**

2. ***Add `timing\_requests`. Anchors that need word times, and pause requests, in one list. This skill should not parse `shots` to learn what to measure.**

3. ***Split pause requests in two. `after\_segment` inserts silence after a clip. `break\_after\_word` is allowed to split a clip. A `not\_before` word is never a split point.**

4. ***Director ranges become hints. This skill owns the millisecond table. A requested range is clamped, not obeyed as a fact about the performance.**

5. ***Add `pronunciation: literal` on a span. "Speak as written" currently has nowhere to live. Without the flag, a helpful lexicon will rename the anchor out from under the director.**

6. ***Do not expect emotion to be performed. Delivery strings can stay as notes. Round 1 should say a later skill may ignore them. Two voice ids are the cooperative performance plan.**

7. ***This skill owns `narration.json`. The director plan should not also define a timing sidecar. Movie Builder reads this file for times and the director file for intent. If they disagree about a word, the measurement wins and the missing measurement is a hole, not a cue for the director to invent a second.**

***One revision I am not asking for: conditional reactions should stay in the director plan. This skill reports silence duration and gets out of the way. The 800 ms decision is a consumer's rule, not a measurement.**

## ***Ideas Worth Revisiting in Round 4**

1. ***One script indexer or three. This skill can compute character offsets because it has code. Story Director may not. Keep substring plus `nth` as the interchange until all three skills can run the same indexer. Then offsets can become canonical, with the substring as a check.**

2. ***Who requests word times. A director list, a Movie Builder list, or always-on alignment. Always-on is simpler and slower to install. Pick one. Do not leave both skills emitting competing requests.**

3. ***Pause names. Freeze `beat` and `long` only after a real read is heard. Delete the director's millisecond range if Movie Builder never reads it.**

4. ***SRT ownership. This skill can emit cues. Movie Builder must apply spoiler breaks, because only it sees `not\_before`. A single shared SRT writer is worth it if the alternative is two caption tracks.**

5. ***Sample rate. 24 kHz matches Kokoro. The movie may want 48 kHz. The skill that resamples has to rewrite or scale every index. Decide that owner before either schema freezes.**

6. ***Supplied-audio remix. The rule now is no. Revisit only if users regularly want a beat inserted into their own recording. That is a different mode, and it must not become the default.**

7. ***Emotion engine. Revisit CosyVoice, or anything instruction-following, only after M5 passes with a flat voice. Do not block the contract on acting.**

8. ***Hosted vendor. One adapter is enough. Choose it when there is a key and a price, not in the schema.**

9. ***Casting. "Bang" as a second speaker should remain a director or user decision. Do not let this skill grow a rule that certain words imply a character.**

10. ***Version. Bump `narration-studio/0` when the fields Movie Builder actually reads are known. Unknown fields stay ignorable. A missing `audio.file`, or word times claimed without a method, is fatal.**

***5 citations**

*![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://gist.github.com/fagenorn/d4aa16704541370d9b9d5f91f1f07b34")![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/k2-fsa/sherpa-onnx/discussions/985")![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/k2-fsa/sherpa-onnx/issues/3705")![](data:image/png;base64,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 "Favicon for https://ryanwelch.co.uk/blog/kokoro-word-timestamps/")![](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://k2-fsa.github.io/sherpa/onnx/tts/pretrained_models/kokoro.html&size=64 "Favicon for https://k2-fsa.github.io/sherpa/onnx/tts/pretrained\_models/kokoro.html")**[\[FEATURE\] Word-Level Timestamps in TTS Output**](https://github.com/k2-fsa/sherpa-onnx/issues/3705)

***[https://github.com/k2-fsa/sherpa-onnx/issues/3705**](https://github.com/k2-fsa/sherpa-onnx/issues/3705)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/k2-fsa/sherpa-onnx/issues/3705")](https://github.com/k2-fsa/sherpa-onnx/issues/3705)**[github.com**](https://github.com/k2-fsa/sherpa-onnx/issues/3705)

***[Kokoro for TTS and word timestamps | Ryan Welch**](https://ryanwelch.co.uk/blog/kokoro-word-timestamps/)

***[https://ryanwelch.co.uk/blog/kokoro-word-timestamps/**](https://ryanwelch.co.uk/blog/kokoro-word-timestamps/)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAIAAAAlC+aJAAAACXBIWXMAAAsTAAALEwEAmpwYAAAHtUlEQVRoge1aXWgTSxSe7ma3k8QEjClUKKHYEmmFoJDmQazBarBq609t8aEvCpbqmz4JCtqCFKS+SR98tSDGvxZaakEoiIJYA4WI4g+oBMGCSaCNm6y7OeN9GN27d3d2m6a9pIV+T2VypnO+mXPOfGd3q37//o0QQggBgKIoAEAIQWsVHMfxPC+KIs/zdKSKEigUCqqqVtS35UEQBKfTiRDi0Dr0HiGkqmqhUEAIcQCw7rynUFUVADhFUSrtSflQFIUDgEq7UT4AgFvLNWdJEEK4SvuwUmwQqDQ2CFQaDoQQx3GiKBp+oOVVf8dRHULHrWoXtbFajCm0BEGw8W/JS9bBcdzi4uKtW7eqq6sRQhoTURRFUezr69P+xdevX9+8eVNXV9fQ0OD3+wHA4BDHcfPz8/fv3zdvB0JIUZSjR4/W19frpwiCMDIyYuVcc3Pzvn377Dk4EEL5fH52dtbj8eh/AACM8blz57T59fX1Pp9vaGjo9evXjY2N0Wi0ra0tEAgoikJ9IoQEAoG5uTlZls3noChKLpcbHByUZVk/XlNTc/fuXarMDA68evXqwIED9gT+5IDD4RD+C4yxYSMJIV6vd3h4uKWlRZKkiYmJ/v7+S5cuzc/Pa2EAAL29vQAgmOB2u2dnZ9PpNMf9m3gAEIvFisWi2R5jvLi4mEwm9faWBEoEIQQALly4kMvlMMY+n+/Lly/9/f2JRAJjTB1qa2uzkicul+vp06f6wyGE+P3+1tZW5jY7nc5Hjx4xA7JMAuhvnOzfv58uKQiCz+cbGBhIJpOCIBBCMMZHjhxhOoQxHhsbMwwqitLR0UG1sQGCIJgPbaUEEEIA0NraqpexPp/v6tWrqqpyHKcoyuHDh3O5HHNuoVBIJBJ6hwghoVDI7/cz7c2HtjoEtm7dao6TFy9e8DxPjygUCllFxdTUlCEqAKCnp0eSJLM989D0KPMic7lchhFRFN+9e6c51NXVxew0mFFhnzmKoiQSCavrokwCmzZtKhaLhsFMJkPPWlXVcDjsdruZc5mpbJM5oig+fvzYKor+RynR1dVlKPkUVqlslTmCICSTyVQqxUzlMgn8/PnT4XAYBj0ejxYGABCNRvP5PHO6OSpo5jQ1NTEPweVyzczMMA+hTAJmzwCgublZ75Df79eqrQGiKE5NTRkcAoBTp04xMwdjPD4+TqvcKhDgef779++G5fP5fCQS0SciFT+lF3iaOTYVk1a51SEwNzenL4WSJB07dszv9+uFGiEkGAwGAgGrqGAW+O7ubmbmuN3usbGxVSDAcZwsy9PT01oES5K0ffv2vr4+88IAcOLECauoePjwodk+FotZZU4qlfr48aMhipZNwOl03rt3j+6ELMvZbPb48eNDQ0PMKg4Ae/futYoKADCnsr00mp6eNlyCyyDAcRzGeGJiIh6P003t7u4eHR09ffq0qqrMFocQwvN8Z2cnMyqYBd5eGj158kSWZf0hGEuhjfeEkGvXrqVSqbNnz7a0tDQ2NtIH2kznNABAR0dHPB6nctXgUDKZTKfTXq9X469JI2bg0Xp68OBBzb7UEyCEcBw3ODh48eLFeDze39/f29s7MjLy9u1bjLFNW0ijIhKJWKXy5OSkuZ729PRYXYIPHjzQ2y8jhAghsizv2LHjzp07tbW1kiTNzMxcuXLlzJkztB+wEr2Kopw8eZIZFTQmEUJmaWT10DadTuu7nGUnMb1NhoeHadvl9XoVRRkYGLh58ybP80wO9oKZpnLp0sjpdE5OTmqpXM49QAjZvHnz+fPntVP2+XwvX768fPmyTcGxEsxWqWwjjZ4/f65dgmVKCQDYuXOn/pQxxh8+fBgfH2fmg41gZmq1JaXRs2fPKOcyCdDUNJRkt9s9OjoKAOZAso8Kplazl0bxeJz+vSI57fV6DSMA8P79e6axTVQAQF1dnXnQShqpqtrU1LSiE6Bg9mWfPn1irmrTagLAnj17DAFGKz1TGtG9oPYrIlBdXW3whuf5Hz9+WNkzW01VVaPRKMbYfJfbSKNdu3atAgFmvmazWataxGw1C4WC4RmHBqY0UlW1vb1dFEVKeEUEzOoAIfTr1y/7WYZWUxTFcDhs9bTYLI0KhYL+miufAABs2bLFPL6kNNK3mqqqdnZ22tibL0G/3x8MBpethZioqakxl3b7Z7E0Kg4dOkTNCoXC7t277d+U6qWRLMsdHR16+xWdwLZt28p4zawoSnt7O40Kw3ZaLaTFTD6fj0ajq0OAEBIOhw2PxQVBWDIHtFZTkiTDdlrZY4xjsZgkSZFIxNC4/iFQLBbV/0KW5SV3FwCuX7+ezWb1YTM/P28/C/1tNTOZTEtLSylv2umhZTIZrfxrcCCEXC5Xa2ur+Sm2KIr2/50Q0tDQcPv27Rs3bnz+/Lm6uprn+Xw+n0qlamtrbQKDtpqhUCgQCNgnvbZQMBgMhUJa+ddQtbCwwHxHRpcp5TsQOp123N++fUMIeTyezs5O+8imr7b0vdiSqzDtqxYWFkqZX8oC+vurRObL+tCBaV9qT7wkCCHL/exiVezX/XviDQKVxgaBSmODQKXB2b/IX+Pg7L+OWfvgeZ6tgtYLRFHkeJ63/+RozUIQBJ7nOYSQ0+lcdxy0j7+r1vvn9/8A+4n/EpTyHk4AAAAASUVORK5CYII= "Favicon for https://ryanwelch.co.uk/blog/kokoro-word-timestamps/")](https://ryanwelch.co.uk/blog/kokoro-word-timestamps/)**[ryanwelch.co.uk**](https://ryanwelch.co.uk/blog/kokoro-word-timestamps/)

***[Kokoro — sherpa 1.3 documentation**](https://k2-fsa.github.io/sherpa/onnx/tts/pretrained_models/kokoro.html)

***[https://k2-fsa.github.io/sherpa/onnx/tts/pretrained\_models/kokoro.html**](https://k2-fsa.github.io/sherpa/onnx/tts/pretrained_models/kokoro.html)

*[![](https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://k2-fsa.github.io/sherpa/onnx/tts/pretrained_models/kokoro.html&size=64 "Favicon for https://k2-fsa.github.io/sherpa/onnx/tts/pretrained\_models/kokoro.html")](https://k2-fsa.github.io/sherpa/onnx/tts/pretrained_models/kokoro.html)**[k2-fsa.github.io**](https://k2-fsa.github.io/sherpa/onnx/tts/pretrained_models/kokoro.html)

***[need timestamps for the decoded text · k2-fsa sherpa-onnx**](https://github.com/k2-fsa/sherpa-onnx/discussions/985)

***[https://github.com/k2-fsa/sherpa-onnx/discussions/985**](https://github.com/k2-fsa/sherpa-onnx/discussions/985)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/k2-fsa/sherpa-onnx/discussions/985")](https://github.com/k2-fsa/sherpa-onnx/discussions/985)**[github.com**](https://github.com/k2-fsa/sherpa-onnx/discussions/985)

***[Kokoro timestamped demo**](https://gist.github.com/fagenorn/d4aa16704541370d9b9d5f91f1f07b34)

***[https://gist.github.com/fagenorn/d4aa16704541370d9b9d5f91f1f07b34**](https://gist.github.com/fagenorn/d4aa16704541370d9b9d5f91f1f07b34)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://gist.github.com/fagenorn/d4aa16704541370d9b9d5f91f1f07b34")](https://gist.github.com/fagenorn/d4aa16704541370d9b9d5f91f1f07b34)**[gist.github.com**](https://gist.github.com/fagenorn/d4aa16704541370d9b9d5f91f1f07b34)

*![]()**$0.1614,006 tok**

*![](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNzkuNSIgaGVpZ2h0PSIyNzkuNSIgcHJlc2VydmVBc3BlY3RSYXRpbz0ieE1pZFlNaWQiIHZpZXdCb3g9Ii0xMS43NSAtOS43NSAyNzkuNSAyNzkuNSI+PHBhdGggIGQ9Ik0yMzkuMTg0IDEwNi4yMDNhNjQuNzE2IDY0LjcxNiAwIDAgMC01LjU3Ni01My4xMDNDMjE5LjQ1MiAyOC40NTkgMTkxIDE1Ljc4NCAxNjMuMjEzIDIxLjc0QTY1LjU4NiA2NS41ODYgMCAwIDAgNTIuMDk2IDQ1LjIyYTY0LjcxNiA2NC43MTYgMCAwIDAtNDMuMjMgMzEuMzZjLTE0LjMxIDI0LjYwMi0xMS4wNjEgNTUuNjM0IDguMDMzIDc2Ljc0YTY0LjY2NSA2NC42NjUgMCAwIDAgNS41MjUgNTMuMTAyYzE0LjE3NCAyNC42NSA0Mi42NDQgMzcuMzI0IDcwLjQ0NiAzMS4zNmE2NC43MiA2NC43MiAwIDAgMCA0OC43NTQgMjEuNzQ0YzI4LjQ4MS4wMjUgNTMuNzE0LTE4LjM2MSA2Mi40MTQtNDUuNDgxYTY0Ljc2NyA2NC43NjcgMCAwIDAgNDMuMjI5LTMxLjM2YzE0LjEzNy0yNC41NTggMTAuODc1LTU1LjQyMy04LjA4My03Ni40ODNabS05Ny41NiAxMzYuMzM4YTQ4LjM5NyA0OC4zOTcgMCAwIDEtMzEuMTA1LTExLjI1NWwxLjUzNS0uODcgNTEuNjctMjkuODI1YTguNTk1IDguNTk1IDAgMCAwIDQuMjQ3LTcuMzY3di03Mi44NWwyMS44NDUgMTIuNjM2Yy4yMTguMTExLjM3LjMyLjQwOS41NjN2NjAuMzY3Yy0uMDU2IDI2LjgxOC0yMS43ODMgNDguNTQ1LTQ4LjYwMSA0OC42MDFabS0xMDQuNDY2LTQ0LjYxYTQ4LjM0NSA0OC4zNDUgMCAwIDEtNS43ODEtMzIuNTg5bDEuNTM0LjkyMSA1MS43MjIgMjkuODI2YTguMzM5IDguMzM5IDAgMCAwIDguNDQxIDBsNjMuMTgxLTM2LjQyNXYyNS4yMjFhLjg3Ljg3IDAgMCAxLS4zNTguNjY1bC01Mi4zMzUgMzAuMTg0Yy0yMy4yNTcgMTMuMzk4LTUyLjk3IDUuNDMxLTY2LjQwNC0xNy44MDNaTTIzLjU0OSA4NS4zOGE0OC40OTkgNDguNDk5IDAgMCAxIDI1LjU4LTIxLjMzM3Y2MS4zOWE4LjI4OCA4LjI4OCAwIDAgMCA0LjE5NSA3LjMxNmw2Mi44NzQgMzYuMjcyLTIxLjg0NSAxMi42MzZhLjgxOS44MTkgMCAwIDEtLjc2NyAwTDQxLjM1MyAxNTEuNTNjLTIzLjIxMS0xMy40NTQtMzEuMTcxLTQzLjE0NC0xNy44MDQtNjYuNDA1di4yNTZabTE3OS40NjYgNDEuNjk1LTYzLjA4LTM2LjYzTDE2MS43MyA3Ny44NmEuODE5LjgxOSAwIDAgMSAuNzY4IDBsNTIuMjMzIDMwLjE4NGE0OC42IDQ4LjYgMCAwIDEtNy4zMTYgODcuNjM1di02MS4zOTFhOC41NDQgOC41NDQgMCAwIDAtNC40LTcuMjEzWm0yMS43NDItMzIuNjktMS41MzUtLjkyMi01MS42MTktMzAuMDgxYTguMzkgOC4zOSAwIDAgMC04LjQ5MiAwTDk5Ljk4IDk5LjgwOFY3NC41ODdhLjcxNi43MTYgMCAwIDEgLjMwNy0uNjY1bDUyLjIzMy0zMC4xMzNhNDguNjUyIDQ4LjY1MiAwIDAgMSA3Mi4yMzYgNTAuMzkxdi4yMDVaTTg4LjA2MSAxMzkuMDk3bC0yMS44NDUtMTIuNTg1YS44Ny44NyAwIDAgMS0uNDEtLjYxNFY2NS42ODVhNDguNjUyIDQ4LjY1MiAwIDAgMSA3OS43NTctMzcuMzQ2bC0xLjUzNS44Ny01MS42NyAyOS44MjVhOC41OTUgOC41OTUgMCAwIDAtNC4yNDYgNy4zNjdsLS4wNTEgNzIuNjk3Wm0xMS44NjgtMjUuNTggMjguMTM4LTE2LjIxNyAyOC4xODggMTYuMjE4djMyLjQzNGwtMjguMDg2IDE2LjIxOC0yOC4xODgtMTYuMjE4LS4wNTItMzIuNDM0WiIvPjwvc3ZnPgo= "Favicon for openai")**GPT Sol Latest**

***[https://github.com/steveonw/Read-Aloud-Main](https://github.com/steveonw/Read-Aloud-Main)Auto**

***[https://raw.githubusercontent.com/steveonw/Read-Aloud-Main/main/web/app.js](https://raw.githubusercontent.com/steveonw/Read-Aloud-Main/main/web/app.js)Auto**

# ***Narration Studio Skill Implementation Plan**

***Status: Design proposal only. No Skill or supporting scripts are being implemented in this round.**

***Core responsibility:**

***Narration Studio turns text or recordings into reusable audio and trustworthy timing metadata. It owns audio realization and measurement—not visual direction or video rendering.***

***It must be useful independently for audiobooks, lessons, dialogue, proofreading, and recording alignment.**


## ***1. Skill name and triggering description**

### ***Proposed name**

***Narration Studio**

***Suggested package identifier: `narration-studio`.**

### ***Proposed triggering description**

***Create, revise, assemble, transcribe, or align narrated audio. Use for text-to-speech, multi-speaker dialogue, pronunciation corrections, reusable speech clips, deliberate pauses, WAV export, subtitles, and script-to-recording timing. Support local or optional hosted engines when available. Preserve original text separately from speech-normalized text. Distinguish measured clip boundaries from aligned word timestamps. Does not direct visuals, generate illustrations, or render video.***

### ***Example requests**

- “***Narrate this chapter using a local voice.”**

- “***Use different voices for the narrator and Kevin.”**

- “***Correct the pronunciation of these names without changing my script.”**

- “***Regenerate only the sentence I changed.”**

- “***Align this MP3 with my original script.”**

- “***Find the precise time when the narrator says ‘fourteen.’”**

- “***Export a WAV, sentence labels, and subtitles.”**

### ***Capability boundary**

***The Skill’s instructions alone do not guarantee installed engines, model files, network access, or executable tools.**

***When execution is unavailable, it should produce a clearly labeled preparation package or setup guidance—not claim that audio has been generated.**


## ***2. Read-Aloud-Main: verified inspiration versus proposed extensions**

***I inspected the current [repository README](https://github.com/steveonw/Read-Aloud-Main) and [`web/app.js`](https://github.com/steveonw/Read-Aloud-Main/blob/main/web/app.js). This is source-level verification, not a build, listening test, or benchmark.**

### ***Verified in the inspected source**

| Behavior | Evidence and relevance |
| - | - |
| Sentence-oriented segmentation | **`segmentText()`** identifies text spans; long spans can be split into smaller chunks |
| Pronunciation substitutions | **`applyPronunciation()`** transforms speech input without replacing the underlying draft |
| Cached generated speech | **`sentenceCache`** stores sample arrays and sample rates |
| Synthesis-setting-aware cache keys | Keys include voice, speaker, delivery preset, speed, and spoken text |
| Independent reuse after edits | Rendering skips existing cache entries |
| Sample-based narration assembly | **`buildNarrationPcm()`** accumulates actual rendered samples and inserted gaps |
| Sentence/paragraph gap rules | Export distinguishes ordinary sentence gaps, paragraph gaps, and continuation chunks |
| WAV export | **`exportWav()`** writes mono PCM audio |
| Audacity timing labels | Labels contain start time, end time, and spoken text |
| Postprocessing affects timing | Export measures the pitch-resampled samples, rather than assuming the original length |

### ***Important limitations**

- ***The inspected speech cache is in-memory, not a persistent production cache.**

- ***Sentence labels describe exported clip intervals, including any silence inside those clips.**

- ***These labels do not establish individual word timestamps.**

- ***The current speaker controls do not constitute a complete per-segment multi-character production manifest.**

- ***Natural/Steady synthesis presets and pitch controls are not general instruction-based emotional acting.**

### ***Proposed adaptations**

***Borrow the pattern:**

***Segment → synthesize → cache → process → measure → assemble → export audio and timing together.***

***Add persistent storage, stable IDs, per-segment voice assignments, explicit pause events, source-to-spoken mappings, and selective alignment.**

***There is no reason to inherit the browser, USB launcher, or WASM build infrastructure unless portability becomes a separate product requirement.**

***Implementation note: Record the exact upstream commit inspected or reused during development. The repository’s default branch can change.**


## ***3. Standalone workflows**

### ***A. Text to narration**

***Inputs: Text, voice preference, optional pronunciation dictionary and pacing.**

***Outputs:**

- ***`narration.wav`**

- ***`narration.json`**

- ***Cached speech clips**

- ***Short production report**

***Default behavior should preserve wording while allowing explicitly recorded speech normalization.**

### ***B. Multi-speaker dialogue**

***Inputs: Script with speaker labels or confirmed speaker assignments.**

***Behavior:**

- ***Assign a supported voice to each speaker.**

- ***Generate reusable performance units.**

- ***Insert explicit turn gaps.**

- ***Assemble a complete narration track.**

***Do not silently substitute a character’s voice halfway through production.**

***Version one can handle sequential dialogue. Overlapping speech should be a later capability or a flagged unsupported instruction.**

### ***C. Audiobook or educational narration**

***Use sentence-sized units where practical, but allow longer units for natural continuity.**

***Support pronunciation rules for:**

- ***Names.**

- ***Acronyms.**

- ***Dates and numbers.**

- ***Technical terms.**

- ***Mathematical expressions.**

***Ambiguous equations require confirmed spoken wording; symbol expansion must not silently alter meaning.**

### ***D. Revise existing narration**

***Regenerate affected units only.**

***Changing a pause should require reassembly, not resynthesis. Changing one voice should invalidate the units assigned to that voice, not unrelated speakers.**

### ***E. Align a supplied recording**

***Inputs: MP3/WAV and original script.**

***Outputs:**

- ***Timing manifest.**

- ***Script/recording mismatch report.**

- ***Optional captions.**

- ***Original recording retained unchanged.**

***A decoded analysis copy may be created. Whether that copy becomes the cooperative master should be explicit.**

### ***F. Transcribe without a script**

***Produce a transcription with available timing and uncertainty.**

***These are transcription-derived segments, not references to an original authored script.**

### ***G. Precise timing lookup**

***Locate a requested phrase using reliable existing timestamps or selective alignment.**

***If the requested word is absent or uncertain, return an unresolved result rather than a fabricated timestamp.**


## ***4. Cooperation with the other Skills**

### ***With Story Director**

***Accept:**

- ***Source revision and script IDs.**

- ***Speaker identities.**

- ***Performance requests.**

- ***Pronunciation instructions.**

- ***Pause requests.**

- ***Important phrase anchors.**

- ***Whether supplied audio may be edited.**

***Return:**

- ***Actual narration revision.**

- ***Measured clip placements.**

- ***Resolved phrase/word anchors where available.**

- ***Pause realizations.**

- ***Unsupported performance requests.**

- ***Mismatches and timing uncertainty.**

***Narration Studio should not reinterpret a punchline or choose a reaction image.**

### ***With Movie Builder**

***Provide:**

- ***A declared audio timing reference.**

- ***Sample rate and actual duration.**

- ***Local audio paths.**

- ***Segment and word timing.**

- ***Silence events.**

- ***Caption candidates.**

- ***Unresolved anchors.**

***Movie Builder resolves visual timing against these outputs.**

### ***Important contract**

***Script segments, synthesis units, audio clips, and visual shots are not the same thing.**

***One synthesis unit may cover several script segments. One script segment may require multiple synthesis units. A clip may be reused at several timeline positions.**

***Avoid making these identities interchangeable.**


## ***5. Recommended `SKILL.md` structure**

***Keep the main file operational and concise.**

1. ***Metadata and triggering description**

2. ***Scope and non-capabilities**

3. ***Check execution environment**

   - ***Tools, engine, models, storage, network permission.**

4. ***Choose workflow**

   - ***Generate, revise, assemble, transcribe, align, or resolve anchors.**

5. ***Preserve source and establish identities**

6. ***Select engine and confirm voice assignments**

7. ***Prepare spoken text and pronunciation mappings**

8. ***Generate or reuse clips**

9. ***Apply processing and assemble**

10. ***Produce timing and optional captions**

11. ***Validate and report**

12. ***Failure and fallback rules**

13. ***Reference index**

***Core instruction:**

***Never infer word timestamps by evenly dividing a clip’s duration among words.***


## ***6. Proposed package, scripts, and references**

```
***`narration-studio/`**

`├── ***SKILL.md`**

`├── ***references/`**

`│   ├── ***narration-format.md`**

`│   ├── ***engine-selection.md`**

`│   ├── ***pronunciation-and-performance.md`**

`│   ├── ***alignment-and-uncertainty.md`**

`│   └── ***acceptance-tests.md`**

`├── ***examples/`**

`│   ├── ***single\_speaker\_request.json`**

`│   ├── ***dialogue\_request.json`**

`│   └── ***supplied\_recording\_report.json`**

`└── ***scripts/`**

`    ├── ***synthesize.py`**

`    ├── ***assemble.py`**

`    ├── ***align.py`**

`    ├── ***validate\_audio.py`**

`    └── ***export\_labels.py`**
```

***These are proposed files, not existing deliverables.**

### ***Script responsibilities**

| Proposed script | Responsibility |
| - | - |
| **`synthesize.py`** | Generate requested units through one supported adapter |
| **`assemble.py`** | Process clips, insert pauses, write WAV and matching metadata |
| **`align.py`** | Resolve script/audio or selective word timing |
| **`validate\_audio.py`** | Check media, durations, references, and suspicious audio |
| **`export\_labels.py`** | Export Audacity labels and optional SRT |

***Start with one engine adapter. Do not implement a large provider registry.**

### ***Optional assets**

- ***Pronunciation dictionary template.**

- ***Speaker-assignment template.**

- ***Small permitted test recordings.**

- ***Engine setup profiles.**

***Do not bundle voice models by default until distribution rights and package size are reviewed.**


## ***7. TTS and alignment options**

***The following are candidates to evaluate, not a verified compatibility matrix or performance ranking.**

### ***TTS candidates**

| Candidate | Proposed use | What must be checked |
| - | - | - |
| Native Sherpa-ONNX with a compatible Piper voice | Lightweight local baseline inspired by Read-Aloud-Main | Native API, model compatibility, pronunciation, installation |
| Kokoro | Alternative local narration | Runtime dependencies, voices, language support, actual host performance |
| Compatible KittenTTS package | Lightweight multi-voice exploration | Native support for the selected package and voice behavior |
| CosyVoice-family engine | Later expressive narration evaluation | Hardware, setup burden, instruction reliability, license |
| Hosted TTS | Optional expressive or convenient backend | Current availability, price, rights, privacy, timestamp behavior |

***Recommended first experiment: Compare one compatible native Sherpa/Piper setup against one alternative voice on the actual target machine, then select a single baseline.**

***Do not promise CPU real-time generation or emotional quality before measuring and listening.**

### ***Alignment candidates**

- ***faster-whisper: transcription and approximate timing support; not by itself a guarantee of script-constrained forced alignment.**

- ***WhisperX or another compatible aligner: candidate for word-level refinement.**

- ***A dedicated forced aligner: useful where language/model setup is appropriate.**

- ***Provider-native timestamps: useful if their relationship to the returned audio is documented and validated.**

***For supplied recordings, transcription may help detect deviations before aligning the expected wording.**

***For generated clips, selective alignment should be sufficient when only a few important inside-clip anchors are needed.**

### ***Timestamp provenance**

***Each timing result should identify whether it came from:**

- ***Measured clip placement.**

- ***Native provider timestamps.**

- ***Forced alignment.**

- ***Transcription.**

- ***Speech-activity detection.**

***These methods have different meanings and confidence characteristics.**


## ***8. Robust caching strategy**

### ***Separate identity from content**

***Use stable IDs for editorial identity:**

- ***Script segment.**

- ***Synthesis unit.**

- ***Clip.**

- ***Assembly event.**

***Use a content hash for cache reuse.**

***Two identical lines may share cached audio while retaining distinct timeline events.**

### ***Synthesis cache key**

***Include all inputs that can affect generated audio:**

- ***Actual spoken text.**

- ***Engine and model revision or checksum.**

- ***Voice and speaker.**

- ***Language.**

- ***Applied synthesis settings.**

- ***Accepted performance controls.**

- ***Seed, if applicable.**

- ***Context supplied to the engine, if applicable.**

***Hash a canonical serialized request.**

### ***Derived processing cache**

***Keep original generated audio separately from processed audio.**

***Derived keys include:**

- ***Source audio checksum.**

- ***Resampling.**

- ***Silence trimming.**

- ***Speed or pitch transformation.**

- ***Gain or other processing settings.**

- ***Processing version.**

### ***Assembly cache**

***Track ordered clip placements, pause lengths, and output settings.**

***Changing a gap invalidates assembly, not speech generation.**

### ***Reliability rules**

- ***Write files atomically.**

- ***Validate audio before marking a cache entry complete.**

- ***Save metadata beside cached clips.**

- ***Reuse only complete entries.**

- ***Detect missing or corrupt files.**

- ***Never evict media still referenced by a saved project.**

- ***Store hosted results locally immediately.**

***Persist returned audio rather than assuming repeated requests will sound identical.**

***Nuance: If synthesis uses surrounding context, changing one sentence may legitimately invalidate neighboring units. “Regenerate only one sentence” cannot be an unconditional guarantee.**


## ***9. Proposed audio timing JSON schema**

### ***Timing conventions**

***Use integer sample-frame positions as the canonical coordinate system for an assembled PCM master.**

- ***Start is inclusive.**

- ***End is exclusive.**

- ***Positions refer to the declared master sample rate.**

- ***Seconds can be exported as convenience values.**

- ***Stereo still has one frame position per simultaneous pair of channel samples.**

***Measure after all duration-changing processing.**

***Native or alignment timestamps must be converted to this coordinate system with their provenance retained.**

### ***Illustrative example**

***This shortened example represents two generated clips separated by a deliberate pause. Only one requested word has alignment data.**

```
***`\{`**

`  ***"schema\_version": "0.1-draft",`**

`  ***"source\_revision": "r1",`**

`  ***"audio\_revision": "a1",`**

`  ***"mode": "generated",`**

`  ***"master": \{`**

`    ***"path": "narration.wav",`**

`    ***"sample\_rate\_hz": 48000,`**

`    ***"channels": 1,`**

`    ***"total\_frames": 216000`**

`  ***\},`**

`  ***"script\_segments": \[`**

`    ***\{`**

`      ***"id": "seg\_001",`**

`      ***"speaker\_id": "narrator",`**

`      ***"original\_text": "The first frame took fourteen hours."`**

`    ***\},`**

`    ***\{`**

`      ***"id": "seg\_002",`**

`      ***"speaker\_id": "sound\_guy",`**

`      ***"original\_text": "Bang."`**

`    ***\}`**

`  ***\],`**

`  ***"speakers": \[`**

`    ***\{`**

`      ***"id": "narrator",`**

`      ***"voice\_ref": "voice\_narrator"`**

`    ***\},`**

`    ***\{`**

`      ***"id": "sound\_guy",`**

`      ***"voice\_ref": "voice\_sound\_guy"`**

`    ***\}`**

`  ***\],`**

`  ***"units": \[`**

`    ***\{`**

`      ***"id": "unit\_001",`**

`      ***"script\_segment\_ids": \["seg\_001"\],`**

`      ***"spoken\_text": "The first frame took fourteen hours.",`**

`      ***"clip\_id": "clip\_001",`**

`      ***"performance": \{`**

`        ***"requested": "deadpan",`**

`        ***"applied": "neutral",`**

`        ***"status": "not\_supported"`**

`      ***\}`**

`    ***\},`**

`    ***\{`**

`      ***"id": "unit\_002",`**

`      ***"script\_segment\_ids": \["seg\_002"\],`**

`      ***"spoken\_text": "Bang.",`**

`      ***"clip\_id": "clip\_002"`**

`    ***\}`**

`  ***\],`**

`  ***"clips": \[`**

`    ***\{`**

`      ***"id": "clip\_001",`**

`      ***"path": "clips/clip\_001.wav",`**

`      ***"sample\_rate\_hz": 48000,`**

`      ***"frames": 144000`**

`    ***\},`**

`    ***\{`**

`      ***"id": "clip\_002",`**

`      ***"path": "clips/clip\_002.wav",`**

`      ***"sample\_rate\_hz": 48000,`**

`      ***"frames": 48000`**

`    ***\}`**

`  ***\],`**

`  ***"events": \[`**

`    ***\{`**

`      ***"id": "event\_001",`**

`      ***"kind": "speech\_clip",`**

`      ***"unit\_id": "unit\_001",`**

`      ***"clip\_id": "clip\_001",`**

`      ***"start\_frame": 0,`**

`      ***"end\_frame": 144000,`**

`      ***"timing\_method": "measured\_clip\_placement"`**

`    ***\},`**

`    ***\{`**

`      ***"id": "pause\_event\_001",`**

`      ***"kind": "silence",`**

`      ***"origin": "inserted",`**

`      ***"request\_id": "pause\_001",`**

`      ***"intent": "reaction",`**

`      ***"start\_frame": 144000,`**

`      ***"end\_frame": 168000`**

`    ***\},`**

`    ***\{`**

`      ***"id": "event\_002",`**

`      ***"kind": "speech\_clip",`**

`      ***"unit\_id": "unit\_002",`**

`      ***"clip\_id": "clip\_002",`**

`      ***"start\_frame": 168000,`**

`      ***"end\_frame": 216000,`**

`      ***"timing\_method": "measured\_clip\_placement"`**

`    ***\}`**

`  ***\],`**

`  ***"word\_timings": \[`**

`    ***\{`**

`      ***"id": "word\_001",`**

`      ***"script\_segment\_id": "seg\_001",`**

`      ***"text": "fourteen",`**

`      ***"occurrence": 1,`**

`      ***"start\_frame": 96000,`**

`      ***"end\_frame": 120000,`**

`      ***"method": "selective\_forced\_alignment",`**

`      ***"review\_status": "unreviewed"`**

`    ***\}`**

`  ***\],`**

`  ***"issues": \[`**

`    ***\{`**

`      ***"code": "PERFORMANCE\_NOT\_SUPPORTED",`**

`      ***"unit\_id": "unit\_001"`**

`    ***\}`**

`  ***\]`**

***`\}`**
```

***All audio values and alignment results above are illustrative.**

### ***Required extensions beyond this abbreviated example**

***The final format should support:**

- ***Engine/model provenance.**

- ***Source-to-spoken text mappings.**

- ***Supplied-recording mismatches.**

- ***Unresolved anchors.**

- ***Optional detected speech boundaries.**

- ***Provider-specific confidence or quality signals.**

***Avoid inventing a universal numeric confidence score. Some engines do not supply one, and scores from different tools are not automatically comparable.**


## ***10. Performance, pronunciation, and emotion limitations**

### ***Performance control**

***Keep separate:**

1. ***Requested performance.**

2. ***Supported controls.**

3. ***Applied controls.**

4. ***Observed outcome, if reviewed.**

***An engine accepting an emotion instruction does not prove it performed that emotion.**

***Speed, gain, and pitch manipulation cannot substitute reliably for frustration, sarcasm, exhaustion, or character acting.**

### ***Pronunciation mapping**

***Maintain:**

- ***Original text.**

- ***Spoken text.**

- ***Applied substitutions.**

- ***A mapping between affected source and spoken spans.**

***This matters because one original token may become several spoken words.**

***For example, an acronym expanded into a phrase needs a phrase interval—not a fabricated single-word timestamp.**

### ***Clip boundaries versus speech boundaries**

***A clip can contain leading and trailing silence.**

***Keep measured clip placement authoritative for assembly, but store detected or aligned speech boundaries separately where needed.**

### ***Segment length tradeoff**

***Short units improve correction and caching. Longer units may improve prosody and continuity.**

***Default to natural performance units constrained by the engine—not a rigid sentence-only rule.**


| Test | Expected behavior |
| - | - |
| Change one sentence | Regenerate affected unit; reuse unrelated valid clips |
| Change only a pause | Reassemble without new TTS calls |
| Change one character’s voice | Invalidate that character’s affected units |
| Repeat identical dialogue | Allow cache reuse while preserving separate event IDs |
| Substitute pronunciation | Preserve original text and record transformed speech input |
| Precise reveal inside a clip | Resolve through native timestamps or selective alignment |
| No word timestamps available | Export clip timing; mark word anchor unresolved |
| Mixed sample rates | Resample explicitly; measure resulting frame counts |
| Speed/pitch processing | Recompute affected timing after processing |
| Recording deviates from script | Report missing, added, or changed passages |
| Recording contains silence | Mark detected silence, not automatically intentional silence |
| Restart after interruption | Reuse complete persisted clips |
| Corrupt cached clip | Reject and regenerate or report unavailable |
| Hosted provider fails | Preserve completed work; no silent voice substitution |
| Source revision changes | Flag affected mappings and timing as stale |

### ***Exact timing test**

***Use synthetic audio fixtures with known sample lengths and inserted gaps.**

***Verify:**

- ***Event boundaries equal written sample-frame positions.**

- ***Final frame count equals assembled content.**

- ***No cumulative rounding drift.**

- ***Exported labels reflect the same master.**

***This tests sample accounting, not speech recognition accuracy.**

### ***Word-timing test**

***Use a short human-reviewed recording with a clearly audible target phrase.**

***Check the resolved anchor against an agreed tolerance appropriate to the editing use case. Define that tolerance before evaluation; do not report an untested accuracy benchmark.**

### ***Listening test**

***Evaluate:**

- ***Natural continuity.**

- ***Pronunciation.**

- ***Speaker distinguishability.**

- ***Pause placement.**

- ***Clipping and distracting artifacts.**

***Correct timing does not guarantee pleasant narration.**


## ***12. Failure handling, dependencies, licensing, and milestones**

### ***Failure handling**

- ***No engine installed: Provide setup options or a preparation package.**

- ***Hosted failure: Use bounded retries; retain successful clips.**

- ***Unsupported voice: Request a replacement assignment; do not silently switch.**

- ***Unsupported emotion: Report neutral or supported realization.**

- ***Alignment disagreement: Preserve both script and observed recording text.**

- ***Ambiguous anchor: Return candidates or unresolved status.**

- ***Empty/corrupt audio: Reject the result.**

- ***Suspicious duration or silence: Flag for review, not automatically delete.**

- ***No permission for cloud processing: Keep text and recordings local.**

- ***Authoritative supplied audio: Do not insert pauses, trim, or normalize it without authorization.**

### ***Dependencies**

***Keep separate install profiles:**

- ***Core manifest/cache/assembly utilities.**

- ***One local TTS engine.**

- ***Optional alignment.**

- ***Optional hosted adapter.**

***FFmpeg is a practical optional dependency for compressed-audio decoding and export. The TTS and alignment stacks will introduce their own dependencies; pin tested versions during implementation.**

***Do not require every engine to be installed.**

### ***Licensing and privacy**

***The inspected Read-Aloud-Main repository is listed under MIT. Reused code must retain applicable notices.**

***Check separately:**

- ***Runtime license.**

- ***Model and voice license.**

- ***Redistribution rights.**

- ***Generated-audio usage terms.**

- ***Hosted data-retention policy.**

- ***Voice-cloning permission, if added later.**

***No current hosted prices or performance figures are asserted here.**

### ***Milestones**

1. ***One local voice, persistent clips, WAV assembly**

   - ***Complete narration and sample-based metadata.**

2. ***Revision and multi-speaker assignment**

   - ***Independent regeneration and explicit gaps.**

3. ***Supplied-recording alignment**

   - ***Script correspondence and mismatch reporting.**

4. ***Selective word anchors and exports**

   - ***Audacity labels and optional SRT.**

5. ***Optional hosted adapter**

   - ***Cost authorization, retries, privacy controls.**

6. ***Companion handoff test**

   - ***Story Director requests a reveal and pause; Movie Builder consumes actual timing.**

***The first working demonstration should generate a short narration, change one line, adjust one gap, and export a matching WAV and manifest.**


## ***13. Recommended revisions to the Round 1 plan**

### ***1. Add synthesis units without changing script identity**

***Story Director’s script segmentation should not force Narration Studio’s synthesis chunking.**

### ***2. Refine pause requests**

***Add:**

- ***Qualitative length intent.**

- ***Optional preferred duration or allowable range.**

- ***Whether audio editing is permitted.**

- ***Fallback if unavailable.**

***Narration Studio returns realized pause events separately.**

### ***3. Distinguish three timing boundaries**

***Story Director should be able to request:**

- ***Clip boundary.**

- ***Actual speech boundary.**

- ***Word/phrase boundary.**

“***Segment end” is currently ambiguous.**

### ***4. Include pronunciation-aware anchor resolution**

***Anchor matching must operate through source-to-spoken mappings. Original text and synthesized words may not match literally.**

### ***5. Keep audio-version-specific overrides downstream**

***A script-relative creative anchor can survive regeneration if still valid. An absolute-time correction belongs to a specific audio revision.**

### ***6. Clarify caption ownership**

***Narration Studio can export text and timing. Movie Builder owns typography, placement, and final caption presentation.**

***Reveal-sensitive caption constraints come from Story Director.**

### ***7. Treat emotion as intent, not achieved output**

***Round 1’s performance directions should explicitly permit unsupported or partially supported responses.**


## ***Ideas Worth Revisiting in Round 4**

1. ***Canonical timing reference: Decide whether cooperative exports require a PCM WAV master, especially for imported MP3 recordings with decoder delay or padding.**

2. ***Shared anchor vocabulary: Agree on clip, speech, phrase, and word boundaries.**

3. ***Source-to-spoken mapping: Choose the smallest representation that supports substitutions, expansions, and educational notation.**

4. ***Pause negotiation: Finalize requested, inserted, detected, and editorially used silence as distinct concepts.**

5. ***Chunking and naturalness: Test sentence-level generation against longer performance units before fixing defaults.**

6. ***Overlapping dialogue: Decide whether it is postponed, supported through separate tracks, or required by the first integrated story.**

7. ***Caption contract: Determine how Narration Studio’s timing and Story Director’s reveal protection reach Movie Builder.**

8. ***Version and cache rules: Align source revisions, audio revisions, clip identities, and invalidation across all three Skills.**

9. ***Minimum engine baseline: Select based on actual setup and listening tests—not model reputation alone.**

10. ***Integrated acceptance test: Use the same DOOM excerpt to demonstrate reusable narration, a precise reveal, an intentional pause, and a rendered reaction shot.**

***The guiding principle remains: preserve timing when producing audio, measure it after processing, and align only where the available metadata is insufficient.**

