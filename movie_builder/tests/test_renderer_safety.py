"""Audio preservation and absolute-frame planning regressions for Movie Builder."""
import json
import math
import shutil
import struct
import subprocess
import tempfile
import unittest
import wave
from pathlib import Path

from PIL import Image
from movie_builder.renderer import plan_frames, render
from movie_builder.verify_cuts import verify


def audio_wav(path, seconds):
    sr = 48000
    with wave.open(str(path), 'wb') as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sr)
        # Last 0.12 s contains an audible tone, suitable for checking truncation.
        audio.writeframes(b''.join(struct.pack('<h', int(8500 * math.sin(i * 2*math.pi*440/sr))
                                              if i / sr > seconds - 0.12 else 0)
                                   for i in range(round(seconds * sr))))


def make_spec(path, seconds, exact=False):
    root = path.parent
    Image.new('RGB', (160, 90), (155, 20, 20)).save(root / 'a.png')
    Image.new('RGB', (160, 90), (20, 155, 20)).save(root / 'b.png')
    audio_wav(root / 'voice.wav', seconds)
    shots = ([{'image':'a.png','end_frame':15},{'image':'b.png','end_frame':30}]
             if exact else [{'image':'a.png','duration':0.5},{'image':'b.png','duration':0.5}])
    path.write_text(json.dumps({'audio':'voice.wav','width':160,'height':90,
                                'fps':30,'shots':shots}))
    return path


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg required')
class FrameSafeMovieBuilder(unittest.TestCase):
    def test_short_audio_does_not_chop_last_video_frame(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_spec(Path(tmp) / 'project.json', 0.98)
            output = Path(tmp) / 'out.mp4'
            report = render(project, output)
            self.assertEqual((report['expected_frames'], report['actual_frames']), (30, 30))
            self.assertEqual(report['final_shot_extended_frames'], 0)
            self.assertTrue(verify(project, output)['pass'])

    def test_audio_slightly_longer_extends_final_still(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_spec(Path(tmp) / 'project.json', 1.02)
            output = Path(tmp) / 'out.mp4'
            report = render(project, output)
            self.assertEqual((report['planned_frames'], report['actual_frames']), (30, 31))
            self.assertEqual(report['final_shot_extended_frames'], 1)
            self.assertGreaterEqual(report['output_audio_seconds'], 1.017)
            data = subprocess.run(['ffmpeg','-v','error','-i',str(output),'-ar','16000',
                                   '-ac','1','-f','s16le','-'], check=True, capture_output=True).stdout
            # Decoded signal near 1.0 s must remain audible after muxing.
            samples = struct.unpack('<' + 'h' * (len(data) // 2), data)
            self.assertGreater(max(abs(x) for x in samples[int(0.95*16000):int(1.01*16000)]), 700)

    def test_mp3_padding_does_not_falsely_reject_timeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_spec(Path(tmp) / 'project.json', 1.02)
            root = Path(tmp)
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(root/'voice.wav'),
                            '-c:a','libmp3lame',str(root/'voice.mp3')],check=True,capture_output=True)
            plan = json.loads(project.read_text())
            plan['audio'] = 'voice.mp3'
            project.write_text(json.dumps(plan))
            output = root / 'mp3.mp4'
            report = render(project, output)
            self.assertGreater(report['container_audio_seconds'], 1.04)
            self.assertAlmostEqual(report['input_audio_seconds'], 1.02, places=3)
            self.assertEqual(report['actual_frames'], 31)

    def test_absolute_end_frame_contract(self):
        self.assertEqual(plan_frames([{'end_frame':7},{'end_frame':15},{'end_frame':30}],30), [7,8,15])
        with tempfile.TemporaryDirectory() as tmp:
            project = make_spec(Path(tmp) / 'project.json', 1.0, exact=True)
            output = Path(tmp) / 'out.mp4'
            report = render(project, output)
            self.assertEqual(report['actual_frames'], 30)
            self.assertTrue(verify(project, output)['pass'])

    def test_cumulative_shot_rounding_and_invalid_inputs(self):
        lengths = plan_frames([{'duration':0.11}]*20, 10)
        self.assertEqual(sum(lengths), 22)
        self.assertEqual(lengths.count(2), 2)
        with self.assertRaisesRegex(ValueError,'Use end_frame'):
            plan_frames([{'duration':1},{'end_frame':12}],30)
        with self.assertRaisesRegex(ValueError,'shorter than one'):
            plan_frames([{'end_frame':3},{'end_frame':3}],30)
        with self.assertRaises(ValueError):
            plan_frames([{'duration':float('nan')}],30)
        with self.assertRaises(ValueError):
            plan_frames([{'end_frame':True}],30)

    def test_excessive_duration_mismatch_rejected_before_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_spec(Path(tmp) / 'project.json', 0.7)
            output = Path(tmp) / 'out.mp4'
            with self.assertRaisesRegex(ValueError,'Audio/shot mismatch'):
                render(project, output)
            self.assertFalse(output.exists())

if __name__=='__main__':
    unittest.main()
