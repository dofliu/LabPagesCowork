#!/usr/bin/env python3
"""
LabPagesCowork — 統一管理入口
================================
一個指令管理所有研究室網站更新：專案掃描、部落格、儀表板部署。

用法:
    python scripts/update_all.py                 # 掃描專案 + 部署儀表板
    python scripts/update_all.py --scan          # 只掃描專案
    python scripts/update_all.py --deploy        # 只部署（不掃描）
    python scripts/update_all.py --blog          # 只更新 blog.html 文章列表
    python scripts/update_all.py --all           # 全部：掃描 + 部落格 + 部署
    python scripts/update_all.py --push          # 加上此旗標會自動 git push

作者: 劉瑞弘研究室 (DOF Lab)
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────
LABPAGES_DIR = Path(__file__).parent.parent.resolve()  # MCP/LabPagesCowork/
PROJECT_ROOT = LABPAGES_DIR.parent.parent.resolve()     # Project_CodingSimulation/
POSTS_DIR = LABPAGES_DIR / "posts"
GITHUB_REPO = "https://github.com/dofliu/LabPagesCowork.git"

# Files to copy from Project_CodingSimulation → LabPagesCowork
DEPLOY_FILES = {
    "RESEARCH_DASHBOARD.html": "dashboard.html",
    "RESEARCH_MAP.html": "map.html",
    ".research_os_data.json": "data.json",
    ".research_os_cache.json": "status.json",
}


def log(icon, msg):
    print(f"   {icon} {msg}")


# ── Step 1: 掃描專案 ─────────────────────────────────────
def scan_projects():
    """Run update_research_os.py from Project_CodingSimulation root."""
    print("\n📊 Step 1: 掃描所有專案 STATUS.yaml...")
    scan_script = PROJECT_ROOT / "update_research_os.py"
    if not scan_script.exists():
        log("⚠️", f"找不到 {scan_script}")
        return False

    result = subprocess.run(
        [sys.executable, str(scan_script)],
        cwd=str(PROJECT_ROOT),
        timeout=120,
    )
    return result.returncode == 0


# ── Step 2: 複製儀表板檔案 ───────────────────────────────
def deploy_dashboard():
    """Copy dashboard files from Project root to LabPagesCowork."""
    print("\n📁 Step 2: 複製儀表板檔案到 LabPagesCowork...")
    copied = 0
    for src_name, dst_name in DEPLOY_FILES.items():
        src = PROJECT_ROOT / src_name
        dst = LABPAGES_DIR / dst_name
        if src.exists():
            shutil.copy2(str(src), str(dst))
            size_kb = src.stat().st_size / 1024
            log("✅", f"{src_name} → {dst_name} ({size_kb:.1f} KB)")
            copied += 1
        else:
            log("⚠️", f"{src_name} 不存在，跳過")
    log("📦", f"{copied}/{len(DEPLOY_FILES)} 檔案已複製")
    return copied > 0


# ── Step 3: 更新 blog.html 文章列表 ─────────────────────
def update_blog_index():
    """Scan posts/ folder and update the KNOWN_POST_FILES list in blog.html."""
    print("\n📝 Step 3: 更新 blog.html 文章列表...")

    blog_path = LABPAGES_DIR / "blog.html"
    if not blog_path.exists():
        log("⚠️", "blog.html 不存在")
        return False

    if not POSTS_DIR.exists():
        log("⚠️", "posts/ 資料夾不存在")
        return False

    # Collect all post files
    posts = []
    for f in POSTS_DIR.iterdir():
        if f.is_file() and f.suffix in ('.html', '.md'):
            posts.append(f.name)

    # Sort by filename (date descending)
    posts.sort(reverse=True)
    log("📄", f"找到 {len(posts)} 篇文章")

    # Build JS array string
    js_array = "    const KNOWN_POST_FILES = [\n"
    for p in posts:
        js_array += f"      '{p}',\n"
    js_array += "    ];"

    # Read blog.html and replace the array
    content = blog_path.read_text(encoding='utf-8')

    import re
    pattern = r"const KNOWN_POST_FILES\s*=\s*\[.*?\];"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + js_array.strip() + content[match.end():]
        blog_path.write_text(content, encoding='utf-8')
        log("✅", f"blog.html 已更新（{len(posts)} 篇文章）")
        return True
    else:
        log("⚠️", "找不到 KNOWN_POST_FILES 陣列")
        return False


# ── Step 4: Git push ─────────────────────────────────────
def git_push():
    """Stage, commit, and push changes."""
    print("\n🚀 Step 4: 推送到 GitHub...")

    def run_git(args):
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=str(LABPAGES_DIR),
                capture_output=True, text=True, timeout=60,
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)

    # Check git repo
    if not (LABPAGES_DIR / ".git").exists():
        log("⚠️", "Git repo 不存在，請先初始化")
        return False

    run_git(["add", "-A"])

    ok, status = run_git(["status", "--porcelain"])
    if not status.strip():
        log("ℹ️", "沒有變更需要推送")
        return True

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"auto: update research portal — {timestamp}"
    ok, out = run_git(["commit", "-m", msg])
    if not ok:
        log("❌", f"commit 失敗: {out}")
        return False
    log("✅", f"已提交: {msg}")

    ok, out = run_git(["push"])
    if not ok:
        log("❌", f"push 失敗: {out}")
        log("💡", "可能需要先建立 PR（branch protection）")
        return False

    log("✅", "已推送到 GitHub!")
    log("🌐", "https://doflab.cc/")
    return True


# ── Main ─────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("🔬 LabPagesCowork — Research Portal Manager")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"📂 {LABPAGES_DIR}")
    print("=" * 55)

    args = sys.argv[1:]
    do_scan = "--scan" in args or "--all" in args or not any(a.startswith("--") for a in args)
    do_blog = "--blog" in args or "--all" in args
    do_deploy = "--deploy" in args or "--all" in args or not any(a.startswith("--") for a in args)
    do_push = "--push" in args

    if do_scan:
        scan_projects()

    if do_deploy:
        deploy_dashboard()

    if do_blog:
        update_blog_index()

    if do_push:
        git_push()
    else:
        print("\n💡 加上 --push 旗標可自動推送到 GitHub")
        print("💡 或手動: cd MCP/LabPagesCowork && git add -A && git commit -m 'update' && git push")

    print("\n✅ 完成！")


if __name__ == "__main__":
    main()
