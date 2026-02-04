import os
import random
import time
import requests
import telebot
import threading
from telebot.types import Message
from telebot import TeleBot
from flask import Flask, request
from datetime import datetime, timedelta

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)


app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang hoạt động trên Render!"


import requests
from requests.exceptions import Timeout, RequestException

@bot.message_handler(commands=['like', 'Like'])
def handle_like(message):
    user_id = message.from_user.id

    # Check command format
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(
            message,
            "❌ Invalid format\n"
            "<b>Usage:</b> <code>/like vn 10000001</code>",
            parse_mode="HTML"
        )
        return

    region = parts[1].lower()
    uid = parts[2]

    loading_msg = bot.reply_to(
        message,
        f"⏳ Sending likes to UID <code>{uid}</code>...",
        parse_mode="HTML"
    )

    api_url = f"https://like-free-fire-nine.vercel.app/like?uid={uid}&server_name={region}"

    try:
        response = requests.get(api_url, timeout=15)

        # Check status code
        if response.status_code != 200:
            bot.edit_message_text(
                f"❌ API Error ({response.status_code})\nPlease try again later.",
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id
            )
            return

        # Check JSON
        if "application/json" not in response.headers.get("Content-Type", ""):
            bot.edit_message_text(
                "❌ API returned invalid data (not JSON).",
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id
            )
            return

        data = response.json()

        required_keys = [
            "LikesGivenByAPI",
            "LikesbeforeCommand",
            "LikesafterCommand"
        ]

        if not all(k in data for k in required_keys):
            bot.edit_message_text(
                "❌ Invalid API response.\nPlease try again later.",
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id
            )
            return

        if data["LikesGivenByAPI"] == 0:
            bot.edit_message_text(
                f"<blockquote>💔 UID <code>{uid}</code> has reached daily like limit.</blockquote>",
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                parse_mode="HTML"
            )
            return

        nickname = data.get("PlayerNickname", "Unknown")
        uid = data.get("UID", uid)
        likes_before = data["LikesbeforeCommand"]
        likes_after = data["LikesafterCommand"]
        likes_given = likes_after - likes_before

        reply = (
            "<blockquote>"
            "🎮 <b>LIKE SUCCESS</b>\n"
            "──────────────\n"
            f"👤 <b>Name:</b> {nickname}\n"
            f"🆔 <b>UID:</b> {uid}\n"
            f"❤️ <b>Likes Given:</b> {likes_given}\n"
            f"📈 <b>Before:</b> {likes_before}\n"
            f"📉 <b>After:</b> {likes_after}\n"
            "──────────────\n"
            "📩 <b>Contact:</b> @nhathaov"
            "</blockquote>"
        )

        bot.edit_message_text(
            reply,
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            parse_mode="HTML"
        )

    except Timeout:
        bot.edit_message_text(
            "<blockquote>⏳ API timeout.\nPlease try again later.</blockquote>",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            parse_mode="HTML"
        )

    except RequestException as e:
        print("Request error:", e)
        bot.edit_message_text(
            "<blockquote>🌐 Cannot connect to API.\nPlease try again later.</blockquote>",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            parse_mode="HTML"
        )

    except Exception as e:
        print("Unknown error:", e)
        bot.edit_message_text(
            "<blockquote>❌ Unexpected system error.</blockquote>",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            parse_mode="HTML"
        )


VIDEO_URL = "https://api.tiktokv.com/aweme/v1/play/?file_id=2fab7e5637e64628a0e0d98f3f6028a0&is_play_url=1&item_id=7508799426123549957&line=0&signaturev3=dmlkZW9faWQ7ZmlsZV9pZDtpdGVtX2lkLjQ1MWYyY2Y5YzhlMzRjMGYzNGM0NTVlYmY3NmFkYzdl&source=FEED&video_id=v09044g40000d0q9pb7og65v3lr1sqc0&name=taivideo.vn - Geto Kenjaku Desktop live wallpaper geto getosuguru kenjaku jujutsukaisen desktoplivewallpapers anim.mp4"

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    chat_id = message.chat.id

    for user in message.new_chat_members:
        first = user.first_name
        username = f"@{user.username}" if user.username else "None"
        user_id = user.id

        caption = f"""
<pre>
👋 Hello, welcome {first} to Support!

Name      : {first}
Username  : {username}
ID        : {user_id}

👍 GET LIKES IN FREE FIRE ACCOUNT
├── Format : /like {{region}} {{Uid}}
├── Example: /like ind 12345678
└── ✅ All Regions Supported

🚨 More Coming Soon
Keep Support 😊

• I hope you understand everything clearly. 🗿
• Thanks for using this group! 😁
</pre>
"""

        bot.send_video(
            chat_id,
            VIDEO_URL,
            caption=caption
        )
        


@bot.message_handler(commands=['id', 'info'])
def get_user_info(message):
    # Nếu reply thì lấy user được reply
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        user = message.from_user

    user_id = user.id
    first_name = user.first_name or "None"
    last_name = user.last_name or ""
    username = f"@{user.username}" if user.username else "None"
    language = user.language_code or "Unknown"
    is_bot = user.is_bot

    info_text = f"""
<pre>
📌 TELEGRAM USER INFO
├─ 🆔 ID: {user_id}
├─ 👤 Name: {first_name} {last_name}
├─ 🔗 Username: {username}
├─ 🌐 Language: {language}
└─ 🤖 Is Bot: {is_bot}
</pre>
"""

    # Lấy ảnh đại diện
    photos = bot.get_user_profile_photos(user_id, limit=1)

    if photos.total_count > 0:
        file_id = photos.photos[0][-1].file_id
        bot.send_photo(
            message.chat.id,
            photo=file_id,
            caption=info_text,
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            message.chat.id,
            info_text + "\n<pre>(User has no profile picture.The user has no photo.)</pre>",
            parse_mode="HTML"
        )
   

import telebot
from datetime import datetime
import pytz

COUNTRY_TIMEZONES = {
    # Việt Nam
    "viet nam": "Asia/Ho_Chi_Minh",
    "vietnam": "Asia/Ho_Chi_Minh",

    # Ấn Độ
    "an do": "Asia/Kolkata",
    "india": "Asia/Kolkata",

    # Nepal
    "nepal": "Asia/Kathmandu",

    # Nhật Bản
    "nhat ban": "Asia/Tokyo",
    "japan": "Asia/Tokyo",

    # Hàn Quốc
    "han quoc": "Asia/Seoul",
    "korea": "Asia/Seoul",
    "south korea": "Asia/Seoul",

    # Trung Quốc
    "trung quoc": "Asia/Shanghai",
    "china": "Asia/Shanghai",

    # Thái Lan
    "thai lan": "Asia/Bangkok",
    "thailand": "Asia/Bangkok",

    # Mỹ
    "my": "America/New_York",
    "usa": "America/New_York",
    "united states": "America/New_York",

    # Anh
    "anh": "Europe/London",
    "uk": "Europe/London",
    "england": "Europe/London",

    # Pháp
    "phap": "Europe/Paris",
    "france": "Europe/Paris"
}


@bot.message_handler(commands=['time'])
def time_by_country_name(message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        bot.reply_to(
            message,
            "<pre>❌ Use: /time viet nam | india | nepal ...</pre>",
            parse_mode="HTML"
        )
        return

    country_name = args[1].lower().strip()

    if country_name not in COUNTRY_TIMEZONES:
        bot.reply_to(
            message,
            "<pre>❌ This country was not found.</pre>",
            parse_mode="HTML"
        )
        return

    tz_name = COUNTRY_TIMEZONES[country_name]
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)

    text = f"""
<pre>
🌍 WORLD TIME

🌐 Country : {country_name.title()}
🕒 Time    : {now.strftime('%H:%M:%S')}
📅 Date    : {now.strftime('%d-%m-%Y')}
⏰ Zone    : {tz_name}
</pre>
"""

    bot.reply_to(message, text, parse_mode="HTML")


        


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
