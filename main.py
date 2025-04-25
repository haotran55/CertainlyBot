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
        bot.reply_to(message, "Bot Chỉ Hoạt Động Trong Nhóm Này.\nLink: https://t.me/HaoEsport01")
        return

    video_url = get_random_video()
    if video_url:
        try:
            bot.send_chat_action(message.chat.id, "upload_video")
            res = requests.get(video_url, stream=True, timeout=10)
            if res.status_code == 200:
                video_file = BytesIO(res.content)
                video_file.name = "video.mp4"
                bot.send_video(message.chat.id, video=video_file, caption="Video gái xinh By @CertainllyBot")
            else:
                bot.send_message(message.chat.id, "Không thể tải video từ nguồn.")
        except Exception as e:
            print("Lỗi gửi video:", e)
            bot.send_message(message.chat.id, "Lỗi khi gửi video.")
    else:
        bot.send_message(message.chat.id, "Không lấy được video, thử lại sau nhé!")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot Chỉ Hoạt Động Trong Nhóm Này.\nLink: https://t.me/HaoEsport01")
        return
    name = message.from_user.first_name or "None"

    text = f"""<blockquote>
<b>Xin Chào {name}!</b>

Gõ /about để xem danh sách lệnh của bot mà bạn có thể sử dụng:

<i>(Nếu thấy bot thú vị, đừng ngần ngại chia sẻ với bạn bè để họ cùng dùng nhé!)</i>
</blockquote>"""

    bot.reply_to(message, text, parse_mode="HTML")



from datetime import datetime, timedelta

@bot.message_handler(commands=['about'])
def send_about(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot Chỉ Hoạt Động Trong Nhóm Này.\nLink: https://t.me/HaoEsport01")
        return

    user = message.from_user
    full_name = f"{user.first_name} {user.last_name or ''}".strip()

    bot.reply_to(message, f"""<blockquote>
Xin Chào Bạn <b>{full_name}</b>

| Danh Sách Lệnh |
» /likes - Buff Like
» /visit - Buff View FF
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
» /admin : Liên Hệ Admin
</blockquote>""", parse_mode="HTML")

OWM_API_KEY = '1dcdf9b01ee855ab4b7760d43a10f854'
@bot.message_handler(commands=['thoitiet'])
def get_weather(message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        bot.reply_to(message, "Vui lòng nhập tên thành phố.\nVí dụ: /thoitiet Hanoi")
        return

    city = args[1]
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric&lang=vi"

    try:
        res = requests.get(url)
        data = res.json()

        if data.get("cod") != 200:
            bot.reply_to(message, f"Không tìm thấy thành phố <b>{city}</b>.", parse_mode="HTML")
            return

        # Lấy dữ liệu
        name = data["name"]
        country = data["sys"]["country"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        desc = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        icon = data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon}@4x.png"

        # Nội dung blockquote HTML
        caption = f"""
<b>Thời tiết tại {name}, {country}:</b>

<blockquote>
🌡️ <b>Nhiệt độ:</b> {temp}°C (Cảm giác: {feels_like}°C)<br/>
🌤️ <b>Trạng thái:</b> {desc}<br/>
💧 <b>Độ ẩm:</b> {humidity}%<br/>
💨 <b>Gió:</b> {wind} m/s
</blockquote>
"""

        # Gửi ảnh kèm caption HTML
        bot.send_photo(message.chat.id, icon_url, caption=caption, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, "Đã xảy ra lỗi khi truy xuất dữ liệu thời tiết.")





@bot.message_handler(commands=['tiktokinfo'])
def tiktok_info(message):
    # Chặn ngoài nhóm
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/HaoEsport01")
        return

    try:
        args = message.text.split()
        if len(args) < 2:
            return bot.reply_to(message, "Vui lòng nhập username TikTok.\nVí dụ: /tiktokinfo bacgau1989")

        username = args[1]
        url = f"http://145.223.80.56:5009/info_tiktok?username={username}"
        r = requests.get(url)
        data = r.json()

        if not data or "username" not in data:
            return bot.reply_to(message, "Không tìm thấy người dùng TikTok!")

        # Dữ liệu người dùng
        name = data.get("name", "Không rõ")
        user = data["username"]
        bio = data.get("signature", "Không có")
        followers = f"{data.get('followers', 0):,}"
        following = f"{data.get('following', 0):,}"
        hearts = f"{data.get('hearts', 0):,}"
        videos = f"{data.get('videos', 0):,}"
        pfp = data.get("profile_picture")

        # Tin nhắn trả về
        msg = f"""
<blockquote>
<b>Thông tin TikTok:</b>
• Tên: <code>{name}</code>
• Username: <code>@{user}</code>
• Followers: <b>{followers}</b>
• Following: <b>{following}</b>
• Likes: <b>{hearts}</b>
• Videos: <b>{videos}</b>
• Bio: <i>{bio}</i>
</blockquote>
        """

        # Gửi ảnh + info
        bot.send_photo(message.chat.id, pfp, caption=msg, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"<b>Lỗi:</b> <code>{e}</code>", parse_mode="HTML")

import time
import requests
from telebot.types import Message

user_last_like_time = {}

@bot.message_handler(commands=['likes'])
def like_handler(message: Message):
    user_id = message.from_user.id
    current_time = time.time()

    try:
        bot.send_chat_action(message.chat.id, "typing")
    except Exception as e:
        print(f"Bot không thể gửi hành động typing: {e}")
        return

    # Lấy thời gian hiện tại theo ngày (chỉ so sánh ngày)
    current_day = time.strftime("%Y-%m-%d", time.gmtime(current_time))
    last_time = user_last_like_time.get(user_id, None)

    # Kiểm tra nếu người dùng đã thực hiện lệnh trong ngày hôm nay
    if last_time and last_time == current_day:
        bot.reply_to(message, "<blockquote>⏳ Bạn chỉ có thể sử dụng lệnh này một lần mỗi ngày.</blockquote>", parse_mode="HTML")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "<blockquote>Cú pháp đúng: /like UID</blockquote>", parse_mode="HTML")
        return

    uid = parts[1]
    api_url = f"https://www.xlanznet.site/ffstats?id={uid}"

    try:
        loading_msg = bot.reply_to(message, "<blockquote>⏳ Đang tiến hành buff like...</blockquote>", parse_mode="HTML")
    except Exception as e:
        print(f"Lỗi gửi tin nhắn loading: {e}")
        return

    def safe_get(data, key):
        value = data.get(key)
        return str(value) if value not in [None, "", "null"] else "Không xác định"

    def extract_number(text):
        if isinstance(text, int):
            return str(text)
        for part in str(text).split():
            if part.isdigit():
                return part
        return "Không xác định"

    try:
        response = requests.get(api_url, timeout=15)
        data = response.json()
    except Exception as e:
        bot.edit_message_text(
            "<blockquote>Lỗi kết nối đến API. Vui lòng thử lại sau.</blockquote>",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            parse_mode="HTML"
        )
        return

    if not data or data.get("status") != 1:
        bot.edit_message_text(
            "<blockquote>Server đang bảo trì hoặc quá tải, vui lòng thử lại sau.</blockquote>",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            parse_mode="HTML"
        )
        return

    # Lưu lại ngày người dùng thực hiện lệnh
    user_last_like_time[user_id] = current_day

    info = data["data"]["basic_info"]
    reply_text = (
        "<blockquote>"
        f"BUFF LIKE THÀNH CÔNG✅ (Dùng API chính)\n"
        f"╭👤 Name: {info['name']}\n"
        f"├🆔 UID {info['id']}\n"
        f"├🌏 Region : vn\n"
        f"├📉 Like trước đó: {info['likes']}\n"
        f"├📈 Like sau khi gửi: {info['likes']}\n"
        f"╰👍 Like được gửi: 0"
    )

    if data.get("status") == 2:
        reply_text += "\n⚠️ Giới hạn like hôm nay, mai hãy thử lại sau."

    reply_text += "</blockquote>"

    try:
        bot.edit_message_text(
            reply_text,
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Lỗi gửi kết quả: {e}")




@bot.message_handler(commands=['ffinfo'])
def ffinfo_command(message):
    # Kiểm tra xem lệnh có được dùng trong nhóm cho phép không
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/HaoEsport01")
        return

    try:
        args = message.text.split()
        if len(args) < 2:
            return bot.reply_to(message, "Vui lòng nhập UID.\nVí dụ: /ffinfo 3827953808")

        uid = args[1]
        url = f"https://www.xlanznet.site/ffstats?id={uid}"
        r = requests.get(url)
        data = r.json()

        if data.get("status") != "success":
            return bot.reply_to(message, "Không tìm thấy người chơi!")

        info = data["data"]["basic_info"]
        guild = data["data"].get("Guild")

        msg = f"""
<blockquote>
<b>Thông tin người chơi:</b>
• Tên: <code>{info['name']}</code>
• UID: <code>{info['id']}</code>
• Level: <b>{info['level']}</b>
• Likes: <b>{info['likes']}</b>
• Server: <code>{info['server']}</code>
• Bio: <i>{info['bio'] or 'Không có'}</i>

<b>Guild:</b>
• Tên: <code>{guild['name']}</code>
• Leader: <code>{guild['leader']['name']}</code>
• Thành viên: <b>{guild['members_count']}</b>
</blockquote>
        """
        bot.reply_to(message, msg, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"<b>Lỗi:</b> <code>{e}</code>", parse_mode="HTML")



import requests

@bot.message_handler(commands=['rutgon'])
def shorten_link(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot Chỉ Hoạt Động Trong Nhóm Này.\nLink: https://t.me/HaoEsport01")
        return

    
    

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
    return 'ok', 200

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
