import logging
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
START, SELECT_OPTION, ENTER_TEXT, PROCESS_TEXT, SEARCH_MOVIE = range(5)
OPTION_ONE, OPTION_TWO = range(2)

# Lista de sugestões de palavras
suggestions_list = ["maçã", "banana", "cereja", "data", "uva"]

# Função para iniciar a conversa quando o usuário digita o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("10", callback_data=str(OPTION_ONE))],
        [InlineKeyboardButton("20", callback_data=str(OPTION_TWO))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Quantidade de Filmes:", reply_markup=reply_markup)
    return SELECT_OPTION

# Função para lidar com a seleção de uma opção por meio dos botões inline
async def select_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['selected_option'] = int(query.data)
    await query.message.reply_text("Por favor digite o nome do filme que deseja usar como base")
    return ENTER_TEXT

# Função para receber o texto inserido pelo usuário
async def enter_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data['user_input'] = text
    await process_text(update, context)  # Chama a função process_text imediatamente
    return ConversationHandler.END

# Função para processar o texto inserido e fornecer uma resposta com base na opção selecionada
async def process_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_option = context.user_data.get('selected_option')
    user_input = context.user_data.get('user_input')

    if selected_option == OPTION_ONE:
        # Processa com base na primeira opção
        response = f"Opção 1 selecionada. Você digitou: {user_input}"
    elif selected_option == OPTION_TWO:
        # Processa com base na segunda opção
        # Sugere palavras com base na lista predefinida
        suggestions = suggest_words(user_input)
        response = f"Opção 2 selecionada. Sugestões: {', '.join(suggestions)}"
    else:
        response = "Opção inválida selecionada."

    await update.message.reply_text(response)  # Envia a resposta automaticamente após o processamento
    return ConversationHandler.END


# Função para sugerir palavras com base no texto inserido pelo usuário
def suggest_words(input_text):
    # Implemente aqui a lógica de sugestão de palavras com base na lista predefinida
    # Neste exemplo, sugerimos palavras que começam com o texto inserido
    suggestions = [word for word in suggestions_list if word.startswith(input_text)]
    return suggestions

# Função principal do programa
def main() -> None:
    # Cria a Application e passa o token do seu bot
    application = Application.builder().token("6668316627:AAFVM4xk4CdpIoQbLyA1P3lGfPaeIdVYUqg").build()

    # Cria um ConversationHandler para gerenciar a conversa
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_OPTION: [CallbackQueryHandler(select_option, pattern="^" + str(OPTION_ONE) + "$|^" + str(OPTION_TWO) + "$")],
            ENTER_TEXT: [MessageHandler(None, enter_text)],
            PROCESS_TEXT: [MessageHandler(None, process_text)],
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
