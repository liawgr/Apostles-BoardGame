# 🕊️ 《使徒:大使命》(Apostles: The Great Commission)

> **一款 1 ~ 4 人深度合作、信仰拓荒與領受大使命的史詩敘事桌遊。**  
> *「所以，你們要去，使萬民作我的門徒，奉父、子、聖靈的名給他們施洗。凡我所吩咐你們的，都教訓他們遵守，我就常與你們同在，直到世界的末了。」——《馬太福音 28:19-20》*

---

## 🎯 快速展示導覽 (Quick Showcase)

- 🌐 **專案官方展示主頁**：[index.html](index.html)
- 🚀 **10 分鐘開箱速成手冊 (新手推薦)**：[docs/quickstart.html](docs/quickstart.html) | [Markdown 版](docs/quickstart.md)
- 📜 **官方全彩標準規則手冊**：[docs/rulebook.html](docs/rulebook.html) | [Markdown 版](docs/rulebook.md)
- 📖 **專案展示提案手冊 (3 分鐘掌握全案)**：[docs/PROJECT_PITCH.md](docs/PROJECT_PITCH.md)
- 📋 **完整遊戲企劃文件 (GDD v1.0 全案完成)**：[docs/GDD.md](docs/GDD.md)
- 🖨️ **實體卡牌預覽與 A4 列印工具**：[tools/previewer.html](tools/previewer.html)（支援瀏覽器直接預覽與 Ctrl+P 快速打樣列印）
- 📦 **全套實體全盒實體配件完整清單 (35項物料)**：[data/components.csv](data/components.csv)

---

## 📁 專案目錄結構

`	ext
BoardGameProject/
├── index.html                  # 專案官方主頁（含全特色導覽與規則速覽）
├── docs/                       # 企劃與規則核心
│   ├── quickstart.html         # 🚀 10 分鐘新手開箱速成手冊（網頁全彩版）
│   ├── quickstart.md           # 10 分鐘新手開箱速成手冊（Markdown 版）
│   ├── rulebook.html           # 📜 官方正式全彩手冊（網頁版，支援列印/另存 PDF）
│   ├── rulebook.md             # 官方正式規則手冊（Markdown 版）
│   ├── PROJECT_PITCH.md        # ⭐ 專案展示與提案概覽手冊
│   ├── GDD.md                  # 遊戲設計核心文件（完整系統與哲學規則）
│   └── design_notes.md         # 設計日誌與靈感庫
├── data/                       # 遊戲資料庫
│   ├── cards.csv               # 通用卡牌資料表（角色、恩賜、神蹟、誘惑）
│   ├── decks/                  # 模組化地區專屬牌堆 (三大宣教區)
│   ├── components.csv          # 全盒實體配件完整清單
│   └── balance_guide.md        # 數值平衡指南
├── playtesting/                # 測試與回饋
│   ├── test_feedback_template.md # 盲測試玩回饋問卷
│   └── playtest_log.md         # 測試場次詳細日誌
├── assets/                     # 美術與打樣資源
│   └── print_and_play/         # 即印即玩 (PnP) 打樣規範
└── tools/                      # 工具腳本
    ├── previewer.html          # ⭐ 卡牌視覺化預覽與 A4 列印網頁工具
    ├── simulate_playtest.py    # 全流程實戰跑測模擬推演引擎
    └── card_generator.py       # Python 數值統計分析腳本
`

---

## 🚀 如何開啟與運行

本專案所有的網頁展示、規則書與卡牌列印工具皆為**純靜態網頁（Zero-dependency HTML5/CSS/JS）**：
1. **直接開啟**：用任何瀏覽器（Chrome, Edge, Safari, Firefox）雙擊開啟 index.html 即可瀏覽！
2. **啟動 GitHub Pages**：若將本倉庫上傳至 GitHub，可在倉庫的 **Settings -> Pages** 中選擇 main 分支並保存，即可免費獲得線上公開網址！
