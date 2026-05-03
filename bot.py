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
ADMIN_ID = 883609508

# -------------------------
# 📂 DATA
# -------------------------
def load():
    if not os.path.exists(DATA_FILE):
        default = {
            "teams": {},
            "schedule": [],
            "matches": [],
            "playoff": [],
            "rules": "Правила не заданы",
            "live_match": None,
            "subscribers": []
        }
        save(default)
        return default
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "subscribers" not in data:
                data["subscribers"] = []
            return data
    except:
        return {
            "teams": {},
            "schedule": [],
            "matches": [],
            "playoff": [],
            "rules": "Ошибка загрузки",
            "live_match": None,
            "subscribers": []
        }

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------------
# 📣 УВЕДОМЛЕНИЯ
# -------------------------
async def notify_all(text: str):
    data = load()
    subscribers = data.get("subscribers", [])
    for user_id in subscribers:
        try:
            await bot.send_message(int(user_id), text, parse_mode="HTML")
        except Exception as e:
            print(f"Не удалось отправить {user_id}: {e}")

# -------------------------
# 📱 МЕНЮ
# -------------------------
user_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Расписание"), KeyboardButton(text="⚽ Команды")],
        [KeyboardButton(text="🏆 Результаты"), KeyboardButton(text="🥊 Плей-офф")],
        [KeyboardButton(text="📋 Правила")]
    ],
    resize_keyboard=True
)

# -------------------------
# 🚀 START + SUBSCRIBE
# -------------------------
@dp.message(Command("start"))
async def start(message: Message):
    data = load()
    uid = str(message.from_user.id)
    if uid not in data["subscribers"]:
        data["subscribers"].append(uid)
        save(data)
    await message.answer(
        "⚽ <b>Добро пожаловать в турнир!</b>\n\n"
        "Ты автоматически подписан на уведомления о матчах!\n\n"
        "Выбери раздел:",
        reply_markup=user_menu,
        parse_mode="HTML"
    )

@dp.message(Command("subscribe"))
async def subscribe(message: Message):
    data = load()
    uid = str(message.from_user.id)
    if uid not in data["subscribers"]:
        data["subscribers"].append(uid)
        save(data)
        await message.answer("✅ Ты подписан на уведомления!")
    else:
        await message.answer("✅ Ты уже подписан!")

# -------------------------
# 📅 РАСПИСАНИЕ
# -------------------------
@dp.message(F.text == "📅 Расписание")
async def show_schedule(message: Message):
    data = load()
    schedule = data.get("schedule", [])
    if not schedule:
        await message.answer("📅 Расписание пока не добавлено")
        return
    text = "📅 <b>Расписание матчей:</b>\n\n"
    for i, m in enumerate(schedule, 1):
        text += f"{i}. {m.get('date','')} {m.get('time','')} | <b>{m.get('home','')}</b> vs <b>{m.get('away','')}</b>\n"
    await message.answer(text, parse_mode="HTML")

# -------------------------
# ⚽ КОМАНДЫ
# -------------------------
@dp.message(F.text == "⚽ Команды")
async def show_teams(message: Message):
    data = load()
    teams = data.get("teams", {})
    if not teams:
        await message.answer("⚽ Команды пока не добавлены")
        return
    text = "⚽ <b>Команды турнира:</b>\n\n"
    for team_name, info in teams.items():
        players = info.get("players", [])
        text += f"🔵 <b>{team_name}</b>\n"
        if players:
            for p in players:
                text += f"   • {p}\n"
        else:
            text += "   (нет игроков)\n"
        text += "\n"
    await message.answer(text, parse_mode="HTML")

# -------------------------
# 🏆 РЕЗУЛЬТАТЫ + LIVE
# -------------------------
@dp.message(F.text == "🏆 Результаты")
async def show_results(message: Message):
    data = load()
    matches = data.get("matches", [])
    live = data.get("live_match")
    text = ""
    if live:
        text += f"🔴 <b>LIVE:</b> {live['home']} <b>{live['score']}</b> {live['away']}\n"
        if live.get("scorers"):
            text += f"⚡ Голы: {live['scorers']}\n"
        text += "\n"
    if matches:
        text += "🏆 <b>Завершённые матчи:</b>\n\n"
        for m in reversed(matches):
            text += f"⚽ {m['home']} <b>{m['score']}</b> {m['away']}\n"
            if m.get("scorers"):
                text += f"   ⚡ {m['scorers']}\n"
    if not text:
        text = "Матчей пока нет"
    await message.answer(text, parse_mode="HTML")

# -------------------------
# 🥊 ПЛЕЙ-ОФФ
# -------------------------
@dp.message(F.text == "🥊 Плей-офф")
async def show_playoff(message: Message):
    data = load()
    playoff = data.get("playoff", [])
    if not playoff:
        await message.answer("🥊 Плей-офф ещё не начался")
        return
    text = "🥊 <b>Плей-офф:</b>\n\n"
    for stage in playoff:
        text += f"━━━ <b>{stage['stage']}</b> ━━━\n"
        for m in stage.get("matches", []):
            score = m.get("score", "vs")
            winner = ""
            if m.get("winner"):
                winner = f" 🏆 {m['winner']}"
            text += f"  {m['home']} {score} {m['away']}{winner}\n"
        text += "\n"
    await message.answer(text, parse_mode="HTML")

# -------------------------
# 📋 ПРАВИЛА
# -------------------------
@dp.message(F.text == "📋 Правила")
async def show_rules(message: Message):
    data = load()
    await message.answer(f"📋 <b>Правила:</b>\n\n{data.get('rules','Не заданы')}", parse_mode="HTML")

# -------------------------
# 👑 ADMIN КОМАНДЫ (через /cmd)
# -------------------------
@dp.message(Command("admin"))
async def admin_info(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа")
        return
    await message.answer(
        "👑 <b>Управление через веб-админку</b>\n\n"
        "Открой админ-панель на сайте турнира для управления.\n\n"
        "Или используй команды:\n"
        "/live Команда1|2:1|Команда2|Голы — начать live\n"
        "/stoplive — завершить матч\n"
        "/notify Текст — отправить уведомление всем\n"
        "/startmatch Команда1|Команда2 — уведомить о начале",
        parse_mode="HTML"
    )

@dp.message(Command("live"))
async def cmd_live(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.replace("/live", "").strip()
    parts = [p.strip() for p in args.split("|")]
    if len(parts) < 3:
        await message.answer("Формат: /live Команда1|2:1|Команда2|Кто забил")
        return
    data = load()
    home, score, away = parts[0], parts[1], parts[2]
    scorers = parts[3] if len(parts) > 3 else ""
    data["live_match"] = {"home": home, "score": score, "away": away, "scorers": scorers}
    save(data)
    notify_text = f"🔴 <b>LIVE!</b>\n⚽ <b>{home} {score} {away}</b>"
    if scorers:
        notify_text += f"\n⚡ {scorers}"
    await notify_all(notify_text)
    await message.answer(f"✅ Live обновлён и уведомление отправлено!\n{notify_text}", parse_mode="HTML")

@dp.message(Command("stoplive"))
async def cmd_stoplive(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    data = load()
    live = data.get("live_match")
    if not live:
        await message.answer("⚠️ Нет активного матча")
        return
    data["matches"].append({
        "home": live["home"],
        "away": live["away"],
        "score": live["score"],
        "scorers": live.get("scorers", "")
    })
    data["live_match"] = None
    save(data)
    notify_text = f"🏁 <b>Матч завершён!</b>\n⚽ {live['home']} <b>{live['score']}</b> {live['away']}"
    await notify_all(notify_text)
    await message.answer("✅ Матч завершён!", parse_mode="HTML")

@dp.message(Command("startmatch"))
async def cmd_startmatch(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.replace("/startmatch", "").strip()
    parts = [p.strip() for p in args.split("|")]
    if len(parts) < 2:
        await message.answer("Формат: /startmatch Команда1|Команда2")
        return
    notify_text = f"⚽ <b>Матч начинается!</b>\n🆚 {parts[0]} vs {parts[1]}\n\nСледи за счётом в боте!"
    await notify_all(notify_text)
    await message.answer(f"✅ Уведомление отправлено!\n{notify_text}", parse_mode="HTML")

@dp.message(Command("notify"))
async def cmd_notify(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.replace("/notify", "").strip()
    if not text:
        await message.answer("Формат: /notify Текст уведомления")
        return
    await notify_all(f"📣 <b>Объявление:</b>\n\n{text}")
    await message.answer("✅ Уведомление отправлено!")

# -------------------------
# 🔥 СТАРТ
# -------------------------
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
