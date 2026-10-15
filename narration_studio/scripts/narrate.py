#!/usr/bin/env python3
"""Narration Studio command line.

  narrate.py build STORY.md --model-dir VOICE_DIR --out OUT [--config cfg.json]
  narrate.py assemble clips.json --out OUT
  narrate.py import-readaloud narration.wav labels.txt --out OUT
  narrate.py verify OUT

Every mode writes OUT/narration.wav, narration.json, narration.srt and
narration-labels.txt, then runs `verify` and prints a short report.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ns_build import build_from_clips, build_from_text, import_readaloud, verify  # noqa: E402
from ns_engines import make_engine  # noqa: E402


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
    for w in side.get("warnings", []):
        print("WARNING:", w)
    problems = verify(out_dir)
    for p in problems:
        print("VERIFY FAILED:", p)
    if not problems:
        print("Verify: OK (events tile the audio exactly; silences are zero; checksums match)")
    return 1 if problems else 0


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

    s = sub.add_parser("assemble", help="join supplied clips listed in a manifest")
    s.add_argument("manifest")
    s.add_argument("--out", required=True)

    r = sub.add_parser("import-readaloud", help="convert a Read Aloud export + label track")
    r.add_argument("audio")
    r.add_argument("labels")
    r.add_argument("--out", required=True)

    v = sub.add_parser("verify", help="re-check an output folder against its narration.json")
    v.add_argument("out")

    a = ap.parse_args(argv)
    if a.cmd == "verify":
        problems = verify(a.out)
        print("\n".join(problems) if problems else "Verify: OK")
        return 1 if problems else 0
    if a.cmd == "build":
        config = json.loads(Path(a.config).read_text(encoding="utf-8")) if a.config else {}
        default_dir = a.model_dir or config.get("model_dir")
        if a.config and default_dir and not a.model_dir:
            default_dir = str((Path(a.config).parent / default_dir).resolve())
        def factory(model_dir):
            if model_dir and a.config and not Path(model_dir).is_absolute():
                model_dir = str((Path(a.config).parent / model_dir).resolve())
            return make_engine(a.engine, model_dir or default_dir)
        side = build_from_text(a.input, a.out, factory, config, a.cache)
    elif a.cmd == "assemble":
        side = build_from_clips(a.manifest, a.out)
    else:
        side = import_readaloud(a.audio, a.labels, a.out)
    return report(side, a.out)


if __name__ == "__main__":
    sys.exit(main())
