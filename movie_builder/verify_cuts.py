#!/usr/bin/env python3
"""Verify adjacent encoded video frames at still-image cut boundaries."""
import argparse
import io
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageOps, ImageStat


def decoded_frame(video, index):
    cmd = ["ffmpeg", "-v", "error", "-i", str(video), "-vf",
           f"select=eq(n\\,{index})", "-frames:v", "1",
           "-f", "image2pipe", "-vcodec", "png", "-"]
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode or not p.stdout:
        raise RuntimeError(f"Cannot decode frame {index}: " + p.stderr.decode(errors="replace")[-1000:])
    with Image.open(io.BytesIO(p.stdout)) as im:
        return im.convert("RGB")


def error(frame, image):
    with Image.open(image) as original:
        ref = ImageOps.fit(original.convert("RGB"), frame.size)
    return sum(ImageStat.Stat(ImageChops.difference(frame, ref)).mean) / 3


def verify(spec_path, video_path, tolerance=35, min_separation=8):
    spec_path = Path(spec_path).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    fps = int(spec.get("fps", 30))
    if not 1 <= fps <= 60:
        raise ValueError("Invalid fps")
    shots = spec.get("shots", [])
    if len(shots) < 2:
        raise ValueError("Need >=2 shots for a cut verification")
    frame_counts = [round(float(s["duration"]) * fps) for s in shots]
    if any(n <= 0 for n in frame_counts):
        raise ValueError("Shot must last at least one frame")
    sources = [(spec_path.parent / s["image"]).resolve() for s in shots]
    boundary = 0
    checks = []
    for i in range(len(shots) - 1):
        boundary += frame_counts[i]
        for frame_no, expected, other in [
            (boundary - 1, sources[i], sources[i + 1]),
            (boundary, sources[i + 1], sources[i])
        ]:
            frame = decoded_frame(video_path, frame_no)
            good = error(frame, expected)
            bad = error(frame, other)
            checks.append({"frame": frame_no, "expected": expected.name,
                           "mae": round(good, 3), "other_mae": round(bad, 3),
                           "pass": good <= tolerance and bad - good >= min_separation})
    return {"pass": all(x["pass"] for x in checks), "checks": checks,
            "warning": "Visual frame boundary check; not spoken-word alignment"}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("project_json")
    p.add_argument("video_mp4")
    a = p.parse_args()
    result = verify(a.project_json, a.video_mp4)
    print(json.dumps(result, indent=2))
    if not result["pass"]:
        raise SystemExit(1)
