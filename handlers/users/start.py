from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from google_utils import append_to_sheet, upload_to_drive
import os
import datetime
import logging
import traceback

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
CONTACT_PERSON, CONTACT_PHONE, ADDRESS, CADASTRAL, TRANSFORMER, PHOTO, LOCATION = range(7)


# Команда /start
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.debug("start_handler ishga tushdi")
    await update.message.reply_text("Введите контактное лицо:")
    return CONTACT_PERSON


# Обработка контактного лица
async def contact_person(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.debug("contact_person ishga tushdi")
    context.user_data['contact_person'] = update.message.text
    phone_button = KeyboardButton(text="Отправить номер телефона", request_contact=True)
    reply_keyboard = [[phone_button]]
    await update.message.reply_text(
        "Отправьте контактный телефон:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CONTACT_PHONE


# Обработка контактного телефона
async def contact_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.debug("contact_phone ishga tushdi")
    contact = update.message.contact
    context.user_data['contact_phone'] = contact.phone_number
    await update.message.reply_text("Введите адрес:")
    return ADDRESS


# Обработка адреса
async def address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.debug("address ishga tushdi")
    context.user_data['address'] = update.message.text
    await update.message.reply_text("Введите кадастровый номер:")
    return CADASTRAL


# Обработка кадастрового номера
async def cadastral(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.debug("cadastral ishga tushdi")
    context.user_data['cadastral'] = update.message.text
    await update.message.reply_text("Введите данные о трансформаторе:")
    return TRANSFORMER


# Обработка данных о трансформаторе
async def transformer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.debug("transformer ishga tushdi")
    context.user_data['transformer'] = update.message.text
    # Rasm so'rash o'rniga to'g'ridan-to'g'ri lokaция so'raymiz
    location_button = KeyboardButton(text="Отправить локацию", request_location=True)
    reply_keyboard = [[location_button]]
    await update.message.reply_text(
        "Отправьте локацию:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return LOCATION


# Обработка фотографии (vaqtincha o'chirildi)
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.debug("photo funksiyasi vaqtincha o'chirildi")
    await update.message.reply_text("Пропускаем загрузку фото. Отправьте локацию:")
    location_button = KeyboardButton(text="Отправить локацию", request_location=True)
    reply_keyboard = [[location_button]]
    await update.message.reply_text(
        "Отправьте локацию:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return LOCATION


# Обработка локации
async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.debug("location ishga tushdi")
    location = update.message.location
    # Lokaцияni Google Maps URL formatiga o'tkazish
    latitude = location.latitude
    longitude = location.longitude
    google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
    context.user_data['location'] = google_maps_url
    logger.debug(f"Google Maps URL: {google_maps_url}")

    # Joriy sana va vaqtni olish
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Сохранение всех данных в Google Sheets
    values = [
        current_time,  # Дата и время (A ustuni)
        context.user_data['contact_person'],  # Контактное лицо (B ustuni)
        context.user_data['contact_phone'],  # Контактный телефон (C ustuni)
        context.user_data['address'],  # Адрес (D ustuni)
        context.user_data['cadastral'],  # Кадастр (E ustuni)
        context.user_data['transformer'],  # Трансформатор (F ustuni)
        "",  # Фотография места (G ustuni, hozircha bo'sh)
        context.user_data['location']  # Локация (H ustuni, Google Maps URL)
    ]
    append_to_sheet(values)

    await update.message.reply_text("Данные успешно сохранены! Нажмите /start, чтобы начать заново.")
    return ConversationHandler.END


# Команда /cancel
async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.debug("cancel_handler ishga tushdi")
    await update.message.reply_text("Операция отменена. Нажмите /start, чтобы начать заново.")
    return ConversationHandler.END


# Обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Xatolik haqida ma'lumotni log qilish
    error = context.error
    logger.error(f"Xatolik yuz berdi: {str(error)}")
    logger.error(f"Xatolik stack trace: {traceback.format_exc()}")

    # Foydalanuvchiga xatolik haqida aniqroq xabar berish
    error_message = "Произошла ошибка. Попробуйте снова с /start."
    if "timeout" in str(error).lower():
        error_message = "Ошибка: Время ожидания истекло. Проверьте интернет-соединение и попробуйте снова с /start."
    elif "network" in str(error).lower():
        error_message = "Ошибка: Проблема с сетью. Проверьте интернет-соединение и попробуйте снова с /start."

    await update.message.reply_text(error_message)


# Регистрация ConversationHandler
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start_handler)],
    states={
        CONTACT_PERSON: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_person)],
        CONTACT_PHONE: [MessageHandler(filters.CONTACT, contact_phone)],
        ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
        CADASTRAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, cadastral)],
        TRANSFORMER: [MessageHandler(filters.TEXT & ~filters.COMMAND, transformer)],
        PHOTO: [MessageHandler(filters.PHOTO, photo)],  # Hozircha ishlatilmaydi, lekin qoldiriladi
        LOCATION: [MessageHandler(filters.LOCATION, location)],
    },
    fallbacks=[CommandHandler('cancel', cancel_handler)]
)