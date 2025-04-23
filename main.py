import os
import requests
from flask import Flask
from telebot import TeleBot, types
from datetime import datetime
from io import BytesIO

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Địa chỉ webhook của bạn (Render domain)
WEBHOOK_HOST = "https://certainlybot.onrender.com"  # thay <your-render-url> bằng domain Render của bạn
WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

ALLOWED_GROUP_IDS = [-1002639856138]

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
        bot.reply_to(message, "Tham Gia Nhóm Của Chúng Tôi Để Bot Có Thể Trò Chuyện Với Bạn Dễ Dàng Hơn.\nLink Đây: [ https://t.me/HaoEsport01 ]\n\nLưu Ý, Bot Chỉ Hoạt Động Trong Những Nhóm Cụ Thể Thôi Nha!")
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
            video_file.name = "welcome.mp4"

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

# Thiết lập webhook khi start
@app.before_first_request
def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

# Route để Telegram gửi update vào
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def receive_update():
    json_string = request.get_data().decode("utf-8")
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok', 200

# Route test
@app.route('/')
def home():
    return "Bot đang hoạt động qua Webhook!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
