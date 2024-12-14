# Task No. 6: Recommendations --------------------------------------------------------------


async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'recommend'
    context.user_data['preferences'] = {'likes': [], 'dislikes': []}  # stores
    await send_image(update, context, 'recommend')
    chat_gpt.set_prompt(load_prompt('recommend'))
    await send_text_buttons(update, context, load_message('recommend'), buttons={
        'recommend_books': 'Книги 📚',
        'recommend_movies': 'Фильмы 🎞️',
        'recommend_music': 'Музыка 🎧',
        'recommend_games': 'Игры 🎮',
        'stop': 'Завершить'
    })


async def recommend_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    genre_input = str(update.message.text)
    # recommend_answer = await chat_gpt.add_message(genre_input)
    response = await recommend_preference_based(genre_input, context)
    await send_text_buttons(update, context, response, buttons={
        'rec_like': 'Нравится, хочу похожее',
        'rec_dislike': 'Не нравится',
        'stop': 'Завершить'
    })


async def recommend_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_choice = update.callback_query.data
    response = await recommend_preference_based(user_choice, context)
    await send_text_buttons(update, context, response, buttons={
        'surprise_me': 'Удиви меня!',
        'stop': 'Завершить'
    })
    # -----
    # if data == 'surprise_me':
    #     await recommend_surprise_button(update, context)
    # else:
    #     await chat_gpt.add_message(data)
    #     await send_text_buttons(update, context, 'Какой жанр тебя интересует?', buttons={
    #         'surprise_me': 'Удиви меня!'
    #     })


async def recommend_surprise_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    surprise_answer = await chat_gpt.add_message('surprise_me')
    await send_text_buttons(update, context, surprise_answer, buttons={
        'rec_like': 'Нравится, хочу похожее',
        'rec_dislike': 'Не нравится',
        'stop': 'Завершить'
    })


async def recommend_preference_based(user_input, context):
    if user_input == 'rec_like':
        last_item = context.user_data.get('last_recommendation')
        if last_item:
            context.user_data['preferences']['likes'].append(last_item)
        return await chat_gpt.add_message("rec_like")
    elif user_input == 'rec_dislike':
        last_item = context.user_data.get('last_recommendation')
        if last_item:
            context.user_data['preferences']['dislikes'].append(last_item)
        return await chat_gpt.add_message("rec_dislike")
    elif user_input == 'surprise_me':
        return await chat_gpt.add_message("surprise_me")
    else:
        context.user_data['last_recommendation'] = user_input
        return await chat_gpt.add_message(user_input)


app.add_handler(CommandHandler('recommend', recommend))
app.add_handler(CallbackQueryHandler(recommend_buttons, '^recommend_.*'))
app.add_handler(CallbackQueryHandler(recommend_surprise_button, 'surprise_me'))
app.add_handler(CallbackQueryHandler(recommend_buttons, '^rec_.*'))