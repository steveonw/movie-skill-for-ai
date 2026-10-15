"""Audio I/O, sample-exact assembly and speech-boundary measurement.

All positions are integer sample frames at the master sample rate:
start inclusive, end exclusive. Seconds are derived values only.
"""
import hashlib
import os
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

SPEECH_WINDOW_SECONDS = 0.010
SPEECH_ABS_FLOOR_DBFS = -50.0
SPEECH_REL_FLOOR_DB = -30.0


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def float_to_int16(samples):
    arr = np.clip(np.asarray(samples, dtype=np.float32), -1.0, 1.0)
    # Same asymmetric scaling as Read-Aloud-Main's buildNarrationPcm().
    return np.where(arr < 0, arr * 32768.0, arr * 32767.0).astype(np.int16)


def read_wav(path):
    """Read 16-bit PCM WAV -> (int16 array shaped (frames, channels), rate)."""
    with wave.open(str(path), "rb") as w:
        if w.getsampwidth() != 2 or w.getcomptype() != "NONE":
            raise ValueError(f"{path}: not 16-bit PCM")
        ch, rate, n = w.getnchannels(), w.getframerate(), w.getnframes()
        data = np.frombuffer(w.readframes(n), dtype="<i2").reshape(-1, ch)
    return data.copy(), rate


def write_wav(path, samples, rate):
    """Write int16 (frames, channels) atomically."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    samples = np.asarray(samples, dtype=np.int16)
    if samples.ndim == 1:
        samples = samples.reshape(-1, 1)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    os.close(fd)
    try:
        with wave.open(tmp, "wb") as w:
            w.setnchannels(samples.shape[1])
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(samples.astype("<i2").tobytes())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def have_ffmpeg():
    return shutil.which("ffmpeg") is not None


def load_audio(path, rate=None, channels=None):
    """Load any audio file as int16 PCM, converting with FFmpeg only if needed.

    Returns (samples, rate, processing) where processing lists any
    conversion applied, so callers can record provenance.
    """
    path = Path(path)
    if path.suffix.lower() == ".wav":
        try:
            data, r = read_wav(path)
            if (rate is None or r == rate) and (channels is None or data.shape[1] == channels):
                return data, r, []
        except (ValueError, wave.Error):
            pass
    if not have_ffmpeg():
        raise RuntimeError(f"{path}: needs conversion but FFmpeg is not installed")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "converted.wav"
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(path),
               "-map", "0:a:0", "-c:a", "pcm_s16le"]
        if rate:
            cmd += ["-ar", str(rate)]
        if channels:
            cmd += ["-ac", str(channels)]
        cmd.append(str(out))
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f"FFmpeg could not decode {path}: {result.stderr[-800:]}")
        data, r = read_wav(out)
    step = {"tool": "ffmpeg", "from": path.suffix.lower().lstrip(".") or "unknown",
            "to": f"pcm_s16le {r} Hz {data.shape[1]} ch"}
    return data, r, [step]


def speech_bounds(samples, rate):
    """Measure where audible speech starts/ends inside a clip.

    Engines pad clips with silence, so a clip boundary is not a speech
    boundary. This uses 10 ms RMS windows: a window counts as speech when it
    is above both -50 dBFS and 30 dB below the clip's loudest window.
    Returns (start, end) relative to the clip, or None if the clip is silent.
    Resolution is one window (10 ms), and provenance must say so.
    """
    mono = np.asarray(samples, dtype=np.float32)
    if mono.ndim == 2:
        mono = mono.mean(axis=1)
    mono /= 32768.0
    win = max(1, int(round(rate * SPEECH_WINDOW_SECONDS)))
    n = len(mono) // win
    if n == 0:
        return None
    rms = np.sqrt(np.mean(mono[: n * win].reshape(n, win) ** 2, axis=1))
    peak = float(rms.max())
    if peak <= 0:
        return None
    threshold = max(10 ** (SPEECH_ABS_FLOOR_DBFS / 20), peak * 10 ** (SPEECH_REL_FLOOR_DB / 20))
    loud = np.nonzero(rms >= threshold)[0]
    if len(loud) == 0:
        return None
    return int(loud[0] * win), int(min(len(mono), (loud[-1] + 1) * win))


def assemble(events, rate, channels=1):
    """Lay out clips and silences back to back.

    events: list of dicts, each either
      {"type": "clip", "samples": int16 array, ...}  or
      {"type": "silence", "frames": int, ...}
    Every event receives integer start_sample/end_sample. Silences are
    literal zero samples. Returns (master int16 (frames, channels), events).
    """
    total = 0
    for ev in events:
        if ev["type"] == "clip":
            s = np.asarray(ev["samples"], dtype=np.int16)
            if s.ndim == 1:
                s = s.reshape(-1, 1)
            if s.shape[1] != channels:
                raise ValueError(f"clip {ev.get('id')}: {s.shape[1]} channels, master has {channels}")
            ev["samples"] = s
            length = s.shape[0]
        else:
            length = int(ev["frames"])
            if length < 0:
                raise ValueError("negative silence")
        ev["start_sample"], ev["end_sample"] = total, total + length
        total += length
    master = np.zeros((total, channels), dtype=np.int16)
    for ev in events:
        if ev["type"] == "clip":
            master[ev["start_sample"]:ev["end_sample"]] = ev["samples"]
    return master, events
