import datetime

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler
from creds import bot_token
from util import send_text, send_image


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f'{text} - {update.effective_user.full_name} | {datetime.datetime.now()}')
    morphed_text = f'{text}-{'-'.join([text[-3:]] * 3)}-{'-'.join([text[-2:]] * 1)}...'
    await context.bot.send_message(update.effective_chat.id, f'{morphed_text}')


async def default_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'gpt')
    await send_text(update, context, 'Welcome, friend! I am an Intelligent bot.')

app = Application.builder().token(bot_token).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.add_handler(CommandHandler('start', default_command_handler))
app.run_polling()