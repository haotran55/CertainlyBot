import os
import threading
import requests
import telebot
import requests
from telebot import TeleBot
from telebot.types import Message  # ✅ Import thêm dòng này
from flask import Flask, request
from datetime import datetime
from io import BytesIO
import requests
from io import BytesIO

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
ALLOWED_GROUP_IDS = [-1002639856138]

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang hoạt động trên Render!"

@bot.message_handler(commands=['like'])
def handle_like(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "<blockquote>Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/HaoEsport01</blockquote>", parse_mode="HTML")
        return
        
    user_id = message.from_user.id
    today_str = datetime.now().strftime("%Y-%m-%d")

    if verified_users.get(user_id) != today_str:
        bot.reply_to(message, "<blockquote>❌ Bạn chưa nhập KEY hôm nay hoặc KEY đã hết hạn.\n👉 Dùng /getkey để lấy key mới.</blockquote>", parse_mode="HTML")
        return   

    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "<blockquote>Vui lòng cung cấp khu vực và UID hợp lệ.\nVí dụ: /like vn 8324665667</blockquote>", parse_mode="HTML")
        return

    region = parts[1]
    uid = parts[2]

    loading_msg = bot.reply_to(message, f"<blockquote>Đang gửi lượt thích tới {uid}, vui lòng đợi...</blockquote>", parse_mode="HTML")

    try:
        api_url = f"https://freefirelike-api.onrender.com/like?uid={uid}&server_name={region}&key=qqwweerrb"
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
            f"<blockquote>✅ BUFF LIKE THÀNH CÔNG\n"
            f"👤 Người Chơi: {nickname}\n"
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

#video
from datetime import datetime

verified_users = {}  # { user_id: "2025-05-13" }

import requests

def TimeStamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_key(user_id):
    today_str = datetime.now().strftime("%Y%m%d")  # ví dụ: 20250513
    return "HaoEsports" + str(user_id * int(today_str) - 2007)

@bot.message_handler(commands=['getkey'])
def startkey(message):
    user_id = message.from_user.id
    key = generate_key(user_id)

    api_token = '67c1fe72a448b83a9c7e7340'
    key_url = f"https://dichvukey.site/key.html?key={key}"

    try:
        response = requests.get(f'https://link4m.co/api-shorten/v2?api={api_token}&url={key_url}')
        response.raise_for_status()
        url_data = response.json()

        if 'shortenedUrl' in url_data:
            url_key = url_data['shortenedUrl']
            text = (
                f"<blockquote>"
                f"🔑 <b>KEY Hôm Nay (Ngày {TimeStamp()})</b>\n"
                f"➡️ <a href='{url_key}'>Bấm Vào Đây Để Lấy KEY</a>\n\n"
                f"📌 Sau khi lấy key, hãy dùng lệnh <code>/key HaoEsportxxxx</code> để tiếp tục.\n"
                f"💡 Gợi ý: Dùng <code>/muavip</code> để không phải lấy key mỗi ngày.\n"
                f"</blockquote>"
            )
            bot.reply_to(message, text, parse_mode='HTML')
        else:
            bot.reply_to(message, '<b>❌ Lỗi khi rút gọn link.</b>', parse_mode='HTML')
    except requests.RequestException:
        bot.reply_to(message, '<b>❌ Lỗi kết nối khi tạo key.</b>', parse_mode='HTML')



@bot.message_handler(commands=['key'])
def key(message):
    if len(message.text.split()) != 2:
        bot.reply_to(message, '<b>❗ Sai cú pháp.</b> Dùng: <code>/key HaoEsportxxxx</code>', parse_mode='HTML')
        return

    user_id = message.from_user.id
    key_input = message.text.split()[1]
    expected_key = generate_key(user_id)

    if key_input == expected_key:
        verified_users[user_id] = datetime.now().strftime("%Y-%m-%d")  # đánh dấu đã xác minh hôm nay
        text_message = (
            f"<blockquote>"
            f"✅ <b>[KEY HỢP LỆ]</b>\n"
            f"🆔 Người dùng: <b>{user_id}</b>\n"
            f"🚀 Được cấp quyền dùng  lệnh <code>/like</code>\n"
            f"</blockquote>"
        )
        video_url = 'https://v16m-default.tiktokcdn.com/ccf79902a33306cfe044872ad94b2619/6809d4ec/video/tos/alisg/tos-alisg-pve-0037c001/oo4jREIYzDasfQ44IKcR5FAQGeARLDge8CsQOI/?a=0&bti=OUBzOTg7QGo6OjZAL3AjLTAzYCMxNDNg&ch=0&cr=0&dr=0&er=0&lr=all&net=0&cd=0%7C0%7C0%7C0&cv=1&br=1580&bt=790&cs=0&ds=6&ft=EeF4ntZWD03Q12NvQaxQWIxRSfYFpq_45SY&mime_type=video_mp4&qs=0&rc=OTQ1NmQ3ZGZlaDc7Zjg5aUBpM2ltO245cjU6MzMzODczNEAxMDFhYy4yXi0xXjBhMzNjYSNicmlfMmQ0NDFhLS1kMWBzcw%3D%3D&vvpl=1&l=20250424080617D39FC2B3B674FA0853C2&btag=e000b8000'
        bot.send_video(message.chat.id, video_url, caption=text_message, parse_mode='HTML')
    else:
        bot.reply_to(message, '<blockquote>❌ <b>KEY KHÔNG HỢP LỆ hoặc đã hết hạn.</b>\n👉 Dùng lại /getkey để lấy key mới.</blockquote>', parse_mode='HTML')

#hmm
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
