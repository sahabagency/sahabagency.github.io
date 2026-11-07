#!/usr/bin/env python3
"""Generate Arabic MP3 lesson narration for the public reading journal.

Run by GitHub Actions. Writes static MP3s to reading/audio, no API secrets.
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path

import edge_tts

ROOT = Path("reading")
OUT = ROOT / "audio"
VOICE = "ar-SA-HamedNeural"
SEMAPHORE = asyncio.Semaphore(2)


def load_lessons():
    html = (ROOT / "index.html").read_text("utf-8")
    found = re.search(
        r'<script type="application/json" id="payload">(.*?)</script>',
        html,
        flags=re.DOTALL,
    )
    if not found:
        raise RuntimeError("Could not find reading journal lesson data")
    return json.loads(found.group(1))["lessons"]


def build_narration(lesson):
    sections = [
        ("الموضوع", lesson["title"]),
        ("المعنى المبسط", lesson["easy"]),
        ("التعريف الدقيق", lesson["definition"]),
        ("التفسير بالتفصيل", lesson["deep"]),
        ("مثال من الواقع", lesson["example"]),
        ("متى تسمع هذا المصطلح", lesson["recognize"]),
        ("ماذا لا يعني هذا المصطلح", lesson["misconception"]),
        ("خطوات التطبيق", " ".join(
            f"الخطوة {n}: {step}" for n, step in enumerate(lesson["steps"], 1)
        )),
        ("تطبيق إضافي", lesson["task"]),
        ("اختبر فهمك", lesson["question"]),
        ("خلاصة الدرس", lesson["takeaway"]),
    ]
    return "\n\n".join(
        f"{title}. {str(content).strip()}"
        for title, content in sections
        if str(content).strip()
    )


async def generate(lesson):
    number = lesson["id"]
    path = OUT / f"lesson-{number:02d}.mp3"
    if path.exists() and path.stat().st_size > 10_000:
        print(f"skip: {path}", flush=True)
        return True
    async with SEMAPHORE:
        for attempt in range(1, 5):
            try:
                audio = edge_tts.Communicate(
                    build_narration(lesson), VOICE, rate="-4%"
                )
                await audio.save(str(path))
                if path.stat().st_size < 10000:
                    raise RuntimeError(f"Audio file too small: {path.stat().st_size}")
                print(f"OK: {path}, {path.stat().st_size} bytes", flush=True)
                return True
            except Exception as exc:
                print(f"ERROR {number}, try {attempt}: {exc}", flush=True)
                if path.exists():
                    path.unlink()
                await asyncio.sleep(min(4 * attempt, 15))
        return False


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    lessons = load_lessons()
    if len(lessons) != 49:
        raise RuntimeError(f"Expected 49 lessons, got {len(lessons)}")
    outcomes = await asyncio.gather(*(generate(t) for t in lessons))
    if not all(outcomes):
        failures = [lessons[i]["id"] for i, ok in enumerate(outcomes) if not ok]
        print(f"FAILED lessons: {failures}", file=sys.stderr)
        raise SystemExit(1)
    print(f"All {len(lessons)} MP3 lessons ready", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
