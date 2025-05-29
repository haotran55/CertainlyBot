import telebot
from telebot.types import ChatPermissions
from datetime import datetime, timedelta

TOKEN = "7954514943:AAEzy-Usoav6spR4CCdSlOZs4iHMpzySdFY"
ADMINS = [7606197696, 7658079324]

bot = telebot.TeleBot(TOKEN)

def is_admin(user_id):
    return user_id in ADMINS

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot đã khởi động và sẵn sàng!")

@bot.message_handler(commands=['kick'])
def kick(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này!")
        return

    target_id = None
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    else:
        args = message.text.split()
        if len(args) >= 2:
            try:
                target_id = int(args[1])
            except:
                bot.reply_to(message, "❌ ID user không hợp lệ.")
                return
        else:
            bot.reply_to(message, "Dùng: /kick <user_id> hoặc reply vào tin nhắn.")
            return

    try:
        bot.kick_chat_member(message.chat.id, target_id)
        bot.reply_to(message, f"✅ Đã kick user {target_id}")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi kick: {e}")

@bot.message_handler(commands=['mute'])
def mute(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này!")
        return

    target_id = None
    duration = 5

    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        args = message.text.split()
        if len(args) > 1:
            try:
                duration = int(args[1])
            except:
                pass
    else:
        args = message.text.split()
        if len(args) >= 2:
            try:
                target_id = int(args[1])
                if len(args) > 2:
                    duration = int(args[2])
            except:
                bot.reply_to(message, "❌ ID user hoặc thời gian không hợp lệ.")
                return
        else:
            bot.reply_to(message, "Dùng: /mute <user_id> [phút] hoặc reply vào tin nhắn.")
            return

    until_date = datetime.utcnow() + timedelta(minutes=duration)
    until_timestamp = int(until_date.timestamp())

    permissions = ChatPermissions(can_send_messages=False)

    try:
        bot.restrict_chat_member(message.chat.id, target_id, permissions=permissions, until_date=until_timestamp)
        bot.reply_to(message, f"✅ Đã mute user {target_id} trong {duration} phút.")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi mute: {e}")

@bot.message_handler(commands=['unmute'])
def unmute(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này!")
        return

    target_id = None
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    else:
        args = message.text.split()
        if len(args) >= 2:
            try:
                target_id = int(args[1])
            except:
                bot.reply_to(message, "❌ ID user không hợp lệ.")
                return
        else:
            bot.reply_to(message, "Dùng: /unmute <user_id> hoặc reply vào tin nhắn.")
            return

    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True
    )

    try:
        bot.restrict_chat_member(message.chat.id, target_id, permissions=permissions, until_date=0)
        bot.reply_to(message, f"✅ Đã bỏ mute user {target_id}.")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi unmute: {e}")

@bot.message_handler(commands=['ban'])
def ban(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này!")
        return

    target_id = None
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    else:
        args = message.text.split()
        if len(args) >= 2:
            try:
                target_id = int(args[1])
            except:
                bot.reply_to(message, "❌ ID user không hợp lệ.")
                return
        else:
            bot.reply_to(message, "Dùng: /ban <user_id> hoặc reply vào tin nhắn.")
            return

    try:
        bot.kick_chat_member(message.chat.id, target_id)
        bot.reply_to(message, f"✅ Đã ban user {target_id}.")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi ban: {e}")

@bot.message_handler(commands=['unban'])
def unban(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này!")
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Dùng: /unban <user_id>")
        return

    try:
        target_id = int(args[1])
        bot.unban_chat_member(message.chat.id, target_id)
        bot.reply_to(message, f"✅ Đã bỏ ban user {target_id}.")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi unban: {e}")

print("Bot đang chạy...")

if __name__ == "__main__":
    bot_active = True
    bot.infinity_polling()
