import asyncio
import os
import json
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("8504021199:AAEeIIx--ydG57k_x9kWAzdss5CncTYw3y4)

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "data.json"

# -------------------------
# 📂 работа с данными
# -------------------------

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# -------------------------
# 🔘 меню
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
# старт
# -------------------------

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("🏆 Турнир запущен", reply_markup=menu)

# -------------------------
# расписание
# -------------------------

@dp.message(F.text == "📅 Расписание")
async def schedule(message: Message):
    data = load_data()

    text = "📅 РАСПИСАНИЕ:\n\n"
    if not data["schedule"]:
        text += "Пока нет матчей"
    else:
        for s in data["schedule"]:
            text += f"⚽ {s}\n"

    await message.answer(text)

# -------------------------
# матчи
# -------------------------

@dp.message(F.text == "⚽ Матчи")
async def matches(message: Message):
    data = load_data()

    text = "⚽ МАТЧИ:\n\n"
    if not data["matches"]:
        text += "Пока нет результатов"
    else:
        for m in data["matches"]:
            text += f"{m['home']} vs {m['away']} → {m['score']}\n"

    await message.answer(text)

# -------------------------
# таблица
# -------------------------

@dp.message(F.text == "🏆 Таблица")
async def table(message: Message):
    data = load_data()

    teams = data["teams"]
    sorted_teams = sorted(teams.items(), key=lambda x: x[1]["pts"], reverse=True)

    text = "🏆 ТАБЛИЦА:\n\n"

    for name, t in sorted_teams:
        text += (
            f"{name}\n"
            f"Очки: {t['pts']}\n"
            f"Игры: {t['played']}\n"
            f"Победы: {t['wins']}\n\n"
        )

    await message.answer(text)

# -------------------------
# запуск
# -------------------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
