from flask import Flask, request, jsonify, send_from_directory
import os
import json
import threading
import asyncio
from bot import dp, bot, notify_all

app = Flask(__name__, static_folder="static")
DATA_FILE = "data.json"
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "admin123")

def load():
    if not os.path.exists(DATA_FILE):
        return {"teams": {}, "schedule": [], "matches": [], "playoff": [], "rules": "Правила не заданы", "live_match": None, "subscribers": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if "subscribers" not in data:
            data["subscribers"] = []
        return data

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_auth(req):
    return req.headers.get("X-Admin-Secret") == ADMIN_SECRET

# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def home():
    return "⚽ Football Tournament Bot is running!"

@app.route("/admin")
def admin_panel():
    return send_from_directory("static", "admin.html")

@app.route("/health")
def health():
    return {"ok": True}

# --- GET DATA ---
@app.route("/api/data")
def get_data():
    return jsonify(load())

# --- TEAMS ---
@app.route("/api/team", methods=["POST"])
def add_team():
    if not check_auth(request): return jsonify({"error": "Unauthorized"}), 401
    name = request.json.get("name", "").strip()
    if not name: return jsonify({"error": "Нет названия"}), 400
    data = load()
    if name in data["teams"]: return jsonify({"error": "Команда уже существует"}), 400
    data["teams"][name] = {"players": []}
    save(data)
    return jsonify({"ok": True})

@app.route("/api/team/<name>", methods=["DELETE"])
def delete_team(name):
    if not check_auth(request): return jsonify({"error": "Unauthorized"}), 401
    data = load()
    if name in data["teams"]:
        del data["teams"][name]
        save(data)
    return jsonify({"ok": True})

# --- PLAYERS ---
@app.route("/api/player", methods=["POST"])
def add_player():
    if not check_auth(request): return jsonify({"error": "Unauthorized"}), 401
    team = request.json.get("team", "").strip()
    player = request.json.get("player", "").strip()
    if not team or not player: return jsonify({"error": "Нет данных"}), 400
    data = load()
    if team not in data["teams"]: return jsonify({"error": "Команда не найдена"}), 400
    data["teams"][team]["players"].append(player)
    save(data)
    return jsonify({"ok": True})

@app.route("/api/player", methods=["DELETE"])
def delete_player():
    if not check_auth(request): return jsonify({"error": "Unauthorized"}), 401
    team = request.json.get("team", "").strip()
    player = request.json.get("player", "").strip()
    data = load()
    if team in data["teams"] and player in data["teams"][team]["players"]:
        data["teams"][team]["players"].remove(player)
        save(data)
    return jsonify({"ok": True})

# --- SCHEDULE ---
@app.route("/api/schedule", methods=["POST"])
def add_schedule():
    if not check_auth(request): return jsonify({"error": "Unauthorized"}), 401
    d = request.json
    match = {"date": d.get("date",""), "time": d.get("time",""), "home": d.get("home",""), "away": d.get("away","")}
    if not match["home"] or not match["away"]: return jsonify({"error": "Нет команд"}), 400
    data = load()
    data["schedule"].append(match)
    save(data)
    return jsonify({"ok": True})

@app.route("/api/schedule/<int:index>", methods=["DELETE"])
def delete_schedule(index):
    if not check_auth(request): return jsonify({"error": "Unauthorized"}), 401
    data = load()
    if 0 <= index < len(data["schedule"]):
        data["schedule"].pop(index)
        save(data)
    return jsonify({"ok": True})

# --- LIVE SCORE ---
@app.route("/api/live", methods=["POST"])
def set_live():
    if not check_auth(request): return jsonify({"error": "Unauthorized"}), 401
    d = request.json
    home = d.get("home","").strip()
    away = d.get("away","").strip()
    score = d.get("score","0:0").strip()
    scorers = d.get("scorers","").strip()
    action = d.get("action","update")

    data = load()

    if action == "stop":
        live = data.get("live_match")
        if live:
            data["matches"].append({"home": live["home"], "away": live["away"], "score": live["score"], "scorers": live.get("scorers","")})
            data["live_match"] = None
            save(data)
            notify_text = f"🏁 <b>Матч завершён!</b>\n⚽ {live['home']} <b>{live['score']}</b> {live['away']}"
            asyncio.run_coroutine_threadsafe(notify_all(notify_text), bot_loop)
        return jsonify({"ok": True})

    if action == "start":
        data["live_match"] = {"home": home, "away": away, "score": "0:0", "scorers": ""}
        save(data)
        notify_text = f"⚽ <b>Матч начинается!</b>\n🆚 <b>{home}</b> vs <b>{away}</b>\nСледи за счётом в боте!"
        asyncio.run_coroutine_threadsafe(notify_all(notify_text), bot_loop)
        return jsonify({"ok": True})

    # update score
    data["live_match"] = {"home": home, "away": away, "score": score, "scorers": scorers}
    save(data)
    notify_text = f"🔴 <b>LIVE обновление!</b>\n⚽ <b>{home} {score} {away}</b>"
    if scorers:
        notify_text += f"\n⚡ {scorers}"
    asyncio.run_coroutine_threadsafe(notify_all(notify_text), bot_loop)
    return jsonify({"ok": True})

# --- PLAYOFF ---
@app.route("/api/playoff", methods=["POST"])
def add_playoff():
    if not check_auth(request): return jsonify({"error": "Unauthorized"}), 401
    d = request.json
    stage = d.get("stage","").strip()
    home = d.get("home","").strip()
    away = d.get("away","").strip()
    if not stage or not home or not away: return jsonify({"error": "Нет данных"}), 400
    data = load()
    found = False
    for s in data["playoff"]:
        if s["stage"] == stage:
            s["matches"].append({"home": home, "away": away, "score": "vs"})
            found = True
            break
    if not found:
        data["playoff"].append({"stage": stage, "matches": [{"home": home, "away": away, "score": "vs"}]})
    save(data)
    return jsonify({"ok": True})

@app.route("/api/playoff/score", methods=["POST"])
def update_playoff_score():
    if not check_auth(request): return jsonify({"error": "Unauthorized"}), 401
    d = request.json
    stage = d.get("stage","")
    idx = d.get("match_index", 0)
    score = d.get("score","")
    winner = d.get("winner","")
    data = load()
    for s in data["playoff"]:
        if s["stage"] == stage and idx < len(s["matches"]):
            s["matches"][idx]["score"] = score
            if winner:
                s["matches"][idx]["winner"] = winner
            break
    save(data)
    return jsonify({"ok": True})

@app.route("/api/playoff/clear", methods=["POST"])
def clear_playoff():
    if not check_auth(request): return jsonify({"error": "Unauthorized"}), 401
    data = load()
    data["playoff"] = []
    save(data)
    return jsonify({"ok": True})

# --- RULES ---
@app.route("/api/rules", methods=["POST"])
def set_rules():
    if not check_auth(request): return jsonify({"error": "Unauthorized"}), 401
    rules = request.json.get("rules","").strip()
    data = load()
    data["rules"] = rules
    save(data)
    return jsonify({"ok": True})

# --- NOTIFY ---
@app.route("/api/notify", methods=["POST"])
def send_notify():
    if not check_auth(request): return jsonify({"error": "Unauthorized"}), 401
    text = request.json.get("text","").strip()
    if not text: return jsonify({"error": "Нет текста"}), 400
    asyncio.run_coroutine_threadsafe(notify_all(f"📣 <b>Объявление:</b>\n\n{text}"), bot_loop)
    return jsonify({"ok": True})

# -------------------------
# BOT LOOP
# -------------------------
bot_loop = None

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

async def main():
    global bot_loop
    bot_loop = asyncio.get_event_loop()
    thread = threading.Thread(target=run_flask, daemon=True)
    thread.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
