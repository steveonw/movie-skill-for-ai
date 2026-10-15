# AGENTS.md — Instructions for AI Assistants

This repository is the durable working home of a low-cost, AI-directed story-to-video toolkit made from **three standalone but interoperable ChatGPT Skills**: Story Director, Narration Studio, and Movie Builder.

## First understand the mission

**We are building three standalone ChatGPT Skills that together turn stories into low-cost narrated illustrated movies.** The workshop is not the product; the movie-making experience is the product.

1. **Story Director:** interpret a story, direct visuals, plan comedic timing and shots without rewriting the author's text.
2. **Narration Studio:** generate/align narration, preserve pronunciation mappings, compute real clip and selective word timings.
3. **Movie Builder:** assemble supplied/generated visual assets with narration into a playable MP4, with accurate reveals and QA.

The three Skills must work separately as well as in a pipeline. See [README.md](README.md) for the human-readable goal and [AI_HANDOFF.md](AI_HANDOFF.md) for the detailed handoff.

### Collaboration is a helper, not a blocker

[WORKSHOP.md](WORKSHOP.md) defines our **four-seat, selective-message collaboration protocol** (Story Director, Narration Studio, Movie Builder, Integrator/QA, plus the human coordinator). **[Issue #2](https://github.com/steveonw/movie-skill-for-ai/issues/2) is the only team-wide AI message bus.** Workers share deliberately using `TRANSMIT:` at the start of their comments; the coordinator uses `BROADCAST:`. Keep private working conversations outside the public repository, detailed testing in task issues/PRs, and do not make routine clock-in commits to `main`. **Never refuse or delay a substantive filmmaking request merely because a clock-in form, message board, or GitHub Issues comment is unavailable.** If repository writing is possible, leave a concise record. If it is not, do the task as far as possible and provide the handoff in your response. There are no continuously running agents behind those status labels.

## On every new session

0. **Check [Issue #2](https://github.com/steveonw/movie-skill-for-ai/issues/2) first** for recent `TRANSMIT:` messages, coordinator `BROADCAST:` messages, unresolved requests and claimed files. Review linked branches and PRs. Before substantive code edits, post `TRANSMIT: CLOCK IN` naming issue, branch, exact files and intended test; at the end post `TRANSMIT: HANDOFF / CLOCK OUT` with evidence and released file scope. Do not make a claims table or routine commits to `main`; skip ceremony for tiny documentation edits.
1. **Use Issue #2 as a selective collaboration channel**, not a full transcript. Respond to relevant `TRANSMIT:` questions and `BROADCAST:` instructions, and only send findings others can act on. Link task/PR details. GitHub comments are public and do not wake an AI session or imply that other seats are active. “AIDE REQUEST:” is usable only when a real aide/tool workflow exists in the current worker's environment.
2. Read `AI_HANDOFF.md`, `CONVERSATION_SUMMARY.md`, `DECISIONS.md`, and `ROADMAP.md`.
3. Check what actually exists in the repository before claiming something is built or tested.
4. For contested design choices consult `research/originals/` (four independent multi-AI planning documents) and `HISTORY_AND_PROMPTS.md`. Original files are historical evidence, **not** specifications to implement uncritically.
5. Check current open GitHub Issues. Work toward a runnable acceptance test, rather than producing additional abstract handoffs.
6. For substantive milestones or cross-Skill blockers, use **`TRANSMIT: FINDING`, `TRANSMIT: QUESTION`, or `TRANSMIT: REVIEW` on Issue #2** with the intended recipient, task/PR link, verified evidence (or `PROPOSED` / `NOT TESTED`), and next action. The human coordinator may use `BROADCAST:` for priorities and final decisions. Never treat an unapproved proposal or someone's self-reported role as authorization to change global contracts; accepted changes require owner/designated integrator approval and tested updates to `ARCHITECTURE.md` / `DECISIONS.md`.
7. After substantial work, update `AI_HANDOFF.md`, `DECISIONS.md` if decisions change, `ROADMAP.md` milestones and tests. State exactly what ran and what did not.

## Non-negotiable product aims

- **Standalone First, Cooperative by Design**: no Skill requires either of the other Skills merely to perform its own primary task.
- Text/story + optional audio -> AI directs still-image video -> MP4 with accurate pacing, intentional punchline reveals, reusable images and optional captions. No forced manual shot-by-shot JSON editing.
- Keep generated audio word timing distinct from **exact clip sample boundaries**. User-supplied recordings are the audio timing authority.
- Preserve original script text; keep spoken pronunciations separate. Exact mathematics, numbers and title cards should be rendered programmatically.
- Use a small, versioned interchange contract: `script.json`, `plan.json`, `narration.json` (+ audio), and compiled `timeline.json`. Treat current schema examples as **provisional** pending tests.
- Allow free placeholder animatics; NEVER silently label an output with missing audio/images as a complete final render.
- Prefer Python + FFmpeg with deterministic technical QA. Provider access, licensing, costs and GPU capacity must be checked; do not assume free hosted inference.
- No tokens, credentials, unpublished story manuscripts or private recordings in this **public** repository unless the owner expressly asks.

## Repository preservation rules

- **Never overwrite, compress, edit or delete the four research sources in `research/originals/`** during normal development. Add interpretations elsewhere.
- Keep `AI_HANDOFF.md` as the concise *current* project snapshot, with dated updates. Keep `HISTORY_AND_PROMPTS.md` and `CONVERSATION_SUMMARY.md` for historical context.
- Preserve traceability: link design changes to an issue, PR, test, or documentation note.
- Prefer reviewable changes. Avoid sweeping reorganizations without need. If moving a file, preserve its history where possible.
- Protect user-owned MTH263 video and other reference artifacts. Don't rewrite them as part of tests.

## Development order (current, subject to real evidence)

1. Movie Builder standalone: 5 images + audio + simple timeline -> playable MP4, timed title card, contact sheet, ffprobe QA. See issue #1.
2. Narration Studio: assemble clips/pause events exactly by sample count, disk cache, optional TTS and external-audio alignment.
3. Story Director: independent storyboards and machine-readable creative shot plans.
4. Integrated ~60–90-second DOOM: Chalkboard Edition teaser with a deliberate "Bang" reveal and reaction hold.
5. Package three independent validated Skills. Keep enhancements optional until basic tests pass.

## Documentation for a fresh AI

**START:** [AI_HANDOFF.md](AI_HANDOFF.md)  
**History:** [CONVERSATION_SUMMARY.md](CONVERSATION_SUMMARY.md), [HISTORY_AND_PROMPTS.md](HISTORY_AND_PROMPTS.md)  
**Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md), [DECISIONS.md](DECISIONS.md)  
**Original sources:** [research/originals/](research/originals/)  
**Build list:** [ROADMAP.md](ROADMAP.md) and GitHub Issues

**Status as of 2026-10-14:** Design and archival documentation only; do not claim the Skills or production engine are implemented until verification.
