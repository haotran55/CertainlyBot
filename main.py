import os
import threading
import requests
import telebot  # Thêm dòng này để sử dụng telebot
from flask import Flask, request
from datetime import datetime
from io import BytesIO

# Lấy token từ biến môi trường
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
ALLOWED_GROUP_IDS = [-1002639856138]

# Flask App
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang hoạt động trên Render!"

# Hàm lấy video
def get_random_video():
    try:
        res = requests.get("https://api.ffcommunity.site/randomvideo.php", timeout=5)
        data = res.json()
        return data.get("url")
    except:
        return None

# Lệnh /video
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


@bot.message_handler(commands=['start'])
def send_welcome(message):
    name = message.from_user.first_name or "None"

    text = f"""<blockquote>
<b>Xin Chào {name}!</b>

Gõ <code>/about</code> để xem danh sách lệnh của bot mà bạn có thể sử dụng:

<i>(Nếu thấy bot thú vị, đừng ngần ngại chia sẻ với bạn bè để họ cùng dùng nhé!)</i>
</blockquote>"""

    bot.reply_to(message, text, parse_mode="HTML")



from datetime import datetime, timedelta

@bot.message_handler(commands=['about'])
def send_help(message):
    username = message.from_user.username or "None"
    now = datetime.utcnow() + timedelta(hours=7)
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%d/%m/%Y")

    text = f"""<blockquote>
📑 <b>Danh Sách Lệnh</b>  
⏰ Thời Gian: <code>{current_time}</code>  
📅 Ngày: <code>{current_date}</code>  
👤 Người Gọi Lệnh: @{username}
</blockquote>

<b>| Lệnh Chung |</b>
» /likes - Buff Like  
» /video - Random Video Gái  
» /anhgai - Random Ảnh Gái  
» /thoitiet - Check Thời Tiết  
» /rutgon - Rút Gọn Link  
» /spam - Spam SDT Thường  
» /spamvip - Spam SDT Vip  
» /tiktok - Tải Video TikTok  
» /ttinfo - Kiểm Tra Tài Khoản TikTok  
» /ffinfo - Kiểm Tra Tài Khoản Free Fire  

<b>| Contact |</b>
» /admin - Liên Hệ Admin
"""

    bot.reply_to(message, text, parse_mode="HTML")


@bot.message_handler(commands=['admin'])
def admin_info(message):
    text = """<blockquote>
👨‍💻 <b>Liên Hệ Admin</b>

» @HaoEsports05
</blockquote>"""

    bot.reply_to(message, text, parse_mode="HTML")



import requests

@bot.message_handler(commands=['rutgon'])
def shorten_link(message):
    args = message.text.split(" ", 1)
    if len(args) == 1:
        bot.reply_to(message, "Vui lòng nhập link cần rút gọn.\nVí dụ: <code>/rutgon https://example.com</code>", parse_mode="HTML")
        return

    long_url = args[1]

    try:
        api_url = f"http://tinyurl.com/api-create.php?url={long_url}"
        response = requests.get(api_url)

        if response.status_code == 200:
            short_url = response.text
            reply_text = f"""<blockquote>
🔗 <b>Link Đã Được Rút Gọn:</b>
<code>{short_url}</code>
</blockquote>"""
            bot.reply_to(message, reply_text, parse_mode="HTML")
        else:
            bot.reply_to(message, "Rút gọn thất bại. Vui lòng thử lại sau.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi khi rút gọn link: {e}")




# Welcome thành viên mới
# Welcome thành viên mới
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from io import BytesIO
import requests

@bot.message_handler(content_types=['new_chat_members'])
def welcome_user(message):
    for user in message.new_chat_members:
        uid = user.id
        username = f"@{user.username}" if user.username else "@None"
        full_name = f"{user.first_name} {user.last_name or ''}".strip()
        time_joined = datetime.now().strftime("%H:%M:%S | %d/%m/%Y")

        try:
            caption = f"""🖐 <b>Welcome, {full_name}!</b>

<blockquote>
🌟 <b>UID:</b> <code>{uid}</code>
📛 <b>Username:</b> {username}
⏰ <b>Thời Gian:</b> <code>{time_joined}</code>

✨ <i>Rất vui khi bạn đã gia nhập <b>Box Hào Esports</b>!</i>
</blockquote>
"""

            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("BUFF LIKE", url="https://t.me/checkinfo123"))

            bot.send_video(
                chat_id=message.chat.id,
                video="https://v16m-default.tiktokcdn.com/ccf79902a33306cfe044872ad94b2619/6809d4ec/video/tos/alisg/tos-alisg-pve-0037c001/oo4jREIYzDasfQ44IKcR5FAQGeARLDge8CsQOI/?a=0&bti=OUBzOTg7QGo6OjZAL3AjLTAzYCMxNDNg&ch=0&cr=0&dr=0&er=0&lr=all&net=0&cd=0%7C0%7C0%7C0&cv=1&br=1580&bt=790&cs=0&ds=6&ft=EeF4ntZWD03Q12NvQaxQWIxRSfYFpq_45SY&mime_type=video_mp4&qs=0&rc=OTQ1NmQ3ZGZlaDc7Zjg5aUBpM2ltO245cjU6MzMzODczNEAxMDFhYy4yXi0xXjBhMzNjYSNicmlfMmQ0NDFhLS1kMWBzcw%3D%3D&vvpl=1&l=20250424080617D39FC2B3B674FA0853C2&btag=e000b8000",
                caption=caption,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as e:
            bot.send_message(message.chat.id, f"Chào mừng {full_name} nhé! (Gửi video lỗi)\nLỗi: {e}")

# Webhook nhận update từ Telegram
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

# Khởi chạy Flask và bot song song
if __name__ == "__main__":
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
    if not WEBHOOK_URL:
        raise Exception("Thiếu biến môi trường WEBHOOK_URL")

    # Xóa webhook cũ và thiết lập webhook mới
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

    # Chạy Flask (webhook listener)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
