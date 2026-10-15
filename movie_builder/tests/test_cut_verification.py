"""Regression proof: verify actual encoded frames at cut boundaries."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from movie_builder.verify_cuts import verify


class EncodedCutsTest(unittest.TestCase):
    def test_frame_before_and_after_reveal(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            for i, color in enumerate(((200,35,20),(20,180,50),(35,45,210))):
                Image.new("RGB", (160,90), color).save(root / f"{i}.png")
            spec = {"fps":10,"width":160,"height":90,
                    "shots":[{"image":f"{i}.png","duration":0.5} for i in range(3)]}
            (root / "project.json").write_text(json.dumps(spec))
            cmd = ["ffmpeg","-v","error","-y"]
            for i in range(3):
                cmd += ["-loop","1","-framerate","10","-t","0.5","-i",str(root/f"{i}.png")]
            cmd += ["-filter_complex","[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]",
                    "-map","[v]","-c:v","libx264","-pix_fmt","yuv420p",str(root/"test.mp4")]
            subprocess.run(cmd, check=True, capture_output=True)
            good = verify(root/"project.json",root/"test.mp4")
            self.assertTrue(good["pass"],good)
            self.assertEqual([r["frame"] for r in good["checks"]],[4,5,9,10])
            spec["shots"][1]["image"] = "2.png"
            (root/"wrong.json").write_text(json.dumps(spec))
            bad = verify(root/"wrong.json",root/"test.mp4")
            self.assertFalse(bad["pass"])

if __name__ == "__main__":
    unittest.main()
