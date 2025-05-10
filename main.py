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


# Hàm lấy tên item (nếu cần tên)
import requests

def fetch_data(user_id, region):
    url = f'https://free-fire-gnwz.onrender.com/api/account?uid={user_id}&region={region}'
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

@bot.message_handler(commands=['get'])
def handle_command(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot Chỉ Hoạt Động Trong Nhóm Này https://t.me/HaoEsport01")
        return
        
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "<blockquote>❌ Sai cú pháp!\nVí dụ: /get 12345678 sg</blockquote>", parse_mode="HTML")
        return

    _, user_id, region = parts

    try:
        data = fetch_data(user_id, region)
        if not data:
            bot.reply_to(message, "<blockquote>❌ Không tìm thấy người chơi hoặc server quá tải!</blockquote>", parse_mode="HTML")
            return

        basic = data['basicInfo']
        clan = data['clanBasicInfo']
        captain = data['captainBasicInfo']

        def g(key, dic): return dic.get(key, 'Không có')

        info = f"""
<blockquote>
<b>📌 Thông tin tài khoản:</b>
Tên: {g('nickname', basic)}
ID: {g('accountId', basic)}
Cấp độ: {g('level', basic)}
Booyah Pass: {g('hasElitePass', basic)}
Lượt thích: {g('liked', basic)}
Máy chủ: {g('region', basic)}
Ngày tạo: {g('createAt', basic)}

<b>👥 Thông tin quân đoàn:</b>
Tên: {g('clanName', clan)}
Cấp độ: {g('clanLevel', clan)}
Thành viên: {g('memberNum', clan)}

<b>👑 Chủ quân đoàn:</b>
Tên: {g('nickname', captain)}
Cấp độ: {g('level', captain)}
Lượt thích: {g('liked', captain)}
Ngày tạo: {g('createAt', captain)}
</blockquote>
"""
        bot.reply_to(message, info.strip(), parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, "<blockquote>⚠️ Đã xảy ra lỗi khi xử lý yêu cầu.</blockquote>", parse_mode="HTML")
        print(e)

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

