#!/usr/bin/env python3
"""把渲好的場景 MP4 依分鏡表用 xfade 轉場串接,並混入音樂/音效,產出成品。

自含腳本 — 只依賴 ffmpeg。音訊三種模式(依「不要吵」的實戰教訓調校):
  --music FILE   使用者提供的音樂(推薦):短於片長時 1.5s 交叉淡接循環(硬接有縫),
                 頭 1s 淡入、尾 3s 淡出,loudnorm 到 --loudness(預設 -16;
                 想要「背景音樂感」用 -20)
  --bed          安靜合成氛圍(無音樂檔時的退路):暖和弦 pad + 每 2s 一顆軟心跳,
                 -23 LUFS。刻意不含持續性噪聲層 — 60 秒嘶聲是「吵」的頭號來源
  (預設)         無聲 — 交給使用者後製配樂

  --sfx          另外疊極輕的轉場氣音(0.18 音量)與 3 顆重點低音 impact;
                 預設關閉,有音樂時通常不需要

用法:
  python assemble_video.py storyboard.json --workdir work/intro --out intro.mp4 \
      [--music bgm.mp3] [--music-gain -4] [--loudness -20] [--bed] [--sfx]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], step: str, timeout: int = 1200) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"{step} 失敗 (code {proc.returncode}): {(proc.stderr or '')[:500]}")
    return proc


def offsets(scenes: list[dict], xf: float) -> tuple[list[float], float]:
    starts, t = [], 0.0
    for i, sc in enumerate(scenes):
        starts.append(t)
        t += float(sc["duration"]) - (xf if i < len(scenes) - 1 else 0.0)
    return starts, t


def join_video(scenes: list[dict], workdir: Path, xf: float, fps: int, tmp: Path) -> Path:
    starts, _ = offsets(scenes, xf)
    inputs: list[str] = []
    for sc in scenes:
        inputs += ["-i", str(workdir / f"{Path(sc['file']).stem}.mp4")]
    fg, prev = [], "[0:v]"
    for i in range(1, len(scenes)):
        trans = scenes[i - 1].get("transition") or "fade"
        fg.append(f"{prev}[{i}:v]xfade=transition={trans}:duration={xf}:offset={starts[i]:.3f}[v{i}]")
        prev = f"[v{i}]"
    fg.append(f"{prev}format=yuv420p[vout]")
    dst = tmp / "joined.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
         "-filter_complex", ";".join(fg), "-map", "[vout]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", str(fps), str(dst)],
        "xfade 串接")
    return dst


def music_track(music: Path, total: float, gain_db: float, tmp: Path) -> Path:
    probe = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=nw=1:nk=1", str(music)], "ffprobe 音樂", 60)
    mdur = float(probe.stdout.strip())
    cf = 1.5
    copies = 1
    while copies * mdur - (copies - 1) * cf < total + 0.5:
        copies += 1
    dst = tmp / "music.wav"
    fade = f"volume={gain_db}dB,afade=t=in:d=1.0,afade=t=out:st={total - 3:.3f}:d=3"
    if copies == 1:
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(music),
             "-af", fade, "-t", f"{total:.3f}", "-ar", "48000", "-ac", "2", str(dst)],
            "音樂裁切")
    else:
        m_inputs: list[str] = []
        for _ in range(copies):
            m_inputs += ["-i", str(music)]
        fg, prev = [], "[0:a]"
        for i in range(1, copies):
            fg.append(f"{prev}[{i}:a]acrossfade=d={cf}:c1=tri:c2=tri[m{i}]")
            prev = f"[m{i}]"
        fg.append(f"{prev}{fade}[mout]")
        run(["ffmpeg", "-y", "-loglevel", "error", *m_inputs,
             "-filter_complex", ";".join(fg), "-map", "[mout]",
             "-t", f"{total:.3f}", "-ar", "48000", "-ac", "2", str(dst)],
            "音樂交叉淡接循環")
    return dst


def bed_track(total: float, kick_in: float, kick_out: float, tmp: Path) -> list[Path]:
    """安靜合成氛圍:暖 pad(Am↔F 8 秒互溶) + 稀疏心跳。"""
    d = f"{total:.3f}"
    padexpr = (
        "0.15*((0.5+0.5*cos(PI*t/4))*(sin(2*PI*110*t)+0.9*sin(2*PI*164.81*t)+0.25*sin(2*PI*220*t))"
        "+(0.5-0.5*cos(PI*t/4))*(sin(2*PI*87.31*t)+0.9*sin(2*PI*130.81*t)+0.25*sin(2*PI*174.61*t)))"
        "*(0.96+0.04*sin(2*PI*0.18*t))"
    )
    pad = tmp / "pad.wav"
    run(["ffmpeg", "-y", "-loglevel", "error",
         "-f", "lavfi", "-i", f"aevalsrc={padexpr}:s=48000:d={d}",
         "-af", ("lowpass=f=900,aecho=0.6:0.35:140:0.18,"
                 f"afade=t=in:d=2.5,afade=t=out:st={total - 3.5:.3f}:d=3.5"),
         str(pad)], "合成 pad")
    kick = tmp / "kick.wav"
    run(["ffmpeg", "-y", "-loglevel", "error",
         "-f", "lavfi", "-i",
         f"aevalsrc=sin(2*PI*(42+50*exp(-16*mod(t\\,2)))*mod(t\\,2))*exp(-6*mod(t\\,2))*0.6:s=48000:d={d}",
         "-af", f"lowpass=f=140,afade=t=in:st={kick_in:.3f}:d=2,afade=t=out:st={kick_out:.3f}:d=2",
         str(kick)], "合成心跳")
    return [pad, kick]


def sfx_tracks(cut_offsets: list[float], accents: list[float], tmp: Path) -> tuple[Path, Path]:
    whoosh = tmp / "whoosh.wav"
    run(["ffmpeg", "-y", "-loglevel", "error",
         "-f", "lavfi", "-i", "anoisesrc=color=pink:sample_rate=48000:duration=0.8",
         "-af", "lowpass=f=1600,highpass=f=200,afade=t=in:d=0.38,afade=t=out:st=0.4:d=0.4,volume=0.18",
         str(whoosh)], "合成 whoosh")
    boom = tmp / "boom.wav"
    run(["ffmpeg", "-y", "-loglevel", "error",
         "-f", "lavfi", "-i",
         "aevalsrc=sin(2*PI*(36+60*exp(-6*t))*t)*exp(-3.6*t)*0.9:s=48000:d=1.4",
         "-af", "lowpass=f=200,volume=0.5", str(boom)], "合成 impact")
    return whoosh, boom


def main() -> int:
    ap = argparse.ArgumentParser(description="xfade 串接 + 配樂出片")
    ap.add_argument("storyboard", type=Path)
    ap.add_argument("--workdir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--music", type=Path, default=None)
    ap.add_argument("--music-gain", type=float, default=0.0)
    ap.add_argument("--loudness", type=float, default=None,
                    help="LUFS 目標(音樂預設 -16,背景感 -20;bed 固定 -23)")
    ap.add_argument("--bed", action="store_true", help="無音樂檔時用安靜合成氛圍")
    ap.add_argument("--sfx", action="store_true", help="疊極輕轉場氣音/重點 impact")
    a = ap.parse_args()

    sb = json.loads(a.storyboard.read_text(encoding="utf-8"))
    scenes = sb["scenes"]
    fps = int(sb.get("fps", 30))
    xf = float(sb.get("xfade", 0.6))
    starts, total = offsets(scenes, xf)
    tmp = a.workdir / "_assemble"
    tmp.mkdir(parents=True, exist_ok=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)

    video = join_video(scenes, a.workdir, xf, fps, tmp)

    layers: list[Path] = []
    if a.music is not None:
        layers.append(music_track(a.music, total, a.music_gain, tmp))
        target_i = a.loudness if a.loudness is not None else -16
    elif a.bed:
        layers += bed_track(total, kick_in=starts[min(2, len(starts) - 1)],
                            kick_out=max(0.0, total - 9.0), tmp=tmp)
        target_i = a.loudness if a.loudness is not None else -23
    else:
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video),
             "-c", "copy", "-movflags", "+faststart", str(a.out)], "無聲出片")
        print(f"[done] {a.out}(無聲,{total:.1f}s)")
        return 0

    inputs: list[str] = []
    for p in layers:
        inputs += ["-i", str(p)]
    fg, tags, idx = [], [f"[{i}:a]" for i in range(len(layers))], len(layers)
    if a.sfx:
        whoosh, boom = sfx_tracks(starts[1:], [], tmp)
        for off in starts[1:]:
            inputs += ["-i", str(whoosh)]
            at = int(max(0.0, off - 0.35) * 1000)
            fg.append(f"[{idx}:a]adelay={at}|{at}[w{idx}]")
            tags.append(f"[w{idx}]")
            idx += 1
        for at_s in (1.05, starts[-1] + 0.75):
            inputs += ["-i", str(boom)]
            at = int(at_s * 1000)
            fg.append(f"[{idx}:a]adelay={at}|{at}[b{idx}]")
            tags.append(f"[b{idx}]")
            idx += 1
    if len(tags) == 1 and not fg:
        fg.append(f"{tags[0]}loudnorm=I={target_i}:TP=-1.5:LRA=11[aout]")
    else:
        fg.append("".join(tags) + f"amix=inputs={len(tags)}:duration=first:normalize=0,"
                  f"loudnorm=I={target_i}:TP=-1.5:LRA=11[aout]")
    bed = tmp / "bed.m4a"
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
         "-filter_complex", ";".join(fg), "-map", "[aout]",
         "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", str(bed)], "混音")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(bed),
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy",
         "-movflags", "+faststart", "-t", f"{total:.3f}", str(a.out)], "mux")
    print(f"[done] {a.out}({total:.1f}s,響度目標 {target_i} LUFS)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
