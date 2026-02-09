import os
import requests
import telebot
from flask import Flask, request
from datetime import datetime
import pytz

# ================== CONFIG ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

if not BOT_TOKEN or not WEBHOOK_URL:
    raise Exception("❌ Thiếu BOT_TOKEN hoặc WEBHOOK_URL")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

# ================== BASIC ROUTES ==================
@app.route("/")
def home():
    return "Bot is running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# ================== /LIKE COMMAND ==================

ALLOWED_GROUP_ID = -1003616607301


import time
import requests
from telebot.types import Message

# 👉 PUT YOUR GROUP ID HERE
ALLOWED_GROUP_ID = -1001234567890  # change this

user_last_like_day = {}

@bot.message_handler(commands=['likes'])
def like_handler(message: Message):
    # ❌ Ignore private chats
    if message.chat.type == "private":
        return

    # ❌ Only allow specific group
    if message.chat.id != ALLOWED_GROUP_ID:
        return

    user_id = message.from_user.id
    current_day = time.strftime("%Y-%m-%d", time.gmtime())

    # ⛔ Limit: once per day per user
    if user_last_like_day.get(user_id) == current_day:
        bot.reply_to(message, "⏳ You can only use this command once per day.")
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Usage: /likes UID")
        return

    uid = parts[1]
    api_url = f"https://like-free-firee.vercel.app/like?uid={uid}&server_name=vn"

    try:
        loading_msg = bot.reply_to(message, "⏳ Sending likes, please wait...")
    except:
        return

    def safe_get(data, key):
        value = data.get(key)
        return str(value) if value not in [None, "", "null"] else "Unknown"

    def extract_number(text):
        if isinstance(text, int):
            return str(text)
        for part in str(text).split():
            if part.isdigit():
                return part
        return "Unknown"

    try:
        response = requests.get(api_url, timeout=15)
        data = response.json()
    except:
        bot.edit_message_text(
            "❌ Failed to connect to API. Try again later.",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id
        )
        return

    if not data or data.get("status") != 1:
        bot.edit_message_text(
            "Your likes have reached their maximum. Please try again tomorrow. 💔",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id
        )
        return

    # ✅ Save usage day
    user_last_like_day[user_id] = current_day

    name = safe_get(data, 'PlayerNickname')
    uid_str = safe_get(data, 'UID')
    like_before = safe_get(data, 'LikesbeforeCommand')
    like_after = safe_get(data, 'LikesafterCommand')
    like_sent = extract_number(data.get('LikesGivenByAPI'))

    reply_text = (
        "✅ Likes Send Success\n\n"
        f"👤 Name: {name}\n"
        f"🆔 UID: {uid_str}\n"
        f"🌏 Region: vn\n"
        f"📉 Likes Before: {like_before}\n"
        f"📈 Likes After: {like_after}\n"
        f"✅ Likes Sent: {like_sent}"
    )

    if data.get("status") == 2:
        reply_text += "\n⚠️ Daily like limit reached for this account."

    try:
        bot.edit_message_text(
            reply_text,
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id
        )
    except Exception as e:
        print(f"Error sending result: {e}")



# ================== START APP ==================
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
