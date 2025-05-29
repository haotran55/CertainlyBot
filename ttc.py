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
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này!")
        return

    target_user_id = None
    # Nếu reply vào tin nhắn
    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
    else:
        args = message.text.split()
        if len(args) >= 2:
            try:
                target_user_id = int(args[1])
            except:
                bot.reply_to(message, "❌ ID user không hợp lệ.")
                return
        else:
            bot.reply_to(message, "Dùng: /kick <user_id> hoặc reply vào tin nhắn.")
            return

    try:
        bot.kick_chat_member(message.chat.id, target_user_id)
        bot.reply_to(message, f"✅ Đã kick user {target_user_id}")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi kick: {e}")

@bot.message_handler(commands=['mute'])
def mute(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này!")
        return

    target_user_id = None
    duration_minutes = 5  # mặc định 5 phút

    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
        args = message.text.split()
        if len(args) >= 2:
            try:
                duration_minutes = int(args[1])
            except:
                pass
    else:
        args = message.text.split()
        if len(args) >= 2:
            try:
                target_user_id = int(args[1])
            except:
                bot.reply_to(message, "❌ ID user không hợp lệ.")
                return
            if len(args) >= 3:
                try:
                    duration_minutes = int(args[2])
                except:
                    pass
        else:
            bot.reply_to(message, "Dùng: /mute <user_id> [phút] hoặc reply vào tin nhắn.")
            return

    until_date = datetime.utcnow() + timedelta(minutes=duration_minutes)
    until_timestamp = int(until_date.timestamp())

    permissions = ChatPermissions(can_send_messages=False)

    try:
        bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target_user_id,
            permissions=permissions,
            until_date=until_timestamp
        )
        bot.reply_to(message, f"✅ Đã mute user {target_user_id} trong {duration_minutes} phút.")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi mute: {e}")

@bot.message_handler(commands=['unmute'])
def unmute(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này!")
        return

    target_user_id = None
    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
    else:
        args = message.text.split()
        if len(args) >= 2:
            try:
                target_user_id = int(args[1])
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
        bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target_user_id,
            permissions=permissions,
            until_date=0  # bỏ mute luôn
        )
        bot.reply_to(message, f"✅ Đã bỏ mute user {target_user_id}.")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi unmute: {e}")

@bot.message_handler(commands=['ban'])
def ban(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này!")
        return

    target_user_id = None
    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
    else:
        args = message.text.split()
        if len(args) >= 2:
            try:
                target_user_id = int(args[1])
            except:
                bot.reply_to(message, "❌ ID user không hợp lệ.")
                return
        else:
            bot.reply_to(message, "Dùng: /ban <user_id> hoặc reply vào tin nhắn.")
            return

    try:
        bot.kick_chat_member(message.chat.id, target_user_id)
        bot.reply_to(message, f"✅ Đã ban user {target_user_id}.")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi ban: {e}")

@bot.message_handler(commands=['unban'])
def unban(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này!")
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Dùng: /unban <user_id>")
        return

    try:
        target_user_id = int(args[1])
        bot.unban_chat_member(message.chat.id, target_user_id)
        bot.reply_to(message, f"✅ Đã bỏ ban user {target_user_id}.")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi unban: {e}")

print("Bot đang chạy...")
bot.infinity_polling()
