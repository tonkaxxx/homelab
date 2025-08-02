import cv2
import pytesseract
import tempfile
import os
import nltk
import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# Инициализация словарей nltk
nltk.download('punkt')

# Установите свой токен
TELEGRAM_TOKEN = '7686102771:AAGTK3QjGduaCTLnepudS_wpMVh2sClIVBg'  # Используйте переменные окружения для безопасности

# ID администратора для отправки логов
ADMIN_ID = 1143331646

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция для отправки сообщений админу
async def send_log_to_admin(context: ContextTypes.DEFAULT_TYPE, message: str):
    await context.bot.send_message(chat_id=ADMIN_ID, text=message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    log_message = f"Команда /start от пользователя: {user_id} ({username})"
    logger.info(log_message)
    await send_log_to_admin(context, log_message)

    # Отправка приветственного сообщения и картинки
    await update.message.reply_text(
        'Привет! Отправь мне фото с текстом, и укажи количество слов для сокращения.\n'
        'Пример: 10, чтобы оставить суть текста в 10 словах.\n'
        'А если хочешь чтобы я вывел весь текст, ничего не пиши после изображения! \n'
        '\n'
        'Вот пример:'
    )

    # Отправка изображения
    with open("welcome.jpg", "rb") as image_file:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=InputFile(image_file))

async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    log_message = f"Обработка изображения от пользователя: {user_id} ({username})"
    logger.info(log_message)
    await send_log_to_admin(context, log_message)

    file = await update.message.photo[-1].get_file()

    # Сохраняем изображение во временный файл
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        await file.download_to_drive(temp_file.name)
        logger.info(f"Изображение сохранено временно: {temp_file.name}")

    # Используем OpenCV и pytesseract для распознавания текста на изображении
    img = cv2.imread(temp_file.name)
    text = pytesseract.image_to_string(img, lang='rus')
    os.remove(temp_file.name)  # Удаляем временный файл

    # Если текст не обнаружен, отправляем пользователю предупреждение
    if not text.strip():
        log_message = f"Текст не обнаружен на изображении от {user_id} ({username})"
        logger.info(log_message)
        await send_log_to_admin(context, log_message)
        await update.message.reply_text("На этой фотографии нет текста!")
        return

    # Добавляем распознанный текст в лог и отправляем его админу
    log_message = f"Распознанный текст от {user_id} ({username}):\n{text}"
    logger.info(log_message)
    await send_log_to_admin(context, log_message)

    # Проверка на количество слов, если пользователь указал его в сообщении
    try:
        word_limit = int(update.message.caption) if update.message.caption else 12349
    except ValueError:
        word_limit = 121312
    logger.info(f"Ограничение по словам от {user_id} ({username}): {word_limit}")

    # Сокращаем текст до указанного количества слов, сохраняя смысл
    summarized_text = summarize_text(text, word_limit)
    logger.info(f"Сокращенный текст от {user_id} ({username}): {summarized_text}")

    await update.message.reply_text(summarized_text)

def summarize_text(text, word_limit):
    parser = PlaintextParser.from_string(text, Tokenizer("russian"))
    summarizer = LsaSummarizer()

    # Получаем список предложений из суммированного текста
    summary = summarizer(parser.document, sentences_count=max(1, word_limit // 10))  # Примерное количество предложений

    # Объединяем предложения в текст и ограничиваем по слову
    summarized_text = ' '.join(str(sentence) for sentence in summary)
    return ' '.join(summarized_text.split()[:word_limit])  # Ограничение по количеству слов

def main():
    # Создаем приложение с использованием безопасного способа передачи токена
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики команд и изображений
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.PHOTO, process_image))

    logger.info("Запуск бота...")
    # Запускаем бота
    app.run_polling()

if __name__ == '__main__':
    main()
