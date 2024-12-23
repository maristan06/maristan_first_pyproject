from telegram import (Update, InlineKeyboardMarkup, InlineKeyboardButton,
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (Application, ApplicationBuilder, CallbackQueryHandler,
                          ContextTypes, CommandHandler, MessageHandler,
                          filters, ConversationHandler)
from creds import ChatGPT_TOKEN, bot_token
from gpt import ChatGptService
from util import (load_message, load_prompt, send_text, send_image, show_main_menu,
                  default_callback_handler, send_text_buttons)
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'main'
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'translator': 'Воспользоваться умным переводчиком 🇯🇵 🇬🇧'
        # 'recommend': 'Что посоветуешь 🎞️📚🎧🎮'

    })


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await send_text(update, context, 'Возвращаемся в главное меню…')
    await start(update, context)


stop_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Завершить',
                                                          callback_data='stop')]])


# Task No. 1: Random fact --------------------------------------------------------------------
async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'random'
    await send_image(update, context, 'random')
    # message = await send_text(update, context, 'Searching through my data banks...')
    prompt = load_prompt('random')
    answer = await chat_gpt.send_question(prompt, '')
    await send_text_buttons(update, context, answer, {
        'random_more': 'Ещё факт!',
        'stop': 'Завершить'
    })


async def random_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    if context.user_data['mode'] != 'random':
        return
    await random(update, context)


# Task No. 2: ChatGPT interface --------------------------------------------------------------
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'gpt'
    chat_gpt.set_prompt(load_prompt('gpt'))
    text = load_message('gpt')
    await send_image(update, context, 'gpt')
    await send_text(update, context, text)


async def gpt_dialogue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.message.text
    message = await send_text(update, context, "...")
    answer = await chat_gpt.add_message(request)
    await message.delete()
    await send_text_buttons(update, context,
                            answer,
                            buttons={'stop': 'Завершить'})


# Task No. 3: Convo with a celebrity ---------------------------------------------------------
async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'talk'
    text = load_message('talk')
    await send_image(update, context, 'talk')
    await send_text_buttons(update, context, text, buttons={
        'talk_cobain': 'Курт Кобейн',
        'talk_hawking': 'Стивен Хокинг',
        'talk_nietzsche': 'Фридрих Ницше',
        'talk_queen': 'Елизавета Вторая',
        'talk_tolkien': 'Джон Толкиен'
    })


async def talk_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    chat_gpt.set_prompt(load_prompt(data))
    greet = await chat_gpt.add_message('greet me')
    await send_image(update, context, data)
    await send_text(update, context, greet)


# Task No. 4: Quiz --------------------------------------------------------------------------
THEME, CHOOSE, ANSWER, CHOOSE_AFTER = range(4)


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'quiz'
    context.user_data['score'] = 0
    await send_text(update, context, "Начинаем квиз! Выбери тему, на которую будем играть:")
    await send_image(update, context, 'quiz')
    chat_gpt.set_prompt(load_prompt('quiz'))
    await send_text_buttons(update, context, load_message('quiz'), {
        'quiz_prog': 'Программирование на Питоне 🐍',
        'quiz_math': 'Математика 📊',
        'quiz_biology': 'Биология 🦠',
        'quiz_movies': 'Популярное кино 🎞️',
        'stop': 'Завершить квиз'
    })
    return THEME


async def quiz_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    question = await chat_gpt.add_message(update.callback_query.data)
    await send_text(update, context, question)
    return ANSWER


async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    if answer == 'Правильно!':
        context.user_data['score'] = context.user_data.get('score', 0) + 1
        answer = "Правильно! Ваш счет: " + "\U00002B50" * int(context.user_data['score'])
    await send_text_buttons(update, context, answer, {
        'quiz_more': 'Еще вопрос!',
        'quiz_result': 'Результаты',
        'stop': 'Завершить игру'
    })
    return CHOOSE_AFTER


async def quiz_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == 'quiz_more':
        return await quiz_theme(update, context)
    elif update.callback_query.data == 'quiz_result':
        await update.callback_query.answer()
        if context.user_data['score'] != 0:
            await send_text(update, context, "Твой итоговый счет: " + "\U00002B50" * int(context.user_data['score'])
                            + "\n\nМолодец! 🦾")
        else:
            await send_text(update, context, "Твой итоговый счет: 0 😕\n\nХочешь попробовать ещё?")
        await start(update, context)
        return ConversationHandler.END
    else:
        await update.callback_query.answer()
        return await quiz(update, context)


# Task No. 5: Translator --------------------------------------------------------------------
async def translator_intro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'translator'
    chat_gpt.set_prompt(load_prompt('translator'))
    await send_image(update, context, 'translator')
    await send_text_buttons(update, context, load_message('translator'), buttons={
        'translate_to_japanese': 'Японский 🇯🇵',
        'translate_to_english': 'Английский 🇬🇧',
        'translate_to_german': 'Немецкий 🇩🇪',
        'translate_to_valyrian': 'Язык Древней Валирии 🐉'
    })


async def translator_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    initial_text = update.message.text
    message = await send_text(update, context, "Перевожу...")
    translated_text = await chat_gpt.add_message(initial_text)
    await message.delete()
    await send_text_buttons(update, context,
                            translated_text,
                            buttons={'stop': 'Завершить'})


async def translator_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    await chat_gpt.add_message(data)
    await send_text(update, context, 'Введи текст, перевод которого тебе нужен:')


# ------------------------------------------------------------------------------------------


async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    print(data)


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data['mode'] in ('gpt', 'talk'):
        await gpt_dialogue(update, context)
    elif context.user_data['mode'] in ('main', 'random'):
        await start(update, context)
    elif context.user_data['mode'] == 'translator':
        await translator_main(update, context)
    else:
        await echo(update, context)


chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(bot_token).build()

app.add_handler(ConversationHandler(
    entry_points=[CommandHandler('quiz', quiz)],
    states={
        THEME: [CallbackQueryHandler(quiz_theme, pattern='^quiz_.*')],
        CHOOSE: [
            CallbackQueryHandler(quiz_theme, pattern='quiz_more'),
            CallbackQueryHandler(quiz, pattern='quiz_change')
        ],
        ANSWER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_answer)
        ],
        CHOOSE_AFTER: [
            CallbackQueryHandler(quiz_choose, pattern='^quiz_.*')
        ]

    },
    fallbacks=[CommandHandler('stop', stop)]
))


app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('translator', translator_intro))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.add_handler(CallbackQueryHandler(cb_handler, pattern='^start_.*'))
app.add_handler(CallbackQueryHandler(stop, 'stop'))
app.add_handler(CallbackQueryHandler(random_buttons, 'random_.*'))
app.add_handler(CallbackQueryHandler(talk_buttons, 'talk_.*'))
app.add_handler(CallbackQueryHandler(translator_buttons, '^translate_.*'))

app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
