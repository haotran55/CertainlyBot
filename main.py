import requests
import time
import threading
from telebot import TeleBot
from flask import Flask
from datetime import datetime
from keep_alive import keep_alive
keep_alive()
BOT_TOKEN = os.environ.get('BOT_TOKEN')  # <- thêm dòng này
bot = telebot.TeleBot(BOT_TOKEN)         # <- bot dùng biến này

print(BOT_TOKEN)

# ID nhóm được phép sử dụng bot
ALLOWED_GROUP_ID = -1002639856138
GROUP_LINK = "https://t.me/HaoEsport01"  # Link nhóm

def group_only(func):
    """Chỉ cho phép bot hoạt động trong nhóm cụ thể."""
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
    

@bot.message_handler(commands=['video'])
@group_only
def random_video(message):
    """Lấy video ngẫu nhiên từ API và gửi cho người dùng."""
    try:
        res = requests.get("https://api.ffcommunity.site/randomvideo.php")
        data = res.json()
        video_url = data.get("url")

        if video_url:
            bot.send_chat_action(message.chat.id, "upload_video")
            bot.send_video(message.chat.id, video=video_url, caption="Video gái xinh By @CertainllyBot")
        else:
            bot.send_message(message.chat.id, "Không lấy được video, thử lại sau nhé!")
    except Exception as e:
        bot.send_message(message.chat.id, "Đã xảy ra lỗi khi lấy video.")

@bot.message_handler(content_types=['new_chat_members'])
@group_only
def welcome_new_member(message):
    """Chào người mới tham gia nhóm và gửi video."""
    for new_member in message.new_chat_members:
        uid = new_member.id
        username = new_member.username if new_member.username else "Unknown"
        members_count = bot.get_chat_members_count(message.chat.id)
        current_time = datetime.now().strftime("%H:%M:%S | %d/%m/%Y")
        
        welcome_text = f"""
🧤 Hello {new_member.first_name}
┌ UID: {uid}
├ Username: @{username}
├ Thành Viên: {members_count}
├ Thời Gian: {current_time}
├ Chào Mừng Bạn Đã Tham Gia Nhóm @HaoEsports05
✅ Gõ /bot Để Xem Lệnh Bot Hỗ Trợ Nhé!
"""
        bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

        try:
            res = requests.get("https://api.ffcommunity.site/randomvideo.php")
            data = res.json()
            video_url = data.get("url")

            if video_url:
                bot.send_chat_action(message.chat.id, "upload_video")
                bot.send_video(message.chat.id, video=video_url, caption="Chúc mừng bạn tham gia nhóm! 🎥")
            else:
                bot.send_message(message.chat.id, "Không lấy được video, thử lại sau nhé!")
        except Exception as e:
            bot.send_message(message.chat.id, "Đã xảy ra lỗi khi gửi video.")

import html
@bot.message_handler(commands=['fl'])
def get_tiktok_fl(message):
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "❗ Vui lòng dùng đúng cú pháp:\n<b>/fl &lt;username&gt;</b>", parse_mode="HTML")
            return

        username = args[1]
        url = f"http://145.223.80.56:5009/info_tiktok?username={username}"
        response = requests.get(url)

        if response.status_code != 200:
            bot.reply_to(message, "Không thể tăng Follow từ API.", parse_mode="HTML")
            return

        data = response.json()

        # Escape toàn bộ để an toàn
        name = html.escape(data.get('name', 'Không rõ'))
        followers = f"{data.get('followers', 0):,}"
        blockquote = (
            f" Đã Tăng Follow Thành Công\n\n"
            f" Follow Trước: {followers}\n"
            f" Follow Sau: {followers}\n"
            f" Đã Cộng: 0\n"
            f" Tên: {name}\n"
        )

        caption = f"<blockquote>{blockquote}</blockquote>"

        bot.reply_to(message, caption, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"❗ Đã xảy ra lỗi: {str(e)}", parse_mode="HTML")


if __name__ == "__main__":
    bot_active = True
    bot.polling()  #
