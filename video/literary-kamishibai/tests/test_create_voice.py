"""Offline regression checks for the packaged audio input checker."""
import contextlib
import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import wave
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import CreateVoice as cv


class CheckInputTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'input').mkdir()
        (self.root / 'masters').mkdir()
        self.line = dict(line_id='line_001', scene_id='scene_001', type='narration',
                         speaker='Narrator', emotion='normal', text='Hello', reading='Hello',
                         pause_before_sec=0, pause_after_sec=0.5)
        self.save([self.line])
        self.master('character_master.csv',
                    ['character', 'voicevox_character', 'default_speaker_id', 'credit'],
                    ['Narrator', 'Test', 3, 'VOICEVOX:Test'])
        self.master('voice_style_master.csv',
                    ['voicevox_character', 'emotion', 'speaker_id', 'param_policy', 'style_name'],
                    ['Test', 'normal', 3, 'none', 'normal'])
        self.master('emotion_master.csv',
                    ['emotion', 'speed_delta', 'pitch_delta', 'intonation_delta', 'volume_delta', 'pause_length_delta'],
                    ['normal', 0, 0, 0, 0, 0])

    def master(self, name, header, row):
        with (self.root / 'masters' / name).open('w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerow(row)

    def save(self, data):
        (self.root / 'input/dialogue.json').write_text(json.dumps(data), encoding='utf-8-sig')

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def check(self, **kwargs):
        with patch.object(cv, 'request_json', side_effect=AssertionError('network attempted')), \
             patch.object(cv, 'synthesize', side_effect=AssertionError('synthesis attempted')), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            cv.run(self.root, 'http://localhost:1', check_only=True, **kwargs)
        return out.getvalue()

    def test_check_preserves_existing_output(self):
        (self.root / 'output/voice').mkdir(parents=True)
        (self.root / 'output/voice/line_001.wav').write_bytes(b'existing output')
        before = self.snapshot()
        self.assertIn('CHECK OK', self.check(line_ids=['line_001']))
        self.assertEqual(before, self.snapshot())

    def test_check_does_not_create_output(self):
        self.check()
        self.assertFalse((self.root / 'output').exists())

    def test_invalid_inputs_fail_without_output(self):
        for data in [[], {}, [None], [self.line, self.line],
                     [dict(self.line, speaker='missing')],
                     [dict(self.line, reading='')],
                     [dict(self.line, pause_after_sec=-1)],
                     [dict(self.line, pause_before_sec='NaN')],
                     [dict(self.line, line_id='../escape')]]:
            with self.subTest(data=data):
                self.save(data)
                with self.assertRaises(ValueError):
                    self.check()
                self.assertFalse((self.root / 'output').exists())

    def test_missing_selection(self):
        with self.assertRaises(ValueError):
            self.check(line_ids=['unknown'])

    def test_segment_selection(self):
        (self.root / 'input/remotion_segment_assets.json').write_text(
            json.dumps([dict(segment_id='segment_001', dialogue_line_ids=['line_001'])]), encoding='utf-8')
        self.assertIn('CHECK OK', self.check(segment_id='segment_001'))

    def test_normal_generation_still_writes_audio_and_timeline(self):
        def fake_synthesis(text, output, **kwargs):
            with wave.open(str(output), 'wb') as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(24000)
                f.writeframes(b'\x00\x00' * 24000)
        with patch.object(cv, 'request_json', return_value='test'), \
             patch.object(cv, 'synthesize', side_effect=fake_synthesis), \
             contextlib.redirect_stdout(io.StringIO()):
            cv.run(self.root, 'http://localhost:1')
        self.assertEqual(cv.wav_duration(self.root / 'output/voice/line_001.wav'), 1)
        self.assertTrue((self.root / 'output/timeline.csv').exists())
        self.assertTrue((self.root / 'output/credits.txt').exists())

    def test_command_exit_codes(self):
        args = [sys.executable, '-B', str(Path(cv.__file__)), str(self.root), '--check', '--engine-url', 'http://localhost:1']
        result = subprocess.run(args, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.save([dict(self.line, emotion='missing')])
        result = subprocess.run(args, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b'ERROR:', result.stderr)
        self.assertFalse((self.root / 'output').exists())


if __name__ == '__main__':
    unittest.main()
