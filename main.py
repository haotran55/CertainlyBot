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
ALLOWED_GROUP_IDS = [-1002631911391]

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang hoạt động trên Render!"


@bot.message_handler(commands=['like'])
def handle_like(message):
    user_id = message.from_user.id

    # ✅ Giới hạn nhóm sử dụng lệnh
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "<blockquote>Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/tranhao1166</blockquote>", parse_mode="HTML")
        return

    # ✅ Kiểm tra người dùng đã tham gia các nhóm bắt buộc chưa

    # ✅ Kiểm tra cú pháp
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "<blockquote>Vui lòng cung cấp khu vực và UID hợp lệ.\nVí dụ: /like vn 8324665667</blockquote>", parse_mode="HTML")
        return

    region = parts[1]
    uid = parts[2]

    loading_msg = bot.reply_to(message, f"<blockquote>Đang gửi lượt thích tới {uid}, vui lòng đợi...</blockquote>", parse_mode="HTML")

    # ... phần code gửi yêu cầu API và xử lý kết quả như bạn đã viết ...

    try:
        api_url = f"http://160.250.137.144:5001/like?uid={uid}&server_name={region}&key=qqwweerrb"
        response = requests.get(api_url, timeout=15)

        if response.status_code != 200:
            bot.edit_message_text(
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                text="<blockquote>Nhập Sai Hoặc Api Bị Lỗi.</blockquote>",
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
            f"<blockquote>👤 Người Chơi: {nickname}\n"
            f"🆔 UID: {uid}\n"
            f"📉 Like Trước: {likes_before}\n"
            f"📈 Like Sau: {likes_after}\n"
            f"✨ Like Đã Gửi: {likes_given_by_bot}\n"
            f"───────────────────\n"
            f"Thuê Api Liên Hệ: @HaoEsports01</blockquote>"
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
            text="<blockquote>Api Đang Bị Lỗi Vui Lòng Thử Lại Sau.</blockquote>",
            parse_mode="HTML"
        )



@bot.message_handler(commands=['checkban'])
def checkban_user(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Vui lòng nhập UID. Ví dụ: /checkban 12345678")
        return

    uid = args[1]
    url = f"https://check-band-p-3uv9.vercel.app/haoesports-region/ban-info?uid={uid}"

    try:
        # Gửi tin nhắn đang xử lý
        sent = bot.reply_to(message, "⏳ Đang kiểm tra UID...")

        response = requests.get(url)
        data = response.json()

        nickname = data.get('nickname', 'Không có dữ liệu')
        uid = data.get('uid', 'Không Có Uid')
        region = data.get('region', 'Không xác định')
        ban_status = data.get('ban_status', 'Không rõ')
        ban_period = data.get('ban_period')
        copyright_ = data.get('copyright')

        reply = (
            "<blockquote>"
            f"✅ <b>Thông tin người chơi:</b>\n"
            f"• 👤 Nickname: <code>{nickname}</code>\n"
            f"• 🆔 ID: <code>{uid}</code>\n"
            f"• 🌎 Khu vực: <code>{region}</code>\n"
            f"• 🚫 Trạng thái ban: <code>{ban_status}</code>\n"
            f"• ⏳ Thời gian ban: <code>{ban_period if ban_period else 'Không bị ban'}</code>\n"
            f"• ©️ Liên Hệ: <code>{copyright_}</code>"
            "</blockquote>"
        )

        bot.edit_message_text(
            chat_id=sent.chat.id,
            message_id=sent.message_id,
            text=reply,
            parse_mode='HTML'
        )

    except Exception as e:
        bot.edit_message_text(
            chat_id=sent.chat.id,
            message_id=sent.message_id,
            text=f"Đã xảy ra lỗi: {e}"
        )

import requests
from io import BytesIO

def get_random_video():
    try:
        res = requests.get("https://api.ffcommunity.site/randomvideo.php", timeout=5)
        data = res.json()
        return data.get("url")
    except:
        return None

@bot.message_handler(commands=['video'])
def random_video(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot Chỉ Hoạt Động Trong Nhóm Này.\nLink: https://t.me/tranhao1166")
        return

    video_url = get_random_video()
    if video_url:
        try:
            bot.send_chat_action(message.chat.id, "upload_video")
            res = requests.get(video_url, stream=True, timeout=10)
            if res.status_code == 200:
                video_file = BytesIO(res.content)
                video_file.name = "video.mp4"
                bot.send_video(message.chat.id, video=video_file, caption="Video gái xinh By @tranhao116")
            else:
                bot.send_message(message.chat.id, "Không thể tải video từ nguồn.")
        except Exception as e:
            print("Lỗi gửi video:", e)
            bot.send_message(message.chat.id, "Lỗi khi gửi video.")
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
