# AI Movie-Making Skills

**Our goal:** Build an affordable, largely automatic filmmaking workflow that turns a **written story or script** (and optionally a recorded voiceover) into a **watchable narrated MP4**. An AI should understand the story, choose and reuse illustrations, place cuts/cards/reveals at the right spoken moments, and assemble the film with FFmpeg. The human should **not** need to hand-edit every scene or JSON timestamp.

**This is a filmmaking project, not an agent attendance or time-clock project.** The optional [AI Workshop](WORKSHOP.md) exists only to help different AI sessions share work and avoid duplicated changes.

## Start here (human or AI)

**Human:** Read this page, check [ROADMAP.md](ROADMAP.md), then open [Issue #1](https://github.com/steveonw/movie-skill-for-ai/issues/1) to see the next engineering goal.

**AI joining the project:** Read [AI_HANDOFF.md](AI_HANDOFF.md) for purpose, history, current reality and next step. Read [AGENTS.md](AGENTS.md) for implementation rules. Check the actual main branch, open issues and pull requests **before** writing code. **Before work, read the [shared AI noticeboard — Issue #2](https://github.com/steveonw/movie-skill-for-ai/issues/2)** for status, other AIs' discoveries and interface questions. During work, keep detailed tests in your own issue/PR; post a short, useful cross-team summary on #2 when opening a substantive PR, reaching a milestone, or discovering a dependency. The [workshop procedure](WORKSHOP.md) is coordination, not a blocker.

**One-sentence mission:** *Story → AI direction → spoken timing → reusable visual assets → MP4 that genuinely matches what the narrator says.*

## Why three Skills?

We are developing **three separate, independently useful ChatGPT Skills**, with optional cooperation via small versioned files:

| Skill | What it should do for someone using it alone | How it helps the finished movie |
| --- | --- | --- |
| **Story Director** | Read a story and produce a useful storyboard, beat sheet, image prompts, character/style notes | Select shots, recognize comedic setups/payoffs, prevent early reveals; export `script.json` / `plan.json` |
| **Narration Studio** | Narrate scripts or align existing WAV/MP3, cache TTS clips, export audio/captions/timing | Supply `narration.wav` and `narration.json` with real timings and pauses |
| **Movie Builder** | Combine supplied images and voiceover into an MP4, even without the other Skills | Render the plan with images, titles, transitions, captions and QA |

**Design rule: Standalone First, Cooperative by Design.** None of these should require the other two to be installed. The video editor is a means to the **creative storytelling goal**, not the entire product.

## What the end-to-end experience should look like

1. Human provides a funny story, educational script or documentary narration. An existing MP3 is optional.
2. **Story Director** understands the narrative, chooses visual beats, reusable images, timing *intent*, and the appropriate joke reveals.
3. **Narration Studio** makes or aligns speech and reports measured timing—not invented word timestamps.
4. **Movie Builder** resolves visual beats against those times, builds a cheap animatic, generates/reuses illustrations, renders exact on-screen words using code, and outputs an MP4.
5. The movie is checked for real technical quality and whether visuals spoil or contradict key moments.

**Acceptance demo:** A 60–90-second excerpt of *DOOM: Chalkboard Edition*, a deliberately ridiculous, deadpan mockumentary. Images, reaction holds, the spoken “Bang,” and captions must land at the right moments.

## What exists today (2026-10-14)

- **Research and durable handoffs:** committed on `main`, including all four original AI planning files under [research/originals/](research/originals/).
- **Earlier video reference:** [MTH263_Calculus_Exam_Review_Narrated.mp4](MTH263_Calculus_Exam_Review_Narrated.mp4), provided by the user; this is **not** a Movie Builder Skill deliverable.
- **First tiny Movie Builder code prototype:** **merged into `main`** via [PR #3](https://github.com/steveonw/movie-skill-for-ai/pull/3). It made a simple five-image/seven-second synthetic-audio test MP4 in the originating session. The `movie_builder/` folder contains a renderer and a demo generator. This is *not* a finished Skill. Follow-up improvements are in [draft PR #7](https://github.com/steveonw/movie-skill-for-ai/pull/7).
- **First development task:** [Issue #1](https://github.com/steveonw/movie-skill-for-ai/issues/1) stays open. It needs stronger duration/reveal checks, contact-sheet automation, a reproducible test and real narration.

Do not tell people that the three Skills or the full filmmaking pipeline have already been built.

## Finding the right file

| I want to… | Read |
| --- | --- |
| Understand the mission and know where we are | **README.md** (here) |
| Resume as a new AI with little or no chat history | [AI_HANDOFF.md](AI_HANDOFF.md) |
| Know current architecture and what can change | [ARCHITECTURE.md](ARCHITECTURE.md), [DECISIONS.md](DECISIONS.md) |
| Pick the next measurable task | [ROADMAP.md](ROADMAP.md), [GitHub Issues](https://github.com/steveonw/movie-skill-for-ai/issues) |
| Learn how to contribute or coordinate with another AI | [AGENTS.md](AGENTS.md), [WORKSHOP.md](WORKSHOP.md) |
| Revisit full raw multi-AI research | [research/originals/](research/originals/), [HISTORY_AND_PROMPTS.md](HISTORY_AND_PROMPTS.md) |
| See human-readable conversation history | [CONVERSATION_SUMMARY.md](CONVERSATION_SUMMARY.md) |

## Shared AI communication

**[Issue #2 — AI Workshop Noticeboard](https://github.com/steveonw/movie-skill-for-ai/issues/2)** is the first place a new agent should **read for other workers' progress** and the place to **post a short status/finding or concrete cross-Skill question**. Detailed evidence belongs in the worker's own [issue](https://github.com/steveonw/movie-skill-for-ai/issues) or PR; link it from #2 so other AIs and the master AI can find it. A post is expected at meaningful milestones, **not** for every clock-in or line of code. Decisions on shared contracts are proposed on #2 and settled by the owner/master AI, then recorded in the architecture docs.

## How we work

Build the smallest real proof, actually test it, preserve discoveries and avoid architecture sprawl. The workshop's “clock-in / clock-out” comments are **optional recordkeeping**, not a reason to refuse a task and not proof of background agents. If GitHub commenting is unavailable, make useful progress and give a normal written handoff.

**Priority:** make a good movie; then make it repeatable; then make the three Skills pleasant to use.
