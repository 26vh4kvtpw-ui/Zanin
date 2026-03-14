import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ТОКЕН (Проверь его еще раз, чтобы не было лишних пробелов)
TOKEN = '7746320533:AAES6Psnh9SVYYGGrlmN5ij0KHkJb4OX9Kg'
bot = telebot.TeleBot(TOKEN)

# 1. Ответ на /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Присылай ссылку на TikTok, и я попробую её скачать! 🚀")

# 2. Логика скачивания
def get_video_url(url):
    api_url = f"https://api.douyin.wtf/api/tiktok/info?url={url}"
    try:
        r = requests.get(api_url, timeout=15)
        data = r.json()
        return data.get('video_data', {}).get('nwm_video_url_HQ')
    except:
        return None

# 3. Обработка ссылок
@bot.message_handler(func=lambda m: 'tiktok.com' in m.text)
def handle_video(message):
    wait_msg = bot.reply_to(message, "⏳ Секунду, достаю видео...")
    link = get_video_url(message.text.strip())
    
    if link:
        try:
            bot.send_video(message.chat.id, link)
            bot.delete_message(message.chat.id, wait_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Ошибка при отправке: {e}", message.chat.id, wait_msg.message_id)
    else:
        bot.edit_message_text("😔 Не смог скачать. Попробуй другую ссылку.", message.chat.id, wait_msg.message_id)

# --- Техническая часть для Render ---
class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

def run_web():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), WebHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.remove_webhook()
    print("БОТ ЗАПУЩЕН!", flush=True)
    bot.infinity_polling()
