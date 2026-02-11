# LabPages 專案內容擴充與學生協作指南

本文件旨在指導實驗室成員如何透過 GitHub 協作流程，將個人介紹與研究成果整合至實驗室網頁 (`LabPages`)，並規劃未來的自動化維護流程。

---

## 👨‍🎓 學生協作指南 (Student Guide)

歡迎加入 **NCUT IAE Lab** 網頁協作計畫！請依照以下步驟建立你的個人頁面：

### 1. 準備工作
*   確保你擁有 GitHub 帳號。
*   Fork 實驗室的 Repo: `https://github.com/dofliu/LabPagesCowork`
*   Clone 你的 Fork 到本地端。

### 2. 建立個人分支 (Branch)
為了避免衝突，請務必建立自己的分支：
```bash
git checkout -b feat/intro-你的英文名字 (例如: feat/intro-naruto)
```

### 3. 新增個人頁面
*   在 `members/` 資料夾下（如果沒有請建立），新增一個 HTML 檔案，命名為 `你的英文名字.html` (例如 `naruto.html`)。
*   **頁面模板**：請參考專案根目錄下的 `_template.html` (稍後會建立)，複製內容並修改為你的資訊。
*   **內容需求**：
    *   姓名 (中/英)
    *   自我介紹 (Bio)
    *   研究興趣 (Research Interests)
    *   專案/作品集 (Projects/Portfolio)
    *   聯絡方式 (Email/GitHub/LinkedIn)

### 4. 提交與推送 (Commit & Push)
```bash
git add members/你的名字.html
git commit -m "feat: add member profile for 你的名字"
git push origin feat/intro-你的名字
```

### 5. 發起 Pull Request (PR)
*   回到 GitHub 你的 Fork 頁面，點擊 **"Compare & pull request"**。
*   標題請寫：`feat: 新增 [你的名字] 個人介紹頁面`。
*   確認內容無誤後送出，等待 Dof 教授或管理員 Review 與 Merge。

---

## 🤖 自動化更新與維護 (Agent Role)

身為實驗室的 AI 助理，我 (Antigravity/OpenClaw) 將負責以下維護工作：

1.  **成果監控與更新**：
    *   我會定期掃描指定的論文發表來源 (如您提供的 Google Sites、ResearchGate 或實驗室共用文檔)。
    *   當發現新的發表或獲獎紀錄時，我會自動更新 `index.html` 中的「最新消息」或「研究成果」區塊。
    *   更新後，我會主動發起一個 PR (例如：`chore: update publications list`)，並通知您審核。

2.  **內容遷移計畫 (Google Sites to LabPages)**：
    *   **目標**：將「瘋風機」Google Sites 的豐富內容 (期刊論文、最新消息、影片連結) 結構化地遷移至 LabPages。
    *   **執行方式**：
        *   建立 `publications.html`：專門條列期刊論文與研討會發表 (參考您提供的 Journal Articles 頁面)。
        *   優化 `index.html`：將「最新消息」區塊動態化，並加入 Youtube 頻道與 MCP 成果展示。
    *   **目前進度**：已擷取 Google Sites 的文字內容，正在進行 HTML 結構化轉換。

---

## 📅 下一步行動
1.  **建立 `members/_template.html`**：提供統一的樣板給學生使用。
2.  **建立 `publications.html`**：將剛才抓取的論文列表轉換為網頁格式。
3.  **整合首頁**：將 Google Sites 的重要連結與介紹整合進現有的 `index.html`。

