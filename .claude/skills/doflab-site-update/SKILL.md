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
`prep_assets.py`（素材圖正規化）、`make_music.py`（原創背景配樂合成）、`add_music.py`（替已上線影片補／換配樂）、`make_web.py`（轉網頁影片＋封面，`--dir papers` 給論文）、`make_paper_scenes.py`（論文 JSON → 5 景）、`preview_scenes.py`（快速排版預覽）、`batch_render.sh`（批次出片）、`site_update.py`（寫 JSON）、
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
分類（wind_energy / industrial_ai / rag_knowledge / edtech / mcp_tools / personal_tools / other）、
**配樂曲風**：`tech`（系統／AI／工具，預設）、`calm`（教育、研究介紹、文件型成果）、`epic`（大型平台、能源、重大成果）。
使用者有指定曲風或給了音樂檔就照他的。

**內容紅線（網站驗證腳本會擋）**：不放未經核實的效能數字（F1、R²、準確率百分比等）；
不放本機路徑、內部 STATUS 欄位、未公開資料；照片含人臉／學生個資先問使用者。

**私人 repo（使用者同意製作，但「不放連結」）**：
- `site_update.py project add` 不給 `--source-url`，改給 `--repo owner/repo`（卡片與彈窗就不會出現連結）；結尾景不寫 github 網址，改寫「研究室內部專案」。
- 動畫只講「解決什麼問題、功能概念、應用情境」，不放程式碼、檔名路徑、API 金鑰／帳號、內部網址、真實截圖、客戶或合作廠商名稱、未發表的數據。
- 涉及個資的專案（點名、健康、招生評選、成績、監視器等）：只呈現系統概念與流程示意，絕不出現任何真實姓名、學號、紀錄樣本。

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

### A5. 配樂 → 出片 → 上網站（每支動畫都要有背景配樂）

配樂來源優先順序：
1. 使用者這次給的音樂檔。
2. `tools/showcase/music/` 裡檔名開頭與曲風相符的檔案（例 `tech-*.mp3`；使用者自備的免版稅音樂）。
3. 以上都沒有 → 用 `make_music.py` 合成原創配樂（無版權問題，約 4 秒完成）：

```bash
DUR=$(python3 -c "import json;s=json.load(open('$P/storyboard.json'));print(sum(x['duration'] for x in s['scenes'])-s.get('xfade',.6)*(len(s['scenes'])-1))")
python3 tools/showcase/make_music.py --out $W/bgm.wav --duration $DUR --mood tech --seed <id>
```
合成配樂的結構對齊五景分鏡：開場約 6 秒只有鋪底與琶音 → 低音與輕鼓進場 → 最後約 4 秒鼓組退場、和弦延音淡出。
`--seed` 填專案 id，每支專案的琶音型都不同。

```bash
python3 tools/showcase/assemble_video.py $P/storyboard.json --workdir $W --out $W/master.mp4 \
    --music $W/bgm.wav --loudness -18          # -18 LUFS＝背景音樂感；使用者嫌小聲用 -16，嫌吵用 -20
python3 tools/showcase/make_web.py $W/master.mp4 --id <id> --cover-at 4.5   # 1280×720 MP4（約 1.3 MB，含 AAC 音軌）＋封面
python3 tools/showcase/site_update.py project add --id <id> --title "<標題>" --tagline "<≤20字>" \
    --category <分類> --source-type repo|document|link|other [--source-url https://...] --tech X --tech Y
```
出片後確認有音軌與響度：
`ffprobe -v error -show_entries stream=codec_type -of csv=p=0 assets/showcase/<id>.mp4`（要有 audio）、
`ffmpeg -i assets/showcase/<id>.mp4 -af ebur128 -f null - 2>&1 | grep "I:" | tail -1`（約 -18）。
只換配樂或音量時**不必重渲場景**，直接改已上線的影片（秒級，影像原樣保留）：
`python3 tools/showcase/add_music.py --id <id> --mood calm`（或 `--music 檔案.mp3`、`--loudness -16`）。
舊的無聲影片也用這支補配樂。
封面若取到轉場或空畫面，換 `--cover-at`（例 5.5）重跑 make_web。
同一個 id 再跑一次＝更新（影片、封面、文字一起換）。下架：`site_update.py project remove --id <id>`。

## B. 研究發表（新增論文＝同時製作 30 秒動畫說明）

發表頁每篇有動畫的論文，條目右側會出現小封面，點開播放（`publications.json` 的 `video_id` →
`assets/papers/<video_id>.mp4/.jpg`）。**新增期刊、預印本、已接受論文時一律一起做動畫**；
研討會論文、專利、獲獎只有在使用者提供全文或摘要時才做（只有題目就不做，避免編造內容）。

### B1. 核對書目並讀摘要
有 DOI：WebSearch 標題 → WebFetch 出版社頁，核對作者、卷期、日期，並讀摘要。
使用者上傳 PDF 就直接讀 PDF。動畫裡的數字與方法名稱**只能用摘要／全文明列的**；
作者自己寫的限制（「初步結果」「普遍性待驗證」）要放進結果景的 note。預印本要標「預印本，非正式期刊出版」。

### B2. 寫 paper.json → 自動產生 5 景
```bash
P=tools/showcase/papers/<id>; mkdir -p $P      # id 例：sr2026-rag-transfer（期刊縮寫＋年份＋主題）
# 寫 $P/paper.json（欄位說明見 make_paper_scenes.py 開頭；範例：tools/showcase/papers/*/paper.json）
python3 tools/showcase/make_paper_scenes.py $P/paper.json
python3 tools/showcase/preview_scenes.py $P/storyboard.json --out <scratchpad>/pv   # 3 秒／景的排版預覽
```
5 景固定：開場（中文說明標題＋原文標題）→ 研究問題（3 卡）→ 研究方法（3–5 步驟依序點亮）→
主要發現（2–3 個數字／結論）→ 結尾（期刊、作者、DOI）。**Read 預覽總覽圖**，有溢出就縮短文字重產。

### B3. 出片（配樂預設 tech）
```bash
bash tools/showcase/batch_render.sh papers <scratchpad>/papers tech <id> [<id2> ...]
# 多篇時平行兩支：printf "%s\n" id1 id2 id3 | xargs -P2 -n1 bash tools/showcase/batch_render.sh papers <W> tech
# 會超過 10 分鐘 → 用 nohup … & 背景執行，定期看 log
```
完成後 Read `<W>/<id>/check_*.png` 抽查。

### B4. 寫入發表資料
```bash
python3 tools/showcase/site_update.py pub add --group journal --video-id <id> --json '{
  "year":"2026","title":"...","authors":"Jui-Hung Liu, ...","venue":"期刊名",
  "detail":"Vol. X, Article Y · 日期","doi":"https://doi.org/...","source_url":"https://...",
  "index":"SCIE","metric":""}'
# 已在清單上的論文補動畫：
python3 tools/showcase/site_update.py pub video --group journal --match "標題關鍵字" --id <id>
```
- group：journal（已正式出版）／accepted（已接受待刊）／preprint／conference／patent／award。
- 審查中、投稿中、草稿 **不上網站**（腳本會拒絕）；每筆必須有公開 `source_url`。
- 中文研討會論文可只給 `citation` 全文引文字串（同既有格式），title 填同一段。
- 首頁「期刊著作紀錄／研討會論文紀錄」數字會自動更新。
- 論文影片換配樂或音量：`python3 tools/showcase/add_music.py --dir papers --id <id> --mood calm`。

## A6. 每日自動模式（排程用：從最近有活動的 repo 挑一個還沒做的）

排程 session **沒有** list_repos／add_repo 工具，GitHub 帳號層級 API 也被擋。所以：
- **公開** repo 名冊存在 `tools/showcase/repos.json`；匿名 `git clone` 就能讀。
- **私人** repo 名單**不存進網站 repo**（網站 repo 是公開的），寫在排程任務的指示裡，執行時用 `--private` 傳入；
  這些私人 repo 已在建立排程任務時以唯讀附加給任務。

```bash
python3 tools/showcase/auto_pick.py --refresh --private "<逗號分隔的私人 repo>"          # 約 10 秒 → {"next": ...}
python3 tools/showcase/auto_pick.py --refresh --private "<...>" --list 5                  # 檢視候選
```
- 排除：showcase.json 已有的（公開比對 `repo`／`source_url`，私人比對 `repo_hash`）、fork、`tools/showcase/auto_skip.json`。依活動時間由新到舊。
- 取得原始碼：`git clone --depth 1 https://github.com/<owner>/<repo> <暫存區>/src/<repo>`。
- 跳過（內容不足、或私人 repo clone 失敗＝建立任務後才新增）：`auto_pick.py --private "<...>" --skip <repo> --reason "<原因>"`
  （私人 repo 只會記雜湊）。一次最多試 3 個。
- 寫入網站：公開 repo 用 `--repo owner/repo --source-url https://github.com/...`；
  私人 repo 用 `--private-repo owner/repo`（只存雜湊），**不給** `--repo`、`--source-url`。
  **任何公開檔案（commit 訊息、showcase.json、場景 HTML、影片）都不得出現私人 repo 的名稱**；commit 訊息用卡片 id。
  私人 repo 的 `id` 與卡片標題要依功能另取（例：`wind-blade-design-lab`），不要直接用 repo 名。
- 一次只做 **1 支**；`batch_render.sh projects <W> <mood> <id>` 背景渲染；完成後照 D 驗證、commit（`showcase: add <id> 30s video (auto)`）、push main。
- `next` 為 null（全部做完）→ 不做任何變更，回覆建議停用排程。
- 互動 session（有 list_repos 工具）更新公開名冊：list_repos 輸出存檔後 `auto_pick.py --merge <檔案>`（私人 repo 會自動略過）。
  新建立的**私人** repo 要重建排程任務（附加＋寫進指示）才會被納入。

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

一兩句說明上線了什麼（含用了哪種配樂），附連結：專案 `https://doflab.cc/projects.html#<id>`（直接開啟該動畫）、
公告 `https://doflab.cc/news.html`、著作 `https://doflab.cc/publications.html#<video_id>`（直接開啟論文動畫）。
GitHub Pages 約 1–2 分鐘後生效。把成品 MP4 也用 SendUserFile 給使用者一份。
