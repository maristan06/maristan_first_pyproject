import datetime

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from creds import bot_token
from util import send_text, send_image


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f'{text} - {update.effective_user.full_name} | {datetime.datetime.now()}')
    morphed_text = f'{text}-{'-'.join([text[-3:]] * 3)}-{'-'.join([text[-2:]] * 1)}...'
    await context.bot.send_message(update.effective_chat.id, f'{morphed_text}')


async def default_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'gpt')
    # await send_text(update, context, '')
    # markup = ReplyKeyboardMarkup(
    #     [
    #         ['1', '2', '3']
    #     ], one_time_keyboard=True
    # )
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('One', callback_data='start_one')],
            [InlineKeyboardButton('Two', callback_data='start_two')],
            [InlineKeyboardButton('Three', callback_data='start_three')]
        ]
    )
    await context.bot.send_message(update.effective_chat.id, 'Welcome, friend! I am an Intelligent bot.', reply_markup=markup)


async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    print(data)

app = Application.builder().token(bot_token).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.add_handler(CommandHandler('start', default_command_handler))
app.add_handler(CallbackQueryHandler(cb_handler, pattern='^start_.*'))
app.run_polling()