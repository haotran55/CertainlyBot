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
def get_item_name(item_id):
    try:
        url = f"https://ff-items-lk.vercel.app/myitem?item_id={item_id}&key=PRINCE"
        res = requests.get(url)
        data = res.json()
        return data.get("item_name", f"Item {item_id}")
    except:
        return f"Item {item_id}"

# Gửi ảnh item (skin, quần áo, pet)
def send_item_image(chat_id, item_id, caption=None):
    image_url = f"https://ff-items-lk.vercel.app/myitem?item_id={item_id}&key=PRINCE"
    try:
        bot.send_photo(chat_id, image_url, caption=caption)
    except Exception as e:
        print(f"❌ Lỗi gửi ảnh item {item_id}: {e}")

# Chỉ xử lý trong nhóm cho phép

# Lệnh /start

# Lệnh /account uid region
@bot.message_handler(commands=['get'])
def get_account_info(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot Chỉ Hoạt Động Trong Nhóm Này https://t.me/HaoEsport01")
        return

    try:
        parts = message.text.strip().split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ Sai cú pháp. Dùng:\n/get uid region")
            return

        uid, region = parts[1], parts[2]
        url = f"https://free-fire-gnwz.onrender.com/api/account?uid={uid}&region={region}"
        response = requests.get(url)
        data = response.json()

        if "basicInfo" not in data:
            bot.reply_to(message, "❌ Không tìm thấy thông tin tài khoản.")
            return

        basic = data["basicInfo"]
        profile = data.get("profileInfo", {})
        pet = data.get("petInfo", {})

        avatar_name = get_item_name(basic.get("headPic", 0))
        banner_name = get_item_name(basic.get("bannerId", 0))
        weapon_names = [get_item_name(wid) for wid in basic.get("weaponSkinShows", [])]
        clothes_names = [get_item_name(cid) for cid in profile.get("clothes", [])]
        pet_skin_name = get_item_name(pet.get("skinId", 0)) if pet else ""

        # Nội dung văn bản
        reply = f"""<b>📌 Thông tin tài khoản:</b>
<blockquote>
👤 Nickname: {basic['nickname']}
🎮 Level: {basic['level']}
🏆 Rank: {basic['rank']} (RP: {basic['rankingPoints']})
💣 CS Rank: {basic['csRank']} (RP: {basic['csRankingPoints']})
🧢 Avatar: {avatar_name}
🎴 Banner: {banner_name}
</blockquote>"""

        if weapon_names:
            reply += "<b>🎯 Vũ khí hiển thị:</b>\n<blockquote>"
            reply += "\n".join(f"🔫 {name}" for name in weapon_names)
            reply += "</blockquote>"

        if clothes_names:
            reply += "<b>👕 Trang phục:</b>\n<blockquote>"
            reply += "\n".join(f"👗 {name}" for name in clothes_names)
            reply += "</blockquote>"

        if pet:
            reply += f"<b>🐾 Pet:</b>\n<blockquote>📛 {pet.get('name', '')}\n🎨 {pet_skin_name}</blockquote>"

        bot.reply_to(message, reply, parse_mode="HTML")

        # Gửi ảnh item
        for cid in profile.get("clothes", []):
            send_item_image(message.chat.id, cid, caption="👕 Trang phục")

        for wid in basic.get("weaponSkinShows", []):
            send_item_image(message.chat.id, wid, caption="🔫 Skin vũ khí")

        if pet:
            send_item_image(message.chat.id, pet.get("skinId", 0), caption="🐾 Pet Skin")

    except Exception as e:
        bot.reply_to(message, f"🚫 Lỗi: {str(e)}")

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

