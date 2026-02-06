import os
import requests
import telebot
from flask import Flask, request
from datetime import datetime
import pytz

# ================== CONFIG ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

if not BOT_TOKEN or not WEBHOOK_URL:
    raise Exception("❌ Thiếu BOT_TOKEN hoặc WEBHOOK_URL")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

# ================== BASIC ROUTES ==================
@app.route("/")
def home():
    return "Bot is running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# ================== /LIKE COMMAND ==================

ALLOWED_GROUP_ID = -1003616607301


@bot.message_handler(commands=["like"])
def handle_like(message):
    # ❌ Ignore private messages
    if message.chat.type == "private":
        return

    # ❌ Chỉ cho phép group được chỉ định
    if message.chat.id != ALLOWED_GROUP_ID:
        return

    parts = message.text.split()

    # ❌ Sai cú pháp
    if len(parts) < 3:
        bot.reply_to(
            message,
            "<b>Usage:</b> <code>/like sg 123456789</code>",
            parse_mode="HTML"
        )
        return

    region = parts[1].lower()
    uid = parts[2]

    # ❌ UID không hợp lệ
    if not uid.isdigit():
        bot.reply_to(
            message,
            "<b>UID must be numbers only.</b>",
            parse_mode="HTML"
        )
        return

    # ⏳ Loading message
    loading = bot.reply_to(
        message,
        "⏳ <b>Sending likes...</b>",
        parse_mode="HTML"
    )

    api_url = f"https://like-free-firee.vercel.app/like?uid={uid}&server_name={region}"

    try:
        r = requests.get(api_url, timeout=15)

        if r.status_code != 200:
            bot.edit_message_text(
                "<b>API is overloaded. Try again later.</b>",
                loading.chat.id,
                loading.message_id,
                parse_mode="HTML"
            )
            return

        data = r.json()

        # ❌ Max likes
        if data.get("LikesGivenByAPI", 0) == 0:
            bot.edit_message_text(
                "💔 <b>Player reached max likes today.</b>",
                loading.chat.id,
                loading.message_id,
                parse_mode="HTML"
            )
            return

        nickname = data.get("PlayerNickname", "Unknown")
        likes_before = data.get("LikesbeforeCommand", 0)
        likes_after = data.get("LikesafterCommand", 0)
        likes_given = max(likes_after - likes_before, 0)

        reply = (
            " ✅ <b>Likes Sent</b>\n"
            f"👤 <b>Nickname:</b> {nickname}\n"
            f"🆔 <b>UID:</b> <code>{uid}</code>\n"
            f"❤️ <b>Likes Given:</b> {likes_given}\n"
            f"📈 <b>Likes Before:</b> {likes_before}\n"
            f"📉 <b>Likes After:</b> {likes_after}"
        )

        bot.edit_message_text(
            reply,
            loading.chat.id,
            loading.message_id,
            parse_mode="HTML"
        )

    except requests.exceptions.RequestException:
        bot.edit_message_text(
            "<b>Network error. Please try again.</b>",
            loading.chat.id,
            loading.message_id,
            parse_mode="HTML"
        )

    except Exception:
        bot.edit_message_text(
            "<b>Unexpected error occurred.</b>",
            loading.chat.id,
            loading.message_id,
            parse_mode="HTML"
    )
        

# ================== WELCOME NEW MEMBER ==================
VIDEO_URL = "https://api.tiktokv.com/aweme/v1/play/?file_id=2fab7e5637e64628a0e0d98f3f6028a0&is_play_url=1&item_id=7508799426123549957&line=0&signaturev3=dmlkZW9faWQ7ZmlsZV9pZDtpdGVtX2lkLjQ1MWYyY2Y5YzhlMzRjMGYzNGM0NTVlYmY3NmFkYzdl&source=FEED&video_id=v09044g40000d0q9pb7og65v3lr1sqc0&name=taivideo.vn - Geto Kenjaku Desktop live wallpaper geto getosuguru kenjaku jujutsukaisen desktoplivewallpapers anim.mp4"

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        caption = f"""
<pre>
👋 Welcome {user.first_name}!

👍 FREE FIRE LIKE BOT
Format : /like {{region}} {{uid}}
Example: /like vn 12345678

🚀 More features coming soon
Thanks for joining 😁
</pre>
"""
        bot.send_video(message.chat.id, VIDEO_URL, caption=caption)

# ================== /ID COMMAND ==================
@bot.message_handler(commands=['id', 'info'])
def user_info(message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user

    info = f"""
<pre>
📌 TELEGRAM USER INFO
├ ID       : {user.id}
├ Name     : {user.first_name or ""} {user.last_name or ""}
├ Username : @{user.username if user.username else "None"}
├ Language : {user.language_code}
└ Is Bot   : {user.is_bot}
</pre>
"""

    photos = bot.get_user_profile_photos(user.id, limit=1)
    if photos.total_count > 0:
        bot.send_photo(message.chat.id, photos.photos[0][-1].file_id, caption=info)
    else:
        bot.send_message(message.chat.id, info)


# ================== START APP ==================
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
