#!/usr/bin/env python3
"""讀寫 assets/i18n/en.js（英文字典）。

  python3 tools/i18n/dict.py get "中文字串"            # 查
  python3 tools/i18n/dict.py set "中文字串" "English"   # 新增／覆寫一筆
  python3 tools/i18n/dict.py merge <file.json>         # 批次合併 {"中文": "English", ...}
  python3 tools/i18n/dict.py count

字典格式：window.DOF_I18N_EN = {"strings": {...}, "rules": [[regex, replacement], ...]};
key = 元素的中文 innerHTML（空白正規化後，見 assets/i18n.js）；rules 為找不到精確 key 時的正規式後援。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILE = ROOT / "assets" / "i18n" / "en.js"
PREFIX = "window.DOF_I18N_EN = "


def load() -> dict:
    if not FILE.exists():
        return {"strings": {}, "rules": []}
    t = FILE.read_text(encoding="utf-8").strip()
    assert t.startswith(PREFIX), FILE
    t = t[len(PREFIX):].rstrip(";")
    return json.loads(t)


def save(d: dict) -> None:
    d["strings"] = dict(sorted(d["strings"].items(), key=lambda kv: (len(kv[0]), kv[0])))
    FILE.parent.mkdir(parents=True, exist_ok=True)
    FILE.write_text(PREFIX + json.dumps(d, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def merge(mapping: dict) -> int:
    d = load()
    n = 0
    for k, v in mapping.items():
        k = norm(k)
        if d["strings"].get(k) != v:
            d["strings"][k] = v
            n += 1
    save(d)
    return n


def main() -> int:
    a = sys.argv[1:]
    if not a or a[0] == "count":
        d = load(); print(f"{len(d['strings'])} strings, {len(d.get('rules', []))} rules"); return 0
    if a[0] == "get":
        print(load()["strings"].get(norm(a[1]), "(none)")); return 0
    if a[0] == "set":
        merge({a[1]: a[2]}); print("✓"); return 0
    if a[0] == "merge":
        n = merge(json.loads(Path(a[1]).read_text(encoding="utf-8"))); print(f"✓ merged {n} entries"); return 0
    print(__doc__); return 1


if __name__ == "__main__":
    sys.exit(main())
