# AI-to-AI Handoff — Resume This Project

**Last curated:** 2026-10-14. **Read this entire file at the beginning of any new chat or coding session.**

## READ THIS FIRST — MISSION, NOT CLOCK-IN PROCEDURE

The owner wants **a functioning, low-cost filmmaking workflow**, not a project-management simulation. We are building **three independently useful ChatGPT Skills**: Story Director (creative plan), Narration Studio (voice and measured timing), Movie Builder (visual composition and MP4 rendering). They can optionally exchange `script.json`, `plan.json`, `narration.json`, and `timeline.json`.

The optional [AI Workshop Protocol](WORKSHOP.md) exists to help AI sessions coordinate through GitHub. Clock-in/out comments are **not** the goal, are not a prerequisite for helping the user, and do not imply autonomous background execution. A new AI should learn the product objective, inspect current code and open issues, then work on a concrete filmmaking milestone. If GitHub issue comments are unavailable, proceed and leave a handoff in your normal response.

**Repo/PR state at this documentation update:** `main` contains durable research, the user-provided calculus sample MP4, and project docs. A first 5-image/7s synthetic-audio Movie Builder technical prototype was merged into `main` via PR #3 (squash commit `3d290561055ed95a5dcddfa1d9f7159601e637f9`). It is not a finished Skill. Issue #1 tracks the remaining checks. **Continue to verify live repository state before making progress claims.**

## Why this exists

The conversation that led to this design was large. The user created `https://github.com/steveonw/movie-skill-for-ai` as a **durable project memory** so a future assistant can continue without depending on previous chat context. Preserve and update this handoff as decisions or implementations change. Do not assert a feature is functional until tested.

## User's actual objective

User writes humorous short stories and wants a low-cost, mostly automatic way to create narrated documentary/mockumentary-style videos: story in, optional narrator MP3 in, AI directs illustrations, aligns pictures to spoken content, uses pans/zooms/cards/captions, exports MP4. AI stills plus traditional editing are preferred to expensive fully generated motion video.

The example short story is **“DOOM: Chalkboard Edition”**: students simulate DOOM by hand-drawing frames on a chalkboard, 14 hours per frame, a bored man says “Bang,” a 23-day door sequence, exhausted Kevin, terrible frame rates, and absurd YouTube comments. Humor comes from rigorous, serious documentary presentation of an inherently silly undertaking. Exact statistics are better code-rendered than entrusted to image models; protect comedic reveals.

An earlier **MTH263 Calculus Exam Review** video, approximately 8m50s, used AI-generated educational still pictures, narration and automated assembly. User considers it a proof of concept. Prior discussion noted imperfect semantic alignment between some visuals and spoken mathematics. **The user subsequently committed this video to the repository as `MTH263_Calculus_Exam_Review_Narrated.mp4`.** Do not say its original frames were hand-drawn diagrams.

## Significant discovery: Read-Aloud-Main

Reference: `https://github.com/steveonw/Read-Aloud-Main`. Its `web/app.js` has `buildNarrationPcm()` that assembles cached sentence audio with zero-sample gaps and computes sentence label times from accumulated sample counts. WAV and optional Audacity labels can be exported. A sentence cache is in-memory in that application. **These labels establish clip boundaries, not reliable word-internal timestamps or exact speech onset after engine padding.**

Adapt ideas to Narration Studio: persistent disk cache, stable IDs separate from text hashes, per-segment casting and adjustable pause events, original/display text separate from pronunciation-normalized spoken text, WAV + JSON timing sidecar with integer sample offsets. For internal word reveals (e.g. “fourteen” within a sentence), get native word timing if verified or forced-align that clip. An independently supplied MP3 requires script/audio reconciliation and alignment. Audio should remain the timing authority.

## Three Skills: standalone first, cooperative by design

1. **Story Director:** Analyze scripts for concept beats, speakers, setup/payoff, visual reveals, storyboard and prompt pack. Preserve author text. Produce `script.json` and `plan.json` when machine-readable output is requested. Avoid one image per sentence; reuse assets. No authoritative absolute timestamps from the LLM. Human-readable storyboard standalone.
2. **Narration Studio:** Text→speech, speaker casting, clip caching, deliberate pauses, pronunciation map; or user MP3 + script→alignment; export `narration.wav`, `narration.json`, optional SRT/Audacity labels. Audio segment boundaries measured by integer samples. Word timing only when necessary, with confidence/provenance. Audiobook use standalone.
3. **Movie Builder:** User images+audio→video standalone (simple heuristic when no director plan), or with `script.json`, `plan.json`, `narration.json`→resolved timeline, visual assets, FFmpeg MP4, contact sheet and technical QA. Generate text cards in code. Image APIs optional and cost-bounded.

Skill instructions are entrypoint `SKILL.md` with precise trigger descriptions and optional bundled scripts/references/assets; eventual packages should be independently installable and tested. The current repository holds planning notes only.

## Agreed or high-confidence design principles

- Use **one small versioned file interface**; don't require one Skill to import another Skill's implementation. Avoid duplicated major engines. Shared conventions and test fixtures first; factor a common library only if actual tested duplication justifies it.
- Maintain immutable original text separate from spoken-pronunciation substitutions. Use stable segment and word anchor IDs, preserve them across edits as far as practical; use audio/script hashes to detect stale timings.
- Story Director chooses intent; Narration measures timing; Movie Builder resolves to frames and executes. Place important reveals no earlier than their spoken anchor. Captions must not pre-display punchlines either.
- No one-sentence-one-image default. Reuse assets, use shots across multiple sentences, use informative code-rendered cards.
- Favor a cheap **animatic** with placeholder graphics to test synchronization before paying for generated stills.
- Deterministic technical QA: duration, codec, gaps, black frames (allow intentional black), caption spoilers, missing assets, contact sheet.
- Cache generated stills and TTS clips; a one-line edit or image replacement should not trigger unrelated model calls.
- Asset failure may use *labeled* placeholders for a preview, but **do not call an incomplete final video successful**. Report missing narration and visuals prominently.
- Prefer standard Python + FFmpeg for a minimal renderer; optimize only after benchmarking. Avoid unbounded automated regeneration.

## Unresolved debates, not settled facts

- Who owns segmentation and shared anchor resolution? Recommended first implementation: publish schema + golden fixture with tiny common helpers, not prematurely duplicate a large core module.
- Exact frame/word timing aligner/model; verify licensing before commercial workflows. Speech recognizers and forced aligners are not identical.
- Scope of emotion-capable TTS; Piper/Kokoro are light but may not act emotional directions faithfully. CosyVoice-class models may be heavier. Avoid claims of guaranteed emotion.
- Which Hugging Face image/TTS inference providers are available and their current prices. Hub repository ≠ hosted inference endpoint; no assumption of unlimited free GPU inference.
- Rendering strategy (one-pass Python frame feed vs FFmpeg filtergraphs vs per-shot caching); choose after a real test. Do not assume arbitrary performance benchmarks.
- Whether to add an optional QA vision model later (likely defer in v1, especially for intentional irony).
- Some proposed timing constants are hypotheses, not measured standards. Critical reveals require explicit validation.

## Proposed minimum interoperability contract

- `script.json`: authoritative original script segments, IDs, original words, speakers.
- `plan.json`: creative beats, asset descriptions/reuse references, shots with script anchors, intent, constraints; no LLM-invented absolute times.
- `narration.wav` + `narration.json`: audio source/hash/sample rate; segment clip sample boundaries, explicit pauses, optional word timestamps and confidence/source tags, original-to-spoken word mapping.
- `timeline.json`: compiled frame boundaries and media paths, generated by Builder.
- Optional `overrides.json` for human corrections; critical absolute overrides need audio hash to avoid staleness.

Version schema with `filmkit/<type>@1.0` (provisional name). Treat IDs as opaque; no hard-coded `L_001` vs `s013` dependence. Declare what can be missing. Exact schemas still need to be authored and tested.

## Suggested phased build

1. **Movie Builder executor test:** 5 images + supplied WAV/MP3 + hand-authored short timeline → valid MP4. A precisely timed card/reveal, contact sheet, QA. Standalone should work.
2. **Narration Studio timing test:** assemble supplied WAV segments + inserted pause by actual sample counts, export sidecar. Then add one local TTS backend and persistent cache; change one line and show only one resynthesis.
3. **Story Director test:** standalone storyboard + structured plan tied to stable source IDs; one automated shot plan, no manual shot-by-shot editing required.
4. **Integration:** 60–90 seconds of the DOOM story, AI-directed visuals, narration timing, a reveal on a critical spoken word, pause/reaction, reused still image, rendered MP4, final inspection. Generated stills optional at executor test but required for an end-to-end generation acceptance demo if provider available.
5. Later: multiple providers, emotional acting, music ducking, cinematic character consistency, UI, advanced visual QA.

## Fresh-AI instructions

1. Read `README.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `ROADMAP.md` from this repo. Treat GitHub as external project notes, not an automatic memory feature.
2. Confirm current repository state and actual implementation before asserting progress. Do not assume raw four planning documents or DOOM story files are committed.
3. Don't reopen every conceptual debate unless a test reveals a problem. Build/test smallest component next; save outputs and update this handoff and decision log.
4. User values practical automation, humor, low compute expense, reliable speech/image synchronization, reusable independent Skills, and no need to edit giant JSON manifests by hand.
5. When editing the repository, use small reviewable commits or a PR if appropriate. No secrets, tokens, private audio or unpublished stories in this **public** repository without express instruction.
