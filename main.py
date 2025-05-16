import os
import time
import json
import requests
import telebot
from telebot import TeleBot
from flask import Flask, request
from datetime import datetime, timedelta

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 5000))

bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)

ALLOWED_GROUP_IDS = [-1002639856138, -1002557075563]
ADMIN_IDS = [123456789]  # Thay ID admin thật

VIP_FILE = "vip_users.json"

def load_vip_users():
    try:
        with open(VIP_FILE, "r") as f:
            data = json.load(f)
            return {int(k): datetime.fromisoformat(v) for k, v in data.items()}
    except:
        return {}

def save_vip_users(vip_dict):
    data = {str(k): v.isoformat() for k, v in vip_dict.items()}
    with open(VIP_FILE, "w") as f:
        json.dump(data, f)

VIP_USERS = load_vip_users()

def is_vip(user_id):
    now = datetime.utcnow()
    if user_id in VIP_USERS:
        if VIP_USERS[user_id] > now:
            return True
        else:
            del VIP_USERS[user_id]
            save_vip_users(VIP_USERS)
            return False
    return False

def add_vip(user_id, days):
    now = datetime.utcnow()
    if user_id in VIP_USERS and VIP_USERS[user_id] > now:
        VIP_USERS[user_id] += timedelta(days=days)
    else:
        VIP_USERS[user_id] = now + timedelta(days=days)
    save_vip_users(VIP_USERS)

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

@bot.message_handler(commands=["like"])
def cmd_like(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "<blockquote>❌ Bot chỉ hoạt động trong nhóm cho phép.</blockquote>", parse_mode="HTML")
        return

    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "<blockquote>⚠️ Vui lòng nhập đúng cú pháp:\n/like &lt;khu vực&gt; &lt;uid&gt;</blockquote>", parse_mode="HTML")
        return

    region = parts[1]
    uid = parts[2]

    loading_msg = bot.reply_to(message, f"<blockquote>⏳ Đang gửi lượt thích tới UID {uid}...</blockquote>", parse_mode="HTML")

    try:
        api_url = f"https://freefirelike-api.onrender.com/like?uid={uid}&server_name={region}&key=qqwweerrb"
        resp = requests.get(api_url, timeout=10)
        if resp.status_code != 200:
            bot.edit_message_text("<blockquote>❌ Lỗi khi gửi lượt thích, thử lại sau.</blockquote>",
                                  chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")
            return

        data = resp.json()
        if data.get("LikesGivenByAPI", 0) == 0:
            bot.edit_message_text(f"<blockquote>💔 UID {uid} đã nhận đủ lượt thích hôm nay.</blockquote>",
                                  chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")
            return

        nickname = data.get("PlayerNickname", "Unknown")
        likes_before = data.get("LikesbeforeCommand", 0)
        likes_after = data.get("LikesafterCommand", 0)
        likes_given = likes_after - likes_before

        reply = (
            f"<blockquote>✅ BUFF LIKE THÀNH CÔNG\n"
            f"👤 Người Chơi: {nickname}\n"
            f"🆔 UID: {uid}\n"
            f"📉 Like Trước: {likes_before}\n"
            f"📈 Like Sau: {likes_after}\n"
            f"👍 Like Đã Gửi: {likes_given}\n"
            f"───────────────\n"
            f"Liên hệ: @HaoEsports01</blockquote>"
        )

        bot.edit_message_text(reply, chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")

    except Exception as e:
        bot.edit_message_text(f"<blockquote>❌ Đã xảy ra lỗi: {e}</blockquote>",
                              chat_id=loading_msg.chat.id, message_id=loading_msg.message_id, parse_mode="HTML")

@bot.message_handler(commands=["addvip"])
def cmd_addvip(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "<blockquote>❌ Bạn không có quyền sử dụng lệnh này.</blockquote>", parse_mode="HTML")
        return

    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "<blockquote>⚠️ Cú pháp: /addvip &lt;user_id&gt; &lt;số ngày&gt;</blockquote>", parse_mode="HTML")
        return

    try:
        user_id = int(parts[1])
        days = int(parts[2])
        if days <= 0:
            bot.reply_to(message, "<blockquote>⚠️ Số ngày phải lớn hơn 0.</blockquote>", parse_mode="HTML")
            return
    except:
        bot.reply_to(message, "<blockquote>⚠️ User ID hoặc số ngày không hợp lệ.</blockquote>", parse_mode="HTML")
        return

    add_vip(user_id, days)
    bot.reply_to(message, f"<blockquote>✅ Đã cấp VIP cho user {user_id} trong {days} ngày.</blockquote>", parse_mode="HTML")

@bot.message_handler(commands=["autobuff"])
def cmd_autobuff(message):
    if not is_vip(message.from_user.id):
        bot.reply_to(message, "<blockquote>❌ Chỉ VIP mới dùng được lệnh này.</blockquote>", parse_mode="HTML")
        return

    auto_buff_list = [
        {"region": "vn", "uid": "8324665667"},
    ]

    bot.reply_to(message, f"<blockquote>⏳ Bắt đầu buff tự động cho {len(auto_buff_list)} UID...</blockquote>", parse_mode="HTML")

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

        time.sleep(2)

    bot.send_message(message.chat.id, "<blockquote>✅ Hoàn thành buff tự động!</blockquote>", parse_mode="HTML")

@bot.message_handler(commands=["test"])
def cmd_test(message):
    bot.reply_to(message, "<blockquote>✅ Lệnh test hoạt động bình thường!</blockquote>", parse_mode="HTML")

if __name__ == "__main__":
    if not BOT_TOKEN or not WEBHOOK_URL:
        raise Exception("Bạn cần đặt biến môi trường BOT_TOKEN và WEBHOOK_URL")

    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

    print("Bot đã sẵn sàng và đang chạy webhook...")

    app.run(host="0.0.0.0", port=PORT)
