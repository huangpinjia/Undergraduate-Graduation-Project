from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import requests
import json
import sqlite3
from datetime import datetime

# 載入 .env
load_dotenv()
GPT_API_BASE = os.getenv("GPT_API_BASE")
GPT_API_KEY = os.getenv("GPT_API_KEY")

# Flask 初始化
app = Flask(__name__, template_folder="templates")

# 每個使用者的記憶體聊天紀錄
chat_history = {}

# 載入 prompt
base_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base_dir, "prompt.txt"), "r", encoding="utf-8") as f:
    base_prompt = f.read()

# 建立 SQLite 資料表（啟動時只跑一次）
def init_db():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# 儲存對話紀錄到 SQLite
def save_chat_to_db(user_id, role, content):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (user_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# 呼叫 GPT API
def ask_gpt_proxy(messages):
    headers = {
        "Content-Type": "application/json",
    }
    if GPT_API_KEY:
        headers["Authorization"] = f"Bearer {GPT_API_KEY}"

    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512
    }

    try:
        response = requests.post(GPT_API_BASE, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ GPT 回應錯誤：{e}"

# 首頁：顯示聊天網頁
@app.route("/")
def index():
    return render_template("index.html")

# 聊天 API 路由
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = data.get("user_id", "web_user")
    user_msg = data.get("message", "")

    if user_id not in chat_history:
        chat_history[user_id] = [{"role": "system", "content": base_prompt}]

    chat_history[user_id].append({"role": "user", "content": user_msg})
    save_chat_to_db(user_id, "user", user_msg)

    ai_reply = ask_gpt_proxy(chat_history[user_id])

    chat_history[user_id].append({"role": "assistant", "content": ai_reply})
    save_chat_to_db(user_id, "assistant", ai_reply)

    return jsonify({"reply": ai_reply})

# 啟動伺服器
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))  # Render 會提供 PORT 環境變數
    app.run(host="0.0.0.0", port=port)

