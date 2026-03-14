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
        return False

def get_video(url):
    # Пытаемся через 3 разных API по очереди
    apis = [
        f"https://api.tiklydown.eu.org/api/download?url={url}",
        f"https://www.tikwm.com/api/?url={url}&hd=1",
        f"https://api.douyin.wtf/api/tiktok/info?url={url}"
    ]
    
    for api in apis:
        try:
            r = requests.get(api, timeout=15)
            if r.status_code == 200:
                data = r.json()
                # Логика для разных API
                if 'tiklydown' in api:
                    res = data.get('video', {}).get('noWatermark')
                elif 'tikwm' in api:
                    res = data.get('data', {}).get('play')
                else:
                    res = data.get('video_data', {}).get('nwm_video_url_HQ')
                
                if res:
                    if not res.startswith('http'): res = "https:" + res
                    return res.replace(':443', '')
        except:
            continue
    return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"👋 Привет! Подпишись на {CHANNEL_ID} и скидывай ссылку на TikTok!")

@bot.message_handler(func=lambda m: 'tiktok.com' in m.text.lower())
def handle(message):
    if not is_subscribed(message.from_user.id):
        bot.reply_to(message, f"❌ Подпишись на канал {CHANNEL_ID}, чтобы качать видео!")
        return

    wait = bot.reply_to(message, "⏳ Ищу видео в лучшем качестве...")
    video_url = get_video(message.text.split()[0])
    
    if video_url:
        try:
            bot.send_video(message.chat.id, video_url, caption="Готово! @ZanimEdits")
            bot.delete_message(message.chat.id, wait.message_id)
        except:
            bot.edit_message_text("❌ Ошибка при отправке видео.", message.chat.id, wait.message_id)
    else:
        bot.edit_message_text("😔 Все серверы заняты. Попробуй через минуту или другую ссылку.", message.chat.id, wait.message_id)

class Web(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

def run():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), Web).serve_forever()

threading.Thread(target=run, daemon=True).start()
bot.remove_webhook()
bot.infinity_polling()
