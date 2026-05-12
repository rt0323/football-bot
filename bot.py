import asyncio
import os
import json
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "data.json"
ADMIN_ID = 883609508
SITE_URL = "https://football-bot-production-bd55.up.railway.app"

START_COINS = 1000       # монет при регистрации
BET_WIN_MULTIPLIER = 2.0 # коэффициент выигрыша (x2)

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
            "subscribers": [],
            "users": {},       # { user_id: { "coins": int, "bets": [] } }
            "open_bets": []    # активные ставки на текущий матч
        }
        save(default)
        return default
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "subscribers" not in data:
            data["subscribers"] = []
        if "users" not in data:
            data["users"] = {}
        if "open_bets" not in data:
            data["open_bets"] = []
        return data
    except:
        return {
            "teams": {}, "schedule": [], "matches": [], "playoff": [],
            "rules": "Ошибка загрузки", "live_match": None,
            "subscribers": [], "users": {}, "open_bets": []
        }

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data, uid: str):
    """Возвращает профиль пользователя, создаёт если нет."""
    if uid not in data["users"]:
        data["users"][uid] = {"coins": START_COINS, "bets": []}
    return data["users"][uid]

# -------------------------
# 📣 УВЕДОМЛЕНИЯ
# -------------------------

async def notify_all(text: str):
    data = load()
    for user_id in data.get("subscribers", []):
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
        [KeyboardButton(text="📋 Правила"), KeyboardButton(text="🎰 Ставки")],
        [KeyboardButton(text="💰 Мой баланс"), KeyboardButton(text="🏅 Топ игроков")]
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
    user = get_user(data, uid)
    save(data)
    await message.answer(
        f"⚽ <b>Добро пожаловать в турнир!</b>\n\n"
        f"Ты автоматически подписан на уведомления!\n"
        f"💰 Твой стартовый баланс: <b>{user['coins']} монет</b>\n\n"
        f"Делай ставки на матчи и соревнуйся с другими!\n\n"
        f"Выбери раздел:",
        reply_markup=user_menu,
        parse_mode="HTML"
    )

@dp.message(Command("subscribe"))
async def subscribe(message: Message):
    data = load()
    uid = str(message.from_user.id)
    if uid not in data["subscribers"]:
        data["subscribers"].append(uid)
    get_user(data, uid)
    save(data)
    await message.answer("✅ Ты подписан на уведомления!")

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
        for p in players:
            text += f"  • {p}\n"
        if not players:
            text += "  (нет игроков)\n"
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
                text += f"  ⚡ {m['scorers']}\n"
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
            winner = f" 🏆 {m['winner']}" if m.get("winner") else ""
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
# 🎰 СТАВКИ — главное меню
# -------------------------

@dp.message(F.text == "🎰 Ставки")
async def bets_menu(message: Message):
    data = load()
    uid = str(message.from_user.id)
    user = get_user(data, uid)
    save(data)

    live = data.get("live_match")

    # Проверяем, есть ли уже ставка пользователя на текущий матч
    existing = next((b for b in data["open_bets"] if str(b["user_id"]) == uid), None)

    if not live:
        # Нет активного матча — показываем ближайший из расписания
        schedule = data.get("schedule", [])
        if not schedule:
            await message.answer(
                f"🎰 <b>Ставки</b>\n\n"
                f"💰 Твой баланс: <b>{user['coins']} монет</b>\n\n"
                f"Сейчас нет активных матчей для ставок.\n"
                f"Ставки принимаются когда админ запускает матч через /startmatch.",
                parse_mode="HTML"
            )
        else:
            next_match = schedule[0]
            home = next_match.get("home", "?")
            away = next_match.get("away", "?")
            date = next_match.get("date", "")
            time = next_match.get("time", "")
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text=f"🔵 {home}", callback_data=f"bet_pre|{home}|{away}|{home}"),
                    InlineKeyboardButton(text=f"🔴 {away}", callback_data=f"bet_pre|{home}|{away}|{away}"),
                ],
                [InlineKeyboardButton(text="🤝 Ничья", callback_data=f"bet_pre|{home}|{away}|draw")]
            ])
            await message.answer(
                f"🎰 <b>Ставки</b>\n\n"
                f"💰 Твой баланс: <b>{user['coins']} монет</b>\n\n"
                f"⏳ Следующий матч: <b>{home}</b> vs <b>{away}</b> ({date} {time})\n\n"
                f"Выбери победителя чтобы сделать ставку:",
                reply_markup=kb,
                parse_mode="HTML"
            )
        return

    # Есть активный матч
    home = live["home"]
    away = live["away"]

    if existing:
        await message.answer(
            f"🎰 <b>Ставки</b>\n\n"
            f"💰 Твой баланс: <b>{user['coins']} монет</b>\n\n"
            f"🔴 LIVE: <b>{home}</b> vs <b>{away}</b>\n\n"
            f"✅ Твоя ставка: <b>{existing['pick']}</b> — {existing['amount']} монет\n"
            f"Ждём результата матча!",
            parse_mode="HTML"
        )
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"🔵 {home}", callback_data=f"bet_live|{home}|{away}|{home}"),
            InlineKeyboardButton(text=f"🔴 {away}", callback_data=f"bet_live|{home}|{away}|{away}"),
        ],
        [InlineKeyboardButton(text="🤝 Ничья", callback_data=f"bet_live|{home}|{away}|draw")]
    ])
    await message.answer(
        f"🎰 <b>Ставки</b>\n\n"
        f"💰 Твой баланс: <b>{user['coins']} монет</b>\n\n"
        f"🔴 LIVE матч: <b>{home}</b> vs <b>{away}</b>\n\n"
        f"На кого ставишь? Выигрыш x2 от ставки!",
        reply_markup=kb,
        parse_mode="HTML"
    )

# -------------------------
# 🎰 ВЫБОР СУММЫ СТАВКИ
# -------------------------

@dp.callback_query(F.data.startswith("bet_live|") | F.data.startswith("bet_pre|"))
async def bet_choose_amount(callback: CallbackQuery):
    data = load()
    uid = str(callback.from_user.id)
    user = get_user(data, uid)
    save(data)

    parts = callback.data.split("|")
    bet_type = parts[0]   # bet_live или bet_pre
    home = parts[1]
    away = parts[2]
    pick = parts[3]

    pick_label = pick if pick != "draw" else "Ничья"
    coins = user["coins"]

    if coins <= 0:
        await callback.answer("У тебя нет монет для ставки! 😢", show_alert=True)
        return

    # Кнопки с суммами (10%, 25%, 50%, всё)
    amounts = []
    for pct, label in [(10, "10%"), (25, "25%"), (50, "50%"), (100, "Всё")]:
        amount = max(1, int(coins * pct / 100))
        amounts.append(
            InlineKeyboardButton(
                text=f"{label} ({amount})",
                callback_data=f"bet_confirm|{bet_type}|{home}|{away}|{pick}|{amount}"
            )
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [amounts[0], amounts[1]],
        [amounts[2], amounts[3]],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="bet_cancel")]
    ])

    await callback.message.edit_text(
        f"🎯 Ставка на: <b>{pick_label}</b>\n"
        f"💰 Баланс: <b>{coins} монет</b>\n\n"
        f"Выбери сумму ставки:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()

# -------------------------
# 🎰 ПОДТВЕРЖДЕНИЕ СТАВКИ
# -------------------------

@dp.callback_query(F.data.startswith("bet_confirm|"))
async def bet_confirm(callback: CallbackQuery):
    data = load()
    uid = str(callback.from_user.id)
    user = get_user(data, uid)

    parts = callback.data.split("|")
    # bet_confirm|bet_type|home|away|pick|amount
    home = parts[2]
    away = parts[3]
    pick = parts[4]
    amount = int(parts[5])

    if user["coins"] < amount:
        await callback.answer("Недостаточно монет!", show_alert=True)
        return

    # Проверяем нет ли уже ставки
    existing = next((b for b in data["open_bets"] if str(b["user_id"]) == uid), None)
    if existing:
        await callback.answer("Ты уже сделал ставку на этот матч!", show_alert=True)
        return

    # Списываем монеты и сохраняем ставку
    user["coins"] -= amount
    pick_label = pick if pick != "draw" else "Ничья"

    data["open_bets"].append({
        "user_id": uid,
        "home": home,
        "away": away,
        "pick": pick,
        "amount": amount
    })
    save(data)

    potential = int(amount * BET_WIN_MULTIPLIER)
    await callback.message.edit_text(
        f"✅ <b>Ставка принята!</b>\n\n"
        f"⚽ Матч: <b>{home}</b> vs <b>{away}</b>\n"
        f"🎯 Ставка на: <b>{pick_label}</b>\n"
        f"💸 Поставлено: <b>{amount} монет</b>\n"
        f"🏆 При выигрыше получишь: <b>{potential} монет</b>\n\n"
        f"💰 Остаток: <b>{user['coins']} монет</b>",
        parse_mode="HTML"
    )
    await callback.answer("Ставка сделана! 🎰")

@dp.callback_query(F.data == "bet_cancel")
async def bet_cancel(callback: CallbackQuery):
    await callback.message.edit_text("❌ Ставка отменена.")
    await callback.answer()

# -------------------------
# 💰 МОЙ БАЛАНС
# -------------------------

@dp.message(F.text == "💰 Мой баланс")
async def my_balance(message: Message):
    data = load()
    uid = str(message.from_user.id)
    user = get_user(data, uid)
    save(data)

    bets = user.get("bets", [])
    wins = sum(1 for b in bets if b.get("result") == "win")
    losses = sum(1 for b in bets if b.get("result") == "loss")

    # Текущая открытая ставка
    open_bet = next((b for b in data["open_bets"] if str(b["user_id"]) == uid), None)

    text = (
        f"💰 <b>Твой профиль</b>\n\n"
        f"🪙 Баланс: <b>{user['coins']} монет</b>\n"
        f"✅ Выигрышей: <b>{wins}</b>\n"
        f"❌ Проигрышей: <b>{losses}</b>\n"
        f"📊 Всего ставок: <b>{len(bets)}</b>\n"
    )

    if open_bet:
        pick_label = open_bet["pick"] if open_bet["pick"] != "draw" else "Ничья"
        text += (
            f"\n⏳ <b>Активная ставка:</b>\n"
            f"  {open_bet['home']} vs {open_bet['away']}\n"
            f"  Ставка на: {pick_label} — {open_bet['amount']} монет\n"
        )

    if bets:
        text += "\n📜 <b>Последние ставки:</b>\n"
        for b in reversed(bets[-5:]):
            icon = "✅" if b.get("result") == "win" else "❌"
            pick_label = b["pick"] if b["pick"] != "draw" else "Ничья"
            text += f"  {icon} {b['home']} vs {b['away']} → {pick_label} ({b['amount']} монет)\n"

    await message.answer(text, parse_mode="HTML")

# -------------------------
# 🏅 ТОП ИГРОКОВ
# -------------------------

@dp.message(F.text == "🏅 Топ игроков")
async def top_players(message: Message):
    data = load()
    users = data.get("users", {})
    if not users:
        await message.answer("Пока никто не зарегистрирован.")
        return

    sorted_users = sorted(users.items(), key=lambda x: x[1].get("coins", 0), reverse=True)
    text = "🏅 <b>Топ игроков по монетам:</b>\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (uid, u) in enumerate(sorted_users[:10], 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        try:
            chat = await bot.get_chat(int(uid))
            name = chat.first_name or f"User{uid}"
        except:
            name = f"User{uid}"
        text += f"{medal} <b>{name}</b> — {u.get('coins', 0)} монет\n"

    await message.answer(text, parse_mode="HTML")

# -------------------------
# 🔧 ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ: определить победителя по счёту
# -------------------------

def determine_winner(home: str, away: str, score: str) -> str:
    """Возвращает 'home_team', 'away_team' или 'draw'."""
    try:
        parts = score.split(":")
        h_goals = int(parts[0].strip())
        a_goals = int(parts[1].strip())
        if h_goals > a_goals:
            return home
        elif a_goals > h_goals:
            return away
        else:
            return "draw"
    except:
        return "unknown"

# -------------------------
# 🔥 РАСЧЁТ СТАВОК (вызывается при /stoplive)
# -------------------------

async def settle_bets(home: str, away: str, score: str):
    """Рассчитываем все открытые ставки на матч."""
    data = load()
    winner = determine_winner(home, away, score)
    remaining_bets = []
    results = []

    for bet in data["open_bets"]:
        if bet["home"] != home or bet["away"] != away:
            remaining_bets.append(bet)
            continue

        uid = str(bet["user_id"])
        user = get_user(data, uid)
        pick = bet["pick"]
        amount = bet["amount"]
        pick_label = pick if pick != "draw" else "Ничья"

        if winner == "unknown":
            # Не смогли определить — возвращаем деньги
            user["coins"] += amount
            result = "refund"
            result_text = f"🔄 Ставка возвращена ({amount} монет)"
        elif (pick == winner) or (pick == "draw" and winner == "draw"):
            winnings = int(amount * BET_WIN_MULTIPLIER)
            user["coins"] += winnings
            result = "win"
            result_text = f"✅ Выигрыш! +{winnings} монет 🎉"
        else:
            result = "loss"
            result_text = f"❌ Проигрыш. -{amount} монет"

        # Добавляем в историю
        user["bets"].append({
            "home": home,
            "away": away,
            "pick": pick,
            "amount": amount,
            "result": result
        })
        results.append((uid, pick_label, result_text, user["coins"]))

    data["open_bets"] = remaining_bets
    save(data)

    # Уведомляем каждого игрока о результате его ставки
    for uid, pick_label, result_text, new_balance in results:
        try:
            await bot.send_message(
                int(uid),
                f"🏁 <b>Матч завершён: {home} {score} {away}</b>\n\n"
                f"Твоя ставка: <b>{pick_label}</b>\n"
                f"{result_text}\n"
                f"💰 Баланс: <b>{new_balance} монет</b>",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Ошибка уведомления {uid}: {e}")

# -------------------------
# 👑 ADMIN КОМАНДЫ
# -------------------------

@dp.message(Command("admin"))
async def admin_info(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Открыть админ-панель", url=f"{SITE_URL}/admin")]
    ])
    await message.answer(
        "👑 <b>Панель администратора</b>\n\n"
        "Команды бота:\n\n"
        "/live Команда1|2:1|Команда2|Кто забил\n"
        "/stoplive — завершить матч + расчёт ставок\n"
        "/startmatch Команда1|Команда2\n"
        "/notify Текст уведомления\n"
        "/addcoins USER_ID|сумма — добавить монеты\n"
        "/resetbets — сбросить все открытые ставки",
        reply_markup=kb,
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
    await message.answer(f"✅ Live обновлён!\n{notify_text}", parse_mode="HTML")

@dp.message(Command("stoplive"))
async def cmd_stoplive(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    data = load()
    live = data.get("live_match")
    if not live:
        await message.answer("⚠️ Нет активного матча")
        return

    home = live["home"]
    away = live["away"]
    score = live["score"]

    data["matches"].append({
        "home": home,
        "away": away,
        "score": score,
        "scorers": live.get("scorers", "")
    })
    data["live_match"] = None
    save(data)

    # Рассчитываем ставки
    await settle_bets(home, away, score)

    notify_text = f"🏁 <b>Матч завершён!</b>\n⚽ {home} <b>{score}</b> {away}"
    await notify_all(notify_text)
    await message.answer("✅ Матч завершён, ставки рассчитаны!", parse_mode="HTML")

@dp.message(Command("startmatch"))
async def cmd_startmatch(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.replace("/startmatch", "").strip()
    parts = [p.strip() for p in args.split("|")]
    if len(parts) < 2:
        await message.answer("Формат: /startmatch Команда1|Команда2")
        return
    notify_text = f"⚽ <b>Матч начинается!</b>\n🆚 {parts[0]} vs {parts[1]}\n\nДелай ставки через кнопку 🎰 Ставки!"
    await notify_all(notify_text)
    await message.answer(f"✅ Уведомление отправлено!\n{notify_text}", parse_mode="HTML")

@dp.message(Command("notify"))
async def cmd_notify(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.replace("/notify", "").strip()
    if not text:
        await message.answer("Формат: /notify Текст")
        return
    await notify_all(f"📣 <b>Объявление:</b>\n\n{text}")
    await message.answer("✅ Уведомление отправлено!")

@dp.message(Command("addcoins"))
async def cmd_addcoins(message: Message):
    """Добавить монеты пользователю: /addcoins USER_ID|сумма"""
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.replace("/addcoins", "").strip()
    parts = [p.strip() for p in args.split("|")]
    if len(parts) < 2:
        await message.answer("Формат: /addcoins USER_ID|сумма")
        return
    try:
        uid = parts[0]
        amount = int(parts[1])
        data = load()
        user = get_user(data, uid)
        user["coins"] += amount
        save(data)
        await message.answer(f"✅ Пользователю {uid} добавлено {amount} монет. Баланс: {user['coins']}")
        try:
            await bot.send_message(int(uid), f"🎁 Тебе начислено <b>{amount} монет</b>!\n💰 Баланс: <b>{user['coins']}</b>", parse_mode="HTML")
        except:
            pass
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

@dp.message(Command("resetbets"))
async def cmd_resetbets(message: Message):
    """Сбросить все открытые ставки (возврат монет)."""
    if message.from_user.id != ADMIN_ID:
        return
    data = load()
    for bet in data["open_bets"]:
        uid = str(bet["user_id"])
        user = get_user(data, uid)
        user["coins"] += bet["amount"]
    count = len(data["open_bets"])
    data["open_bets"] = []
    save(data)
    await message.answer(f"✅ Сброшено {count} ставок, монеты возвращены.")

# -------------------------
# 🔥 СТАРТ
# -------------------------

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())