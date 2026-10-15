# Decision Log and Open Questions

Updated: 2026-10-14

## Accepted project values
- **Standalone first, cooperative by design:** Story Director, Narration Studio and Movie Builder have independent triggers and deliverables.
- User wants **hands-off AI direction**, not a JSON-heavy human video editor.
- Video is primarily AI-generated *still images* + editing; expensive model-generated motion is not required.
- Supplied audio governs timing. AI direction governs what is shown. Compiler governs when it appears.
- Read-Aloud-Main per-sentence caching, literal silent gaps, and sample-count label construction are an inspiration for generated narration.
- Sentence boundaries do not reveal word-internal timing. Use native verified word timestamps or selective alignment for precise reveals.
- For exact typography, mathematics and numbers, code-render text/graphics rather than relying on image generation.
- One reused visual may cover many lines; one sentence may need many shots.
- Make inexpensive placeholder animatics and contact sheets to check timing before costly image generation.
- Cache assets; preserve manual overrides and audit retries/cost.
- No unpublished stories, tokens, model credentials or private audio saved in this public repository by default.

## Preferred but provisional engineering decisions
- Compact versioned JSON interface, likely `filmkit/*@1.0`.
- Original script segments with stable opaque IDs and word anchors. Exact segmentation implementation needs tests.
- Narration-produced master WAV plus sidecar for both standalone and cooperative operation; avoid handing video compiler only an array of heterogeneous audio snippets.
- FFmpeg as production encoder. Renderer internals to be selected by benchmark: filtergraph vs direct frame feed.
- Incomplete asset fallback for preview only; do not silently mark final output as complete.
- One model-backed image provider adapter initially (if image-generation integration is tested); HF could be a provider but is not a free GPU guarantee.
- Technical QA required; expensive vision-based semantic QA deferred.

## Implemented in Narration Studio M1 (2026-10-14, issue #5) — provisional until reviewed
- `narration.json` carries **both** exact clip bounds (`start/end_sample`) and measured audible speech (`speech_start/end_sample`, 10 ms energy threshold, provenance tagged). Cuts and captions should use speech bounds; splicing uses clip bounds.
- Three text fields per segment: `source_text` (author's exact text), `display_text` (Markdown removed), `spoken_text` (after pronunciation map).
- Clip cache key = engine + model checksum + voice (sid, speed) + synthesis settings + spoken text. Segment IDs are excluded, so renumbering or duplicate lines never force re-synthesis.
- Plain-text input gets positional IDs (`s001`…); `script.json` IDs are preserved. Stable IDs across edits are Story Director's job.
- Segments + silences must tile the master exactly; `verify` enforces it and checks inserted silence is literal zeros.
- Measured: VITS synthesis is non-deterministic (same sentence → different length), so cached audio is the timing authority for generated narration.

## Rejected for v1
- A fourth coordinating Skill.
- A general-purpose timeline GUI or editing database.
- A large duplicated shared Python core before necessary.
- Separate per-shot lossy video intermediates and elaborate caches without a performance need.
- Unlimited retry/semantic correction loops.
- Assuming an emotional delivery note implies a lightweight TTS engine can perform it reliably.
- Treating fixed thresholds in AI reviewer plans as measured empirical benchmarks.
- Forcing Story Director to place a hard cut after every punchline.
- Treating Read-Aloud-Main as already having per-word timing or persistent audio cache.

## Unresolved: verify or test rather than debate abstractly
- Exact `script.json`, `plan.json`, `narration.json` schemas and ownership of shared segmentation/resolution helpers.
- Best local TTS engine for quality and emotional range; licensing on individual voices.
- WhisperX/stable-ts/other forced-alignment accuracy and licensing; a verified path for external MP3s.
- How punctuation, digit pronunciations, ad-libs and changed scripts map to stable anchors.
- Best FFmpeg render implementation and runtime benchmarks on available machine.
- Inference-provider availability, current image/TTS price, API credentials and license. HF Hub listings do not guarantee an inference endpoint.
- What happens with an audio script mismatch at critical punchline words.
- Precision tolerance for a reveal, to be determined from sample tests and frame rate.
- Whether importing Read-Aloud-Main exported WAV/labels or extending that app is more useful than a new Python module.

## Multi-AI review summary
Gemini: straightforward production workflow; occasionally overconfident about fallback behavior and avoiding alignment.
Claude: strongest detail on sample-accurate timing, provenance, caching and comprehensive contract testing; potential overengineering.
Grok: strong focus on constrained word-anchored compiler and hard scope limits; occasionally too restrictive.
GPT: balanced standalone/cooperative approach, careful timing provenance and incremental implementation; also requires real tests.

The user provided four substantial Markdown files recording these round-by-round responses. Their verbatim text is not yet checked into this repository. **This repo has curated notes, not the raw source archive.**
