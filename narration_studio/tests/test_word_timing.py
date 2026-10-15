"""Narration Studio M2: word-level timing and outside-recording alignment (#9).

Fast tests need only numpy. The accuracy and alignment tests need both models:
    NS_TEST_MODEL_DIR=vits-piper-en_US-amy-medium \\
    NS_TEST_ASR_DIR=sherpa-onnx-zipformer-small-en-2023-06-26 \\
    python -m unittest discover -s narration_studio/tests -v
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
sys.path.insert(0, str(HERE.parent / "scripts"))

from ns_audio import read_wav, speech_bounds, write_wav  # noqa: E402
from ns_build import add_word_times, align_recording, build_from_text, import_readaloud, verify  # noqa: E402
from ns_text import compile_pronunciations, parse_story, word_units  # noqa: E402
from ns_words import align_units, energy_envelope, heard_chars, normalize_spoken, number_words, refine_onset  # noqa: E402

FRAME_30 = 1 / 30


class TestWordUnits(unittest.TestCase):
    def test_ids_text_and_spoken(self):
        units = word_units('In 2026, "Bang." Dr. Lee left.', compile_pronunciations({"2026": "twenty twenty-six", "Dr.": "Doctor"}))
        self.assertEqual([u["id"] for u in units], ["w1", "w2", "w3", "w4", "w5", "w6"])
        self.assertEqual([u["text"] for u in units], ["In", "2026", "Bang", "Dr", "Lee", "left"])
        self.assertEqual(units[1]["spoken"], "twenty twenty-six")
        self.assertEqual(units[3]["spoken"], "Doctor")

    def test_phrase_spanning_words_is_spoken_on_first_word(self):
        units = word_units("It ran at 0.000002 FPS today.",
                           compile_pronunciations({"0.000002 FPS": "two millionths of a frame per second", "FPS": "frames per second"}))
        fps = [u for u in units if u["text"] == "FPS"][0]
        self.assertTrue(fps["spoken_with_previous"])
        self.assertEqual(units[3]["spoken"], "two millionths of a frame per second")

    def test_script_json_word_ids_are_kept(self):
        units = word_units("Fourteen hours.", [], ids=["fourteen", "hours"])
        self.assertEqual([u["id"] for u in units], ["fourteen", "hours"])

    def test_segments_carry_words(self):
        seg = [i for i in parse_story("Kevin: Bang.") if i["type"] == "segment"][0]
        self.assertEqual(seg["words"], [{"id": "w1", "text": "Bang", "spoken": "Bang"}])


class TestMatching(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual(number_words("41"), "forty one")
        self.assertEqual(number_words("2026"), "twenty twenty six")
        self.assertEqual(number_words("1,500"), "one thousand five hundred")
        self.assertEqual(number_words("3.5"), "three point five")
        self.assertEqual(normalize_spoken("Took 41 minutes!"), "TOOK FORTY ONE MINUTES")

    def test_fuzzy_alignment_handles_mishearing_and_numbers(self):
        # Recognizer heard "STABLE" for "staple" and "IN TURNS" for "interns".
        toks = [(" THE", 0.0), (" ST", 0.5), ("ABLE", 0.6), (" TOOK", 1.0), (" FOR", 1.3), ("TY", 1.4),
                (" ONE", 1.6), (" IN", 2.0), (" TURNS", 2.2)]
        heard, times = heard_chars(toks)
        units = [{"key": k, "spoken": s} for k, s in
                 [("w1", "The"), ("w2", "staple"), ("w3", "took"), ("w4", "41"), ("w5", "interns")]]
        got = align_units(units, heard, times)
        self.assertEqual(got["w2"][0], 0.5)
        self.assertGreaterEqual(got["w2"][1], 0.8)
        self.assertEqual(got["w4"], (1.3, 1.0))
        self.assertEqual(got["w5"][0], 2.0)

    def test_unmatched_word_has_no_time(self):
        heard, times = heard_chars([(" HELLO", 0.0)])
        got = align_units([{"key": "a", "spoken": "hello"}, {"key": "b", "spoken": "xylophone"}], heard, times)
        self.assertEqual(got["a"][0], 0.0)
        self.assertLess(got["b"][1], 0.5)


class TestOnsetRefinement(unittest.TestCase):
    rate = 16000

    def tone(self, seconds, amp=0.3):
        t = np.arange(int(seconds * self.rate)) / self.rate
        return amp * np.sin(2 * np.pi * 220 * t)

    def test_raw_time_inside_a_pause_snaps_to_end_of_pause(self):
        x = np.concatenate([self.tone(1.0), np.zeros(int(0.8 * self.rate)), self.tone(1.0)])
        env, win = energy_envelope(x, self.rate)
        sec, how = refine_onset(env, win, self.rate, raw=1.1)   # 700 ms early, deep in the pause
        self.assertEqual(how, "end_of_pause")
        self.assertAlmostEqual(sec, 1.8, delta=0.011)

    def test_early_raw_time_moves_to_the_dip_before_the_word(self):
        x = np.concatenate([self.tone(1.0), np.full(int(0.06 * self.rate), 0.0), self.tone(1.0)])
        env, win = energy_envelope(x, self.rate)
        sec, how = refine_onset(env, win, self.rate, raw=0.95)  # 110 ms early
        self.assertAlmostEqual(sec, 1.06, delta=0.011)


class TestGapsKeepOriginalAudio(unittest.TestCase):
    def test_readaloud_import_preserves_gap_audio(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            rate = 16000
            rng = np.random.default_rng(1)
            audio = (rng.normal(0, 30, (rate * 2, 1))).astype(np.int16)   # room tone everywhere
            audio[4000:9000] += 3000
            write_wav(tmp / "ra.wav", audio, rate)
            (tmp / "labels.txt").write_text(f"{4000 / rate:.6f}\t{9000 / rate:.6f}\tLine one.\n")
            import_readaloud(tmp / "ra.wav", tmp / "labels.txt", tmp / "out")
            out, _ = read_wav(tmp / "out" / "narration.wav")
            self.assertTrue(np.array_equal(out, audio))
            self.assertEqual(verify(tmp / "out"), [])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


MODELS = os.environ.get("NS_TEST_MODEL_DIR") and os.environ.get("NS_TEST_ASR_DIR")


@unittest.skipUnless(MODELS, "set NS_TEST_MODEL_DIR and NS_TEST_ASR_DIR to run real-model tests")
class TestRealModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from ns_engines import SherpaVitsEngine
        from ns_words import Recognizer
        cls.tts = SherpaVitsEngine(os.environ["NS_TEST_MODEL_DIR"])
        cls.rec = Recognizer(os.environ["NS_TEST_ASR_DIR"])
        cls.tmp = Path(tempfile.mkdtemp(prefix="ns_m2_"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_known_onsets_never_more_than_a_frame_early(self):
        """Two separately spoken pieces joined with a pause: the 2nd piece's onset is known exactly."""
        from ns_words import time_words
        pairs = [("The first frame took", "fourteen hours."), ("The sound guy said", "bang."),
                 ("Kevin opened the", "door, slowly."), ("Nobody expected the", "chalkboard to win."),
                 ("The video got", "twelve views."), ("Marcus refused to", "draw stairs.")]
        sr = self.tts.sample_rate
        errors = []
        for a, b in pairs:
            for gap in (0.0, 0.25, 0.75):
                A, _ = self.tts.synthesize(a, {})
                B, _ = self.tts.synthesize(b, {})
                pcm = np.concatenate([A, np.zeros((int(gap * sr), 1), np.int16), B])
                truth = len(A) + int(gap * sr) + speech_bounds(B, sr)[0]
                units = [{"key": w["id"], "spoken": w["spoken"]} for w in word_units(f"{a} {b}", [])]
                got, _ = time_words(pcm, sr, units, self.rec)
                start = got[f"w{len(a.split()) + 1}"]["start_sample"]
                self.assertIsNotNone(start, f"{b!r} not matched")
                errors.append((start - truth) / sr)
        errors = np.array(errors)
        self.assertEqual(int(np.sum(errors < -FRAME_30)), 0, f"early by >1 frame: {errors}")
        self.assertLess(abs(errors.mean()), 0.015)

    def _narrate(self, text):
        story = self.tmp / "story.md"
        story.write_text(text, encoding="utf-8")
        factory = lambda d=None: self.tts  # noqa: E731
        out = self.tmp / "gen"
        build_from_text(story, out, factory, {})
        return story, out

    def test_words_command_fills_word_times(self):
        story, out = self._narrate("The first frame took 14 hours.\n\nThe sound guy said bang.\n")
        side, found = add_word_times(out, self.rec, find=["bang", "14"])
        self.assertEqual(verify(out), [])
        self.assertEqual(set(found), {"bang", "14"})
        bang = found["bang"][0]
        seg = [s for s in side["segments"] if s["id"] == bang["segment"]][0]
        self.assertTrue(seg["speech_start_sample"] < bang["start_sample"] < seg["speech_end_sample"])
        self.assertGreater(bang["confidence"], 0.7)
        self.assertEqual(side["word_timing"]["segments"], ["s001", "s002"])

    def test_align_outside_recording(self):
        text = ("The first frame took fourteen hours.\n\nKevin: This is fine.\n\n"
                "The sound guy said bang.\n\nNobody expected the chalkboard to win.\n")
        story, gen = self._narrate(text)
        truth = {s["id"]: s for s in json.loads((gen / "narration.json").read_text())["segments"]}
        mp3 = self.tmp / "recording.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(gen / "narration.wav"), "-c:a", "libmp3lame",
                        "-b:a", "128k", str(mp3)], check=True)
        side = align_recording(mp3, story, self.tmp / "al", self.rec)
        self.assertEqual(verify(self.tmp / "al"), [])
        self.assertEqual(side["warnings"], [])
        rate = side["audio"]["sample_rate"]
        for seg in side["segments"]:
            err = (seg["start_sample"] - truth[seg["id"]]["speech_start_sample"]) / rate
            self.assertLess(abs(err), FRAME_30, f"{seg['id']} off by {err * 1000:.0f} ms")
        # The script changes: one line rewritten, one never recorded.
        changed = self.tmp / "changed.md"
        changed.write_text(text.replace("This is fine.", "I would like to speak to the manager immediately please.")
                           + "\nMarcus: This line was never recorded.\n", encoding="utf-8")
        side = align_recording(mp3, changed, self.tmp / "al2", self.rec)
        warnings = " ".join(side["warnings"])
        self.assertIn("never recorded", warnings)
        self.assertTrue("only partly matches" in warnings or "not found" in warnings, warnings)


if __name__ == "__main__":
    unittest.main()
