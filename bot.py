from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler
from openai import OpenAI
from gpt import ChatGptService
from util import (load_message, load_prompt, send_text, send_image, show_main_menu,
                  default_callback_handler)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓'
        # Добавить команду в меню можно так:
        # 'command': 'button text'

    })


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'random')
    message = await send_text(update, context, 'Searching through my data banks...')
    prompt = load_prompt('random')
    answer = await chat_gpt.send_question(prompt, '')
    await message.edit_text(answer)



chat_gpt = ChatGptService('ChatGPT TOKEN')
app = ApplicationBuilder().token('Telegram TOKEN').build()

# Зарегистрировать обработчик команды можно так:
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))

# Зарегистрировать обработчик коллбэка можно так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
