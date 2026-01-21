import os
import random
import time
import requests
import telebot
from telebot.types import Message
from telebot import TeleBot
from flask import Flask, request
from datetime import datetime, timedelta

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
ALLOWED_GROUP_IDS = [-1003616607301, -1002282514761]

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang hoạt động trên Render!"



@bot.message_handler(commands=['like','Like'])
def handle_like(message):
    user_id = message.from_user.id

    # Kiểm tra người dùng đã tham gia kênh chưa
    # Kiểm tra nhóm được phép
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/tranhao1166", parse_mode="HTML")
        return

    # Kiểm tra định dạng lệnh
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Please provide a valid region and UID. Example: /like sg 10000001", parse_mode="HTML")
        return

    region = parts[1]
    uid = parts[2]

    loading_msg = bot.reply_to(message, f"⏳Sending likes to {uid}, please wait...", parse_mode="HTML")

    try:
        api_url = f"https://like-free-fire-nine.vercel.app/like?uid={uid}&server_name={region}"
        response = requests.get(api_url, timeout=15)

        if response.status_code != 200:
            bot.edit_message_text(
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                text="An error occurred. Please check account region or try again later🥲.",
                parse_mode="HTML"
            )
            return

        data = response.json()

        if "LikesGivenByAPI" not in data or "LikesbeforeCommand" not in data or "LikesafterCommand" not in data:
            bot.edit_message_text(
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                text="An error occurred. Please check account region or try again later🥲.",
                parse_mode="HTML"
            )
            return

        if data["LikesGivenByAPI"] == 0:
            bot.edit_message_text(
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                text=f"💔 UID {uid} has already received Max Likes for Today 💔. Please Try a different UID.",
                parse_mode="HTML"
            )
            return

        nickname = data.get("PlayerNickname", "Unknown")
        uid = data.get("UID", "Unknown")
        likes_before = data["LikesbeforeCommand"]
        likes_after = data["LikesafterCommand"]
        likes_given_by_bot = likes_after - likes_before

        reply = (
            f"Player Nickname: {nickname}\n"
            f"Player UID: {uid}\n"
            f"Likes before Command: {likes_before}\n"
            f"Likes after Command: {likes_after}\n"
            f"Likes given by bot: {likes_given_by_bot}\n"
            f"Group: https://t.me/FreeFireEsporrts"
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
            text="Đang lỗi hoặc đang bảo trì vui lòng thử lại sau 💔.",
            parse_mode="HTML"
        )



@bot.message_handler(commands=['level'])
def get_level(message):
    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(message, "Thiếu UID. Cú pháp: <code>/level 8324665667</code>")
        return

    uid = args[1]

    loading = bot.reply_to(message, "🔍 <b>Đang lấy level tài khoản...</b>")

    url = f"https://free-gtet.vercel.app/info?uid={uid}"

    try:
        response = requests.get(url, timeout=20)

        if response.status_code != 200:
            bot.edit_message_text(
                "❌ Không thể kết nối API.",
                message.chat.id,
                loading.message_id
            )
            return

        data = response.json()

        if "AccountInfo" not in data:
            bot.edit_message_text(
                "❌ Không tìm thấy tài khoản.",
                message.chat.id,
                loading.message_id
            )
            return

        acc = data["AccountInfo"]

        name = acc.get("AccountNickname", "N/A")
        level = acc.get("AccountLevel", 0)
        region = acc.get("AccountRegion", "N/A")

        text = (
            "<b>THÔNG TIN LEVEL TÀI KHOẢN</b>\n"
            "-------------------------\n"
            f"<b>Tên:</b> <code>{name}</code>\n"
            f"<b>Level:</b> <b>{level}</b>\n"
            f"<b>Region:</b> <b>{region}</b>\n"
            "-------------------------"
        )

        # Xóa loading
        bot.delete_message(message.chat.id, loading.message_id)

        # Gửi kết quả
        bot.send_message(message.chat.id, text)

    except Exception as e:
        print("Error:", e)
        bot.edit_message_text(
            "❌ Có lỗi hệ thống.",
            message.chat.id,
            loading.message_id
        )


@bot.message_handler(commands=['info'])
def get_info(message):
    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(message, "Lỗi: Thiếu UID. Cú pháp: <code>/info 8324665667</code>")
        return

    uid = args[1]

    # Gửi loading
    loading_msg = bot.reply_to(message, "🔍 <b>Đang lấy thông tin tài khoản...</b>")

    url = f"https://free-gtet.vercel.app/info?uid={uid}"

    try:
        response = requests.get(url, timeout=20)

        if response.status_code != 200:
            bot.edit_message_text(
                "❌ Không thể kết nối API.",
                chat_id=message.chat.id,
                message_id=loading_msg.message_id
            )
            return

        data = response.json()

        if "AccountInfo" not in data:
            bot.edit_message_text(
                "❌ Không tìm thấy dữ liệu cho UID này.",
                chat_id=message.chat.id,
                message_id=loading_msg.message_id
            )
            return

        acc = data["AccountInfo"]
        clan = data.get("clanBasicInfo", {})
        social = data.get("socialInfo", {})
        credit = data.get("creditScoreInfo", {})

        ep_status = "Co" if acc.get("Tài khoản có ElitePass") else "Khong"

        text = (
            "<b>THÔNG TIN TÀI KHOẢN FREE FIRE</b>\n"
            "----------------------------------\n"
            "<b>Tên nhân vật:</b> <code>{name}</code>\n"
            "<b>ID người chơi:</b> <code>{uid_val}</code>\n"
            "<b>Khu vực:</b> <b>{region}</b>\n"
            "<b>Cấp độ:</b> <b>{level}</b>\n"
            "<b>Kinh nghiệm:</b> <b>{exp}</b>\n"
            "<b>Lượt thích:</b> <b>{likes}</b>\n"
            "<b>Chữ ký:</b> <i>{sig}</i>\n\n"

            "<b>THÔNG SỐ XẾP HẠNG</b>\n"
            "<b>Rank Tử Chiến:</b> <b>{cs_rank}</b> (Points: <b>{cs_pts}</b>)\n"
            "<b>Rank Sinh Tồn:</b> <b>{br_rank}</b> (Points: <b>{br_pts}</b>)\n\n"

            "<b>THÔNG TIN QUÂN ĐOÀN</b>\n"
            "<b>Tên quân đoàn:</b> <b>{clan_name}</b>\n"
            "<b>ID quân đoàn:</b> <code>{clan_id}</code>\n"
            "<b>Cấp độ QĐ:</b> <b>{clan_lvl}</b>\n\n"

            "<b>CHI TIẾT KHÁC</b>\n"
            "<b>Elite Pass:</b> <b>{ep}</b>\n"
            "<b>Điểm uy tín:</b> <b>{credit_score}</b>\n"
            "<b>Phiên bản:</b> <b>{version}</b>\n"
            "----------------------------------"
        ).format(
            name=acc.get('AccountNickname', 'N/A'),
            uid_val=acc.get('AccountID', uid),
            region=acc.get('AccountRegion', 'N/A'),
            level=acc.get('AccountLevel', 0),
            exp=acc.get('exp', 0),
            likes=acc.get('AccountLiked', 0),
            sig=social.get('signature', 'Trong'),
            cs_rank=acc.get('CsRank', 0),
            cs_pts=acc.get('CsRankingPoints', 0),
            br_rank=acc.get('AccountRank', 0),
            br_pts=acc.get('AccountRankingPoints', 0),
            clan_name=clan.get('clanName', 'Khong co'),
            clan_id=clan.get('clanId', 'N/A'),
            clan_lvl=clan.get('clanLevel', 0),
            ep=ep_status,
            credit_score=credit.get('creditScore', 'N/A'),
            version=data.get('releaseVersion', 'N/A')
        )

        # Xóa loading
        bot.delete_message(message.chat.id, loading_msg.message_id)

        # Gửi kết quả
        bot.send_message(message.chat.id, text)

    except Exception as e:
        print("Error:", e)
        bot.edit_message_text(
            "❌ Có lỗi hệ thống xảy ra.",
            chat_id=message.chat.id,
            message_id=loading_msg.message_id
        )


# 4. Chạ
@bot.message_handler(commands=["admin"])
def cmd_test(message):
    bot.reply_to(message, "<blockquote>✅ Liên Hệ: @nhathaov</blockquote>", parse_mode="HTML")

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
