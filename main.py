from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_TOKEN
from database import init_db, create_database
from bot_handlers import start, manejar_enlace, manejar_errores

def main():
    # Start database.
    create_database()
    init_db()

    # Create bot application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register the handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_enlace))
    application.add_error_handler(manejar_errores)

    # Start polling
    application.run_polling()

if __name__ == '__main__':
    main()
