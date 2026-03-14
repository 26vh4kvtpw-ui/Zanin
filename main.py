import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- НАСТРОЙКИ ---
TOKEN = '7746320533:AAES6Psnh9SVYYGGrlmN5ij0KHkJb4OX9Kg'
bot = telebot.TeleBot(TOKEN)

def get_video_url(url):
    url = url.strip().split('?')[0]
    apis = [
        f"https://www.tikwm.com/api/?url={url}",
        f"https://api.tiklydown.eu.org/api/download?url={url}"
    ]
    for api in apis:
        try:
            r = requests.get(api, timeout=10)
            if r.status_code == 200:
                data = r.json()
                video_link = None
                if 'tikwm.com' in api:
                    video_link = data.get('data', {}).get('play')
                    if video_link and not video_link.startswith('http'):
                        video_link = "https://www.tikwm.com" + video_link
                else:
                    video_link = data.get('video', {}).get('noWatermark')
                
                if video_link:
                    return video_link.replace(':443', '').replace(':80', '')
        except:
            continue
    return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Пришли ссылку на TikTok, и я скачаю видео без водяного знака! 🚀")

@bot.message_handler(func=lambda m: 'tiktok.com' in m.text.lower())
def handle_tiktok(message):
    wait_msg = bot.reply_to(message, "⏳ Скачиваю видео...")
    links = [word for word in message.text.split() if "tiktok.com" in word]
    if not links:
        bot.edit_message_text("Не вижу ссылки!", message.chat.id, wait_msg.message_id)
        return

    final_url = get_video_url(links[0])
    if final_url:
        try:
            bot.send_video(message.chat.id, final_url)
            bot.delete_message(message.chat.id, wait_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Ошибка: {e}", message.chat.id, wait_msg.message_id)
    else:
        bot.edit_message_text("😔 Не удалось найти видео.", message.chat.id, wait_msg.message_id)

class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Live")

def run():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), WebServer).serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    bot.remove_webhook()
    print("DONE", flush=True)
    bot.infinity_polling()
