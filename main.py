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
    

    # ✅ Giới hạn nhóm sử dụng
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "<blockquote>Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/HaoEsport01</blockquote>", parse_mode="HTML")
        return

    # ✅ Kiểm tra người dùng đã vượt KEY chư

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
            f"🔹 UID: {uid}\n"
            f"🔸 Like Trước: {likes_before}\n"
            f"🔸 Like Sau: {likes_after}\n"
            f"🔹 Like Đã Gửi: {likes_given_by_bot}\n"
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


API_BASE = "https://ffwlxd-info.vercel.app/player-info"

def format_timestamp(ts):
    try:
        return datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return "N/A"

@bot.message_handler(commands=['info'])
def get_ff_info(message):
    args = message.text.strip().split()
    if len(args) != 3:
        bot.reply_to(message, "<blockquote>❗ Dùng đúng cú pháp:\n/info &lt;region&gt; &lt;uid&gt;\nVí dụ: /info sg 1341742864</blockquote>")
        return

    region = args[1].lower()
    uid = args[2]
    url = f"{API_BASE}?region={region}&uid={uid}"

    try:
        res = requests.get(url)
        data = res.json()

        if "AccountInfo" not in data:
            bot.reply_to(message, "<blockquote>⚠️ Không tìm thấy tài khoản. UID hoặc Region không hợp lệ.</blockquote>")
            return

        info = data["AccountInfo"]
        credit = data.get("creditScoreInfo", {})
        pet = data.get("petInfo", {})
        social = data.get("socialinfo", {})
        guild = data.get("GuildInfo", {})

        msg = (
            "<b>✅THÔNG TIN TÀI KHOẢN</b>\n\n"
            "<blockquote>"
            f"🔰 <b>Nickname:</b> {info.get('AccountName', 'N/A')}\n"
            f"🆔 <b>UID:</b> {uid}\n"
            f"🗺️ <b>Region:</b> {info.get('AccountRegion', 'N/A')}\n"
            f"⭐ <b>Level:</b> {info.get('AccountLevel', 'N/A')}\n"
            f"🎯 <b>EXP:</b> {info.get('AccountEXP', 'N/A')}\n"
            f"❤️ <b>Likes:</b> {info.get('AccountLikes', 'N/A')}\n"
            f"🏆 <b>BR Max Rank:</b> {info.get('BrMaxRank', 'N/A')}\n"
            f"⚔️ <b>CS Max Rank:</b> {info.get('CsMaxRank', 'N/A')}\n"
            f"📦 <b>Elite Pass:</b> {'✅' if info.get('hasElitePass') else '❌'}\n"
            f"🕒 <b>Tạo lúc:</b> {format_timestamp(info.get('AccountCreateTime', '0'))}\n"
            f"📲 <b>Đăng nhập cuối:</b> {format_timestamp(info.get('AccountLastLogin', '0'))}\n"
            f"🎮 <b>Version:</b> {info.get('ReleaseVersion', 'N/A')}\n"
        )

        if guild.get("GuildName"):
            msg += (
                f"\n🏰 <b>Guild:</b> {guild.get('GuildName')}\n"
                f"👥 <b>Thành viên:</b> {guild.get('GuildMember', 'N/A')}/{guild.get('GuildCapacity', 'N/A')}\n"
                f"📶 <b>Guild Level:</b> {guild.get('GuildLevel', 'N/A')}\n"
            )

        if "creditScore" in credit:
            msg += f"\n💳 <b>Credit Score:</b> {credit['creditScore']}\n"

        if "id" in pet:
            msg += (
                f"\n🐾 <b>Pet ID:</b> {pet['id']}\n"
                f"🔢 <b>Pet Level:</b> {pet['level']}\n"
                f"📈 <b>Pet EXP:</b> {pet['exp']}\n"
            )

        if social.get("AccountSignature"):
            msg += f"\n✍️ <b>Signature:</b> {social['AccountSignature']}\n"

        msg += "</blockquote>\n✅ <i>API by @HaoEsports</i>"

        bot.reply_to(message, msg)

    except Exception:
        bot.reply_to(message, "<blockquote>🚫 Lỗi khi truy cập dữ liệu. Vui lòng thử lại sau.</blockquote>")


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
