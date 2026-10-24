#!/usr/bin/env python3
"""doflab.cc 內容更新工具 —— 專案動畫、研究發表、公告訊息。

所有指令都在網站根目錄（LabPagesCowork）下執行，只改 JSON 與快取版本號，
頁面由 JSON 自動渲染。執行後請跑 scripts/validate_public_content.py。

專案動畫（showcase.json；影片與封面需先用 make_web.py 產生）
  python tools/showcase/site_update.py project add --id windai-lab \
      --title "風力發電 AI 研究協作平台" --tagline "多代理串起 SCADA 到論文報告" \
      --category wind_energy --source-type repo --source-url https://github.com/dofliu/windAI-Lab \
      --tech Python --tech "LLM Agents" [--date 2026-10-25] [--featured]
  python tools/showcase/site_update.py project remove --id windai-lab
  python tools/showcase/site_update.py project list

研究發表（publications.json）
  python tools/showcase/site_update.py pub add --group journal --json '{"year":"2026","title":"...", ...}'
  python tools/showcase/site_update.py pub list --group journal [--limit 5]

公告訊息（announcements.json）
  python tools/showcase/site_update.py news add --title "..." --body "..." \
      [--date 2026-10-25] [--tag 活動] [--link https://...] [--pinned]
  python tools/showcase/site_update.py news remove --id 2026-10-25-xxxx
  python tools/showcase/site_update.py news list
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TODAY = dt.date.today().isoformat()
CATEGORIES = ("wind_energy", "industrial_ai", "rag_knowledge", "edtech", "mcp_tools", "personal_tools", "other")
SOURCE_TYPES = ("repo", "document", "link", "other")
PUB_GROUPS = ("journal", "conference", "preprint", "accepted", "patent", "award")
TAGLINE_MAX = 20


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def save(name: str, data: dict) -> None:
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    bump_cache(name)
    print(f"✓ 已寫入 {name}")


def bump_cache(name: str) -> None:
    """把頁面裡 `name?v=YYYYMMDD` 的快取版本改成今天，避免訪客看到舊資料。"""
    stamp = TODAY.replace("-", "")
    pat = re.compile(re.escape(name) + r"\?v=\d{8}")
    for f in list(ROOT.glob("*.html")) + [ROOT / "assets" / "editorial.js"]:
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8")
        n = pat.sub(f"{name}?v={stamp}", t)
        if n != t:
            f.write_text(n, encoding="utf-8")


def check_date(s: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        sys.exit(f"日期格式需為 YYYY-MM-DD：{s}")
    return s


def check_url(s: str | None) -> str:
    if s and not s.startswith("https://"):
        sys.exit(f"連結必須是 https:// 開頭：{s}")
    return s or ""


# ───────────────────────── 專案動畫 ─────────────────────────
def video_duration(path: Path) -> float:
    import subprocess
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "default=nw=1:nk=1", str(path)], capture_output=True, text=True).stdout.strip()
    return round(float(out), 1) if out else 0.0


def project_add(a) -> None:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,60}", a.id):
        sys.exit("id 只能用小寫英數與 -")
    if len(a.tagline) > TAGLINE_MAX:
        sys.exit(f"簡介 {len(a.tagline)} 字，超過 {TAGLINE_MAX} 字上限：{a.tagline}")
    for ext in ("mp4", "jpg"):
        if not (ROOT / "assets" / "showcase" / f"{a.id}.{ext}").exists():
            sys.exit(f"找不到 assets/showcase/{a.id}.{ext}，請先執行 make_web.py")
    data = load("showcase.json")
    item = {
        "id": a.id,
        "title": a.title,
        "tagline": a.tagline,
        "category": a.category,
        "date": check_date(a.date or TODAY),
        "video": f"assets/showcase/{a.id}.mp4",
        "cover": f"assets/showcase/{a.id}.jpg",
        "source_type": a.source_type,
        "source_url": check_url(a.source_url),
        "tech": a.tech or [],
        "duration": video_duration(ROOT / "assets" / "showcase" / f"{a.id}.mp4"),
    }
    if a.featured:
        item["featured"] = True
    items = [p for p in data["items"] if p["id"] != a.id]
    replaced = len(items) != len(data["items"])
    items.insert(0, item)
    items.sort(key=lambda p: p["date"], reverse=True)
    items.sort(key=lambda p: not p.get("featured", False))
    data["items"], data["updated"] = items, TODAY
    save("showcase.json", data)
    print(("↻ 更新" if replaced else "＋ 新增") + f"專案：{a.title}（共 {len(items)} 個）")


def project_remove(a) -> None:
    data = load("showcase.json")
    n = len(data["items"])
    data["items"] = [p for p in data["items"] if p["id"] != a.id]
    if len(data["items"]) == n:
        sys.exit(f"找不到 id：{a.id}")
    data["updated"] = TODAY
    save("showcase.json", data)
    print(f"－ 已移除 {a.id}（影片檔保留在 assets/showcase/，要刪請手動 git rm）")


def project_list(a) -> None:
    for p in load("showcase.json")["items"]:
        print(f"{p['date']}  {p['id']:<28} {p['title']} — {p['tagline']}")


# ───────────────────────── 研究發表 ─────────────────────────
def pub_add(a) -> None:
    rec = json.loads(a.json)
    if not rec.get("title") or not rec.get("year"):
        sys.exit("至少需要 year 與 title")
    check_url(rec.get("source_url"))
    if not rec.get("source_url"):
        sys.exit("需要 source_url（公開來源連結，網站驗證規則要求每筆都有）")
    g = a.group
    status = rec.get("status") or {"journal": "published", "conference": "published", "preprint": "preprint",
                                     "accepted": "accepted", "patent": "granted", "award": "awarded"}[g]
    if re.search(r"under review|submitted|draft", status, re.I):
        sys.exit("審查中／投稿中／草稿不公開列出")
    if g == "journal" and status != "published":
        sys.exit("期刊只收已正式出版（published）；已接受請用 --group accepted，預印本用 preprint")
    if g in ("preprint", "accepted"):
        status = g
    rec["status"] = status
    rec.setdefault("verification", "publisher_verified" if rec.get("doi") else "personal_site_record")
    data = load("publications.json")
    items = data[g]
    key = (str(rec["year"]), rec["title"])
    items = [p for p in items if (str(p["year"]), p["title"]) != key]
    items.insert(0, rec)
    items.sort(key=lambda p: str(p["year"]), reverse=True)
    data[g], data["_updated"] = items, TODAY
    save("publications.json", data)
    update_home_stats(data)
    print(f"＋ {g}：{rec['title'][:60]}（該類共 {len(items)} 筆）")


def update_home_stats(pubs: dict) -> None:
    idx = ROOT / "index.html"
    t = idx.read_text(encoding="utf-8")
    for label, g in (("期刊著作紀錄", "journal"), ("研討會論文紀錄", "conference")):
        t = re.sub(r'(<div class="stat__no">)\d+(</div><div class="stat__label">' + label + ")",
                   lambda m: f"{m.group(1)}{len(pubs[g])}{m.group(2)}", t)
    idx.write_text(t, encoding="utf-8")


def pub_list(a) -> None:
    for p in load("publications.json")[a.group][: a.limit]:
        print(f"{p['year']}  {p['title'][:90]}")


# ───────────────────────── 公告訊息 ─────────────────────────
def news_add(a) -> None:
    date = check_date(a.date or TODAY)
    nid = f"{date}-{hashlib.sha1(a.title.encode()).hexdigest()[:6]}"
    data = load("announcements.json")
    item = {"id": nid, "date": date, "title": a.title, "body": a.body or "",
            "tag": a.tag or "公告", "link": check_url(a.link)}
    if a.pinned:
        item["pinned"] = True
    items = [n for n in data["items"] if n["id"] != nid]
    items.append(item)
    items.sort(key=lambda n: n["date"], reverse=True)
    data["items"], data["updated"] = items, TODAY
    save("announcements.json", data)
    print(f"＋ 公告 {nid}：{a.title}")


def news_remove(a) -> None:
    data = load("announcements.json")
    n = len(data["items"])
    data["items"] = [x for x in data["items"] if x["id"] != a.id]
    if len(data["items"]) == n:
        sys.exit(f"找不到公告 id：{a.id}")
    data["updated"] = TODAY
    save("announcements.json", data)


def news_list(a) -> None:
    for n in load("announcements.json")["items"]:
        print(f"{n['id']:<20} {'📌' if n.get('pinned') else '  '} {n['title']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="doflab.cc 內容更新")
    sub = ap.add_subparsers(dest="kind", required=True)

    pr = sub.add_parser("project").add_subparsers(dest="op", required=True)
    p = pr.add_parser("add")
    p.add_argument("--id", required=True); p.add_argument("--title", required=True)
    p.add_argument("--tagline", required=True, help=f"卡片簡介，≤{TAGLINE_MAX} 字")
    p.add_argument("--category", choices=CATEGORIES, default="other")
    p.add_argument("--source-type", choices=SOURCE_TYPES, default="repo")
    p.add_argument("--source-url"); p.add_argument("--date")
    p.add_argument("--tech", action="append"); p.add_argument("--featured", action="store_true")
    p.set_defaults(fn=project_add)
    p = pr.add_parser("remove"); p.add_argument("--id", required=True); p.set_defaults(fn=project_remove)
    pr.add_parser("list").set_defaults(fn=project_list)

    pu = sub.add_parser("pub").add_subparsers(dest="op", required=True)
    p = pu.add_parser("add"); p.add_argument("--group", choices=PUB_GROUPS, required=True)
    p.add_argument("--json", required=True); p.set_defaults(fn=pub_add)
    p = pu.add_parser("list"); p.add_argument("--group", choices=PUB_GROUPS, default="journal")
    p.add_argument("--limit", type=int, default=10); p.set_defaults(fn=pub_list)

    nw = sub.add_parser("news").add_subparsers(dest="op", required=True)
    p = nw.add_parser("add"); p.add_argument("--title", required=True); p.add_argument("--body")
    p.add_argument("--date"); p.add_argument("--tag"); p.add_argument("--link")
    p.add_argument("--pinned", action="store_true"); p.set_defaults(fn=news_add)
    p = nw.add_parser("remove"); p.add_argument("--id", required=True); p.set_defaults(fn=news_remove)
    nw.add_parser("list").set_defaults(fn=news_list)

    a = ap.parse_args()
    a.fn(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
