import os
import threading
import requests
import telebot  # Thêm dòng này để sử dụng telebot
from flask import Flask, request
from datetime import datetime
from io import BytesIO

# Lấy token từ biến môi trường
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
ALLOWED_GROUP_IDS = [-1002639856138]

# Flask App
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang hoạt động trên Render!"


# Hàm lấy tên item (nếu cần tên)
@bot.message_handler(func=lambda message: message.text.lower().startswith('get'))
def get_player_stats(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "❌ Bot Chỉ Hoạt Động Trong Nhóm Này.\n👉 Link: https://t.me/HaoEsport01")
        return
        
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ Format: Get {UID} {region}")
            return

        uid = parts[1]
        region = parts[2].upper()

        api_url = f"https://free-fire-gnwz.onrender.com/api/account?uid={uid}&region={region}"

        response = requests.get(api_url)
        data = response.json()

        # Trích xuất dữ liệu
        basic = data.get("basicInfo", {})
        profile = data.get("profileInfo", {})
        clan = data.get("clanBasicInfo", {})
        pet = data.get("petInfo", {})
        social = data.get("socialInfo", {})
        credit = data.get("creditScoreInfo", {})

        response_text = f"""
🎮 𝗙𝗥𝗘𝗘 𝗙𝗜𝗥𝗘 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗜𝗡𝗙𝗢 🎮

👤 𝗣𝗟𝗔𝗬𝗘𝗥 𝗗𝗘𝗧𝗔𝗜𝗟𝗦
━━━━━━━━━━━━━━━
📝 Name: {basic.get('nickname', 'N/A')}
🆔 UID: {uid}
🌍 Region: {basic.get('region', 'N/A')}
📊 Level: {basic.get('level', 'N/A')}
❤️ Likes: {basic.get('liked', 'N/A')}
🎮 Version: {basic.get('releaseVersion', 'N/A')}

🖼️ 𝗜𝗠𝗔𝗚𝗘𝗦 (ID Only)
━━━━━━━━━━━━━━━
🧑 Avatar ID: {profile.get('avatarId', 'N/A')}
🎨 Banner ID: {basic.get('bannerId', 'N/A')}
🖼️ HeadPic ID: {basic.get('headPic', 'N/A')}

🏆 𝗥𝗔𝗡𝗞 𝗜𝗡𝗙𝗢
━━━━━━━━━━━━━━━
🎯 BR Rank ID: {basic.get('rank', 'N/A')}
📈 BR Points: {basic.get('rankingPoints', 'N/A')}
⚔️ CS Rank ID: {basic.get('csRank', 'N/A')}
📊 CS Points: {basic.get('csRankingPoints', 'N/A')}

🏰 𝗖𝗟𝗔𝗡 𝗜𝗡𝗙𝗢
━━━━━━━━━━━━━━━
🏷️ Name: {clan.get('clanName', 'N/A')}
📑 ID: {clan.get('clanId', 'N/A')}
📈 Level: {clan.get('clanLevel', 'N/A')}
👥 Members: {clan.get('memberNum', 'N/A')}/{clan.get('capacity', 'N/A')}

🐾 𝗣𝗘𝗧 𝗜𝗡𝗙𝗢
━━━━━━━━━━━━━━━
🐶 Name: {pet.get('name', 'N/A')}
🆔 ID: {pet.get('id', 'N/A')}
📊 Level: {pet.get('level', 'N/A')}
⭐ EXP: {pet.get('exp', 'N/A')}

📱 𝗦𝗢𝗖𝗜𝗔𝗟 𝗜𝗡𝗙𝗢
━━━━━━━━━━━━━━━
🌐 Language: {social.get('language', 'N/A')}
🎮 Preferred Mode: {social.get('modePrefer', 'N/A')}
📝 Bio: {social.get('signature', 'N/A')}

📊 𝗖𝗥𝗘𝗗𝗜𝗧 𝗦𝗖𝗢𝗥𝗘
━━━━━━━━━━━━━━━
💯 Score: {credit.get('creditScore', 'N/A')}
"""

        # Danh sách vũ khí
        weapon_skins = basic.get("weaponSkinShows", [])
        if weapon_skins:
            response_text += "\n\n⚔️ 𝗘𝗤𝗨𝗜𝗣𝗣𝗘𝗗 𝗪𝗘𝗔𝗣𝗢𝗡𝗦\n━━━━━━━━━━━━━━━"
            for idx, weapon_id in enumerate(weapon_skins, 1):
                response_text += f"\n🔫 Weapon {idx}: ID {weapon_id}"

        # Trang phục
        outfits = profile.get("clothes", [])
        if outfits:
            response_text += "\n\n🎭 𝗘𝗤𝗨𝗜𝗣𝗣𝗘𝗗 𝗢𝗨𝗧𝗙𝗜𝗧𝗦\n━━━━━━━━━━━━━━━"
            for idx, cloth_id in enumerate(outfits, 1):
                response_text += f"\n👔 Outfit {idx}: ID {cloth_id}"

        if len(response_text) > 4096:
            for x in range(0, len(response_text), 4096):
                bot.reply_to(message, response_text[x:x+4096])
        else:
            bot.reply_to(message, response_text)

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")
        if "data" in locals():
            bot.reply_to(message, f"Debug info: {json.dumps(data, indent=2)}")



# Webhook nhận update từ Telegram
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok', 200

# Khởi chạy Flask và bot song song
if __name__ == "__main__":
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
    if not WEBHOOK_URL:
        raise Exception("Thiếu biến môi trường WEBHOOK_URL")

    # Xóa webhook cũ và thiết lập webhook mới
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

    # Chạy Flask (webhook listener)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

