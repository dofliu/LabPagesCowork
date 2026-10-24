#!/usr/bin/env python3
"""把分鏡表裡的 HTML 動畫場景逐一渲成 MP4(虛擬時鐘無頭逐格擷取)。

自含腳本 — 只依賴 playwright(+任一 Chromium)與 ffmpeg,不依賴宿主專案的程式碼。

為什麼用「虛擬時鐘」而不是即時錄影:即時錄影受機器負載影響,動畫快慢/掉幀不可
重現。這裡在頁面腳本執行前注入 shim,接管 performance.now / Date.now / rAF /
setTimeout / setInterval,每格手動把虛擬時間推進 1/fps 秒並對齊 CSS/WAAPI 動畫的
currentTime,再截一張圖 → 30fps 就是精準 30fps。

用法:
  python render_scenes.py storyboard.json --workdir work/intro [--only scene03_video]

storyboard.json 格式見 SKILL.md。每景輸出:
  <workdir>/<stem>.mp4           場景影片
  <workdir>/check_<stem>.png     85% 時間點的抽查格(渲完務必逐張檢查排版!)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VIRTUAL_CLOCK_JS = r"""
(() => {
  if (window.__vClockInstalled) return;
  window.__vClockInstalled = true;
  let now = 0;
  const RealDate = Date;
  try { window.performance.now = () => now; } catch (e) {}
  function VDate(...args) {
    if (args.length === 0) return new RealDate(now);
    return new RealDate(...args);
  }
  VDate.now = () => now; VDate.parse = RealDate.parse; VDate.UTC = RealDate.UTC;
  VDate.prototype = RealDate.prototype; window.Date = VDate;
  let rafs = []; let rafSeq = 0;
  window.requestAnimationFrame = (cb) => { const id = ++rafSeq; rafs.push([id, cb]); return id; };
  window.cancelAnimationFrame = (id) => { rafs = rafs.filter(([i]) => i !== id); };
  let timers = []; let timerSeq = 0;
  window.setTimeout = (fn, delay, ...args) => {
    const id = ++timerSeq;
    timers.push({ id, fn, due: now + (Number(delay) || 0), args, every: null });
    return id;
  };
  window.setInterval = (fn, delay, ...args) => {
    const id = ++timerSeq; const d = Math.max(1, Number(delay) || 0);
    timers.push({ id, fn, due: now + d, args, every: d });
    return id;
  };
  window.clearTimeout = (id) => { timers = timers.filter((t) => t.id !== id); };
  window.clearInterval = window.clearTimeout;
  window.__advanceFrame = (deltaMs) => {
    now += deltaMs;
    for (let guard = 0; guard < 10000; guard++) {
      const due = timers.filter((t) => t.due <= now).sort((a, b) => a.due - b.due);
      if (due.length === 0) break;
      const t = due[0];
      if (t.every == null) { timers = timers.filter((x) => x !== t); } else { t.due += t.every; }
      try { t.fn(...t.args); } catch (e) {}
    }
    const batch = rafs; rafs = [];
    for (const [, cb] of batch) { try { cb(now); } catch (e) {} }
    try {
      const anims = (document.getAnimations ? document.getAnimations() : []);
      for (const a of anims) { try { a.pause(); a.currentTime = now; } catch (e) {} }
    } catch (e) {}
    return now;
  };
})();
"""


def find_chromium() -> str | None:
    """Chromium 執行檔:環境變數優先,再試 PATH 常見名字;都沒有回 None(交給 playwright 預設)。"""
    for env in ("INTRO_VIDEO_CHROMIUM", "REPO_INTRO_CHROMIUM", "CHROMIUM_PATH", "EDUSTUDIO_CHROMIUM_PATH"):
        p = os.environ.get(env)
        if p and Path(p).exists():
            return p
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    return None


def render_scene(html: Path, out_mp4: Path, *, duration: float, fps: int,
                 width: int, height: int, settle_ms: int = 400) -> None:
    from playwright.sync_api import sync_playwright

    if not shutil.which("ffmpeg"):
        raise FileNotFoundError("ffmpeg 不在 PATH — 渲染需要 ffmpeg")
    total = max(1, round(duration * fps))
    delta = 1000.0 / fps
    launch: dict = {"args": ["--no-sandbox", "--disable-gpu"]}
    exe = find_chromium()
    if exe:
        launch["executable_path"] = exe
    with tempfile.TemporaryDirectory(prefix="intro_frames_") as td:
        frames = Path(td)
        with sync_playwright() as pw:
            try:
                browser = pw.chromium.launch(**launch)
            except Exception as e:
                raise RuntimeError(
                    "Chromium 啟動失敗。若 playwright 版本與預裝瀏覽器不合,"
                    "設 CHROMIUM_PATH 指向瀏覽器執行檔後重試。原始錯誤: %s" % e) from e
            try:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.add_init_script(VIRTUAL_CLOCK_JS)
                page.goto(html.resolve().as_uri(), wait_until="load")
                if settle_ms > 0:
                    page.wait_for_timeout(settle_ms)  # 字型/首批 rAF 落定(真實時間)
                for i in range(total):
                    page.screenshot(path=str(frames / f"f_{i + 1:06d}.jpg"), type="jpeg", quality=92)
                    page.evaluate("(d) => window.__advanceFrame && window.__advanceFrame(d)", delta)
            finally:
                browser.close()
        out_mp4.parent.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-framerate", str(fps), "-i", str(frames / "f_%06d.jpg"),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
            str(out_mp4),
        ], capture_output=True, timeout=600)
        if proc.returncode != 0:
            raise RuntimeError("ffmpeg 合成失敗: %s" % proc.stderr.decode("utf-8", "replace")[:500])


def dump_check_frame(mp4: Path, png: Path, at: float) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{at:.2f}",
                    "-i", str(mp4), "-frames:v", "1", str(png)],
                   capture_output=True, timeout=120)


def main() -> int:
    ap = argparse.ArgumentParser(description="渲染分鏡表中的 HTML 場景")
    ap.add_argument("storyboard", type=Path)
    ap.add_argument("--workdir", type=Path, required=True)
    ap.add_argument("--only", default=None, help="只重渲這一景(檔名 stem),改單景後用")
    a = ap.parse_args()

    sb = json.loads(a.storyboard.read_text(encoding="utf-8"))
    fps = int(sb.get("fps", 30))
    w, h = int(sb.get("width", 1920)), int(sb.get("height", 1080))
    base = a.storyboard.parent
    a.workdir.mkdir(parents=True, exist_ok=True)

    for sc in sb["scenes"]:
        stem = Path(sc["file"]).stem
        if a.only and stem != a.only:
            continue
        html = (base / sc["file"]).resolve()
        dur = float(sc["duration"])
        out = a.workdir / f"{stem}.mp4"
        print(f"[render] {stem} ({dur:.1f}s)…", flush=True)
        render_scene(html, out, duration=dur, fps=fps, width=w, height=h)
        dump_check_frame(out, a.workdir / f"check_{stem}.png", at=dur * 0.85)
        print(f"[render] ✓ {out.name} + check_{stem}.png")
    print("[render] 完成 — 記得逐張檢查 check_*.png 的排版再組片!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
