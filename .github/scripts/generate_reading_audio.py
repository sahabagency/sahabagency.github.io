#!/usr/bin/env python3
"""Narrated Arabic lesson MP3s with educator-style timing, for GitHub Pages.

Free generation uses Microsoft Edge's neural speech service (via edge-tts).
Render five natural teaching sections separately and insert measured silences
with ffmpeg/pydub. Output is a normal audio file played by the browser, not TTS.
"""
from __future__ import annotations

import asyncio
import hashlib
import io
import json
import re
import sys
from pathlib import Path

import edge_tts
from pydub import AudioSegment

ROOT = Path("reading")
OUT = ROOT / "audio"
MANIFEST = OUT / "manifest.json"
VOICE = "ar-SA-HamedNeural"
RATE = "-9%"
LIMIT = asyncio.Semaphore(2)
OPENING = 650
BETWEEN = 850
LONG_PAUSE = 1500
THINKING_PAUSE = 2300


def lessons_from_html():
    html = (ROOT / "index.html").read_text("utf-8")
    m = re.search(
        r'<script type="application/json" id="payload">(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not m:
        raise RuntimeError("Missing lessons JSON from reading/index.html")
    return json.loads(m.group(1))["lessons"]


def spoken(text):
    """Remove notation that causes stumbles in spoken Modern Standard Arabic."""
    text = str(text)
    # English terminology is displayed in writing but normally misread aloud.
    text = re.sub(r"\s*\([A-Za-z][^)]*\)", "", text)
    text = re.sub(r"\s*\([A-Za-z][^)]*\)", "", text)
    text = re.sub(r"\b(?:PKM|MMT|Fiat|Hard Money|Short Squeeze)\b", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def lesson_sections(lesson):
    """Five pieces, spoken as an actual mini-lesson rather than a raw page."""
    deep_paragraphs = [spoken(x) for x in lesson["deep"].split("\n\n") if x.strip()]
    deep_half = max(1, (len(deep_paragraphs) + 1) // 2)
    lesson_title = spoken(lesson["title"])
    sections = [
        (
            f"أهلًا بك في درس جديد من دفتر المعرفة. موضوعنا اليوم: {lesson_title}. "
            f"خلّنا نبدأ بالمعنى. {spoken(lesson['easy'])} "
            f"والتعريف بشكل أدق هو: {spoken(lesson['definition'])}",
            OPENING,
        ),
        (
            "والآن، خلّنا نفهم الفكرة بتفاصيل أكثر. "
            + " ".join(deep_paragraphs[:deep_half]),
            BETWEEN,
        ),
        (
            "نكمّل الشرح. "
            + " ".join(deep_paragraphs[deep_half:])
            if len(deep_paragraphs) > 1 else
            "لنتذكر الآن كيف تظهر هذه الفكرة في الواقع.",
            LONG_PAUSE,
        ),
        (
            f"خلّنا نشوف مثالًا من الواقع. {spoken(lesson['example'])} "
            f"ومتى قد تسمع هذا المصطلح؟ {spoken(lesson['recognize'])}",
            BETWEEN,
        ),
        (
            f"لكن، انتبه لهذا اللبس الشائع. {spoken(lesson['misconception'])} "
            f"والآن، كيف نطبق الفكرة؟ "
            + " ".join(
                f"الخطوة {number}: {spoken(step)}"
                for number, step in enumerate(lesson["steps"], 1)
            )
            + f" وتطبيق إضافي: {spoken(lesson['task'])}",
            THINKING_PAUSE,
        ),
        (
            f"وقبل أن ننهي، فكر في هذا السؤال: {spoken(lesson['question'])} "
            f"خذ وقتك في التفكير. والخلاصة: {spoken(lesson['takeaway'])} "
            "وبهذا نكون انتهينا من درس اليوم. نشوفك في الدرس القادم.",
            0,
        ),
    ]
    # Third section is not needed when no remaining explanation paragraphs.
    if len(deep_paragraphs) <= 1:
        sections.pop(2)
    return [(spoken(text), gap) for text, gap in sections if text.strip()]


def fingerprint(parts):
    message = json.dumps(
        {"voice": VOICE, "rate": RATE, "sections": parts, "version": 3},
        ensure_ascii=False, sort_keys=True,
    )
    return hashlib.sha256(message.encode("utf-8")).hexdigest()


async def synthesize(text, lesson_id, section):
    for attempt in range(1, 5):
        try:
            communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
            buf = io.BytesIO()
            async for event in communicate.stream():
                if event["type"] == "audio":
                    buf.write(event["data"])
            data = buf.getvalue()
            if len(data) < 2000:
                raise RuntimeError(f"Audio too small: {len(data)} bytes")
            return AudioSegment.from_file(io.BytesIO(data), format="mp3")
        except Exception as exc:
            print(f"{lesson_id=} {section=} attempt={attempt}: {exc}", flush=True)
            if attempt == 4:
                raise
            await asyncio.sleep(3 * attempt)


async def generate(lesson, old_manifest, new_manifest):
    number = int(lesson["id"])
    filename = f"lesson-{number:02d}.mp3"
    destination = OUT / filename
    parts = lesson_sections(lesson)
    digest = fingerprint(parts)
    if (destination.exists() and destination.stat().st_size > 10000
            and old_manifest.get(filename) == digest):
        new_manifest[filename] = digest
        print(f"Reuse {filename}", flush=True)
        return True

    async with LIMIT:
        try:
            narration = AudioSegment.silent(duration=350)
            for i, (text, gap_after) in enumerate(parts, 1):
                clip = await synthesize(text, number, i)
                # Avoid clipping the last syllable: retain full audio and add silence.
                narration += clip
                if gap_after:
                    narration += AudioSegment.silent(duration=gap_after)
                await asyncio.sleep(0.35)
            narration += AudioSegment.silent(duration=500)
            temporary = destination.with_suffix(".tmp.mp3")
            narration.export(str(temporary), format="mp3", bitrate="64k")
            if temporary.stat().st_size < 12000:
                raise RuntimeError("Exported lesson MP3 is unexpectedly small")
            temporary.replace(destination)
            new_manifest[filename] = digest
            duration = round(len(narration) / 1000, 1)
            print(f"OK {filename}: {duration}s, {destination.stat().st_size} bytes", flush=True)
            return True
        except Exception as exc:
            print(f"FAILED lesson {number}: {exc}", file=sys.stderr, flush=True)
            return False


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    lessons = lessons_from_html()
    if len(lessons) != 49:
        raise RuntimeError(f"Expected 49 lessons, got {len(lessons)}")
    try:
        old = json.loads(MANIFEST.read_text("utf-8"))
    except (OSError, ValueError):
        old = {}
    new = {}
    # Start with a single trial lesson for error detection before other jobs.
    first = await generate(lessons[0], old, new)
    if not first:
        raise SystemExit("First sample failed. Aborting without hammering provider.")
    results = await asyncio.gather(
        *(generate(lesson, old, new) for lesson in lessons[1:])
    )
    MANIFEST.write_text(
        json.dumps(new, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not all(results):
        failed = [l["id"] for l, ok in zip(lessons[1:], results) if not ok]
        raise SystemExit(f"Some narration jobs failed: {failed}")
    print("49 narrated lessons ready!", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
