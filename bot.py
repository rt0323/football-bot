import asyncio
import os
import json
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 883609508

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "data.json"


def load():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------
# MENU
# -------------------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Расписание")],
        [KeyboardButton(text="⚽ Матчи")],
        [KeyboardButton(text="🏆 Таблица")]
    ],
    resize_keyboard=True
)


# -------------------------
# ADMIN WEBAPP
# -------------------------

@dp.message(Command("admin"))
async def admin(message: Message):

    print("ADMIN COMMAND:", message.from_user.id)  # проверка

    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа")
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🌐 Админка",
                    web_app=WebAppInfo(
                        url="https://football-bot-production-461b.up.railway.app"
                    )
                )
            ]
        ],
        resize_keyboard=True
    )

    await message.answer("👑 Админ панель", reply_markup=kb)

# -------------------------
# START
# -------------------------

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("⚽ Турнир запущен", reply_markup=menu)


# -------------------------
# SCHEDULE
# -------------------------

@dp.message(lambda m: m.text == "📅 Расписание")
async def schedule(message: Message):
    data = load()

    text = "📅 Расписание:\n\n"

    for s in data["schedule"]:
        text += f"{s['home']} vs {s['away']} — {s['time']}\n"

    await message.answer(text or "нет матчей")


# -------------------------
# RUN
# -------------------------

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
