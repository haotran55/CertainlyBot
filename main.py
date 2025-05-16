import os
import threading
import requests
import telebot
from telebot import TeleBot
from telebot.types import Message
from flask import Flask, request
from datetime import datetime
from io import BytesIO
import json
import time

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
ALLOWED_GROUP_IDS = [-1002639856138, -1002557075563]

# Danh sách admin (bạn sửa user_id admin thật vào đây)
ADMIN_IDS = [
    7658079324,  # Thay bằng ID admin thật
]

VIP_FILE = "vip_users.json"
AUTO_BUFF_FILE = "auto_buff_list.json"

VIP_USERS = []
AUTO_BUFF_LIST = []

def load_vip_users():
    global VIP_USERS
    try:
        with open(VIP_FILE, "r") as f:
            VIP_USERS = json.load(f)
    except Exception:
        VIP_USERS = []

def save_vip_users():
    with open(VIP_FILE, "w") as f:
        json.dump(VIP_USERS, f, indent=2)

def load_auto_buff_list():
    global AUTO_BUFF_LIST
    try:
        with open(AUTO_BUFF_FILE, "r") as f:
            AUTO_BUFF_LIST = json.load(f)
    except Exception:
        AUTO_BUFF_LIST = []

def save_auto_buff_list():
    with open(AUTO_BUFF_FILE, "w") as f:
        json.dump(AUTO_BUFF_LIST, f, indent=2)

load_vip_users()
load_auto_buff_list()

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang hoạt động trên Render!"

def is_vip(user_id):
    return user_id in VIP_USERS

def is_admin(user_id):
    return user_id in ADMIN_IDS

@bot.message_handler(commands=['addvip'])
def handle_add_vip(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này.")
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "⚠️ Cú pháp: /addvip <user_id>")
        return
    
    try:
        new_vip_id = int(parts[1])
    except ValueError:
        bot.reply_to(message, "⚠️ User ID phải là số nguyên.")
        return
    
    if new_vip_id in VIP_USERS:
        bot.reply_to(message, f"⚠️ User ID {new_vip_id} đã là VIP rồi.")
        return
    
    VIP_USERS.append(new_vip_id)
    save_vip_users()
    bot.reply_to(message, f"✅ Đã thêm User ID {new_vip_id} vào danh sách VIP.")

@bot.message_handler(commands=['like'])
def handle_like(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "<blockquote>Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/HaoEsport01</blockquote>", parse_mode="HTML")
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

@bot.message_handler(commands=['autolike'])
def handle_autolike(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "<blockquote>Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/HaoEsport01</blockquote>", parse_mode="HTML")
        return

    if not is_vip(message.from_user.id):
        bot.reply_to(message, "<blockquote>❌ Lệnh này chỉ dành cho VIP. Vui lòng liên hệ admin để nâng cấp.</blockquote>", parse_mode="HTML")
        return
    
    if not AUTO_BUFF_LIST:
        bot.reply_to(message, "<blockquote>⚠️ Danh sách tự động buff hiện đang trống. Vui lòng thêm UID bằng lệnh /addautolike</blockquote>", parse_mode="HTML")
        return
    
    loading_msg = bot.reply_to(message, "<blockquote>⏳ Đang tự động buff like, vui lòng chờ...</blockquote>", parse_mode="HTML")
    
    total_likes_sent = 0
    
    for account in AUTO_BUFF_LIST:
        region = account["region"]
        uid = account["uid"]
        
        try:
            api_url = f"https://freefirelike-api.onrender.com/like?uid={uid}&server_name={region}&key=qqwweerrb"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code != 200:
                continue
            
            data = response.json()
            
            if data.get("LikesGivenByAPI", 0) == 0:
                continue
            
            likes_before = data.get("LikesbeforeCommand", 0)
            likes_after = data.get("LikesafterCommand", 0)
            likes_given_by_api = likes_after - likes_before
            
            total_likes_sent += likes_given_by_api
            
            time.sleep(2)
        
        except Exception:
            continue
    
    bot.edit_message_text(
        chat_id=loading_msg.chat.id,
        message_id=loading_msg.message_id,
        text=f"<blockquote>✅ Đã hoàn tất tự động buff like.\nTổng lượt like đã gửi: {total_likes_sent}\nLiên hệ: @HaoEsports01</blockquote>",
        parse_mode="HTML"
    )

@bot.message_handler(commands=['addautolike'])
def handle_add_autolike(message):
    if not is_vip(message.from_user.id):
        bot.reply_to(message, "<blockquote>❌ Lệnh này chỉ dành cho VIP. Vui lòng liên hệ admin để nâng cấp.</blockquote>", parse_mode="HTML")
        return
    
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "<blockquote>⚠️ Vui lòng nhập đúng định dạng:\n/addautolike <region> <uid>\nVí dụ: /addautolike vn 8324665667</blockquote>", parse_mode="HTML")
        return
    
    region = parts[1].lower()
    uid = parts[2]

    for acc in AUTO_BUFF_LIST:
        if acc["uid"] == uid and acc["region"] == region:
            bot.reply_to(message, f"<blockquote>⚠️ UID {uid} khu vực {region} đã có trong danh sách tự động buff rồi.</blockquote>", parse_mode="HTML")
            return
    
    AUTO_BUFF_LIST.append({"region": region, "uid": uid})
    save_auto_buff_list()
    bot.reply_to(message, f"<blockquote>✅ Đã thêm UID {uid} khu vực {region} vào danh sách tự động buff.</blockquote>", parse_mode="HTML")

@bot.message_handler(commands=['removeautolike'])
def handle_remove_autolike(message):
    if not is_vip(message.from_user.id):
        bot.reply_to(message, "❌ Lệnh này chỉ dành cho VIP.")
        return
    
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "⚠️ Cú pháp: /removeautolike <region> <uid>")
        return
    
    region = parts[1].lower()
    uid = parts[2]

    for acc in AUTO_BUFF_LIST:
        if acc["uid"] == uid and acc["region"] == region:
            AUTO_BUFF_LIST.remove(acc)
            save_auto_buff_list()
            bot.reply_to(message, f"✅ Đã xóa UID {uid} khu vực {region} khỏi danh sách.")
            return
    
    bot.reply_to(message, f"⚠️ Không tìm thấy UID {uid} khu vực {region} trong danh sách.")

@bot.message_handler(commands=['listautolike'])
def handle_list_autolike(message):
    if not is_vip(message.from_user.id):
        bot.reply_to(message, "❌ Lệnh này chỉ dành cho VIP.")
        return
    
    if not AUTO_BUFF_LIST:
        bot.reply_to(message, "Danh sách tự động buff hiện đang trống.")
        return
    
    text = "📋 Danh sách UID tự động buff:\n"
    for i, acc in enumerate(AUTO_BUFF_LIST, 1):
        text += f"{i}. Region: {acc['region']} - UID: {acc['uid']}\n"
    bot.reply_to(message, text)

# Các lệnh /follow, webhook, chạy bot ... giữ nguyên

@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok', 200

if __name__ == "__main__":
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
    if not WEBHOOK_URL:
        raise Exception("Thiếu biến môi trường WEBHOOK_URL")

    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

    app.run(host="0
