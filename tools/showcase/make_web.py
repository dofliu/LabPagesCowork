#!/usr/bin/env python3
"""把渲染好的母片轉成網站用影片與封面。

  python tools/showcase/make_web.py master.mp4 --id windai-lab [--cover-at 4.5]

輸出（相對於網站根目錄）：
  assets/showcase/<id>.mp4   1280×720、H.264、faststart（網頁邊下載邊播）
  assets/showcase/<id>.jpg   960×540 封面（取自 --cover-at 秒的畫面）
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "showcase"


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        sys.exit("ffmpeg 失敗：" + p.stderr.decode("utf-8", "replace")[-800:])


def has_audio(src: Path) -> bool:
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                        "stream=index", "-of", "csv=p=0", str(src)], capture_output=True, text=True)
    return bool(p.stdout.strip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("master", type=Path)
    ap.add_argument("--id", required=True, help="專案 id（小寫英數與 -）")
    ap.add_argument("--cover-at", type=float, default=4.5, help="封面取第幾秒的畫面")
    ap.add_argument("--crf", type=int, default=27)
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,60}", a.id):
        sys.exit("id 只能用小寫英數與 -，例如 windai-lab")
    OUT.mkdir(parents=True, exist_ok=True)
    mp4, jpg = OUT / f"{a.id}.mp4", OUT / f"{a.id}.jpg"
    audio = ["-c:a", "aac", "-b:a", "128k"] if has_audio(a.master) else ["-an"]
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(a.master),
         "-vf", "scale=1280:720:flags=lanczos", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", str(a.crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", *audio, str(mp4)])
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a.cover_at:.2f}", "-i", str(a.master),
         "-frames:v", "1", "-vf", "scale=960:540:flags=lanczos", "-q:v", "4", str(jpg)])
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "default=nw=1:nk=1", str(mp4)], capture_output=True, text=True).stdout.strip()
    print(f"✓ {mp4.relative_to(ROOT)}  {mp4.stat().st_size/1e6:.1f} MB  {float(dur):.1f}s")
    print(f"✓ {jpg.relative_to(ROOT)}  {jpg.stat().st_size/1e3:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
