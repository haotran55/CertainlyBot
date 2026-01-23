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


import requests
import json
from requests.exceptions import Timeout, RequestException

@bot.message_handler(commands=['like', 'Like'])
def handle_like(message):
    user_id = message.from_user.id

    # Check allowed group
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(
            message,
            "🚫 This bot only works in the authorized group.\n"
            "👉 https://t.me/FreeFireEsporrts"
        )
        return

    # Check command format
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(
            message,
            "❌ Invalid format\n"
            "<b>Usage:</b> <code>/like vn 10000001</code>",
            parse_mode="HTML"
        )
        return

    region = parts[1].lower()
    uid = parts[2]

    loading_msg = bot.reply_to(
        message,
        f"⏳ Sending likes to UID <code>{uid}</code>...",
        parse_mode="HTML"
    )

    api_url = f"https://like-free-fire-nine.vercel.app/like?uid={uid}&server_name={region}"

    try:
        response = requests.get(api_url, timeout=15)

        # Status code lỗi
        if response.status_code != 200:
            bot.edit_message_text(
                f"❌ API Error ({response.status_code})\nPlease try again later.",
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id
            )
            return

        # Check JSON
        if "application/json" not in response.headers.get("Content-Type", ""):
            bot.edit_message_text(
                "❌ API returned invalid data (not JSON).",
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id
            )
            return

        data = response.json()

        required_keys = [
            "LikesGivenByAPI",
            "LikesbeforeCommand",
            "LikesafterCommand"
        ]

        if not all(k in data for k in required_keys):
            bot.edit_message_text(
                "❌ Invalid API response.\nPlease try again later.",
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id
            )
            return

        if data["LikesGivenByAPI"] == 0:
            bot.edit_message_text(
                f"💔 UID <code>{uid}</code> has reached daily like limit.",
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                parse_mode="HTML"
            )
            return

        nickname = data.get("PlayerNickname", "Unknown")
        uid = data.get("UID", uid)
        likes_before = data["LikesbeforeCommand"]
        likes_after = data["LikesafterCommand"]
        likes_given = likes_after - likes_before

        reply = (
           f"<b>╭ Player Name:</b> {nickname}\n"
           f"<b>├ Player UID:</b> {uid}\n"
           f"<b>├ Likes Given:</b> {likes_given}\n"
           f"<b>├ Likes Before:</b> {likes_before}\n"
           f"<b>├ Likes After:</b> {likes_after}\n"
           f"<b>╰ Contact:</b> @nhathaov"
        )



        bot.edit_message_text(
            reply,
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            parse_mode="HTML"
        )

    except Timeout:
        bot.edit_message_text(
            "⏳ API timeout.\nPlease try again later.",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id
        )

    except RequestException as e:
        print("Request error:", e)
        bot.edit_message_text(
            "🌐 Cannot connect to API.\nPlease try again later.",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id
        )

    except Exception as e:
        print("Unknown error:", e)
        bot.edit_message_text(
            "❌ Unexpected system error.",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id
        )



@bot.message_handler(commands=['level'])
def get_level(message):
    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(
            message,
            "Missing UID.\nUsage: /level 8324665667"
        )
        return

    uid = args[1]

    loading = bot.reply_to(
        message,
        "🔍 Loading account level information..."
    )

    url = f"https://free-gtet.vercel.app/info?uid={uid}"

    try:
        response = requests.get(url, timeout=20)

        if response.status_code != 200:
            bot.edit_message_text(
                "❌ Failed to connect to the API.",
                message.chat.id,
                loading.message_id
            )
            return

        data = response.json()

        if "AccountInfo" not in data:
            bot.edit_message_text(
                "❌ Account not found.",
                message.chat.id,
                loading.message_id
            )
            return

        acc = data["AccountInfo"]

        name = acc.get("AccountNickname", "N/A")
        level = acc.get("AccountLevel", 0)
        region = acc.get("AccountRegion", "N/A")

        text = (
            "📊 ACCOUNT LEVEL INFORMATION\n"
            "----------------------------\n"
            f"Name   : {name}\n"
            f"Level  : {level}\n"
            f"Region : {region}\n"
            "----------------------------"
        )

        # Remove loading message
        bot.delete_message(message.chat.id, loading.message_id)

        # Send result
        bot.send_message(message.chat.id, text)

    except Exception as e:
        print("Error:", e)
        bot.edit_message_text(
            "❌ A system error occurred.",
            message.chat.id,
            loading.message_id
        )


@bot.message_handler(commands=['info'])
def get_info(message):
    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(
            message,
            "Missing UID.\nUsage: /info 8324665667"
        )
        return

    uid = args[1]

    # Send loading message
    loading_msg = bot.reply_to(
        message,
        "🔍 Loading account information..."
    )

    url = f"https://free-gtet.vercel.app/info?uid={uid}"

    try:
        response = requests.get(url, timeout=20)

        if response.status_code != 200:
            bot.edit_message_text(
                "❌ Failed to connect to the API.",
                chat_id=message.chat.id,
                message_id=loading_msg.message_id
            )
            return

        data = response.json()

        if "AccountInfo" not in data:
            bot.edit_message_text(
                "❌ Account data not found.",
                chat_id=message.chat.id,
                message_id=loading_msg.message_id
            )
            return

        acc = data.get("AccountInfo", {})
        clan = data.get("clanBasicInfo", {})
        social = data.get("socialInfo", {})
        credit = data.get("creditScoreInfo", {})

        ep_status = "Yes" if acc.get("Tài khoản có ElitePass") else "No"

        text = (
            "🎮 FREE FIRE ACCOUNT INFORMATION\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Name        : {acc.get('AccountNickname', 'N/A')}\n"
            f"Player ID   : {acc.get('AccountID', uid)}\n"
            f"Region      : {acc.get('AccountRegion', 'N/A')}\n"
            f"Level       : {acc.get('AccountLevel', 0)}\n"
            f"Experience  : {acc.get('exp', 0)}\n"
            f"Likes       : {acc.get('AccountLiked', 0)}\n"
            f"Signature   : {social.get('signature', 'Empty')}\n"
            "\n"
            "🏆 RANK INFORMATION\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Clash Squad : {acc.get('CsRank', 0)} "
            f"(Points: {acc.get('CsRankingPoints', 0)})\n"
            f"Battle Royale: {acc.get('AccountRank', 0)} "
            f"(Points: {acc.get('AccountRankingPoints', 0)})\n"
            "\n"
            "👥 CLAN INFORMATION\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Clan Name   : {clan.get('clanName', 'None')}\n"
            f"Clan ID     : {clan.get('clanId', 'N/A')}\n"
            f"Clan Level  : {clan.get('clanLevel', 0)}\n"
            "\n"
            "📌 OTHER DETAILS\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Elite Pass  : {ep_status}\n"
            f"Credit Score: {credit.get('creditScore', 'N/A')}\n"
            f"Version     : {data.get('releaseVersion', 'N/A')}\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

        # Remove loading message
        bot.delete_message(message.chat.id, loading_msg.message_id)

        # Send result
        bot.send_message(message.chat.id, text)

    except Exception as e:
        print("Error:", e)
        bot.edit_message_text(
            "❌ A system error occurred.",
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
