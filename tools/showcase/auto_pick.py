#!/usr/bin/env python3
"""每日排程用：從「最近有活動」的 repo 往下挑第一個還沒有專案動畫的。

  python tools/showcase/auto_pick.py repos.json            # 印出下一個候選（JSON）
  python tools/showcase/auto_pick.py repos.json --list 10  # 印出前 10 個候選，方便檢查
  python tools/showcase/auto_pick.py --skip owner/repo --reason "README 太少，無法介紹"   # 記錄跳過

repos.json：list_repos 工具的輸出（{"repos":[{full_name, visibility, pushed_at, fork, ...}]}）原樣存檔即可。

排除規則：
  1. showcase.json 已有該 repo（比對 item.repo，或 source_url 指向該 repo；不分大小寫）
  2. fork 的 repo
  3. tools/showcase/auto_skip.json 裡的 repo（網站本身、舊首頁、內容不足等，附原因）
依 pushed_at 由新到舊排序後取第一個。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP = ROOT / "tools" / "showcase" / "auto_skip.json"


def norm(s: str) -> str:
    return s.strip().lower().rstrip("/").removesuffix(".git")


def done_repos() -> set[str]:
    out = set()
    for it in json.loads((ROOT / "showcase.json").read_text(encoding="utf-8"))["items"]:
        if it.get("repo"):
            out.add(norm(it["repo"]))
        url = it.get("source_url") or ""
        if "github.com/" in url:
            parts = url.split("github.com/", 1)[1].split("/")
            if len(parts) >= 2:
                out.add(norm(f"{parts[0]}/{parts[1]}"))
    return out


def load_skip() -> dict:
    return json.loads(SKIP.read_text(encoding="utf-8")) if SKIP.exists() else {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repos", nargs="?", type=Path)
    ap.add_argument("--list", type=int, default=0)
    ap.add_argument("--skip", help="把 owner/repo 加入跳過清單")
    ap.add_argument("--reason", default="")
    a = ap.parse_args()

    if a.skip:
        sk = load_skip()
        sk[norm(a.skip)] = {"reason": a.reason or "未註明", "date": dt.date.today().isoformat()}
        SKIP.write_text(json.dumps(sk, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"＋ 跳過 {a.skip}：{a.reason}")
        return 0

    if not a.repos:
        sys.exit("需要 repos.json")
    data = json.loads(a.repos.read_text(encoding="utf-8"))
    repos = data["repos"] if isinstance(data, dict) else data
    done, skip = done_repos(), load_skip()
    cands = [r for r in repos
             if not r.get("fork")
             and norm(r["full_name"]) not in done
             and norm(r["full_name"]) not in skip]
    cands.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
    if not cands:
        print(json.dumps({"next": None, "message": "所有 repo 都已有動畫或在跳過清單"}, ensure_ascii=False))
        return 0
    if a.list:
        for r in cands[: a.list]:
            print(f"{r.get('pushed_at','')[:10]}  {r['visibility']:<8} {r['full_name']}")
        return 0
    r = cands[0]
    print(json.dumps({"next": r["full_name"], "visibility": r.get("visibility"), "pushed_at": r.get("pushed_at"),
                      "remaining": len(cands)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
