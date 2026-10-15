# Narration Studio — M1

Standalone narration with exact timing. Skill entry point: [`SKILL.md`](SKILL.md).
Tracking issue: #5.

```bash
pip install numpy sherpa-onnx            # FFmpeg optional (format conversion)
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-amy-medium.tar.bz2
tar xjf vits-piper-en_US-amy-medium.tar.bz2

python narration_studio/scripts/narrate.py build narration_studio/examples/sample_story.md \
  --config narration_studio/examples/sample_config.json \
  --model-dir vits-piper-en_US-amy-medium --out out/narration
```

Output: `narration.wav`, `narration.json` ([schema](references/narration-schema.md)),
`narration.srt`, `narration-labels.txt`, and a clip cache in `out/narration/cache/`.

## Tests

```bash
python -m unittest discover -s narration_studio/tests -v
# real voice too:
NS_TEST_MODEL_DIR=vits-piper-en_US-amy-medium python -m unittest discover -s narration_studio/tests -v
```

## Verified 2026-10-14 (Claude session, Linux, Python 3.13, sherpa-onnx 1.13.8, FFmpeg 6.1.1)

- 15/15 tests pass, including the real-voice test and a Movie Builder render.
- Sample story: 8 segments, 33.79 s, built in ~3.5 s on CPU; rebuild reused all 8 clips.
- One edited line → exactly one re-synthesis; unchanged clips byte-identical.
- Read Aloud label round trip is sample-exact (WAV). A LAME MP3 of the same audio
  also decoded sample-exact with FFmpeg 6.1.1; other encoders may add offset.
- Measured on the 8 sample segments: the Amy voice puts 30–60 ms of silence
  before speech and 47–206 ms after it, which is why `speech_start_sample` exists.
- Measured: the same sentence synthesized twice gave different lengths
  (58,624 vs 59,136 samples) because VITS sampling is random. The cache is what
  makes timing reproducible.

## Not done (next steps)

1. Align an independently recorded MP3 to a script (needs a forced aligner; licence check).
2. Word-level timing for reveals inside a line.
3. Kokoro / KittenTTS adapters (Read-Aloud-Main already runs them in WASM).
4. Packaging as an installable Skill (`agents/openai.yaml`) per ROADMAP Phase 5.
