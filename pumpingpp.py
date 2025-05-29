from telegram import Update, ChatPermissions
from telegram.ext import Updater, CommandHandler, CallbackContext
from datetime import timedelta

TOKEN = "7954514943:AAEzy-Usoav6spR4CCdSlOZs4iHMpzySdFY"

# Danh sách user_id của admin được phép dùng lệnh (thay bằng id thật của bạn)
ADMINS = [7606197696, 7658079324]  # ví dụ: [id_admin_1, id_admin_2]

def has_permission(update: Update):
    user_id = update.effective_user.id
    return user_id in ADMINS

def kick(update: Update, context: CallbackContext):
    if not has_permission(update):
        update.message.reply_text("Bạn không có quyền dùng lệnh này!")
        return

    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        try:
            user_id = int(context.args[0])
            target_user = update.effective_chat.get_member(user_id).user
        except Exception:
            update.message.reply_text("Không tìm thấy user.")
            return
    else:
        update.message.reply_text("Dùng: /kick <user_id> hoặc reply vào tin nhắn.")
        return

    try:
        context.bot.kick_chat_member(update.effective_chat.id, target_user.id)
        update.message.reply_text(f"Đã kick {target_user.full_name}")
    except Exception as e:
        update.message.reply_text(f"Lỗi: {e}")

def mute(update: Update, context: CallbackContext):
    if not has_permission(update):
        update.message.reply_text("Bạn không có quyền dùng lệnh này!")
        return

    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        try:
            user_id = int(context.args[0])
            target_user = update.effective_chat.get_member(user_id).user
        except Exception:
            update.message.reply_text("Không tìm thấy user.")
            return
    else:
        update.message.reply_text("Dùng: /mute <user_id> [phút] hoặc reply vào tin nhắn.")
        return

    duration = 5
    if len(context.args) > 1:
        try:
            duration = int(context.args[1])
        except:
            pass

    permissions = ChatPermissions(can_send_messages=False)
    until_date = update.message.date + timedelta(minutes=duration)

    try:
        context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_user.id,
            permissions=permissions,
            until_date=until_date
        )
        update.message.reply_text(f"Đã mute {target_user.full_name} trong {duration} phút.")
    except Exception as e:
        update.message.reply_text(f"Lỗi: {e}")

def unmute(update: Update, context: CallbackContext):
    if not has_permission(update):
        update.message.reply_text("Bạn không có quyền dùng lệnh này!")
        return

    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        try:
            user_id = int(context.args[0])
            target_user = update.effective_chat.get_member(user_id).user
        except Exception:
            update.message.reply_text("Không tìm thấy user.")
            return
    else:
        update.message.reply_text("Dùng: /unmute <user_id> hoặc reply vào tin nhắn.")
        return

    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True
    )

    try:
        context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_user.id,
            permissions=permissions
        )
        update.message.reply_text(f"Đã bỏ mute {target_user.full_name}.")
    except Exception as e:
        update.message.reply_text(f"Lỗi: {e}")

def ban(update: Update, context: CallbackContext):
    if not has_permission(update):
        update.message.reply_text("Bạn không có quyền dùng lệnh này!")
        return

    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        try:
            user_id = int(context.args[0])
            target_user = update.effective_chat.get_member(user_id).user
        except Exception:
            update.message.reply_text("Không tìm thấy user.")
            return
    else:
        update.message.reply_text("Dùng: /ban <user_id> hoặc reply vào tin nhắn.")
        return

    try:
        context.bot.kick_chat_member(update.effective_chat.id, target_user.id)
        update.message.reply_text(f"Đã ban {target_user.full_name}.")
    except Exception as e:
        update.message.reply_text(f"Lỗi: {e}")

def unban(update: Update, context: CallbackContext):
    if not has_permission(update):
        update.message.reply_text("Bạn không có quyền dùng lệnh này!")
        return

    if not context.args:
        update.message.reply_text("Dùng: /unban <user_id>")
        return

    try:
        user_id = int(context.args[0])
        context.bot.unban_chat_member(update.effective_chat.id, user_id)
        update.message.reply_text(f"Đã bỏ ban user {user_id}.")
    except Exception as e:
        update.message.reply_text(f"Lỗi: {e}")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("kick", kick))
    dp.add_handler(CommandHandler("mute", mute))
    dp.add_handler(CommandHandler("unmute", unmute))
    dp.add_handler(CommandHandler("ban", ban))
    dp.add_handler(CommandHandler("unban", unban))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

