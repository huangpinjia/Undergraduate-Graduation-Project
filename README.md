# AIBuddy Web

AIBuddy Web 是一款基於 Flask 的 GPT 聊天應用，具備簡易網頁介面，支援與 OpenAI API 對話並儲存聊天紀錄。適合自架部署於 Render 或本地端測試。

## 🔧 功能特色

- 💬 基於 ChatGPT 的聊天互動功能
- 🗂 聊天紀錄儲存於 SQLite 資料庫
- 🖥 提供簡單網頁介面 (`index.html`)
- 🧠 可設定 prompt 作為系統初始訊息
- 🌐 支援部署於 Render 或本地伺服器

## 📁 專案結構

```
AIBuddy_web/
│
├── app.py                # 主程式：Flask 應用與 GPT 對接邏輯
├── .env                  # API 金鑰與伺服器設定（自行建立）
├── chat_history.db       # 聊天紀錄資料庫（執行後自動建立）
├── prompt_02.txt         # 系統提示詞（載入於每段對話開頭）
├── requirements.txt      # Python 相依套件
├── render.yaml           # Render 平台部署設定
└── templates/
    └── index.html        # 前端頁面
```
## 🧪 使用方式

- 在聊天視窗中輸入問題，例如：「什麼是感知器？」
- 機器人會根據教學順序逐步引導，並使用生活化比喻說明。
- 適合搭配投影、課堂講解或小組討論使用。

---

## 🔧 目前開發狀態

- ✅ 第一版原型已完成：可正常互動、支援五大主題。

- 🛠️ 待優化項目：
  - 多人切換與持久記憶機制
  - 主題進度追蹤與歷程分析介面
  - 課程素材可視化與動畫支援