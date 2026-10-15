# Conversation Summary — 2026-10-14

This is a readable chronological history. For a new AI, **start with [AI_HANDOFF.md](AI_HANDOFF.md)**, then [ARCHITECTURE.md](ARCHITECTURE.md), [DECISIONS.md](DECISIONS.md), and [ROADMAP.md](ROADMAP.md). For details see [HISTORY_AND_PROMPTS.md](HISTORY_AND_PROMPTS.md).

## Our discussion, in order

1. **Low-cost story-to-video idea.** The user wanted to narrate stories using AI illustrations, natural speech, basic camera moves and automation instead of expensive generative video.
2. **Earlier successful proof of concept.** User had produced about an 8m50s MTH263 calculus review with AI-generated illustrations, captions, narration and assembly. Better semantic visual synchronization was a main improvement target.
3. **Creative test: DOOM: Chalkboard Edition.** Students redraw DOOM frames manually, an absurdly tiny FPS, a man simply says “Bang,” a door takes 23 days, and the 563-hour YouTube project gets twelve views. The deadpan documentary treatment and exact punchlines make it a good test.
4. **First handoff to four AIs.** We wrote a comprehensive technical handoff to Gemini, Claude, Grok and GPT. They independently favored stills, FFmpeg, audio-authoritative timing, modular artifacts, and cheap proofs over abstract architecture.
5. **Counter-handoff.** We challenged them to distinguish an automated AI director from a complicated manual editing engine, and to give better separation of creative intent, measurements, and rendering.
6. **Read-Aloud-Main discovery from the user.** `steveonw/Read-Aloud-Main` uses cached sentence-sized TTS audio, intentional silence and sample-based timing labels. This informed the proposed Narration Studio subsystem. It gives accurate **clip** start/end boundaries; precise **word-internal** reveals still need native word timing or alignment. External MP3s also need alignment.
7. **Shift to ChatGPT Skills.** We proposed Story Director, Narration Studio and Movie Builder as Skills. User asked them to be independently useful but also work together. The motto **Standalone First, Cooperative by Design** became central.
8. **Four-round design process.** Round 1 planned Story Director; Round 2 planned Narration Studio; Round 3 planned Movie Builder; Round 4 reconciled all plans and allowed discoveries from later rounds to improve earlier ones.
9. **Large research upload and comparison.** User supplied four Markdown files containing the independent Gemini/Claude/Grok/GPT outputs across the planning rounds. We accepted compact versioned file interoperability, caching, exact typography via code, word-anchored reveals, a cheap animatic preview, FFmpeg output and QA. We rejected unnecessary giant frameworks, unlimited retries, silent missing-audio fallbacks and rigid humor formulas.
10. **GitHub memory repository.** User offered `https://github.com/steveonw/movie-skill-for-ai`. GitHub write permissions were confirmed. We created README, AI_HANDOFF, ARCHITECTURE, DECISIONS, ROADMAP, plus a longer HISTORY_AND_PROMPTS file and a research inventory.
11. **Preserve more, not less.** User explicitly prefers archiving the **verbatim AI research** along with a curated summary. A lossless ZIP of the four original research files was created in the conversation. The archive inventory includes cryptographic SHA-256 checksums. Its contents are *not automatically on GitHub*: follow the upload steps documented in `research/ARCHIVE_INVENTORY.md`.

## What the three Skills do

- **Story Director:** Independently turns text into storyboards, beat analysis and shot/prompt plans; cooperatively writes `script.json` and `plan.json`, using script anchors rather than guessing timestamps.
- **Narration Studio:** Independently produces narration, audiobooks, alignments, subtitles and label files; cooperatively writes `narration.wav` and `narration.json` with measured sample boundaries, intentional pauses, source-tagged word times and spoken pronunciation mappings.
- **Movie Builder:** Independently turns images plus audio into MP4 videos; cooperatively converts plans plus narration timing to `timeline.json`, acquires or reuses visuals, renders graphics and subtitles with FFmpeg and creates a contact sheet and QA report.

## Workflow and philosophy

Prefer: original story → creative story plan → supplied/generated speech and measured timings → resolved timeline → cheap animatic → generated/reused images → rendered MP4 → checks. Depending on audio mode, speech can be generated after an initial performance/pause plan and the exact visual shots should be resolved after durations are known.

Preserve original script text; allow different spoken pronunciations. Code-render exact title cards and mathematical expressions. Never disclose jokes in images or captions before their spoken reveal. Allow editing a single asset or narration clip without unrelated AI generations. Provider independence is a design aim, not evidence an API is deployed or free.

## Project status

**Research and documentation preserved. Actual Skill implementations not yet created or tested.** Future assistants must verify GitHub before claiming a milestone is done. The recommended next first runnable milestone is a simple Movie Builder MP4 with a correctly timed reveal; then sample-accurate Narration Studio, then Story Director and integrated 60–90s DOOM demonstration.

## Key links

- [Original Read-Aloud implementation](https://github.com/steveonw/Read-Aloud-Main)
- [Research archive inventory](research/ARCHIVE_INVENTORY.md)
- [Extended conversation history](HISTORY_AND_PROMPTS.md)

This is a curated history, not a verbatim conversation transcript. The four original model-reply files should remain intact in the archive.
