import telebot
import openai

# Cấu hình
TELEGRAM_TOKEN = '7629597522:AAHZHoRUNcwGH6wapzeNB7I-INIRI6-1dJw'
OPENAI_API_KEY = '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'

openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Hàm gọi OpenAI
def chatgpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Lỗi từ OpenAI: {e}"

# Xử lý lệnh /ask
@bot.message_handler(commands=['ask'])
def handle_ask(message):
    prompt = message.text[len('/ask '):].strip()
    if not prompt:
        bot.reply_to(message, "❗ Hãy nhập câu hỏi sau lệnh /ask")
        return
    bot.reply_to(message, "⏳ Đang xử lý...")
    reply = chatgpt_response(prompt)
    bot.reply_to(message, reply)

# Lệnh mặc định nếu người dùng gửi gì đó
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    bot.reply_to(message, "💬 Dùng lệnh /ask để hỏi ChatGPT nhé!")

# Chạy bot
bot.polling()

