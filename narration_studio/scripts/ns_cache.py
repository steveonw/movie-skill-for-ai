"""Persistent on-disk clip cache.

Key = SHA-256 of a canonical JSON request containing everything that can
change the audio: spoken text, engine, model checksum, speaker id, speed and
synthesis settings. Segment IDs are deliberately NOT part of the key, so two
identical lines share audio and renumbering lines never forces re-synthesis.

Each entry is <key>.wav plus <key>.json. The JSON is written last and holds
the WAV checksum, so an entry is reused only if it was completely written and
is still intact. Anything else is treated as a miss and regenerated.
"""
import json
import os
import tempfile
from pathlib import Path

from ns_audio import read_wav, sha256_file, write_wav
import hashlib

CACHE_FORMAT = 1


def request_key(request):
    canonical = json.dumps({"cache_format": CACHE_FORMAT, **request}, sort_keys=True,
                           separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ClipCache:
    def __init__(self, root):
        self.root = Path(root)
        self.hits, self.misses, self.rejected = [], [], []

    def _paths(self, key):
        d = self.root / key[:2]
        return d / f"{key}.wav", d / f"{key}.json"

    def get(self, key):
        wav, meta = self._paths(key)
        if not (wav.is_file() and meta.is_file()):
            return None
        try:
            info = json.loads(meta.read_text(encoding="utf-8"))
            if not info.get("complete") or sha256_file(wav) != info["wav_sha256"]:
                raise ValueError("checksum mismatch")
            samples, rate = read_wav(wav)
            if samples.shape[0] != info["frames"] or rate != info["sample_rate"]:
                raise ValueError("frame count mismatch")
            return samples, rate
        except Exception as exc:  # corrupt entry: regenerate, never crash
            self.rejected.append({"key": key, "reason": str(exc)})
            return None

    def put(self, key, samples, rate, request):
        wav, meta = self._paths(key)
        write_wav(wav, samples, rate)
        info = {"complete": True, "key": key, "request": request, "sample_rate": rate,
                "frames": int(samples.shape[0]), "wav_sha256": sha256_file(wav)}
        fd, tmp = tempfile.mkstemp(dir=meta.parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=1, ensure_ascii=False)
        os.replace(tmp, meta)

    def get_or_make(self, request, make, label=None):
        key = request_key(request)
        found = self.get(key)
        if found is not None:
            self.hits.append(label or key)
            return found[0], found[1], key, True
        samples, rate = make()
        self.put(key, samples, rate, request)
        self.misses.append(label or key)
        return samples, rate, key, False
