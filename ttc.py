import telebot
from telebot.types import ChatPermissions
from datetime import datetime, timedelta

TOKEN = "7954514943:AAEzy-Usoav6spR4CCdSlOZs4iHMpzySdFY"
bot = telebot.TeleBot(TOKEN)

ADMINS = [7606197696, 7658079324]  # ID admin thật của bạn

@bot.message_handler(commands=['kick'])
def kick(message):
    if message.from_user.id not in ADMINS:
        bot.reply_to(message, "Bạn không có quyền dùng lệnh này!")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "Hãy reply tin nhắn của người muốn kick.")
        return

    user_id = message.reply_to_message.from_user.id
    try:
        bot.kick_chat_member(message.chat.id, user_id)
        bot.reply_to(message, f"Đã kick user {user_id}")
    except Exception as e:
        bot.reply_to(message, f"Lỗi khi kick: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot đã sẵn sàng!")

print("Bot đang chạy...")
bot.infinity_polling()
