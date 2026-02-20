import os
import time
import requests
import telebot
from flask import Flask, request
from telebot.types import Message

# ================== CONFIG ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

if not BOT_TOKEN or not WEBHOOK_URL:
    raise Exception("❌ Missing BOT_TOKEN or WEBHOOK_URL")

# 👉 GROUP ĐƯỢC PHÉP DÙNG LỆNH
ALLOWED_GROUP_ID = -1003616607301  # đổi thành group của bạn

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

# Lưu ngày dùng lệnh của user (reset nếu server return

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

# ================== /LIKES COMMAND ==================
@bot.message_handler(commands=['likes'])
def like_handler(message: Message):
    # ❌ Bỏ qua tin nhắn private
    if message.chat.type == "private":
        return

    # ❌ Bỏ qua bot khác
    if message.from_user.is_bot:
        return

    # ❌ Chỉ cho phép trong group chỉ định
    if message.chat.id != ALLOWED_GROUP_ID:
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Usage: /likes UID")
        return

    uid = parts[1]

    # ❌ UID phải là số
    if not uid.isdigit():
        bot.reply_to(message, "❌ UID must contain numbers only.")
        return

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
            "API not responding, please try again later.",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id
        )
        return

    status = data.get("status")

    # ❌ API lỗi thật sự
    if not data or status not in [1, 2]:
        bot.edit_message_text(
            "Token is malfunctioning or failing to load. ",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id
        )
        return

    

    name = safe_get(data, 'PlayerNickname')
    uid_str = safe_get(data, 'UID')
    like_before = safe_get(data, 'LikesbeforeCommand')
    like_after = safe_get(data, 'LikesafterCommand')
    like_sent = extract_number(data.get('LikesGivenByAPI'))
    level_st = safe_get(data, 'Level')
    region_vcl = safe_get(data, 'Region')

    reply_text = (
        "✅ Likes Sent Successfully\n\n"
        f"👤Name: {name}\n"
        f"🆔UID: {uid_str}\n"
        f"🔥Level: {level_st}\n"
        f"🌍Region: {region_vcl}\n\n"
        f"📉Likes Before: {like_before}\n"
        f"📈Likes After: {like_after}\n"
        f"❤️Likes Sent: {like_sent}\n\n"
        "Buy Likes Contact: @nhathaov"
    )

    # ⚠️ Nếu API báo đã đạt giới hạn
    if status == 2:
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
    bot.set_webhook(url=f"{WEBHOOK_URL.rstrip('/')}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
