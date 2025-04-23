import os
import requests
from telebot import TeleBot, types
from flask import Flask, request
from datetime import datetime
from io import BytesIO

# ENV
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # VD: https://your-render-url.onrender.com
bot = TeleBot(BOT_TOKEN)
ALLOWED_GROUP_IDS = [-1002639856138]

# Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot đang hoạt động trên Render!"


@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

def get_random_video():
    try:
        res = requests.get("https://api.ffcommunity.site/randomvideo.php", timeout=5)
        return res.json().get("url")
    except:
        return None

@bot.message_handler(commands=['video'])
def random_video(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot Chỉ Hoạt Động Trong Nhóm Này.\nLink: https://t.me/HaoEsport01")
        return

    video_url = get_random_video()
    if video_url:
        try:
            bot.send_chat_action(message.chat.id, "upload_video")
            bot.send_video(message.chat.id, video=video_url, caption="Video gái xinh By @CertainllyBot")
        except:
            bot.send_message(message.chat.id, "Lỗi khi gửi video.")
    else:
        bot.send_message(message.chat.id, "Không lấy được video, thử lại sau nhé!")

@bot.message_handler(content_types=['new_chat_members'])
def welcome_user(message):
    for user in message.new_chat_members:
        uid = user.id
        username = f"@{user.username}" if user.username else "@None"
        full_name = f"{user.first_name} {user.last_name or ''}".strip()
        time_joined = datetime.now().strftime("%H:%M:%S | %d/%m/%Y")

        video_url = get_random_video()
        if not video_url:
            bot.send_message(message.chat.id, f"Chào mừng {full_name} nhé! (Không lấy được video)")
            return

        try:
            video_resp = requests.get(video_url)
            video_file = BytesIO(video_resp.content)
            video_file.name = "video.mp4"

            caption = f"""🖐 Hello <b>{full_name}</b>
├ UID: <code>{uid}</code>
├ Username: {username}
├ Thời Gian: <code>{time_joined}</code>
└ <i>Chào Mừng Bạn Đã Tham Gia Nhóm <b>Box Hào Esports</b></i>
Gõ /bot Để Xem Lệnh Bot Hỗ Trợ Nhé!"""

            bot.send_video(
                chat_id=message.chat.id,
                video=video_file,
                caption=caption,
                parse_mode="HTML"
            )
        except:
            bot.send_message(message.chat.id, f"Chào mừng {full_name} nhé! (Gửi video lỗi)")

# Khởi động webhook
if __name__ == '__main__':
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
    if not WEBHOOK_URL:
        raise Exception("Thiếu biến môi trường WEBHOOK_URL")

    # Xóa webhook cũ (nếu có) rồi đặt webhook mới
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    
    # Chạy Flask (webhook listener)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
