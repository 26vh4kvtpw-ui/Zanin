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

import os
import threading
import http.server
import socketserver

def run_static_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    # Запускаем фальшивый сервер в отдельном потоке для Render
    threading.Thread(target=run_static_server, daemon=True).start()
    
    while True:
        try:
            print("Бот запущен!")
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            print(f"Ошибка: {e}")
            import time
            time.sleep(5)
if __name__ == "__main__":
    # 1. Запускаем "обманку" для Render
    threading.Thread(target=run_static_server, daemon=True).start()
    
    # 2. СБРАСЫВАЕМ ЗАВИСШИЕ СОЕДИНЕНИЯ (Добавь эту строку!)
    bot.remove_webhook() 
    
    # 3. Запускаем самого бота
    while True:
        try:
            print("Бот запущен!")
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            print(f"Ошибка: {e}")
            import time
            time.sleep(5)
