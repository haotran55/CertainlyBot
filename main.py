import requests
import html
import time
from telebot import TeleBot
from flask import Flask
from keep_alive import keep_alive

bot = TeleBot("7379468791:AAFjogvlg3b_isuNyGBUYePw9uQ54-xAjms")

# ID nhóm được phép sử dụng bot
ALLOWED_GROUP_ID = -1002639856138
GROUP_LINK = "https://t.me/HaoEsport01"  # Link nhóm

def group_only(func):
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

# Kiểm tra xem người gửi có phải là admin không
def is_admin(chat_id, user_id):
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except:
        return False

# Mute người dùng trong 10 phút
def mute_user(chat_id, user_id):
    # Mute người dùng
    username = message.from_user.username or "None"
    bot.restrict_chat_member(chat_id, user_id, until_date=time.time() + 600, can_send_messages=False)
    bot.send_message(chat_id, f" Người dùng @{username} đã bị mute trong 10 phút!")

# Hủy mute sau 10 phút
def unmute_user(chat_id, user_id):
    # Hủy mute người dùng
    bot.restrict_chat_member(chat_id, user_id, can_send_messages=True)
    bot.send_message(chat_id, f"✅ Người dùng đã được hủy mute.")

@bot.message_handler(func=lambda message: 't.me' in message.text)
@group_only
def handle_tme_link(message):
    # Kiểm tra nếu người gửi không phải là admin thì xóa tin nhắn và mute
    if not is_admin(message.chat.id, message.from_user.id):
        try:
            # Xóa tin nhắn
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, "Tin nhắn chứa link <code>t.me</code> đã bị xóa!", parse_mode="HTML")

            # Mute người gửi trong 10 phút
            mute_user(message.chat.id, message.from_user.id)

            # Hủy mute sau 10 phút
            time.sleep(600)  # Chờ 10 phút (600 giây)
            unmute_user(message.chat.id, message.from_user.id)

        except Exception as e:
            bot.send_message(message.chat.id, f"❗ Đã xảy ra lỗi: {str(e)}")
    else:
        # Nếu là admin thì không xóa và không mute
        bot.send_message(message.chat.id, "Admin đã gửi tin nhắn chứa <code>t.me</code>!", parse_mode="HTML")

@bot.message_handler(commands=['video'])
@group_only
def random_video(message):
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

# Tạo thread riêng để chạy bot polling
def run_bot():
    bot.infinity_polling()

# Gọi keep_alive() và khởi động bot
keep_alive()
run_bot()  # Sử dụng bot.infinity_polling() trực tiếp
