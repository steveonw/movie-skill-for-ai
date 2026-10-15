"""TTS engine adapters.

Each engine exposes:
  identity(voice)        -> dict of everything that changes its audio
  synthesize(text, voice)-> (int16 mono array (frames, 1), sample_rate)

voice is the cast entry for a speaker, e.g. {"sid": 0, "speed": 1.0}.
"""
import math
import os
from pathlib import Path

import numpy as np

from ns_audio import float_to_int16, sha256_file


class SherpaVitsEngine:
    """Local sherpa-onnx VITS/Piper voice (same engine family as Read-Aloud-Main).

    model_dir must contain one *.onnx, tokens.txt and espeak-ng-data/.
    Note: VITS sampling is random, so the same text gives slightly different
    audio (and length) on every call. The clip cache is what keeps timings
    stable between builds; do not rely on re-synthesis being identical.
    """
    name = "sherpa-onnx-vits"

    def __init__(self, model_dir, num_threads=None):
        import sherpa_onnx  # optional dependency, imported only when used
        self.model_dir = Path(model_dir)
        models = sorted(self.model_dir.glob("*.onnx"))
        if len(models) != 1:
            raise FileNotFoundError(f"{model_dir}: expected exactly one .onnx model, found {len(models)}")
        tokens = self.model_dir / "tokens.txt"
        data_dir = self.model_dir / "espeak-ng-data"
        if not tokens.is_file():
            raise FileNotFoundError(tokens)
        self.model = models[0]
        threads = num_threads or max(1, min(4, os.cpu_count() or 1))
        vits = sherpa_onnx.OfflineTtsVitsModelConfig(
            model=str(self.model), tokens=str(tokens),
            data_dir=str(data_dir) if data_dir.is_dir() else "")
        cfg = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(vits=vits, num_threads=threads, provider="cpu"),
            max_num_sentences=1)
        self.tts = sherpa_onnx.OfflineTts(cfg)
        self.settings = {k: round(float(getattr(vits, k)), 6)
                         for k in ("noise_scale", "noise_scale_w", "length_scale")}
        self.model_sha256 = sha256_file(self.model)
        self.version = getattr(sherpa_onnx, "__version__", "unknown")
        self.sample_rate = self.tts.sample_rate
        self.num_speakers = self.tts.num_speakers

    def identity(self, voice):
        return {"engine": self.name, "engine_version": self.version,
                "model": self.model.name, "model_sha256": self.model_sha256,
                "sid": int(voice.get("sid", 0)), "speed": float(voice.get("speed", 1.0)),
                "settings": self.settings}

    def synthesize(self, text, voice):
        sid = int(voice.get("sid", 0))
        if self.num_speakers and sid >= max(1, self.num_speakers):
            raise ValueError(f"speaker id {sid} out of range (model has {self.num_speakers})")
        audio = self.tts.generate(text, sid=sid, speed=float(voice.get("speed", 1.0)))
        if len(audio.samples) == 0:
            raise RuntimeError(f"engine returned no audio for: {text[:60]!r}")
        return float_to_int16(audio.samples).reshape(-1, 1), audio.sample_rate


class ToneEngine:
    """Deterministic NON-SPEECH test engine (no model needed).

    Produces a tone whose length depends on the text, wrapped in known
    silence padding (lead 0.10 s, tail 0.15 s), so tests can check exact
    sample arithmetic and speech-boundary measurement. Never use for output.
    """
    name = "test-tone"
    LEAD, TAIL, PER_CHAR, BASE = 0.10, 0.15, 0.03, 0.20

    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate

    def identity(self, voice):
        return {"engine": self.name, "engine_version": "1", "sample_rate": self.sample_rate,
                "sid": int(voice.get("sid", 0)), "speed": float(voice.get("speed", 1.0))}

    def synthesize(self, text, voice):
        r = self.sample_rate
        speed = float(voice.get("speed", 1.0))
        body = int(round((self.BASE + self.PER_CHAR * len(text)) / speed * r))
        freq = 180.0 + 40.0 * int(voice.get("sid", 0))
        t = np.arange(body) / r
        tone = 0.3 * np.sin(2 * math.pi * freq * t)
        pcm = np.concatenate([np.zeros(int(self.LEAD * r)), tone, np.zeros(int(self.TAIL * r))])
        return float_to_int16(pcm).reshape(-1, 1), r


def make_engine(kind, model_dir=None):
    if kind in ("sherpa", "sherpa-vits", "piper"):
        if not model_dir:
            raise ValueError("the sherpa engine needs --model-dir (a Piper/VITS voice folder)")
        return SherpaVitsEngine(model_dir)
    if kind in ("tone", "test-tone"):
        return ToneEngine()
    raise ValueError(f"unknown engine {kind!r} (use 'sherpa' or 'tone')")
