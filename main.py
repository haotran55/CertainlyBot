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
@bot.message_handler(commands=['like', 'Like'])
def handle_like(message):
    parts = message.text.split()

    if len(parts) < 3:
        bot.reply_to(
            message,
            "❌ Invalid format\n<b>Usage:</b> <code>/like vn 10000001</code>"
        )
        return

    region = parts[1].lower()
    uid = parts[2]

    loading = bot.reply_to(
        message,
        f"⏳ Sending likes to UID <code>{uid}</code>..."
    )

    api_url = f"https://like-free-fire-nine.vercel.app/like?uid={uid}&server_name={region}"

    try:
        r = requests.get(api_url, timeout=15)

        if r.status_code != 200:
            bot.edit_message_text(
                "❌ API error. Try again later.",
                loading.chat.id,
                loading.message_id
            )
            return

        data = r.json()

        if data.get("LikesGivenByAPI", 0) == 0:
            bot.edit_message_text(
                f"<blockquote>💔 UID <code>{uid}</code> reached daily limit.</blockquote>",
                loading.chat.id,
                loading.message_id
            )
            return

        reply = f"""
<blockquote>
🎮 <b>LIKE SUCCESS</b>
──────────────
👤 Name : {data.get("PlayerNickname","Unknown")}
🆔 UID  : {data.get("UID", uid)}
❤️ Likes Given : {data["LikesafterCommand"] - data["LikesbeforeCommand"]}
📈 Before : {data["LikesbeforeCommand"]}
📉 After  : {data["LikesafterCommand"]}
──────────────
📩 Contact : @nhathaov
</blockquote>
"""
        bot.edit_message_text(reply, loading.chat.id, loading.message_id)

    except Exception as e:
        print("Like error:", e)
        bot.edit_message_text(
            "<blockquote>❌ System error. Try again later.</blockquote>",
            loading.chat.id,
            loading.message_id
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

# ================== /TIME COMMAND ==================
COUNTRY_TIMEZONES = {
    "viet nam": "Asia/Ho_Chi_Minh",
    "vietnam": "Asia/Ho_Chi_Minh",
    "india": "Asia/Kolkata",
    "nepal": "Asia/Kathmandu",
    "japan": "Asia/Tokyo",
    "korea": "Asia/Seoul",
    "china": "Asia/Shanghai",
    "thailand": "Asia/Bangkok",
    "usa": "America/New_York",
    "uk": "Europe/London",
    "france": "Europe/Paris"
}

@bot.message_handler(commands=['time'])
def time_cmd(message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        bot.reply_to(message, "<pre>❌ Use: /time viet nam | india | japan</pre>")
        return

    key = args[1].lower()
    if key not in COUNTRY_TIMEZONES:
        bot.reply_to(message, "<pre>❌ Country not found.</pre>")
        return

    tz = pytz.timezone(COUNTRY_TIMEZONES[key])
    now = datetime.now(tz)

    bot.reply_to(
        message,
        f"""
<pre>
🌍 WORLD TIME
Country : {key.title()}
Time    : {now.strftime('%H:%M:%S')}
Date    : {now.strftime('%d-%m-%Y')}
Zone    : {COUNTRY_TIMEZONES[key]}
</pre>
"""
    )

# ================== START APP ==================
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
