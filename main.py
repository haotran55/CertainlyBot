from flask import Flask, request
import telebot
import openai
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

import random
import string
import json
DATA_FILE = "data.json"
history = []
user_turns = {}
profit = {}

# ---------------------- CORE FUNCTIONS ----------------------

def generate_nap_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def analyze_md5(md5_hash):
    global history

    # Thuật toán 1: 2 ký tự cuối
    alg1 = int(md5_hash[-2:], 16) % 2
    result1 = "Tài" if alg1 == 0 else "Xỉu"

    # Thuật toán 2: Tổng 4 byte đầu MD5
    total_hex = sum(int(md5_hash[i:i+2], 16) for i in range(0, 8, 2))
    result2 = "Tài" if total_hex % 2 == 0 else "Xỉu"

    # Thuật toán 3: Tổng toàn bộ MD5 chia 5
    full_sum = sum(int(md5_hash[i:i+2], 16) for i in range(0, 32, 2))
    result3 = "Tài" if full_sum % 5 < 3 else "Xỉu"

    results = [result1, result2, result3]
    final_result = max(set(results), key=results.count)

    prediction = {
        "md5": md5_hash,
        "dự đoán": final_result,
        "thuật toán 1": result1,
        "thuật toán 2": result2,
        "thuật toán 3": result3,
        "kết quả thực tế": None
    }

    history.append(prediction)

    return (
        f"<blockquote>"
        f"📊 <strong>PHÂN TÍCH PHIÊN TÀI XỈU MD5:</strong><br>"
        f"<code>{md5_hash}</code><br><br>"
        f"🧠 <strong>Thuật toán 1</strong> (2 ký tự cuối): {result1}<br>"
        f"🧠 <strong>Thuật toán 2</strong> (4 byte đầu): {result2}<br>"
        f"🧠 <strong>Thuật toán 3</strong> (Tổng MD5): {result3}<br><br>"
        f"✅ <strong>Kết luận:</strong> {final_result} 🔥"
        f"</blockquote>"
    )


 
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({"user_turns": user_turns, "history": history, "profit": profit}, f)

def load_data():
    global user_turns, history, profit
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            user_turns = data.get("user_turns", {})
            history = data.get("history", [])
            profit = data.get("profit", {})
    except (FileNotFoundError, json.JSONDecodeError):
        user_turns = {}
        history = []
        profit = {}
        save_data()


load_data()

@bot.message_handler(commands=['check'])
def handle_check(message):
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "❌ Cú pháp sai. Dùng: /check <md5>")
            return

        md5_hash = args[1].strip().lower()
        if len(md5_hash) != 32 or not all(c in string.hexdigits for c in md5_hash):
            bot.reply_to(message, "❌ MD5 không hợp lệ. Phải là chuỗi 32 ký tự hex.")
            return

        result_msg = analyze_md5(md5_hash)
        bot.reply_to(message, result_msg, parse_mode="HTML")


    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {e}")

@bot.message_handler(commands=['ask'])
def handle_hoi(message):
    text = message.text[len('/ask '):].strip()
    

    # Nếu hợp lệ, cho spam
    if text:
        url = f"https://dichvukey.site/apishare/hoi.php?text={text}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("message", "Không có phản hồi.")
        else:
            reply = "Lỗi."
    else:
        reply = "Lệnh Ví Dụ : /ask xin chào."
    bot.reply_to(message, reply)


@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok', 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
