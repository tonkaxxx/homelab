#pip install python-telegram-bot==20.6
from telegram.ext import Application, CommandHandler # type: ignore
from telegram import Bot # type: ignore
import logging
import asyncio
from datetime import time

TOKEN = ":AAECZvmuzsIMgdqfvaQdgCt5_KL3Vor0zqo"
CHAT_ID = "1143331646"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update, context):
    await update.message.reply_text('Бот запущен! Напоминания с 15:00 до 21:00')

async def send_reminder(context):
    await context.bot.send_message(chat_id=CHAT_ID, text="⏰ Напоминание: прошло 2 часа!")

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))
    
    # Настраиваем расписание (15:00, 17:00, 19:00, 21:00)
    job_queue = application.job_queue
    job_queue.run_daily(send_reminder, time(12, 0))  # 15:00
    job_queue.run_daily(send_reminder, time(14, 0))  # 17:00
    job_queue.run_daily(send_reminder, time(16, 47))  # 19:00
    job_queue.run_daily(send_reminder, time(18, 0))  # 21:00
    job_queue.run_daily(send_reminder, time(20, 0))  # 23:00
    
    application.run_polling()

if __name__ == '__main__':
    main()
