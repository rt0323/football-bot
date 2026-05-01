from flask import Flask
import os
import json

app = Flask(__name__)

DATA_FILE = "data.json"


# -------------------------
# SAFE LOAD (НЕ ПАДАЕТ НИКОГДА)
# -------------------------

def load():
    if not os.path.exists(DATA_FILE):
        return {"status": "ok"}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"status": "broken json"}


# -------------------------
# HOME PAGE
# -------------------------

@app.route("/")
def home():
    return "⚽ Football bot admin is running"


# -------------------------
# HEALTH CHECK (ВАЖНО ДЛЯ RAILWAY)
# -------------------------

@app.route("/health")
def health():
    return {"ok": True}


# -------------------------
# START SERVER (CRITICAL)
# -------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
