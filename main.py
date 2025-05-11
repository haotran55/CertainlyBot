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



#video

def get_random_video():
    try:
        res = requests.get("https://api.ffcommunity.site/randomvideo.php", timeout=5)
        data = res.json()
        return data.get("url")
    except:
        return None

@bot.message_handler(commands=['video'])
def random_video(message):
 

    video_url = get_random_video()
    if video_url:
        try:
            bot.send_chat_action(message.chat.id, "upload_video")
            res = requests.get(video_url, stream=True, timeout=10)
            if res.status_code == 200:
                video_file = BytesIO(res.content)
                video_file.name = "video.mp4"
                bot.send_video(message.chat.id, video=video_file, caption="Video gái xinh By @BotHaoVip_bot")
            else:
                bot.send_message(message.chat.id, "Không thể tải video từ nguồn.")
        except Exception as e:
            print("Lỗi gửi video:", e)
            bot.send_message(message.chat.id, "Lỗi khi gửi video.")
    else:
        bot.send_message(message.chat.id, "Không lấy được video, thử lại sau nhé!")

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


#lệnh

@bot.message_handler(commands=['bot'])
def send_help(message):
    bot.reply_to(message, """<blockquote>
╔════════════════╗  
    📌 *DANH SÁCH LỆNH*
╚════════════════╝  
/start - Bắt đầu  
/help - Trợ giúp  
/info - Check info Telegram
/report - Báo cáo cho Admin  
/id - Lấy ID Tele Của User/Group  
/tv - Đổi Tiếng Việt Trên Tele  
/ask + [tin nhắn] - Hỏi đáp free  
/tt + [username/link TikTok] - Kiểm tra thông tin tài khoản TikTok  
/thoitiet + [thành phố] - Xem tình hình thời tiết  
/visit + [region] + [uid] - Tăng Lượt View Free Fire
/addfr + [uid] - Spam Kết Bạn Free Fire (VN)
/spam + [uid] - Spam Kết Bạn Free Fire (IND)
/xucxac - Lắc xúc xắc ngẫu nhiên
/doaniq - Bot đo chỉ số IQ hài hước của bạn
/share - Buff share bài viết Facebook
/tym + [url] - Tăng Tim TikTok
/fl + [username] - Tăng Follow TikTok
/tiktok + [url] - Tải Video TikTok
/like + [region] + [uid] - Buff Like Free Fire
/thinh - Gửi 1 câu thả thính  
/joker - Gửi 1 câu đùa  
/meme - Gửi một câu meme hài hước random
/time - Xem thời gian hiện tại
/get + [region] + [uid] - Check Info Free Fire
/taoanh - Tạo ảnh bằng AI (VN)  
/image - Tạo ảnh bằng AI (ENG)  
/qr - Tạo mã QR từ văn bản / Tạo QR thanh toán  
/quotes - Gửi một câu danh ngôn truyền cảm hứng
/loikhuyen - Gửi một lời khuyên tích cực ngẫu nhiên
/idfb - Lấy ID Từ Link Hoặc Username Facebook
/choose - Chọn ngẫu nhiên giữa hai lựa chọn  
/uptime – Xem thời gian bot đã hoạt động
/ping – Kiểm tra bot có hoạt động không
/doannhau + [số người] - Ước lượng thiệt hại sau một trận quất sập bàn!
/rutgon + [url] - Tạo link rút gọn TinyURL  
/voice + [văn bản] - Tạo voice từ văn bản  
/bot + [tin nhắn] - Bot auto reply  
/dich + [văn bản] - Dịch tất cả ngôn ngữ thành tiếng việt  
/date + [d/m/Y] - Đã bao nhiêu ngày kể từ ngày  
</blockquote>""", parse_mode='HTML')


@bot.message_handler(commands=['voice'])
def text_to_voice(message):
    text = message.text[7:].strip()  
  
    
    if not text:
        bot.reply_to(message, ' Vui Lòng Nhập nội dung')
        return

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts = gTTS(text, lang='vi')
            tts.save(temp_file.name)
            temp_file_path = temp_file.name  
       
        with open(temp_file_path, 'rb') as f:
            bot.send_voice(message.chat.id, f, reply_to_message_id=message.message_id)
    
    except Exception as e:
        bot.reply_to(message, f'Đã xảy ra lỗi: {e}')
    
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

            

@bot.message_handler(commands=['id', 'ID'])
def handle_id_command(message):
    if message.reply_to_message:  
        user_id = message.reply_to_message.from_user.id
        first_name = message.reply_to_message.from_user.first_name
        bot.reply_to(message, f"ID của {first_name} là: `{user_id}`", parse_mode='Markdown')
    elif len(message.text.split()) == 1:
        if message.chat.type in ["group", "supergroup"]:
            chat_id = message.chat.id
            chat_title = message.chat.title
            bot.reply_to(message, f"ID của nhóm này là: `{chat_id}`\nTên nhóm: {chat_title}", parse_mode='Markdown')
        else:
            user_id = message.from_user.id
            first_name = message.from_user.first_name
            bot.reply_to(message, f"ID của bạn là: `{user_id}`\nTên: {first_name}", parse_mode='Markdown')

@bot.message_handler(commands=['idnhom'])
def handle_id_command(message):
    if message.reply_to_message:  
        user_id = message.reply_to_message.from_user.id
        first_name = message.reply_to_message.from_user.first_name
        bot.reply_to(message, f"ID của {first_name} là: `{user_id}`", parse_mode='Markdown')
    elif len(message.text.split()) == 1:
        if message.chat.type in ["group", "supergroup"]:
            chat_id = message.chat.id
            chat_title = message.chat.title
            bot.reply_to(message, f"ID của nhóm này là: `{chat_id}`\nTên nhóm: {chat_title}", parse_mode='Markdown')
        else:
            user_id = message.from_user.id
            first_name = message.from_user.first_name
            bot.reply_to(message, f"ID của bạn là: `{user_id}`\nTên: {first_name}", parse_mode='Markdown')
   

@bot.message_handler(commands=['tv'])
def tieng_viet(message):
    chat_id = message.chat.id
    message_id = message.message_id
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton("Tiếng Việt 🇻🇳", url='https://t.me/setlanguage/abcxyz')
    keyboard.add(url_button)
    bot.send_message(chat_id, 'Click vào nút "<b>Tiếng Việt</b>" để đổi thành ngôn ngữ Việt Nam.', reply_markup=keyboard, parse_mode='HTML')

sent_messages = []

def delete_all_messages_after_delay(chat_id, delay):
    threading.Event().wait(delay)
    for msg_id in sent_messages:
        try:
            bot.delete_message(chat_id, msg_id)
        except telebot.apihelper.ApiTelegramException:
            pass  # Bỏ qua lỗi nếu tin nhắn đã bị xóa
    sent_messages.clear()

@bot.message_handler(commands=['anhgai'])
def send_anhgai_image(message):
    api_url = "https://subhatde.id.vn/images/gai"

    # Gửi thông báo "Đang tìm kiếm ảnh..."
    searching_message = bot.reply_to(message, "🔎 Đang tìm kiếm ảnh...")
    sent_messages.append(searching_message.message_id)  # Lưu ID tin nhắn

    try:
        # Lấy dữ liệu ảnh từ API
        response = requests.get(api_url)
        data = response.json()

        # Xóa thông báo "Đang tìm kiếm ảnh..." sau khi nhận phản hồi
        try:
            bot.delete_message(searching_message.chat.id, searching_message.message_id)
        except telebot.apihelper.ApiTelegramException:
            pass  # Bỏ qua lỗi nếu đã xóa

        # Kiểm tra xem phản hồi có trường 'url' không
        if 'url' in data:
            image_url = data['url']

            # Gửi ảnh cho người dùng với chú thích
            caption_text = f"Ảnh Mà Bạn Yêu Cầu, @{message.from_user.username}"
            sent_message = bot.send_photo(message.chat.id, image_url, caption=caption_text)
            sent_messages.append(sent_message.message_id)  # Lưu ID tin nhắn

            # Tạo luồng để xóa tất cả tin nhắn sau 60 giây
            threading.Thread(target=delete_all_messages_after_delay, args=(message.chat.id, 200)).start()
        else:
            bot.reply_to(message, "Không tìm thấy ảnh từ API.")
    except Exception as e:
        # Xóa thông báo "Đang tìm kiếm ảnh..." nếu có lỗi xảy ra
        try:
            bot.delete_message(searching_message.chat.id, searching_message.message_id)
        except telebot.apihelper.ApiTelegramException:
            pass  # Bỏ qua lỗi nếu đã xóa
        bot.reply_to(message, f"Có lỗi xảy ra: {str(e)}")


def fetch_tiktok_data(url):
    api_url = f'https://www.tikwm.com/api?url={url}'
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching TikTok data: {e}")
        return None

@bot.message_handler(func=lambda message: message.text.lower().startswith("taivideotiktok"))
def tiktokvideo_command(message):
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2:
        url = command_parts[1].strip()
        data = fetch_tiktok_data(url)

        if data and data.get('code') == 0:
            video_title = data['data'].get('title', 'Không rõ tiêu đề')
            video_url = data['data'].get('play', 'Không có link')
            music_title = data['data']['music_info'].get('title', 'Không rõ nhạc')
            music_url = data['data']['music_info'].get('play', 'Không có link')

            reply_message = f'''Tiêu đề Video: {video_title}
╭────────────────╮
📹 Video: <a href="{video_url}">TẠI ĐÂY</a>
╰────────────────╯
🎵 Nhạc nền: {music_title}
🔗 Link Nhạc: <a href="{music_url}">Nghe tại đây</a>'''

            bot.reply_to(message, reply_message, parse_mode='HTML')
        else:
            bot.reply_to(message, "⚠️ Không thể lấy dữ liệu từ TikTok. Vui lòng kiểm tra lại link.")
    else:
        bot.reply_to(message, "⚠️ Bạn cần nhập link TikTok sau lệnh. Ví dụ:\n`taivideotiktok https://www.tiktok.com/...`", parse_mode='Markdown')


@bot.message_handler(commands=['like'])
def like_handler(message: Message):
    command_parts = message.text.split()  
    if len(command_parts) != 2:  
        bot.reply_to(message, "<blockquote>like 8324665667</blockquote>", parse_mode="HTML")  
        return  

    idgame = command_parts[1]  
    urllike = f"linkapi?uid={idgame}"  

    def safe_get(data, key):
        value = data.get(key)
        return value if value not in [None, ""] else "Không xác định"

    # Gửi request
    try:
        response = requests.get(urllike, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        bot.reply_to(message, "<blockquote>Server đang quá tải, vui lòng thử lại sau.</blockquote>", parse_mode="HTML")
        return
    except ValueError:
        bot.reply_to(message, "<blockquote>Phản hồi từ server không hợp lệ.</blockquote>", parse_mode="HTML")
        return
    status_code = data.get("status")
    reply_text = (
        f"<blockquote>\n"
        f"<b>Player Nickname:</b> {safe_get(data, 'username')}\n"
        f"<b>Player UID:</b> {safe_get(data, 'uid')}\n"
        f"<b>Player Level:</b> {safe_get(data, 'level')}\n"
        f"<b>Likes before Command:</b> {safe_get(data, 'likes_before')}\n"
        f"✅ <b>Likes after Command:</b> {safe_get(data, 'likes_after')}\n"
        f"➕ <b> Likes given:</b> {safe_get(data, 'likes_given')} like"
    )

    if status_code == 2:
        reply_text += "\n\n⚠️ <i> Player has reached max likes today!.</i>"

    reply_text += "\n</blockquote>"
    bot.reply_to(message, reply_text, parse_mode="HTML")




    #
    #like
    
def unban_chat(chat_id, user_id):
    bot.restrict_chat_member(chat_id, user_id, can_send_messages=True)

@bot.message_handler(commands=["ban"])
def ban_user(message):
    if message.from_user.id != ADMIN_ID:
        return  

    try:
        _, user_id, hours = message.text.split()
        user_id, hours = int(user_id), int(hours)

        bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=False)
        bot.reply_to(message, f"Đã cấm chat {user_id} trong {hours} giờ.")

        threading.Timer(hours * 3600, unban_chat, args=(message.chat.id, user_id)).start()

    except:
        bot.reply_to(message, "Sai")



@bot.message_handler(commands=['tiktok'])
def tt_info(message):
  

    try:
        args = message.text.split()
        if len(args) < 2:
            return bot.reply_to(message, "Vui lòng nhập username TikTok.\nVí dụ: /tiktok bacgau1989")

        username = args[1]
        url = f"http://145.223.80.56:5009/info_tiktok?username={username}"
        r = requests.get(url)
        data = r.json()

        if not data or "username" not in data:
            return bot.reply_to(message, "Không tìm thấy người dùng TikTok!")

        # Dữ liệu người dùng
        name = data.get("name", "Không rõ")
        user = data["username"]
        bio = data.get("signature", "Không có")
        followers = f"{data.get('followers', 0):,}"
        following = f"{data.get('following', 0):,}"
        hearts = f"{data.get('hearts', 0):,}"
        videos = f"{data.get('videos', 0):,}"
        pfp = data.get("profile_picture")

        # Tin nhắn trả về
        msg = f"""
<blockquote>
<b>Thông tin TikTok:</b>
• Tên: <code>{name}</code>
• Username: <code>@{user}</code>
• Followers: <b>{followers}</b>
• Following: <b>{following}</b>
• Likes: <b>{hearts}</b>
• Videos: <b>{videos}</b>
• Bio: <i>{bio}</i>
</blockquote>
        """

        # Gửi ảnh + info
        bot.send_photo(message.chat.id, pfp, caption=msg, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"<b>Lỗi:</b> <code>{e}</code>", parse_mode="HTML")

@bot.message_handler(commands=['checkban'])
def checkban_user(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Vui lòng nhập UID. Ví dụ: /checkban 12345678")
        return

    uid = args[1]
    url = f"https://check-band-p-3uv9.vercel.app/haoesports-region/ban-info?uid={uid}"

    try:
        # Gửi tin nhắn đang xử lý
        sent = bot.reply_to(message, "⏳ Đang kiểm tra UID...")

        response = requests.get(url)
        data = response.json()

        nickname = data.get('nickname', 'Không có dữ liệu')
        uid = data.get('uid', 'Không Có Uid')
        region = data.get('region', 'Không xác định')
        ban_status = data.get('ban_status', 'Không rõ')
        ban_period = data.get('ban_period')

        reply = (
            "<blockquote>"
            f"✅ <b>Thông tin người chơi:</b>\n"
            f"• 👤 Nickname: <code>{nickname}</code>\n"
            f"• 🆔 ID: <code>{uid}</code>\n"
            f"• 🌎 Khu vực: <code>{region}</code>\n"
            f"• 🚫 Trạng thái ban: <code>{ban_status}</code>\n"
            f"• ⏳ Thời gian ban: <code>{ban_period if ban_period else 'Không bị ban'}</code>"
            "</blockquote>"
        )

        bot.edit_message_text(
            chat_id=sent.chat.id,
            message_id=sent.message_id,
            text=reply,
            parse_mode='HTML'
        )

    except Exception as e:
        bot.edit_message_text(
            chat_id=sent.chat.id,
            message_id=sent.message_id,
            text=f"Đã xảy ra lỗi: {e}"
        )

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
