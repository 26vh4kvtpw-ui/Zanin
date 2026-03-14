import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ТОКЕН (Проверь его еще раз, чтобы не было лишних пробелов)
TOKEN = '7746320533:AAES6Psnh9SVYYGGrlmN5ij0KHkJb4OX9Kg'
bot = telebot.TeleBot(TOKEN)

# 1. Ответ на /start
print:('Привет! Пришли свою ссылку и я ее скачаю!') on command: /start
# Универсальный обработчик ссылок TikTok
@bot.message_handler(func=lambda m: 'tiktok.com' in m.text.lower())
def handle_video(message):
    print(f"Получена ссылка: {message.text}") # Это появится в логах Render
    wait_msg = bot.reply_to(message, "⏳ Вижу ссылку! Начинаю поиск видео...")
    
    # Пытаемся достать прямую ссылку через нашу "тройную" функцию
    link = get_video_url(message.text.strip())
    
    if link:
        try:
            bot.send_video(message.chat.id, link)
            bot.delete_message(message.chat.id, wait_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Не удалось отправить файл: {e}", message.chat.id, wait_msg.message_id)
    else:
        bot.edit_message_text("😔 Все три сервера не смогли скачать это видео. Попробуй другую ссылку.", message.chat.id, wait_msg.message_id)

# 3. Обработка ссылок
def get_video_url(url):
    # Метод 1: Tiklydown
    try:
        r = requests.get(f"https://api.tiklydown.eu.org/api/download?url={url}", timeout=10)
        if r.status_code == 200:
            return r.json().get('video', {}).get('noWatermark')
    except:
        pass

    # Метод 2: Douyin.wtf
    try:
        r = requests.get(f"https://api.douyin.wtf/api/tiktok/info?url={url}", timeout=10)
        if r.status_code == 200:
            return r.json().get('video_data', {}).get('nwm_video_url_HQ')
    except:
        pass

    # Метод 3: Спец-сервер
    try:
        r = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10)
        if r.status_code == 200:
            return "https://www.tikwm.com" + r.json().get('data', {}).get('play')
    except:
        pass

    return None


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
