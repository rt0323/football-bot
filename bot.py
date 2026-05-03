import asyncio
import os
import json
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# -------------------------
# 🔑 TOKEN
# -------------------------
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
DATA_FILE = "data.json"

ADMIN_ID = 883609508  # твой Telegram ID

# -------------------------
# 📂 DATA
# -------------------------
def load():
    if not os.path.exists(DATA_FILE):
        return {
            "teams": {},
            "schedule": [],
            "matches": [],
            "playoff": [],
            "rules": "Правила не заданы",
            "live_match": None
        }
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "teams": {},
            "schedule": [],
            "matches": [],
            "playoff": [],
            "rules": "Ошибка загрузки",
            "live_match": None
        }

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------------
# 📱 МЕНЮ ПОЛЬЗОВАТЕЛЯ
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
# 👑 МЕНЮ АДМИНИСТРАТОРА
# -------------------------
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить команду"), KeyboardButton(text="👤 Добавить игрока")],
        [KeyboardButton(text="📅 Добавить матч"), KeyboardButton(text="🥊 Добавить плей-офф")],
        [KeyboardButton(text="⚽ Обновить счёт"), KeyboardButton(text="📣 Уведомление")],
        [KeyboardButton(text="📋 Установить правила"), KeyboardButton(text="🔙 Выход из админки")]
    ],
    resize_keyboard=True
)

# -------------------------
# 🚀 START
# -------------------------
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "⚽ <b>Добро пожаловать в турнир!</b>\n\nВыбери раздел:",
        reply_markup=user_menu,
        parse_mode="HTML"
    )

# -------------------------
# 👑 ADMIN
# -------------------------
@dp.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа")
        return
    await message.answer("👑 <b>Панель администратора</b>", reply_markup=admin_menu, parse_mode="HTML")

@dp.message(F.text == "🔙 Выход из админки")
async def exit_admin(message: Message):
    await message.answer("✅ Вернулся в обычный режим", reply_markup=user_menu)

# -------------------------
# 📅 РАСПИСАНИЕ (пользователь)
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
        text += f"{i}. {m['date']} | <b>{m['home']}</b> vs <b>{m['away']}</b>\n"
        if m.get("time"):
            text += f"   🕐 {m['time']}\n"
    await message.answer(text, parse_mode="HTML")

# -------------------------
# ⚽ КОМАНДЫ И ИГРОКИ (пользователь)
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
# 🏆 РЕЗУЛЬТАТЫ (пользователь)
# -------------------------
@dp.message(F.text == "🏆 Результаты")
async def show_results(message: Message):
    data = load()
    matches = data.get("matches", [])
    live = data.get("live_match")

    text = ""

    if live:
        text += f"🔴 <b>LIVE:</b> {live['home']} <b>{live['score']}</b> {live['away']}\n\n"

    if matches:
        text += "🏆 <b>Завершённые матчи:</b>\n\n"
        for m in matches:
            text += f"⚽ {m['home']} <b>{m['score']}</b> {m['away']}\n"
            if m.get("scorers"):
                text += f"   ⚡ {m['scorers']}\n"
    else:
        text += "Матчей пока нет"

    if not text:
        text = "Нет данных"

    await message.answer(text, parse_mode="HTML")

# -------------------------
# 🥊 ПЛЕЙ-ОФФ (пользователь)
# -------------------------
@dp.message(F.text == "🥊 Плей-офф")
async def show_playoff(message: Message):
    data = load()
    playoff = data.get("playoff", [])
    if not playoff:
        await message.answer("🥊 Плей-офф ещё не начался")
        return
    text = "🥊 <b>Плей-офф сетка:</b>\n\n"
    for stage in playoff:
        text += f"🔹 <b>{stage['stage']}</b>\n"
        for match in stage.get("matches", []):
            score = match.get("score", "vs")
            text += f"   {match['home']} <b>{score}</b> {match['away']}\n"
        text += "\n"
    await message.answer(text, parse_mode="HTML")

# -------------------------
# 📋 ПРАВИЛА (пользователь)
# -------------------------
@dp.message(F.text == "📋 Правила")
async def show_rules(message: Message):
    data = load()
    rules = data.get("rules", "Правила не заданы")
    await message.answer(f"📋 <b>Правила турнира:</b>\n\n{rules}", parse_mode="HTML")

# ============================================
# 👑 ADMIN HANDLERS (через состояния вручную)
# ============================================

# Хранилище состояний (в памяти)
user_states = {}

def set_state(user_id, state, extra=None):
    user_states[user_id] = {"state": state, "extra": extra or {}}

def get_state(user_id):
    return user_states.get(user_id, {})

def clear_state(user_id):
    user_states.pop(user_id, None)

# -------------------------
# ➕ ДОБАВИТЬ КОМАНДУ
# -------------------------
@dp.message(F.text == "➕ Добавить команду")
async def add_team_start(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    set_state(message.from_user.id, "add_team")
    await message.answer("✏️ Введи название команды:")

# -------------------------
# 👤 ДОБАВИТЬ ИГРОКА
# -------------------------
@dp.message(F.text == "👤 Добавить игрока")
async def add_player_start(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    data = load()
    teams = list(data.get("teams", {}).keys())
    if not teams:
        await message.answer("⚠️ Сначала добавь команду!")
        return
    text = "Выбери команду (отправь название):\n\n"
    for t in teams:
        text += f"• {t}\n"
    set_state(message.from_user.id, "add_player_team")
    await message.answer(text)

# -------------------------
# 📅 ДОБАВИТЬ МАТЧ В РАСПИСАНИЕ
# -------------------------
@dp.message(F.text == "📅 Добавить матч")
async def add_schedule_start(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    set_state(message.from_user.id, "add_schedule")
    await message.answer(
        "✏️ Введи матч в формате:\n"
        "<code>Дата | Время | Команда1 | Команда2</code>\n\n"
        "Пример:\n<code>15.06 | 18:00 | Реал Мадрид | Барселона</code>",
        parse_mode="HTML"
    )

# -------------------------
# 🥊 ДОБАВИТЬ ПЛЕЙ-ОФФ
# -------------------------
@dp.message(F.text == "🥊 Добавить плей-офф")
async def add_playoff_start(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    set_state(message.from_user.id, "add_playoff")
    await message.answer(
        "✏️ Введи матч плей-офф:\n"
        "<code>Стадия | Команда1 | Команда2</code>\n\n"
        "Пример:\n<code>Полуфинал | Реал Мадрид | Барселона</code>",
        parse_mode="HTML"
    )

# -------------------------
# ⚽ ОБНОВИТЬ СЧЁТ (LIVE)
# -------------------------
@dp.message(F.text == "⚽ Обновить счёт")
async def update_score_start(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    set_state(message.from_user.id, "update_score")
    await message.answer(
        "✏️ Введи счёт:\n"
        "<code>Команда1 | Счёт | Команда2 | Кто забил</code>\n\n"
        "Пример:\n<code>Реал Мадрид | 2:1 | Барселона | Мбаппе 45, Виниций 78</code>\n\n"
        "Или <code>стоп</code> — завершить матч",
        parse_mode="HTML"
    )

# -------------------------
# 📣 УВЕДОМЛЕНИЕ ВСЕМ
# -------------------------
subscribed_users = set()  # в реальном проекте хранить в data.json

@dp.message(Command("subscribe"))
async def subscribe(message: Message):
    subscribed_users.add(message.from_user.id)
    await message.answer("✅ Ты подписан на уведомления о матчах!")

@dp.message(F.text == "📣 Уведомление")
async def send_notify_start(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    set_state(message.from_user.id, "send_notify")
    await message.answer("✏️ Введи текст уведомления для всех подписчиков:")

# -------------------------
# 📋 УСТАНОВИТЬ ПРАВИЛА
# -------------------------
@dp.message(F.text == "📋 Установить правила")
async def set_rules_start(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    set_state(message.from_user.id, "set_rules")
    await message.answer("✏️ Введи текст правил турнира:")

# ============================================
# 📥 ОБРАБОТЧИК ВСЕХ ТЕКСТОВЫХ СООБЩЕНИЙ
# ============================================
@dp.message(F.text)
async def handle_text(message: Message):
    uid = message.from_user.id
    state_info = get_state(uid)
    state = state_info.get("state")
    extra = state_info.get("extra", {})
    text = message.text.strip()

    # --- ДОБАВИТЬ КОМАНДУ ---
    if state == "add_team":
        data = load()
        if text not in data["teams"]:
            data["teams"][text] = {"players": []}
            save(data)
            await message.answer(f"✅ Команда <b>{text}</b> добавлена!", parse_mode="HTML")
        else:
            await message.answer(f"⚠️ Команда <b>{text}</b> уже существует", parse_mode="HTML")
        clear_state(uid)

    # --- ВЫБОР КОМАНДЫ ДЛЯ ИГРОКА ---
    elif state == "add_player_team":
        data = load()
        if text not in data["teams"]:
            await message.answer("❌ Команда не найдена. Попробуй ещё раз:")
            return
        set_state(uid, "add_player_name", {"team": text})
        await message.answer(f"✏️ Введи имя игрока для команды <b>{text}</b>:", parse_mode="HTML")

    # --- ИМЯ ИГРОКА ---
    elif state == "add_player_name":
        data = load()
        team = extra.get("team")
        if team and team in data["teams"]:
            data["teams"][team]["players"].append(text)
            save(data)
            await message.answer(f"✅ Игрок <b>{text}</b> добавлен в <b>{team}</b>!", parse_mode="HTML")
        else:
            await message.answer("❌ Ошибка, команда не найдена")
        clear_state(uid)

    # --- ДОБАВИТЬ МАТЧ В РАСПИСАНИЕ ---
    elif state == "add_schedule":
        parts = [p.strip() for p in text.split("|")]
        if len(parts) < 3:
            await message.answer("❌ Неверный формат. Попробуй:\n<code>15.06 | 18:00 | Команда1 | Команда2</code>", parse_mode="HTML")
            return
        data = load()
        if len(parts) == 4:
            match = {"date": parts[0], "time": parts[1], "home": parts[2], "away": parts[3]}
        else:
            match = {"date": parts[0], "time": "", "home": parts[1], "away": parts[2]}
        data["schedule"].append(match)
        save(data)
        await message.answer(f"✅ Матч добавлен в расписание:\n⚽ <b>{match['home']}</b> vs <b>{match['away']}</b> — {match['date']}", parse_mode="HTML")
        clear_state(uid)

    # --- ДОБАВИТЬ ПЛЕЙ-ОФФ ---
    elif state == "add_playoff":
        parts = [p.strip() for p in text.split("|")]
        if len(parts) != 3:
            await message.answer("❌ Формат: <code>Стадия | Команда1 | Команда2</code>", parse_mode="HTML")
            return
        data = load()
        stage_name, home, away = parts
        # Ищем существующую стадию
        found = False
        for stage in data["playoff"]:
            if stage["stage"] == stage_name:
                stage["matches"].append({"home": home, "away": away})
                found = True
                break
        if not found:
            data["playoff"].append({"stage": stage_name, "matches": [{"home": home, "away": away}]})
        save(data)
        await message.answer(f"✅ Плей-офф добавлен:\n🥊 <b>{stage_name}</b>: {home} vs {away}", parse_mode="HTML")
        clear_state(uid)

    # --- ОБНОВИТЬ СЧЁТ ---
    elif state == "update_score":
        if text.lower() == "стоп":
            data = load()
            live = data.get("live_match")
            if live:
                # Переносим в завершённые матчи
                data["matches"].append({
                    "home": live["home"],
                    "away": live["away"],
                    "score": live["score"],
                    "scorers": live.get("scorers", "")
                })
                data["live_match"] = None
                save(data)
                # Уведомляем подписчиков
                result_text = f"🏁 Матч завершён!\n⚽ {live['home']} <b>{live['score']}</b> {live['away']}"
                for user_id in subscribed_users:
                    try:
                        await bot.send_message(user_id, result_text, parse_mode="HTML")
                    except:
                        pass
                await message.answer("✅ Матч завершён и сохранён в результаты!")
            else:
                await message.answer("⚠️ Нет активного матча")
            clear_state(uid)
            return

        parts = [p.strip() for p in text.split("|")]
        if len(parts) < 3:
            await message.answer("❌ Формат:\n<code>Команда1 | Счёт | Команда2 | Кто забил</code>", parse_mode="HTML")
            return
        data = load()
        home, score, away = parts[0], parts[1], parts[2]
        scorers = parts[3] if len(parts) > 3 else ""
        data["live_match"] = {"home": home, "score": score, "away": away, "scorers": scorers}
        save(data)

        # Уведомляем подписчиков
        notify_text = f"🔴 <b>LIVE обновление!</b>\n⚽ {home} <b>{score}</b> {away}"
        if scorers:
            notify_text += f"\n⚡ {scorers}"
        for user_id in subscribed_users:
            try:
                await bot.send_message(user_id, notify_text, parse_mode="HTML")
            except:
                pass

        await message.answer(f"✅ Счёт обновлён!\n{notify_text}", parse_mode="HTML")
        await message.answer("Отправь новый счёт или напиши <b>стоп</b> для завершения матча", parse_mode="HTML")
        # Не сбрасываем state — ждём следующего обновления

    # --- ОТПРАВИТЬ УВЕДОМЛЕНИЕ ---
    elif state == "send_notify":
        notify_text = f"📣 <b>Объявление:</b>\n\n{text}"
        count = 0
        for user_id in subscribed_users:
            try:
                await bot.send_message(user_id, notify_text, parse_mode="HTML")
                count += 1
            except:
                pass
        await message.answer(f"✅ Уведомление отправлено {count} подписчикам!")
        clear_state(uid)

    # --- УСТАНОВИТЬ ПРАВИЛА ---
    elif state == "set_rules":
        data = load()
        data["rules"] = text
        save(data)
        await message.answer("✅ Правила турнира обновлены!")
        clear_state(uid)

# -------------------------
# 🔥 СТАРТ БОТА
# -------------------------
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
