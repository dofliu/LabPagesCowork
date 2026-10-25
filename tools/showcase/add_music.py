#!/usr/bin/env python3
"""幫已上線的專案動畫補上／更換背景配樂（不必重渲場景）。

  python tools/showcase/add_music.py --id controlboardtwin --mood tech
  python tools/showcase/add_music.py --id windai-lab --music my-track.mp3 --loudness -16

直接改寫 assets/showcase/<id>.mp4：影像串流原樣複製，音軌換成新配樂（頭尾淡入淡出、響度正規化）。
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"失敗：{' '.join(cmd[:3])}…\n{p.stderr[-600:]}")
    return p.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--mood", choices=["tech", "calm", "epic"], default="tech")
    ap.add_argument("--music", type=Path, help="改用指定音樂檔（不合成）")
    ap.add_argument("--loudness", type=float, default=-18)
    a = ap.parse_args()
    mp4 = ROOT / "assets" / "showcase" / f"{a.id}.mp4"
    if not mp4.exists():
        sys.exit(f"找不到 {mp4.relative_to(ROOT)}")
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=nw=1:nk=1", str(mp4)]).strip())
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        src = a.music
        if src is None:
            src = td / "bgm.wav"
            run([sys.executable, str(HERE / "make_music.py"), "--out", str(src),
                 "--duration", f"{dur:.3f}", "--mood", a.mood, "--seed", a.id])
        out = td / "out.mp4"
        af = (f"afade=t=in:d=0.8,afade=t=out:st={max(0, dur - 3):.3f}:d=3,"
              f"loudnorm=I={a.loudness}:TP=-1.5:LRA=11")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-stream_loop", "-1", "-i", str(src),
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", af, "-c:a", "aac", "-b:a", "128k",
             "-ar", "48000", "-t", f"{dur:.3f}", "-movflags", "+faststart", str(out)])
        out.replace(mp4)
    print(f"✓ {mp4.relative_to(ROOT)} 已加上配樂（{'自備音樂' if a.music else 'mood=' + a.mood}，{a.loudness} LUFS，{dur:.1f}s）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
