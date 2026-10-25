#!/usr/bin/env python3
"""論文動畫：由一份內容 JSON 自動產生 5 景 HTML ＋ storyboard.json（約 30 秒）。

  python tools/showcase/make_paper_scenes.py tools/showcase/papers/<id>/paper.json

paper.json 欄位（文字一律繁體中文、短句；數字只放出版社頁面明列的）：
{
  "id": "sr2026-rag-transfer",
  "kicker": "SCIENTIFIC REPORTS · 2026",          # 期刊／年份（英文大寫）
  "title_zh": ["跨來源檢索遷移", "與語料語意豐富度"],  # 中文說明標題，1–2 行，每行 ≤12 字
  "title_en": "Asymmetric cross-source retrieval ...", # 原文標題（小字）
  "hook": "一句話說明這篇在解決什麼",                 # ≤26 字
  "problem": {"heading": "≤14 字", "items": [["🛠️", "≤16 字"], ...3 項]},
  "method":  {"heading": "≤14 字", "steps": ["≤6 字", ...3–5 步], "note": "≤30 字（可省略）"},
  "results": {"heading": "≤14 字", "items": [{"value": "+48.2%", "label": "≤14 字"}, ...2–3 項], "note": "≤34 字（可省略）"},
  "cta": {"venue": "期刊全名", "authors": "作者列", "doi": "10.xxxx/...", "chips": ["≤8 字", ...3 項]}
}
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = (HERE / "scene_template.html").read_text(encoding="utf-8")
e = html.escape


def scene(title: str, dur: float, css: str, body: str, particles: bool = True) -> str:
    t = TEMPLATE.replace("<title>SceneXX</title>", f"<title>{e(title)}</title>")
    t = t.replace("/* ▼▼ 本景專屬 CSS ▼▼ */\n", "/* ▼▼ 本景專屬 CSS ▼▼ */\n" + css + "\n")
    a = t.index("<!-- ▼▼ 本景內容 ▼▼ -->")
    b = t.index("<!-- ▲▲ 本景內容 ▲▲ -->") + len("<!-- ▲▲ 本景內容 ▲▲ -->")
    t = t[:a] + body + t[b:]
    t = t.replace('<div class="stage" style="z-index:2">', f'<div class="stage" style="z-index:2;--dur:{dur}s">')
    if not particles:
        a = t.index('<canvas id="fx"')
        b = t.index("</script>", a) + len("</script>\n")
        t = t[:a] + t[b:]
    return t


HEAD = """
.hd{display:flex;flex-direction:column;align-items:center}
.hd .h1{font-size:84px;margin-top:16px}
"""


def s1(p: dict) -> str:
    lines = p["title_zh"] if isinstance(p["title_zh"], list) else [p["title_zh"]]
    size = 128 if max(len(x) for x in lines) <= 9 else 108
    tl = "".join(f'<div class="h1 pop" style="--d:{0.5 + i * 0.25:.2f}s;font-size:{size}px">{e(x)}</div>' for i, x in enumerate(lines))
    css = """
.ring{position:absolute;left:50%;top:50%;width:980px;height:980px;margin:-490px 0 0 -490px;border-radius:50%;
 border:2px solid rgba(217,173,91,.16);animation:spin 40s linear infinite}
.ring:before{content:"";position:absolute;inset:70px;border-radius:50%;border:1.5px dashed rgba(210,96,47,.2)}
@keyframes spin{to{transform:rotate(360deg)}}
.paper{display:inline-flex;gap:14px;align-items:center;font-size:28px;font-weight:700;color:#f3a57e;letter-spacing:.12em;
 padding:12px 30px;border-radius:999px;border:1.5px solid rgba(210,96,47,.45);background:rgba(210,96,47,.10);white-space:nowrap}
.en{max-width:1500px;margin-top:34px;font-size:30px;line-height:1.45;color:rgba(246,239,227,.55);text-align:center;font-style:italic}
.hook{margin-top:30px;font-size:40px;color:rgba(246,239,227,.86);text-align:center}
"""
    body = f"""
 <div class="ring"></div>
 <div class="paper in" style="--d:.1s">📄 研究論文 · {e(p['kicker'])}</div>
 <div style="margin-top:34px;display:flex;flex-direction:column;align-items:center;gap:6px">{tl}</div>
 <div class="hook in" style="--d:1.4s">{e(p['hook'])}</div>
 <div class="en in" style="--d:1.9s">{e(p['title_en'])}</div>
"""
    return scene("開場", 7, css, body)


def s2(p: dict) -> str:
    items = p["problem"]["items"][:3]
    cards = "".join(
        f'<div class="pc card in" style="--d:{0.9 + i * 0.35:.2f}s"><div class="ic">{e(ic)}</div><div class="tx">{e(tx)}</div></div>'
        for i, (ic, tx) in enumerate(items))
    css = HEAD + """
.row{display:flex;gap:44px;margin-top:80px}
.pc{width:500px;min-height:330px;padding:48px 42px;display:flex;flex-direction:column;align-items:flex-start;gap:26px}
.pc .ic{font-size:76px;line-height:1}
.pc .tx{font-size:42px;font-weight:700;line-height:1.4;text-wrap:balance;word-break:keep-all}
"""
    body = f"""
 <div class="hd"><div class="kicker in" style="--d:.1s">THE PROBLEM · 研究問題</div>
 <div class="h1 in" style="--d:.3s">{e(p['problem']['heading'])}</div></div>
 <div class="row">{cards}</div>
"""
    return scene("問題", 6.5, css, body, particles=False)


def s3(p: dict) -> str:
    steps = p["method"]["steps"][:5]
    w = {3: 380, 4: 320, 5: 270}.get(len(steps), 300)
    parts = []
    for i, s in enumerate(steps):
        lit = 1.3 + i * 0.55
        if i:
            parts.append(f'<div class="ar" style="--l:{lit - 0.25:.2f}s"></div>')
        parts.append(f'<div class="st" style="--l:{lit:.2f}s;width:{w}px"><span class="n">{i + 1:02d}</span>{e(s)}</div>')
    note = p["method"].get("note")
    nt = f'<div class="note in" style="--d:{1.6 + len(steps) * 0.55:.2f}s">{e(note)}</div>' if note else ""
    css = HEAD + """
.pipe{display:flex;align-items:stretch;margin-top:90px}
.st{padding:34px 18px;text-align:center;font-size:38px;font-weight:700;border-radius:20px;line-height:1.3;
 display:flex;flex-direction:column;justify-content:center;text-wrap:balance;
 background:rgba(40,31,23,.9);border:1.5px solid rgba(217,173,91,.2);color:rgba(246,239,227,.42);animation:lit .5s ease-out forwards;animation-delay:var(--l)}
.st{word-break:keep-all}
.st .n{display:block;font-size:24px;letter-spacing:.2em;color:var(--gold);margin-bottom:10px;opacity:.8}
@keyframes lit{to{background:linear-gradient(165deg,rgba(210,96,47,.35),rgba(80,35,15,.6));border-color:rgba(240,150,100,.75);color:#fff;box-shadow:0 0 40px rgba(210,96,47,.33)}}
.ar{width:50px;height:3px;background:rgba(217,173,91,.25);position:relative;flex:none;align-self:center}
.ar:after{content:"";position:absolute;inset:0;background:var(--gold);transform:scaleX(0);transform-origin:left;animation:fill .35s ease-out forwards;animation-delay:var(--l)}
@keyframes fill{to{transform:scaleX(1)}}
.note{font-size:36px;color:rgba(246,239,227,.78);margin-top:80px;text-align:center;max-width:1500px}
"""
    body = f"""
 <div class="hd"><div class="kicker in" style="--d:.1s">THE METHOD · 研究方法</div>
 <div class="h1 in" style="--d:.3s">{e(p['method']['heading'])}</div></div>
 <div class="pipe in" style="--d:.8s">{''.join(parts)}</div>
 {nt}
"""
    return scene("方法", 6.5, css, body, particles=False)


def vsize(v: str) -> int:
    w = sum(1.0 if ord(c) > 0x2E80 else 0.58 for c in v)  # 中文全形＝1、英數＝0.58
    return 96 if w <= 5 else 80 if w <= 6.2 else 66 if w <= 7.5 else 56


def s4(p: dict) -> str:
    items = p["results"]["items"][:3]
    w = 520 if len(items) == 3 else 640
    cards = "".join(
        f'<div class="rc card in" style="--d:{0.8 + i * 0.4:.2f}s;width:{w}px">'
        f'<div class="v pop" style="--d:{1.1 + i * 0.4:.2f}s;font-size:{vsize(it["value"])}px">{e(it["value"])}</div><div class="lb">{e(it["label"])}</div></div>'
        for i, it in enumerate(items))
    note = p["results"].get("note")
    nt = f'<div class="note in" style="--d:{1.4 + len(items) * 0.4:.2f}s">{e(note)}</div>' if note else ""
    css = HEAD + """
.row{display:flex;gap:44px;margin-top:80px}
.rc{min-height:330px;padding:46px 40px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:22px}
.rc .v{font-size:96px;font-weight:900;line-height:1.05;white-space:nowrap;
 background:linear-gradient(100deg,#fff8ec 10%,#f0c98a 50%,#e58a5c 90%);-webkit-background-clip:text;background-clip:text;color:transparent}
.rc .lb{font-size:38px;font-weight:700;line-height:1.35;color:rgba(246,239,227,.9);text-wrap:balance}
.note{font-size:32px;color:rgba(246,239,227,.62);margin-top:60px;text-align:center;max-width:1560px}
"""
    body = f"""
 <div class="hd"><div class="kicker in" style="--d:.1s">KEY FINDINGS · 主要發現</div>
 <div class="h1 in" style="--d:.3s">{e(p['results']['heading'])}</div></div>
 <div class="row">{cards}</div>
 {nt}
"""
    return scene("結果", 6.5, css, body, particles=False)


def s5(p: dict) -> str:
    c = p["cta"]
    chips = "".join(f'<div class="chip in" style="--d:{1.0 + i * 0.2:.1f}s">{e(x)}</div>' for i, x in enumerate(c["chips"][:3]))
    lines = p["title_zh"] if isinstance(p["title_zh"], list) else [p["title_zh"]]
    full = lines[0]
    for x in lines[1:]:
        full += (" " if (full[-1:].isascii() and full[-1:].isalnum() and x[:1].isascii()) else "") + x
    tsize = 104 if len(full) <= 14 else 88 if len(full) <= 18 else 76
    css = """
.chips{display:flex;gap:26px;margin-top:50px}
.venue{margin-top:56px;font-size:38px;font-weight:700;color:var(--gold);text-align:center;max-width:1600px}
.au{margin-top:16px;font-size:30px;color:rgba(246,239,227,.75);text-align:center;max-width:1600px}
.doi{margin-top:26px;font-size:34px;color:rgba(246,239,227,.9);font-family:"DejaVu Sans Mono",monospace}
.doi b{color:#f3a57e}
.by{margin-top:24px;font-size:28px;color:rgba(246,239,227,.5)}
"""
    body = f"""
 <div class="kicker in" style="--d:.1s">DOF LAB · 研究發表</div>
 <div class="h1 pop glow" style="--d:.4s;margin-top:26px;font-size:{tsize}px;max-width:1700px">{e(full)}</div>
 <div class="chips">{chips}</div>
 <div class="venue in" style="--d:1.7s">{e(c['venue'])}</div>
 <div class="au in" style="--d:1.9s">{e(c['authors'])}</div>
 <div class="doi in" style="--d:2.1s">doi.org/<b>{e(c['doi'])}</b></div>
 <div class="by in" style="--d:2.3s">國立勤益科技大學 智慧自動化工程系 · 風電運維自動化技術研究室</div>
"""
    return scene("結尾", 6, css, body)


def main() -> int:
    spec_path = Path(sys.argv[1])
    p = json.loads(spec_path.read_text(encoding="utf-8"))
    out = spec_path.parent
    files = [("scene01_open.html", s1, 7, "fade"), ("scene02_problem.html", s2, 6.5, "smoothleft"),
             ("scene03_method.html", s3, 6.5, "circleopen"), ("scene04_results.html", s4, 6.5, "fade"),
             ("scene05_cta.html", s5, 6, None)]
    scenes = []
    for fn, fnc, dur, tr in files:
        (out / fn).write_text(fnc(p), encoding="utf-8")
        sc = {"file": fn, "duration": dur}
        if tr:
            sc["transition"] = tr
        scenes.append(sc)
    (out / "storyboard.json").write_text(json.dumps({"fps": 30, "width": 1920, "height": 1080, "xfade": 0.6,
                                                     "scenes": scenes}, indent=2), encoding="utf-8")
    print(f"✓ {out}：5 景 + storyboard.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
