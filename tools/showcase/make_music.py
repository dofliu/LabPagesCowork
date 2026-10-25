#!/usr/bin/env python3
"""為專案動畫產生原創背景配樂（純程式合成，無版權問題）。

  python tools/showcase/make_music.py --out bgm.wav --duration 30.1 --mood tech --seed windai-lab

曲風（--mood）：
  tech   科技感：小調流行和弦、八分音符琶音、輕鼓組（預設，適合系統／AI／工具類專案）
  calm   溫和：七和弦、慢速、無大鼓，只有輕拍（適合教育、研究介紹、文件型成果）
  epic   壯闊：較大的鋪底與低音、第三段堆疊（適合大型平台、能源、成果發表）

結構會對齊 30 秒五景分鏡：前 ~6 秒只有鋪底與琶音（開場），之後鼓組進入，
最後 ~4 秒鼓組退場、主和弦延音收尾並淡出。--seed 讓每個專案的琶音型與音色細節不同。
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}

MOODS = {
    # bpm, 和弦進行（音名列表，第一個為根音），鼓組強度, 琶音密度(每拍音數), 鋪底亮度
    "tech": dict(bpm=96, prog=[["A", "C", "E"], ["F", "A", "C"], ["C", "E", "G"], ["G", "B", "D"]],
                 drums=1.0, arp=2, bright=1800, pluck=0.18),
    "calm": dict(bpm=80, prog=[["C", "E", "G", "B"], ["A", "C", "E", "G"], ["F", "A", "C", "E"], ["G", "B", "D", "F"]],
                 drums=0.35, arp=2, bright=1200, pluck=0.16),
    "epic": dict(bpm=100, prog=[["D", "F", "A"], ["A#", "D", "F"], ["F", "A", "C"], ["C", "E", "G"]],
                 drums=1.15, arp=4, bright=2200, pluck=0.13),
}


def freq(name: str, octave: int) -> float:
    return 440.0 * 2 ** ((NOTE[name] + 12 * (octave + 1) - 69) / 12)


def onepole_lp(x: np.ndarray, cutoff: float) -> np.ndarray:
    a = np.exp(-2 * np.pi * cutoff / SR)
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x)


def env_adsr(n: int, a: float, d: float, s: float, r: float) -> np.ndarray:
    t = np.arange(n) / SR
    dur = n / SR
    e = np.where(t < a, t / max(a, 1e-4), 1.0)
    e = np.where((t >= a) & (t < a + d), 1 - (1 - s) * (t - a) / max(d, 1e-4), e)
    e = np.where(t >= a + d, s, e)
    rel_start = max(dur - r, a)
    e = np.where(t >= rel_start, e * np.clip(1 - (t - rel_start) / max(r, 1e-4), 0, 1), e)
    return e


def saw_soft(f: float, n: int, detune: float, rng: np.random.Generator) -> np.ndarray:
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, 7):  # 帶限鋸齒（前 6 個泛音）
        out += np.sin(2 * np.pi * f * k * (1 + detune) * t + rng.uniform(0, 6.28)) / k
    return out


def place(buf: np.ndarray, sig: np.ndarray, start: float, pan: float = 0.0) -> None:
    i = int(start * SR)
    if i >= buf.shape[0]:
        return
    sig = sig[: buf.shape[0] - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * l * 1.414
    buf[i:i + len(sig), 1] += sig * r * 1.414


def reverb(x: np.ndarray, seconds: float, rng: np.random.Generator) -> np.ndarray:
    from scipy.signal import fftconvolve
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros_like(x)
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-t * 6.0 / seconds)
        ir = onepole_lp(ir, 4000)
        ir /= np.sqrt(np.sum(ir ** 2))
        out[:, ch] = fftconvolve(x[:, ch], ir)[: len(x)]
    return out


def compose(duration: float, mood: str, seed: str) -> np.ndarray:
    cfg = MOODS[mood]
    rng = np.random.default_rng(int(hashlib.sha1(seed.encode()).hexdigest()[:8], 16))
    beat = 60.0 / cfg["bpm"]
    bar = beat * 4
    total = duration + 0.2
    N = int(total * SR)
    pad, arp, bass, drums = (np.zeros((N, 2)) for _ in range(4))
    intro_end = min(6.0, duration * 0.2)
    outro = max(duration - 4.2, intro_end + 4)
    nbars = int(np.ceil(duration / bar)) + 1

    # 琶音型：依 seed 從幾種型態中挑一種
    patterns = [[0, 1, 2, 1], [0, 2, 1, 2], [0, 1, 2, 3], [2, 1, 0, 1], [0, 2, 3, 1]]
    pat = patterns[rng.integers(len(patterns))]
    arp_oct = 4 + (1 if mood == "epic" else 0)

    for b in range(nbars):
        chord = cfg["prog"][b % len(cfg["prog"])]
        t0 = b * bar
        if t0 >= total:
            break
        last = t0 + bar >= outro  # 進入尾段：最後一個和弦延長
        length = (total - t0) if last else bar + 0.35
        n = int(length * SR)

        # ── 鋪底 pad：每個和弦音兩顆微失諧鋸齒，低通、慢起音 ──
        p = np.zeros(n)
        for j, nm in enumerate(chord):
            octv = 3 if j == 0 else 4
            f = freq(nm, octv)
            p += saw_soft(f, n, 0.0025, rng) + saw_soft(f, n, -0.0025, rng)
        p = onepole_lp(p, cfg["bright"]) * env_adsr(n, 0.6, 0.4, 0.85, 0.5) * 0.045
        place(pad, p, t0, pan=-0.15)
        place(pad, p * 0.8, t0 + 0.012, pan=0.15)

        # ── 低音：根音，intro 後才出現 ──
        if t0 + 0.01 >= intro_end * 0.6:
            root = freq(chord[0], 2)
            hits = [0, 1.5, 2, 3] if mood != "calm" else [0, 2]
            for h in hits:
                st = t0 + h * beat
                if st >= (outro if not last else total) or st >= total:
                    continue
                ln = beat * (1.4 if h in (0, 2) else 0.45)
                if last and h == 0:
                    ln = total - st
                m = int(ln * SR)
                tt = np.arange(m) / SR
                s = np.sin(2 * np.pi * root * tt) + 0.25 * np.sin(2 * np.pi * root * 2 * tt)
                place(bass, s * env_adsr(m, 0.008, 0.15, 0.7, 0.12) * 0.16, st)
            if last:
                break_bass = True  # noqa: F841

        # ── 琶音 pluck ──
        if not last or t0 < outro:
            steps = 4 * cfg["arp"]
            step = beat / cfg["arp"]
            tones = chord + [chord[0]]
            for k in range(steps):
                st = t0 + k * step
                if st >= outro - 0.1:
                    break
                idx = pat[k % len(pat)] % len(tones)
                nm = tones[idx]
                octv = arp_oct + (1 if idx == len(tones) - 1 else 0)
                f = freq(nm, octv)
                m = int(0.9 * SR)
                tt = np.arange(m) / SR
                s = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 18)
                     + 0.12 * np.sin(2 * np.pi * 3 * f * tt) * np.exp(-tt * 30))
                vel = 0.75 + 0.25 * (k % cfg["arp"] == 0) + rng.uniform(-0.06, 0.06)
                s *= np.exp(-tt * (5.5 if mood != "calm" else 3.5)) * cfg["pluck"] * vel
                fade_in = np.clip((st) / max(intro_end, 0.1), 0.35, 1.0)
                place(arp, s * fade_in, st, pan=0.35 if k % 2 else -0.35)

        # ── 鼓組：intro 後進場、尾段退場 ──
        if intro_end - 0.05 <= t0 < outro - 0.05:
            dz = cfg["drums"]
            for h in range(4):
                st = t0 + h * beat
                if h in (0, 2) and mood != "calm":  # 大鼓
                    m = int(0.35 * SR); tt = np.arange(m) / SR
                    k_ = np.sin(2 * np.pi * (48 + 90 * np.exp(-tt * 28)) * tt) * np.exp(-tt * 9)
                    place(drums, k_ * 0.42 * dz, st)
                if h in (1, 3):  # 拍手／軟軍鼓（短促濾波雜音＋音體）
                    m = int(0.22 * SR); tt = np.arange(m) / SR
                    nz = onepole_lp(rng.standard_normal(m), 3500) - onepole_lp(rng.standard_normal(m), 600)
                    sn = nz * np.exp(-tt * 22) * 0.16 + np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 30) * 0.08
                    place(drums, sn * dz, st, pan=0.05)
                for e in range(2):  # 八分音符 hi-hat（極短）
                    hs = st + e * beat / 2
                    m = int(0.05 * SR); tt = np.arange(m) / SR
                    hh = rng.standard_normal(m)
                    hh = hh - onepole_lp(hh, 7000)
                    place(drums, hh * np.exp(-tt * 90) * (0.05 if e else 0.035) * dz, hs, pan=0.25)

    # 尾段上揚：最後一個 bar 開頭疊一顆柔和低音 impact
    m = int(2.0 * SR); tt = np.arange(m) / SR
    imp = np.sin(2 * np.pi * (40 + 40 * np.exp(-tt * 5)) * tt) * np.exp(-tt * 2.2) * 0.25
    place(drums, imp, outro)

    dry = pad + arp * 0.9 + bass + drums
    wet = reverb(pad + arp, 2.6, rng)
    mix = dry + wet * 0.32
    # 側鏈感：鋪底在大鼓處輕微下壓，讓節奏有呼吸
    if cfg["drums"] > 0.5:
        t = np.arange(N) / SR
        ph = np.mod(t - intro_end, beat * 2) / (beat * 2)
        duck = 1 - 0.18 * np.exp(-ph * 9) * ((t > intro_end) & (t < outro))
        mix *= duck[:, None]
    # 頭尾淡入淡出
    t = np.arange(N) / SR
    mix *= np.clip(t / 0.8, 0, 1)[:, None]
    mix *= np.clip((total - t) / 2.8, 0, 1)[:, None]
    mix = np.tanh(mix * 1.4) / 1.4  # 柔和飽和，避免削波
    mix /= max(1e-6, np.max(np.abs(mix))) / 0.89
    return mix[: int(duration * SR)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--duration", type=float, required=True, help="影片總秒數")
    ap.add_argument("--mood", choices=sorted(MOODS), default="tech")
    ap.add_argument("--seed", default="doflab", help="通常填專案 id，讓每支配樂略有不同")
    a = ap.parse_args()
    audio = compose(a.duration, a.mood, a.seed)
    pcm = (np.clip(audio, -1, 1) * 32767).astype("<i2")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(a.out), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"✓ {a.out}  {a.duration:.1f}s  mood={a.mood}  seed={a.seed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
