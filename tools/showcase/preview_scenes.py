#!/usr/bin/env python3
"""快速排版預覽：不渲染影片，只截每景 85% 時間點的畫面，拼成一張總覽圖（約 3 秒／景）。

  python tools/showcase/preview_scenes.py <storyboard.json> [<storyboard.json> ...] --out <dir>

每個 storyboard 產出 <dir>/<資料夾名>_sheet.jpg（5 景縮圖拼接）。正式渲染前先用它抓文字溢出、相撞。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_scenes import VIRTUAL_CLOCK_JS, find_chromium  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("storyboards", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--at", type=float, default=0.85)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    launch = {"args": ["--no-sandbox", "--disable-gpu"]}
    exe = find_chromium()
    if exe:
        launch["executable_path"] = exe
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as td:
        b = pw.chromium.launch(**launch)
        for sb_path in a.storyboards:
            sb = json.loads(sb_path.read_text(encoding="utf-8"))
            shots = []
            for sc in sb["scenes"]:
                page = b.new_page(viewport={"width": 1920, "height": 1080})
                page.add_init_script(VIRTUAL_CLOCK_JS)
                page.goto((sb_path.parent / sc["file"]).resolve().as_uri(), wait_until="load")
                page.wait_for_timeout(300)
                target = float(sc["duration"]) * a.at * 1000
                for _ in range(int(target // 100)):
                    page.evaluate("d => window.__advanceFrame(d)", 100)
                png = Path(td) / f"{sb_path.parent.name}_{Path(sc['file']).stem}.png"
                page.screenshot(path=str(png))
                page.close()
                shots.append(png)
            sheet = a.out / f"{sb_path.parent.name}_sheet.jpg"
            inputs = sum((["-i", str(s)] for s in shots), [])
            n = len(shots)
            # 2 欄排版
            layout = "|".join(f"{(i % 2) * 960}_{(i // 2) * 540}" for i in range(n))
            fg = "".join(f"[{i}:v]scale=960:540[s{i}];" for i in range(n)) + "".join(f"[s{i}]" for i in range(n)) + \
                f"xstack=inputs={n}:layout={layout}:fill=black"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fg,
                            "-frames:v", "1", "-q:v", "3", str(sheet)], check=True)
            print(f"✓ {sheet}")
        b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
