#!/usr/bin/env python3
"""Narration Studio command line.

  narrate.py build STORY.md --model-dir VOICE_DIR --out OUT [--config cfg.json] [--asr-model ASR_DIR]
  narrate.py assemble clips.json --out OUT
  narrate.py import-readaloud narration.wav labels.txt --out OUT
  narrate.py words OUT --asr-model ASR_DIR [--find bang,fourteen | --only s002,s004]
  narrate.py align RECORDING.mp3 STORY.md --asr-model ASR_DIR --out OUT [--config cfg.json]
  narrate.py verify OUT

build/assemble/import-readaloud/align write OUT/narration.wav, narration.json,
narration.srt and narration-labels.txt; `words` adds word timing to an existing
folder. Every command finishes with `verify` and a short report.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ns_build import (add_word_times, align_recording, build_from_clips, build_from_text,  # noqa: E402
                      import_readaloud, verify)
from ns_engines import make_engine  # noqa: E402


def check(out_dir):
    problems = verify(out_dir)
    for p in problems:
        print("VERIFY FAILED:", p)
    if not problems:
        print("Verify: OK (events tile the audio exactly; inserted silences are zero; checksums match)")
    return 1 if problems else 0


def report(side, out_dir):
    a = side["audio"]
    print(f"Wrote {Path(out_dir) / a['file']}: {a['duration_seconds']:.2f} s, "
          f"{a['total_samples']} samples @ {a['sample_rate']} Hz, "
          f"{len(side['segments'])} segments, {len(side['silences'])} silences")
    cache = side.get("build", {}).get("cache")
    if cache:
        print(f"Cache: {cache['hits']} reused, {cache['misses']} synthesized"
              + (f" ({', '.join(cache['synthesized'])})" if 0 < cache["misses"] <= 12 else ""))
        if cache["rejected_entries"]:
            print(f"Cache: {len(cache['rejected_entries'])} damaged entries were regenerated")
    wt = side.get("word_timing") or {}
    if wt.get("available"):
        n = sum(len(s.get("word_times") or []) for s in side["segments"])
        low = sum(1 for s in side["segments"] for w in (s.get("word_times") or []) if w.get("low_confidence"))
        print(f"Word timing: {n} words in {len(wt['segments'])} segments"
              + (f", {low} low-confidence (don't use those for reveals)" if low else ""))
    for w in side.get("warnings", []):
        print("WARNING:", w)
    return check(out_dir)


def print_found(found, rate):
    if not found:
        print("No requested words were found in the script.")
    for word, hits in found.items():
        for h in hits:
            if h.get("start_sample") is None:
                print(f"  {word!r} in {h['segment']}: not matched in the audio")
                continue
            flag = "  LOW CONFIDENCE" if h.get("low_confidence") else ""
            print(f"  {word!r} in {h['segment']}: starts at sample {h['start_sample']} "
                  f"({h['start_sample'] / rate:.3f} s), match {h['confidence']:.0%}{flag}")


def load_config(path):
    return json.loads(Path(path).read_text(encoding="utf-8")) if path else {}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="narrate a story/script with a local TTS voice")
    b.add_argument("input", help=".md/.txt story or filmkit script.json")
    b.add_argument("--out", required=True)
    b.add_argument("--config", help="JSON: cast, pronunciations, pauses, detect_speakers")
    b.add_argument("--engine", default="sherpa", help="sherpa (default) or tone (test only)")
    b.add_argument("--model-dir", help="Piper/VITS voice folder for the sherpa engine")
    b.add_argument("--cache", help="clip cache folder (default OUT/cache/audio)")
    b.add_argument("--asr-model", help="also add word timing using this speech-recognition model")

    s = sub.add_parser("assemble", help="join supplied clips listed in a manifest")
    s.add_argument("manifest")
    s.add_argument("--out", required=True)

    r = sub.add_parser("import-readaloud", help="convert a Read Aloud export + label track")
    r.add_argument("audio")
    r.add_argument("labels")
    r.add_argument("--out", required=True)

    w = sub.add_parser("words", help="add word-level timing to an existing narration folder")
    w.add_argument("out")
    w.add_argument("--asr-model", required=True, help="sherpa-onnx transducer ASR folder")
    w.add_argument("--find", help="comma-separated words: only time the lines containing them")
    w.add_argument("--only", help="comma-separated segment IDs to time")

    al = sub.add_parser("align", help="time a recording made outside this tool against its script")
    al.add_argument("recording")
    al.add_argument("story")
    al.add_argument("--asr-model", required=True)
    al.add_argument("--out", required=True)
    al.add_argument("--config", help="pronunciations / detect_speakers, as for build")

    v = sub.add_parser("verify", help="re-check an output folder against its narration.json")
    v.add_argument("out")

    a = ap.parse_args(argv)
    if a.cmd == "verify":
        problems = verify(a.out)
        print("\n".join(problems) if problems else "Verify: OK")
        return 1 if problems else 0
    if a.cmd in ("words", "align") or getattr(a, "asr_model", None):
        from ns_words import Recognizer
        recognizer = Recognizer(a.asr_model)
    if a.cmd == "words":
        find = [x.strip() for x in a.find.split(",")] if a.find else None
        only = {x.strip() for x in a.only.split(",")} if a.only else None
        side, found = add_word_times(a.out, recognizer, only=only, find=find)
        if find:
            print_found(found, side["audio"]["sample_rate"])
        return report(side, a.out)
    if a.cmd == "align":
        side = align_recording(a.recording, a.story, a.out, recognizer, load_config(a.config))
        return report(side, a.out)
    if a.cmd == "build":
        config = load_config(a.config)
        default_dir = a.model_dir or config.get("model_dir")
        if a.config and default_dir and not a.model_dir:
            default_dir = str((Path(a.config).parent / default_dir).resolve())

        def factory(model_dir):
            if model_dir and a.config and not Path(model_dir).is_absolute():
                model_dir = str((Path(a.config).parent / model_dir).resolve())
            return make_engine(a.engine, model_dir or default_dir)
        side = build_from_text(a.input, a.out, factory, config, a.cache)
        if a.asr_model:
            side, _ = add_word_times(a.out, recognizer)
    elif a.cmd == "assemble":
        side = build_from_clips(a.manifest, a.out)
    else:
        side = import_readaloud(a.audio, a.labels, a.out)
    return report(side, a.out)


if __name__ == "__main__":
    sys.exit(main())
