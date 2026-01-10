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

def get_random_video():
    try:
        # Tăng timeout để tránh lỗi kết nối chậm
        res = requests.get("https://quanghauquanlybottele.x10.mx/videogai.php", timeout=10)
        data = res.json()
        # Sửa lại đúng key "video_url" từ API
        return data.get("video_url")
    except Exception as e:
        print(f"Lỗi API: {e}")
        return None

def delete_message_after_time(chat_id, message_id, delay):
    """Hàm chạy ngầm để xóa tin nhắn sau một khoảng thời gian"""
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Không thể xóa tin nhắn: {e}")

@bot.message_handler(commands=['video'])
def random_video(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot Chỉ Hoạt Động Trong Nhóm Này.\nLink: https://t.me/tranhao1166")
        return

    video_url = get_random_video()
    if video_url:
        try:
            bot.send_chat_action(message.chat.id, "upload_video")
            res = requests.get(video_url, stream=True, timeout=20)
            
            if res.status_code == 200:
                video_file = BytesIO(res.content)
                video_file.name = "video.mp4"
                
                # Gửi video và nhận lại thông tin tin nhắn đã gửi
                sent_msg = bot.send_video(
                    message.chat.id, 
                    video=video_file, 
                    caption="Video gái xinh By @tranhao116\n(Video này sẽ tự xóa sau 5 phút)"
                )
                
                # Tạo một luồng (thread) riêng để đếm ngược 5 phút (300 giây) rồi xóa
                threading.Thread(target=delete_message_after_time, args=(message.chat.id, sent_msg.message_id, 300)).start()
                
            else:
                bot.send_message(message.chat.id, "Không thể tải video từ nguồn.")
        except Exception as e:
            print("Lỗi gửi video:", e)
            bot.send_message(message.chat.id, "Lỗi khi xử lý video.")
    else:
        bot.send_message(message.chat.id, "Không lấy được video, thử lại sau nhé!")
        
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
