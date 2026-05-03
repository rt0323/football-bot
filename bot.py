import asyncio
import os
import json
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
DATA_FILE = "data.json"

def load():
    if not os.path.exists(DATA_FILE):
        return {"teams": {}, "matches": [], "schedule": [], "rules": "3 очка победа / 1 ничья / 0 поражение"}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"teams": {}, "matches": [], "schedule": [], "rules": "error json"}

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Расписание")],
        [KeyboardButton(text="⚽ Матчи")],
        [KeyboardButton(text="🏆 Таблица")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("⚽ Турнир запущен", reply_markup=menu)

ADMIN_ID = 883609508

@dp.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID:  # ✅ исправлено
        await message.answer("⛔ Нет доступа")
        return
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🌐 Админка", web_app=WebAppInfo(url="https://football-bot-production-bd55.up.railway.app"))]],
        resize_keyboard=True
    )
    await message.answer("👑 Панель управления", reply_markup=kb)

@dp.message(F.text == "📅 Расписание")
async def schedule(message: Message):
    data = load()
    text = "📅 Расписание:\n\n" + "\n".join(f"⚽ {s}" for s in data.get("schedule", []))
    await message.answer(text or "Нет матчей")

@dp.message(F.text == "⚽ Матчи")
async def matches(message: Message):
    data = load()
    text = "⚽ Матчи:\n\n" + "\n".join(str(m) for m in data.get("matches", []))
    await message.answer(text or "Нет матчей")

@dp.message(F.text == "🏆 Таблица")
async def table(message: Message):
    data = load()
    teams = data.get("teams", {})
    text = "🏆 Таблица:\n\n" + "\n".join(f"{name}: {stats}" for name, stats in teams.items())
    await message.answer(text or "Нет команд")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
