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

# Hàm lấy video
import requests
from io import BytesIO

def get_random_video():
    try:
        res = requests.get("https://api.ffcommunity.site/randomvideo.php", timeout=5)
        data = res.json()
        return data.get("url")
    except:
        return None

@bot.message_handler(commands=['video'])
def random_video(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot Chỉ Hoạt Động Trong Nhóm Này.\nLink: https://t.me/HaoEsport01")
        return

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


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot Chỉ Hoạt Động Trong Nhóm Này.\nLink: https://t.me/HaoEsport01")
        return
    name = message.from_user.first_name or "None"

    text = f"""<blockquote>
<b>Xin Chào {name}!</b>

Gõ /about để xem danh sách lệnh của bot mà bạn có thể sử dụng:

<i>(Nếu thấy bot thú vị, đừng ngần ngại chia sẻ với bạn bè để họ cùng dùng nhé!)</i>
</blockquote>"""

    bot.reply_to(message, text, parse_mode="HTML")



from datetime import datetime, timedelta

@bot.message_handler(commands=['about'])
def send_about(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot Chỉ Hoạt Động Trong Nhóm Này.\nLink: https://t.me/HaoEsport01")
        return

    user = message.from_user
    full_name = f"{user.first_name} {user.last_name or ''}".strip()

    bot.reply_to(message, f"""
    Xin Chào Bạn <b>{full_name}</b>
<blockquote>
| Danh Sách Lệnh |
<blockquote>

» /likes - Buff Like
» /visit - Buff View FF
» /video - Random Video Gái
» /anhgai - Random Ảnh Gái
» /thoitiet - Check Thời Tiết
» /rutgon - Rút Gọn Link
» /spam - Spam SDT Thường
» /spamvip - Spam SDT Vip
» /tiktok - Tải Video TikTok
» /ttinfo - Kiểm Tra Tài Khoản TikTok
» /ffinfo - Kiểm Tra Tài Khoản Free Fire
» /checkban - Kiểm Tra Tài Khoản FF Có Bị Band Không
<b>| Contact |</b>
» /admin : Liên Hệ Admin
</blockquote>""", parse_mode="HTML")

API_KEY = '1dcdf9b01ee855ab4b7760d43a10f854'
def anv(city):
    base_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=vi'
    tna = requests.get(base_url)
    nan = tna.json()

    if nan['cod'] == 200:
        weather_info = nan['weather'][0]['description'].capitalize()
        icon = nan['weather'][0]['main']
        temp_info = nan['main']['temp']
        feels_like = nan['main']['feels_like']
        temp_min = nan['main']['temp_min']
        temp_max = nan['main']['temp_max']
        city = nan['name']
        lat = nan['coord']['lat']
        lon = nan['coord']['lon']
        country = nan['sys']['country']
        clouds = nan['clouds']['all']
        humidity = nan['main']['humidity']
        wind_speed = nan['wind']['speed']
        map_link = f"https://www.google.com/maps/place/{lat},{lon}"

        return f"""
<b>Thời tiết tại {city}, {country}:</b>

🌐 <b>Thành phố:</b> {city}
🔗 <b>Bản đồ:</b> <a href="{map_link}">Xem trên Google Maps</a>
🌤️ <b>Tình trạng:</b> {weather_info} ({icon})
🌡️ <b>Nhiệt độ:</b> {temp_info}°C (cảm nhận: {feels_like}°C)
⬆️ <b>Tối đa:</b> {temp_max}°C | ⬇️ <b>Tối thiểu:</b> {temp_min}°C
💧 <b>Độ ẩm:</b> {humidity}%
☁️ <b>Mây bao phủ:</b> {clouds}%
💨 <b>Gió:</b> {wind_speed} m/s
"""
    else:
        return '<b>Không tìm thấy thông tin thời tiết cho địa điểm này.</b>'

@bot.message_handler(commands=['thoitiet'])
def thoitiet(message):
    parts = message.text.split()
    if len(parts) == 1:
        bot.reply_to(message, 'Nhập đúng định dạng:\n/thoitiet [Tên tỉnh thành]')
        return
    city = ' '.join(parts[1:])
    try:
        result = anv(city)
        bot.reply_to(message, result, parse_mode='HTML', disable_web_page_preview=False)
    except Exception as e:
        bot.reply_to(message, f'<b>Lỗi:</b> {str(e)}', parse_mode='HTML')



@bot.message_handler(commands=['checkban'])
def checkban_user(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Vui lòng nhập UID. Ví dụ: /checkban 12345678")
        return

    uid = args[1]
    url = f"https://check-band-p.vercel.app/certainly-region/ban-info?uid={uid}"

    try:
        # Gửi tin nhắn đang xử lý
        sent = bot.reply_to(message, "⏳ Đang kiểm tra UID...")

        response = requests.get(url)
        data = response.json()

        nickname = data.get('nickname', 'Không có dữ liệu')
        region = data.get('region', 'Không xác định')
        ban_status = data.get('ban_status', 'Không rõ')
        ban_period = data.get('ban_period')
        copyright_ = data.get('copyright')

        reply = (
            "<blockquote>"
            f"👤 <b>Thông tin người chơi:</b>\n"
            f"• 🆔 Nickname: <code>{nickname}</code>\n"
            f"• 🌎 Khu vực: <code>{region}</code>\n"
            f"• 🚫 Trạng thái ban: <code>{ban_status}</code>\n"
            f"• ⏳ Thời gian ban: <code>{ban_period if ban_period else 'Không bị ban'}</code>\n"
            f"• ©️ Bản quyền: <code>{copyright_}</code>"
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




import time
import os
import subprocess
import tempfile

last_usage = {}
blacklist = ["112", "113", "114", "115", "116", "117", "118", "119", "0", "1", "2", "3", "4"]
bot_active = True
admin_mode = False
admins = [7658079324]  # ID admin
name_bot = "Bot Hào Vip"

def get_nha_mang(sdt):
    if sdt.startswith("086") or sdt.startswith("096") or sdt.startswith("097") or sdt.startswith("098") or sdt.startswith("032") or sdt.startswith("033") or sdt.startswith("034") or sdt.startswith("035") or sdt.startswith("036") or sdt.startswith("037") or sdt.startswith("038") or sdt.startswith("039"):
        return "Viettel"
    elif sdt.startswith("089") or sdt.startswith("090") or sdt.startswith("093") or sdt.startswith("070") or sdt.startswith("079") or sdt.startswith("077") or sdt.startswith("076") or sdt.startswith("078"):
        return "Mobifone"
    elif sdt.startswith("088") or sdt.startswith("091") or sdt.startswith("094") or sdt.startswith("083") or sdt.startswith("084") or sdt.startswith("085") or sdt.startswith("081") or sdt.startswith("082"):
        return "Vinaphone"
    elif sdt.startswith("092") or sdt.startswith("056") or sdt.startswith("058"):
        return "Vietnamobile"
    elif sdt.startswith("099") or sdt.startswith("059"):
        return "Gmobile"
    else:
        return "Không xác định"


@bot.message_handler(commands=['spam'])
def spam(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/HaoEsport01")
        return
    user_id = message.from_user.id
    current_time = time.time()

    if not bot_active:
        msg = bot.reply_to(message, 'Bot hiện đang tắt.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return

    if admin_mode and user_id not in admins:
        msg = bot.reply_to(message, 'Có lẽ admin đang fix gì đó, hãy đợi xíu.')
        return

    if user_id in last_usage and current_time - last_usage[user_id] < 150:
        remaining = 150 - (current_time - last_usage[user_id])
        bot.reply_to(message, f"Vui lòng đợi {remaining:.1f} giây trước khi sử dụng lệnh lại.")
        return

    last_usage[user_id] = current_time

    params = message.text.split()[1:]
    if len(params) != 2:
        bot.reply_to(message, 
            "<blockquote>» SAI ĐỊNH DẠNG!!!\n\n"
            "» Vui Lòng Nhập Đúng Định Dạng Bên Dưới\n\n"
            "» /spam + SĐT + SỐ_LẦN\n"
            "» VD: /spam 0987654321 10</blockquote>",
            parse_mode="HTML"
        )
        return

    sdt, count = params
    if not count.isdigit():
        bot.reply_to(message, "Số lần spam không hợp lệ. Vui lòng chỉ nhập số.")
        return

    count = int(count)
    if count > 40:
        bot.reply_to(message, "/spam sdt số_lần tối đa là 40 - đợi 150 giây để sử dụng lại.")
        return

    if sdt in blacklist:
        bot.reply_to(message, f"Số điện thoại {sdt} đã bị cấm spam.")
        return

    # Gửi icon loading đồng hồ
    loading_msg = bot.send_message(message.chat.id, "⏳")
    nha_mang = get_nha_mang(sdt)

    diggory_chat3 = f'''
┌──⭓ {name_bot}
» Spam: Thành Công
» Số Lần Spam Free: {count}
» Đang Tấn Công: {sdt}
» Nhà Mạng: {nha_mang}
» Spam 5 Lần Tầm 1-2p mới xong
» Hạn Chế Spam Nhé!
└──
'''


    script_filename = "dec.py"
    try:
        if not os.path.isfile(script_filename):
            bot.reply_to(message, "Không tìm thấy file script. Vui lòng kiểm tra lại.")
            return

        with open(script_filename, 'r', encoding='utf-8') as file:
            script_content = file.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(script_content.encode('utf-8'))
            temp_file_path = temp_file.name

        # Thực thi script
        subprocess.Popen(
            ["python", temp_file_path, sdt, str(count)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Xoá đồng hồ, gửi kết quả
        try:
            bot.delete_message(message.chat.id, loading_msg.message_id)
        except Exception as e:
            print(f"Lỗi khi xóa loading_msg: {e}")

        # Gửi tin nhắn kết quả
        bot.send_message(
            message.chat.id,
            f'<blockquote>{diggory_chat3}</blockquote>',
            parse_mode='HTML'
        )


    except Exception as e:
        bot.reply_to(message, f"Lỗi xảy ra: {str(e)}")



def fetch_tiktok_data(url):
    api_url = f'https://scaninfo.vn/api/down/tiktok.php?url={url}'
    try:
        response = requests.get(api_url)
        response.raise_for_status()  
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching TikTok data: {e}")
        return None

@bot.message_handler(commands=['tiktok'])
def tiktok_command(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/HaoEsport01")
        return
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2:
        url = command_parts[1].strip()
        data = fetch_tiktok_data(url)
        
        if data and 'code' in data and data['code'] == 0:
            video_title = data['data'].get('title', 'N/A')
            video_url = data['data'].get('play', 'N/A')
            music_title = data['data']['music_info'].get('title', 'N/A')
            music_url = data['data']['music_info'].get('play', 'N/A')
            
            reply_message = f"Tiêu đề Video: {video_title}\nĐường dẫn Video: {video_url}\n\nTiêu đề Nhạc: {music_title}\nĐường dẫn Nhạc: {music_url}"
            bot.reply_to(message, reply_message)
        else:
            bot.reply_to(message, "Không thể lấy dữ liệu từ TikTok.")
    else:
        bot.reply_to(message, "Hãy cung cấp một đường dẫn TikTok hợp lệ.")


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
            threading.Thread(target=delete_all_messages_after_delay, args=(message.chat.id, 60)).start()
        else:
            bot.reply_to(message, "Không tìm thấy ảnh từ API.")
    except Exception as e:
        # Xóa thông báo "Đang tìm kiếm ảnh..." nếu có lỗi xảy ra
        try:
            bot.delete_message(searching_message.chat.id, searching_message.message_id)
        except telebot.apihelper.ApiTelegramException:
            pass  # Bỏ qua lỗi nếu đã xóa
        bot.reply_to(message, f"Có lỗi xảy ra: {str(e)}")





@bot.message_handler(commands=['ttinfo'])
def tt_info(message):
    # Chặn ngoài nhóm
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/HaoEsport01")
        return

    try:
        args = message.text.split()
        if len(args) < 2:
            return bot.reply_to(message, "Vui lòng nhập username TikTok.\nVí dụ: /tiktokinfo bacgau1989")

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

import time
import requests
from telebot.types import Message

user_last_like_time = {}

@bot.message_handler(commands=['likes'])
def like_handler(message: Message):
    user_id = message.from_user.id
    current_time = time.time()

    try:
        bot.send_chat_action(message.chat.id, "typing")
    except Exception as e:
        print(f"Bot không thể gửi hành động typing: {e}")
        return

    # Lấy thời gian hiện tại theo ngày (chỉ so sánh ngày)
    current_day = time.strftime("%Y-%m-%d", time.gmtime(current_time))
    last_time = user_last_like_time.get(user_id, None)

    # Kiểm tra nếu người dùng đã thực hiện lệnh trong ngày hôm nay
    if last_time and last_time == current_day:
        bot.reply_to(message, "<blockquote>⏳ Bạn chỉ có thể sử dụng lệnh này một lần mỗi ngày.</blockquote>", parse_mode="HTML")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "<blockquote>Cú pháp đúng: /like UID</blockquote>", parse_mode="HTML")
        return

    uid = parts[1]
    api_url = f"https://likes-freefire.vercel.app/likes?uid={uid}&region=sg&key=GoodKey"

    try:
        loading_msg = bot.reply_to(message, "<blockquote>⏳ Đang tiến hành buff like...</blockquote>", parse_mode="HTML")
    except Exception as e:
        print(f"Lỗi gửi tin nhắn loading: {e}")
        return

    def safe_get(data, key):
        value = data.get(key)
        return str(value) if value not in [None, "", "null"] else "Không xác định"

    def extract_number(text):
        if isinstance(text, int):
            return str(text)
        for part in str(text).split():
            if part.isdigit():
                return part
        return "Không xác định"

    try:
        response = requests.get(api_url, timeout=15)
        data = response.json()
    except Exception as e:
        bot.edit_message_text(
            "<blockquote>Lỗi kết nối đến API. Vui lòng thử lại sau.</blockquote>",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            parse_mode="HTML"
        )
        return

    if not data or data.get("status") != 1:
        bot.edit_message_text(
            "<blockquote>Server đang bảo trì hoặc quá tải, vui lòng thử lại sau.</blockquote>",
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            parse_mode="HTML"
        )
        return

    # Lưu lại ngày người dùng thực hiện lệnh
    user_last_like_time[user_id] = current_day

    status_code = data.get("status")
    reply_text = (
        "<blockquote>"
        "BUFF LIKE THÀNH CÔNG✅\n"
        f"╭👤 Name: {safe_get(data, 'PlayerNickname')}\n"
        f"├🆔 UID : {safe_get(data, 'UID')}\n"
        f"├🌏 Region : vn\n"
        f"├📉 Like trước đó: {safe_get(data, 'LikesbeforeCommand')}\n"
        f"├📈 Like sau khi gửi: {safe_get(data, 'LikesafterCommand')}\n"
        f"╰👍 Like được gửi: {extract_number(data.get('LikesGivenByAPI'))}"
    )

    if data.get("status") == 2:
        reply_text += "\n⚠️ Giới hạn like hôm nay, mai hãy thử lại sau."

    reply_text += "</blockquote>"

    try:
        bot.edit_message_text(
            reply_text,
            chat_id=loading_msg.chat.id,
            message_id=loading_msg.message_id,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Lỗi gửi kết quả: {e}")





@bot.message_handler(commands=['ffinfo'])
def ffinfo_command(message):
    # Kiểm tra xem lệnh có được dùng trong nhóm cho phép không
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot chỉ hoạt động trong nhóm này.\nLink: https://t.me/HaoEsport01")
        return

    try:
        args = message.text.split()
        if len(args) < 2:
            return bot.reply_to(message, "Vui lòng nhập UID.\nVí dụ: /ffinfo 3827953808")

        uid = args[1]
        url = f"https://aditya-info.onrender.com/player-info?uid={uid}&region=vn"
        r = requests.get(url)
        data = r.json()

        # Không còn data["status"], nên kiểm tra khác
        if not data.get("basicInfo"):
            return bot.reply_to(message, "Không tìm thấy người chơi!")

        basic_info = data["basicInfo"]
        clan_info = data.get("clanBasicInfo")
        social_info = data.get("socialInfo")

        nickname = basic_info.get("nickname", "Không có")
        account_id = basic_info.get("accountId", "Không có")
        level = basic_info.get("level", "Không có")
        likes = basic_info.get("liked", "Không có")
        region = basic_info.get("region", "Không có")
        bio = social_info.get("signature", "Không có") if social_info else "Không có"

        if clan_info:
            clan_name = clan_info.get("clanName", "Không có")
            clan_members = clan_info.get("memberNum", "Không có")
        else:
            clan_name = "Không có"
            clan_members = "Không có"

        msg = f"""
<blockquote>
<b>Thông tin người chơi:</b>
• Tên: <code>{nickname}</code>
• UID: <code>{account_id}</code>
• Level: <b>{level}</b>
• Likes: <b>{likes}</b>
• Server: <code>{region}</code>
• Bio: <i>{bio}</i>

<b>Guild:</b>
• Tên: <code>{clan_name}</code>
• Thành viên: <b>{clan_members}</b>
</blockquote>
        """

        # Gửi tin nhắn thông tin
        bot.reply_to(message, msg, parse_mode="HTML")

        # Gửi thêm ảnh banner
        banner_url = f"https://aditya-banner.onrender.com/banner-image?uid={uid}&region=vn"
        bot.send_photo(message.chat.id, banner_url)

    except Exception as e:
        bot.reply_to(message, f"<b>Lỗi:</b> <code>{e}</code>", parse_mode="HTML")



import requests

@bot.message_handler(commands=['rutgon'])
def shorten_link(message):
    if message.chat.id not in ALLOWED_GROUP_IDS:
        bot.reply_to(message, "Bot Chỉ Hoạt Động Trong Nhóm Này.\nLink: https://t.me/HaoEsport01")
        return

    
    

    args = message.text.split(" ", 1)
    if len(args) == 1:
        bot.reply_to(message, "Vui lòng nhập link cần rút gọn.\nVí dụ: <code>/rutgon https://example.com</code>", parse_mode="HTML")
        return

    long_url = args[1]

    try:
        api_url = f"http://tinyurl.com/api-create.php?url={long_url}"
        response = requests.get(api_url)

        if response.status_code == 200:
            short_url = response.text
            reply_text = f"""<blockquote>
🔗 <b>Link Đã Được Rút Gọn:</b>
<code>{short_url}</code>
</blockquote>"""
            bot.reply_to(message, reply_text, parse_mode="HTML")
        else:
            bot.reply_to(message, "Rút gọn thất bại. Vui lòng thử lại sau.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi khi rút gọn link: {e}")











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
