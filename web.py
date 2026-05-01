from flask import Flask, request, redirect
import json

app = Flask(__name__)

DATA_FILE = "data.json"


def load():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -------------------------
# 🏠 UI
# -------------------------

@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Турнир</title>

<style>
body {background:#0f172a;color:white;font-family:Arial;text-align:center;}
.box {background:#1f2937;margin:10px;padding:15px;border-radius:10px;}
input,button{padding:10px;margin:5px;border-radius:8px;border:none;}
button{background:#22c55e;}
</style>
</head>

<body>

<h2>⚽ Админка турнира</h2>

<div class="box">
<h3>➕ Команда</h3>
<form action="/add_team" method="post">
<input name="team">
<button>Добавить</button>
</form>
</div>

<div class="box">
<h3>👤 Игрок</h3>
<form action="/add_player" method="post">
<input name="team">
<input name="player">
<button>Добавить</button>
</form>
</div>

<div class="box">
<h3>📅 Расписание</h3>
<form action="/add_schedule" method="post">
<input name="home">
<input name="away">
<input name="time">
<button>Добавить</button>
</form>
</div>

<div class="box">
<h3>⚽ Матч</h3>
<form action="/add_match" method="post">
<input name="home">
<input name="away">
<input name="score">
<button>Добавить</button>
</form>
</div>

<div class="box">
<h3>🏆 Плей-офф</h3>
<form action="/generate_playoff" method="post">
<button>Создать плей-офф</button>
</form>
</div>

</body>
</html>
"""


# -------------------------
# ➕ TEAM
# -------------------------

@app.route("/add_team", methods=["POST"])
def add_team():
    data = load()
    team = request.form["team"]

    if team not in data["teams"]:
        data["teams"][team] = {"pts": 0, "played": 0, "wins": 0}

    save(data)
    return redirect("/")


# -------------------------
# 👤 PLAYER
# -------------------------

@app.route("/add_player", methods=["POST"])
def add_player():
    data = load()
    team = request.form["team"]
    player = request.form["player"]

    if team not in data["players"]:
        data["players"][team] = []

    data["players"][team].append(player)
    save(data)
    return redirect("/")


# -------------------------
# 📅 SCHEDULE
# -------------------------

@app.route("/add_schedule", methods=["POST"])
def add_schedule():
    data = load()

    data["schedule"].append({
        "home": request.form["home"],
        "away": request.form["away"],
        "time": request.form["time"]
    })

    save(data)
    return redirect("/")


# -------------------------
# ⚽ MATCH
# -------------------------

@app.route("/add_match", methods=["POST"])
def add_match():
    data = load()

    home = request.form["home"]
    away = request.form["away"]
    score = request.form["score"]

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

    save(data)
    return redirect("/")


# -------------------------
# 🏆 PLAYOFF
# -------------------------

@app.route("/generate_playoff", methods=["POST"])
def generate_playoff():
    data = load()

    teams = sorted(data["teams"].items(), key=lambda x: x[1]["pts"], reverse=True)
    top4 = [t[0] for t in teams[:4]]

    data["playoff"]["bracket"] = [
        {"home": top4[0], "away": top4[3], "score": None},
        {"home": top4[1], "away": top4[2], "score": None}
    ]

    data["playoff"]["enabled"] = True

    save(data)
    return redirect("/")


# -------------------------
# RUN
# -------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
