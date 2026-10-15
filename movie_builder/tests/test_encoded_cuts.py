"""Decode the FINAL MP4 and verify each cut exactly at its intended frame.

Run: python -m unittest discover -s movie_builder/tests -v
Requires FFmpeg, ffprobe, and Pillow. The colors and audio are generated locally.
"""
import json
import shutil
import subprocess
import tempfile
import unittest
import wave
from pathlib import Path

from PIL import Image
from movie_builder.renderer import render


def decoded_center_pixel(video: Path, frame: int, width=160, height=90):
    """Extract one *encoded video* frame by index, not an input image."""
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video),
        "-vf", f"select=eq(n\\,{frame})",
        "-vsync", "0", "-frames:v", "1", "-pix_fmt", "rgb24",
        "-f", "rawvideo", "pipe:1",
    ]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    expected = width * height * 3
    if len(proc.stdout) != expected:
        raise AssertionError(f"Decoded frame {frame} bytes={len(proc.stdout)}, expected {expected}")
    offset = ((height // 2) * width + width // 2) * 3
    return tuple(proc.stdout[offset:offset+3])


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg required")
class EncodedCutTest(unittest.TestCase):
    def test_color_at_frame_before_and_after_each_cut(self):
        # 4 shots * 15 frames = exactly 60 frames at 30 fps and 2s WAV.
        colors = [(230, 30, 30), (30, 220, 30), (30, 30, 230), (230, 200, 30)]
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            for index, rgb in enumerate(colors):
                Image.new("RGB", (160, 90), rgb).save(folder / f"frame{index}.png")
            with wave.open(str(folder / "voice.wav"), "wb") as audio:
                audio.setnchannels(1)
                audio.setsampwidth(2)
                audio.setframerate(48000)
                audio.writeframes(b"\x00\x00" * (48000 * 2))
            spec = {
                "fps": 30, "width": 160, "height": 90, "audio": "voice.wav",
                "shots": [{"image": f"frame{i}.png", "duration": 0.5}
                          for i in range(len(colors))],
            }
            (folder / "project.json").write_text(json.dumps(spec), encoding="utf-8")
            output = folder / "cut-check.mp4"
            report = render(folder / "project.json", output)
            self.assertEqual(report["actual_frames"], 60)
            # The exact expected frame at a cut is the first frame of the NEW shot.
            for frame in [0, 14, 15, 29, 30, 44, 45, 59]:
                shot_index = frame // 15
                got = decoded_center_pixel(output, frame)
                expected = colors[shot_index]
                with self.subTest(frame=frame, expected_shot=shot_index):
                    self.assertTrue(all(abs(g-e) <= 22 for g,e in zip(got,expected)),
                                    f"Encoded frame {frame} RGB {got} != {expected}")
