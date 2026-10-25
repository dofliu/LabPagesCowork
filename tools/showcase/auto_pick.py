#!/usr/bin/env python3
"""每日排程用：從「最近有活動」的 repo 往下挑第一個還沒有專案動畫的。

排程 session 沒有 list_repos／add_repo 工具，GitHub 帳號層級 API 也被擋，所以：
  - repo 名冊存在 tools/showcase/repos.json（visibility、fork、pushed_at）
  - --refresh 時即時更新每個 repo 的最近活動時間：
      公開 repo → 匿名淺層 clone（只抓 commit，不抓檔案）讀最新 commit 時間
      私人 repo → gh api repos/<owner>/<repo>（排程任務建立時已附加為唯讀）
    取不到就沿用名冊裡的舊時間。

用法：
  python tools/showcase/auto_pick.py --refresh                 # 更新活動時間 → 印出下一個候選（JSON）
  python tools/showcase/auto_pick.py --list 10                 # 前 10 個候選
  python tools/showcase/auto_pick.py --merge list_repos.json   # 互動 session 用：把 list_repos 輸出併入名冊（新 repo 會加進來）
  python tools/showcase/auto_pick.py --skip owner/repo --reason "README 太少"
  私人 repo：名單「不」存進本 repo（網站 repo 是公開的），由排程任務的指示用 --private 傳入：
    python tools/showcase/auto_pick.py --refresh --private dofliu/a,dofliu/b,...
  showcase.json／auto_skip.json 對私人 repo 只記 sha256 雜湊（repo_hash / "h:<hash>"），不記名稱。

排除：showcase.json 已有（比對 item.repo 與 source_url）、fork、tools/showcase/auto_skip.json。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "tools" / "showcase"
ROSTER = HERE / "repos.json"
SKIP = HERE / "auto_skip.json"


def norm(s: str) -> str:
    return s.strip().lower().rstrip("/").removesuffix(".git")


def jload(p: Path, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def jsave(p: Path, data) -> None:
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rhash(name: str) -> str:
    import hashlib
    return hashlib.sha256(norm(name).encode()).hexdigest()[:16]


def done_repos() -> set[str]:
    """回傳已做過的 key：公開 repo 用名稱，私人 repo 用 'h:<hash>'。"""
    out = set()
    for it in jload(ROOT / "showcase.json", {"items": []})["items"]:
        if it.get("repo"):
            out.add(norm(it["repo"]))
        if it.get("repo_hash"):
            out.add("h:" + it["repo_hash"])
        url = it.get("source_url") or ""
        if "github.com/" in url:
            parts = url.split("github.com/", 1)[1].split("/")
            if len(parts) >= 2:
                out.add(norm(f"{parts[0]}/{parts[1]}"))
    return out


def live_pushed(r: dict) -> str | None:
    name = r["full_name"]
    try:
        if r.get("visibility") == "private":
            p = subprocess.run(["gh", "api", f"repos/{name}", "--jq", ".pushed_at"],
                               capture_output=True, text=True, timeout=30)
            v = p.stdout.strip()
            return v if p.returncode == 0 and v.startswith("20") else None
        with tempfile.TemporaryDirectory() as td:
            p = subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout",
                                "--bare", f"https://github.com/{name}", f"{td}/r"],
                               capture_output=True, text=True, timeout=60)
            if p.returncode != 0:
                return None
            v = subprocess.run(["git", "-C", f"{td}/r", "log", "-1", "--format=%cI"],
                               capture_output=True, text=True).stdout.strip()
            if not v:
                return None
            return dt.datetime.fromisoformat(v).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None


def refresh(roster: list[dict]) -> tuple[int, int]:
    todo = [r for r in roster if not r.get("fork")]
    with ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(live_pushed, todo))
    ok = 0
    for r, v in zip(todo, res):
        if v:
            r["pushed_at"], ok = v, ok + 1
    return ok, len(todo)


def key(r: dict) -> str:
    return "h:" + rhash(r["full_name"]) if r.get("visibility") == "private" else norm(r["full_name"])


def candidates(roster: list[dict]) -> list[dict]:
    done, skip = done_repos(), jload(SKIP, {})
    c = [r for r in roster if not r.get("fork") and key(r) not in done and key(r) not in skip]
    c.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
    return c


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="先即時更新活動時間")
    ap.add_argument("--list", type=int, default=0)
    ap.add_argument("--merge", type=Path, help="list_repos 工具輸出的 JSON")
    ap.add_argument("--skip", help="把 owner/repo 加入跳過清單")
    ap.add_argument("--private", default="", help="私人 repo 名單（逗號分隔），只在執行時使用、不存檔")
    ap.add_argument("--hash", help="印出某 repo 的雜湊（私人 repo 寫入 showcase.json 用）")
    ap.add_argument("--reason", default="")
    a = ap.parse_args()

    private = [norm(x) for x in a.private.split(",") if x.strip()]
    if a.hash:
        print(rhash(a.hash))
        return 0
    if a.skip:
        sk = jload(SKIP, {})
        is_priv = norm(a.skip) in private
        k = "h:" + rhash(a.skip) if is_priv else norm(a.skip)
        sk[k] = {"reason": a.reason or "未註明", "date": dt.date.today().isoformat()}
        jsave(SKIP, sk)
        print(f"＋ 跳過 {'（私人 repo，僅存雜湊）' if is_priv else a.skip}：{a.reason}")
        return 0

    roster = jload(ROSTER, {"repos": []})
    roster["repos"] = [r for r in roster["repos"] if r.get("visibility") != "private"]  # 名冊只存公開 repo
    repos = roster["repos"]
    priv_recs = [{"full_name": n, "visibility": "private", "fork": False, "pushed_at": ""} for n in private]

    if a.merge:
        data = jload(a.merge, {})
        src = data["repos"] if isinstance(data, dict) else data
        idx = {norm(r["full_name"]): r for r in repos}
        added = 0
        for r in src:
            if r.get("visibility") == "private":
                continue  # 私人 repo 不寫進公開名冊
            k = norm(r["full_name"])
            rec = {"full_name": r["full_name"], "visibility": r.get("visibility", "public"),
                   "fork": bool(r.get("fork")), "pushed_at": r.get("pushed_at", "")}
            if k in idx:
                idx[k].update(rec)
            else:
                repos.append(rec); added += 1
        roster["updated"] = dt.date.today().isoformat()
        jsave(ROSTER, roster)
        print(f"✓ 名冊 {len(repos)} 個 repo（新增 {added}）")
        return 0

    if a.refresh:
        ok, n = refresh(repos + priv_recs)
        roster["refreshed"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        jsave(ROSTER, roster)
        print(f"[refresh] 更新 {ok}/{n} 個 repo 的活動時間", file=sys.stderr)

    c = candidates(repos + [r for r in priv_recs if r["pushed_at"] or not a.refresh])
    if a.list:
        for r in c[: a.list]:
            print(f"{(r.get('pushed_at') or '')[:10]}  {r.get('visibility',''):<8} {r['full_name']}")
        return 0
    if not c:
        print(json.dumps({"next": None, "message": "所有 repo 都已有動畫或在跳過清單"}, ensure_ascii=False))
        return 0
    r = c[0]
    print(json.dumps({"next": r["full_name"], "visibility": r.get("visibility"), "pushed_at": r.get("pushed_at"),
                      "remaining": len(c)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
