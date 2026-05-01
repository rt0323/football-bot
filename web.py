from flask import Flask, request, redirect
import json

app = Flask(__name__)

DATA_FILE = "data.json"

# -------------------------
# 📂 DATA
# -------------------------

def load():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"teams": {}, "matches": [], "schedule": []}

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------------
# 🎨 UI
# -------------------------

def layout(content):
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Футбольная админка</title>

<style>
body {{
    margin: 0;
    font-family: Arial;
    background: #0f172a;
    color: white;
}}

.sidebar {{
    width: 220px;
    height: 100vh;
    position: fixed;
    background: #111827;
    padding: 20px;
}}

.sidebar h2 {{
    color: #22c55e;
}}

.sidebar a {{
    display: block;
    color: white;
    text-decoration: none;
    padding: 10px;
    margin-top: 10px;
    border-radius: 8px;
}}

.sidebar a:hover {{
    background: #1f2937;
}}

.main {{
    margin-left: 240px;
    padding: 20px;
}}

.card {{
    background: #1f2937;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
}}

input {{
    padding: 10px;
    margin: 5px;
    border-radius: 8px;
    border: none;
}}

button {{
    padding: 10px;
    background: #22c55e;
    border: none;
    border-radius: 8px;
    cursor: pointer;
}}

table {{
    width: 100%;
    margin-top: 20px;
    background: #111827;
    border-radius: 10px;
}}

td, th {{
    padding: 10px;
}}
</style>

</head>

<body>

<div class="sidebar">
<h2>⚽ Турнир</h2>
<a href="/">🏠 Главная</a>
</div>

<div class="main">
{content}
</div>

</body>
</html>
"""

# -------------------------
# 🏠 DASHBOARD
# -------------------------

@app.route("/")
def index():
    data = load()

    teams = sorted(data["teams"].items(), key=lambda x: x[1]["pts"], reverse=True)

    content = """
    <h1>📊 Панель управления турниром</h1>

    <div class="card">
    <h3>➕ Добавить команду</h3>
    <form action="/add_team" method="post">
        <input name="team" placeholder="Название команды">
        <button>Добавить</button>
    </form>
    </div>

    <div class="card">
    <h3>⚽ Добавить матч</h3>
    <form action="/add_match" method="post">
        <input name="home" placeholder="Домашняя">
        <input name="away" placeholder="Гостевая">
        <input name="score" placeholder="2:1">
        <button>Добавить</button>
    </form>
    </div>

    <h2>🏆 Таблица</h2>
    <table>
    <tr><th>Команда</th><th>Очки</th><th>Победы</th><th>Игры</th></tr>
    """

    for name, t in teams:
        content += f"""
        <tr>
            <td>{name}</td>
            <td>{t['pts']}</td>
            <td>{t['wins']}</td>
            <td>{t['played']}</td>
        </tr>
        """

    content += "</table>"

    return layout(content)

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
# 🚀 RUN
# -------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
