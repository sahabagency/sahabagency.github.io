"""Local CPU content renderer. No remote calls, no automatic publication."""
import os
import re
import shutil
import subprocess
import tempfile
import textwrap
import uuid
import zipfile
from pathlib import Path

def ass_text(value):
    value = re.sub(r"[{}\x00-\x1f\\]", " ", str(value)).strip()
    return r"\N".join(textwrap.wrap(value, width=24, break_long_words=True))

def clock(seconds):
    return f"{seconds//3600}:{seconds//60%60:02}:{seconds%60:02}.00"

def render(root, title, slides, seconds=5):
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 100:
        raise ValueError("invalid title")
    if not isinstance(slides, list) or not 1 <= len(slides) <= 8 or any(
        not isinstance(x, str) or not 1 <= len(x.strip()) <= 140 for x in slides
    ):
        raise ValueError("invalid slides")
    if type(seconds) is not int or not 3 <= seconds <= 8:
        raise ValueError("invalid duration")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg_unavailable")
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    key = uuid.uuid4().hex
    with tempfile.TemporaryDirectory(prefix=".render-", dir=root) as directory:
        work = Path(directory)
        header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 0
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Brand,DejaVu Sans,29,&H00C7E27D,&H00FFFFFF,&H00131909,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,8,40,40,85,1
Style: Title,DejaVu Sans,40,&H00FFFFFF,&H00FFFFFF,&H00131909,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,8,50,50,225,1
Style: Body,DejaVu Sans,53,&H00FFFFFF,&H00FFFFFF,&H00131909,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,55,55,60,1
Style: Foot,DejaVu Sans,25,&H00C7E27D,&H00FFFFFF,&H00131909,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,50,50,100,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        duration = seconds * len(slides)
        def event(start, end, style, value):
            return f"Dialogue: 0,{clock(start)},{clock(end)},{style},,0,0,0,,{value}\n"
        script = header + event(0, duration, "Brand", "SAHAB / CONTENT STUDIO") + event(0, duration, "Title", ass_text(title))
        for i, slide in enumerate(slides):
            start = i * seconds
            script += event(start, start+seconds, "Body", ass_text(slide))
            script += event(start, start+seconds, "Foot", f"{i+1:02} / {len(slides):02}   |   SAHAB")
        (work / "captions.ass").write_text(script, encoding="utf-8")
        def run(args):
            subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y", *args],
                           cwd=work, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True, timeout=120)
        run(["-f","lavfi","-i",f"color=c=0x091319:s=720x1280:r=25:d={duration}",
             "-vf","ass=captions.ass","-c:v","libx264","-threads","2","-preset","veryfast",
             "-crf","22","-pix_fmt","yuv420p","-movflags","+faststart","video.mp4"])
        with zipfile.ZipFile(work/"carousel.zip","w",zipfile.ZIP_DEFLATED) as archive:
            for i in range(len(slides)):
                image=f"slide-{i+1:02}.png"
                run(["-ss",str(i*seconds+1),"-i","video.mp4","-frames:v","1","-threads","1",image])
                archive.write(work/image,image)
        for name in ("video.mp4","carousel.zip"):
            if (work/name).stat().st_size < 1000:
                raise RuntimeError("empty output")
        target=root/key
        target.mkdir(mode=0o700)
        for name in ("video.mp4","carousel.zip"):
            os.replace(work/name,target/name)
    return {"id":key,"duration":duration,"slides":len(slides),"format":"720x1280","audio":False}
