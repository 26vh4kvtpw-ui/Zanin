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

import time

# Твой основной код (хендлеры и т.д.) должен быть ВЫШЕ этой строки

if __name__ == "__main__":
    print("Бот запускается...")
    while True:
        try:
            # infinity_polling сам перезапускается при разрывах
            # skip_pending=True удалит старые сообщения, чтобы бот не спамил при старте
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception as e:
            # Если видим ошибку 409 (Conflict), просто ждем 5 секунд и пробуем снова
            print(f"Замечен конфликт или ошибка: {e}. Пробую снова через 5 сек...")
            time.sleep(5)


import os
from threading import Thread
from flask import Flask
import time

# --- Твой основной код бота и хендлеры здесь ---

# Создаем мини-сервер для обмана Render
app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    # Render дает порт в переменной окружения PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    # Запускаем "сайт" в отдельном потоке
    keep_alive()
    
    # Запускаем бота с бесконечным циклом
    while True:
        try:
            print("Бот запущен!")
