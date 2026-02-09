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


import time
import requests
from telebot.types import Message

# 👉 PUT YOUR GROUP ID HERE
ALLOWED_GROUP_ID = -1001234567890  # change this

user_last_like_day = {}

@bot.message_handler(commands=['likes'])
def like_handler(message: Message):
    # ❌ Ignore private chats
    if message.chat.type == "private":
        return

    # ❌ Only allow specific group
    if message.chat.id != ALLOWED_GROUP_ID:
        return

    user_id = message.from_user.id
    current_day = time.strftime("%Y-%m-%d", time.gmtime())

    # ⛔ Limit: once per day per user
    if user_last_like_day.get(user_id) == current_day:
        bot.reply_to(message, "⏳ You can only use this command once per day.")
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Usage: /likes UID")
        return

    uid = parts[1]
    api_url = f"https://like-free-firee.vercel.app/like?uid={uid}&server_name=vn"

    try:
        loading_msg = bot.reply_to(message, "⏳ Sending likes, please wait...")
    except:
        return

    def safe_get(data, key):
        value = data.get(key)
        return str(value) if value not in [None, "", "null"] else "Unknown"

    def extract_number(text):
        if isinstance(text, int):
            return str(text)
        for part in str(text).split():
            if part.isdigit():
                return part
        return "Unknown"

    try:
        response = requests.get(api_url, timeout=15)
        data = response.json()
    except:
        bot.edit_message_text(
            "❌ Failed to connect to API. Try again later.",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id
        )
        return

    if not data or data.get("status") != 1:
        bot.edit_message_text(
            "⚠️ Server is busy or under maintenance. Try again later.",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id
        )
        return

    # ✅ Save usage day
    user_last_like_day[user_id] = current_day

    name = safe_get(data, 'PlayerNickname')
    uid_str = safe_get(data, 'UID')
    like_before = safe_get(data, 'LikesbeforeCommand')
    like_after = safe_get(data, 'LikesafterCommand')
    like_sent = extract_number(data.get('LikesGivenByAPI'))

    reply_text = (
        "✅ Likes Send Success\n"
        f"👤 Name: {name}\n"
        f"🆔 UID: {uid_str}\n"
        f"🌏 Region: vn\n"
        f"📉 Likes Before: {like_before}\n"
        f"📈 Likes After: {like_after}\n"
        f"👍 Likes Sent: {like_sent}"
    )

    if data.get("status") == 2:
        reply_text += "\n⚠️ Daily like limit reached for this account."

    try:
        bot.edit_message_text(
            reply_text,
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id
        )
    except Exception as e:
        print(f"Error sending result: {e}")




from collections import defaultdict
from datetime import datetime, timedelta

visit_limits = defaultdict(lambda: {"count": 0, "reset_time": datetime.utcnow()})
MAX_VISITS = 4
RESET_AFTER = timedelta(days=1)

        
@bot.message_handler(commands=["visit"])
def handle_visit(message):
    user_id = message.from_user.id
    user_data = visit_limits[user_id]
    now = datetime.utcnow()

    # 🔄 Reset nếu đã qua 24h
    if now >= user_data["reset_time"]:
        user_data["count"] = 0
        user_data["reset_time"] = now + RESET_AFTER

    # 🚫 Check giới hạn
    if user_data["count"] >= MAX_VISITS:
        remaining_time = user_data["reset_time"] - now
        hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
        minutes = remainder // 60

        bot.reply_to(
            message,
            f"🚫 <b>You have used all 5 visits today.</b>\n"
            f"⏳ Try again in {hours}h {minutes}m.",
            parse_mode="HTML"
        )
        return

    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Please double check the UID or Region.")
        return

    region = parts[1]
    uid = parts[2]

    loading = bot.reply_to(message, "⏳ <b>Sending Visits in Progress</b>", parse_mode="HTML")

    try:
        r = requests.get(
            "https://visit-amotvts.vercel.app/visit",
            params={"region": region, "uid": uid},
            timeout=60
        )
        r.raise_for_status()
        data = r.json()

        if data.get("success", 0) == 0:
            bot.edit_message_text(
                "❌ <b>API Handling Failed</b>",
                loading.chat.id,
                loading.message_id,
                parse_mode="HTML"
            )
            return

        # ✅ Thành công → tăng lượt
        user_data["count"] += 1
        remaining = MAX_VISITS - user_data["count"]

        bot.edit_message_text(
            "✅ <b>Visit Success</b>\n\n"
            f"👤 <b>Nickname:</b> {data.get('nickname')}\n"
            f"🆔 <b>UID:</b> <code>{data.get('uid')}</code>\n"
            f"🌍 <b>Region:</b> {data.get('region')}\n"
            f"⭐ <b>Level:</b> {data.get('level')}\n"
            f"❤️ <b>Likes:</b> {data.get('likes')}\n"
            f"📈 <b>Success:</b> {data.get('success')}\n\n"
            f"🔢 <b>Remaining today:</b> {remaining}/5",
            loading.chat.id,
            loading.message_id,
            parse_mode="HTML"
        )

    except requests.exceptions.RequestException:
        bot.edit_message_text(
            "<b>❌ Network error. Please try again.</b>",
            loading.chat.id,
            loading.message_id,
            parse_mode="HTML"
        )

    except Exception:
        bot.edit_message_text(
            "<b>⚠️ Unexpected error occurred.</b>",
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
