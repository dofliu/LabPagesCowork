# LabPagesCowork - 實驗室網頁協作專案 🍥

歡迎來到實驗室網頁的協作陣地！這是一個讓大家練習 GitHub 協作流程並同時完成我們網頁的專案。

## 🛠 協作流程
## 🎯 當前任務
請參考 Issue 列表，領取你的「S 級任務」！

## 🔄 個人研究資料更新

* **GitHub 專案與活動**：`.github/workflows/refresh-github-cache.yml` 每天更新 `github-data.json`，並把 `dofliu` 最近更新的公開 repository 寫入 `data.json` 的 `github_recent_projects`；`projects.html` 會在「GitHub 最近更新」區塊顯示這些專案，`github.html` 則以快取作為 API 受限時的備援。可在 Actions 頁面手動執行 **Refresh DOF Lab site data**。
* **研究發表**：`scripts/sync_publications.py` 會從 Google Sites 的期刊論文頁讀取最上方已刊登的 `2022~2026` 最新期刊資料，合併到 `publications.json` 的 `journal` 陣列；`Under Review`、`Submitted`、`Draft` 類稿件不會自動放進正式發表列表。`publications.html` 會自動重新計算各類別數量與顯示內容。
2. **開發功能**: 在指定目錄下建立你的自我介紹分頁
3. **提交 PR (Pull Request)**: 送出後由老大 Review
4. **合併 (Merge)**: 通過後併入主分支

## 🎯 當前任務
請參考 Issue 列表，領取你的「S 級任務」！
