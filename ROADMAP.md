# Build and Test Roadmap

Updated 2026-10-14: Movie Builder prototype merged (PR #3); Narration Studio M1 on branch `work/narration-studio-m1` (#5).

## Phase 0 — Preserve and checkpoint
- [x] Curate memory, interoperability concept, decision log and AI handoff on GitHub.
- [ ] Review documentation for mistakes; choose license/desired openness.
- [ ] Build executable schema fixtures and validation tests after one concrete prototype defines needed fields.

## Phase 1 — Movie Builder standalone executor
- [ ] Confirm Python + FFmpeg environment.
- [ ] Supply five images, narration WAV/MP3, and a small timing plan.
- [ ] Compile deterministic timeline to MP4; verify duration and codec with ffprobe.
- [ ] Show a reveal card at/after its real audio anchor (not before); avoid caption spoilers.
- [ ] Generate a contact sheet and basic QA report.
- [ ] Keep Movie Builder standalone: no Story Director, no Narration Studio required.

## Phase 2 — Narration Studio standalone timing
- [x] Accept supplied WAV clips and assemble with sample-exact inserted pauses. *(narration_studio M1, tested)*
- [x] Produce a master WAV and segment/silence timing JSON sidecar; compare sample counts. *(narration_studio M1, tested)*
- [x] Implement a disk clip cache keyed on voice/model/synthesis settings and spoken text. *(narration_studio M1, tested)*
- [x] Test change-one-line → only that line resynthesizes. *(narration_studio M1, tested)*
- [x] Add one local TTS adapter and multi-speaker rendering *(sherpa-onnx VITS/Piper; per-speaker sid/speed/model; tested)*
- [ ] Verify licence of each shipped voice before any commercial use (Amy MODEL_CARD points to mimic3-voices; not yet reviewed).
- [x] Align an external MP3 to a script; detect mismatches and confidence issues. *(narration_studio M2 `align`, #9; validated on synthetic speech, human recordings untested)*
- [x] Resolve a word-internal “fourteen” or “Bang” reveal with verified timestamps/selective alignment. *(M2 `words --find`; 60 known onsets: none more than 1 frame early)*
- [x] Optionally import Read-Aloud-Main WAV and label-track metadata. *(narration_studio M1, tested)*

## Phase 3 — Story Director standalone and structured planning
- [ ] Storyboard, beat sheet, reusable character sheet and image prompt-pack, with no other Skill installed.
- [ ] Script segments with stable IDs; preserve author's original text.
- [ ] Machine-readable shot plan, semantic purpose, non-spoiler reveals, asset reuse.
- [ ] Demonstrate a plausible director-generated DOOM excerpt plan with no human-written per-shot timing.

## Phase 4 — End-to-end proof
- [ ] Feed a 60–90 s DOOM excerpt into the director; use supplied or generated narration.
- [ ] Render a free placeholder animatic, check punchline timing.
- [ ] Generate/reuse AI images within a set budget; code-render statistics/cards.
- [ ] Build 1080p/30 H.264/AAC MP4, proper captions, contact sheet, QA.
- [ ] Demonstrate one image swap → no other image generation, and one narration text change → only relevant TTS regenerated.
- [ ] Have a viewer who has not read the script assess coherence/humor (subjective).

## Phase 5 — package Skills
- [ ] Each independent package gets `SKILL.md`, `agents/openai.yaml`, mode-specific scripts/references/assets.
- [ ] Validate against actual ChatGPT Skill requirements; test each in isolation.
- [ ] Package each Skill separately, keeping bundles under platform size constraints.
- [ ] Add a minimal combined workflow recipe that composes their outputs.
- [ ] Update AI_HANDOFF.md when any feature is actually tested or released.

## Later, not v1
Expressive hosted TTS, character conditioning, more providers, animated scenes, per-shot render caching, GUI, advanced sound design and expensive semantic QA.

## Restart procedure
Open this repo and read `AI_HANDOFF.md` and `DECISIONS.md`; verify code/tests actually present. Select next unchecked test. Avoid producing another essay in place of a prototype.
