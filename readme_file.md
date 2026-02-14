# DOF Lab - 劉瑞弘 教授個人網站

這是劉瑞弘教授的個人學術網站，專注於展示生成式AI在自動化領域的研究成果與專案開發。

## 🌟 網站特色

- **現代化設計**: 採用漸變色彩和玻璃透明效果的現代UI設計
- **響應式佈局**: 完美適配桌面、平板、手機等各種裝置
- **動畫效果**: 豐富的滾動動畫和互動效果
- **SEO優化**: 適當的meta標籤和語義化HTML結構
- **快速載入**: 優化的CSS和JavaScript，確保快速載入

## 📁 網站結構

```
doflab.cc/
├── index.html          # 首頁 - 整體介紹與最新消息
├── research.html       # 研究領域 - 四大研究方向詳細介紹
├── publications.html   # 研究成果 - 期刊論文、競賽獲獎、產學合作
├── projects.html       # 專案開發 - 實際技術應用與系統開發
├── about.html         # 關於我 - 個人背景、經歷與專業技能
├── contact.html       # 聯絡方式 - 聯絡資訊與研究生招募
├── css/               # 樣式檔案 (未來擴展用)
├── js/                # JavaScript檔案 (未來擴展用)
├── images/            # 圖片資源 (需要添加)
└── docs/              # 文件資料 (未來擴展用)
```

## 🚀 部署步驟

### 1. GitHub Pages 設置

1. 將所有HTML檔案上傳到您的 `dofliu.github.io` 倉庫
2. 在GitHub倉庫設定中啟用GitHub Pages
3. 選擇 `main` 分支作為來源
4. 網站將自動部署到 `https://dofliu.github.io`

### 2. 域名設定 (doflab.cc)

1. 在您的域名註冊商處設定DNS記錄：
   ```
   類型: CNAME
   名稱: @ (或留空)
   值: dofliu.github.io
   ```

2. 在GitHub倉庫根目錄建立 `CNAME` 檔案，內容為：
   ```
   doflab.cc
   ```

3. 等待DNS生效 (通常需要幾小時到24小時)

### 3. SSL憑證

GitHub Pages會自動為自訂域名提供免費的SSL憑證，確保網站安全。

## 📝 內容更新指南

### 新增研究成果

編輯 `publications.html`，在對應的section中添加新的 `publication-item`:

```html
<div class="publication-item" data-filter="journal">
    <div class="pub-header">
        <div class="pub-date">[年份.月份] 類型</div>
        <div class="pub-type">期刊論文</div>
    </div>
    <div class="pub-title">論文標題</div>
    <div class="pub-journal">期刊名稱</div>
    <div class="pub-description">論文描述</div>
    <div class="pub-tags">
        <span class="tag">標籤1</span>
        <span class="tag">標籤2</span>
    </div>
</div>
```

### 新增專案

編輯 `projects.html`，在適當的category中添加新的 `project-card`:

```html
<div class="project-card">
    <div class="project-header">
        <div class="status-badge status-completed">狀態</div>
        <div class="project-icon">
            <i class="fas fa-icon-name"></i>
        </div>
        <div class="project-title">專案標題</div>
        <div class="project-subtitle">專案副標題</div>
    </div>
    <div class="project-content">
        <div class="project-description">專案描述</div>
        <div class="tech-stack">
            <h4>技術特色：</h4>
            <div class="tech-tags">
                <span class="tech-tag">技術1</span>
                <span class="tech-tag">技術2</span>
            </div>
        </div>
        <div class="project-links">
            <a href="#" class="project-link">
                <i class="fas fa-link"></i>
                連結文字
            </a>
        </div>
    </div>
</div>
```

### 更新聯絡資訊

編輯 `contact.html` 中的聯絡資訊，包括：
- 電子郵件地址
- 辦公室位置
- 電話號碼
- 社交媒體連結

## 🎨 自訂設計

### 更改配色

主要配色在CSS中定義：
- 主色調: `#667eea` (藍色)
- 輔助色調: `#764ba2` (紫色)
- 背景色: `#f8f9fa` (淺灰)

### 添加個人照片

1. 將照片上傳到 `images/` 資料夾
2. 在 `about.html` 中將 `profile-placeholder` 替換為實際照片：

```html
<div class="profile-image">
    <img src="images/profile.jpg" alt="劉瑞弘教授" 
         style="width: 250px; height: 250px; border-radius: 50%; object-fit: cover;">
</div>
```

## 🔧 技術特點

### 使用的技術

- **HTML5**: 語義化標記
- **CSS3**: Flexbox、Grid、動畫效果
- **JavaScript**: 互動功能、動畫控制
- **Font Awesome**: 圖示系統
- **Google Fonts**: 網頁字體 (Segoe UI fallback)

### 瀏覽器支援

- Chrome (推薦)
- Firefox
- Safari
- Edge
- 支援IE11+ (部分功能可能受限)

### 效能優化

- 壓縮的CSS和JavaScript
- 優化的圖片格式
- 懶加載動畫
- 快取友好的資源載入

## 📱 響應式設計

網站針對以下螢幕尺寸進行優化：
- 桌面: 1200px+
- 平板: 768px - 1199px
- 手機: 320px - 767px

### 響應式特色
- 彈性網格佈局
- 可調整的導航選單
- 適應性字體大小
- 觸控友好的按鈕尺寸

## 🔍 SEO 優化

### 已實作的SEO功能
- 語義化HTML結構
- 適當的標題階層 (H1-H6)
- Meta描述和關鍵字
- Open Graph標籤 (可進一步添加)
- 結構化資料 (可進一步添加)

### 建議的SEO改進
1. 添加Google Analytics追蹤碼
2. 建立sitemap.xml
3. 設定robots.txt
4. 添加結構化資料標記
5. 優化圖片alt標籤

## 🌐 多語言支援 (未來功能)

網站架構已預留多語言支援的空間：
- 中文 (繁體) - 目前版本
- 英文 - 可擴展
- 其他語言 - 可依需求添加

## 📊 Google Analytics 設置

在每個HTML檔案的 `<head>` 區域添加：

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🛡️ 安全性考量

### 已實作的安全功能
- HTTPS強制 (透過GitHub Pages)
- 內容安全政策 (CSP) 友好的程式碼
- 無inline JavaScript (除了必要的互動功能)
- 外部連結安全設定

### 建議的安全改進
- 添加CSP headers (透過server設定)
- 實作表單安全驗證
- 定期檢查依賴項安全性

## 🔄 更新維護

### 定期更新項目
1. **研究成果** (publications.html)
   - 新發表的論文
   - 獲得的獎項
   - 完成的專案

2. **專案開發** (projects.html)
   - 進行中的專案狀態
   - 新開始的專案
   - 技術影片連結

3. **首頁動態** (index.html)
   - 最新消息更新
   - 重要公告
   - 招募資訊

### 版本控制建議
- 使用Git進行版本控制
- 為每次重大更新建立標籤
- 保持commit訊息的清晰性

## 📞 技術支援

如需技術協助，請聯絡：
- 網站技術問題: [GitHub Issues](https://github.com/dofliu/dofliu.github.io/issues)
- 內容更新協助: contact@doflab.cc
- 設計調整需求: 透過郵件討論

## 🎯 未來改進計劃

### 短期目標 (1-3個月)
- [ ] 添加個人照片和實驗室照片
- [ ] 整合Google Analytics
- [ ] 建立完整的sitemap
- [ ] 優化載入速度

### 中期目標 (3-6個月)
- [ ] 添加英文版本
- [ ] 建立部落格功能
- [ ] 整合學術資料庫連結
- [ ] 建立線上預約系統

### 長期目標 (6個月以上)
- [ ] 開發互動式專案展示
- [ ] 建立學生作品展示區
- [ ] 整合研究數據視覺化
- [ ] 建立協作平台

## 📋 檢查清單

部署前請確認：
- [ ] 所有HTML檔案語法正確
- [ ] 連結測試完成
- [ ] 響應式設計在各裝置正常
- [ ] 圖片和影片連結有效
- [ ] 聯絡資訊正確無誤
- [ ] GitHub Pages設定完成
- [ ] 自訂域名設定完成
- [ ] SSL憑證運作正常

## 🏆 網站特色總結

這個網站的設計重點在於：

1. **專業形象**: 體現學術研究的專業性與創新性
2. **使用者體驗**: 直觀的導航和豐富的互動效果
3. **內容展示**: 清晰地展示研究成果和技術能力
4. **招募功能**: 有效地吸引潛在的研究合作者和學生
5. **技術前瞻**: 展現對最新技術趨勢的掌握

透過這個網站，訪客可以：
- 快速了解您的研究方向和專業能力
- 查看具體的研究成果和專案實例
- 輕鬆找到聯絡方式進行合作洽談
- 了解研究生招募的相關資訊

## 📞 聯絡資訊

如有任何問題或需要進一步的技術支援，歡迎聯絡：

**劉瑞弘教授 DOF Lab**
- 📧 Email: contact@doflab.cc
- 🏢 辦公室: G309
- 🔬 研究室: 瘋風機 Wind Turbine Chaser
- 🌐 網站: https://doflab.cc
- 📱 GitHub: https://github.com/dofliu

---

*最後更新: 2025年9月*
*版本: 1.0.0*
*作者: DOF Lab*
