import os
import threading
import requests
import telebot
import requests
from telebot import TeleBot
from telebot.types import Message  # ✅ Import thêm dòng này
from flask import Flask, request
from datetime import datetime
from io import BytesIO
import requests
from io import BytesIO

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
ALLOWED_GROUP_IDS = [-1002639856138, -1002557075563]

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang hoạt động trên Render!"

@bot.message_handler(commands=['like'])
def handle_like(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "<blockquote>Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/HaoEsport01</blockquote>", parse_mode="HTML")
        return
        

    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "<blockquote>Vui lòng cung cấp khu vực và UID hợp lệ.\nVí dụ: /like vn 8324665667</blockquote>", parse_mode="HTML")
        return

    region = parts[1]
    uid = parts[2]

    loading_msg = bot.reply_to(message, f"<blockquote>Đang gửi lượt thích tới {uid}, vui lòng đợi...</blockquote>", parse_mode="HTML")

    try:
        api_url = f"https://freefirelike-api.onrender.com/like?uid={uid}&server_name={region}&key=qqwweerrb"
        response = requests.get(api_url, timeout=10)

        if response.status_code != 200:
            bot.edit_message_text(
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                text="<blockquote>Đã xảy ra lỗi. Vui lòng kiểm tra khu vực tài khoản hoặc thử lại sau.</blockquote>",
                parse_mode="HTML"
            )
            return

        data = response.json()

        if "LikesGivenByAPI" not in data or "LikesbeforeCommand" not in data or "LikesafterCommand" not in data:
            bot.edit_message_text(
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                text="<blockquote>Đã xảy ra lỗi. Vui lòng kiểm tra khu vực tài khoản hoặc thử lại sau.</blockquote>",
                parse_mode="HTML"
            )
            return

        if data["LikesGivenByAPI"] == 0:
            bot.edit_message_text(
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                text=f"<blockquote>💔 UID {uid} đã nhận đủ lượt thích hôm nay. Vui lòng thử UID khác.</blockquote>",
                parse_mode="HTML"
            )
            return

        nickname = data.get("PlayerNickname", "Unknown")
        uid = data.get("UID", "Unknown")
        likes_before = data["LikesbeforeCommand"]
        likes_after = data["LikesafterCommand"]
        likes_given_by_bot = likes_after - likes_before

        reply = (
            f"<blockquote>✅ BUFF LIKE THÀNH CÔNG\n"
            f"👤 Người Chơi: {nickname}\n"
            f"🆔 UID: {uid}\n"
            f"📉 Like Trước: {likes_before}\n"
            f"📈 Like Sau: {likes_after}\n"
            f"👍 Like Đã Gửi: {likes_given_by_bot}\n"
            f"───────────────────\n"
            f"Liên Hệ: @HaoEsports01</blockquote>"
        )

        bot.edit_message_text(
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            text=reply,
            parse_mode="HTML"
        )

    except Exception:
        bot.edit_message_text(
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            text="<blockquote>Đã xảy ra lỗi. Vui lòng kiểm tra khu vực tài khoản hoặc thử lại sau.</blockquote>",
            parse_mode="HTML"
        )

import time
@bot.message_handler(commands=['follow', 'fl', 'tiktok'])
def handle_follow_command(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập username TikTok.")
            return

        username = parts[1].strip().replace("@", "")

        info_url = f"http://145.223.80.56:5009/info_tiktok?username={username}"
        buff_url = f"https://tiktok-follow-api-obiyeuem.onrender.com/follow?username={username}"

        # Lấy số follow trước
        res_before = requests.get(info_url, timeout=999).json()
        follow_before = res_before["followers"]

        # Gửi ảnh loading
        loading_msg = bot.send_photo(
            message.chat.id,
            photo="https://i.imgur.com/9p6ZiSb.png",  # fix lại link hình
            caption=(
                f"<blockquote>⏳ Đang gửi buff follow cho @{username}...\n"
                f"Follower trước: {follow_before}</blockquote>"
            ),
            parse_mode='HTML'
        )

        # Gửi request buff
        requests.get(buff_url, timeout=999)

        # Chờ một chút (1-2s cho server cập nhật)
        time.sleep(2)

        # Lấy lại số follow sau
        res_after = requests.get(info_url, timeout=999).json()
        follow_after = res_after["followers"]

        tang = follow_after - follow_before

        # Cập nhật lại caption ảnh
        bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=loading_msg.message_id,
            caption=(
                f"<blockquote>✅ Đã buff follow cho @{username}!\n"
                f"🔹 Follower trước: {follow_before}\n"
                f"🔸 Follower sau: {follow_after}\n"
                f"✨ Đã tăng: +{tang} follow</blockquote>"
            ),
            parse_mode='HTML'
        )

    except Exception as e:
        bot.reply_to(message, f"🚨 Lỗi: {e}")

#hmm
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
