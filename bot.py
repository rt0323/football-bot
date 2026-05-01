import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8504021199:AAEeIIx--ydG57k_x9kWAzdss5CncTYw3y4"

bot = Bot(token=TOKEN)
dp = Dispatcher()

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚽ Матчи сегодня")],
        [KeyboardButton(text="🏆 Таблица")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Добро пожаловать в футбольный бот ⚽",
        reply_markup=kb
    )

@dp.message()
async def buttons(message: Message):

    if message.text == "⚽ Матчи сегодня":
        await message.answer(
            "Сегодня:\nArsenal vs Chelsea 20:30"
        )

    elif message.text == "🏆 Таблица":
        await message.answer(
            "1. Arsenal\n2. Liverpool\n3. Chelsea"
        )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())