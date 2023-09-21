import logging
import util
import pandas as pd
import textwrap as twp
import pickle
from recommender import Recommender
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
)


# Configuração de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Estados da conversa
START, SELECT_OPTION, ENTER_TEXT_TO_SEARCH, ENTER_TEXT_TO_RECOMMEND, PROCESS_TEXT, SEARCH_MOVIE = range(6)
OPTION_ONE, OPTION_TWO = range(2)

# Carregando modelo salvo
with open('./app/files/knn_model.pkl', 'rb') as f:
    knn_model = pickle.load(f)

with open('./app/files/features.pkl', 'rb') as f:
    features = pickle.load(f)

with open('./app/files/df.pkl', 'rb') as f:
    dataset = pickle.load(f)

# Classe de recomendação
recommender = Recommender(knn_model, dataset, features)

# Função para iniciar a conversa quando o usuário digita o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("👋 Hello, welcome to myNextMovie Bot!")

async def searchMovie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("🔍 Please enter the name of the movie you want to search for.")
    return ENTER_TEXT_TO_SEARCH

async def myNextMovie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("10 movies", callback_data=str(OPTION_ONE))],
        [InlineKeyboardButton("20 movies", callback_data=str(OPTION_TWO))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🍿 How many movies would you like me to recommend?", reply_markup=reply_markup)
    return SELECT_OPTION

async def select_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['selected_option'] = int(query.data)
    await query.message.reply_text("Please enter the name and year of the movie you want to use as a reference. Example: 🎥 Twilight, 2008")
    return ENTER_TEXT_TO_RECOMMEND

# Function to receive the text entered by the user
async def enter_text_to_recommend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data['user_input'] = text
    await recommend_movie(update, context)
    return ConversationHandler.END

async def enter_text_to_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data['user_input'] = text
    await search_movie(update, context)
    return ConversationHandler.END

# Function to process the entered text and provide a response based on the selected option
async def recommend_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_option = context.user_data.get('selected_option')
    user_input = context.user_data.get('user_input')

    movie_title = user_input.split(",")[0]
    year = int(user_input.split(",")[1])

    print(movie_title, year)

    if selected_option == OPTION_ONE:
        if recommender.is_in_movie(movie_title, year):
            recommendations = recommender.get_recommendation(movie_title, year, 10)
            response = "Here are your movies: 🍿\n"
            await update.message.reply_text(response, parse_mode="MarkdownV2")
            img_buffer = recommender.recommend_movie(recommendations)
        else:
            img_buffer = recommender.suggest_movies(movie_title)
            if img_buffer != None:
                response = "Movie not found\. Here are some titles similar to what you entered: 📚\n"
                await update.message.reply_text(response, parse_mode="MarkdownV2")

            else:
                response = "Movie not found 🤷‍♂️"
                await update.message.reply_text(response, parse_mode="MarkdownV2")


    elif selected_option == OPTION_TWO:
        if recommender.is_in_movie(movie_title, year):
            recommendations = recommender.get_recommendation(movie_title, year, 20)
            response = "Here are your movies: 🍿\n"
            await update.message.reply_text(response, parse_mode="MarkdownV2")
            img_buffer = recommender.recommend_movie(recommendations)
        else:
            img_buffer = recommender.suggest_movies(movie_title)
            if img_buffer != None:
                response = "Movie not found\. Here are some titles similar to what you entered: 📚\n"
                await update.message.reply_text(response, parse_mode="MarkdownV2")
            else:
                response = "Movie not found 🤷‍♂️"
                await update.message.reply_text(response, parse_mode="MarkdownV2")
    else:
        response = "Invalid option selected\. Please try again. 🚫"
        await update.message.reply_text(response, parse_mode="MarkdownV2")

    if img_buffer:
        await update.message.reply_photo(photo=img_buffer)
        img_buffer.close()
        
    return ConversationHandler.END

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = context.user_data.get('user_input')

    movie_title = user_input.split(",")[0]

    img_buffer = recommender.suggest_movies(movie_title)
    if img_buffer:
        response = "Some titles similar to what you entered: 📚\n"
        await update.message.reply_text(response, parse_mode="MarkdownV2")  # Send the response automatically after processing
        await update.message.reply_photo(photo=img_buffer)
    else:
        response = "No movies found 🤷‍♂️"
        await update.message.reply_text(response, parse_mode="MarkdownV2")  # Send the response automatically after processing

    return ConversationHandler.END

def main() -> None:
    # Cria a Application e passa o token do seu bot
    application = Application.builder().token("6668316627:AAFVM4xk4CdpIoQbLyA1P3lGfPaeIdVYUqg").build()

    # Cria um ConversationHandler para gerenciar a conversa
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("myNextMovie", myNextMovie),
                    CommandHandler("searchMovie", searchMovie)],
        states={
            SELECT_OPTION: [CallbackQueryHandler(select_option, pattern="^" + str(OPTION_ONE) + "$|^" + str(OPTION_TWO) + "$")],
            ENTER_TEXT_TO_RECOMMEND: [MessageHandler(None, enter_text_to_recommend)],
            PROCESS_TEXT: [MessageHandler(None, recommend_movie)],
            ENTER_TEXT_TO_SEARCH: [MessageHandler(None, enter_text_to_search)],
            SEARCH_MOVIE: [MessageHandler(None, search_movie)],

        },
        fallbacks=[],
    )

    # Adiciona o ConversationHandler à aplicação
    application.add_handler(conv_handler)

    # Executa o bot até que o usuário pressione Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# Verifica se o programa está sendo executado como um script principal
if __name__ == "__main__":
    main()


