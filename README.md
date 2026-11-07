# LabPagesCowork - 實驗室網頁協作專案 🍥

歡迎來到實驗室網頁的協作陣地！這是一個讓大家練習 GitHub 協作流程並同時完成我們網頁的專案。

## 🛠 協作流程
## 🎯 當前任務
請參考 Issue 列表，領取你的「S 級任務」！

## 🔄 個人研究資料更新

* **GitHub 專案與活動**：`github.html` 會在訪客瀏覽時直接讀取 GitHub Public API；`.github/workflows/refresh-github-cache.yml` 也會每天建立 `github-data.json` 快取，讓 API 暫時受限時仍有最近一次的內容可顯示。可在 Actions 頁面手動執行 **Refresh GitHub profile cache**。
* **研究發表**：以 `publications.json` 作為網站的單一資料來源，並在 `_source` 保留教授個人著作網站連結。新增或修正著作時，依既有欄位更新此檔案並改寫 `_updated` 日期；`publications.html` 會自動重新計算各類別數量與顯示內容。
2. **開發功能**: 在指定目錄下建立你的自我介紹分頁
3. **提交 PR (Pull Request)**: 送出後由老大 Review
4. **合併 (Merge)**: 通過後併入主分支

## 🎯 當前任務
請參考 Issue 列表，領取你的「S 級任務」！

## 🌐 中／英雙語介面

- 原始頁面一律是繁體中文；英文由 `assets/i18n.js` 在瀏覽器端套用 `assets/i18n/en.js` 字典（key = 元素的中文 innerHTML）。導覽列右側的「中 / EN」切換會記在 localStorage，也可用 `?lang=en` 直接開英文版。
- 資料檔用 `*_en` 欄位（`showcase.json` 的 `title_en`／`tagline_en`／`tech_en`、`announcements.json` 的 `title_en`／`body_en`、`publications.json` 的 `_note_en`／`status_label_en`）；沒有英文欄位時英文介面會退回中文，不會壞頁。
- 專案與論文動畫各有英文版 `assets/showcase/<id>.en.mp4`、`assets/papers/<id>.en.mp4`（英文介面優先播放）；製作流程見 `tools/showcase/EN_SCENES.md`，`tools/showcase/site_update.py en-sync` 會自動掛上 `video_en` 旗標。
- 改過 HTML 文字後：`node tools/i18n/extract_keys.js && python3 tools/i18n/check_missing.py` 列出缺英文的字串，用 `python3 tools/i18n/dict.py set "中文" "English"` 補進字典。
- 研究日誌（posts/）內容維持中文；英文介面會註明。

## 公開內容資料與檢查

- `publications.json`：正式期刊、研討會、預印本、已接受待刊、專利與代表性獲獎分組，保留每筆公開來源。`verification` 區分出版社核對與個人著作網站紀錄。
- `research-projects.json`：歷年計畫、期間與來源狀態；洽談、申請紀錄不當作已執行或已結案。
- `data.json`：去除備份及工作樹重複後的公開專案摘要。專案頁、研究儀表板與研究圖共用此檔。只保留展示必要欄位；不要直接公開內部 STATUS 原始檔、本機路徑、工作紀錄或未核實的百分比。
- 內容更動後執行 `python3 scripts/validate_public_content.py`，並檢查受影響頁面的桌面、手機排版和來源連結。首頁精選內容與統計須同步更新。

本次公開資料核對：2026-10-10。
