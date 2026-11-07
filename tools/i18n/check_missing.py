#!/usr/bin/env python3
"""對照 tools/i18n/keys.json（node tools/i18n/extract_keys.js 產生）與 assets/i18n/en.js，列出每頁還沒有英文的字串。

  node tools/i18n/extract_keys.js && python3 tools/i18n/check_missing.py [--json out.json]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dict import load  # noqa: E402

KEYS = Path(__file__).resolve().parent / "keys.json"


def main() -> int:
    d = load()
    strings, rules = d["strings"], [re.compile(r[0]) for r in d.get("rules", [])]
    pages = json.loads(KEYS.read_text(encoding="utf-8"))
    missing: dict[str, list[str]] = {}
    for page, v in pages.items():
        for k in v["strings"] + v["attrs"] + v["head"]:
            if k in strings or any(r.search(k) for r in rules):
                continue
            missing.setdefault(page, []).append(k)
    total = sum(len(v) for v in missing.values())
    for page, ks in missing.items():
        print(f"== {page}: {len(ks)} missing")
        for k in ks:
            print("   ", k[:120])
    if "--json" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--json") + 1])
        out.write_text(json.dumps({k: "" for ks in missing.values() for k in ks}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{total} missing across {len(missing)} pages" if total else "✓ all page strings have English")
    return 1 if total else 0


if __name__ == "__main__":
    main()
