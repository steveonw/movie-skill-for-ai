# Conversation History and Four-Prompt Design Process (Reconstructed)

**2026-10-14; project status: planning only.** This document reconstructs substantial context from the originating conversation. It is NOT a verbatim transcript. For complete AI responses see `research/ARCHIVE_INVENTORY.md` and the original Markdown research archive once uploaded.

## Originating motivation

User wants to automate illustrative narrated videos (deadpan mockumentaries, absurd comedy, educational review lessons) by combining a written story, optional human-recorded MP3 or synthesized speech, AI still illustrations, narration-driven images, motion/holds/cuts, captions, programmatic statistics/equations, and FFmpeg video rendering. Costs should remain low. User prefers practical, modular, verifiable work, no complex human-editing requirements, no full generative animation requirement.

Example `DOOM: Chalkboard Edition`: students manually redraw a first-person shooter on a chalkboard; 14 hours per frame; bored sound-effects man says `Bang`; 23 days to reach a door; Kevin shouts about already knowing what a door looks like; final 563-hour YouTube video gets twelve views and sarcastic comments, including `Bro invented PowerPoint`. These plot details and user-provided lines are background for tests. The complete original story was not committed.

An earlier approximately 8m50s calculus exam review video used generated images with narration, but the video artifact itself is not in this repository. A previous review noted some visuals didn't track the spoken mathematical subject perfectly. Therefore semantic coherence matters as well as audio duration.

## Initial AI-to-AI handoff

A long comprehensive project handoff was drafted covering goals, an image-stills pipeline, multi-stage workflow (story -> LLM director -> image generation -> TTS or user audio -> speech alignment -> Python/FFmpeg editing -> QA), an example directory layout, Hugging Face as an optional inference source, and first milestone: supplied story + MP3 + images -> synced MP4. Proposed services/models included possible FLUX.1 Schnell illustrations; Piper, Kokoro, Kyutai Pocket TTS and instruct-capable alternatives like CosyVoice; faster-whisper/forced alignment. Availability, licenses and fees were not verified globally. Generated code examples from outside AIs were critiqued, including misuse of FFmpeg concat to mux one video stream and one audio stream.

## Four-AI critique, first major correction

Reviews agreed on FFmpeg, audio-authoritative timing, reusable images, separation of audio segments from visual shots, caching and early demo before polishing. A challenge was raised: accurate word alignment does not make a system a creative film director. An aligner answers WHEN, while a director determines WHAT and WHY viewers see it. Comedy needs timed reveals, holds, reaction shots and no premature captions. Shared manifest should retain both timing intent and editorial intent.

Another challenge: a completed video from a supplied narration must align to spoken audio; if TTS is being generated, directing the narrator's performance and pauses before synthesis is reasonable. Thus separate generated-audio and provided-audio entry paths should converge on an interchangeable narration timeline.

The user stressed the objective is AI filmmaking automation, not an editing utility that requires a person to author every cut.

## Read-Aloud-Main discovery

User raised `https://github.com/steveonw/Read-Aloud-Main`. The repository is a cross-platform portable browser/WASM read-aloud/proofreading application. Its `buildNarrationPcm()` in `web/app.js` constructs a single waveform from cached sentence-level TTS chunks, integer-sample lengths and inserted zero-sample gaps. It exports WAV or MP3 and optional Audacity clip labels. This means generated audio can preserve clip start/end timing instead of transcribing its own output to recover it. But that does not supply word-internal start times; engine silence/padding matters for audible onset. Its existing cache is not a project-persistent disk cache. Extending Read-Aloud or implementing this pattern in Python were discussed; not decided.

## Three independent Skills proposal

User preferred three useful Skills that cooperate well but **are never dependencies of one another**:

- Story Director: analyze story, create storyboard, speaker/character/style/beat sheet, prompts, anchored shot directions. Standalone storyboarding useful.
- Narration Studio: TTS, voice casting, pronunciation dictionary, chunk-and-cache, WAV/JSON timings, optional SRT/Audacity labels or external MP3 alignment. Standalone audiobook/voiceover useful.
- Movie Builder: produce videos from assets and MP3 without the other Skills, or accept their shared files, render with FFmpeg, generate image assets if backend exists, create cards and QA. Standalone slideshow/explainer useful.

The phrase **Standalone First, Cooperative by Design** was selected. User then suggested three planning prompts, one per Skill, and a fourth to revise all three, allowing a great idea from the third to improve the first.

## The four planning prompts, original intent

Round 1 asked an AI to *design, not implement* Story Director, including YAML trigger description, standalone capabilities and examples, cooperative output, SKILL.md contents, scripts/references/assets, script/shot IDs, timing expressed as words/segments rather than invented seconds, comedic beat reasoning, budgets, failure handling, tests, deferred ideas and a mandatory `Ideas Worth Revisiting in Round 4` section.

Round 2 asked for a similarly comprehensive Narration Studio design: local/hosted TTS, audio files, generated and recorded-audio paths, verified Read-Aloud-Main concepts, per-clip caching, pronunciation, pause events, precise boundary timing, optional word alignment, multiple voices, licensing, example JSON, tests and revisions proposed to Round 1; do not confuse clip boundaries and word timing.

Round 3 asked for a similarly comprehensive Movie Builder design: standalone MP3+images video, compatible shared manifests, FFmpeg, still image providers (including HF if truly hosted), placeholder animatics, camera moves/holds/fades, caption safety, title cards and equations, content-addressed visual caching, measured cost limits, technical/semantic QA, runnable first demonstration and earlier-plan revision proposals.

Round 4 asked an AI to examine all three provisional plans and **challenge, reconcile and revise** them, including contradictions in segmentation, shared schema, alignment, caption ownership, prompt formation, creative overrides, failure handling, versioning, test fixtures, implementation order, and how to change Skill 1 if Skills 2 or 3 discovered a better pattern. It requested revised concrete plans for all Skills plus shared contract, test matrix, decision log and packaging approach. No implementation yet.

Four large Markdown files contain responses from Gemini/Claude/Grok/GPT to these four prompts. Their raw files were uploaded to chat, and their exact checksums are recorded in `research/ARCHIVE_INVENTORY.md`.

## Important expert disagreement across reviewers

- **Segmentation:** one deterministic shared tokenizer with stable segment/word IDs vs independent scripts with a small shared specification. Large copied `filmkit_core.py` was proposed, then critiqued as premature complexity. Need a minimal tested fixture and shared version contract.
- **Timeline ownership:** Story Director gives word/segment anchors; Narration Studio timestamps speech; Movie Builder resolves anchors to video frames. Some proposed a shared anchor-resolver helper; others Narration Studio exporting a pre-resolved file. Avoid multiple contradictory sources of truth.
- **Audio units:** use integer audio samples, not cumulative float durations, for generated WAV/gaps. Tag word timing as manually set/model-predicted/forced-aligned/measured instead of claiming precision not delivered by the engine.
- **Original vs spoken:** captions honor original numbers/notation, TTS uses pronounceable versions and keeps mapping. One model suggested `script.json` should never copy text into `plan.json`; the key principle is preserving original source text.
- **Script anchors:** exact word IDs and segment IDs rather than locating an ambiguous repeated word string, with a safe fallback for missing/changed words.
- **Comedy:** early proposals mandated hard cuts for every payoff; corrected to creative discretion. Non-spoiling captions and overlays important. Show a relevant reveal at or after its intended word's audible onset.
- **Image prompts:** separate subject/character/style from model adapter implementation. Reuse stills and crop differently. Render required text/statistics/equations separately.
- **Rendering:** FFmpeg filtergraph/zoompan vs Python frame generator vs per-shot cached intermediates. Per-shot caching is elaborate and can cause dual encodes. Start simple and benchmark. Never claim video completes in seconds without test.
- **QA:** syntax/schema/codec/timing checks deterministic, vision-semantic judgments advisory. Intentionally ironic images are not errors. Report asset failure clearly; incomplete placeholders okay for animatics, not as quietly accepted final movie.
- **Hugging Face:** public model repository is not equivalent to deployed inference. Costs, licenses, endpoint access change.
- **Audio acting:** lightweight local TTS can be cheap but may fail to deliver anger/flat irony convincingly. Instruct models can be heavier or hosted.
- **License:** verify each voice model/aligner and any hosted image generation commercial rights; don't infer from engine package.
- **Versioning:** provisional format `filmkit/<kind>@1.0`, compatible readers on optional additive fields, migrate breaking changes.

## Prior review verdict

Gemini favored straightforward assembly but occasionally overpromised free hosted generation or silent placeholder fallback. Claude produced rigorous timing sources/tests and detailed common contract but a large shared library and extensive QA risk overengineering. Grok enforced scope and precise spoiler avoidance but some rigid limits risk creative inflexibility. GPT balanced modular independent use and gradual engineering but still needed empirical testing.

The recommendation at the end of the four-AI comparison was: first prove Movie Builder's supplied-images+audio output, then Narration Studio's clip timing/caching, then Story Director's prompt-and-plan generation, finally a DOOM 60–90-second integrated video with a correctly timed `Bang` reveal and reaction hold. This is a pragmatic sequence, not a law; the end state has Story Director as the creative brain.

## Preservation and next action

On 2026-10-14 a new public GitHub repository `steveonw/movie-skill-for-ai` received README, AI_HANDOFF, ARCHITECTURE, DECISIONS and ROADMAP. User objected to losing original detail and asked to preserve more. This document and inventory extend the checkpoint. **The raw AI response files require a separate upload, tracked in `research/ARCHIVE_INVENTORY.md`.**

For a fresh assistant: read these notes; use the original source archive when available; verify existing code and repo state; avoid declaring imagined implementation; deliver actual tested artifacts and keep GitHub documentation updated after changes. Never assume public GitHub is a safe place for keys, unpublished voice recordings, or sensitive material.
