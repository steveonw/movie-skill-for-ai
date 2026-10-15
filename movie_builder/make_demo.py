#!/usr/bin/env python3
"""Make five test images, a seven-second WAV, and a demo project spec."""
import json
import math
import struct
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def make_demo(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    names = ["CLASSROOM", "DRAWING ONE FRAME", "14 HOURS LATER", "BANG!", "DEADPAN REACTION"]
    colors = [(25, 42, 70), (38, 75, 80), (10, 10, 10), (130, 46, 31), (52, 45, 76)]
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
    except OSError:
        font = ImageFont.load_default()
    for i, (label, color) in enumerate(zip(names, colors), 1):
        img = Image.new("RGB", (640, 360), color)
        d = ImageDraw.Draw(img)
        d.text((40, 145), label, fill="white", font=font)
        img.save(folder / f"shot_{i}.png")
    sr, secs = 48000, 7
    with wave.open(str(folder / "audio.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        for start in range(0, sr * secs, 4800):
            buf = bytearray()
            for j in range(start, min(start + 4800, sr * secs)):
                t = j / sr
                amp = 0.14 if 0.3 < t < 5.0 else 0.0
                if 4.2 < t < 4.34: amp = 0.44
                value = int(32767 * amp * math.sin(2 * math.pi * 220 * t))
                buf += struct.pack("<h", value)
            w.writeframesraw(buf)
    data = {"fps": 30, "width": 640, "height": 360,
            "audio": "audio.wav",
            "shots": [{"image": f"shot_{i}.png", "duration": 1.4} for i in range(1, 6)]}
    (folder / "project.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(folder / "project.json")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("directory")
    make_demo(p.parse_args().directory)
