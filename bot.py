import asyncio
import os
import json
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "data.json"

# -------------------------
# 📂 работа с данными
# -------------------------

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"teams": {}, "schedule": [], "matches": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
    await message.answer("🏆 Добро пожаловать в футбольную лигу!", reply_markup=menu)

# -------------------------
# 📅 расписание
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
# ⚽ матчи
# -------------------------

@dp.message(F.text == "⚽ Матчи")
async def matches(message: Message):
    data = load_data()

    text = "⚽ РЕЗУЛЬТАТЫ:\n\n"

    if not data["matches"]:
        text += "Пока нет матчей"
    else:
        for m in data["matches"]:
            text += f"{m['home']} vs {m['away']} → {m['score']}\n"

    await message.answer(text)

# -------------------------
# 🏆 таблица (авто подсчёт)
# -------------------------

@dp.message(F.text == "🏆 Таблица")
async def table(message: Message):
    data = load_data()

    teams = data["teams"]

    # если нет команд
    if not teams:
        await message.answer("Нет команд")
        return

    sorted_teams = sorted(teams.items(), key=lambda x: x[1].get("pts", 0), reverse=True)

    text = "🏆 ТАБЛИЦА ЛИГИ:\n\n"

    for name, t in sorted_teams:
        text += (
            f"{name}\n"
            f"Очки: {t.get('pts', 0)}\n"
            f"Игры: {t.get('played', 0)}\n"
            f"Победы: {t.get('wins', 0)}\n\n"
        )

    await message.answer(text)

# -------------------------
# 🚀 запуск
# -------------------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
