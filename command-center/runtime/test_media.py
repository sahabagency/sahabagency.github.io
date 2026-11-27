"""Offline smoke test: python -m unittest runtime.test_media."""
import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from .media import render

class MediaTests(unittest.TestCase):
    def test_invalid_input(self):
        with tempfile.TemporaryDirectory() as folder:
            for title, slides, secs in [("", ["x"], 5), ("x", [], 5), ("x", ["x"], 0)]:
                with self.assertRaises(ValueError):
                    render(folder, title, slides, secs)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "requires FFmpeg")
    def test_arabic_video_and_carousel(self):
        with tempfile.TemporaryDirectory() as folder:
            result = render(folder, "اختبار مصنع المحتوى", ["فهم الجمهور أولاً", "اختبر الفكرة", "قِس النتائج"], 3)
            root = Path(folder) / result["id"]
            video = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                "stream=codec_name,width,height:format=duration", "-of", "json", str(root / "video.mp4")]))
            self.assertEqual(video["streams"][0]["codec_name"], "h264")
            self.assertEqual((video["streams"][0]["width"], video["streams"][0]["height"]), (720, 1280))
            self.assertAlmostEqual(float(video["format"]["duration"]), 9, places=1)
            with zipfile.ZipFile(root / "carousel.zip") as archive:
                self.assertEqual(len(archive.namelist()), 3)
                self.assertIsNone(archive.testzip())

if __name__ == "__main__":
    unittest.main()
