from flask import Flask
import os
import threading
import asyncio
from bot import dp, bot

app = Flask(__name__)

@app.route("/")
def home():
    return "⚽ Football site is running"

@app.route("/health")
def health():
    return {"ok": True}

def run_bot():
    asyncio.run(bot_main())

async def bot_main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# Запускаем бота в отдельном потоке
thread = threading.Thread(target=run_bot, daemon=True)
thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
