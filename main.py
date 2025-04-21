import requests
import time
import threading
from telebot import TeleBot
from flask import Flask
from keep_alive import keep_alive
from datetime import datetime

bot = TeleBot("7379468791:AAFjogvlg3b_isuNyGBUYePw9uQ54-xAjms")

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
                f"❗ Bot chỉ hoạt động trong nhóm này: <a href=\"{GROUP_LINK}\">Box Chat</a>",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
    return wrapper

def is_admin(chat_id, user_id):
    """Kiểm tra xem người gửi có phải là admin không."""
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except:
        return False

def mute_user(chat_id, user_id):
    """Mute người dùng trong 10 phút."""
    user = bot.get_chat_member(chat_id, user_id).user
    username = user.username or user.first_name or "Unknown"
    bot.restrict_chat_member(chat_id, user_id, until_date=time.time() + 600, can_send_messages=False)
    bot.send_message(chat_id, f"Người dùng @{username} đã bị mute trong 10 phút!")

def unmute_user(chat_id, user_id):
    """Hủy mute người dùng."""
    user = bot.get_chat_member(chat_id, user_id).user
    username = user.username or user.first_name or "Người dùng"
    bot.restrict_chat_member(chat_id, user_id, can_send_messages=True)
    bot.send_message(chat_id, f"✅ Người dùng @{username} đã được hủy mute.")

def schedule_unmute(chat_id, user_id, delay=600):
    """Hẹn giờ unmute không làm treo bot."""
    threading.Timer(delay, lambda: unmute_user(chat_id, user_id)).start()

@bot.message_handler(func=lambda message: 't.me' in message.text)
@group_only
def handle_tme_link(message):
    """Xử lý link 't.me' trong nhóm."""
    if not is_admin(message.chat.id, message.from_user.id):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, "Tin nhắn chứa link <code>t.me</code> đã bị xóa!", parse_mode="HTML")
            mute_user(message.chat.id, message.from_user.id)
            schedule_unmute(message.chat.id, message.from_user.id)
        except Exception as e:
            bot.send_message(message.chat.id, f"❗ Đã xảy ra lỗi: {str(e)}")
    else:
        bot.send_message(message.chat.id, "Admin đã gửi tin nhắn chứa <code>t.me</code>!", parse_mode="HTML")

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

if __name__ == "__main__":
    bot_active = True
    bot.polling()  #
