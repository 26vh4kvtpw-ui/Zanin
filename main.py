import telebot
import requests
from threading import Thread
from flask import Flask # Нужно добавить Flask, чтобы Render не ругался

# Веб-сервер для "обмана" Render
app = Flask('')
@app.route('/')
def home():
    return "I'm alive"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# --- ТВОЙ КОД БОТА ---
TOKEN = '7746320533:AAH2wr3tBIfvM9BUqGgS5XlSm65A6gW7EDw'
bot = telebot.TeleBot(TOKEN)

def get_tiktok_video(url):
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        res = requests.get(api_url).json()
        return res['data'].get('play')
    except:
        return None

@bot.message_handler(func=lambda m: "tiktok.com" in m.text)
def download(message):
    link = get_tiktok_video(message.text)
    if link:
        bot.send_video(message.chat.id, link)
    else:
        bot.send_message(message.chat.id, "Ошибка скачивания")

# Запуск
if __name__ == "__main__":
    # Запускаем веб-сервер в отдельном потоке
    Thread(target=run_web).start()
    import time

# ... твой остальной код ...

if __name__ == "__main__":
    while True:
        try:
            print("Бот запускается...")
            # infinity_polling сам умеет переподключаться
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            print(f"Ошибка: {e}")
            # Если возник конфликт (409), ждем 5 секунд и пробуем снова
            time.sleep(5)

