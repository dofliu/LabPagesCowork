#!/usr/bin/env python3
"""把來源素材(本地圖片 / 雲端下載的 base64)正規化成可嵌入場景的資產。

做四件事:等比縮到 --max-width 以內(不放大)、統一命名、輸出到場景可用的相對目錄、
產出 assets_manifest.json 讓寫場景時知道每張圖的實際尺寸(橫圖走全幅、直圖走卡片)。

只依賴 ffmpeg/ffprobe(渲染本來就需要),不需要 PIL。

用法:
  # 本地檔案或資料夾(資料夾會撈第一層圖片)
  python prep_assets.py --out promo/assets shot1.png logo.png /path/to/folder

  # 雲端連接器抓下來的 base64:dl.json = [{"name":"logo.png","b64":"iVBOR..."}]
  python prep_assets.py --out promo/assets --from-base64 dl.json

輸出:
  <out>/asset_01.png …            正規化後的圖
  <out>/assets_manifest.json      原檔名 → 新檔名 → 寬高 → 形狀(wide/tall/square)
"""
from __future__ import annotations

import argparse
import base64
import binascii
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff"}


def probe_size(path: Path) -> tuple[int, int] | None:
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(path)],
        capture_output=True, text=True, timeout=60)
    out = (proc.stdout or "").strip().splitlines()
    if proc.returncode != 0 or not out:
        return None
    try:
        w, h = out[0].split("x")[:2]
        return int(w), int(h)
    except ValueError:
        return None


def shape_of(w: int, h: int) -> str:
    r = w / h if h else 1.0
    if r >= 1.25:
        return "wide"
    if r <= 0.8:
        return "tall"
    return "square"


def normalize(src: Path, dst: Path, max_width: int) -> tuple[int, int] | None:
    """等比縮到 max_width 以內(不放大),寫成 dst。回傳最終尺寸。"""
    size = probe_size(src)
    if size is None:
        return None
    w, h = size
    # 寬高都補成偶數,避免某些編碼器/縮放器抱怨
    scale = f"scale='min({max_width},iw)':-2:flags=lanczos" if w > max_width else "scale=trunc(iw/2)*2:trunc(ih/2)*2"
    proc = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", scale,
         "-frames:v", "1", str(dst)],
        capture_output=True, timeout=180)
    if proc.returncode != 0 or not dst.exists():
        return None
    return probe_size(dst)


def collect_inputs(items: list[str]) -> list[Path]:
    found: list[Path] = []
    for it in items:
        p = Path(it).expanduser()
        if p.is_dir():
            found += sorted(q for q in p.iterdir()
                            if q.is_file() and q.suffix.lower() in IMG_EXT)
        elif p.is_file():
            found.append(p)
        else:
            print(f"[prep] ⚠ 找不到:{p}", file=sys.stderr)
    return found


def land_base64(manifest: Path, tmp: Path) -> list[Path]:
    """把 [{"name":..., "b64":...}] 寫成暫存檔。也接受 data:image/png;base64,… 前綴。"""
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("files", [])
    out: list[Path] = []
    for i, item in enumerate(data, 1):
        name = item.get("name") or f"dl_{i:02d}.png"
        raw = item.get("b64") or item.get("data") or ""
        if "," in raw[:64] and raw.lstrip().startswith("data:"):
            raw = raw.split(",", 1)[1]
        try:
            blob = base64.b64decode(raw, validate=False)
        except (binascii.Error, ValueError) as e:
            print(f"[prep] ⚠ {name} base64 解碼失敗:{e}", file=sys.stderr)
            continue
        if not blob:
            print(f"[prep] ⚠ {name} 是空的,跳過", file=sys.stderr)
            continue
        p = tmp / Path(name).name
        p.write_bytes(blob)
        out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="正規化場景素材圖片")
    ap.add_argument("inputs", nargs="*", help="圖片檔或資料夾")
    ap.add_argument("--out", type=Path, required=True, help="輸出目錄(建議 <場景目錄>/assets)")
    ap.add_argument("--from-base64", type=Path, default=None,
                    help='JSON: [{"name":"a.png","b64":"…"}] — 雲端下載用')
    ap.add_argument("--max-width", type=int, default=1920)
    ap.add_argument("--prefix", default="asset")
    a = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            print(f"[prep] {tool} 不在 PATH", file=sys.stderr)
            return 1

    a.out.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []

    with tempfile.TemporaryDirectory(prefix="prep_assets_") as td:
        tmp = Path(td)
        srcs = collect_inputs(a.inputs)
        if a.from_base64:
            srcs += land_base64(a.from_base64, tmp)
        if not srcs:
            print("[prep] 沒有輸入素材", file=sys.stderr)
            return 1

        for i, src in enumerate(srcs, 1):
            ext = ".jpg" if src.suffix.lower() in {".jpg", ".jpeg"} else ".png"
            dst = a.out / f"{a.prefix}_{i:02d}{ext}"
            size = normalize(src, dst, a.max_width)
            if size is None:
                print(f"[prep] ⚠ 略過(不是可讀圖片):{src.name}", file=sys.stderr)
                dst.unlink(missing_ok=True)
                continue
            w, h = size
            manifest.append({"source": src.name, "file": dst.name,
                             "width": w, "height": h, "shape": shape_of(w, h)})
            print(f"[prep] ✓ {src.name} → {dst.name} ({w}×{h}, {shape_of(w, h)})")

    if not manifest:
        print("[prep] 沒有任何素材成功轉出", file=sys.stderr)
        return 1

    (a.out / "assets_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[prep] 完成 {len(manifest)} 張 → {a.out}/assets_manifest.json")
    print("[prep] HTML 用相對路徑引用,例:<img src=\"assets/%s\">" % manifest[0]["file"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
