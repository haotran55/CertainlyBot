import os
import threading
import requests
from telebot import TeleBot
from flask import Flask
from datetime import datetime
from keep_alive import keep_alive
from io import BytesIO

# Giữ Flask sống
keep_alive()

# Lấy token từ biến môi trường
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = TeleBot(BOT_TOKEN)
# ID nhóm được phép sử dụng bot
ALLOWED_GROUP_ID = -1002639856138
GROUP_LINK = "https://t.me/HaoEsport01"

def group_only(func):
    def wrapper(message):
        if message.chat.id == ALLOWED_GROUP_ID:
            return func(message)
        else:
            bot.reply_to(
                message,
                f"❗ Bot chỉ hoạt động trong nhóm này: <a href=\"{GROUP_LINK}\">Tại Đây</a>",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
    return wrapper

#video
# Hàm lấy video từ API
def get_random_video():
    try:
        res = requests.get("https://api.ffcommunity.site/randomvideo.php", timeout=5)
        data = res.json()
        return data.get("url")
    except:
        return None

@bot.message_handler(commands=['video'])
@group_only
def random_video(message):
    video_url = get_random_video()
    if video_url:
        try:
            bot.send_chat_action(message.chat.id, "upload_video")
            bot.send_video(
                message.chat.id,
                video=video_url,
                caption="Video gái xinh By @CertainllyBot"
            )
        except Exception as e:
            bot.send_message(message.chat.id, "Lỗi khi gửi video.")
    else:
        bot.send_message(message.chat.id, "Không lấy được video, thử lại sau nhé!")
#spam



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
            video_file.name = "https://i.imgur.com/YV2Wzoq.mp4"

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

# Flask Server cho Render / UptimeRobot
def run_flask():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return "Bot đang hoạt động trên Render!"

    app.run(host="0.0.0.0", port=8080)

# Thread cho Flask
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Thread cho bot Telegram
def run_bot():
    bot.polling(non_stop=True)

bot_thread = threading.Thread(target=run_bot)
bot_thread.start()
