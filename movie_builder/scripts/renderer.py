#!/usr/bin/env python3
"""Standalone still-image + WAV/MP3 -> frame-checked H.264/AAC MP4 and contact sheet.

Only a simple project JSON is required. No other filmmaking Skill is imported.
"""
import argparse
import json
import math
import subprocess
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


def run(cmd):
    completed = subprocess.run([str(part) for part in cmd], capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError(f"Command failed ({completed.returncode}): {' '.join(map(str, cmd))}\n"
                           + completed.stderr[-4000:])
    return completed.stdout


def probe(path):
    return json.loads(run(["ffprobe", "-v", "error", "-show_entries",
                           "format=duration:stream=codec_type,codec_name,width,height,nb_frames,duration,sample_rate",
                           "-of", "json", path]))


def effective_audio_seconds(path, info):
    """Use decoded samples, not MP3 container duration (which includes encoder padding)."""
    audio_streams = [stream for stream in info.get("streams", [])
                     if stream.get("codec_type") == "audio"]
    if not audio_streams:
        raise ValueError("Input contains no audio stream")
    sample_rate = int(audio_streams[0].get("sample_rate", 0))
    if sample_rate:
        raw = run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_frames",
                   "-show_entries", "frame=nb_samples", "-of", "csv=p=0", path])
        total_samples = sum(int(value) for value in raw.splitlines()
                            if value.strip().isdigit())
        if total_samples > 0:
            return total_samples / sample_rate
    # Codec/container without decoded sample counts: this is an estimate.
    return float(info["format"]["duration"])


def plan_frames(shots, fps):
    """Return per-shot frame counts from cumulative times or exact end_frame indices.

    end_frame is absolute, exclusive and 0-based. Duration mode rounds cumulative
    absolute boundaries, never each individual duration (avoids cumulative drift).
    """
    if not isinstance(shots, list) or not shots or len(shots) > 120:
        raise ValueError("Provide between 1 and 120 shots")
    use_frames = ["end_frame" in shot for shot in shots]
    if any(use_frames) and not all(use_frames):
        raise ValueError("Use end_frame for every shot, or duration for every shot")
    if all(use_frames):
        boundaries = []
        for shot in shots:
            if "duration" in shot:
                raise ValueError("Do not mix duration with end_frame")
            end = shot["end_frame"]
            if type(end) is not int or end < 1:
                raise ValueError("end_frame must be a positive integer")
            boundaries.append(end)
    else:
        boundaries = []
        cumulative = Decimal(0)
        for shot in shots:
            try:
                duration = shot["duration"]
                if isinstance(duration, bool):
                    raise ValueError("Invalid duration")
                value = Decimal(str(duration))
            except (KeyError, InvalidOperation, TypeError) as exc:
                raise ValueError("Each shot needs a finite positive duration") from exc
            if not value.is_finite() or value <= 0:
                raise ValueError("Each shot needs a finite positive duration")
            cumulative += value
            boundaries.append(int((cumulative * fps).to_integral_value(rounding=ROUND_HALF_UP)))
    result, previous = [], 0
    for end in boundaries:
        if end <= previous:
            raise ValueError("A shot is shorter than one video frame")
        result.append(end - previous)
        previous = end
    return result


def render(spec_path, output_path):
    from PIL import Image, ImageDraw, ImageOps

    spec_path, output_path = Path(spec_path).resolve(), Path(output_path).resolve()
    data = json.loads(spec_path.read_text(encoding="utf-8"))
    fps = int(data.get("fps", 30))
    width, height = int(data.get("width", 640)), int(data.get("height", 360))
    if not (1 <= fps <= 60 and 64 <= width <= 3840 and 64 <= height <= 2160):
        raise ValueError("Invalid output profile")
    if width % 2 or height % 2:
        raise ValueError("H.264 yuv420p requires even width and height")
    shots = data.get("shots", [])
    frames = plan_frames(shots, fps)
    audio = (spec_path.parent / data["audio"]).resolve()
    if not audio.is_file():
        raise FileNotFoundError(audio)
    audio_info = probe(audio)
    audio_duration = effective_audio_seconds(audio, audio_info)
    if not math.isfinite(audio_duration) or audio_duration <= 0:
        raise ValueError("Invalid audio duration")

    planned_frames = sum(frames)
    planned_seconds = planned_frames / fps
    if abs(planned_seconds - audio_duration) > 1 / fps + 0.001:
        raise ValueError(f"Audio/shot mismatch: audio={audio_duration:.3f}s, "
                         f"shots={planned_seconds:.3f}s (tolerance one video frame)")
    # Preserve the entire audio even when it exceeds the planned timeline by a
    # fraction of one frame. Extend the final still, rather than trim narration.
    min_audio_frames = math.ceil(audio_duration * fps - 1e-6)
    extra_frames = max(0, min_audio_frames - planned_frames)
    frames[-1] += extra_frames
    total_frames = sum(frames)
    render_seconds = total_frames / fps
    images = []
    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for shot, count in zip(shots, frames):
        image = (spec_path.parent / shot["image"]).resolve()
        if not image.is_file():
            raise FileNotFoundError(image)
        images.append(image)
        args += ["-loop", "1", "-framerate", str(fps), "-t", f"{count / fps:.9f}",
                 "-i", str(image)]
    args += ["-i", str(audio)]
    filters = []
    for i, count in enumerate(frames):
        filters.append(f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
                       f"crop={width}:{height},setsar=1,format=yuv420p,"
                       f"trim=end_frame={count},setpts=PTS-STARTPTS[v{i}]")
    filters.append("".join(f"[v{i}]" for i in range(len(frames))) +
                   f"concat=n={len(frames)}:v=1:a=0[v]")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Pad short audio and trim that pad to the exact visual duration. Avoid
    # -shortest: it can drop the final AAC packet even when timelines match.
    args += ["-filter_complex", ";".join(filters), "-map", "[v]",
             "-map", f"{len(frames)}:a:0", "-af", f"apad,atrim=duration={render_seconds:.9f}", "-c:v", "libx264",
             "-pix_fmt", "yuv420p", "-r", str(fps), "-c:a", "aac", "-ar", "48000",
             "-movflags", "+faststart", str(output_path)]
    run(args)
    info = probe(output_path)
    video = [s for s in info["streams"] if s["codec_type"] == "video"]
    sound = [s for s in info["streams"] if s["codec_type"] == "audio"]
    if len(video) != 1 or len(sound) != 1:
        raise RuntimeError("Expected exactly one audio stream and one video stream")
    if video[0]["codec_name"] != "h264" or sound[0]["codec_name"] != "aac":
        raise RuntimeError("Unexpected output codecs")
    actual_frames = int(video[0].get("nb_frames", 0))
    if actual_frames != total_frames:
        raise RuntimeError(f"Wrong video frame count: {actual_frames} != {total_frames}")
    output_audio_duration = float(sound[0].get("duration", info["format"]["duration"]))
    if output_audio_duration + 0.003 < audio_duration:
        raise RuntimeError(f"Output audio may be truncated: {output_audio_duration} < {audio_duration}")

    thumb_w, thumb_h, columns = 320, 180, 3
    sheet = Image.new("RGB", (columns * thumb_w,
                              math.ceil(len(images) / columns) * (thumb_h + 25)), (22, 22, 22))
    draw = ImageDraw.Draw(sheet)
    start = 0
    for i, (image, count) in enumerate(zip(images, frames)):
        with Image.open(image) as original:
            thumbnail = ImageOps.fit(original.convert("RGB"), (thumb_w, thumb_h))
        x, y = (i % columns) * thumb_w, (i // columns) * (thumb_h + 25)
        sheet.paste(thumbnail, (x, y))
        draw.text((x + 7, y + thumb_h + 5),
                  f"Shot {i+1}: {start/fps:.2f}-{(start+count)/fps:.2f}s", fill="white")
        start += count
    sheet_path = output_path.with_suffix(".contact_sheet.png")
    sheet.save(sheet_path)
    report = {"complete": True, "fps": fps, "width": width, "height": height,
              "expected_frames": total_frames, "actual_frames": actual_frames,
              "planned_frames": planned_frames, "final_shot_extended_frames": extra_frames,
              "input_audio_seconds": audio_duration,
              "container_audio_seconds": float(audio_info["format"]["duration"]),
              "output_audio_seconds": output_audio_duration,
              "expected_duration": render_seconds,
              "actual_duration": float(info["format"]["duration"]),
              "codec_video": video[0]["codec_name"], "codec_audio": sound[0]["codec_name"],
              "contact_sheet": str(sheet_path),
              "contact_sheet_warning": "Source-image preview, not encoded-cut verification",
              "shots": [{"image": shot["image"], "frames": count}
                        for shot, count in zip(shots, frames)]}
    output_path.with_suffix(".qa.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Rendered: {output_path}\nContact sheet: {sheet_path}\nQA: {output_path.with_suffix('.qa.json')}")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_json")
    parser.add_argument("output_mp4")
    args = parser.parse_args()
    render(args.project_json, args.output_mp4)
