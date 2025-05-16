import os
import time
import requests
import telebot
from telebot import TeleBot
from flask import Flask, request
from datetime import datetime, timedelta

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 5000))

bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)

ALLOWED_GROUP_IDS = [-1002639856138, -1002557075563]
ADMIN_IDS = [123456789]  # Thay ID admin thật

@app.route("/")
def home():
    return "Bot đang chạy!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=["like"])
def cmd_like(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "<blockquote>❌ Bot chỉ hoạt động trong nhóm cho phép.</blockquote>", parse_mode="HTML")
        return

    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "<blockquote>⚠️ Vui lòng nhập đúng cú pháp:\n/like &lt;khu vực&gt; &lt;uid&gt;</blockquote>", parse_mode="HTML")
        return

    region = parts[1]
    uid = parts[2]

    loading_msg = bot.reply_to(message, f"<blockquote>⏳ Đang gửi lượt thích tới UID {uid}...</blockquote>", parse_mode="HTML")

    try:
        api_url = f"https://freefirelike-api.onrender.com/like?uid={uid}&server_name={region}&key=qqwweerrb"
        resp = requests.get(api_url, timeout=10)
        if resp.status_code != 200:
            bot.edit_message_text("<blockquote>❌ Lỗi khi gửi lượt thích, thử lại sau.</blockquote>",
                                  chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")
            return

        data = resp.json()
        if data.get("LikesGivenByAPI", 0) == 0:
            bot.edit_message_text(f"<blockquote>💔 UID {uid} đã nhận đủ lượt thích hôm nay.</blockquote>",
                                  chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")
            return

        nickname = data.get("PlayerNickname", "Unknown")
        likes_before = data.get("LikesbeforeCommand", 0)
        likes_after = data.get("LikesafterCommand", 0)
        likes_given = likes_after - likes_before

        reply = (
            f"<blockquote>✅ BUFF LIKE THÀNH CÔNG\n"
            f"👤 Người Chơi: {nickname}\n"
            f"🆔 UID: {uid}\n"
            f"📉 Like Trước: {likes_before}\n"
            f"📈 Like Sau: {likes_after}\n"
            f"👍 Like Đã Gửi: {likes_given}\n"
            f"───────────────\n"
            f"Liên hệ: @HaoEsports01</blockquote>"
        )

        bot.edit_message_text(reply, chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")

    except Exception as e:
        bot.edit_message_text(f"<blockquote>❌ Đã xảy ra lỗi: {e}</blockquote>",
                              chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")

@bot.message_handler(commands=["admin"])
def cmd_test(message):
    bot.reply_to(message, "<blockquote>✅ Liên Hệ: @HaoEsports01!</blockquote>", parse_mode="HTML")

if __name__ == "__main__":
    if not BOT_TOKEN or not WEBHOOK_URL:
        raise Exception("Bạn cần đặt biến môi trường BOT_TOKEN và WEBHOOK_URL")

    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

    print("Bot đã sẵn sàng và đang chạy webhook...")

    app.run(host="0.0.0.0", port=PORT)
