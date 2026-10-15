"""Narration Studio build pipeline: text -> clips -> master WAV + narration.json.

Modes
  build_from_text     story/script + local TTS engine (cached)
  build_from_clips    user-supplied WAV/MP3 clips listed in a manifest
  import_readaloud    Read-Aloud-Main WAV/MP3 + Audacity label track
  verify              re-check a narration folder against its sidecar
"""
import json
import os
import re
import tempfile
from pathlib import Path

import numpy as np

import hashlib

from ns_audio import assemble, load_audio, read_wav, sha256_file, speech_bounds, write_wav
from ns_cache import ClipCache
from ns_text import load_input, word_units

TOOL_VERSION = "0.1.0"
SCHEMA = "filmkit/narration@1.0"

DEFAULT_PAUSES = {          # seconds; sentence/paragraph mirror Read-Aloud-Main defaults
    "sentence": 0.35,
    "paragraph": 0.75,
    "speaker_change": 0.45,
    "heading": 0.9,
    "pause": 0.8,           # "[pause]" with no length
    "beat": 0.6,            # "[beat]"
    "scene_break": 1.5,     # "---"
    "lead_in": 0.0,
    "tail": 0.5,
}

TIMING_NOTE = ("Positions are integer sample frames at audio.sample_rate; start inclusive, end "
               "exclusive. Segment start/end_sample are CLIP boundaries (exact). speech_start/"
               "end_sample are measured inside the clip with a 10 ms energy threshold and mark "
               "audible speech; resolution is one window. No word-internal timing is claimed.")


def _seconds(samples, rate):
    return round(samples / rate, 6)


def _rel(path, base):
    try:
        return os.path.relpath(path, base)
    except ValueError:
        return Path(path).name


def _silence(frames, reason, requested=None):
    return {"type": "silence", "frames": int(frames), "reason": reason, "requested_seconds": requested}


def plan_gaps(items, pauses, rate):
    """Insert silence events between segment items.

    Natural gaps depend on context (sentence / paragraph / speaker change /
    after heading). Explicit pause items replace the natural gap; several in
    a row add up. Silence lengths are rounded to whole samples once, here.
    """
    p = {**DEFAULT_PAUSES, **(pauses or {})}
    frames = lambda s: int(round(float(s) * rate))
    out, prev, explicit = [], None, []
    if p["lead_in"] > 0:
        out.append(_silence(frames(p["lead_in"]), "lead_in", p["lead_in"]))
    for item in items:
        if item["type"] == "pause":
            secs = item["seconds"] if item["seconds"] is not None else p[item["kind"]]
            explicit.append((secs, item["kind"]))
            continue
        if explicit:
            total = sum(s for s, _ in explicit)
            reason = "explicit_" + "+".join(k for _, k in explicit)
            out.append(_silence(frames(total), reason, total))
            explicit = []
        elif prev is not None:
            if prev["kind"] == "heading":
                key = "heading"
            elif item["paragraph"] != prev["paragraph"]:
                key = "paragraph"
            elif item["speaker"] != prev["speaker"]:
                key = "speaker_change"
            else:
                key = "sentence"
            out.append(_silence(frames(p[key]), key, p[key]))
        out.append({"type": "clip", "segment": item})
        prev = item
    trailing = sum(s for s, _ in explicit) + p["tail"]
    if trailing > 0:
        out.append(_silence(frames(trailing), "tail", trailing))
    return [ev for ev in out if ev["type"] == "clip" or ev["frames"] > 0]


def _resample(samples, rate, target_rate):
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "in.wav"
        write_wav(src, samples, rate)
        data, r, _ = load_audio(src, rate=target_rate, channels=samples.shape[1])
    return data


def write_outputs(out_dir, mode, events, master, rate, extra):
    """Write narration.wav, narration.json, narration.srt, narration-labels.txt."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    wav_path = out_dir / "narration.wav"
    write_wav(wav_path, master, rate)
    total = int(master.shape[0])
    segments, silences, order = [], [], []
    gap_n = 0
    for ev in events:
        if ev["type"] == "clip":
            seg = ev["segment"]
            rel = ev.get("speech")
            entry = {
                "id": seg["id"], "speaker": seg.get("speaker", "narrator"),
                "kind": seg.get("kind", "line"), "paragraph": seg.get("paragraph"),
                "source_text": seg.get("source_text"), "display_text": seg.get("display_text"),
                "spoken_text": seg.get("spoken_text"), "substitutions": seg.get("substitutions", []),
                "words": seg.get("words") or word_units(seg.get("display_text") or "", []),
                "start_sample": ev["start_sample"], "end_sample": ev["end_sample"],
                "start_seconds": _seconds(ev["start_sample"], rate),
                "end_seconds": _seconds(ev["end_sample"], rate),
                "speech_start_sample": ev["start_sample"] + rel[0] if rel else None,
                "speech_end_sample": ev["start_sample"] + rel[1] if rel else None,
                "speech_bounds_source": ev.get("speech_source") or ("energy_threshold_10ms" if rel else "not_detected"),
                "word_times": seg.get("word_times") or [],
            }
            for k in ("voice", "cache", "clip_source", "processing"):
                if ev.get(k) is not None:
                    entry[k] = ev[k]
            segments.append(entry)
            order.append(seg["id"])
        else:
            gap_n += 1
            sid = f"gap{gap_n:03d}"
            silences.append({"id": sid, "start_sample": ev["start_sample"],
                             "end_sample": ev["end_sample"], "kind": ev.get("kind", "inserted"),
                             "reason": ev["reason"], "requested_seconds": ev.get("requested_seconds"),
                             "frames": ev["end_sample"] - ev["start_sample"]})
            order.append(sid)
    sidecar = {
        "schema": SCHEMA,
        "schema_status": "provisional (see narration_studio/references/narration-schema.md)",
        "generator": {"tool": "narration_studio", "version": TOOL_VERSION},
        "mode": mode,
        "audio": {"file": wav_path.name, "sha256": sha256_file(wav_path), "sample_rate": rate,
                  "channels": int(master.shape[1]), "sample_format": "pcm_s16le",
                  "total_samples": total, "duration_seconds": _seconds(total, rate)},
        "timing_conventions": TIMING_NOTE,
        "segments": segments,
        "silences": silences,
        "order": order,
        "word_timing": {"available": False,
                        "reason": "Not implemented in M1. Needs native engine timestamps or forced alignment."},
        **extra,
    }
    sidecar.setdefault("warnings", [])
    (out_dir / "narration.json").write_text(json.dumps(sidecar, indent=2, ensure_ascii=False), encoding="utf-8")
    write_srt(out_dir / "narration.srt", segments, rate)
    write_labels(out_dir / "narration-labels.txt", segments, rate)
    return sidecar


def _ts(samples, rate):
    ms = int(round(samples * 1000 / rate))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(path, segments, rate):
    """Plain captions: one cue per segment, timed to measured speech."""
    lines = []
    for i, seg in enumerate(segments, 1):
        a = seg["speech_start_sample"] if seg["speech_start_sample"] is not None else seg["start_sample"]
        b = seg["speech_end_sample"] if seg["speech_end_sample"] is not None else seg["end_sample"]
        lines += [str(i), f"{_ts(a, rate)} --> {_ts(b, rate)}", seg["display_text"] or "", ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def write_labels(path, segments, rate):
    """Audacity label track (same format Read-Aloud-Main exports)."""
    rows = [f"{seg['start_sample'] / rate:.6f}\t{seg['end_sample'] / rate:.6f}\t{seg['display_text'] or ''}"
            for seg in segments]
    Path(path).write_text("\n".join(rows) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- modes

def build_from_text(input_path, out_dir, engine_factory, config=None, cache_dir=None):
    """Story/script -> narration. engine_factory(model_dir_or_None) -> engine."""
    config = config or {}
    items, raw = load_input(input_path, config.get("pronunciations"), config.get("detect_speakers", True))
    if not any(i["type"] == "segment" for i in items):
        raise ValueError(f"{input_path}: no speakable text found")
    cast = {"narrator": {}, **(config.get("cast") or {})}
    engines = {}

    def engine_for(voice):
        key = voice.get("model_dir")
        if key not in engines:
            engines[key] = engine_factory(key)
        return engines[key]

    master_engine = engine_for(cast["narrator"])
    rate = master_engine.sample_rate
    cache = ClipCache(cache_dir or Path(out_dir) / "cache" / "audio")
    warnings, unknown = [], set()
    events = plan_gaps(items, config.get("pauses"), rate)
    for ev in events:
        if ev["type"] != "clip":
            ev["kind"] = "inserted"
            continue
        seg = ev["segment"]
        voice = cast.get(seg["speaker"])
        if voice is None:
            voice = cast["narrator"]
            if seg["speaker"] not in unknown:
                unknown.add(seg["speaker"])
                warnings.append(f"Speaker {seg['speaker']!r} has no cast entry; using the narrator voice.")
        engine = engine_for(voice)
        request = {**engine.identity(voice), "spoken_text": seg["spoken_text"]}
        samples, clip_rate, key, hit = cache.get_or_make(
            request, lambda: engine.synthesize(seg["spoken_text"], voice), label=seg["id"])
        processing = []
        if clip_rate != rate:
            samples = _resample(samples, clip_rate, rate)
            processing.append({"tool": "ffmpeg", "resample": [clip_rate, rate]})
        ev["samples"] = samples
        ev["speech"] = speech_bounds(samples, rate)
        ev["voice"] = {k: v for k, v in request.items() if k not in ("spoken_text", "model_sha256")}
        ev["cache"] = {"key": key, "hit": hit}
        if processing:
            ev["processing"] = processing
        if ev["speech"] is None:
            warnings.append(f"Segment {seg['id']}: no audible speech detected in its clip.")
    master, events = assemble(events, rate, channels=1)
    extra = {
        "source": {"file": Path(input_path).name, "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                   "ids": "from script.json" if str(input_path).endswith(".json") else
                          "positional (s001...); supply script.json for IDs that survive edits"},
        "build": {"engine": master_engine.identity(cast["narrator"]),
                  "pauses": {**DEFAULT_PAUSES, **(config.get("pauses") or {})},
                  "cache": {"dir": _rel(cache.root, out_dir), "hits": len(cache.hits),
                            "misses": len(cache.misses), "synthesized": cache.misses,
                            "rejected_entries": cache.rejected}},
        "warnings": warnings,
    }
    return write_outputs(out_dir, "generated", events, master, rate, extra)


def build_from_clips(manifest_path, out_dir):
    """Assemble supplied clips. Manifest items: {"id","clip","text","speaker"} or {"pause": s}."""
    manifest_path = Path(manifest_path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    base = manifest_path.parent
    rate, channels = data.get("sample_rate"), data.get("channels")
    default_gap = float(data.get("default_gap", 0.0))
    events, warnings, pending, prev_clip = [], [], 0.0, False
    if data.get("lead_in"):
        events.append(_silence(0, "lead_in", float(data["lead_in"])))
    for n, item in enumerate(data["items"], 1):
        if "pause" in item:
            pending += float(item["pause"])
            continue
        clip_path = base / item["clip"]
        samples, r, processing = load_audio(clip_path, rate, channels)
        rate, channels = rate or r, channels or samples.shape[1]
        if pending or (prev_clip and default_gap):
            secs = pending or default_gap
            events.append(_silence(0, "explicit_pause" if pending else "default_gap", secs))
            pending = 0.0
        text = item.get("text")
        seg = {"id": str(item.get("id", f"c{n:03d}")), "speaker": item.get("speaker", "narrator"),
               "kind": "line", "paragraph": None, "source_text": text, "display_text": text,
               "spoken_text": item.get("spoken_text", text), "substitutions": []}
        events.append({"type": "clip", "segment": seg, "samples": samples,
                       "speech": speech_bounds(samples, r),
                       "clip_source": {"file": item["clip"], "sha256": sha256_file(clip_path)},
                       "processing": processing or None})
        prev_clip = True
    tail = pending + float(data.get("tail", 0.0))
    if tail:
        events.append(_silence(0, "tail", tail))
    if rate is None:
        raise ValueError("manifest has no clips")
    for ev in events:  # silence lengths need the final master rate
        if ev["type"] == "silence":
            ev["frames"] = int(round(ev["requested_seconds"] * rate))
            ev["kind"] = "inserted"
    events = [ev for ev in events if ev["type"] == "clip" or ev["frames"] > 0]
    master, events = assemble(events, rate, channels)
    extra = {"source": {"file": manifest_path.name, "sha256": sha256_file(manifest_path)},
             "warnings": warnings}
    return write_outputs(out_dir, "assembled_clips", events, master, rate, extra)


def parse_labels(path):
    rows = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split("\t", 2)
        if len(parts) < 2:
            raise ValueError(f"{path}:{n}: not an Audacity label line")
        rows.append((float(parts[0]), float(parts[1]), parts[2] if len(parts) > 2 else ""))
    return rows


def import_readaloud(audio_path, labels_path, out_dir):
    """Read-Aloud-Main export (WAV preferred, MP3 accepted) + label track -> narration.json."""
    samples, rate, processing = load_audio(audio_path)
    total = samples.shape[0]
    warnings = []
    if processing:
        warnings.append("Audio was decoded from a compressed format. MP3 encoding/decoding can add "
                        "padding at the start, which shifts every label slightly. Export WAV from "
                        "Read Aloud for exact timing.")
    labels = parse_labels(labels_path)
    events, cursor, gap_reasons = [], 0, []
    for i, (t0, t1, text) in enumerate(labels, 1):
        a, b = int(round(t0 * rate)), int(round(t1 * rate))
        if a < cursor or b <= a:
            raise ValueError(f"label {i} overlaps or is out of order ({t0}..{t1})")
        if b > total:
            if b - total > rate * 0.05:
                raise ValueError(f"label {i} ends {(b - total) / rate:.3f}s after the audio ends")
            warnings.append(f"Label {i} ends {b - total} samples past the audio; clamped.")
            b = total
        if a > cursor:
            events.append({"type": "silence", "frames": a - cursor, "kind": "inferred_from_labels",
                           "reason": "lead_in" if cursor == 0 else "gap", "requested_seconds": None,
                           "samples": samples[cursor:a]})
        clip = samples[a:b]
        seg = {"id": f"s{i:03d}", "speaker": "narrator", "kind": "line", "paragraph": None,
               "source_text": text, "display_text": text, "spoken_text": None, "substitutions": []}
        events.append({"type": "clip", "segment": seg, "samples": clip, "speech": speech_bounds(clip, rate)})
        cursor = b
    if cursor < total:
        events.append({"type": "silence", "frames": total - cursor, "kind": "inferred_from_labels",
                       "reason": "tail", "requested_seconds": None, "samples": samples[cursor:]})
    master, events = assemble(events, rate, samples.shape[1])
    if not np.array_equal(master, samples):
        raise AssertionError("internal error: re-tiled audio differs from the imported audio")
    extra = {"source": {"file": Path(audio_path).name, "sha256": sha256_file(audio_path),
                        "labels": Path(labels_path).name, "labels_sha256": sha256_file(labels_path),
                        "note": "Read-Aloud labels carry the draft text; pronunciation-dictionary "
                                "substitutions are not exported, so spoken_text is null."},
             "warnings": warnings}
    if processing:
        extra["processing"] = processing
    return write_outputs(out_dir, "imported_readaloud", events, master, rate, extra)


LOW_CONFIDENCE = 0.5
SEGMENT_FOUND = 0.3        # mean letter-match below this: line treated as missing from the recording
SEGMENT_DOUBTFUL = 0.7     # mean below this: line probably differs from the script


def align_recording(recording, story, out_dir, recognizer, config=None):
    """A narration recorded outside this tool + its script -> narration.json.

    The recording is the timing authority and is copied unchanged (as PCM)
    into narration.wav. Each script line is located by recognizing the
    recording and aligning the heard words to the script's words; word starts
    are refined against the audio. Lines that can't be found, or that seem
    to differ from the script, are reported as warnings, never silently fixed.
    """
    from ns_words import (ASR_EARLY_BIAS, METHOD, VALIDATION, align_units, energy_envelope,
                          heard_chars, refine_sequence, transcribe_long)
    config = config or {}
    items, raw_text = load_input(story, config.get("pronunciations"), config.get("detect_speakers", True))
    segs = [i for i in items if i["type"] == "segment"]
    if not segs:
        raise ValueError(f"{story}: no speakable text found")
    samples, rate, processing = load_audio(recording)
    total = samples.shape[0]
    heard_text, tokens = transcribe_long(recognizer, samples, rate)
    heard, times = heard_chars(tokens)
    units = [{"key": (si, w["id"]), "spoken": w["spoken"]}
             for si, s in enumerate(segs) for w in s["words"] if not w.get("spoken_with_previous")]
    raw = align_units(units, heard, times)
    env, win = energy_envelope(samples, rate)
    timed = refine_sequence([u["key"] for u in units], raw, env, win, rate)

    peak = float(env.max()) if len(env) else 0.0
    quiet = max(10 ** (-50 / 20), peak * 10 ** (-30 / 20))

    def speech_end_after(start_sample, limit):
        """First point after start where the audio stays quiet for 120 ms (or limit)."""
        i, need = start_sample // win + int(0.1 * rate / win), max(1, int(0.12 * rate / win))
        run = 0
        while i < min(len(env), limit // win):
            run = run + 1 if env[i] < quiet else 0
            if run >= need:
                return (i - need + 1) * win
            i += 1
        return limit

    warnings, placed = [], []
    for si, seg in enumerate(segs):
        keys = [(si, w["id"]) for w in seg["words"] if not w.get("spoken_with_previous")]
        confs = [timed[k]["confidence"] for k in keys]
        starts = [timed[k]["start_sample"] for k in keys if timed[k]["start_sample"] is not None]
        mean_conf = sum(confs) / len(confs) if confs else 0.0
        if not starts or mean_conf < SEGMENT_FOUND:
            warnings.append(f"Line {seg['id']} ({seg['display_text'][:50]!r}) was not found in the recording "
                            f"(match {mean_conf:.0%}); left out of the timing.")
            continue
        if mean_conf < SEGMENT_DOUBTFUL:
            warnings.append(f"Line {seg['id']} ({seg['display_text'][:50]!r}) only partly matches the recording "
                            f"(match {mean_conf:.0%}); the reading may differ from the script.")
        seg["_si"], seg["_start"], seg["_last_word"], seg["_conf"] = si, min(starts), max(starts), mean_conf
        placed.append(seg)
    events, cursor = [], 0
    for n, seg in enumerate(placed):
        start = max(seg["_start"], cursor)
        limit = placed[n + 1]["_start"] if n + 1 < len(placed) else total
        end = speech_end_after(max(seg["_last_word"], start), limit)
        if end <= start:
            warnings.append(f"Line {seg['id']} overlaps the next line in the recording; left out.")
            continue
        if start > cursor:
            gap = samples[cursor:start]
            events.append({"type": "silence", "frames": start - cursor, "kind": "gap_in_recording",
                           "reason": "lead_in" if cursor == 0 else "gap", "requested_seconds": None,
                           "samples": gap})
            genv, gwin = energy_envelope(gap, rate)
            if (genv > quiet).sum() * gwin / rate > 0.3 and (start - cursor) / rate > 0.5:
                warnings.append(f"Speech between {cursor / rate:.2f}s and {start / rate:.2f}s isn't in the script "
                                "(ad-lib, retake or a missing line?).")
        entries = []
        for w in seg["words"]:
            t = timed.get((seg["_si"], w["id"]))
            if w.get("spoken_with_previous") or t is None:
                continue
            e = {"word_id": w["id"], "text": w["text"], "start_sample": t["start_sample"], "end_sample": None,
                 "confidence": t["confidence"], "source": METHOD, "how": t["how"]}
            if t.get("raw_sample") is not None:
                e["raw_asr_sample"] = t["raw_sample"]
            if e["start_sample"] is not None:
                e["start_sample"] = min(max(e["start_sample"], start), end - 1)
                e["start_seconds"] = _seconds(e["start_sample"], rate)
            if t["confidence"] < LOW_CONFIDENCE:
                e["low_confidence"] = True
            entries.append(e)
        timed_entries = [e for e in entries if e["start_sample"] is not None]
        for cur, nxt in zip(timed_entries, timed_entries[1:] + [None]):
            cur["end_sample"] = max(nxt["start_sample"] if nxt else end, cur["start_sample"] + 1)
        seg["word_times"] = entries
        events.append({"type": "clip", "segment": seg, "samples": samples[start:end],
                       "speech": (0, end - start), "speech_source": "asr_alignment"})
        cursor = end
    if cursor < total:
        events.append({"type": "silence", "frames": total - cursor, "kind": "gap_in_recording",
                       "reason": "tail", "requested_seconds": None, "samples": samples[cursor:]})
    master, events = assemble(events, rate, samples.shape[1])
    if not np.array_equal(master, samples):
        raise AssertionError("internal error: re-tiled audio differs from the recording")
    for seg in placed:
        for k in ("_si", "_start", "_last_word", "_conf"):
            seg.pop(k, None)
    extra = {"source": {"file": Path(story).name, "sha256": hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
                        "recording": Path(recording).name, "recording_sha256": sha256_file(recording)},
             "heard_text": heard_text,
             "word_timing": {"available": True, "segments": [s["id"] for s in placed], "method": METHOD,
                             "recognizer": recognizer.identity, "early_bias_seconds": ASR_EARLY_BIAS,
                             "validation": VALIDATION, "low_confidence_below": LOW_CONFIDENCE,
                             "note": "Segment bounds come from aligned words: start = first word onset, "
                                     "end = where the voice stops. Validation figures are for synthetic speech."},
             "warnings": warnings}
    if processing:
        extra["processing"] = processing
    return write_outputs(out_dir, "aligned_recording", events, master, rate, extra)


def _word_key(text):
    return re.sub(r"[^a-z0-9']", "", (text or "").lower())


def add_word_times(out_dir, recognizer, only=None, find=None):
    """Fill segments[].word_times in an existing narration folder. Audio is untouched.

    only: segment IDs to process; find: words (any case) whose segments to process.
    Returns (sidecar, {found_word: [entries]}).
    """
    from ns_words import ASR_EARLY_BIAS, METHOD, VALIDATION, time_words
    out_dir = Path(out_dir)
    side = json.loads((out_dir / "narration.json").read_text(encoding="utf-8"))
    wav = out_dir / side["audio"]["file"]
    if sha256_file(wav) != side["audio"]["sha256"]:
        raise ValueError("narration.wav no longer matches narration.json; rebuild before adding word timing")
    samples, rate = read_wav(wav)
    wanted = {_word_key(w) for w in (find or []) if _word_key(w)}
    chosen = []
    for seg in side["segments"]:
        words = seg.get("words") or word_units(seg.get("display_text") or "", [])
        seg["words"] = words
        if only and seg["id"] not in only:
            continue
        if wanted and not any(_word_key(w["text"]) in wanted for w in words):
            continue
        chosen.append(seg)
    found = {}
    for seg in chosen:
        spoken_known = seg.get("spoken_text") is not None
        units = [{"key": w["id"], "spoken": w["spoken"] if spoken_known else w["text"]}
                 for w in seg["words"] if not w.get("spoken_with_previous")]
        a, b = seg["start_sample"], seg["end_sample"]
        timed, heard = time_words(samples[a:b], rate, units, recognizer, base_sample=a)
        speech_end = seg.get("speech_end_sample") or b
        entries, prev = [], None
        for w in seg["words"]:
            if w.get("spoken_with_previous") and prev is not None:
                entries.append({"word_id": w["id"], "text": w["text"], "spoken_with": prev["word_id"],
                                "start_sample": prev["start_sample"], "source": "covered_by_previous_word"})
                continue
            t = timed.get(w["id"], {"start_sample": None, "confidence": 0.0, "how": "unmatched"})
            e = {"word_id": w["id"], "text": w["text"], "start_sample": t["start_sample"],
                 "end_sample": None, "confidence": t["confidence"], "source": METHOD, "how": t["how"]}
            if t.get("raw_sample") is not None:
                e["raw_asr_sample"] = t["raw_sample"]
            if e["start_sample"] is not None:
                e["start_sample"] = min(max(e["start_sample"], a), b - 1)
                e["start_seconds"] = _seconds(e["start_sample"], rate)
            if t["confidence"] < LOW_CONFIDENCE:
                e["low_confidence"] = True
            entries.append(e)
            prev = e
        timed_entries = [e for e in entries if e.get("start_sample") is not None and "spoken_with" not in e]
        for cur, nxt in zip(timed_entries, timed_entries[1:] + [None]):
            end = nxt["start_sample"] if nxt else max(speech_end, cur["start_sample"] + 1)
            cur["end_sample"] = max(end, cur["start_sample"] + 1)
        seg["word_times"] = entries
        seg["heard_text"] = heard
        for e in entries:
            if wanted and _word_key(e["text"]) in wanted:
                found.setdefault(e["text"], []).append({"segment": seg["id"], **e})
    prior = side.get("word_timing") or {}
    done = sorted(set(prior.get("segments", [])) | {s["id"] for s in chosen},
                  key=[s["id"] for s in side["segments"]].index)
    side["word_timing"] = {
        "available": bool(done), "segments": done, "method": METHOD,
        "recognizer": recognizer.identity, "early_bias_seconds": ASR_EARLY_BIAS,
        "validation": VALIDATION, "low_confidence_below": LOW_CONFIDENCE,
        "note": "word start_sample = refined audible onset (use for reveals, rounded UP to the next frame). "
                "end_sample = next word's start (approximate). Skip entries flagged low_confidence for reveals."}
    (out_dir / "narration.json").write_text(json.dumps(side, indent=2, ensure_ascii=False), encoding="utf-8")
    return side, found


def verify(out_dir):
    """Deterministic checks of a narration folder. Returns a list of problems."""
    out_dir = Path(out_dir)
    problems = []
    side = json.loads((out_dir / "narration.json").read_text(encoding="utf-8"))
    audio = side["audio"]
    wav = out_dir / audio["file"]
    if sha256_file(wav) != audio["sha256"]:
        problems.append("narration.wav does not match the sidecar checksum (stale or edited)")
    samples, rate = read_wav(wav)
    if rate != audio["sample_rate"]:
        problems.append(f"sample rate {rate} != sidecar {audio['sample_rate']}")
    if samples.shape[0] != audio["total_samples"]:
        problems.append(f"WAV has {samples.shape[0]} frames, sidecar says {audio['total_samples']}")
    events = sorted([("segment", s) for s in side["segments"]] + [("silence", s) for s in side["silences"]],
                    key=lambda e: e[1]["start_sample"])
    cursor = 0
    for kind, ev in events:
        if ev["start_sample"] != cursor:
            problems.append(f"{ev['id']}: starts at {ev['start_sample']}, expected {cursor} (gap or overlap)")
        if ev["end_sample"] <= ev["start_sample"]:
            problems.append(f"{ev['id']}: empty or negative span")
        if kind == "silence" and ev.get("kind") == "inserted" and np.any(samples[ev["start_sample"]:ev["end_sample"]]):
            problems.append(f"{ev['id']}: inserted silence contains non-zero samples")
        if kind == "segment":
            for w in ev.get("word_times") or []:
                if w.get("start_sample") is not None and not (ev["start_sample"] <= w["start_sample"] < ev["end_sample"]):
                    problems.append(f"{ev['id']}/{w['word_id']}: word start outside its segment")
        if kind == "segment" and ev.get("speech_start_sample") is not None:
            if not (ev["start_sample"] <= ev["speech_start_sample"] < ev["speech_end_sample"] <= ev["end_sample"]):
                problems.append(f"{ev['id']}: speech bounds fall outside its clip")
        cursor = ev["end_sample"]
    if cursor != audio["total_samples"]:
        problems.append(f"events cover {cursor} samples, audio has {audio['total_samples']}")
    return problems
