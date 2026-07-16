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