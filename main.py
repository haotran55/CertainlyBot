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


app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang hoạt động trên Render!"

@bot.message_handler(commands=['like'])
def handle_like(message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❗ Please use the correct syntax: /like [uid] [region]\nExample: /like 12345678 sg")
            return

        uid = parts[1]
        region = parts[2]

        # Send loading notification
        loading_msg = bot.reply_to(message, "🔄 Processing...")

        api_url = f"https://freefirelike-api.onrender.com/like?uid={uid}&server_name={region}&key=tranhao116b"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        likes_start_day = data.get("LikesGivenByAPI", 0)

        # If LikesGivenByAPI == 0, report specific error
        if likes_start_day == 0:
            error_msg = f"UID {uid} has already received Max Likes for Today. Please Try a different UID."
            bot.edit_message_text(
                chat_id=loading_msg.chat.id,
                message_id=loading_msg.message_id,
                text=error_msg
            )
            return

        nickname = data.get("PlayerNickname", "Unknown")
        likes_before = data.get("LikesbeforeCommand", 0)
        likes_after = data.get("LikesafterCommand", 0)
        likes_given_by_bot = likes_after - likes_before

        reply = (
            f"Likes Sent ✅\n"
            f"Player Nickname: {nickname}\n"
            f"Before Likes: {likes_before}\n"
            f"After Likes: {likes_after}\n"
            f"Likes Given By Bot: {likes_given_by_bot}\n"
            f"@checkinfo123"
        )

        # Edit loading message to show result
        bot.edit_message_text(
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            text=reply
        )

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")


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
