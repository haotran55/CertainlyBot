import os
import threading
import requests
from telebot import TeleBot
from flask import Flask
from datetime import datetime
from keep_alive import keep_alive

# Giữ server Flask hoạt động
keep_alive()

# Khởi tạo bot với token
BOT_TOKEN = os.environ.get('BOT_TOKEN')  # <- Thêm dòng này
bot = TeleBot(BOT_TOKEN)

# ID nhóm được phép sử dụng bot
ALLOWED_GROUP_ID = -1002639856138
GROUP_LINK = "https://t.me/HaoEsport01"  # Link nhóm

def group_only(func):
    """Chỉ cho phép bot hoạt động trong nhóm cụ thể."""
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

@bot.message_handler(commands=['video'])
@group_only
def random_video(message):
    """Lấy video ngẫu nhiên từ API và gửi cho người dùng."""
    try:
        res = requests.get("https://api.ffcommunity.site/randomvideo.php")
        data = res.json()
        video_url = data.get("url")

        if video_url:
            bot.send_chat_action(message.chat.id, "upload_video")
            bot.send_video(message.chat.id, video=video_url, caption="Video gái xinh By @CertainllyBot")
        else:
            bot.send_message(message.chat.id, "Không lấy được video, thử lại sau nhé!")
    except Exception as e:
        bot.send_message(message.chat.id, "Đã xảy ra lỗi khi lấy video.")

# Khởi tạo và chạy Flask trong một thread riêng
def run_flask():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return "Bot đang chạy!"

    app.run(host="0.0.0.0", port=8080)  # Cổng phải là 8080 nếu chạy trên Heroku

# Chạy Flask trên một thread riêng
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Chạy bot trong một thread riêng để không bị gián đoạn khi Flask đang chạy
def run_bot():
    bot.polling(none_stop=True)

# Chạy bot
bot_thread = threading.Thread(target=run_bot)
bot_thread.start()
