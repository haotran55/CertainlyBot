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

    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "<blockquote>Vui lòng cung cấp khu vực và UID hợp lệ.\nVí dụ: /like 8324665667 vn</blockquote>", parse_mode="HTML")
        return

    uid = parts[1]
    region = parts[2]

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
        likes_before = data["LikesbeforeCommand"]
        likes_after = data["LikesafterCommand"]
        likes_given_by_bot = likes_after - likes_before

        reply = (
            f"<blockquote>✅ Likes Sent Successfully\n"
            f"👤 Player Nickname: {nickname}\n"
            f"📉 Likes Before: {likes_before}\n"
            f"📈 Likes After: {likes_after}\n"
            f"✅ Likes Given: {likes_given_by_bot}\n"
            f"@HaoEsport01</blockquote>"
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
