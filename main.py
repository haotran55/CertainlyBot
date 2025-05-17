import os
import time
import requests
import telebot
from telebot.types import Message
from telebot import TeleBot
from flask import Flask, request
from datetime import datetime, timedelta

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
ALLOWED_GROUP_IDS = [-1002639856138]

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang hoạt động trên Render!"


user_last_like_time = {}

# thời gian chờ (giây)
LIKE_COOLDOWN = 60

@bot.message_handler(commands=['like'])
def like_handler(message: Message):
    user_id = message.from_user.id
    current_time = time.time()

    last_time = user_last_like_time.get(user_id, 0)
    time_diff = current_time - last_time

    if time_diff < LIKE_COOLDOWN:
        wait_time = int(LIKE_COOLDOWN - time_diff)
        bot.reply_to(message, f"<blockquote>⏳ Vui lòng chờ {wait_time} giây trước khi dùng lại lệnh này.</blockquote>", parse_mode="HTML")
        return

    command_parts = message.text.split()
    if len(command_parts) != 3:
        bot.reply_to(message, "<blockquote>⚠️ Cách dùng đúng: /like {region} {uid}\nVí dụ: /like vn 1733997441</blockquote>", parse_mode="HTML")
        return

    region = command_parts[1]
    uid = command_parts[2]

    user_last_like_time[user_id] = current_time  # cập nhật thời gian sử dụng

    urllike = f"https://freefirelike-api.onrender.com/like?uid={uid}&server_name={region}&key=qqwweerrb"

    def safe_get(data, key):
        value = data.get(key)
        return value if value not in [None, ""] else "Không xác định"

    def extract_number(text):
        if not text:
            return "Không xác định"
        for part in text.split():
            if part.isdigit():
                return part
        return "Không xác định"

    loading_msg = bot.reply_to(message, "⏳", parse_mode="HTML")


    try:
        response = requests.get(urllike, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        bot.edit_message_text("<blockquote>❌ Server đang quá tải, vui lòng thử lại sau.</blockquote>",
                              chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")
        return
    except ValueError:
        bot.edit_message_text("<blockquote>❌ Phản hồi từ server không hợp lệ.</blockquote>",
                              chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")
        return

    status_code = data.get("status")

    reply_text = (
        "<blockquote>"
        "✅ BUFF LIKE THÀNH CÔNG\n"
        f"╭👤 Name: {safe_get(data, 'PlayerNickname')}\n"
        f"├🆔 UID: {safe_get(data, 'uid')}\n"
        f"├🌏 Region: {region}\n"
        f"├📉 Like trước đó: {safe_get(data, 'likes_before')}\n"
        f"├📈 Like sau khi gửi: {safe_get(data, 'likes_after')}\n"
        f"╰👍 Like được gửi: {extract_number(data.get('likes_given'))}"
    )

    if status_code == 2:
        reply_text += "\n⚠️ Giới hạn like hôm nay, mai hãy thử lại sau."

    reply_text += "</blockquote>"

    bot.edit_message_text(reply_text, chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")


@bot.message_handler(commands=["admin"])
def cmd_test(message):
    bot.reply_to(message, "<blockquote>✅ Liên Hệ: @HaoEsports01!</blockquote>", parse_mode="HTML")

@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok', 200

#cc
if __name__ == "__main__":
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
    if not WEBHOOK_URL:
        raise Exception("Thiếu biến môi trường WEBHOOK_URL")

    # Xóa webhook cũ và thiết lập webhook mới
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

    # Chạy Flask (webhook listener)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
