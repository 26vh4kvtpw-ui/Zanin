import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Настройки
TOKEN = '7746320533:AAES6Psnh9SVYYGGrlmN5ij0KHkJb4OX9Kg'
CHANNEL_ID = '@ZanimEdits'
bot = telebot.TeleBot(TOKEN)

# Проверка подписки
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# Получение видео в HD
def get_video(url):
    api_url = f"https://www.tikwm.com/api/?url={url}&hd=1"
    try:
        r = requests.get(api_url, timeout=15)
        data = r.json()
        if data.get('code') == 0:
            res = data['data'].get('hdplay') or data['data'].get('play')
            if res:
                if not res.startswith('http'): res = "https://www.tikwm.com" + res
                return res.replace(':443', '')
    except:
        pass
    return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"👋 Привет! Подпишись на {CHANNEL_ID} и присылай ссылку на TikTok!")

@bot.message_handler(func=lambda m: 'tiktok.com' in m.text.lower())
def handle(message):
    if not is_subscribed(message.from_user.id):
        bot.reply_to(message, f"❌ Ошибка! Сначала подпишись на канал: {CHANNEL_ID}")
        return

    wait = bot.reply_to(message, "⏳ Скачиваю в HD качестве...")
    video_url = get_video(message.text.split()[0])
    
    if video_url:
        try:
            bot.send_video(message.chat.id, video_url, caption="Готово! @ZanimEdits")
            bot.delete_message(message.chat.id, wait.message_id)
        except:
            bot.edit_message_text("❌ Ошибка отправки видео.", message.chat.id, wait.message_id)
    else:
        bot.edit_message_text("😔 Видео не найдено. Попробуй другую ссылку.", message.chat.id, wait.message_id)

# Сервер для Render
class Web(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

def run():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), Web).serve_forever()

# Запуск без сложных условий
threading.Thread(target=run, daemon=True).start()
bot.remove_webhook()
print("BOT STARTED")
bot.infinity_polling()
