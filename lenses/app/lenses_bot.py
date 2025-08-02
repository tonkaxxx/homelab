import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

bot = Bot(
    token=API_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

count_days = 0

def get_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅", callback_data="check")],
        [InlineKeyboardButton(text="🔁 Reset", callback_data="reset")]
    ])
    return keyboard

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("press that button:", reply_markup=get_menu())

@dp.callback_query(F.data == "check")
async def check_handler(callback: types.CallbackQuery):
    global count_days
    count_days += 1
    await callback.answer()

    if count_days >= 15:
        await callback.message.answer("change ur lenses!")
        count_days = 0
    else:
        await callback.message.answer(f"day {count_days}/15")

@dp.callback_query(F.data == "reset")
async def reset_handler(callback: types.CallbackQuery):
    global count_days
    count_days = 0
    await callback.answer("counter was reset")
    await callback.message.answer("counter was reset")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
