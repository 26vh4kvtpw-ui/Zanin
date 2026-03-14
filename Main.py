import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- НАСТРОЙКИ ---
TOKEN = '7746320533:AAES6Psnh9SVYYGGrlmN5ij0KHkJb4OX9Kg'
CHANNEL_ID = '@ZanimEdits' # Твой канал
bot = telebot.TeleBot(TOKEN)

# Функция проверки подписки
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        # Если статус не 'left', значит пользователь в канале
        return status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        # Если бота не добавили в админы канала, он может выдавать ошибку
        return True 

def get_video_url(url):
    url = url.strip().split('?')[0]
    api_url = f"https://www.tikwm.com/api/?url={url}"
    try:
        r = requests.get(api_url, timeout=10)
        if r.status_code == 200:
            res = r.json()
            if 'data' in res and 'play' in res['data']:
                video = res['data']['play']
                if not video.startswith('http'):
                    video = "https://www.tikwm.com" + video
                return video.replace(':443', '').replace(':80', '')
    except:
        pass
    return None

# Приветствие
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, "Привет! Просто пришли ссылку на TikTok! 🚀\n\n*Для работы бота нужно быть подписанным на @ZanimEdits*")

# Обработка ссылок
@bot.message_handler(func=lambda m: 'tiktok.com' in m.text.lower())
def handle_link(message):
    # ПРОВЕРКА ПОДПИСКИ
    if not is_subscribed(message.from_user.id):
        bot.reply_to(message, f"❌ Ошибка! Чтобы пользоваться ботом, подпишись на наш канал: {CHANNEL_ID}\n\nПосле подписки просто отправь ссылку снова!")
        return

    msg = bot.reply_to(message, "⏳ Минутку, качаю...")
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

# Технический блок для Render
class Web(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    p = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', p), Web).serve_forever()

threading.Thread(target=run_server, daemon=True).start()
bot.remove_webhook()
print("BOT IS READY WITH SUBSCRIPTION CHECK")
bot.infinity_polling()
