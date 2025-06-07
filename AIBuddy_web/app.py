from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import json
import requests
from datetime import datetime

# 初始化
load_dotenv()
GPT_API_BASE = os.getenv("GPT_API_BASE")
GPT_API_KEY = os.getenv("GPT_API_KEY")

app = Flask(__name__, template_folder="templates")
base_dir = os.path.dirname(os.path.abspath(__file__))

# 載入 system prompt 範本
with open(os.path.join(base_dir, "prompt_02.txt"), "r", encoding="utf-8") as f:
    base_prompt_template = f.read()

# 動態主題提示組合
def generate_system_prompt(topic=None):
    if topic:
        topic_notice = f"""
請特別注意：
- 僅針對「{topic}」主題進行回應；
- 不要提及或引導至其他主題；
- 若學生答不出，也請繼續以「{topic}」為主軸鼓勵與引導；
"""
    else:
        topic_notice = """
請注意：目前學生尚未明確表達主題，請使用開放式語氣鼓勵學生提出目標，不可主動指定主題。
"""
    return base_prompt_template + topic_notice

# 載入主題模仿資料
topic_files = {
    "感知器": "感知器.json",
    "線性回歸": "線性回歸.json",
    "決策樹": "決策樹.json",
    "KNN": "KNN.json"
}
topic_dialogs = {}
for topic, file in topic_files.items():
    file_path = os.path.join(base_dir, "data", file)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            topic_dialogs[topic] = json.load(f)

# 儲存使用者對話
def save_chat_to_json(user_id, role, content):
    folder = os.path.join(base_dir, "Conversation_Record")
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{user_id}.json")
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
        data.append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content
        })
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ 儲存錯誤：{e}")

# 主題辨識
def detect_topic(user_input):
    if any(word in user_input for word in ["感知器", "分類", "激勵函數"]):
        return "感知器"
    elif any(word in user_input for word in ["斜率", "線性", "趨勢線"]):
        return "線性回歸"
    elif any(word in user_input for word in ["節點", "決策樹", "分裂"]):
        return "決策樹"
    elif any(word in user_input for word in ["K", "距離", "近鄰"]):
        return "KNN"
    else:
        return None

# 查找相似語句
def find_similar_from_topic(user_input, topic):
    if topic not in topic_dialogs:
        return None, None
    for item in topic_dialogs[topic]:
        if user_input[:10] in item["user"]:
            return {"role": "user", "content": item["user"]}, {"role": "assistant", "content": item["bot"]}
    return None, None

# 產生仿語氣任務說明
def generate_mimic_prompt(sim_user, sim_bot, user_msg):
    return f"""
請模仿以下對話的語氣與風格來回應學生的問題，但請依照新內容進行回答，避免重複原句。

【範例使用者】：{sim_user['content']}
【範例機器人】：{sim_bot['content']}

【現在學生的提問】：{user_msg}
請用相似語氣與節奏進行引導回答。
"""

# 呼叫 GPT
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

# 首頁
@app.route("/")
def index():
    return render_template("index.html")

# 對話處理
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = data.get("user_id", "web_user")
    user_msg = data.get("message", "").strip()

    topic = detect_topic(user_msg)
    system_prompt = generate_system_prompt(topic)
    messages = [{"role": "system", "content": system_prompt}]

    sim_user, sim_bot = None, None
    if topic:
        sim_user, sim_bot = find_similar_from_topic(user_msg, topic)

    if sim_user and sim_bot:
        mimic_task = generate_mimic_prompt(sim_user, sim_bot, user_msg)
        messages.append({"role": "user", "content": mimic_task})
    else:
        messages.append({"role": "user", "content": user_msg})

    save_chat_to_json(user_id, "user", user_msg)
    ai_reply = ask_gpt_proxy(messages)
    save_chat_to_json(user_id, "assistant", ai_reply)

    return jsonify({"reply": ai_reply})

# 啟動
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
