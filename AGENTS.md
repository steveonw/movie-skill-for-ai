# AGENTS.md — Instructions for AI Assistants

This repository is the durable working home of a low-cost, AI-directed story-to-video toolkit made from **three standalone but interoperable ChatGPT Skills**: Story Director, Narration Studio, and Movie Builder.

## AI collaboration and session ownership

Follow [WORKSHOP.md](WORKSHOP.md) for clock-in, issue-based message board comments, progress findings, takeover, and clock-out handoffs. A GitHub status entry does not mean an AI continues working after its chat/session ends. Do not mark tasks claimed before actually beginning the associated work.

## On every new session

1. Read `AI_HANDOFF.md`, `CONVERSATION_SUMMARY.md`, `DECISIONS.md`, and `ROADMAP.md`.
2. Check what actually exists in the repository before claiming something is built or tested.
3. For contested design choices consult `research/originals/` (four independent multi-AI planning documents) and `HISTORY_AND_PROMPTS.md`. Original files are historical evidence, **not** specifications to implement uncritically.
4. Check current open GitHub Issues. Work toward a runnable acceptance test, rather than producing additional abstract handoffs.
5. After substantial work, update `AI_HANDOFF.md`, `DECISIONS.md` if decisions change, `ROADMAP.md` milestones and tests. State exactly what ran and what did not.

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
