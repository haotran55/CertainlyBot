import os
import random
import time
import requests
import telebot
from telebot.types import Message
from telebot import TeleBot
from flask import Flask, request
from datetime import datetime, timedelta

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
ALLOWED_GROUP_IDS = [-1003329703456, -1002282514761]

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang hoạt động trên Render!"



@bot.message_handler(commands=['like','Like'])
def handle_like(message):
    user_id = message.from_user.id

    # Kiểm tra người dùng đã tham gia kênh chưa
    # Kiểm tra nhóm được phép
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/tranhao1166", parse_mode="HTML")
        return

    # Kiểm tra định dạng lệnh
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Please provide a valid region and UID. Example: /like sg 10000001", parse_mode="HTML")
        return

    region = parts[1]
    uid = parts[2]

    loading_msg = bot.reply_to(message, f"⏳Sending likes to {uid}, please wait...", parse_mode="HTML")

    try:
        api_url = f"https://like-free-fire-nine.vercel.app/like?uid={uid}&server_name={region}"
        response = requests.get(api_url, timeout=15)

        if response.status_code != 200:
            bot.edit_message_text(
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                text="An error occurred. Please check account region or try again later🥲.",
                parse_mode="HTML"
            )
            return

        data = response.json()

        if "LikesGivenByAPI" not in data or "LikesbeforeCommand" not in data or "LikesafterCommand" not in data:
            bot.edit_message_text(
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                text="An error occurred. Please check account region or try again later🥲.",
                parse_mode="HTML"
            )
            return

        if data["LikesGivenByAPI"] == 0:
            bot.edit_message_text(
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                text=f"💔 UID {uid} has already received Max Likes for Today 💔. Please Try a different UID.",
                parse_mode="HTML"
            )
            return

        nickname = data.get("PlayerNickname", "Unknown")
        uid = data.get("UID", "Unknown")
        likes_before = data["LikesbeforeCommand"]
        likes_after = data["LikesafterCommand"]
        likes_given_by_bot = likes_after - likes_before

        reply = (
            f"Player Nickname: {nickname}\n"
            f"Player UID: {uid}\n"
            f"Likes before Command: {likes_before}\n"
            f"Likes after Command: {likes_after}\n"
            f"Likes given by bot: {likes_given_by_bot}\n"
            f"Group: https://t.me/tranhao1166"
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
            text="Đang lỗi hoặc đang bảo trì vui lòng thử lại sau 💔.",
            parse_mode="HTML"
        )



@bot.message_handler(commands=['isbanned','Isbanned'])
def checkban_user(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Please provide a UID to check. Syntax: /isbanned <uid>")
        return

    uid = args[1]
    url = f"https://ban-info.vercel.app/bancheck?uid={uid}&key=tanhao1167"

    try:
        # Gửi tin nhắn đang xử lý
        loading_msg = bot.reply_to(message, "⏳ Checking UID...")

        response = requests.get(url)
        data = response.json()

        status = data.get('status', 'Không xác định')
        uid = data.get('uid', 'Không xác định')
        

        reply = (
            f"🔹 UID: {uid}\n"
            f"✅ Status: {status}\n"
            f"🎉 group: https://t.me/tranhao1166"
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
            text="Đang lỗi hoặc đang bảo trì vui lòng thử lại sau 💔.",
            parse_mode="HTML"
        )

import requests
from io import BytesIO
import threading
import time


API_URL = "https://quanghauquanlybottele.x10.mx/videogai.php"

# 2. Hàm lấy link video từ API
def get_random_video_url():
    try:
        # Gửi yêu cầu đến API với timeout 7 giây để tránh treo bot
        response = requests.get(API_URL, timeout=7)
        if response.status_code == 200:
            data = response.json()
            # Lấy key 'url' từ JSON trả về
            return data.get("url")
        return None
    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")
        return None

# 3. Xử lý lệnh /video
@bot.message_handler(commands=['video'])
def handle_random_video(message):
    # Kiểm tra quyền hoạt động trong nhóm
    if message.chat.id not in ALLOWED_GROUP_IDS:
        error_msg = "⚠️ Bot chỉ hoạt động trong nhóm được cho phép.\nLink: https://t.me/tranhao1166"
        bot.reply_to(message, error_msg)
        return

    # Thông báo cho người dùng là bot đang xử lý (tạo cảm giác mượt mà)
    sent_status = bot.reply_to(message, "⏳ Đang lấy video, đợi xíu nhé...")
    
    username = message.from_user.username
    display_name = f"@{username}" if username else message.from_user.first_name

    # Lấy URL video
    video_url = get_random_video_url()

    if video_url:
        try:
            # Gửi video trực tiếp bằng URL
            bot.send_video(
                chat_id=message.chat.id,
                video=video_url,
                caption=f"✅ Video của bạn đây!\n👤 Yêu cầu bởi: {display_name}",
                reply_to_message_id=message.message_id
            )
            # Xóa tin nhắn "Đang lấy video" sau khi gửi xong cho sạch nhóm
            bot.delete_message(message.chat.id, sent_status.message_id)
            
        except Exception as e:
            print(f"Lỗi Telegram gửi video: {e}")
            bot.edit_message_text(
                "❌ Lỗi: Không thể gửi video này (có thể file quá nặng hoặc lỗi định dạng).",
                message.chat.id, 
                sent_status.message_id
            )
    else:
        bot.edit_message_text(
            "❌ Hiện tại không lấy được video từ server. Thử lại sau nhé!",
            message.chat.id, 
            sent_status.message_id
        )

# 4. Chạ
@bot.message_handler(commands=["admin"])
def cmd_test(message):
    bot.reply_to(message, "<blockquote>✅ Liên Hệ: @tranhao116!</blockquote>", parse_mode="HTML")

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
