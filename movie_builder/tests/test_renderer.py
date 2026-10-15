"""Regression checks for standalone Movie Builder. Run: python -m unittest discover -s movie_builder/tests -v"""
import json
import tempfile
import unittest
from pathlib import Path

from movie_builder.make_demo import make_demo
from movie_builder.renderer import render

class MovieBuilderTest(unittest.TestCase):
    def test_demo_render_and_duration_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            make_demo(folder)
            output = folder / "result.mp4"
            report = render(folder / "project.json", output)
            self.assertTrue(output.is_file())
            self.assertTrue(output.with_suffix(".contact_sheet.png").is_file())
            self.assertEqual(report["expected_frames"], 210)
            self.assertEqual(report["actual_frames"], 210)
            self.assertEqual(report["codec_video"], "h264")
            self.assertEqual(report["codec_audio"], "aac")
            self.assertAlmostEqual(report["actual_duration"], 7.0, places=1)
            self.assertTrue(report["complete"])
            spec = json.loads((folder / "project.json").read_text())
            spec["shots"] = spec["shots"][:1]
            (folder / "invalid.json").write_text(json.dumps(spec))
            with self.assertRaisesRegex(ValueError, "Audio/shot mismatch"):
                render(folder / "invalid.json", folder / "should-not-exist.mp4")
            self.assertFalse((folder / "should-not-exist.mp4").exists())

if __name__ == "__main__":
    unittest.main()
