# Narration Studio — M1 + M2

Standalone narration with exact timing. Skill entry point: [`SKILL.md`](SKILL.md).
Tracking issues: #5 (M1, PR #8), #9 (M2: word timing + outside recordings).

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

Word timing and outside recordings need the speech-recognition model (112 MB, Apache-2.0):

```bash
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-small-en-2023-06-26.tar.bz2
tar xjf sherpa-onnx-zipformer-small-en-2023-06-26.tar.bz2

# when is "regression" said?
python narration_studio/scripts/narrate.py words out/narration \
  --asr-model sherpa-onnx-zipformer-small-en-2023-06-26 --find regression

# time a recording you made yourself against the script
python narration_studio/scripts/narrate.py align my_reading.mp3 narration_studio/examples/sample_story.md \
  --config narration_studio/examples/sample_config.json \
  --asr-model sherpa-onnx-zipformer-small-en-2023-06-26 --out out/aligned
```

## Tests

```bash
python -m unittest discover -s narration_studio/tests -v
# with the real voice and speech-recognition models too:
NS_TEST_MODEL_DIR=vits-piper-en_US-amy-medium \
NS_TEST_ASR_DIR=sherpa-onnx-zipformer-small-en-2023-06-26 \
python -m unittest discover -s narration_studio/tests -v
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

## Verified 2026-10-14, M2 (same machine; zipformer-small-en ASR)

- 28/28 tests pass with both models; the 4 real-model tests passed on 3 repeat runs.
- Raw recognizer word times are **early**: 63–285 ms on joined phrases, up to 784 ms
  after a 0.75 s pause. Used directly, they'd put a punchline picture several frames early.
- After refinement, on 60 known word onsets (pauses of 0, 0.25 and 0.75 s before the
  word): mean −1.2 ms, 56 of 60 within 10 ms, **none more than one 30 fps frame early**,
  one 97 ms late (word starting with a soft "z").
- `align` on the sample story read back as a 128 kbps MP3: all 8 lines start within
  5 ms and end within 20 ms of their true positions. A rewritten line (49% match), a line
  missing from the recording, and a recorded line missing from the script were each reported.
- Found and fixed: imported audio used to get its gaps zero-filled (it affected Read Aloud
  MP3 imports); gaps now keep the original samples, checked bit-exact.

## Not done (next steps)

1. Validate word timing on real human recordings (only synthetic speech is measured so far).
2. Speed: `align` transcribes in 8–20 s pieces on CPU; long audiobooks are untested.
3. Kokoro / KittenTTS adapters (Read-Aloud-Main already runs them in WASM).
4. Packaging as an installable Skill (`agents/openai.yaml`) per ROADMAP Phase 5.
