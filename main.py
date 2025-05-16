import os
import time
import json
import requests
import telebot
from telebot import TeleBot
from flask import Flask, request

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 5000))

bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)

ALLOWED_GROUP_IDS = [-1002639856138, -1002557075563]  # nhóm được dùng bot
ADMIN_IDS = [123456789]  # thay bằng user id admin thật

VIP_FILE = "vip_users.json"
try:
    with open(VIP_FILE, "r") as f:
        VIP_USERS = json.load(f)
except:
    VIP_USERS = []

def save_vip_users():
    with open(VIP_FILE, "w") as f:
        json.dump(VIP_USERS, f)

def is_vip(user_id):
    return user_id in VIP_USERS

def is_admin(user_id):
    return user_id in ADMIN_IDS

@app.route("/")
def home():
    return "Bot đang chạy!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

# Lệnh /like buff like cho UID nhập vào
@bot.message_handler(commands=["like"])
def cmd_like(message):
    print(f"Nhận lệnh /like từ {message.from_user.id} - chat {message.chat.id}")
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "❌ Bot chỉ hoạt động trong nhóm cho phép.")
        return

    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "⚠️ Vui lòng nhập đúng cú pháp:\n/like <khu vực> <uid>")
        return

    region = parts[1]
    uid = parts[2]

    loading_msg = bot.reply_to(message, f"⏳ Đang gửi lượt thích tới UID {uid}...")

    try:
        api_url = f"https://freefirelike-api.onrender.com/like?uid={uid}&server_name={region}&key=qqwweerrb"
        resp = requests.get(api_url, timeout=10)
        if resp.status_code != 200:
            bot.edit_message_text("❌ Lỗi khi gửi lượt thích, thử lại sau.",
                                  chat_id=loading_msg.chat.id, message_id=loading_msg.message_id)
            return

        data = resp.json()
        if data.get("LikesGivenByAPI", 0) == 0:
            bot.edit_message_text(f"💔 UID {uid} đã nhận đủ lượt thích hôm nay.",
                                  chat_id=loading_msg.chat.id, message_id=loading_msg.message_id)
            return

        nickname = data.get("PlayerNickname", "Unknown")
        likes_before = data.get("LikesbeforeCommand", 0)
        likes_after = data.get("LikesafterCommand", 0)
        likes_given = likes_after - likes_before

        reply = (
            f"✅ BUFF LIKE THÀNH CÔNG\n"
            f"👤 Người Chơi: {nickname}\n"
            f"🆔 UID: {uid}\n"
            f"📉 Like Trước: {likes_before}\n"
            f"📈 Like Sau: {likes_after}\n"
            f"👍 Like Đã Gửi: {likes_given}\n"
            f"───────────────\n"
            f"Liên hệ: @HaoEsports01"
        )

        bot.edit_message_text(reply, chat_id=loading_msg.chat.id, message_id=loading_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Đã xảy ra lỗi: {e}",
                              chat_id=loading_msg.chat.id, message_id=loading_msg.message_id)

# Lệnh admin thêm user VIP
@bot.message_handler(commands=["addvip"])
def cmd_addvip(message):
    print(f"Nhận lệnh /addvip từ {message.from_user.id}")
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bạn không có quyền sử dụng lệnh này.")
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "⚠️ Cú pháp: /addvip <user_id>")
        return

    try:
        user_id = int(parts[1])
    except:
        bot.reply_to(message, "⚠️ User ID không hợp lệ.")
        return

    if user_id in VIP_USERS:
        bot.reply_to(message, "⚠️ User đã là VIP.")
        return

    VIP_USERS.append(user_id)
    save_vip_users()
    bot.reply_to(message, f"✅ Đã thêm user {user_id} vào danh sách VIP.")

# Lệnh tự động buff like cho VIP (auto buff UID đã add)
@bot.message_handler(commands=["autobuff"])
def cmd_autobuff(message):
    print(f"Nhận lệnh /autobuff từ {message.from_user.id}")

    if not is_vip(message.from_user.id):
        bot.reply_to(message, "❌ Chỉ VIP mới dùng được lệnh này.")
        return

    # Giả sử VIP có 1 danh sách UID cần buff tự động (bạn có thể lưu hoặc hardcode)
    # Ví dụ ở đây bạn tự thêm UID trong list, hoặc từ file/DB
    auto_buff_list = [
        {"region": "vn", "uid": "8324665667"},
        # Bạn thêm UID khác tại đây
    ]

    bot.reply_to(message, f"⏳ Bắt đầu buff tự động cho {len(auto_buff_list)} UID...")

    for acc in auto_buff_list:
        region = acc["region"]
        uid = acc["uid"]

        try:
            api_url = f"https://freefirelike-api.onrender.com/like?uid={uid}&server_name={region}&key=qqwweerrb"
            resp = requests.get(api_url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                print(f"Buff {uid} => Like gửi: {data.get('LikesGivenByAPI', 0)}")
            else:
                print(f"Buff {uid} lỗi status_code={resp.status_code}")
        except Exception as e:
            print(f"Buff {uid} lỗi: {e}")

        time.sleep(2)  # delay để tránh spam quá nhanh

    bot.send_message(message.chat.id, "✅ Hoàn thành buff tự động!")

if __name__ == "__main__":
    if not BOT_TOKEN or not WEBHOOK_URL:
        raise Exception("Bạn cần đặt biến môi trường BOT_TOKEN và WEBHOOK_URL")

    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

    print("Bot đã sẵn sàng và đang chạy webhook...")

    app.run(host="0.0.0.0", port=PORT)
