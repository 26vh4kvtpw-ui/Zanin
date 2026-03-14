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
    except:
        return True

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Бот обновлен! Теперь использую резервные серверы. Присылай ссылку!")

@bot.message_handler(func=lambda m: 'tiktok.com' in m.text.lower())
def handle_video(message):
    if not is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id, f"❌ Подпишись на {CHANNEL_ID}")
        return

    msg = bot.reply_to(message, "📥 Загружаю оригинал...")
    link = message.text.split()[0]
    video_url = None

    # Попытка №1: TiklyDown
    try:
        res = requests.get(f"https://api.tiklydown.eu.org/api/download?url={link}", timeout=10).json()
        video_url = res.get('video', {}).get('noWatermark')
    except:
        # Попытка №2: TikWM (если первый упал)
        try:
            res = requests.get(f"https://www.tikwm.com/api/?url={link}&hd=1", timeout=10).json()
            video_url = res['data'].get('hdplay') or res['data'].get('play')
            if video_url and not video_url.startswith('http'):
                video_url = "https://www.tikwm.com" + video_url
        except:
            pass

    if video_url:
        try:
            file_path = f"video_{message.chat.id}.mp4"
            r = requests.get(video_url)
            with open(file_path, 'wb') as f:
                f.write(r.content)
            
            # Отправка документом, чтобы не лагал звук
            with open(file_path, 'rb') as video:
                bot.send_document(message.chat.id, video, caption="HD Оригинал 🔥 @ZanimEdits")
            
            os.remove(file_path)
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Ошибка отправки: {e}", message.chat.id, msg.message_id)
    else:
        bot.edit_message_text("😔 Все серверы заняты или ссылка битая. Попробуй еще раз через минуту.", message.chat.id, msg.message_id)

class S(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

def run():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), S).serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
