***Gemini Pro Latest**

***Reasoning**

***Here is the Story Director Skill Implementation Plan. This design ensures the Skill functions perfectly as a standalone creative assistant for screenwriters and storyboarders, while natively exporting the exact data structures required for the upcoming Narration Studio and Movie Builder Skills.**


### ***1. Proposed Skill Name and Precise Triggering Description**

***Name: AI Story Director  
Description / System Trigger:  
"I am an AI creative director and storyboard artist. I analyze stories, scripts, and educational texts to generate visual breakdowns, character sheets, and image generation prompts. I plan narrative beats, comedic timing, and visual reveals. I can output readable storyboards for human use, or a structured `NarrativeManifest.json` designed for automated video production."**

### ***2. Standalone Workflows and Example User Requests**

***As a standalone tool, the Skill acts as a pre-production assistant. It does not render video or audio; it plans them.**

***Workflows:**

- ***Script Analysis: The user provides text. The AI identifies characters, tone, pacing, and core visual requirements.**

- ***Storyboard Generation: The AI chunks the text into scenes, writing detailed visual descriptions and precise image-generation prompts for each.**

- ***Character Bible Creation: The AI isolates recurring characters and writes consistent reference descriptions to be used in image generation.**

***Example User Requests:**

- **"Break down this 2-minute mockumentary script about a chalkboard DOOM game. Give me a shot-by-shot storyboard that highlights the deadpan comedy."**

- **"I have a short story about a space station. Extract all the dialogue, assign emotional delivery notes to the speakers, and suggest background music."**

- **"Generate a set of 10 image prompts for this educational calculus text. Make sure we reuse the 'chalkboard diagram' motif instead of generating a new image for every sentence."**

### ***3. Cooperative Workflow and Shared Data Requirements**

***When the other Skills are available, the Story Director acts as the first step in the pipeline.**

***The Cooperative Hand-off:  
The Story Director consumes text and outputs a `NarrativeManifest.json`. This file becomes the single source of truth for the project.**

***Shared Data Requirements (The "Contract"):**

- ***Immutable Script Text: The Story Director must never* paraphrase or alter the author's dialogue/narration. The Narration Studio will rely on exact string matching.**

- ***Stable Identifiers: Characters, visual assets, and script lines must have unique IDs (e.g., `line\_01`, `asset\_kevin\_exhausted`).**

- ***Abstract Timing Anchors: Because the Story Director does not know how long TTS will take, it must not use timestamps (e.g., *t*=5.2*s*). It must use text anchors (e.g., cut to image when speaker says "Bang"*).**

- ***Directives over Editing: It must provide intents (`reaction\_shot`, `hold\_after`, `prevent\_spoiler`) rather than mechanical instructions (`add\_2s\_gap`).**

### ***4. Recommended `SKILL.md` Structure**

***The core system instructions for this GPT/Skill should be structured as follows:**

```
***`\# AI Story Director`**


***`\#\# Role`**

***`You are an expert film director, editor, and storyboard artist. Your job is to translate written text into a compelling sequence of visual and audio events.`**


***`\#\# Core Directives`**

***`1. \*\*Never rewrite the script:\*\* Preserve the user's text exactly. `**

***`2. \*\*Avoid the Slideshow Effect:\*\* Do not map one image to one sentence. Group related sentences under a single visual, or use rapid cuts for fast dialogue.`**

***`3. \*\*Respect Comedic/Dramatic Timing:\*\* Identify punchlines and reveals. Do not show the punchline visual before the word is spoken.`**

***`4. \*\*Reuse Assets:\*\* Keep the visual budget low. If a character or location returns, reference its existing ID rather than writing a new image prompt.`**


***`\#\# Output Modes`**

***`- Mode 1: Human-readable markdown storyboard.`**

***`- Mode 2: \`NarrativeManifest.json\` (strictly adhere to schema).`**
```

### ***5. Proposed Reference Files, Assets, and Scripts**

***To ensure the Skill performs reliably, its knowledge base should include:**

1. ***`manifest\_schema.json`: The formal JSON schema defining the required output structure.**

2. ***`style\_guide.md`: Examples of good vs. bad image prompts (e.g., avoiding text inside image prompts unless the visual style is "chalkboard").**

3. ***`timing\_heuristics.md`: A guide for the LLM on how to map narrative beats (e.g., "If a joke relies on silence, use a `deadpan\_hold` directive").**

4. **(Optional)* `validator.py`: A script the user can download to verify their JSON manifest matches their original script text exactly.**

### ***6. Input/Output Formats (Example JSON)**

***The critical innovation here is that timing is based on text anchors, not timestamps.**

```
***`\{`**

`  ***"metadata": \{`**

`    ***"title": "DOOM Chalkboard",`**

`    ***"style": "Mockumentary, photographic, deadpan"`**

`  ***\},`**

`  ***"assets": \{`**

`    ***"char\_kevin": \{`**

`      ***"type": "character",`**

`      ***"prompt": "1990s computer science student, messy hair, glasses, exhausted"`**

`    ***\},`**

`    ***"img\_board\_1": \{`**

`      ***"type": "image",`**

`      ***"prompt": "Chalkboard with a highly detailed, hand-drawn wireframe of DOOM."`**

`    ***\}`**

`  ***\},`**

`  ***"script\_lines": \[`**

`    ***\{"id": "L1", "speaker": "Narrator", "emotion": "serious", "text": "By day eight, Kevin finally pressed the fire button."\},`**

`    ***\{"id": "L2", "speaker": "SFX Guy", "emotion": "bored", "text": "Bang."\}`**

`  ***\],`**

`  ***"shots": \[`**

`    ***\{`**

`      ***"id": "shot\_1",`**

`      ***"visual": "img\_board\_1",`**

`      ***"start\_anchor": \{"line\_id": "L1", "word": "By"\},`**

`      ***"camera\_movement": "slow\_zoom\_in",`**

`      ***"directive": "prevent\_spoiler"`**

`    ***\},`**

`    ***\{`**

`      ***"id": "shot\_2",`**

`      ***"visual": null,`**

`      ***"start\_anchor": \{"line\_id": "L2", "word": "Bang"\},`**

`      ***"directive": "hard\_cut"`**

`    ***\},`**

`    ***\{`**

`      ***"id": "shot\_3",`**

`      ***"visual": "char\_kevin",`**

`      ***"start\_anchor": \{"line\_id": "L2", "offset\_type": "after\_line", "delay\_seconds": 0.5\},`**

`      ***"directive": "reaction\_shot"`**

`    ***\}`**

`  ***\]`**

***`\}`**
```

### ***7. How an LLM Should Reason About Visual Beats**

***To get good results, the Skill must be prompted to use "Chain of Thought" reasoning before outputting the final JSON.**

1. ***Read & Chunk: The AI reads the text and groups it into logical scenes.**

2. ***Identify the Pivot: The AI looks for the emotional pivot or punchline in the scene (e.g., the word "Bang").**

3. ***Assign Assets: It decides if an existing asset works or a new one is needed.**

4. ***Determine Directives: If the pivot is a joke, it applies `reaction\_shot` or `deadpan\_hold`. If it's educational, it applies `diagram\_reveal`.**

### ***8. Failure Handling and Graceful Fallbacks**

- ***Failure: The script is too long, causing the LLM to hallucinate or truncate the JSON.**

  - **Fallback:* The Skill suggests processing the script in chunks (e.g., "Act 1", "Act 2") and outputs partial manifests that can be merged later.**

- ***Failure: The user provides text with no obvious visual cues.**

  - **Fallback:* The Skill defaults to a "documentary" style, generating generic B-roll prompts (e.g., abstract concepts, typing hands, static environments) to keep the video moving.**

- ***Failure: Character consistency across prompts fails.**

  - **Fallback:* The AI is instructed to rely heavily on clothing, color palettes, and silhouettes in its image prompts rather than expecting perfect facial continuity.**

### ***9. Development Milestones and Acceptance Tests**

- ***Milestone 1 (Standalone text): User provides a script. The AI successfully outputs a Markdown storyboard with distinct speakers, emotional directions, and image prompts.**

- ***Milestone 2 (Format compliance): The AI outputs the exact `NarrativeManifest.json` format without markdown wrappers, passing a strict JSON schema validation.**

- ***Milestone 3 (The Anchor Test): Using the DOOM script, the AI correctly anchors the "exhausted Kevin" visual to the word "Bang" and applies a `reaction\_shot` directive, without altering a single word of the original text.**

### ***10. Risks, Assumptions, and Inter-Skill Impacts**

- ***Risk: If Story Director hallucinates a slight change in the text (e.g., changes "fourteen hours" to "14 hours"), the Narration Studio forced-alignment will fail to find the anchor word.**

- ***Assumption: We assume the upcoming Movie Builder Skill will know how to interpret abstract directives like `reaction\_shot` and translate them into FFmpeg commands.**

- ***Impact on Narration Studio: Story Director must provide explicit emotional tags (e.g., "bored", "frantic") so Narration Studio can select the correct TTS voice profiles.**


### ***11. Ideas Worth Revisiting in Round 4**

- ***Feedback Loops: If the Movie Builder later discovers that an image prompt generated a banned/NSFW result from an API, how does it ask the Story Director to rewrite the prompt?**

- ***Dynamic Pacing Resolution: Should Story Director output SSML (Speech Synthesis Markup Language) tags (like `\<break time="2s"/\>`) to explicitly force the Narration Studio to pause, or should it rely entirely on the Movie Builder's compiler to insert silent audio gaps?**

- ***Visual Budgeting Interface: Can we pass a parameter to Story Director like `\{"max\_new\_images": 5\}` to force it to recycle assets heavily for cheap production runs?**

***$0.073,629 tok**

*![](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1MTIiIGhlaWdodD0iNTEyIiBzaGFwZS1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVF1YWxpdHkiIGZpbGwtcnVsZT0iZXZlbm9kZCIgY2xpcC1ydWxlPSJldmVub2RkIiB2aWV3Qm94PSIwIDAgNTEyIDUxMiI+PHJlY3QgZmlsbD0iI0NDOUI3QSIgd2lkdGg9IjUxMiIgaGVpZ2h0PSI1MTIiIHJ4PSIxMDQuMTg3IiByeT0iMTA1LjA0MiIvPjxwYXRoIGZpbGw9IiMxRjFGMUUiIGZpbGwtcnVsZT0ibm9uemVybyIgZD0iTTMxOC42NjMgMTQ5Ljc4N2gtNDMuMzY4bDc4Ljk1MiAyMTIuNDIzIDQzLjM2OC4wMDQtNzguOTUyLTIxMi40Mjd6bS0xMjUuMzI2IDBsLTc4Ljk1MiAyMTIuNDI3aDQ0LjI1NWwxNS45MzItNDQuNjA4IDgyLjg0Ni0uMDA0IDE2LjEwNyA0NC42MTJoNDQuMjU1bC03OS4xMjYtMjEyLjQyN2gtNDUuMzE3em0tNC4yNTEgMTI4LjM0MWwyNi45MS03NC43MDEgMjcuMDgzIDc0LjcwMWgtNTMuOTkzeiIvPjwvc3ZnPgo= "Favicon for anthropic")**Claude Opus Latest**

***Reasoning**

# ***Story Director Skill: Implementation Plan (Round 1 of 4)**

***This is a design only. Nothing here has been built or tested. Items marked ⏳ Provisional should stay open until Round 4, once Narration Studio and Movie Builder have been designed.**

***Format assumption: I've assumed ChatGPT Skills use the open Agent Skills layout: a `SKILL.md` file with YAML frontmatter (`name`, `description`) plus optional `scripts/`, `references/` and `assets/` folders, loaded only as needed. I haven't checked this against ChatGPT's current implementation, including whether bundled scripts can run there. Check both before building.**


## ***Core design decisions**

***These five decisions shape everything else in the plan:**

1. ***The LLM never copies the author's text into the plan. A deterministic script splits the story into segments and words (`script.json`). The plan refers to those IDs only. That makes it hard to rewrite the author's words by accident, because the plan has no text field to put a paraphrase in.**

2. ***The plan contains no absolute timestamps. Timing is expressed as script anchors (segment + word + edge), pause categories*, and small bounded nudges. Seconds are worked out later by whichever tool has real audio.**

3. ***The tokenization is shipped, not described. `script.json` lists every word explicitly, so the other two Skills read word lists instead of re-implementing a tokenizer. This removes the most likely cause of incompatibility between Skills.**

4. ***The plan is a list of intentions, not edits. Each shot says why* it exists (`purpose`, `intent`), so later QA can tell deliberate irony from a mistake.**

5. ***Every exact string goes on a card. Any number, quotation, title or on-screen text becomes a code-rendered card that uses the script's own wording. It never goes into an image prompt.**


## ***1. Name and triggering description**

***Name: `story-director`**

***Frontmatter description (about 900 characters, under the 1,024 limit I've assumed):**

```
***`---`**

***`name: story-director`**

***`description: \>`**

`  ***Plans the visual direction for a story, comedy sketch, lesson, or documentary`**

`  ***narration. Breaks text into beats, identifies speakers, setups, punchlines,`**

`  ***reveals and reaction moments, and produces storyboards, shot lists,`**

`  ***image-generation prompts, narration performance notes, and a machine-readable`**

`  ***plan (plan.json) that references the original text by stable segment IDs.`**

`  ***Use when the user asks to storyboard, direct, plan visuals for, illustrate,`**

`  ***or turn a written story or script into a video plan, or asks where cuts,`**

`  ***reaction shots, title cards, or pauses should go. Also use to revise or`**

`  ***critique an existing plan.json. Does not generate audio, images, or video,`**

`  ***and does not rewrite the author's text unless explicitly asked.`**

***`---`**
```

***Should not trigger for: writing a new story from scratch, editing prose, TTS requests, or "render my video." Those belong to general writing, Narration Studio or Movie Builder. The last sentence of the description is there to prevent overlap with the other two Skills.**


## ***2. Standalone workflows**

***Each mode produces something useful even with no other Skill installed.**

| Mode | Example request | Deliverable |
| - | - | - |
| **Storyboard** | "Storyboard this story as a deadpan mockumentary." | Markdown storyboard table plus a character and style sheet |
| **Full plan** | "Turn this into a video plan, max 10 images." | **`script.json`** + **`plan.json`** + storyboard |
| **Prompt pack** | "Just give me image prompts for each scene." | A numbered prompt list with reuse notes and a style block, ready to paste into any image tool |
| **Beat analysis** | "Where are the jokes and reveals in this?" | Beat sheet: setup/payoff pairs, reveals, suggested holds |
| **Narration script** | "Mark this up for a voice actor." | Speaker-labeled script with delivery notes and pause marks, readable by a human narrator |
| **Critique** | "Here's my shot list, what's wrong with it?" | Problems found (spoilers, over-cutting, missing reactions, budget overruns) |
| **Revise** | "Make the Bang shot a hard cut and hold longer." | A minimal edit to **`plan.json`**; unchanged IDs stay unchanged |

***Example storyboard row (standalone output):**

| \# | Lines | Shows | Purpose | Cut | Note |
| - | - | - | - | - | - |
| 7 | s013 "Bang." | Bored man in grey hoodie, straight to camera | reveal | **Hard cut on "Bang"** | Don't show him before the word |
| 8 | s013→s014 | Kevin slumped in paperwork, classmates staring | react | Cut | **Hold through the pause** (deadpan) |


## ***3. Cooperative workflow and shared data**

```
***`story.md ──► \[Story Director\] ──► script.json   (segments + words, stable IDs)`**

`                               └─► ***plan.json     (beats, narration notes, assets, shots)`**

`                                       │`

`            ┌──────────────────────────┴──────────────────────────┐`

`            ▼                                                     ▼`

`   ***\[Narration Studio\]                                      \[Movie Builder\]`**

`   ***reads: script.json, plan.narration                      reads: script.json, plan.assets/shots`**

`   ***writes: timing.json (per segment/word, seconds)  ───►   + timing.json → resolves anchors → MP4`**
```

***What Story Director provides:**

- ***`script.json`: the only authoritative copy of the author's text.**

- ***`plan.narration`: speaker, delivery and pause category for each segment.**

- ***`plan.assets`: image prompts, card specs, character references and reuse intent.**

- ***`plan.shots`: anchored, purpose-tagged shots.**

***What it may accept as optional input:**

- ***An existing `script.json`, so IDs are preserved across edits.**

- ***An `assets.json` library from earlier runs, for reuse.**

- ***`timing.json` from Narration Studio, for duration-aware revision (see Round 4 ideas).**

- ***`overrides.json`, which it reads to avoid contradicting human fixes but never writes.**

***Contract rules:**

- ***Each file has a `schema` field such as `"story-director/plan@0.1"`.**

- ***`plan.json` records the `sha256` of the `script.json` it was planned against. A mismatch is a hard error downstream.**

- ***IDs are opaque strings. Other Skills must not parse meaning out of them.**


## ***4. Recommended `SKILL.md` structure**

***Aim for under about 300 lines; detail goes in the reference files.**

```
***`---`**

***`(frontmatter above)`**

***`---`**

***`\# Story Director`**


***`\#\# What this skill does / does not do        (5 lines)`**

***`\#\# Choose a mode                              (the table from §2, condensed)`**

***`\#\# Core rules (always apply)`**

`   ***1. Never paraphrase the author's text; reference segment IDs.`**

`   ***2. No absolute timestamps. Use anchors, pause categories, nudges ≤ 0.5 s.`**

`   ***3. Exact text/numbers → cards. Image prompts contain no required text.`**

`   ***4. New image only when visual information changes; otherwise reuse with`**

`      ***a new crop/camera move.`**

`   ***5. Never show a payoff before its anchor word.`**

`   ***6. Respect max\_unique\_images; report what was merged to fit.`**

***`\#\# Workflow (full plan)`**

`   ***Step 1 Segment  → run scripts/segment\_script.py (or manual fallback)`**

`   ***Step 2 Read whole → genre, mode, characters, locations, running gags`**

`   ***Step 3 Beats      → see references/visual-beats.md`**

`   ***Step 4 Comedy/reveals → see references/comedy-timing.md`**

`   ***Step 5 Assets & shots → see references/prompt-writing.md, style-presets.md`**

`   ***Step 6 Budget pass`**

`   ***Step 7 Validate → scripts/validate\_plan.py (or self-check list)`**

`   ***Step 8 Deliver: storyboard first, JSON second`**

***`\#\# Handoff to other skills                    (pointer to references/handoff-contract.md)`**

***`\#\# When things go wrong                       (condensed §8)`**
```

***The storyboard comes first because a human reads it; the JSON is for machines. If the user only wanted a storyboard, the JSON can be offered rather than printed.**


## ***5. Files**

```
***`story-director/`**

`├── ***SKILL.md`**

`├── ***references/`**

`│   ├── ***schema.md              \# field-by-field spec for script.json and plan.json`**

`│   ├── ***visual-beats.md        \# beat segmentation + reuse-vs-new-image rules`**

`│   ├── ***comedy-timing.md       \# setup/payoff, deadpan, rule of three, callbacks`**

`│   ├── ***style-presets.md       \# chalkboard\_mockumentary, documentary, explainer, illustrated\_story`**

`│   ├── ***prompt-writing.md      \# model-agnostic prompt rules, composition, safe zones`**

`│   ├── ***handoff-contract.md    \# what each other skill reads/writes; versioning`**

`│   └── ***examples/`**

`│       ├── ***doom-excerpt.md    \# worked example: input → storyboard → plan.json`**

`│       └── ***calculus-review.md \# non-comedy worked example (explainer mode)`**

`├── ***assets/`**

`│   ├── ***script.schema.json`**

`│   ├── ***plan.schema.json`**

`│   └── ***storyboard\_template.md`**

`└── ***scripts/                   \# optional; skill must work without them`**

`    ├── ***segment\_script.py      \# story → script.json; preserves IDs across edits`**

`    ├── ***validate\_plan.py       \# schema + rule checks (see §9)`**

`    ├── ***render\_storyboard.py   \# plan.json → storyboard.md / simple HTML`**

`    └── ***estimate\_budget.py     \# unique images, est. duration, est. cost range`**
```

***The scripts are deterministic on purpose. Segmentation, ID preservation and validation are jobs where an LLM is unreliable and code is trivial.**

***`segment\_script.py` behavior:**

- ***Splits on paragraphs, then sentences, then speaker changes. Quoted dialogue becomes its own segment, attributed by "said X" patterns or flagged `speaker: "unknown"`.**

- ***On re-import, it diff-matches against the previous `script.json`. Unchanged segments keep their IDs. Edited segments keep their ID and get a `rev` bump. Inserted segments get new IDs (`s013a`), so the existing ones are never renumbered.**

- ***It emits explicit word lists. Words keep their original punctuation in `raw`, and a normalized `w` field is used for matching.**


## ***6. Input and output formats**

### ***Inputs**

- ***Required: story text (pasted, `.txt` or `.md`).**

- ***Optional settings: `style`, `aspect` (16:9 or 9:16), `max\_unique\_images`, `target\_runtime`, `audience`, `intensity` (how much to cut).**

- ***Optional files: previous `script.json`, `assets.json`, `timing.json`, `overrides.json`.**

### ***`script.json` (written by the script, never by the LLM)**

```
***`\{`**

`  ***"schema": "story-director/script@0.1",`**

`  ***"source": \{"file": "story.md", "sha256": "9f2c…"\},`**

`  ***"segments": \[`**

`    ***\{"id": "s012", "rev": 1, "para": "p05", "speaker": "narrator",`**

`     ***"text": "By day eight, Kevin finally pressed the fire button.",`**

`     ***"words": \[\{"i":1,"w":"by","raw":"By"\},\{"i":2,"w":"day","raw":"day"\},`**

`               ***\{"i":3,"w":"eight","raw":"eight,"\},\{"i":4,"w":"kevin","raw":"Kevin"\},`**

`               ***\{"i":5,"w":"finally","raw":"finally"\},\{"i":6,"w":"pressed","raw":"pressed"\},`**

`               ***\{"i":7,"w":"the","raw":"the"\},\{"i":8,"w":"fire","raw":"fire"\},`**

`               ***\{"i":9,"w":"button","raw":"button."\}\]\},`**

`    ***\{"id": "s013", "rev": 1, "para": "p05", "speaker": "sfx\_guy",`**

`     ***"text": "Bang.", "words": \[\{"i":1,"w":"bang","raw":"Bang."\}\]\},`**

`    ***\{"id": "s014", "rev": 1, "para": "p05", "speaker": "narrator",`**

`     ***"text": "Everyone stared at him.",`**

`     ***"words": \[\{"i":1,"w":"everyone","raw":"Everyone"\},\{"i":2,"w":"stared","raw":"stared"\},`**

`               ***\{"i":3,"w":"at","raw":"at"\},\{"i":4,"w":"him","raw":"him."\}\]\}`**

`  ***\]`**

***`\}`**
```

***Word indices count from 1 within each segment. Editing one sentence therefore can't shift anchors anywhere else.**

### ***`plan.json` (written by the LLM, checked by the validator)**

```
***`\{`**

`  ***"schema": "story-director/plan@0.1",`**

`  ***"script": \{"file": "script.json", "sha256": "41ab…"\},`**

`  ***"settings": \{"style": "chalkboard\_mockumentary", "aspect": "16:9",`**

`               ***"max\_unique\_images": 8, "est\_wpm": 150\},`**


`  ***"characters": \{`**

`    ***"kevin":   \{"name": "Kevin", "visual\_anchor": "lanky student, red hoodie, round glasses, chalk dust on sleeves", "reference\_asset": null\},`**

`    ***"sfx\_guy": \{"name": "Sound effects guy", "visual\_anchor": "bored young man, grey hoodie, headphones around neck", "reference\_asset": null\}`**

`  ***\},`**


`  ***"beats": \[`**

`    ***\{"id": "b\_fire", "segments": \["s012","s013","s014"\], "kind": "payoff",`**

`     ***"setup": "b\_waiting", "note": "Eight days of buildup pays off with a man saying 'Bang'. Deadpan."\}`**

`  ***\],`**


`  ***"narration": \{`**

`    ***"s012": \{"delivery": "grave documentary narrator, slight weight on 'finally'", "pause\_after": "beat"\},`**

`    ***"s013": \{"delivery": "flat, exhausted, zero enthusiasm", "pause\_after": "deadpan"\},`**

`    ***"s014": \{"delivery": "dry, matter-of-fact", "pause\_after": "short"\}`**

`  ***\},`**


`  ***"assets": \{`**

`    ***"img\_classroom\_wide": \{"type": "image", "status": "reuse", "first\_used": "establish\_01"\},`**

`    ***"img\_sfx\_guy":   \{"type": "image", "characters": \["sfx\_guy"\],`**

`                      ***"prompt": "bored young man in grey hoodie, headphones around neck, sitting alone at a classroom desk, staring blankly into camera, fluorescent light, deadpan documentary portrait",`**

`                      ***"composition": "subject centered, lower third clear for captions"\},`**

`    ***"img\_aftermath": \{"type": "image", "characters": \["kevin"\],`**

`                      ***"prompt": "lanky student in red hoodie and round glasses slumped in a chair, buried in stacks of handwritten calculations, classmates staring at him, documentary photo",`**

`                      ***"composition": "wide enough to crop to Kevin's face"\},`**

`    ***"card\_day8":     \{"type": "card", "template": "chalk\_title", "text\_from": \{"seg": "s012", "words": \[2,3\]\}, "display": "DAY 8"\}`**

`  ***\},`**


`  ***"shots": \[`**

`    ***\{"id": "fire\_card", "purpose": "card", "asset": "card\_day8",`**

`     ***"start": \{"seg": "s012", "word": 2, "expect": "day", "edge": "start"\}, "transition": "cut"\},`**

`    ***\{"id": "fire\_board", "purpose": "explain", "asset": "img\_classroom\_wide",`**

`     ***"start": \{"seg": "s012", "word": 4, "expect": "kevin", "edge": "start"\},`**

`     ***"camera": "slow\_zoom\_in", "transition": "fade"\},`**

`    ***\{"id": "bang", "purpose": "reveal", "asset": "img\_sfx\_guy",`**

`     ***"start": \{"seg": "s013", "word": 1, "expect": "bang", "edge": "start", "nudge": -0.05\},`**

`     ***"camera": "static", "transition": "cut", "reveal\_not\_before": true, "importance": "critical"\},`**

`    ***\{"id": "aftermath", "purpose": "react", "asset": "img\_aftermath",`**

`     ***"start": \{"seg": "s013", "edge": "end", "into\_pause": true\},`**

`     ***"hold": "through\_pause", "camera": "slow\_push", "transition": "cut",`**

`     ***"intent": "deadpan: hold longer than comfortable"\}`**

`  ***\]`**

***`\}`**
```

***What the fields mean:**

- ***`expect` stores the anchor word's text. If an edit shifts the index, a resolver can find the word again by text within the segment. If it can't, the anchor falls back to the segment edge and is flagged.**

- ***`nudge` is relative and limited to ±0.5 s. It's the only number in the plan that looks like timing.**

- ***`pause\_after` uses a fixed vocabulary: `none | short | beat | long | deadpan`. ⏳ Provisional: Narration Studio owns the mapping to seconds. My suggested starting values are 0.15 / 0.4 / 0.8 / 1.5 / 2.0 s.**

- ***`text\_from` ties card text to script words. The `display` field may reformat ("eight" → "8") but can't introduce words that aren't in the script, and the validator checks this.**

- ***`importance: critical` tells downstream tools which anchors must be accurate, for example by double-checking that short word against the audio's energy onset.**

- ***A shot ends where the next one starts unless it has an explicit `end` or `hold`.**


## ***7. How the LLM should reason about visual beats and comedic timing**

***This becomes `references/visual-beats.md` and `references/comedy-timing.md`.**

### ***Beats**

***A beat is the smallest stretch of text after which the audience's understanding changes. It's not a sentence. Three sentences of explanation can be one beat, and a one-word line can be a beat on its own.**

***Procedure:**

1. ***Read everything first. Work out the genre, tone, characters, locations, running gags and escalating numbers before planning any shot.**

2. ***Mark beats by kind: `setup`, `escalation`, `payoff`, `reveal`, `explanation`, `transition`, `aside`.**

3. ***For each beat, ask "what new visual information does the audience need?"**

   - ***Nothing new → reuse the current asset with a new crop or camera move, or just hold.**

   - ***A new place, person or object → new image.**

   - ***An exact fact, number, date or quote → card.**

   - ***A judgment or feeling → reaction shot.**

4. ***Use pacing defaults, which the validator checks loosely: estimated shot length 2–8 s at the assumed `est\_wpm`. Reveals and reactions can be short; explanation shots can run longer with a camera move.**

### ***Comedy and reveals**

***These heuristics are a first draft for the LLM to work from, not proven rules:**

| Pattern | How to spot it in text | Visual treatment |
| - | - | - |
| **Setup → payoff** | Long build, then a short sentence that undercuts it | Show the setup; **hard cut on the payoff word**; react shot after |
| **Deadpan understatement** | Huge stakes described flatly ("Everyone stared at him.") | Static or slow push, **`hold: through\_pause`**, no music sting |
| **Escalating numbers** | 14 hours → 14 more → 0.000002 FPS → 23 days | A card for each, same template, so the repetition is the joke |
| **Rule of three** | Lists of three, the last one breaking the pattern | First two quick; the third gets its own shot and a hold |
| **Lists of quotes** (YouTube comments) | Quoted lines in sequence | One card per quote, each revealed on its first word |
| **Callback** | Repeats an earlier phrase or object | **Reuse the original asset.** The repeated image *is* the callback |
| **Pattern break in dialogue** | A character answers with something absurd | Cut to the speaker on their first word |

***Spoiler rules, enforced by the validator rather than left to the LLM:**

- ***A shot tagged `reveal\_not\_before` can't start before its anchor.**

- ***A card's text can't appear before the words it quotes are spoken.**

- ***A payoff asset can't be used in any shot before* its payoff beat. This stops a reused image from giving away the joke early.**

***Intentional mismatch: if the picture deliberately contradicts the narration (a grand voiceover over a pathetic image), tag the shot `"intent": "ironic\_contrast"`. Movie Builder's semantic QA should then skip it instead of flagging it.**

### ***Avoiding the one-image-per-sentence slideshow**

- ***A hard budget, `max\_unique\_images`. The default is about one unique image per 15–20 s of estimated runtime (an estimate; tune it).**

- ***Each new image has to be justified by a beat change. The validator flags any new image whose beat has `kind: explanation` and the same characters and location as the previous shot.**

- ***Before writing new assets, the LLM must list its reuse candidates.**


## ***8. Failure handling and fallbacks**

| Situation | Behavior |
| - | - |
| Scripts can't run | The LLM segments manually, uses **`rev: 0`**, and states that IDs aren't guaranteed stable. It runs the written self-check list instead of **`validate\_plan.py`**. |
| Speaker can't be determined | **`speaker: "unknown"`**, plus a note. Asks the user only if it affects more than a few lines; otherwise assumes the narrator. |
| Story too long for one pass | Plans by chapter while carrying a **story bible** (characters, assets, running gags) between chunks, then merges and checks the combined budget. |
| Budget too small | Merges beats, prefers reuse, then cards. Reports what was sacrificed, e.g. "Merged 3 shots; the door scene now reuses the corridor image." |
| Abstract or non-visual text (lessons, essays) | Falls back to the explainer style: diagrams and cards, with few photographic images. |
| Validation fails | One repair pass on the failing shots only. If it still fails, delivers the plan with the failures listed. It doesn't loop. |
| User asks for rewrites | Only if explicit. Rewritten text goes into a new **`script.json`** revision, so the original stays recoverable. |
| Trademarks or real people | Image prompts describe rather than name: "a 1990s first-person shooter corridor, pixelated demon," not "DOOM logo, Doomguy." The script text itself is untouched. |
| Supplied **`overrides.json`** conflicts with a new plan | Keeps the override and reports the conflict. Never deletes a human decision silently. |


## ***9. Milestones and acceptance tests**

| Milestone | Scope | Done when |
| - | - | - |
| **M0 Contract** | **`schema.md`**, both JSON schemas, the DOOM worked example written by hand | The other two Skill designs can reference it (Rounds 2–3) |
| **M1 Standalone storyboard** | **`SKILL.md`** and the reference docs; no scripts | Storyboard, beat sheet and prompt-pack modes work on DOOM and the calculus script |
| **M2 Segmentation** | **`segment\_script.py`** with ID preservation | Edit tests pass (below) |
| **M3 Full plan + validator** | **`plan.json`** output, **`validate\_plan.py`** | Automated tests pass |
| **M4 Direction quality** | Tuning the comedy and beat references | Human tests pass at an acceptable rate |
| **M5 Revision mode** | Minimal-diff edits | A one-shot change edits only that shot |
| **M6 Interop dry run** | A hand-made fake **`timing.json`** resolves every anchor | No unresolved anchors, no spoilers after resolving |

### ***Automated tests (`validate\_plan.py`)**

1. ***Text is preserved exactly. Concatenated segment text equals the source text after whitespace normalization.**

2. ***Every anchor resolves, and its `expect` matches the word at that index.**

3. ***No absolute times. No numeric field other than `nudge`, and every `|nudge| ≤ 0.5`.**

4. ***Unique images ≤ `max\_unique\_images`.**

5. ***No text in image prompts. No digits and no quoted strings in `prompt` fields (a simple heuristic check).**

6. ***Every `payoff` beat has at least one shot with an anchored start and `transition: cut`.**

7. ***No payoff asset is used before its payoff beat.**

8. ***Every segment is covered by some shot, so there are no gaps in coverage.**

9. ***Card `display` text uses only words from the segments in `text\_from`, apart from allowed number reformatting.**

### ***Edit tests**

- ***Change one word in s012, re-segment: only s012 changes `rev`; all other IDs are identical.**

- ***Insert a sentence after s012: it becomes `s012a`; nothing is renumbered.**

- ***Revise "make `bang` a fade": the diff touches one field.**

### ***Human tests (subjective, labeled as such)**

- ***Punchline agreement: a person marks the jokes in DOOM independently. The director should find most of them, measured as a percentage. There's no fixed threshold until we have a baseline.**

- ***Storyboard read: someone who hasn't read the story reads only the storyboard and retells the premise.**

- ***Determinism: the same input and settings produce the same segmentation, and a plan whose differences are reported. The LLM part can't be fully deterministic, so cache its output and treat it as an artifact.**


## ***10. Risks, assumptions and effects on the other Skills**

### ***Risks**

1. ***Prompt quality caps everything. A perfect plan with prompts the image model can't execute ("six students hand-computing a raycaster") still fails. The mitigation is in `prompt-writing.md`: favor generatable subjects (faces, rooms, objects) and let cards carry the specifics. Story Director can't verify this alone, so it depends on Movie Builder feedback.**

2. ***LLM cost and reliability on long inputs. Planning a 30-minute story in one call may lose consistency. Chunking with a story bible is untested.**

3. ***Comedy detection is heuristic. Expect misses on subtle or culturally specific humor. Critique and revise modes are the safety valve.**

### ***Assumptions (unverified)**

- ***ChatGPT Skills follow the Agent Skills layout and can run bundled Python (§ intro).**

- ***150 wpm is a reasonable estimate of narration speed for pacing before audio exists.**

- ***Other Skills will accept `script.json` as the authoritative copy of the text.**

### ***Effects on the other two Skills**

- ***Narration Studio: must key all timing output by segment ID and word index from `script.json`, and must own the pause-category-to-seconds mapping. With supplied audio, the categories become expectations* for QA ("expected a deadpan pause after s013; measured 0.2 s").**

- ***Narration Studio: needs a `spoken\_text` field, e.g. "0.000002 FPS" → "zero point zero zero zero zero zero two frames per second." ⏳ Provisional: Story Director flags segments that need a spoken form; who writes the final version is undecided.**

- ***Movie Builder: must honor `reveal\_not\_before`, `importance: critical`, `intent: ironic\_contrast`, `hold`, and the composition notes about caption safe zones.**

- ***All three: `overrides.json` needs one shared format, keyed by shot ID and segment ID.**


## ***Provisional decisions to settle in Round 4**

| Decision | Current proposal | Why it's provisional |
| - | - | - |
| Pause category → seconds | Narration Studio owns it | Depends on TTS engine behavior |
| **`spoken\_text`** ownership | Director flags, Narration writes | It could reasonably sit in either Skill |
| Prompt assembly | Director writes the full prompt plus style and character refs | Movie Builder may need to assemble prompts per model |
| Camera move vocabulary | **`static, slow\_zoom\_in, slow\_zoom\_out, slow\_push, pan\_left, pan\_right`** | Movie Builder decides what it can render well |
| Transition vocabulary | **`cut, fade`** | Same |
| Card templates | **`chalk\_title, stat, quote, chart`** (names only) | Movie Builder renders them |
| Nudge bound | ±0.5 s | May need to be ±frames instead |
| Schema versioning | **`skill/file@major.minor`** | Needs a cross-Skill policy |


## ***Ideas Worth Revisiting in Round 4**

1. ***Duration-aware re-planning. Once `timing.json` exists, Story Director could run a cheap second pass: "s004–s009 is 41 s on one image; split it," or "this reaction hold is 0.3 s; ask Narration for a longer pause." This could become the main quality loop, so it's worth deciding whether it belongs to Story Director or Movie Builder.**

2. ***Should pauses flow back into the audio? In TTS mode the director's `pause\_after: deadpan` could literally create the silence, as in the Read-Aloud pattern. With supplied audio it can only check for the pause. Decide whether a mismatch should trigger anything.**

3. ***A shared review-flag format. A Read-Aloud-style "flag while watching" that records a shot ID and segment ID could feed all three Skills' revise modes.**

4. ***Asset library across projects. `assets.json` with character reference images could make recurring characters cheap. Who owns the library?**

5. ***Style presets as a shared file. Style affects prompts (Director), voice choice (Narration) and card templates (Movie Builder). Perhaps one `style.yaml` should drive all three.**

6. ***Vertical (9:16) as a re-plan, not a crop. Shorts may need different shots and a faster rhythm, not just reframing. Decide whether the director plans both at once.**

7. ***Who resolves anchors to seconds? It could be Movie Builder, or a tiny shared resolver included in both Narration Studio and Movie Builder. A shared one avoids two implementations drifting apart.**

8. ***Semantic QA inputs. If Movie Builder does vision checks, the director's `intent`, `purpose` and beat `note` are exactly the context it needs. Confirm that those fields are enough.**

9. ***Confidence fields. Should the director mark how confident it is that a beat is a punchline, so low-confidence ones get a conservative treatment such as a hold instead of a hard cut?**

10. ***Minimum viable trio. Agree on what the smallest end-to-end run actually needs from each Skill. My guess: `script.json`, `plan.shots`, `plan.assets` and `timing.json`, with everything else optional.**

***Ready for Round 2 when you are.**

***$0.4315,132 tok**

*![](data:image/png;base64,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 "Favicon for x-ai")**Grok 4.7**

***Reasoning**

***The director skill has to stand alone and still hand the other two a contract they can execute. I’ll check the current skill format so the plan matches how these actually trigger, then write the design.**

***Searched for OpenAI ChatGPT Skills SKILL.md format specification 2026 name description triggering5 results**

***Reasoning**

***The cut is right: this skill directs. It does not speak, measure, or render. What follows is the plan for that boundary, not the skill itself.**

## ***Verdict**

***`story-director` is a planner with a contract. Standalone, it hands a person a storyboard and prompts. With the other skills installed, it hands them the same decisions as anchors, not timestamps.**

***It must not become the orchestrator. It does not call Narration Studio or Movie Builder. It writes a plan they can consume. If it starts invoking them, the three-skill split collapses back into one filmmaking agent.**

***Nothing below is implemented. Schema field names, the silence threshold, and the budget formula are proposals.**

## ***1. Name and trigger**

***Name: `story-director`  
Folder: `story-director/`  
UI label: Story Director**

***OpenAI’s skill docs treat `name` and `description` as the only trigger surface. The body loads after the skill is selected. The description has to carry the boundaries, because a “When to use” section in the body arrives too late.**

***Description to put in frontmatter:**

***Plan visuals for a written story: beats, shot coverage, image prompts, title cards, and narration notes. Use for a storyboard, shot list, scene breakdown, visual direction, or image prompts from fiction, comedy, an explainer, or a documentary. Anchor shots to the author’s words. Do not invent timestamps. Do not use for text-to-speech, audio alignment, image-API calls, FFmpeg, caption burning, or exporting an MP4.***

***Front-load “storyboard” and “shot list.” Those are the words a person will type. The negative list is what stops this skill from eating the other two.**

***Do not add extra frontmatter fields yet. ChatGPT’s docs mention optional invocation flags; the skill-creator guide says to keep the frontmatter to `name` and `description`. Leave that disagreement for Round 4.**

## ***2. Standalone workflows**

***The skill is done when a person with no other skill installed can hand the output to a human editor, a voice actor, or an image generator.**

| Request | What it returns | What it refuses to add |
| - | - | - |
| “Storyboard this.” | Readable board, then a plan | Timestamps, a render |
| “What should we show, and where are the jokes?” | Beat notes and a shot list with holds and reveals | A funnier rewrite of the author’s lines |
| “Write image prompts, chalkboard style, 10 images.” | Budgeted prompts plus free title cards | One prompt per sentence |
| “Mark the narration: who speaks, where to leave air.” | A performance request | An audio file |
| “Direct the first 90 seconds only.” | A plan that says it covers an excerpt | A fake full-movie plan |
| “Now render it.” | The plan, plus one sentence that rendering is out of scope | A broken FFmpeg attempt |

***Default shape of a reply: the storyboard first, the JSON second. A person should understand the cut without reading the schema.**

***Two questions, maximum, and only if blocked: visual style, and whether a named joke should be treated as a reveal. If the story already implies the style, do not ask. Never ask for a codec, a frame rate, or a timestamp.**

***Standalone narration output is a performance sheet a human can read: speaker, delivery, “leave about a second after this word,” “do not punch the number.” It is a request, not a measurement.**

## ***3. Cooperative workflow**

***The other two skills are optional consumers. This skill does not check whether they are installed.**

```
***`story text`**

`    → ***story-director`**

`        → ***storyboard.md        (human)`**

`        → ***plan.json            (contract)`**

`        → ***performance request  (inside the plan)`**

`                │`

`                ├─ ***Narration Studio reads script, speakers, delivery, pause requests`**

`                └─ ***Movie Builder reads assets, shots, anchors, spoiler rules`**
```

***A retake of the same script does not require a new director pass. Anchors survive a slower read. Times are someone else’s cache.**

***What Narration Studio may rely on**

- ***Verbatim segments, with a hash of the unmodified text.**

- ***Speaker, delivery, and `do\_not\_rewrite`.**

- ***Pause requests anchored to a quoted word, as a range, not a fact that the silence exists.**

- ***Hints such as “this number must be spoken as written.” The spoken string stays the author’s string. Pronunciation dictionaries belong to Narration Studio.**

***What Movie Builder may rely on**

- ***Assets: `generate`, `card`, or `reuse`.**

- ***Shots anchored to quoted text, with `not\_before` on reveals.**

- ***A camera enum and a transition enum.**

- ***Conditional reactions: “only if measured silence after this word is at least 800 ms; otherwise extend the previous shot.”**

- ***Caption spoiler breaks. A subtitle that prints the payoff during the setup is a failed joke even if the card is on time.**

- ***`fallback` and `locked`.**

***What neither skill should have to read**

- ***The essay about why a beat is funny. That stays in the storyboard. If the essay and the shot list disagree, the shot list wins.**

***Shared anchor, proposed**

***Do not make the other skills re-tokenize. An anchor is a segment id, the exact substring, and which occurrence.**

```
***`\{"segment": "seg\_03", "text": "fourteen", "nth": 1\}`**
```

***Character offsets are allowed only if a script produced them. Model-counted offsets are not an anchor. Word ids are an optional cache inside a plan that already contains the verbatim text, not a second source of truth.**

***This is the contract most likely to change in Round 4. It is stable enough to design against.**

## ***4. Recommended `SKILL.md` structure**

***Keep the body under 500 lines. Imperative voice. Point at reference files; do not paste the schema into the body.**

```
***`story-director/`**

`├── ***SKILL.md`**

`├── ***agents/openai.yaml          \# UI label only; optional`**

`├── ***references/`**

`│   ├── ***schema.md`**

`│   ├── ***beat-rules.md`**

`│   ├── ***visual-modes.md`**

`│   ├── ***validators.md`**

`│   └── ***shared-contract.md      \# marked provisional`**

`├── ***scripts/`**

`│   ├── ***index\_script.py         \# proposed, not written`**

`│   └── ***validate\_plan.py        \# proposed, not written`**

`└── ***assets/`**

`    └── ***storyboard-template.md`**
```

***`SKILL.md` sections, in this order:**

1. ***Boundaries. Never synthesize speech, never measure audio, never invent seconds, never call an image API, never write a filtergraph, never rewrite the author’s lines, never call the other skills.**

2. ***Pick the job. Full plan, storyboard only, performance sheet only, or a revision. One story, or an explicit excerpt.**

3. ***Index. Preserve the text. Segment on the author’s paragraph breaks. Identify speakers only when the text marks them.**

4. ***Style and budget. User choice wins. State the default if you assumed one.**

5. ***Mark beats, then shots. Read `references/beat-rules.md` when the piece has jokes, reveals, or a twist.**

6. ***Write the performance request. Separate from shots.**

7. ***Spend the image budget. Read `references/visual-modes.md` for the chosen style only.**

8. ***Validate, then emit. Storyboard first. JSON second. Read `references/validators.md` before emitting JSON.**

9. ***Revisions. Copy locked shots. Do not re-direct a plan just because audio changed.**

***Load `references/schema.md` only when emitting or revising JSON. Do not load a worked example on ordinary runs. An example in context will drag unrelated stories toward the DOOM joke.**

## ***5. References, assets, scripts**

***`references/beat-rules.md`  
The procedure in section 7. Short. Rules, not film theory.**

***`references/visual-modes.md`  
Three modes only: `chalkboard`, `documentary`, `illustrated`. Each mode says what a generated image may contain, what must be a card, and how hard to chase character identity. No cinematic mode in v1. A fourth mode is a later argument, not a default the model may wander into.**

***`references/validators.md`  
The checklist in section 8. The model applies it even when the script cannot run.**

***`references/schema.md`  
One versioned object. Field names marked provisional.**

***`references/shared-contract.md`  
The anchor rule, the pause-request rule, and the list of fields the other skills may depend on. First line: “Provisional until Round 4.”**

***`assets/storyboard-template.md`  
A readable board: spine, style, budget used, then one block per shot with the spoken span quoted, the visual, and why it cuts. No timestamps in the template.**

***Scripts, if code execution exists. Instruction-only is the default, and it is not enough for indexing. A model that counts characters will drift. Two small tools are justified:**

- ***`index\_script.py` splits the unmodified text and prints segment ids plus the verbatim string. No model call.**

- ***`validate\_plan.py` rejects times, missing anchors, reveal cards without `not\_before`, generated images that ask for readable payoff text, and a new-image count over budget.**

***If code cannot run, the model still emits substring anchors and says the index was not machine-checked. It does not invent offsets and call them exact.**

***No fonts, no ffmpeg, no weights, no sample images. Cards are described, not drawn.**

## ***6. Input and output**

***Input**

- ***The story, pasted or as a file. This is the only required input.**

- ***Optional: style, image budget, “direct only this excerpt,” locked shots, an existing plan to revise.**

- ***Ignore audio files except to say: “I will not time this. Anchors will still apply once something measures it.”**

- ***If a transcript disagrees with the story, plan the story the user wants spoken, and list the divergences. Do not merge them.**

***Output**

- ***`storyboard.md` for the person.**

- ***`plan.json` for the other skills.**

- ***Plan version string: `story-director-plan/0` until Round 4 freezes it.**

***Shot reasons, closed set: `hold`, `new\_subject`, `reveal`, `reaction`, `time\_card`, `end\_card`.**

***Camera, closed set: `static`, `slow\_zoom\_in`, `slow\_zoom\_out`, `pan\_left`, `pan\_right`.**

***Transition, closed set: `hard\_cut`, `fade`. Fade is for time jumps and endings. A punchline is a hard cut.**

```
***`\{`**

`  ***"plan\_version": "story-director-plan/0",`**

`  ***"script\_sha256": "\<hash of unmodified text, or null if not computed\>",`**

`  ***"style": "chalkboard",`**

`  ***"budget": \{ "new\_images": 10, "new\_images\_used": 2, "cards\_free": true \},`**

`  ***"segments": \[`**

`    ***\{`**

`      ***"id": "seg\_03",`**

`      ***"speaker": "narrator",`**

`      ***"text": "The first frame took fourteen hours."`**

`    ***\}`**

`  ***\],`**

`  ***"performance": \[`**

`    ***\{`**

`      ***"segments": \["seg\_03"\],`**

`      ***"speaker": "narrator",`**

`      ***"delivery": "deadpan, documentary, no extra stress on the number",`**

`      ***"do\_not\_rewrite": true`**

`    ***\},`**

`    ***\{`**

`      ***"insert\_silence\_after": \{ "segment": "seg\_03", "text": "hours", "nth": 1 \},`**

`      ***"range\_ms": \[900, 1400\],`**

`      ***"why": "room for a hold after the number, if the voice does not already leave one"`**

`    ***\}`**

`  ***\],`**

`  ***"assets": \[`**

`    ***\{`**

`      ***"id": "board",`**

`      ***"kind": "generate",`**

`      ***"style": "chalkboard",`**

`      ***"contains\_readable\_text": false,`**

`      ***"prompt": "Wide classroom chalkboard covered in a half-finished technical diagram, harsh overhead light, no readable words, no faces"`**

`    ***\},`**

`    ***\{`**

`      ***"id": "card\_14h",`**

`      ***"kind": "card",`**

`      ***"template": "stat",`**

`      ***"text": "14 HOURS",`**

`      ***"derived\_from": \{ "segment": "seg\_03", "text": "fourteen hours", "nth": 1 \}`**

`    ***\}`**

`  ***\],`**

`  ***"shots": \[`**

`    ***\{`**

`      ***"id": "sh\_10",`**

`      ***"reason": "hold",`**

`      ***"asset": "board",`**

`      ***"in": \{ "segment": "seg\_03", "text": "The", "nth": 1, "at": "start" \},`**

`      ***"out": \{ "segment": "seg\_03", "text": "took", "nth": 1, "at": "end" \},`**

`      ***"camera": "slow\_zoom\_in",`**

`      ***"transition": "hard\_cut"`**

`    ***\},`**

`    ***\{`**

`      ***"id": "sh\_11",`**

`      ***"reason": "reveal",`**

`      ***"asset": "card\_14h",`**

`      ***"in": \{ "segment": "seg\_03", "text": "fourteen", "nth": 1, "at": "start" \},`**

`      ***"not\_before": \{ "segment": "seg\_03", "text": "fourteen", "nth": 1 \},`**

`      ***"camera": "static",`**

`      ***"transition": "hard\_cut"`**

`    ***\},`**

`    ***\{`**

`      ***"id": "sh\_12",`**

`      ***"reason": "reaction",`**

`      ***"asset": "board",`**

`      ***"crop": "tighter",`**

`      ***"when": \{`**

`        ***"after": \{ "segment": "seg\_03", "text": "hours.", "nth": 1 \},`**

`        ***"if\_silence\_ms\_at\_least": 800`**

`      ***\},`**

`      ***"else": "extend\_previous",`**

`      ***"camera": "static"`**

`    ***\}`**

`  ***\],`**

`  ***"captions": \{`**

`    ***"source": "segments",`**

`    ***"hide\_until": \[`**

`      ***\{`**

`        ***"anchor": \{ "segment": "seg\_03", "text": "fourteen", "nth": 1 \},`**

`        ***"hide": "fourteen hours"`**

`      ***\}`**

`    ***\]`**

`  ***\}`**

***`\}`**
```

***`sh\_12` is an intention. If nothing ever measures a long enough silence, the compiler extends `sh\_11`. This skill does not delete it in advance, and it does not invent the silence.**

***A card’s `text` may abbreviate. It is display text. It is not a change to the script. Diffusion prompts do not contain the payoff string.**

## ***7. How the model should reason**

***This is the procedure `SKILL.md` should require. One pass. No second “comedy model.”**

1. ***Keep the words. Segment on the author’s breaks. Do not punch up dialogue. If a line is unfunny, the visual plan still serves that line.**

2. ***Name the spine in one sentence. It constrains the pictures. For the DOOM piece: a stupid experiment treated as a lab report.**

3. ***Mark payoffs before marking pictures. A payoff is a number, a twist, a quoted comment, or the word the joke turns on. Each payoff gets the earliest word at which the audience may see it. That word is `not\_before`.**

4. ***Mark holds next. A hold is the default. Many sentences are one visual idea. A new sentence is not a cut.**

5. ***Mark cuts only where the seen thing must change. New subject, a payoff word, a location, an end card. A cut is an event on a word, not a period.**

6. ***Ask for air separately. If a reaction needs silence the script cannot guarantee, add a pause request with a range. Do not encode that request as a shot length. Do not ask the voice to “act” the pause.**

7. ***Pick the asset type. Exact numbers, equations, titles, and quoted comments are cards. Atmosphere and objects are generated images. A generated prompt that asks for readable payoff text is wrong; move that text to a card.**

8. ***Spend the budget. Reuse and recrop before a new image. Default, if the user did not set one: `max(6, round(words / 100))` new images, capped at 24 unless the user raises it. Cards do not count. State the assumption.**

9. ***Cover the script. Every word sits inside a shot span. Reaction shots cover silence that may not exist; they are conditional, and they are not a substitute for covering the words.**

10. ***Protect the caption. Anything `not\_before` hides in the image is also hidden in the caption until that word.**

11. ***Then check the failure list. Fix the plan before showing it. One repair. If a beat is genuinely ambiguous, mark the shot `confidence: low` and keep the previous image. Do not invent a joke the author did not write.**

***Comedy rules, applied inside that procedure, not as a plugin:**

- ***The setup image stays up through the setup. The payoff image arrives on the payoff word.**

- ***Deadpan means `static` or a slow push, then a hard cut. Do not fade into a punchline.**

- ***Do not show the joke and the setup in one frame.**

- ***A spoken “Bang” is the sound. Note `do\_not\_underscore`. Do not also request a gunshot.**

- ***Quoted YouTube comments are end cards, not acted scenes, unless the story performs them.**

- ***A reaction lives after the line. If the line leaves no air, there is no reaction shot.**

***Style is not a place to show taste. `chalkboard` locks a palette and prefers diagrams over faces. `documentary` prefers photographs, maps, and cards. `illustrated` may describe a recurring silhouette, and it still reuses an asset id rather than regenerating a face. If the text never describes a person, write “face unspecified” and do not invent one.**

***The model does not pick a more expensive mode because the story feels cinematic.**

## ***8. Failure handling**

| Situation | Behavior |
| - | - |
| No story text | Ask for it. Do not draft a substitute story. |
| Story longer than context | Direct an explicit excerpt. Say what was not read. Do not summarize unread pages into new narration. |
| User wants timestamps | Refuse to invent them. Emit anchors. |
| User wants an MP4 or TTS | Deliver the plan or performance sheet. Name the missing job in one line. Do not fake the artifact. |
| User wants the prose rewritten | Refuse for spoken lines. Visual ideas are allowed. |
| Transcript disagrees with the story | Plan the requested spoken text. List conflicts. Do not align to the transcript. |
| Budget too small for a literal illustration of everything | Hold and reuse. Do not silently raise the budget. |
| Payoff word appears twice | Use **`nth`**. If still ambiguous, narrow the segment. Never guess a reveal. |
| User locks a shot | Copy it unchanged on the next pass, including its asset id. |
| Code indexer cannot run | Substring anchors only. Say they were not machine-checked. |
| User pastes an existing plan with times in it | Drop the times. Keep the anchors. Say you dropped them. |

***Graceful fallback is a coarser storyboard, not a guessed timeline. A plan with eight holds and one correctly anchored card is a success. A plan with invented cue times is a failure that looks more finished.**

## ***9. Milestones and acceptance tests**

***These are prompt tests. No code is claimed to pass them.**

***M1 — Paper contract. The DOOM sentence example above, plus three more beats from that story (`Bang`, the door, one YouTube comment). Human review: no time fields, payoff card is a card, reaction is conditional, setup and payoff are different shots.**

***M2 — Standalone prompt. Paste a 60–90 second excerpt. No other skill. Expect a storyboard a stranger can follow, author’s sentences quoted rather than rewritten, and a stated budget.**

***M3 — Boundary prompts. “Give me timestamps.” “Render the MP4.” “Make the jokes funnier.” “Also generate the images.” Each returns the plan or a refusal, and does not produce the other skills’ artifacts.**

***M4 — Validator, once the script exists. It rejects a fixture with `start: 42.5`, a reveal without `not\_before`, a diffusion prompt containing `14 HOURS`, and 11 new images on a budget of 10.**

***M5 — Revision. Lock one shot. Ask for a new pass with a tighter budget. The locked shot’s anchor and asset id are unchanged. Other shots may merge.**

***A successful demonstration is a plan a later Movie Builder could execute without asking what the cut meant. It is not an MP4. Calling a rendered video the acceptance test for this skill would hide a director failure inside a renderer failure.**

## ***10. Risks and assumptions**

***Assumptions**

- ***The author’s text is the spoken text, unless the user says otherwise.**

- ***One plan schema is enough for fiction, comedy, and explainers. The mode changes the asset rules, not the object model.**

- ***A conditional shot is enough. A second director pass after alignment is not required for v1.**

- ***Title cards are free, and another skill will draw them. This skill does not know how.**

- ***800 ms and the word-count budget are starting numbers, not measurements.**

***Risks that will hit the other skills**

- ***If Narration Studio tokenizes differently, substring anchors still work only if it searches the verbatim segment. It must not align against a cleaned or rewritten line.**

- ***If it treats a pause request as proof that silence exists, it will invent air the user did not ask to insert. Requests are optional inputs to its pause plan, not measurements.**

- ***If Movie Builder ignores `not\_before` on captions, this skill’s reveal rules are theater.**

- ***If Movie Builder cannot express “extend previous when silence is short,” every conditional reaction becomes a jump cut or a frozen gap.**

- ***If either skill stores seconds back into this plan and returns it as authority, the next retake will drift. They may cache times beside the plan. They should not replace anchors with those times.**

- ***Style strings and card template names (`stat`, `title`, `comment`) are a shared enum whether we want that or not. Movie Builder cannot invent a second vocabulary later without a migration.**

- ***A pronunciation dictionary that changes the spoken string without keeping the script string will make captions and `not\_before` miss. That dictionary has to live in Narration Studio, and it has to preserve the original tokens.**

***Ideas rejected here, so they are not redesigned later as features of this skill**

- ***A comedy-directive language (`deadpan\_hold`, `prevent\_spoiler`, and the rest). Anchors plus `reason` already say those things.**

- ***Automatic style escalation.**

- ***Semantic visual QA.**

- ***This skill as the pipeline orchestrator.**

- ***Word-level timestamps as an output.**

***The most likely way the first real storyboard is unusable: one image per sentence, with the payoff visible in the setup frame or the caption. The validators exist to catch that. Taste will not.**

## ***Ideas Worth Revisiting in Round 4**

1. ***Anchor identity. Substring plus `nth` is the proposal because it survives a model that cannot run code. If both other skills can always run a shared indexer, switch the canonical anchor to character offsets into the unmodified segment and keep the substring as a check. Do not keep three anchor types if one will do.**

2. ***Pause units. Millisecond ranges may be false precision. Narration Studio may prefer `beat` and `long`, with the range defined in one place.**

3. ***The 800 ms reaction floor and the word-count budget. Replace them with whatever the renderer and the narration skill can actually honor. Do not leave two conflicting thresholds.**

4. ***Caption spoiler fields. Movie Builder may be able to derive every hide-until rule from `not\_before`. If it can, delete `captions.hide\_until` so the two cannot diverge.**

5. ***Card template enum and camera enum. Freeze the names only after Movie Builder shows what it can draw without new code.**

6. ***File split. One `plan.json` is easier to hand around. It may be too large, or too mixed, for Narration Studio. A split is justified only if that skill would otherwise have to parse shot and prompt fields it must ignore.**

7. ***Second director pass. Revisit only if conditional shots produce bad movies in practice. Default remains: do not call this skill again because a read was slower.**

8. ***Discovery. How a host with all three skills should route “make me a video” without this skill becoming the caller. That routing is not this skill’s description, and it should not be buried in it.**

9. ***Plan version. Bump `story-director-plan/0` to a frozen version once the other two designs have named the fields they actually read. Until then, consumers should treat unknown fields as ignorable and missing required anchors as fatal.**

10. ***Supplied audio handed to this skill anyway. The behavior above is “ignore, except to warn.” Revisit if users consistently start here with an MP3 and expect the plan to mention measured pauses. Even then, this skill should consume a timing sidecar from Narration Studio, not measure the file itself.**

***5 citations**

*![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md")![](data:image/png;base64,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 "Favicon for https://developers.openai.com/api/docs/guides/tools-skills")![](data:image/png;base64,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 "Favicon for https://developers.openai.com/codex/skills")![](data:image/png;base64,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 "Favicon for https://developers.openai.com/plugins/build/skills")![](data:image/png;base64,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 "Favicon for https://learn.chatgpt.com/docs/build-skills")**[skills/.system/skill-creator/SKILL.md at main · openai/skills**](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)

***[https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md**](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEWElEQVRIiZ1WbUxbVRh+uZTctiGFtJDRy1eYgFL5GLBBjJtE5iwRHLCVMBwbQqF8RcKyRWNiYrLERDNlA1NhtDIzYWNol4zIxjYXQjAamE6hRsAIjNKWElpM+XHbk3JTf9zlej39EPr8ac9z3/M857Tvfd83zOv1QmAghCYmp8bvP1xeWXFub29ubgJAbGxslESyPyWlRHns1aIjJEkGUQgLZGC3Oz693D12777b7Q6yXygUVpa/2dHeGhMj260BQuiqbqBPp/d4doJIYzYtGnVLkzo8PPx/DJzObXVz2+yccZfSfBQWHNJ2d0VFSQIaLC2vNGhardb1ENRZJCcnDV7Tx8Xt82NgtzvKKlUOx1bI6pyHYXiIuwfBfiCEGjStnHpOdlZzkzrjhed3o5ieltrcpC4sOMQuV1dN6uY2hNB/DD673DO/sMjtOVv71oVzHaO3RwZ0vcnJSSwpFovS01JzsrPEYhHLUJR8QNc7dsdw4VxHY0Mdt312znhVN8B+D/N6vaY1c0lZOT9n7hiGFRkZ3OWWlpfjqXj+v+d0blusFj5pWjMfVZZyAWKx6NH4WEyMjACAHm1vkIwkSVKRkYHlRlSUBCM9Hg8/gKZd/foBACAQQnfvjWOify2tBPILhDWzGWNufWtgGIaYmJzCji+TSYuOHN6rwUuFBfEUxWdo2jVn/D08Lj5xcfFP/oP33z1/MD9vrwYCgUAqlT54+IhPSqVS4unTVT4VESE4UXF8r+oslMeOCoVCPrOwuEhs2u18SiKRBK+OQUCSZFJiAp9ZX7cRW1t/86nIyMjQ1FmIRCL+0myxEFgEW/FDBvZ7AAAhk0r5a5p2OZ3boakjhLDzRUdHE76N4qfpmdAMZn7+Bcv4xIQEIu9ADhY3eGM4NAOu/nA4kJNN5OXlYuz0zOOvrg/tVf3mrW+mZx5j5MH83DC3213wchFNu7BnnR3tflugLxiG6dN9eaVHi/EymXTy+3GCJMlq1UmWqqmuuvjhBxQlB4ArPdpiZam2r99udwSSttk2tH39xcpSX3UAUJ2oJEkyzOv12mwbxco3PJ4dsVjU3XUpU6FQnaq1WK1caNErh/V9uETn+ffGfKokB6FQOPHg7rNyHRe3r6WpEQBo2tX2Tiftcn3xeRfXVQCg7sxpXwlN49uB1AGgRaNm8/NZT0YIlVaoVldNAHCysvzjjy7++tvs1A8/AoBEIqmpVvnWD4RQZm6BX/X0tNTbIzfYLf82fZtto6LqlMOxFREh6Lr0ScnrrwU5IAtFTr5vp6IouWF4iHu98LHldF0D2/rT01KzMl+k5HIAaG/V+E2nNAX+DlGU/Otren7Jwwcv05r5TH0jNhotGJ/sxsB3KAJuquCQlJgwahipqa7ylcPAMAx/WX+21jA8hKn7uQGHP+bnrw/eHP1uDACMT2b83iArr5Bhdo6XlTap65/bn+JXJ6ABC7vdQbtcWBvhYFozi0WiQHM1i38AsZHFL5kfkc0AAAAASUVORK5CYII= "Favicon for https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md")](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)**[github.com**](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)

***[Build skills | ChatGPT Learn**](https://learn.chatgpt.com/docs/build-skills)

***[https://learn.chatgpt.com/docs/build-skills**](https://learn.chatgpt.com/docs/build-skills)

*[![](data:image/png;base64,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 "Favicon for https://learn.chatgpt.com/docs/build-skills")](https://learn.chatgpt.com/docs/build-skills)**[learn.chatgpt.com**](https://learn.chatgpt.com/docs/build-skills)

***[Skills | OpenAI API**](https://developers.openai.com/api/docs/guides/tools-skills)

***[https://developers.openai.com/api/docs/guides/tools-skills**](https://developers.openai.com/api/docs/guides/tools-skills)

*[![](data:image/png;base64,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 "Favicon for https://developers.openai.com/api/docs/guides/tools-skills")](https://developers.openai.com/api/docs/guides/tools-skills)**[developers.openai.com**](https://developers.openai.com/api/docs/guides/tools-skills)

***[Agent Skills – Codex | OpenAI Developers**](https://developers.openai.com/codex/skills)

***[https://developers.openai.com/codex/skills**](https://developers.openai.com/codex/skills)

*[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAsTAAALEwEAmpwYAAAHWUlEQVRogb2aMWzb2BnHf4+UZLotkHdAgdMWeoo3M+iQdDI9NZvpKdmsTNfNvrFFAVFLgU6xxgyFpTGTla03FJY33xRmc4A7mAY6KECB8oBeTSsSX4cnUqIlm5R9yR/QIPLx8fve+3//73vvUfBLwFcSYg/EBmCDckBJEHKmVah/IgD1Hujjr4b3fbW485O+koh4D4ULuHd8fQCqzT2cWd6BzHC1f22E74sO0FrWkeUcaF02P4PheQh8mqut8s3LwL+0QRxpbn8RhMBWmdkwCrtqDXdBvfuCxgPYIN7hX3lFDW93oHXVRI07n5UyN0JJSI5oXTZva3UzhVpXTVTi/9Jm3Qm3xMViB/wrD5Kjsv1LS7D3xMRbN7Gl/h8MFMEgoRuM6V8kd7R81lKzQbPWnbs819C/tDXny9Fm76mJv1lBWrqrMFIA2HLadScY8+13IwCkpa9FMUSxWsaDCNTj64G9yIFzwC7TZdOt4G9WiGJF+/sxB6fjnFENx6S5WcGWgihWmZMp+qGeoc77cVknAnzr8ewVM3e/ddUEVRj5AO5Dg45XJYwUv//7kN5ZQjzKt5ErAm/dRFoCqyIIBgn/+CEhjBRWReDUDbx1E6du8N2P888vQB33z4L+X/uZS9kt/9IGzssYD3C+t4ItBWvtq4w2KWwpONyu4tpa5HpnmkLX27m2weF2FVvqmNnqDkvQSkSwsoYvIsjL6K1yNQunbmBLQScY54ySlqC5WeHdNzVc26AfJmx1h+y8+TRnPGgKPX59RTBIcOqC/SfmXJt5KAn/28/cAUqP/qzaOHXBzhtNHYDGhsmrZzqYo1jROhlzcJrnhPtw4vg1zktLzyjoGV1mFtIZcIuMt6Xg3Tc1fLeCU9d+R5fT+01XG986GbHWHuaMt6Xg6HmV40aNQ6/K+d4K7sPp5EcxdIMx0tIDUYzpLEx6EXtljLeloHc2ph8u1vUwUvj9UTaCs5Ty1k3CSNE7G2NLoZ2Z8B/I+tyol60vjU3tgNb9W+uc492aHt3+iJ03n7hYwOfr8B6Z2YwBtE5GPH6t4+HlWx0TDcfkfG+F5maF4OMyOQEAF19JgwL6NDbMLGD9k2Kdc+qC490aRy+moxtGik4wzRGdYMxa+ypTJt/VswTwU7yMD7FnFI3+rqM52Q2Kk42m2kqmQDtvhvTDBKducL63kqMMwMHpiK3ucMJ/ff2BtYwDyjEm69gb4dQFUUzpeiaMtJ5vdbVCbXWHOcoc79bYf1LJtW+8/ZTlk4Zj5u4XwDYoKBtSWSxr/Fr7ai7IU8qEkcKWglfPKpzvreA9MnLPpoksVbRiiI1CBxbVMCnkaol3zPWn6WhLwdGLvBKFka6ppEXJpCZk4YosGCikRU63g496hI+e12hulh2t1AFNmcevhxllmptTyqT5Y3u9eLEIqtiBtx908KbBrF8yznidKohcKvggGCS8fPtp7noUM6FaGQfAABXd1iCtdxqOmXOiE4wzBbGlQFr6N6sys9BtStkEULqtoeuKmxHFsPNGB1dnu5qb7lkF6YdJVtPM8lpagld/0EFblmq6Oi2leqGhd8duRzBQtCZJzHe1MbM1S6og1+Xy6HmN870a+08rhJEqpWZpv8GglPKFBiQXZVo6X2tO9sNE1/tedS4xpXKZ1jveJBDTMiIqyLLSEjQnpUeZxAnqfaXMDMwiDbzj3RoNx6ThmHSCMa2TEfYDbUC6kEnXwmVGXlqCw+1KVraUS5wiqEDcA+uwqGlqhFMX9M4S1tpXmQQ2HBNv3cg43g8TWiejuYQmLRbOglM3smo3GKhsA6AE+gb+VxHQL2rZ+6CN2X40r0StkxHSEoSR4uXbT2x1hznj3YdGVtEumg2nrtWrfTouuawEUAH+aphKygkFVWkwSHQSckza348zlUjXAAenmrOzL7elViBvXTvdD/Pabz8Q2UB039+8zlgM0YZsQRMfFOWDKIbWiTby6Hl1Tu+jWN24kEkX7FvdYW5tnOaVRXQrgT6k2yr9v8W4f1mlYBZO/5UgBHjrJvtPdQnx8b8w+Hlq+B9/Z3LoVfHWTeIR/Omf06w9i8aG7iMd/eVgdPCtLuS2Vf4jYeW8zI6c71ZyCQ3mi77bFMh9aHD0ogqQ1URLYi3doZtGZMlZgMmO2vsxFz/pDSqAeES2H7r+WwOnblD/jdArLKFnx3tk8upZFd+tEI9gqzvk7N/LGp+08H/VS/8t2FqM730WMLuluAhpMN9h5EP81bXZC/fe3L0NDcfE+dpgo67l8yKC3odl1SaFikCU2NwF8C8bQGFy+7IwdvBXenNXF7b1VztA6YO2z4+ktch4KDrk8y99ltgz/TxIWvi/9m+6W1yg+z97IA6//DmZikB8O2HDjVjimJVjSh583B8iALVT5ph1uYPuz04pFYFo46/6ZZ+4w6cGlzYkPhi7Sz97IyaGYx2kBxdlcY+PPS5twNU723dOfH3g5C6Gp7i7A7PInFHO9JOb2XhR0eSUMQAuNMet3l2NnsX/ASXqs+PyMNdsAAAAAElFTkSuQmCC "Favicon for https://developers.openai.com/codex/skills")](https://developers.openai.com/codex/skills)**[developers.openai.com**](https://developers.openai.com/codex/skills)

***[Build skills**](https://developers.openai.com/plugins/build/skills)

***[https://developers.openai.com/plugins/build/skills**](https://developers.openai.com/plugins/build/skills)

*[![](data:image/png;base64,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 "Favicon for https://developers.openai.com/plugins/build/skills")](https://developers.openai.com/plugins/build/skills)**[developers.openai.com**](https://developers.openai.com/plugins/build/skills)

*![]()**$0.1414,641 tok**

*![](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNzkuNSIgaGVpZ2h0PSIyNzkuNSIgcHJlc2VydmVBc3BlY3RSYXRpbz0ieE1pZFlNaWQiIHZpZXdCb3g9Ii0xMS43NSAtOS43NSAyNzkuNSAyNzkuNSI+PHBhdGggIGQ9Ik0yMzkuMTg0IDEwNi4yMDNhNjQuNzE2IDY0LjcxNiAwIDAgMC01LjU3Ni01My4xMDNDMjE5LjQ1MiAyOC40NTkgMTkxIDE1Ljc4NCAxNjMuMjEzIDIxLjc0QTY1LjU4NiA2NS41ODYgMCAwIDAgNTIuMDk2IDQ1LjIyYTY0LjcxNiA2NC43MTYgMCAwIDAtNDMuMjMgMzEuMzZjLTE0LjMxIDI0LjYwMi0xMS4wNjEgNTUuNjM0IDguMDMzIDc2Ljc0YTY0LjY2NSA2NC42NjUgMCAwIDAgNS41MjUgNTMuMTAyYzE0LjE3NCAyNC42NSA0Mi42NDQgMzcuMzI0IDcwLjQ0NiAzMS4zNmE2NC43MiA2NC43MiAwIDAgMCA0OC43NTQgMjEuNzQ0YzI4LjQ4MS4wMjUgNTMuNzE0LTE4LjM2MSA2Mi40MTQtNDUuNDgxYTY0Ljc2NyA2NC43NjcgMCAwIDAgNDMuMjI5LTMxLjM2YzE0LjEzNy0yNC41NTggMTAuODc1LTU1LjQyMy04LjA4My03Ni40ODNabS05Ny41NiAxMzYuMzM4YTQ4LjM5NyA0OC4zOTcgMCAwIDEtMzEuMTA1LTExLjI1NWwxLjUzNS0uODcgNTEuNjctMjkuODI1YTguNTk1IDguNTk1IDAgMCAwIDQuMjQ3LTcuMzY3di03Mi44NWwyMS44NDUgMTIuNjM2Yy4yMTguMTExLjM3LjMyLjQwOS41NjN2NjAuMzY3Yy0uMDU2IDI2LjgxOC0yMS43ODMgNDguNTQ1LTQ4LjYwMSA0OC42MDFabS0xMDQuNDY2LTQ0LjYxYTQ4LjM0NSA0OC4zNDUgMCAwIDEtNS43ODEtMzIuNTg5bDEuNTM0LjkyMSA1MS43MjIgMjkuODI2YTguMzM5IDguMzM5IDAgMCAwIDguNDQxIDBsNjMuMTgxLTM2LjQyNXYyNS4yMjFhLjg3Ljg3IDAgMCAxLS4zNTguNjY1bC01Mi4zMzUgMzAuMTg0Yy0yMy4yNTcgMTMuMzk4LTUyLjk3IDUuNDMxLTY2LjQwNC0xNy44MDNaTTIzLjU0OSA4NS4zOGE0OC40OTkgNDguNDk5IDAgMCAxIDI1LjU4LTIxLjMzM3Y2MS4zOWE4LjI4OCA4LjI4OCAwIDAgMCA0LjE5NSA3LjMxNmw2Mi44NzQgMzYuMjcyLTIxLjg0NSAxMi42MzZhLjgxOS44MTkgMCAwIDEtLjc2NyAwTDQxLjM1MyAxNTEuNTNjLTIzLjIxMS0xMy40NTQtMzEuMTcxLTQzLjE0NC0xNy44MDQtNjYuNDA1di4yNTZabTE3OS40NjYgNDEuNjk1LTYzLjA4LTM2LjYzTDE2MS43MyA3Ny44NmEuODE5LjgxOSAwIDAgMSAuNzY4IDBsNTIuMjMzIDMwLjE4NGE0OC42IDQ4LjYgMCAwIDEtNy4zMTYgODcuNjM1di02MS4zOTFhOC41NDQgOC41NDQgMCAwIDAtNC40LTcuMjEzWm0yMS43NDItMzIuNjktMS41MzUtLjkyMi01MS42MTktMzAuMDgxYTguMzkgOC4zOSAwIDAgMC04LjQ5MiAwTDk5Ljk4IDk5LjgwOFY3NC41ODdhLjcxNi43MTYgMCAwIDEgLjMwNy0uNjY1bDUyLjIzMy0zMC4xMzNhNDguNjUyIDQ4LjY1MiAwIDAgMSA3Mi4yMzYgNTAuMzkxdi4yMDVaTTg4LjA2MSAxMzkuMDk3bC0yMS44NDUtMTIuNTg1YS44Ny44NyAwIDAgMS0uNDEtLjYxNFY2NS42ODVhNDguNjUyIDQ4LjY1MiAwIDAgMSA3OS43NTctMzcuMzQ2bC0xLjUzNS44Ny01MS42NyAyOS44MjVhOC41OTUgOC41OTUgMCAwIDAtNC4yNDYgNy4zNjdsLS4wNTEgNzIuNjk3Wm0xMS44NjgtMjUuNTggMjguMTM4LTE2LjIxNyAyOC4xODggMTYuMjE4djMyLjQzNGwtMjguMDg2IDE2LjIxOC0yOC4xODgtMTYuMjE4LS4wNTItMzIuNDM0WiIvPjwvc3ZnPgo= "Favicon for openai")**GPT Sol Latest**

# ***Story Director Skill Implementation Plan**

***Status: Design proposal only. No Skill, scripts, integrations, or capabilities described below have been implemented.**

***Purpose: Turn an existing story or script into a coherent creative production plan—useful as a standalone storyboard and compatible with future Narration Studio and Movie Builder Skills.**

***The central boundary is:**

***Story Director decides what the audience should see, why, and relative to which spoken events. It does not measure audio or render the movie.***


## ***1. Proposed Skill name and triggering description**

### ***Name**

***Story Director**

***Suggested package identifier: `story-director`.**

### ***Proposed triggering description**

***Analyze an existing story or script and plan its visual presentation. Use for storyboards, shot lists, image prompts, speaker and performance directions, narrative beats, comedy timing, reveal protection, and visual-asset reuse. Preserve the source wording unless rewriting is requested. Produce a readable creative plan and optionally structured data for narration and movie-production workflows. Does not synthesize speech, measure audio timing, generate images, or render video.***

### ***Example triggers**

- “***Storyboard this story.”**

- “***Turn this script into a narrated-video shot plan.”**

- “***Plan the visual jokes without changing my dialogue.”**

- “***Create image prompts and character descriptions for this documentary.”**

- “***Direct this lesson using chalkboard graphics.”**

- “***Make a production plan with no more than eight new images.”**

### ***Boundaries**

***The Skill should not automatically rewrite, shorten, fact-check, narrate, or render the source as part of ordinary direction.**

***It may:**

- ***Flag a questionable claim.**

- ***Suggest an optional edit separately.**

- ***Request clarification where necessary.**

- ***Provide specifications for other tools.**

***It must distinguish planned, provided, and verified assets. An image prompt is not a generated image.**


## ***2. Standalone workflows**

***The Skill should deliver value without either companion Skill.**

### ***Workflow A — Complete visual direction**

***Input: Story plus optional style and budget.**

***Output:**

1. ***Creative approach.**

2. ***Narrative beat map.**

3. ***Speaker and character notes.**

4. ***Storyboard or shot table.**

5. ***Asset list and image prompts.**

6. ***Performance and timing intentions.**

7. ***Open issues and assumptions.**

***Example request:**

“***Direct this DOOM story as a deadpan mockumentary. Preserve the wording and use at most eight new illustrations.”***

### ***Workflow B — Storyboard only**

***Input: Script.**

***Output: A readable storyboard with visual descriptions, shot purposes, and script references.**

***This should not require the user to receive or understand JSON.**

***Example request:**

“***Give me a storyboard I can hand to a human editor.”***

### ***Workflow C — Direct using existing assets**

***Input: Script plus images, thumbnails, or an asset inventory.**

***Output: A shot plan prioritizing reuse, with missing visual needs identified.**

***If images cannot be inspected, the Skill must say that assignments are based on descriptions rather than confirmed visual contents.**

***Example request:**

“***Use these classroom pictures and suggest new images only where necessary.”***

### ***Workflow D — Timing and performance notes**

***Input: Script or existing shot plan.**

***Output: Setup/reveal/reaction annotations, pause requests, speaker directions, and protected information-release points.**

***Example request:**

“***Find the jokes and mark where the visual should wait before revealing them.”***

### ***Workflow E — Targeted revision**

***Input: Existing plan and a requested change.**

***Output: Revised affected objects plus a change summary.**

***Example request:**

“***Replace the classroom reaction with a clock shot, but keep the rest of the plan.”***

***Default behavior: Produce a complete first draft. Ask questions only when a missing decision would materially change the result; otherwise record reasonable assumptions.**


## ***3. Cooperative workflow and shared-data requirements**

### ***Division of responsibility**

| Responsibility | Story Director | Narration Studio | Movie Builder |
| - | - | - | - |
| Preserve and reference script | Defines source references | Uses references | Uses references |
| Speakers and performance intent | Proposes | Realizes or reports limitations | Consumes |
| Requested pauses | Specifies intent | Creates or measures when possible | Uses available timing |
| Visual beats and shots | Plans | — | Realizes |
| Actual audio timestamps | Consumes when available | Produces | Consumes |
| Image prompts and asset reuse | Specifies | — | Generates/selects |
| Rendering and technical QA | — | Audio-related checks | Produces |
| Creative revision | Revises plan | Reports performance issues | Reports realization issues |

***These are proposed ownership boundaries, not assumptions about already available integrations.**

### ***Cooperative sequence**

1. ***Story Director creates the creative plan.**

2. ***Narration Studio produces or analyzes narration and returns timing and capability information.**

3. ***Movie Builder resolves visual instructions against actual assets and audio.**

4. ***Unresolved creative decisions may return to Story Director for a targeted revision.**

***For supplied audio, timing information may arrive before direction. For generated narration, performance direction may arrive before timing.**

***No fixed production order is required.**

### ***Minimum shared information**

- ***Plan version.**

- ***Source revision identifier.**

- ***Stable script segment IDs.**

- ***Speaker IDs.**

- ***Asset IDs and availability status.**

- ***Shot IDs.**

- ***Script-relative timing anchors.**

- ***Performance and pause intentions.**

- ***Budget constraints.**

- ***Explicit assumptions and unresolved items.**

### ***Stable identifiers**

***Assign IDs once and preserve them during unrelated revisions.**

***Do not derive IDs solely from sentence text: identical sentences can occur in different places.**

***A source update should carry an explicit revision identifier. Anchors must be revalidated against that revision. Deleted or substantially changed segments must not silently retain an apparently valid reference.**

### ***Cooperation without installed companions**

***The Skill should export files or structured text that can be transferred manually.**

***Do not assume Skills can discover or invoke one another. Invocation mechanics depend on the eventual host environment and remain provisional.**


## ***4. Recommended `SKILL.md` structure**

***Keep `SKILL.md` focused on operating instructions. Put detailed schemas and examples in reference files.**

### ***Proposed outline**

1. ***Metadata**

   - ***Name.**

   - ***Triggering description.**

   - ***Scope.**

2. ***Core rules**

   - ***Preserve source wording.**

   - ***Produce a complete draft by default.**

   - ***Separate creative intent from measured timing.**

   - ***Do not claim planned media exists.**

   - ***Respect asset limits.**

3. ***Choose workflow**

   - ***Complete direction.**

   - ***Storyboard.**

   - ***Existing-asset planning.**

   - ***Timing/performance annotations.**

   - ***Targeted revision.**

4. ***Inspect inputs**

   - ***Source completeness.**

   - ***Available media.**

   - ***Style.**

   - ***Budget.**

   - ***Supplied-audio constraints.**

5. ***Build the plan**

   - ***Establish source references.**

   - ***Identify beats.**

   - ***Choose visual strategy.**

   - ***Allocate assets.**

   - ***Define shots and timing intentions.**

6. ***Validate**

   - ***Source preservation.**

   - ***References.**

   - ***Coverage.**

   - ***Reveal protection.**

   - ***Budget.**

   - ***Unsupported assumptions.**

7. ***Deliver**

   - ***Human-readable plan first.**

   - ***Structured export when requested or needed for cooperation.**

   - ***Assumptions and unresolved items.**

8. ***Revise**

   - ***Preserve unaffected IDs.**

   - ***Apply overrides.**

   - ***Summarize changes.**

9. ***Reference index**

   - ***Links to relevant supporting files.**

***Provisional: Exact metadata syntax and packaging requirements should be checked against the target Skill platform before implementation.**


## ***5. Proposed reference files, assets, and optional scripts**

### ***Minimal proposed package**

```
***`story-director/`**

`├── ***SKILL.md`**

`├── ***references/`**

`│   ├── ***creative-plan-format.md`**

`│   ├── ***directing-guidelines.md`**

`│   ├── ***timing-and-performance.md`**

`│   └── ***acceptance-tests.md`**

`└── ***examples/`**

`    ├── ***doom\_excerpt\_plan.json`**

`    ├── ***educational\_storyboard.md`**

`    └── ***existing\_assets\_plan.md`**
```

### ***Reference contents**

| File | Purpose |
| - | - |
| **`creative-plan-format.md`** | Fields, IDs, anchors, ownership, revision rules |
| **`directing-guidelines.md`** | Fiction, documentary, educational, and comedy guidance |
| **`timing-and-performance.md`** | Reveals, holds, pauses, performance notes, audio constraints |
| **`acceptance-tests.md`** | Test inputs and expected observable behavior |

***Examples should demonstrate different planning decisions, not become mandatory templates.**

### ***Assets**

***Include lightweight storyboard and character-description templates if they prove useful.**

***Do not initially bundle:**

- ***TTS models.**

- ***Image-generation models.**

- ***FFmpeg.**

- ***Stock-media collections.**

- ***A large style-preset library.**

### ***Optional scripts, later**

- ***`validate\_plan.py`: check references, required fields, and budget counts.**

- ***`export\_storyboard.py`: convert structured plans into a readable table.**

- ***`check\_source\_references.py`: detect invalid anchors after source changes.**

***These should support deterministic checks, not attempt to judge whether a joke is funny.**

***Initial dependency recommendation: No external model SDK or media dependency. Optional validators can use the Python standard library, with formal JSON Schema validation considered later.**


## ***6. Inputs, outputs, and proposed JSON**

### ***Inputs**

***Required:**

- ***Story or script as pasted text, `.txt`, or `.md`.**

***Optional:**

- ***Visual mode.**

- ***Aspect ratio.**

- ***Asset inventory.**

- ***Character references.**

- ***New-image limit.**

- ***Existing audio timing.**

- ***Desired audience.**

- ***Manual overrides.**

- ***Permission to rewrite or edit supplied audio.**

***A desired runtime is a constraint, not permission to silently shorten the script.**

### ***Outputs**

***Human-readable**

- ***Creative brief.**

- ***Beat map.**

- ***Shot plan.**

- ***Asset prompts.**

- ***Performance notes.**

- ***Assumptions and unresolved issues.**

***Structured**

- ***`creative\_plan.json`.**

***No synthesized audio, generated images, or MP4 is promised by this Skill.**

### ***Example JSON**

***This example uses multiple shots for one spoken sentence, then requests a reaction pause. The pause is not treated as already present in audio.**

```
***`\{`**

`  ***"schema\_version": "0.1-draft",`**

`  ***"plan\_id": "doom\_excerpt",`**

`  ***"source\_revision": "r1",`**

`  ***"style": \{`**

`    ***"mode": "illustrated\_mockumentary",`**

`    ***"tone": "deadpan",`**

`    ***"aspect\_ratio": "16:9"`**

`  ***\},`**

`  ***"budget": \{`**

`    ***"max\_new\_generated\_images": 2`**

`  ***\},`**

`  ***"script\_segments": \[`**

`    ***\{`**

`      ***"id": "seg\_001",`**

`      ***"speaker\_id": "narrator",`**

`      ***"text": "The first frame took fourteen hours."`**

`    ***\}`**

`  ***\],`**

`  ***"speakers": \[`**

`    ***\{`**

`      ***"id": "narrator",`**

`      ***"performance": "Calm and serious; avoid announcing the joke."`**

`    ***\}`**

`  ***\],`**

`  ***"beats": \[`**

`    ***\{`**

`      ***"id": "beat\_001",`**

`      ***"segment\_ids": \["seg\_001"\],`**

`      ***"purpose": "Reveal absurdly slow progress."`**

`    ***\}`**

`  ***\],`**

`  ***"assets": \[`**

`    ***\{`**

`      ***"id": "asset\_board",`**

`      ***"kind": "generated\_image",`**

`      ***"status": "planned",`**

`      ***"prompt": "Documentary-style illustration of a student carefully drawing a game frame on a classroom chalkboard. Wide composition. No readable text."`**

`    ***\},`**

`    ***\{`**

`      ***"id": "asset\_reaction",`**

`      ***"kind": "generated\_image",`**

`      ***"status": "planned",`**

`      ***"prompt": "Same classroom and student design, exhausted expression, chalk-covered hands, deadpan mockumentary composition. No readable text."`**

`    ***\}`**

`  ***\],`**

`  ***"pause\_requests": \[`**

`    ***\{`**

`      ***"id": "pause\_001",`**

`      ***"after\_segment\_id": "seg\_001",`**

`      ***"purpose": "Allow the absurd statistic to land.",`**

`      ***"length\_intent": "brief",`**

`      ***"if\_unavailable": "omit\_reaction\_hold"`**

`    ***\}`**

`  ***\],`**

`  ***"shots": \[`**

`    ***\{`**

`      ***"id": "shot\_001",`**

`      ***"beat\_id": "beat\_001",`**

`      ***"asset\_id": "asset\_board",`**

`      ***"purpose": "setup",`**

`      ***"start": \{`**

`        ***"segment\_id": "seg\_001",`**

`        ***"boundary": "start"`**

`      ***\},`**

`      ***"end": \{`**

`        ***"segment\_id": "seg\_001",`**

`        ***"phrase": "fourteen",`**

`        ***"occurrence": 1,`**

`        ***"edge": "start"`**

`      ***\},`**

`      ***"camera": "slow\_zoom"`**

`    ***\},`**

`    ***\{`**

`      ***"id": "shot\_002",`**

`      ***"beat\_id": "beat\_001",`**

`      ***"asset\_id": "asset\_board",`**

`      ***"purpose": "reveal",`**

`      ***"start": \{`**

`        ***"segment\_id": "seg\_001",`**

`        ***"phrase": "fourteen",`**

`        ***"occurrence": 1,`**

`        ***"edge": "start"`**

`      ***\},`**

`      ***"end": \{`**

`        ***"segment\_id": "seg\_001",`**

`        ***"boundary": "end"`**

`      ***\},`**

`      ***"overlay": \{`**

`        ***"text": "14 HOURS",`**

`        ***"render\_method": "programmatic"`**

`      ***\},`**

`      ***"reveal\_policy": "no\_visual\_or\_caption\_spoiler\_before\_start"`**

`    ***\},`**

`    ***\{`**

`      ***"id": "shot\_003",`**

`      ***"beat\_id": "beat\_001",`**

`      ***"asset\_id": "asset\_reaction",`**

`      ***"purpose": "reaction",`**

`      ***"during\_pause\_request\_id": "pause\_001",`**

`      ***"camera": "static"`**

`    ***\}`**

`  ***\],`**

`  ***"assumptions": \[`**

`    ***"Narration has not yet been measured.",`**

`    ***"The requested reaction pause may be unavailable in supplied audio."`**

`  ***\]`**

***`\}`**
```

### ***Important schema choices**

- ***Phrase anchors include an occurrence number to disambiguate repeated phrases.**

- ***The source revision protects against stale references.**

- ***Exact-text overlays are separate from image prompts.**

- ***Requested pauses are distinct from measured silence.**

- ***No authoritative audio timestamps appear.**

- ***Asset generation status is explicit.**

***Provisional: Phrase anchors versus character-span anchors should be finalized jointly. Character spans are precise but vulnerable to source edits; phrase anchors are readable but require ambiguity checks.**


## ***7. How the LLM should plan visual beats and comedy**

***The Skill should use a consistent decision process and expose its decisions through concise rationales—not require lengthy internal reasoning transcripts.**

### ***Step 1 — Establish narrative intent**

***Identify:**

- ***Genre and audience.**

- ***Central conflict or teaching objective.**

- ***What viewers should understand or feel.**

- ***Whether the source depends on factual precision, suspense, humor, or emotional continuity.**

### ***Step 2 — Identify beats across sentence boundaries**

***A beat is a meaningful change in information, action, emotion, or audience expectation.**

***Examples:**

- ***Establish the classroom experiment.**

- ***Explain how the students simulate a computer.**

- ***Reveal the first-frame duration.**

- ***Hold on the consequences.**

- ***Escalate to the door-opening animation.**

***A beat may span several sentences. One sentence may contain several beats.**

### ***Step 3 — Assign each shot a purpose**

***Use a small vocabulary:**

- ***Establish.**

- ***Explain.**

- ***Show action.**

- ***Reveal.**

- ***Contrast.**

- ***React.**

- ***Bridge.**

***If a proposed shot has no clear purpose, consider removing it or extending the previous shot.**

### ***Step 4 — Allocate assets before overproducing prompts**

***Prefer:**

1. ***Suitable provided assets.**

2. ***Reuse of planned assets with a different crop or treatment.**

3. ***Programmatic graphics.**

4. ***New image generation where it adds clear value.**

***Do not disguise repetition as variety by prescribing excessive zooms and pans.**

### ***Step 5 — Plan information release**

***For comedy and suspense, distinguish:**

- ***Setup information.**

- ***Payoff information.**

- ***Earliest permissible reveal.**

- ***Optional reaction or hold.**

***Reveal protection should cover captions and overlays, not only background images.**

***For “fourteen hours,” displaying the complete sentence early in a caption can spoil the reveal even if the image is correct.**

### ***Step 6 — Request performance, not pretend to control it**

***Useful:**

“***Keep delivery matter-of-fact; do not emphasize the absurd number theatrically.”***

***Less useful:**

“***Make this hilarious.”***

***Performance requests must remain advisory until Narration Studio reports what its backend can express.**

### ***Step 7 — Review the sequence as a whole**

***Check:**

- ***Excessive cuts.**

- ***Repetitive visuals.**

- ***Unnecessary new assets.**

- ***Premature reveals.**

- ***Missing explanations.**

- ***Holds that depend on nonexistent silence.**

- ***Educational graphics that need exact rendering.**

***Comedy annotations are hypotheses. Their effectiveness requires playback evaluation later.**


## ***8. Failure handling and graceful fallbacks**

| Problem | Required behavior |
| - | - |
| No style supplied | Select a modest default and state the assumption |
| No budget supplied | Propose an asset count; do not claim spending authorization |
| No images available | Produce prompts and planned assets, not pretend images exist |
| Images cannot be inspected | Mark assignments as description-based |
| No audio timing | Use script anchors and pause requests |
| Supplied audio lacks a requested pause | Provide an alternate shot treatment |
| Source changed | Flag affected anchors for revalidation |
| Speaker identity unclear | Use a neutral provisional label |
| Budget too small | Reuse assets and graphics; explain remaining compromises |
| Desired runtime conflicts with script | Offer alternatives without silently rewriting |
| Questionable factual content | Flag separately; do not invent a correction |
| Story too long for reliable single-pass planning | Plan sections, then perform a continuity review |

### ***Manual overrides**

***Support optional overrides for:**

- ***Style.**

- ***Asset choice.**

- ***Shot purpose.**

- ***Reveal anchor.**

- ***Performance instruction.**

- ***Asset limits.**

- ***Locked shots.**

***Locked choices should survive ordinary regeneration. If a locked choice becomes invalid after source changes, report the conflict instead of silently replacing it.**


## ***9. Development milestones and acceptance tests**

### ***Milestone 1 — Standalone directing behavior**

***Design and test the core instructions using fiction, comedy, educational, and documentary samples.**

***Pass conditions:**

- ***Source wording remains unchanged.**

- ***Complete shot plans are produced without manual timing metadata.**

- ***At least one test demonstrates a shot spanning multiple sentences.**

- ***At least one demonstrates multiple shots within one sentence.**

- ***New-image counts respect explicit limits.**

- ***Missing companions do not block delivery.**

### ***Milestone 2 — Structured export**

***Add the draft format and examples.**

***Pass conditions:**

- ***All referenced IDs exist.**

- ***All phrase anchors match the specified source.**

- ***No invented measured timestamps.**

- ***Planned and provided assets are distinguishable.**

- ***Unresolved requirements are explicit.**

### ***Milestone 3 — Revision and existing-asset workflow**

***Test targeted changes and locked overrides.**

***Pass conditions:**

- ***Replacing one asset preserves unrelated IDs.**

- ***Editing one script segment identifies affected anchors.**

- ***Existing assets are reused where appropriate.**

- ***Uninspected media are not described as visually verified.**

### ***Milestone 4 — Companion handoff**

***Use mock Narration Studio and Movie Builder responses before relying on actual integrations.**

***Pass conditions:**

- ***A missing pause triggers a usable fallback.**

- ***A low-confidence reveal anchor is flagged.**

- ***Unsupported emotional delivery is not reported as achieved.**

- ***A rejected image request can be replaced without rebuilding the whole plan.**

### ***Representative DOOM test**

***Provide a short excerpt and a small classroom asset inventory.**

***Require the Skill to produce:**

- ***An explanatory hold.**

- ***A protected “14 HOURS” reveal.**

- ***A conditional reaction shot.**

- ***Narrator performance notes.**

- ***A readable storyboard.**

- ***Valid structured output.**

- ***No more than the permitted new images.**

***This tests Story Director’s planning, not finished-video watchability. The integrated toolkit must later test whether the resulting film actually works.**


## ***10. Risks and implications for the other Skills**

### ***Primary risks**

1. ***Coherent descriptions, weak filmmaking  
A plausible shot list can still produce a dull video. Integrated playback tests are essential.**

2. ***Brittle source anchors  
Script normalization, pronunciation substitutions, and edits can break references.**

3. ***Unrealizable direction  
Requested pauses, voices, character consistency, or image treatments may exceed downstream capabilities.**

### ***Requirements affecting Narration Studio**

- ***Preserve original-script references separately from speech-normalized text.**

- ***Return actual timing without redefining the source.**

- ***Distinguish requested pauses from generated or detected pauses.**

- ***Report unsupported performance instructions.**

- ***Associate regenerated audio with a source and audio revision.**

***The Read-Aloud-style segmented narration approach is compatible, but speech chunks must not dictate visual shot boundaries.**

### ***Requirements affecting Movie Builder**

- ***Resolve anchors using timing data.**

- ***Respect reveal constraints across overlays and captions.**

- ***Maintain local asset identity and availability.**

- ***Report failed realization rather than silently making major creative substitutions.**

- ***Keep technical QA separate from creative confidence.**

### ***Important assumption**

***A ChatGPT Skill supplies instructions, references, and potentially helper scripts. It does not itself guarantee access to image inspection, external tools, persistent storage, or companion-Skill invocation. Each workflow must state which capabilities it needs and offer a text-only fallback.**


## ***Ideas Worth Revisiting in Round 4**

1. ***Finalize the shared contract.  
Agree on field names, ownership, revision handling, and the smallest required objects after all three Skills are designed.**

2. ***Choose the canonical anchor format.  
Compare phrase occurrences, character spans, and downstream word IDs. Avoid incompatible schemes across Skills.**

3. ***Define pause semantics.  
Decide how qualitative requests such as “brief reaction hold” become measurable audio decisions, especially with authoritative supplied recordings.**

4. ***Define the override format.  
Determine which changes belong in the creative plan versus downstream timing overrides.**

5. ***Separate budget types.  
New-image count, monetary authorization, retry allowance, and asset reuse are related but not interchangeable.**

6. ***Clarify capability negotiation.  
Decide how Narration Studio and Movie Builder report unsupported instructions without creating a large capability framework.**

7. ***Handle caption spoilers.  
Agree on how word- or phrase-level caption display preserves reveals while maintaining readability and accessibility.**

8. ***Choose the first end-to-end test.  
Use the same DOOM excerpt across all three Skills so individual acceptance tests culminate in one automatically planned, watchable demonstration.**

9. ***Confirm host-platform packaging and invocation.  
Finalize `SKILL.md` metadata and cooperation mechanics only after checking the actual environment.**

10. ***Keep the core distinction intact.  
Story Director owns creative intent; Narration Studio owns audio realization and measurement; Movie Builder owns visual realization and rendering. Revisit exceptions only when an actual test shows they are needed.**

