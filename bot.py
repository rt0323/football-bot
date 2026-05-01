import asyncio
import os
import json
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("TOKEN")

ADMIN_ID = 883609508  # твой Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "data.json"

# -------------------------
# 📂 работа с JSON
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
# 👑 проверка админа
# -------------------------

def is_admin(user_id):
    return user_id == ADMIN_ID

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
# 🚀 старт
# -------------------------

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("🏆 Футбольная лига запущена!", reply_markup=menu)

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
# 🏆 таблица
# -------------------------

@dp.message(F.text == "🏆 Таблица")
async def table(message: Message):
    data = load_data()

    teams = data["teams"]

    if not teams:
        await message.answer("Нет команд")
        return

    sorted_teams = sorted(teams.items(), key=lambda x: x[1]["pts"], reverse=True)

    text = "🏆 ТАБЛИЦА:\n\n"

    for name, t in sorted_teams:
        text += (
            f"{name}\n"
            f"Очки: {t.get('pts', 0)}\n"
            f"Игры: {t.get('played', 0)}\n"
            f"Победы: {t.get('wins', 0)}\n\n"
        )

    await message.answer(text)

# -------------------------
# 👑 АДМИН: добавить матч
# -------------------------

@dp.message(Command("add_match"))
async def add_match(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Нет доступа")

    try:
        parts = message.text.split()
        home = parts[1]
        away = parts[2]
        score = parts[3]

        data = load_data()

        data["matches"].append({
            "home": home,
            "away": away,
            "score": score
        })

        save_data(data)

        await message.answer("✅ Матч добавлен")

    except:
        await message.answer("❌ /add_match TeamA TeamB 2:1")

# -------------------------
# 👑 АДМИН: расписание
# -------------------------

@dp.message(Command("add_schedule"))
async def add_schedule(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Нет доступа")

    text = message.text.replace("/add_schedule ", "")

    data = load_data()
    data["schedule"].append(text)
    save_data(data)

    await message.answer("✅ Добавлено в расписание")

# -------------------------
# 👑 АДМИН: команды
# -------------------------

@dp.message(Command("add_team"))
async def add_team(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Нет доступа")

    try:
        team = message.text.split()[1]

        data = load_data()

        if team not in data["teams"]:
            data["teams"][team] = {"pts": 0, "played": 0, "wins": 0}
            save_data(data)

        await message.answer(f"✅ Команда {team} добавлена")

    except:
        await message.answer("❌ /add_team TeamName")

# -------------------------
# 👑 АДМИН: очки
# -------------------------

@dp.message(Command("set_points"))
async def set_points(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Нет доступа")

    try:
        parts = message.text.split()
        team = parts[1]
        points = int(parts[2])

        data = load_data()

        if team not in data["teams"]:
            data["teams"][team] = {"pts": 0, "played": 0, "wins": 0}

        data["teams"][team]["pts"] = points

        save_data(data)

        await message.answer("✅ Очки обновлены")

    except:
        await message.answer("❌ /set_points Team 10")

# -------------------------
# 🚀 запуск
# -------------------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
