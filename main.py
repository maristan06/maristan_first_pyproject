from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from creds import bot_token


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(text)



app = Application.builder().token(bot_token).build()
app.add_handler(MessageHandler(filters.TEXT, start))
app.run_polling()