from flask import Flask, request, redirect
import json
import os

app = Flask(__name__)

DATA_FILE = "data.json"


def load():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"teams": {}, "players": {}, "matches": [], "schedule": []}


def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -------------------------
# HOME
# -------------------------

@app.route("/")
def index():
    return "⚽ Football Admin is running"


# -------------------------
# RUN (ВАЖНО ДЛЯ RAILWAY)
# -------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
