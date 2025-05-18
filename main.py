import os
import time
import requests
import telebot
from telebot.types import Message
from telebot import TeleBot
from flask import Flask, request
from datetime import datetime, timedelta

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
ALLOWED_GROUP_IDS = [-1002639856138]

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang hoạt động trên Render!"


@bot.message_handler(commands=['like'])
def handle_like(message):
    user_id = message.from_user.id

    # ✅ Giới hạn nhóm sử dụng
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "<blockquote>Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/HaoEsport01</blockquote>", parse_mode="HTML")
        return

    # ✅ Kiểm tra người dùng đã vượt KEY chưa
    expire_time = active_keys.get(user_id)
    if not expire_time or time.time() > expire_time:
        bot.reply_to(message, "<blockquote>⛔ Bạn chưa vượt KEY hoặc KEY đã hết hạn.\n👉 Dùng lệnh /getkey để lấy và xác thực.</blockquote>", parse_mode="HTML")
        return

    # ✅ Kiểm tra cú pháp
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "<blockquote>Vui lòng cung cấp khu vực và UID hợp lệ.\nVí dụ: /like vn 8324665667</blockquote>", parse_mode="HTML")
        return

    region = parts[1]
    uid = parts[2]

    loading_msg = bot.reply_to(message, f"<blockquote>Đang gửi lượt thích tới {uid}, vui lòng đợi...</blockquote>", parse_mode="HTML")

    try:
        api_url = f"http://160.250.137.144:5001/like?uid={uid}&server_name={region}&key=qqwweerrb"
        response = requests.get(api_url, timeout=10)

        if response.status_code != 200:
            bot.edit_message_text(
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                text="<blockquote>Đã xảy ra lỗi. Vui lòng kiểm tra khu vực tài khoản hoặc thử lại sau.</blockquote>",
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
            f"✅ BUFF LIKE THÀNH CÔNG\n"
            f"<blockquote>👤 Người Chơi: {nickname}\n"
            f"🆔 UID: {uid}\n"
            f"📉 Like Trước: {likes_before}\n"
            f"📈 Like Sau: {likes_after}\n"
            f"👍 Like Đã Gửi: {likes_given_by_bot}\n"
            f"───────────────────\n"
            f"Liên Hệ: @HaoEsports01</blockquote>"
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
            text="<blockquote>Đã xảy ra lỗi. Vui lòng kiểm tra khu vực tài khoản hoặc thử lại sau.</blockquote>",
            parse_mode="HTML"
        )


@bot.message_handler(commands=['checkkey'])
def check_key(message):
    user_id = message.from_user.id
    expire_time = active_keys.get(user_id)

    if expire_time:
        remaining_seconds = int(expire_time - time.time())
        if remaining_seconds > 0:
            hours = remaining_seconds // 3600
            minutes = (remaining_seconds % 3600) // 60
            seconds = remaining_seconds % 60
            bot.reply_to(message, f"⏳ Key của bạn sẽ hết hạn sau: {hours} giờ {minutes} phút {seconds} giây.")
        else:
            bot.reply_to(message, "❌ Key của bạn đã hết hạn.")
            del active_keys[user_id]  # Xoá luôn key hết hạn
    else:
        bot.reply_to(message, "❌ Bạn chưa nhập key hoặc key đã hết hạn.")


import datetime
import time
import requests

# Lưu các key hợp lệ và thời gian hết hạn (user_id: expire_timestamp)
active_keys = {}  # Ex: {123456789: 1716043211.0}

@bot.message_handler(commands=['getkey'])
def startkey(message):
    user_id = message.from_user.id
    today_day = datetime.date.today().day

    # Tạo key
    key = "vLong" + str(user_id * today_day - 2007)

    # Tạo link key
    api_token = '67c1fe72a448b83a9c7e7340'
    key_url = f"http://haoesports2010.liveblog365.com/key.php?r={key}"

    try:
        # Gọi API rút gọn link
        response = requests.get(f'https://link4m.co/api-shorten/v2?api={api_token}&url={key_url}')
        response.raise_for_status()
        url_data = response.json()

        # Nếu có link rút gọn
        if 'shortenedUrl' in url_data:
            url_key = url_data['shortenedUrl']

            # Tính thời gian hết hạn sau 5 giờ (18000 giây)
            expire_timestamp = time.time() + 18000
            active_keys[user_id] = expire_timestamp

            # Gửi link key cho người dùng
            text = (
                f'🔑 Link lấy KEY hợp lệ ngày {datetime.date.today()} là:\n{url_key}\n\n'
                '⏳ KEY sẽ hết hạn sau 5 giờ.\n'
                '✅ Sau khi lấy KEY, dùng lệnh:\n'
                '`/key vLongXXXXX` để xác thực\n'
                '📌 Hoặc dùng /muavip để không cần vượt key\n'
            )
            bot.reply_to(message, text, parse_mode='Markdown')
        else:
            bot.reply_to(message, '⚠️ Không thể tạo link rút gọn. Vui lòng thử lại sau.')
    except requests.RequestException:
        bot.reply_to(message, '❌ Lỗi kết nối khi tạo link key.')

import time  # <--- dùng time thay vì datetime

# Tạo dict lưu key và thời gian hết hạn (timestamp)
active_keys = {}  # {user_id: expire_timestamp}

@bot.message_handler(commands=['key'])
def key(message):
    if len(message.text.split()) != 2:
        bot.reply_to(message, 'Key Đã Vượt Là? đã vượt thì nhập /key chưa vượt thì /muavip nhé')
        return

    user_id = message.from_user.id
    key_input = message.text.split()[1]
    today_day = datetime.date.today().day
    expected_key = "HaoEsports" + str(user_id * today_day - 2007)

    if key_input == expected_key:
        expire_timestamp = time.time() + 18000  # 5 giờ = 18000 giây
        active_keys[user_id] = expire_timestamp

        text_message = f'<blockquote>[ KEY HỢP LỆ ] NGƯỜI DÙNG CÓ ID: [ {user_id} ] ĐƯỢC PHÉP DÙNG LỆNH  [/like] TRONG VÒNG 5 GIỜ</blockquote>'
        video_url = 'https://v16m-default.akamaized.net/...'  # giữ nguyên
        bot.send_video(message.chat.id, video_url, caption=text_message, parse_mode='HTML')
    else:
        bot.reply_to(message, 'KEY KHÔNG HỢP LỆ.')


@bot.message_handler(commands=["admin"])
def cmd_test(message):
    bot.reply_to(message, "<blockquote>✅ Liên Hệ: @HaoEsports01!</blockquote>", parse_mode="HTML")

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
