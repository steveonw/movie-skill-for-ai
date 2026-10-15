"""Word-level timing: local speech recognition + fuzzy alignment + onset refinement.

Pipeline for one stretch of audio whose script words are known:
  1. A local sherpa-onnx transducer (e.g. Zipformer, Apache-2.0) transcribes it
     and gives a timestamp for every token it hears.
  2. The heard letters are aligned to the script's spoken letters
     (difflib), so mishearings ("staple" -> "STABLE", "interns" -> "IN TURNS")
     and numbers ("41" -> "FORTY ONE") still map to the right script word.
  3. Raw recognizer timestamps run EARLY (measured: 63-285 ms, mean 126 ms on
     the Amy voice). Each word start is therefore refined against the audio:
     among the energy dips near the expected onset, pick the one closest to
     raw time + measured bias, always preferring a real pause.

Validation (2026-10-14, 60 known-onset cases, 30 held out): mean error
-2.6 ms, worst -15 ms, no case more than one 30 fps frame early. Measured on
synthetic Piper/VITS speech only; real human recordings are untested.
"""
import contextlib
import os
import re
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np

from ns_audio import sha256_file

ASR_EARLY_BIAS = 0.12       # seconds; measured mean early bias of raw timestamps
REFINE_BACK = 0.03          # search this far before the raw timestamp...
REFINE_LOOK = 0.35          # ...and this far after it
REFINE_WINDOW = 0.005       # 5 ms energy windows
PAUSE_FLOOR = 0.01          # dip below 1% of peak energy = a real pause
METHOD = "asr_timestamps+energy_onset_refinement"
VALIDATION = {"cases": 60, "held_out": 30, "mean_error_ms": -2.6, "worst_error_ms": -15,
              "more_than_one_30fps_frame_early": 0,
              "conditions": "synthetic Piper/VITS speech (Amy voice), zipformer-small-en; human speech untested"}

# --------------------------------------------------------------------------- numbers -> words

_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen " \
        "fifteen sixteen seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def _cardinal(n):
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else " " + _ONES[n % 10])
    for size, name in ((10 ** 9, "billion"), (10 ** 6, "million"), (1000, "thousand"), (100, "hundred")):
        if n >= size:
            rest = n % size
            return _cardinal(n // size) + " " + name + ("" if rest == 0 else " " + _cardinal(rest))
    return str(n)


def number_words(token):
    """'41' -> 'forty one', '2026' -> 'twenty twenty six', '3.5' -> 'three point five'."""
    t = token.replace(",", "")
    m = re.fullmatch(r"(\d+)(?:\.(\d+))?", t)
    if not m:
        return token
    whole, frac = m.group(1), m.group(2)
    n = int(whole)
    if frac is None and len(whole) == 4 and 1100 <= n <= 2099 and n % 100 != 0 and not 2000 <= n <= 2009:
        words = _cardinal(n // 100) + " " + (("oh " + _ONES[n % 100]) if n % 100 < 10 else _cardinal(n % 100))
    else:
        words = _cardinal(n)
    if frac:
        words += " point " + " ".join(_ONES[int(d)] for d in frac)
    return words


def normalize_spoken(text):
    """Uppercase letters and spaces only, numbers spelled out, for matching."""
    out = []
    for tok in re.findall(r"[A-Za-z0-9.,']+", text or ""):
        tok = tok.strip(".,'")
        if not tok:
            continue
        if any(ch.isdigit() for ch in tok):
            tok = number_words(tok)
        out.append(tok)
    s = " ".join(out).upper().replace("-", " ")
    return re.sub(r"[^A-Z' ]", "", s).strip()


# --------------------------------------------------------------------------- recognizer

@contextlib.contextmanager
def _quiet_stderr():
    """sherpa-onnx's C++ layer logs a line per resample; keep reports readable."""
    try:
        fd = os.dup(2)
    except OSError:
        yield
        return
    with open(os.devnull, "w") as devnull:
        os.dup2(devnull.fileno(), 2)
        try:
            yield
        finally:
            os.dup2(fd, 2)
            os.close(fd)


class Recognizer:
    """Local sherpa-onnx offline transducer (encoder/decoder/joiner + tokens.txt)."""

    def __init__(self, model_dir, num_threads=None):
        import sherpa_onnx
        d = Path(model_dir)

        def pick(part, prefer_int8):
            files = sorted(d.glob(f"{part}*.onnx"))
            if not files:
                raise FileNotFoundError(f"{model_dir}: no {part}*.onnx (need a transducer ASR model)")
            int8 = [f for f in files if ".int8." in f.name]
            fp = [f for f in files if ".int8." not in f.name]
            return (int8 or fp)[0] if prefer_int8 else (fp or int8)[0]

        enc, dec, join = pick("encoder", True), pick("decoder", False), pick("joiner", True)
        tokens = d / "tokens.txt"
        if not tokens.is_file():
            raise FileNotFoundError(tokens)
        threads = num_threads or max(1, min(4, os.cpu_count() or 1))
        self.rec = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=str(enc), decoder=str(dec), joiner=str(join), tokens=str(tokens),
            num_threads=threads, decoding_method="greedy_search")
        self.identity = {"asr": "sherpa-onnx-transducer", "model": d.name,
                         "encoder": enc.name, "encoder_sha256": sha256_file(enc)}

    def transcribe(self, samples, rate):
        """samples: int16 (frames, ch) or float mono. Returns (text, [(token, seconds)])."""
        x = np.asarray(samples)
        if x.ndim == 2:
            x = x.mean(axis=1)
        if x.dtype != np.float32:
            x = x.astype(np.float32) / 32768.0
        with _quiet_stderr():
            stream = self.rec.create_stream()
            stream.accept_waveform(rate, x)
            self.rec.decode_stream(stream)
        r = stream.result
        return r.text, list(zip(r.tokens, [float(t) for t in r.timestamps]))


def heard_chars(tokens, offset=0.0):
    """Flatten tokens to (string, per-char times). A leading space/'▁' starts a word."""
    chars, times = [], []
    for tok, t in tokens:
        starts_word = tok.startswith((" ", "▁"))
        tok = tok.lstrip(" ▁").upper()
        if starts_word and chars:
            chars.append(" ")
            times.append(t + offset)
        for ch in tok:
            if ch.isalpha() or ch == "'":
                chars.append(ch)
                times.append(t + offset)
    return "".join(chars), times


# --------------------------------------------------------------------------- alignment

def align_units(units, heard, heard_times):
    """Map each script word to a heard time.

    units: [{"key": any, "spoken": str}] in script order.
    Returns {key: (raw_seconds or None, confidence 0..1)}.
    """
    exp, owner = [], []
    for ui, u in enumerate(units):
        norm = normalize_spoken(u["spoken"])
        if not norm:
            continue
        if exp:
            exp.append(" ")
            owner.append(None)
        for ch in norm:
            exp.append(ch)
            owner.append(ui if ch != " " else None)
    exp_s = "".join(exp)
    letters = {}
    for o in owner:
        if o is not None:
            letters[o] = letters.get(o, 0) + 1
    first = {}
    hits = {}
    for a, b, n in SequenceMatcher(None, exp_s, heard, autojunk=False).get_matching_blocks():
        for k in range(n):
            o = owner[a + k]
            if o is None:
                continue
            hits[o] = hits.get(o, 0) + 1
            if o not in first or a + k < first[o][0]:
                first[o] = (a + k, heard_times[b + k])
    result = {}
    for ui, u in enumerate(units):
        if ui not in letters:
            result[u["key"]] = (None, 0.0)
            continue
        conf = hits.get(ui, 0) / letters[ui]
        result[u["key"]] = (first[ui][1] if ui in first else None, round(conf, 3))
    return result


# --------------------------------------------------------------------------- onset refinement

def energy_envelope(samples, rate):
    x = np.asarray(samples, dtype=np.float32)
    if x.ndim == 2:
        x = x.mean(axis=1)
    if np.abs(x).max() > 1.5:
        x = x / 32768.0
    win = max(1, int(rate * REFINE_WINDOW))
    n = len(x) // win
    env = np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, axis=1)) if n else np.zeros(0)
    return np.convolve(env, np.ones(3) / 3, mode="same") if n >= 3 else env, win


def refine_onset(env, win, rate, raw, lo=None, hi=None, bias=ASR_EARLY_BIAS):
    """Refine a raw (early) word time to the audible onset. Seconds in, seconds out.

    lo/hi bound the search (previous word's onset, next word's expected onset).
    Returns (seconds, how) where how is 'refined' or 'raw+bias'.
    """
    if len(env) < 3:
        return raw + bias, "raw+bias"
    peak = float(env.max()) or 1.0
    # After a pause the recognizer stamps the word while still in the silence
    # (measured up to ~0.8 s early). A word can only start where that silence ends.
    i_raw = int(raw * rate / win)
    if 0 <= i_raw < len(env) and env[i_raw] < PAUSE_FLOOR * peak:
        limit = len(env) if hi is None else min(len(env), int(hi * rate / win) + 1)
        limit = min(limit, i_raw + int(1.5 * rate / win))
        rise = max(2 * PAUSE_FLOOR * peak, 2 * float(env[i_raw]))
        j = i_raw
        while j < limit and env[j] < rise:
            j += 1
        if j < limit:
            return j * win / rate, "end_of_pause"
    start = raw - REFINE_BACK if lo is None else max(raw - REFINE_BACK, lo + 0.02)
    end = raw + REFINE_LOOK if hi is None else min(raw + REFINE_LOOK, hi)
    i0, i1 = max(0, int(start * rate / win)), min(len(env) - 1, int(end * rate / win))
    if i1 - i0 < 2:
        return max(raw + bias, start), "raw+bias"
    seg = env[i0:i1 + 1]
    best = None
    for m in range(len(seg)):
        if (m > 0 and seg[m] > seg[m - 1]) or (m < len(seg) - 1 and seg[m] > seg[m + 1]):
            continue  # not a local minimum
        floor = seg[m]
        thr = max(floor * 2.0, floor + 0.02 * peak)
        j = m
        while j < len(seg) and seg[j] < thr:
            j += 1
        if j >= len(seg):
            continue
        onset = (i0 + j) * win / rate
        score = abs(onset - (raw + bias))
        if floor < PAUSE_FLOOR * peak:
            score -= 0.15          # a real pause before the word wins
        elif seg[max(0, m - 8):m + 9].max() < 4 * floor:
            score += 0.05          # shallow wiggle, probably mid-word
        if best is None or score < best[0]:
            best = (score, onset)
    if best is None:
        return max(raw + bias, start), "raw+bias"
    return best[1], "refined"


def refine_sequence(keys, raw, env, win, rate, base_sample=0):
    """Refine raw times for words in script order; starts stay strictly increasing."""
    raws = [raw[k][0] for k in keys]
    out, prev = {}, None
    for i, k in enumerate(keys):
        t, conf = raw[k]
        if t is None:
            out[k] = {"start_sample": None, "confidence": conf, "how": "unmatched"}
            continue
        nxt = next((r for r in raws[i + 1:] if r is not None and r > t), None)
        hi = nxt + ASR_EARLY_BIAS - 0.02 if nxt is not None else None
        sec, how = refine_onset(env, win, rate, t, lo=prev, hi=hi)
        if prev is not None and sec <= prev:
            sec, how = prev + REFINE_WINDOW, "clamped_after_previous"
        prev = sec
        out[k] = {"start_sample": base_sample + int(round(sec * rate)),
                  "raw_sample": base_sample + int(round(t * rate)),
                  "confidence": conf, "how": how}
    return out


def time_words(samples, rate, units, recognizer, base_sample=0):
    """Word timing for one stretch of audio (e.g. one narrated sentence).

    units: [{"key", "spoken"}]. Returns ({key: entry}, heard_text) where entry has
    start_sample (absolute = base_sample + position), raw_sample, confidence, how.
    """
    text, toks = recognizer.transcribe(samples, rate)
    heard, times = heard_chars(toks)
    raw = align_units(units, heard, times)
    env, win = energy_envelope(samples, rate)
    return refine_sequence([u["key"] for u in units], raw, env, win, rate, base_sample), text


def transcribe_long(recognizer, samples, rate, max_chunk=20.0, min_chunk=8.0):
    """Transcribe long audio in pieces cut at the quietest point, so words are not split.

    Returns (full_text, [(token, absolute_seconds)]).
    """
    env, win = energy_envelope(samples, rate)
    total = len(samples)
    texts, tokens, start = [], [], 0
    while start < total:
        end = total
        if (total - start) / rate > max_chunk:
            lo = start + int(min_chunk * rate)
            hi = start + int(max_chunk * rate)
            i0, i1 = lo // win, min(len(env) - 1, hi // win)
            cut_win = i0 + int(np.argmin(env[i0:i1 + 1])) if i1 > i0 else hi // win
            end = min(total, cut_win * win)
        text, toks = recognizer.transcribe(samples[start:end], rate)
        offset = start / rate
        texts.append(text)
        toks = [((" " + tok) if i == 0 and not tok.startswith((" ", "\u2581")) else tok, t)
                for i, (tok, t) in enumerate(toks)]  # never glue words across a cut
        tokens += [(tok, t + offset) for tok, t in toks]
        start = end
    return " ".join(t for t in texts if t), tokens
