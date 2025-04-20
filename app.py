import logging
from telegram.ext import Application, ConversationHandler, CommandHandler
from handlers.users.start import start_handler, cancel_handler, error_handler, conversation_handler

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
CONTACT_PERSON, CONTACT_PHONE, ADDRESS, CADASTRAL, TRANSFORMER, PHOTO, LOCATION = range(7)

def main():
    # Haqiqiy bot tokeningizni bu yerga qo‘ying
    application = Application.builder().token('8166835620:AAErZb2f3Af6LrfPIBDG2mY_CxCn2hHBcAU').build()

    # Регистрация хэндлеров
    application.add_handler(conversation_handler)
    application.add_handler(CommandHandler('cancel', cancel_handler))
    application.add_error_handler(error_handler)

    # Запуск бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    main()