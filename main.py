import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- НАСТРОЙКИ ---
TOKEN = '7746320533:AAES6Psnh9SVYYGGrlmN5ij0KHkJb4OX9Kg'
bot = telebot.TeleBot(TOKEN)

# Функция для получения видео
def get_video_url(url):
    url = url.strip().split('?')[0]
    # Используем TikWM как основной и самый чистый сервис
    api_url = f"https://www.tikwm.com/api/?url={url}"
    try:
        r = requests.get(api_url, timeout=10)
        if r.status_code == 200:
            res = r.json()
            if 'data' in res and 'play' in res['data']:
                video = res['data']['play']
                if not video.startswith('http'):
                    video = "https://www.tikwm.com" + video
                # Убираем порт, чтобы Telegram не ругался (ошибка 400)
                return video.replace(':443', '').replace(':80', '')
    except:
        pass
    return None

# Приветствие
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, "Привет! Просто пришли ссылку на TikTok! 🚀")

# Обработка ссылок
@bot.message_handler(func=lambda m: 'tiktok.com' in m.text.lower())
def handle_link(message):
    msg = bot.reply_to(message, "⏳ Минутку, качаю...")
    # Берем первое слово (ссылку)
    link = message.text.split()[0]
    video_url = get_video_url(link)
    
    if video_url:
        try:
            bot.send_video(message.chat.id, video_url)
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Ошибка Telegram: {e}", message.chat.id, msg.message_id)
    else:
        bot.edit_message_text("😔 Не вышло. Попробуй другую ссылку.", message.chat.id, msg.message_id)

# Технический блок для Render (без сложных условий)
class Web(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    p = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', p), Web).serve_forever()

# ЗАПУСК
threading.Thread(target=run_server, daemon=True).start()
bot.remove_webhook()
print("BOT IS READY")
bot.infinity_polling()
