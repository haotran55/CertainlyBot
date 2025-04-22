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


from io import BytesIO

@bot.message_handler(content_types=['new_chat_members'])
def welcome_user(message):
    for user in message.new_chat_members:
        uid = user.id
        username = f"@{user.username}" if user.username else "Không có"
        full_name = f"{user.first_name} {user.last_name or ''}".strip()
        time_joined = datetime.now().strftime("%H:%M:%S | %d/%m/%Y")

        # Lấy video
        video_url = get_random_video()
        video_resp = requests.get(video_url)
        video_file = BytesIO(video_resp.content)
        video_file.name = "https://i.imgur.com/YV2Wzoq.mp4"  # Bắt buộc phải có tên file

        # Caption
        caption = f"""🖐 Hello <b>{full_name}</b>
├ UID: <code>{uid}</code>
├ Username: {username}
├ Thời Gian: <code>{time_joined}</code>
└ <i>Chào Mừng Bạn Đã Tham Gia Nhóm <b>Box Hào Esports</b></i>
Gõ /bot Để Xem Lệnh Bot Hỗ Trợ Nhé!"""

        # Gửi video
        bot.send_video(
            chat_id=message.chat.id,
            video=video_file,
            caption=caption,
            parse_mode="HTML"
        )


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
