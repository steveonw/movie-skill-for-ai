#!/usr/bin/env python3
"""Minimal standalone image+audio -> MP4 renderer. Requires FFmpeg/ffprobe."""
import argparse
import json
import subprocess
from pathlib import Path

def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("Command failed:\n" + " ".join(map(str, cmd)) + "\n" + result.stderr[-3000:])
    return result.stdout

def render(spec_path, output_path):
    spec_path = Path(spec_path).resolve()
    data = json.loads(spec_path.read_text(encoding="utf-8"))
    fps = int(data.get("fps", 30))
    width, height = int(data.get("width", 640)), int(data.get("height", 360))
    if not (1 <= fps <= 60 and 64 <= width <= 3840 and 64 <= height <= 2160):
        raise ValueError("Invalid video profile")
    shots = data["shots"]
    if not shots:
        raise ValueError("No shots")
    audio = (spec_path.parent / data["audio"]).resolve()
    if not audio.is_file():
        raise FileNotFoundError(audio)
    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    lengths = []
    for shot in shots:
        image = (spec_path.parent / shot["image"]).resolve()
        if not image.is_file():
            raise FileNotFoundError(image)
        frames = round(float(shot["duration"]) * fps)
        if frames < 1:
            raise ValueError(f"Shot must last at least one frame: {image}")
        lengths.append(frames)
        args += ["-loop", "1", "-framerate", str(fps), "-t", f"{frames/fps:.9f}", "-i", str(image)]
    args += ["-i", str(audio)]
    filters = []
    for index in range(len(shots)):
        filters.append(f"[{index}:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1,format=yuv420p[v{index}]")
    inputs = "".join(f"[v{i}]" for i in range(len(shots)))
    filters.append(f"{inputs}concat=n={len(shots)}:v=1:a=0[v]")
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    args += ["-filter_complex", ";".join(filters), "-map", "[v]", "-map", f"{len(shots)}:a:0",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(fps),
             "-c:a", "aac", "-ar", "48000", "-movflags", "+faststart", "-shortest",
             str(output_path)]
    run(args)
    raw = run(["ffprobe", "-v", "error", "-show_entries",
               "format=duration:stream=codec_type,codec_name,width,height",
               "-of", "json", str(output_path)])
    report = json.loads(raw)
    report["expected_frames"] = sum(lengths)
    report["expected_duration"] = sum(lengths) / fps
    report["shots"] = [{"image": shot["image"], "frames": n} for shot, n in zip(shots, lengths)]
    report_path = output_path.with_suffix(".qa.json")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Rendered: {output_path}")
    print(f"QA: {report_path}")
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_json")
    parser.add_argument("output_mp4")
    a = parser.parse_args()
    render(a.project_json, a.output_mp4)
