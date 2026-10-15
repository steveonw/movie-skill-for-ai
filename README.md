# AI Filmmaking Skills — Project Memory

**Status:** Planning and preservation; no skill packages or video pipeline have been implemented or tested.  
**Snapshot:** 2026-10-14

Goal: Develop **three standalone-first, cooperative-by-design ChatGPT Skills** that together turn a written story and optionally an MP3 into a watchable narrated movie using AI-generated still images, accurate speech timing, simple motion, and FFmpeg. Minimize cost and manual editing. Maintain modularity.

## Start here after a conversation reset

**Read [AI_HANDOFF.md](AI_HANDOFF.md) first.** It is written for a fresh AI with no previous chat context.

Supporting materials:
- [ARCHITECTURE.md](ARCHITECTURE.md) — Skill boundaries and provisional interoperability contract.
- [DECISIONS.md](DECISIONS.md) — accepted, contested, deferred, and unverified decisions.
- [ROADMAP.md](ROADMAP.md) — first implementation and validation milestones.

## The three Skills

| Skill | Works independently | When cooperating |
|---|---|---|
| **Story Director** | Storyboards, shot/beat lists, image prompts, script and character notes | Outputs a narrative plan with script-based visual anchors |
| **Narration Studio** | Audiobooks/TTS, multiple speaker voices, script-to-audio alignment, SRT and timing data | Outputs master narration WAV plus segment/word/pause metadata |
| **Movie Builder** | Narrated slideshow or explainer from supplied images and audio; QA | Resolves plans against audio, generates or reuses images, renders MP4 |

None requires the other Skills to be installed. The common interface is **files**, not inter-Skill imports. Avoid creating a fourth orchestrator Skill initially.

## Sources and provenance

The design arose from a multi-round comparison of **Gemini, Claude, Grok, and GPT**, based on four planning prompts (Story Director, Narration Studio, Movie Builder, final integration/revision). Their lengthy raw replies were supplied as four uploaded markdown files in the originating chat; **this repository preserves a curated synthesis, not a verbatim archive of those uploads**.

Key technical inspiration: [Read-Aloud-Main](https://github.com/steveonw/Read-Aloud-Main) by steveonw — per-sentence TTS, cache, explicit silent gaps, WAV and Audacity label export. Repository README and `web/app.js` had been examined in the originating conversation. Borrow the architecture, not necessarily its entire browser/WASM/USB application. Confirm current source before implementing.

## Project rule

**Deliver a watchable movie, not just elegant manifests.** Architecture is provisional until it survives real rendering tests. Git history preserves changes to our decisions.
