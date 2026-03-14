import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = '7746320533:AAES6Psnh9SVYYGGrlmN5ij0KHkJb4OX9Kg'
CHANNEL_ID = '@ZanimEdits'
bot = telebot.TeleBot(TOKEN)

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"ОШИБКА ПРОВЕРКИ: {e}")
        # Если бот не админ, он выдаст ошибку сюда
        return False 

def get_video_hd(url):
    # Используем мощный сервер Loovit для HD качества
    api_url = f"https://api.tikwm.com/api/?url={url}&hd=1" 
    try:
        r = requests.get(api_url, timeout=15)
        res = r.json()
        if res.get('code') == 0:
            # Пробуем взять HD, если нет - обычное
            video = res['data'].get('hdplay') or res['data'].get('play')
            if video:
                if not video.startswith('http'):
                    video = "https://www.tikwm.com" + video
                return video.replace(':443', '')
    except:
        pass
    return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"🔥 Бот готов! Чтобы качать в HD, подпишись на {CHANNEL_ID}")

@bot.message_handler(func=lambda m: 'tiktok.com' in m.text.lower())
def handle(message):
    if not is_subscribed(message.from_user.id):
        bot.reply_to(message, f"❌ Доступ закрыт! Подпишись на канал {CHANNEL_ID}, чтобы качать видео.")
        return

    wait = bot.reply_to(message, "🚀 Качаю в HD качестве... подожди немного.")
    video_url = get_video_hd(message.text.split()[0])
    
    if video_url:
        try:
            bot.send_video(message.chat.id, video_url, caption="Готово! @ZanimEdits")
            bot.delete_message(message.chat.id, wait.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Ошибка отправки HD: {e}", message.chat.id, wait.message_id)
    else:
        bot.edit_message_text("😔 Видео не найдено или сервер перегружен.", message.chat.id, wait.message_id)

# Мини-сервер для Render
class Web(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

def run():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), Web).serve_forever()

threading.Thread(target=run, daemon=True).start()
bot.remove_webhook()
bot.infinity_polling()
