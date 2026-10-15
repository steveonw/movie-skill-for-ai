"""Narration Studio M1 acceptance tests.

Run from the repository root:
    python -m unittest discover -s narration_studio/tests -v

Optional real-voice test: set NS_TEST_MODEL_DIR to a Piper/VITS voice folder
(e.g. vits-piper-en_US-amy-medium) with sherpa-onnx installed.
Optional Movie Builder integration test needs FFmpeg + Pillow.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent / "scripts"))

from ns_audio import read_wav, speech_bounds, write_wav  # noqa: E402
from ns_build import build_from_clips, build_from_text, import_readaloud, verify  # noqa: E402
from ns_engines import ToneEngine, make_engine  # noqa: E402
from ns_text import parse_story, split_sentences  # noqa: E402

STORY = """# Test Title

The first frame took fourteen hours. The second frame took fourteen more.

Kevin: This is fine.

[pause 1.5s]

The end.
"""


def tone_factory(model_dir=None):
    return ToneEngine(22050)


class TempDir(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ns_test_"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def story(self, text=STORY, name="story.md"):
        p = self.tmp / name
        p.write_text(text, encoding="utf-8")
        return p


class TestText(unittest.TestCase):
    def test_parse_story_structure(self):
        items = parse_story(STORY, {"fourteen": "14"})
        segs = [i for i in items if i["type"] == "segment"]
        self.assertEqual([s["id"] for s in segs], ["s001", "s002", "s003", "s004", "s005"])
        self.assertEqual(segs[0]["kind"], "heading")
        self.assertEqual(segs[3]["speaker"], "Kevin")
        self.assertEqual(segs[3]["display_text"], "This is fine.")
        pauses = [i for i in items if i["type"] == "pause"]
        self.assertEqual(pauses, [{"type": "pause", "kind": "pause", "seconds": 1.5}])

    def test_display_and_spoken_text_stay_separate(self):
        segs = [i for i in parse_story("Use **2026** now.", {"2026": "twenty twenty-six"})
                if i["type"] == "segment"]
        self.assertEqual(segs[0]["source_text"], "Use **2026** now.")
        self.assertEqual(segs[0]["display_text"], "Use 2026 now.")
        self.assertEqual(segs[0]["spoken_text"], "Use twenty twenty-six now.")
        self.assertEqual(segs[0]["substitutions"], [{"from": "2026", "to": "twenty twenty-six", "count": 1}])

    def test_sentence_split_respects_abbreviations(self):
        text = "Dr. Smith arrived. It was 3 p.m. today? Yes!"
        spans = [text[a:b] for a, b in split_sentences(text)]
        self.assertEqual(spans[0], "Dr. Smith arrived.")
        self.assertEqual(spans[-1], "Yes!")


class TestClipAssembly(TempDir):
    """ROADMAP Phase 2: supplied clips + sample-exact inserted pauses."""

    def test_exact_sample_positions(self):
        rate = 16000
        lengths = [1000, 2500, 777]
        for i, n in enumerate(lengths):
            write_wav(self.tmp / f"c{i}.wav", np.full((n, 1), 1000 * (i + 1), np.int16), rate)
        manifest = {"items": [{"id": "a", "clip": "c0.wav", "text": "One."},
                              {"pause": 0.5},
                              {"id": "b", "clip": "c1.wav", "text": "Two."},
                              {"id": "c", "clip": "c2.wav", "text": "Three."}],
                    "lead_in": 0.25, "tail": 0.125}
        (self.tmp / "clips.json").write_text(json.dumps(manifest))
        side = build_from_clips(self.tmp / "clips.json", self.tmp / "out")
        segs = {s["id"]: s for s in side["segments"]}
        self.assertEqual((segs["a"]["start_sample"], segs["a"]["end_sample"]), (4000, 5000))
        self.assertEqual((segs["b"]["start_sample"], segs["b"]["end_sample"]), (13000, 15500))
        self.assertEqual((segs["c"]["start_sample"], segs["c"]["end_sample"]), (15500, 16277))
        self.assertEqual(side["audio"]["total_samples"], 4000 + 1000 + 8000 + 2500 + 777 + 2000)
        self.assertEqual([g["frames"] for g in side["silences"]], [4000, 8000, 2000])
        data, r = read_wav(self.tmp / "out" / "narration.wav")
        self.assertEqual(data.shape[0], side["audio"]["total_samples"])
        self.assertTrue(np.all(data[5000:13000] == 0))
        self.assertTrue(np.all(data[13000:15500] == 2000))
        self.assertEqual(verify(self.tmp / "out"), [])

    def test_verify_catches_tampering(self):
        write_wav(self.tmp / "c.wav", np.full((500, 1), 5, np.int16), 8000)
        (self.tmp / "m.json").write_text(json.dumps({"items": [{"clip": "c.wav"}, {"pause": 0.1}, {"clip": "c.wav"}]}))
        build_from_clips(self.tmp / "m.json", self.tmp / "out")
        data, r = read_wav(self.tmp / "out" / "narration.wav")
        data[600] = 99  # noise inside the inserted silence
        write_wav(self.tmp / "out" / "narration.wav", data, r)
        problems = verify(self.tmp / "out")
        self.assertTrue(any("checksum" in p for p in problems))
        self.assertTrue(any("non-zero" in p for p in problems))


class TestGeneratedNarration(TempDir):
    def test_build_tiles_audio_and_gaps(self):
        side = build_from_text(self.story(), self.tmp / "out", tone_factory,
                               {"pauses": {"tail": 0.5, "sentence": 0.3}})
        self.assertEqual(verify(self.tmp / "out"), [])
        reasons = [g["reason"] for g in side["silences"]]
        self.assertEqual(reasons, ["heading", "sentence", "paragraph", "explicit_pause", "tail"])
        explicit = side["silences"][3]
        self.assertEqual(explicit["frames"], round(1.5 * 22050))
        sentence = side["silences"][1]
        self.assertEqual(sentence["frames"], round(0.3 * 22050))
        for name in ("narration.wav", "narration.json", "narration.srt", "narration-labels.txt"):
            self.assertTrue((self.tmp / "out" / name).is_file(), name)

    def test_change_one_line_resynthesizes_only_that_line(self):
        cache = self.tmp / "cache"
        first = build_from_text(self.story(), self.tmp / "out", tone_factory, {}, cache)
        self.assertEqual(first["build"]["cache"]["misses"], 5)
        edited = STORY.replace("This is fine.", "This is not fine.")
        second = build_from_text(self.story(edited), self.tmp / "out", tone_factory, {}, cache)
        c = second["build"]["cache"]
        self.assertEqual((c["misses"], c["hits"]), (1, 4))
        self.assertEqual(c["synthesized"], ["s004"])
        # Unchanged lines reuse byte-identical audio.
        a = {s["id"]: s["cache"]["key"] for s in first["segments"]}
        b = {s["id"]: s["cache"]["key"] for s in second["segments"]}
        self.assertEqual({k for k in a if a[k] != b[k]}, {"s004"})

    def test_pronunciation_change_invalidates_only_affected_line(self):
        cache = self.tmp / "cache"
        build_from_text(self.story(), self.tmp / "out", tone_factory, {}, cache)
        side = build_from_text(self.story(), self.tmp / "out", tone_factory,
                               {"pronunciations": {"Kevin": "Kev"}, "detect_speakers": True}, cache)
        # "Kevin:" is a speaker tag, not spoken text, so nothing is resynthesized.
        self.assertEqual(side["build"]["cache"]["misses"], 0)
        side = build_from_text(self.story(), self.tmp / "out", tone_factory,
                               {"pronunciations": {"frame": "frayme"}}, cache)
        self.assertEqual(side["build"]["cache"]["synthesized"], ["s002", "s003"])

    def test_damaged_cache_entry_is_regenerated(self):
        cache = self.tmp / "cache"
        build_from_text(self.story(), self.tmp / "out", tone_factory, {}, cache)
        victim = sorted(cache.rglob("*.wav"))[0]
        victim.write_bytes(victim.read_bytes()[:-100])
        side = build_from_text(self.story(), self.tmp / "out", tone_factory, {}, cache)
        c = side["build"]["cache"]
        self.assertEqual((c["misses"], len(c["rejected_entries"])), (1, 1))
        self.assertEqual(verify(self.tmp / "out"), [])

    def test_speech_bounds_find_padding(self):
        samples, rate = ToneEngine().synthesize("hello there", {})
        start, end = speech_bounds(samples, rate)
        self.assertAlmostEqual(start / rate, ToneEngine.LEAD, delta=0.0101)
        self.assertAlmostEqual((len(samples) - end) / rate, ToneEngine.TAIL, delta=0.0101)

    def test_unknown_speaker_falls_back_with_warning(self):
        side = build_from_text(self.story(), self.tmp / "out", tone_factory,
                               {"cast": {"narrator": {"sid": 0}}})
        self.assertTrue(any("Kevin" in w for w in side["warnings"]))
        kevin = [s for s in side["segments"] if s["speaker"] == "Kevin"][0]
        self.assertEqual(kevin["voice"]["sid"], 0)


class TestReadAloudImport(TempDir):
    def test_round_trip_is_sample_exact(self):
        side = build_from_text(self.story(), self.tmp / "gen", tone_factory, {})
        imported = import_readaloud(self.tmp / "gen" / "narration.wav",
                                    self.tmp / "gen" / "narration-labels.txt", self.tmp / "imp")
        self.assertEqual(verify(self.tmp / "imp"), [])
        orig = [(s["start_sample"], s["end_sample"], s["display_text"]) for s in side["segments"]]
        got = [(s["start_sample"], s["end_sample"], s["display_text"]) for s in imported["segments"]]
        self.assertEqual(orig, got)
        self.assertEqual(imported["audio"]["total_samples"], side["audio"]["total_samples"])
        self.assertIsNone(imported["segments"][0]["spoken_text"])

    def test_readaloud_label_format(self):
        """Labels written the way Read-Aloud-Main writes them: 6-decimal seconds."""
        rate = 22050
        write_wav(self.tmp / "ra.wav", np.zeros((rate * 2, 1), np.int16), rate)
        labels = [(0, 9001), (16718, 30000)]
        (self.tmp / "ra.txt").write_text("".join(
            f"{a / rate:.6f}\t{b / rate:.6f}\tLine {i}\n" for i, (a, b) in enumerate(labels)))
        side = import_readaloud(self.tmp / "ra.wav", self.tmp / "ra.txt", self.tmp / "out")
        self.assertEqual([(s["start_sample"], s["end_sample"]) for s in side["segments"]], labels)


@unittest.skipUnless(os.environ.get("NS_TEST_MODEL_DIR"), "set NS_TEST_MODEL_DIR to run the real-voice test")
class TestRealVoice(TempDir):
    def test_sherpa_build(self):
        model = os.environ["NS_TEST_MODEL_DIR"]
        side = build_from_text(self.story(), self.tmp / "out", lambda d=None: make_engine("sherpa", model), {})
        self.assertEqual(verify(self.tmp / "out"), [])
        self.assertEqual(side["build"]["engine"]["engine"], "sherpa-onnx-vits")
        for seg in side["segments"]:
            self.assertIsNotNone(seg["speech_start_sample"], seg["id"])
        # Rebuild: VITS output is random, so identical timing proves the cache was used.
        again = build_from_text(self.story(), self.tmp / "out", lambda d=None: make_engine("sherpa", model), {})
        self.assertEqual(again["audio"]["sha256"], side["audio"]["sha256"])


def _have(*tools):
    return all(shutil.which(t) for t in tools)


@unittest.skipUnless(_have("ffmpeg", "ffprobe"), "needs FFmpeg")
class TestMovieBuilderIntegration(TempDir):
    """narration.json -> Movie Builder project.json, cutting on measured speech starts."""

    def test_render_with_sidecar_timing(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("needs Pillow")
        side = build_from_text(self.story(), self.tmp / "n", tone_factory, {})
        rate, fps = side["audio"]["sample_rate"], 30
        total = side["audio"]["total_samples"]
        # One shot per segment, cut at its speech start rounded UP to the next
        # frame (ARCHITECTURE invariant 4). Cumulative frame boundaries, not
        # per-shot rounding, so error cannot accumulate.
        cuts = [0] + [-(-s["speech_start_sample"] * fps // rate) for s in side["segments"][1:]]
        # Last whole frame inside the audio (the tail is silence), so the video
        # never outlasts the audio; renderers using -shortest then keep every frame.
        end_frame = total * fps // rate
        shots = []
        for i, a in enumerate(cuts):
            b = cuts[i + 1] if i + 1 < len(cuts) else end_frame
            img = self.tmp / f"img{i}.png"
            Image.new("RGB", (64, 36), (40 * i, 80, 160)).save(img)
            shots.append({"image": img.name, "duration": (b - a) / fps})
        shutil.copy(self.tmp / "n" / "narration.wav", self.tmp / "narration.wav")
        (self.tmp / "project.json").write_text(json.dumps(
            {"audio": "narration.wav", "fps": fps, "width": 320, "height": 180, "shots": shots}))
        out = self.tmp / "out.mp4"
        subprocess.run([sys.executable, str(ROOT / "movie_builder" / "renderer.py"),
                        str(self.tmp / "project.json"), str(out)], check=True, capture_output=True)
        qa = json.loads(out.with_suffix(".qa.json").read_text())
        self.assertEqual(qa["expected_frames"], end_frame)
        self.assertEqual([s["frames"] for s in qa["shots"]],
                         [b - a for a, b in zip(cuts, cuts[1:] + [end_frame])])
        # Measure the MP4 directly so the test doesn't depend on the QA report layout.
        probe = json.loads(subprocess.run(
            ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
             "-show_entries", "stream=nb_read_frames:format=duration", "-of", "json", str(out)],
            check=True, capture_output=True, text=True).stdout)
        self.assertEqual(int(probe["streams"][0]["nb_read_frames"]), end_frame)
        self.assertAlmostEqual(float(probe["format"]["duration"]), total / rate, delta=2 / fps)


if __name__ == "__main__":
    unittest.main()
