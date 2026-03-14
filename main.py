import telebot
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. Твой токен
TOKEN = '7746320533:AAHsQngCsZW-VyhQoU7akrZHsO8CY2Tl1-o'
bot = telebot.TeleBot(TOKEN)

# 2. Обманка для Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_static_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# 3. Твои обработчики
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Присылай свою ссылку и я ее скачаю!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Ты сказал: {message.text}")

# 4. ЗАПУСК С ЗАЩИТОЙ
if __name__ == "__main__":
    # Сначала запускаем сервер-заглушку, чтобы Render был доволен
    threading.Thread(target=run_static_server, daemon=True).start()
    
    print("Ждем 15 секунд, чтобы убить старые копии...", flush=True)
    time.sleep(15) # Даем Telegram время «забыть» старого бота
    
    bot.remove_webhook()
    print("Бот запущен и готов к работе!", flush=True)
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            print(f"Ошибка: {e}", flush=True)
            time.sleep(5)
