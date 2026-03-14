import telebot
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. Твой токен
TOKEN = '7746320533:AAH2wr3tBIfvM9BUqGgS5XlSm65A6gW7EDw'
bot = telebot.TeleBot(TOKEN)

# 2. Обманка для Render (Web Service требует порт)
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

# 3. ТВОИ КОМАНДЫ (Пример)
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я работаю на Render!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Ты написал: {message.text}")

# 4. ЗАПУСК
if __name__ == "__main__":
    # Запускаем сервер в отдельном потоке
    threading.Thread(target=run_static_server, daemon=True).start()
    
    # Сбрасываем старые зависшие сессии
    bot.remove_webhook()
    
    print("Бот запущен!") # Эта надпись ДОЛЖНА появиться в логах
    
    try:
        bot.infinity_polling(timeout=20, long_polling_timeout=10)
    except Exception as e:
        print(f"Ошибка при работе: {e}")
