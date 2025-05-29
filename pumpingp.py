from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Hàm xử lý tin nhắn: bot sẽ gửi lại tin nhắn giống hệt người dùng gửi
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text(user_message)

if __name__ == '__main__':
    # Thay TOKEN ở đây bằng token bot của bạn
    TOKEN = "7954514943:AAEzy-Usoav6spR4CCdSlOZs4iHMpzySdFY"

    app = ApplicationBuilder().token(TOKEN).build()

    # Gắn handler xử lý tất cả tin nhắn văn bản
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    print("Bot is running...")
    app.run_polling()
