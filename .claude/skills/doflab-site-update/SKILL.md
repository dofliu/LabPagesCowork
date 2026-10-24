---
name: doflab-site-update
description: 更新個人網站 doflab.cc（repo dofliu/LabPagesCowork）。(1) 指定一個 repo、文件、網址或其他成果 → 做成 30 秒專案動畫 MP4，加進「專案成果」頁（封面＋20 字內簡介，點開播放）；(2) 新增研究發表（期刊、研討會、預印本、專利、獲獎）；(3) 發布最新公告。只要使用者說「把 XX repo 做成動畫放上網站」「更新 doflab」「新增一篇論文／著作」「發一則公告」「網站加一個專案」就用本技能。
---

# doflab-site-update — 更新 doflab.cc

網站 repo：`dofliu/LabPagesCowork`（GitHub Pages，CNAME = doflab.cc）。
頁面全部由 JSON 驅動，本技能只改資料檔與 `assets/showcase/`，不手改 HTML。

| 要更新什麼 | 資料檔 | 呈現頁面 |
|---|---|---|
| 專案動畫 | `showcase.json` + `assets/showcase/<id>.mp4/.jpg` | projects.html |
| 研究發表 | `publications.json` | publications.html（首頁統計數字自動同步） |
| 公告 | `announcements.json` | 首頁「最新公告」前 4 則 + news.html |

工具都在 `tools/showcase/`：`render_scenes.py`（HTML 場景逐格渲染）、`assemble_video.py`（轉場串接）、
`prep_assets.py`（素材圖正規化）、`make_web.py`（轉網頁影片＋封面）、`site_update.py`（寫 JSON）、
`scene_template.html`（品牌場景模板）。範例成品：`tools/showcase/projects/windai-lab/`。

## 0. 準備網站 repo（每次都做）

```bash
# 若 /home/claude/labpagescowork 不存在：先用 add_repo（owner dofliu, repo LabPagesCowork, access push），再
git clone --depth 1 https://github.com/dofliu/labpagescowork /home/claude/labpagescowork
cd /home/claude/labpagescowork && git pull --rebase origin main
python3 -c "import playwright" && which ffmpeg   # 動畫模式才需要
```

先判斷使用者要哪一種更新（可一次多種），再跳到對應段落。

## A. 專案動畫（repo / 文件 / 網址 / 其他）

### A1. 讀來源，萃取四件事

| 來源 | 怎麼讀 |
|---|---|
| 使用者的 repo | add_repo（public 用 read，private 用 push 才拿得到）→ `git clone --depth 1`；讀 README、docs/、主要程式目錄、截圖 |
| 上傳的文件（PDF/Word/PPT） | 用對應的讀檔技能（pdf-reading、docx、pptx）讀全文；文件裡的圖可抽出當素材 |
| 網址 | WebFetch 讀頁面；需要登入的頁面請使用者貼內容或截圖 |
| 其他（口述、照片、影片） | 直接問使用者重點，不要自己編 |

萃取：**一句話定位**、**3 個觀眾有感的重點**、**一個最敢說的主張**、**連結**（公開 https 才放）。
另外決定：`id`（小寫英數與 -，例：`windai-lab`）、卡片標題（≤16 字）、**卡片簡介 ≤20 字**、
分類（wind_energy / industrial_ai / rag_knowledge / edtech / mcp_tools / personal_tools / other）。

**內容紅線（網站驗證腳本會擋）**：不放未經核實的效能數字（F1、R²、準確率百分比等）；
不放本機路徑、內部 STATUS 欄位、未公開資料；照片含人臉／學生個資先問使用者。

### A2. 分鏡（固定 5 景 ≈ 30 秒）

| 景 | 內容 | 秒 | 轉場 |
|---|---|---|---|
| 1 開場 | kicker（DOF LAB · 領域）＋專案名大字＋一句定位，保留粒子層 | 7 | fade |
| 2 重點一 | 最有感的功能，做迷你示意（節點圖、卡片、面板），不要只有字 | 6.5 | smoothleft |
| 3 重點二 | 流程／管線動畫（逐步點亮） | 6.5 | circleopen |
| 4 成果 | 產出物卡片群（圖表、報告、介面） | 6.5 | fade |
| 5 結尾 | 名稱回歸＋三特點 chip＋連結＋「國立勤益科技大學 智慧自動化工程系」 | 6 | — |

5 景 32.5 秒扣 4 刀 xfade(0.6s) = 30.1 秒。有真實截圖就用 `.shot` / `.frame` / `.hero-img` 放進第 2–4 景。
使用者在場就把分鏡表貼給他看一眼；不在場就直接做，交付時說可以怎麼改。

### A3. 寫場景

```bash
P=tools/showcase/projects/<id>; mkdir -p $P/assets
```
每景複製 `tools/showcase/scene_template.html` 為 `$P/sceneNN_xxx.html`，只改 `<title>`、
`.stage` 的 `--dur`、本景 CSS 與 `.stage` 內容（可參考 windai-lab 的五景寫法）。
素材圖：`python3 tools/showcase/prep_assets.py --out $P/assets <圖檔...>`，HTML 用相對路徑引用。
寫 `$P/storyboard.json`（格式同 windai-lab）。**動手前先讀 `references/scene_design.md` 的陷阱清單。**
文字：繁體中文，標題 ≤14 字、chip ≤8 字；不得外連（file:// 離線渲染）。

### A4. 渲染（每景約 1.5–2 分鐘，整支會超過單一指令 10 分鐘上限 → 背景執行）

```bash
W=<scratchpad>/<id>; mkdir -p $W
nohup python3 tools/showcase/render_scenes.py $P/storyboard.json --workdir $W > $W/render.log 2>&1 &
# 每隔一段時間檢查：tail -2 $W/render.log；出現「完成」才往下
```
**逐張 Read `$W/check_*.png`**：文字溢出、元素相撞、置中跑位、節點壓到標題。
有問題改該景 HTML，用 `--only <scene_stem>` 單景重渲。沒看過抽查格不准出片。

### A5. 出片 → 上網站

```bash
python3 tools/showcase/assemble_video.py $P/storyboard.json --workdir $W --out $W/master.mp4   # 預設無聲
python3 tools/showcase/make_web.py $W/master.mp4 --id <id> --cover-at 4.5   # 1280×720 MP4（約 1 MB）＋封面
python3 tools/showcase/site_update.py project add --id <id> --title "<標題>" --tagline "<≤20字>" \
    --category <分類> --source-type repo|document|link|other [--source-url https://...] --tech X --tech Y
```
使用者有給背景音樂才加 `--music bgm.mp3`。封面若取到轉場或空畫面，換 `--cover-at`（例 5.5）重跑 make_web。
同一個 id 再跑一次＝更新（影片、封面、文字一起換）。下架：`site_update.py project remove --id <id>`。

## B. 研究發表

整理成一筆 JSON（欄位比照 publications.json 既有條目），有 DOI 先 WebFetch 出版社頁核對書目：

```bash
python3 tools/showcase/site_update.py pub add --group journal --json '{
  "year":"2026","title":"...","authors":"Jui-Hung Liu, ...","venue":"期刊名",
  "detail":"Vol. X, Article Y · 日期","doi":"https://doi.org/...","source_url":"https://...",
  "index":"SCIE","metric":""}'
```
- group：journal（已正式出版）／accepted（已接受待刊）／preprint／conference／patent／award。
- 審查中、投稿中、草稿 **不上網站**（腳本會拒絕）；每筆必須有公開 `source_url`。
- 中文研討會論文可只給 `citation` 全文引文字串（同既有格式），title 填同一段。
- 首頁「期刊著作紀錄／研討會論文紀錄」數字會自動更新。

## C. 公告

```bash
python3 tools/showcase/site_update.py news add --title "<標題>" --body "<一兩句說明>" \
    [--date YYYY-MM-DD] [--tag 活動|招生|獲獎|成果|網站] [--link https://...] [--pinned]
python3 tools/showcase/site_update.py news list      # 查 id
python3 tools/showcase/site_update.py news remove --id <id>
```
專案動畫上線時，可順手發一則「新增專案動畫：XXX」公告（link 用 `https://doflab.cc/projects.html#<id>`）—
先問使用者要不要。

## D. 驗證 → 推上 main（使用者指定直接推，不開 PR）

```bash
python3 scripts/validate_public_content.py          # 必須 PASS
git add -A showcase.json announcements.json publications.json index.html *.html assets/ tools/
git commit -m "<動詞>: <內容>"                        # 例：showcase: add windai-lab 30s video
git fetch origin main && git rebase origin/main && git push origin HEAD:main
```
推之前可用 `python3 -m http.server` + playwright 截 projects.html 確認卡片與彈窗播放正常（改過版面時必做）。

## 交付

一兩句說明上線了什麼，附連結：專案 `https://doflab.cc/projects.html#<id>`（直接開啟該動畫）、
公告 `https://doflab.cc/news.html`、著作 `https://doflab.cc/publications.html`。
GitHub Pages 約 1–2 分鐘後生效。把成品 MP4 也用 SendUserFile 給使用者一份。
