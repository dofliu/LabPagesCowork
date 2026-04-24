# 專案健康檢查日誌

| 日期 | 活躍專案數 | 自動處理 | 開立 Issue | 備註 |
|------|-----------|---------|-----------|------|
| 2026-04-11 | 15 | 0 | 0 (gh CLI 未認證，跳過 GitHub 操作) | 初始建檔 |
| 2026-04-12 | 17 | 0 | 0 (gh CLI 未可用，僅本地掃描) | windAILab 139c, digiWindFarm 74c, citingVerify 38c 最活躍；zImage DEBUG=True 待修；InduSpect 4 個 TODO 待實作 |

---
## 2026-04-14 健檢日誌

### 自動處理
- [picasa] 補建 STATUS.yaml（progress=60, status=active）— commit 5f4c886

### 掃描結果摘要
- 活躍 repo 數：15（近一個月有 commit）
- gh CLI 未認證，跳過 GitHub issue 操作
- 本地掃描完成

---
## 2026-04-17 健檢日誌

### 自動處理
- [scanmail_bot] 同步 STATUS.yaml last_updated 2026-04-13 → 2026-04-16（落後 3 天）— commit e42effa

### 掃描結果摘要
- 活躍 repo 數：17（近一個月有 commit，含 scanmail_bot_repo 無 remote 已跳過）
- gh CLI 未安裝，跳過 GitHub issue 操作，僅本地掃描
- 最活躍：windAILab 168c、digiWindFarm 130c、RAG_Ultimate 82c、citingVerify 38c、scanmail-bot 36c
- 今日 commit 但 STATUS.yaml 尚未同步的 repo（正常、當日工作）：LabPagesCowork、RAG_Ultimate、windAILab、digiWindTurbine
- zImage STATUS.yaml description_zh 提到「DEBUG=True 需在上線前修正」，但 config.py 實際已為 `DEBUG = False`（描述過時，建議下次同步時清理）
- InduSpect Flutter TODO 仍阻塞 next_milestone「實機端到端測試」：file_picker 整合、oneStopProcess 呼叫、簽名板實作（todo.md Phase 2）
- infoCard 3 個 MCP/本地模型掃描 TODO 與 next_milestone 完全對應（已被追蹤）

---
## 2026-04-18 健檢日誌

### 自動處理
- [zImage] 清理 STATUS.yaml description_zh 過時 DEBUG=True 警告並同步 last_updated 2026-04-16 → 2026-04-18 — commit 0bc2861
- [LabPagesCowork] STATUS.yaml last_updated 2026-04-16 → 2026-04-18 已編輯，但 commit 被 .git/index 損壞（100KB 全 0x00）與 stale index.lock 阻擋，需教授手動清理 `.git/index.lock` 後重新 `git add STATUS.yaml && git commit`

### 掃描結果摘要
- 活躍 repo 數：16（dofliu 原創，近一個月有 commit；scanmail_bot_repo 無 remote 已跳過）
- gh CLI 未安裝，跳過 GitHub issue 操作，僅本地掃描
- 最活躍：windAILab 178c、digiWindFarm 153c、citingVerify 38c、scanmail-bot 37c、infoCard 32c、LabPagesCowork 31c
- **排程任務限制**：本次從 scheduled-task session 內無法呼叫 `create_scheduled_task`，故直接執行安全級修正而非派工
- zImage DEBUG 過時描述已清理（config.py 自 2026-04-17 前就是 DEBUG=False）
- 7 天以上沒 commit 但本月有活動：course-scheduling-system（27d）、citingVerify（14d）、englishSpeakingTutor（28d）
- InduSpect backend `form_fill.py:50` TODO「正式環境改用資料庫」與 next_milestone 不同但屬 P2 建議
- windAILab `useWebSocket.ts:266` TODO「parse from WebSocket messages」屬 P2 前端改善
- digiWindTurbine TODO 全在 `opc_bachmann/openopc2-0.1.18/` 第三方 vendored 套件內，略過
- attendence 5 個 TODO 皆在 `scripts/legacy/` 且為佔位註解或 Few-Shot 實驗，屬 P2
- infoCard 3 個 MCP/本地模型掃描 TODO 持續與 next_milestone 對應，已被追蹤

---
## 2026-04-20 健檢日誌

### 自動處理
- [attendence] 同步 STATUS.yaml last_updated 2026-04-13 → 2026-04-19（落後 6 天）— commit c63ea88

### 掃描結果摘要
- 活躍 repo 數：17（dofliu 原創，近一個月有 commit；scanmail_bot_repo 無 remote 已跳過）
- 近一週（2026-04-13 起）有 commit：13 個 repo
- gh CLI 未安裝，跳過 GitHub issue 操作，僅本地掃描
- 最活躍：windAILab 189c、digiWindTurbine 158c、RAG_Ultimate 101c、scanmail-bot 40c、citingVerify 30c、infoCard 31c、LabPagesCowork 31c、zImage 28c
- STATUS.yaml 仍有落差（當日/數日內常態工作，未自動處理）：RAG_Ultimate(4d)、windAILab(3d)、digiWindTurbine(3d)、scanmail_bot(2d)、infoCard(2d)、zImage(1d)
- 7 天以上沒 commit 但本月有活動：course-scheduling-system（30d）、englishSpeakingTutor（30d）、citingVerify（17d）、translateGemma（9d）
- attendence 2 個 Few-Shot 實驗 TODO 在 `facial_recognition_test_tool.py:1370` 與 `low_shot_evaluation.py:445`（屬 P2 研究性質）
- InduSpect 5 TODO 皆與 next_milestone「實機端到端測試」對應（簽名板、file_picker、oneStopProcess、資料庫改接），已被追蹤
- windAILab 僅 `useWebSocket.ts:266` 是實際 TODO；其餘 `DEBUG` 字串為 logger/config 預設值，非待辦
- RAG_Ultimate/LabPagesCowork/zImage 關鍵字命中皆為 DEBUG 字串或部落格文內提及，無新增程式碼 TODO
- infoCard 3 個 MCP/本地模型掃描 TODO 持續與 next_milestone 對應，已被追蹤
- 無新開 issue 必要（P0 零件、P1/P2 全數已被現有 next_milestone 追蹤）

