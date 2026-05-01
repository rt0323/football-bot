import asyncio
import os
import json
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 883609508

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "data.json"

# -------------------------
# 📂 DATA
# -------------------------

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"teams": {}, "schedule": [], "matches": [], "players": {}, "playoff": {"rounds": []}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_admin(user_id):
    return user_id == ADMIN_ID

# -------------------------
# 📱 MENUS
# -------------------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏆 Таблица"), KeyboardButton(text="⚽ Матчи")],
        [KeyboardButton(text="📅 Расписание"), KeyboardButton(text="👤 Игроки")],
        [KeyboardButton(text="🏟 Плей-офф")]
    ],
    resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Команда"), KeyboardButton(text="⚽ Матч")],
        [KeyboardButton(text="📅 Расписание"), KeyboardButton(text="👤 Игроки")],
        [KeyboardButton(text="🏟 Плей-офф"), KeyboardButton(text="⏭ Следующий матч")]
    ],
    resize_keyboard=True
)

# -------------------------
# 🚀 START
# -------------------------

@dp.message(Command("start"))
async def start(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("👑 Админ панель", reply_markup=admin_menu)
    else:
        await message.answer("🏆 Футбольный турнир", reply_markup=menu)

# -------------------------
# 📅 SCHEDULE
# -------------------------

@dp.message(F.text == "📅 Расписание")
async def schedule(message: Message):
    data = load_data()
    text = "📅 РАСПИСАНИЕ:\n\n"

    if not data["schedule"]:
        text += "Пусто"
    else:
        for s in data["schedule"]:
            text += f"⚽ {s}\n"

    await message.answer(text)

# -------------------------
# ⚽ MATCHES
# -------------------------

@dp.message(F.text == "⚽ Матчи")
async def matches(message: Message):
    data = load_data()
    text = "⚽ МАТЧИ:\n\n"

    for m in data["matches"]:
        text += f"{m['home']} vs {m['away']} → {m['score']}\n"

    await message.answer(text)

# -------------------------
# 🏆 TABLE
# -------------------------

@dp.message(F.text == "🏆 Таблица")
async def table(message: Message):
    data = load_data()
    teams = data["teams"]

    if not teams:
        return await message.answer("Нет команд")

    sorted_teams = sorted(teams.items(), key=lambda x: x[1]["pts"], reverse=True)

    text = "🏆 ТАБЛИЦА:\n\n"

    place = 1
    for name, t in sorted_teams:
        text += f"{place}. {name} | {t['pts']} очков | {t['wins']} побед\n"
        place += 1

    await message.answer(text)

# -------------------------
# 👤 PLAYERS
# -------------------------

@dp.message(F.text == "👤 Игроки")
async def players(message: Message):
    data = load_data()

    text = "👤 ИГРОКИ:\n\n"

    for name, p in data["players"].items():
        text += f"{name} ({p['team']})\n⚽ {p['goals']} | 🎯 {p['assists']}\n\n"

    await message.answer(text)

# -------------------------
# 🏟 PLAYOFF
# -------------------------

@dp.message(F.text == "🏟 Плей-офф")
async def playoff(message: Message):
    data = load_data()

    text = "🏟 ПЛЕЙ-ОФФ:\n\n"

    for r in data["playoff"]["rounds"]:
        text += f"🔷 {r['name']}\n"
        for m in r["matches"]:
            score = m["score"] if m["score"] else "—"
            text += f"{m['a']} vs {m['b']} → {score}\n"
        text += "\n"

    await message.answer(text)

# -------------------------
# 👑 ADD TEAM
# -------------------------

@dp.message(F.text == "➕ Команда")
async def add_team(message: Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer("Напиши: Название команды")

@dp.message()
async def handler(message: Message):
    data = load_data()

    if not is_admin(message.from_user.id):
        return

    text = message.text

    # ➕ команда
    if len(text.split()) == 1 and text.isalpha():
        if text not in data["teams"]:
            data["teams"][text] = {"pts": 0, "played": 0, "wins": 0}
            save_data(data)
            return await message.answer("✅ Команда добавлена")

    # ⚽ матч
    if len(text.split()) == 3 and ":" in text:
        home, away, score = text.split()
        h, a = map(int, score.split(":"))

        data["matches"].append({
            "home": home,
            "away": away,
            "score": score
        })

        for t in [home, away]:
            if t not in data["teams"]:
                data["teams"][t] = {"pts": 0, "played": 0, "wins": 0}

        data["teams"][home]["played"] += 1
        data["teams"][away]["played"] += 1

        if h > a:
            data["teams"][home]["pts"] += 3
            data["teams"][home]["wins"] += 1
        elif a > h:
            data["teams"][away]["pts"] += 3
            data["teams"][away]["wins"] += 1
        else:
            data["teams"][home]["pts"] += 1
            data["teams"][away]["pts"] += 1

        save_data(data)
        await message.answer("⚽ Матч добавлен + таблица обновлена")

# -------------------------
# 🚀 RUN
# -------------------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
