# 專案／論文動畫的英文版（`<id>/en/`）

網站有中／英切換（`assets/i18n.js`）。英文介面下，專案卡片與論文條目會優先播放英文版影片
`assets/showcase/<id>.en.mp4`、`assets/papers/<id>.en.mp4`（沒有英文版就退回中文版）。

## 檔案配置

```
tools/showcase/projects/<id>/
  scene01_open.html … scene05_cta.html   ← 中文（原版，不動）
  storyboard.json
  assets/                                 ← 素材圖（中英共用）
  en/
    scene01_open.html … scene05_cta.html  ← 英文版（檔名與中文版一致）
    storyboard.json                       ← 內容與中文版相同（檔名相對 en/）
```

論文同理：`tools/showcase/papers/<id>/en/` 由 `make_paper_scenes.py <paper.json> --lang en` 自動產生，
英文內容放在 paper.json 的 `*_en` 欄位（見該腳本檔頭）。

## 製作英文場景（專案）

1. `mkdir -p $P/en && cp $P/scene0*.html $P/storyboard.json $P/en/`
2. 逐景翻譯 `<!-- ▼▼ 本景內容 ▼▼ -->` … `<!-- ▲▲ 本景內容 ▲▲ -->` 內所有看得到的中文（含 `<title>`），
   `<html lang="zh-Hant">` 改成 `lang="en"`；CSS、class、動畫延遲（`--d`、`--l`）、emoji、SVG 一律不動。
3. 素材圖路徑改成上一層：`src="assets/x.png"` → `src="../assets/x.png"`。
4. 固定用語：
   | 中文 | 英文 |
   |---|---|
   | 國立勤益科技大學 智慧自動化工程系 | National Chin-Yi University of Technology · Dept. of Intelligent Automation Engineering |
   | 研究室內部專案 | Internal lab project |
   | DOF LAB · 風力發電 AI | DOF LAB · WIND ENERGY AI（kicker 全大寫） |
   | 工業 AI 巡檢 | Industrial AI Inspection |
   | RAG 知識管理 | RAG Knowledge |
   | 教育科技 | EdTech |
   | MCP 工具鏈 | MCP Toolchain |
   | 生產力工具 | Productivity Tools |
   | 風電運維 | Wind O&M |
   | 風機 | wind turbine |
   | 運維 | operations & maintenance (O&M) |
   | 離岸風場 | offshore wind farm |
   | 檢索增強生成 | Retrieval-Augmented Generation (RAG) |
5. 英文比中文長：標題 `font-size` 可降 10–25%、chip 文字縮短成 2–3 個字、卡片文字允許換行（拿掉 `white-space:nowrap`
   前先確認不是膠囊）。寧可改寫成更短的英文，也不要讓字溢出。
6. 預覽（每景約 3 秒）並 **Read 總覽圖**，修到沒有溢出、相撞、被裁切：
   ```bash
   CHROMIUM_PATH=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome \
   python3 tools/showcase/preview_scenes.py $P/en/storyboard.json --out <暫存區>/pv_<id>
   ```
7. 出片：`bash tools/showcase/batch_render.sh projects <W> <mood> <id>` 會同時出中英兩版（`LANGS=en` 只出英文）；
   之後 `python3 tools/showcase/site_update.py en-sync` 把 `video_en`／`cover_en` 寫進 showcase.json／publications.json。

## 卡片文字

`site_update.py project add` 加 `--title-en "<≤ 40 chars>" --tagline-en "<≤ 60 chars>" --tech-en ...`；
公告用 `news add --title-en --body-en`。沒給英文時英文介面顯示中文（不會壞）。
