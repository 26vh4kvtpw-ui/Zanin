import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = '7746320533:AAES6Psnh9SVYYGGrlmN5ij0KHkJb4OX9Kg'
bot = telebot.TeleBot(TOKEN)

def get_video_url(url):
    # Метод 1: Tiklydown
    try:
        r = requests.get(f"https://api.tiklydown.eu.org/api/download?url={url}", timeout=10)
        if r.status_code == 200:
            return r.json().get('video', {}).get('noWatermark')
    except:
        pass
    # Метод 2: TikWM
    try:
        r = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10)
        if r.status_code == 200:
            res = r.json()
            if 'data' in res:
                return "https://www.tikwm.com" + res['data'].get('play')
    except:
        pass
    return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Присылай ссылку на TikTok, и я её скачаю! 🚀")

@bot.message_handler(func=lambda m: 'tiktok.com' in m.text.lower())
def handle_tiktok(message):
    wait = bot.reply_to(message, "⏳ Секунду, пробую скачать...")
    link = get_video_url(message.text.strip())
    if link:
        try:
            bot.send_video(message.chat.id, link)
            bot.delete_message(message.chat.id, wait.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Ошибка отправки: {e}", message.chat.id, wait.message_id)
    else:
        bot.edit_message_text("😔 Не удалось скачать. Возможно, сервера пидорасы.", message.chat.id, wait.message_id)

class Web(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Live")

def run():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), Web).serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    bot.remove_webhook()
    print("DONE", flush=True)
    bot.infinity_polling()


