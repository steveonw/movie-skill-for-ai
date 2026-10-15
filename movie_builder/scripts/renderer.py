#!/usr/bin/env python3
"""Standalone Movie Builder: still images + WAV/MP3 -> validated MP4 and contact sheet."""
import argparse
import json
import math
import subprocess
from pathlib import Path

def run(cmd):
    p = subprocess.run([str(s) for s in cmd], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"Command failed ({p.returncode}): {' '.join(map(str, cmd))}\n{p.stderr[-4000:]}")
    return p.stdout

def probe(path):
    return json.loads(run(["ffprobe", "-v", "error", "-show_entries",
                           "format=duration:stream=codec_type,codec_name,width,height,nb_frames",
                           "-of", "json", path]))

def render(spec_path, output_path):
    from PIL import Image, ImageDraw
    spec_path = Path(spec_path).resolve()
    data = json.loads(spec_path.read_text(encoding="utf-8"))
    fps, width, height = (int(data.get("fps", 30)), int(data.get("width", 640)),
                          int(data.get("height", 360)))
    if not (1 <= fps <= 60 and 64 <= width <= 3840 and 64 <= height <= 2160):
        raise ValueError("Invalid fps or video dimensions")
    shots = data["shots"]
    if not shots or not isinstance(shots, list):
        raise ValueError("At least one shot is required")
    audio = (spec_path.parent / data["audio"]).resolve()
    if not audio.is_file():
        raise FileNotFoundError(audio)
    ainfo = probe(audio)
    streams = ainfo.get("streams", [])
    if not any(x["codec_type"] == "audio" for x in streams):
        raise ValueError("Audio input has no audio stream")
    aduration = float(ainfo["format"]["duration"])
    if not math.isfinite(aduration) or aduration <= 0:
        raise ValueError("Invalid audio duration")
    lengths = []
    images = []
    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for shot in shots:
        path = (spec_path.parent / shot["image"]).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        duration = float(shot["duration"])
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError(f"Invalid shot duration: {duration}")
        frames = round(duration * fps)
        if frames < 1:
            raise ValueError("Shot shorter than one video frame")
        lengths.append(frames)
        images.append(path)
        args += ["-loop", "1", "-framerate", str(fps), "-t", f"{frames/fps:.9f}", "-i", str(path)]
    expected_frames = sum(lengths)
    expected_duration = expected_frames / fps
    if abs(expected_duration - aduration) > 1 / fps + 0.001:
        raise ValueError(f"Audio/shot mismatch: audio={aduration:.3f}s, "
                         f"shots={expected_duration:.3f}s (limit=one video frame)")
    args += ["-i", str(audio)]
    filters = []
    for i in range(len(shots)):
        filters.append(f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
                       f"crop={width}:{height},setsar=1,format=yuv420p[v{i}]")
    filters.append("".join(f"[v{i}]" for i in range(len(shots))) +
                   f"concat=n={len(shots)}:v=1:a=0[v]")
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    args += ["-filter_complex", ";".join(filters), "-map", "[v]",
             "-map", f"{len(shots)}:a:0", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-r", str(fps), "-c:a", "aac", "-ar", "48000",
             "-movflags", "+faststart", "-shortest", str(output_path)]
    run(args)
    info = probe(output_path)
    vstreams = [x for x in info["streams"] if x["codec_type"] == "video"]
    astreams = [x for x in info["streams"] if x["codec_type"] == "audio"]
    if len(vstreams) != 1 or len(astreams) != 1:
        raise RuntimeError("Expected exactly one audio stream and one video stream")
    if vstreams[0]["codec_name"] != "h264" or astreams[0]["codec_name"] != "aac":
        raise RuntimeError("Unexpected output codecs")
    actual_frames = int(vstreams[0].get("nb_frames", 0))
    if actual_frames != expected_frames:
        raise RuntimeError(f"Wrong video frame count: {actual_frames} != {expected_frames}")
    thumb_w, thumb_h, cols = 320, 180, 3
    rows = math.ceil(len(images) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + 25)), (22, 22, 22))
    draw = ImageDraw.Draw(sheet)
    start_frame = 0
    for idx, (image_path, frames) in enumerate(zip(images, lengths)):
        from PIL import ImageOps
        with Image.open(image_path) as pic:
            preview = ImageOps.fit(pic.convert("RGB"), (thumb_w, thumb_h))
        x, y = (idx % cols) * thumb_w, (idx // cols) * (thumb_h + 25)
        sheet.paste(preview, (x, y))
        draw.text((x + 7, y + thumb_h + 5),
                  f"Shot {idx+1}: {start_frame/fps:.2f}-{(start_frame+frames)/fps:.2f}s",
                  fill="white")
        start_frame += frames
    sheet_path = output_path.with_suffix(".contact_sheet.png")
    sheet.save(sheet_path)
    report = {"complete": True, "audio_input_seconds": aduration,
              "expected_duration": expected_duration,
              "actual_duration": float(info["format"]["duration"]),
              "expected_frames": expected_frames, "actual_frames": actual_frames,
              "fps": fps, "width": width, "height": height,
              "codec_video": vstreams[0]["codec_name"],
              "codec_audio": astreams[0]["codec_name"],
              "contact_sheet": str(sheet_path),
              "contact_sheet_warning": "Source-image storyboard, not cut-timing verification",
              "shots": [{"image": shots[i]["image"], "frames": n}
                        for i, n in enumerate(lengths)]}
    report_path = output_path.with_suffix(".qa.json")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Rendered: {output_path}\nContact sheet: {sheet_path}\nQA: {report_path}")
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_json")
    parser.add_argument("output_mp4")
    args = parser.parse_args()
    render(args.project_json, args.output_mp4)
