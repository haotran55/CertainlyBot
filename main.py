import os
import threading
import requests
from telebot import TeleBot
from flask import Flask
from datetime import datetime
from keep_alive import keep_alive
from io import BytesIO

# Giữ Flask sống
keep_alive()

# Lấy token từ biến môi trường
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = TeleBot(BOT_TOKEN)
processes = []
last_spam_time = {}
# ID nhóm được phép sử dụng bot
ALLOWED_GROUP_ID = -1002639856138
GROUP_LINK = "https://t.me/HaoEsport01"

def group_only(func):
    def wrapper(message):
        if message.chat.id == ALLOWED_GROUP_ID:
            return func(message)
        else:
            bot.reply_to(
                message,
                f"❗ Bot chỉ hoạt động trong nhóm này: <a href=\"{GROUP_LINK}\">Tại Đây</a>",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
    return wrapper

#video
# Hàm lấy video từ API
def get_random_video():
    try:
        res = requests.get("https://api.ffcommunity.site/randomvideo.php", timeout=5)
        data = res.json()
        return data.get("url")
    except:
        return None

@bot.message_handler(commands=['video'])
@group_only
def random_video(message):
    video_url = get_random_video()
    if video_url:
        try:
            bot.send_chat_action(message.chat.id, "upload_video")
            bot.send_video(
                message.chat.id,
                video=video_url,
                caption="Video gái xinh By @CertainllyBot"
            )
        except Exception as e:
            bot.send_message(message.chat.id, "Lỗi khi gửi video.")
    else:
        bot.send_message(message.chat.id, "Không lấy được video, thử lại sau nhé!")
#spam
import phonenumbers
from phonenumbers import carrier

def get_network(phone):
    try:
        number = phonenumbers.parse(f"+84{phone[1:]}" if phone.startswith("0") else phone, "VN")
        return carrier.name_for_number(number, "vi") or "Không xác định"
    except:
        return "Không xác định"

@bot.message_handler(commands=['spam'])
def supersms(message):
    user_id = message.from_user.id
    current_time = time.time()
    if user_id in user_last_command_time:
        elapsed_time = current_time - user_last_command_time[user_id]
        if elapsed_time < 100:
            remaining_time = 100 - elapsed_time
            bot.reply_to(message, f"Vui lòng đợi {remaining_time:.1f} giây trước khi sử dụng lệnh lại.")
            return

    params = message.text.split()[1:]
    if len(params) != 2:
        bot.reply_to(message, "/spam sdt số_lần (tối đa 10)")
        return

    sdt, count = params
    if not count.isdigit():
        bot.reply_to(message, "Số lần không hợp lệ. Vui lòng chỉ nhập số.")
        return

    count = int(count)
    if count > 10:
        bot.reply_to(message, "Số lần tối đa là 10.")
        return

    if sdt in blacklist:
        bot.reply_to(message, f"Số điện thoại {sdt} đã bị cấm spam.")
        return

    sdt_request = f"84{sdt[1:]}" if sdt.startswith("0") else sdt
    network = get_network(sdt)

    diggory_chat3 = f'''{name_bot}
╭ Spam: Thành Công 
├ Người dùng: {message.from_user.username}
├ Số Lần Spam: {count}
├ Nhà Mạng: {network}
╰ Đang Tấn Công: {sdt}'''

    try:
        if not os.path.isfile("dec.py"):
            bot.reply_to(message, "Không tìm thấy file script.")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            with open("dec.py", 'r', encoding='utf-8') as file:
                temp_file.write(file.read().encode('utf-8'))
            temp_path = temp_file.name

        subprocess.Popen(["python", temp_path, sdt, str(count)])

        bot.send_message(
            message.chat.id,
            f'<blockquote>{diggory_chat3}</blockquote>\n<blockquote> GÓI DÙNG : FREE</blockquote>',
            parse_mode='HTML'
        )

        requests.get(f'https://dichvukey.site/apivl/call1.php?sdt={sdt_request}')
        user_last_command_time[user_id] = time.time()

    except Exception as e:
        bot.reply_to(message, "Đã xảy ra lỗi khi xử lý yêu cầu.")
        print(e)

        
last_usage = {}
blacklist = ["112", "113", "114", "115", "116", "117", "118", "119", "0", "1", "2", "3", "4", "078901631"]




@bot.message_handler(content_types=['new_chat_members'])
def welcome_user(message):
    for user in message.new_chat_members:
        uid = user.id
        username = f"@{user.username}" if user.username else "Không có"
        full_name = f"{user.first_name} {user.last_name or ''}".strip()
        time_joined = datetime.now().strftime("%H:%M:%S | %d/%m/%Y")

        video_url = get_random_video()
        if not video_url:
            bot.send_message(message.chat.id, f"Chào mừng {full_name} nhé! (Không lấy được video)")
            return

        try:
            video_resp = requests.get(video_url)
            video_file = BytesIO(video_resp.content)
            video_file.name = "https://i.imgur.com/YV2Wzoq.mp4"

            caption = f"""🖐 Hello <b>{full_name}</b>
├ UID: <code>{uid}</code>
├ Username: {username}
├ Thời Gian: <code>{time_joined}</code>
└ <i>Chào Mừng Bạn Đã Tham Gia Nhóm <b>Box Hào Esports</b></i>
Gõ /bot Để Xem Lệnh Bot Hỗ Trợ Nhé!"""

            bot.send_video(
                chat_id=message.chat.id,
                video=video_file,
                caption=caption,
                parse_mode="HTML"
            )
        except:
            bot.send_message(message.chat.id, f"Chào mừng {full_name} nhé! (Gửi video lỗi)")

# Flask Server cho Render / UptimeRobot
def run_flask():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return "Bot đang hoạt động trên Render!"

    app.run(host="0.0.0.0", port=8080)

# Thread cho Flask
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Thread cho bot Telegram
def run_bot():
    bot.polling(non_stop=True)

bot_thread = threading.Thread(target=run_bot)
bot_thread.start()
