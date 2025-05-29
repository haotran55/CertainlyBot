import asyncio
from telegram import Update, ChatPermissions, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import timedelta

TOKEN = "7954514943:AAEzy-Usoav6spR4CCdSlOZs4iHMpzySdFY"
ADMINS = [7606197696, 7658079324]

def has_permission(update: Update):
    user_id = update.effective_user.id
    return user_id in ADMINS

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not has_permission(update):
        await update.message.reply_text("❌ Bạn không có quyền dùng lệnh này!")
        return

    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        try:
            user_id = int(context.args[0])
            member = await update.effective_chat.get_member(user_id)
            target_user = member.user
        except Exception:
            await update.message.reply_text("❌ Không tìm thấy user hoặc user không trong nhóm.")
            return
    else:
        await update.message.reply_text("Dùng: /kick <user_id> hoặc reply vào tin nhắn.")
        return

    try:
        await context.bot.ban_chat_member(update.effective_chat.id, target_user.id)
        await update.message.reply_text(f"✅ Đã kick {target_user.full_name}")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi kick: {e}")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not has_permission(update):
        await update.message.reply_text("❌ Bạn không có quyền dùng lệnh này!")
        return

    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        try:
            user_id = int(context.args[0])
            member = await update.effective_chat.get_member(user_id)
            target_user = member.user
        except Exception:
            await update.message.reply_text("❌ Không tìm thấy user hoặc user không trong nhóm.")
            return
    else:
        await update.message.reply_text("Dùng: /mute <user_id> [phút] hoặc reply vào tin nhắn.")
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
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_user.id,
            permissions=permissions,
            until_date=until_date
        )
        await update.message.reply_text(f"✅ Đã mute {target_user.full_name} trong {duration} phút.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi mute: {e}")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not has_permission(update):
        await update.message.reply_text("❌ Bạn không có quyền dùng lệnh này!")
        return

    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        try:
            user_id = int(context.args[0])
            member = await update.effective_chat.get_member(user_id)
            target_user = member.user
        except Exception:
            await update.message.reply_text("❌ Không tìm thấy user hoặc user không trong nhóm.")
            return
    else:
        await update.message.reply_text("Dùng: /unmute <user_id> hoặc reply vào tin nhắn.")
        return

    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True
    )

    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_user.id,
            permissions=permissions
        )
        await update.message.reply_text(f"✅ Đã bỏ mute {target_user.full_name}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi unmute: {e}")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not has_permission(update):
        await update.message.reply_text("❌ Bạn không có quyền dùng lệnh này!")
        return

    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        try:
            user_id = int(context.args[0])
            member = await update.effective_chat.get_member(user_id)
            target_user = member.user
        except Exception:
            await update.message.reply_text("❌ Không tìm thấy user hoặc user không trong nhóm.")
            return
    else:
        await update.message.reply_text("Dùng: /ban <user_id> hoặc reply vào tin nhắn.")
        return

    try:
        await context.bot.ban_chat_member(update.effective_chat.id, target_user.id)
        await update.message.reply_text(f"✅ Đã ban {target_user.full_name}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi ban: {e}")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not has_permission(update):
        await update.message.reply_text("❌ Bạn không có quyền dùng lệnh này!")
        return

    if not context.args:
        await update.message.reply_text("Dùng: /unban <user_id>")
        return

    try:
        user_id = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text(f"✅ Đã bỏ ban user {user_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi unban: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot đã khởi động và sẵn sàng!")

async def check_token(token: str):
    bot = Bot(token=token)
    try:
        me = await bot.get_me()
        print(f"Đăng nhập thành công với bot: @{me.username}")
        return True
    except Exception as e:
        print(f"Lỗi token: {e}")
        return False

async def main():
    valid = await check_token(TOKEN)
    if not valid:
        print("Token không hợp lệ, dừng bot.")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("kick", kick))
    application.add_handler(CommandHandler("mute", mute))
    application.add_handler(CommandHandler("unmute", unmute))
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))

    print("Bot đang chạy...")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
