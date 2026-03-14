import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = '7746320533:AAHsQngCsZW-VyhQoU7akrZHsO8CY2Tl1-o'
bot = telebot.TeleBot(TOKEN)

# --- 1. ПРИВЕТСТВИЕ ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Присылай свою ссылку и я ее скачаю! 🚀")

# --- 2. ЛОГИКА СКАЧИВАНИЯ ---
def get_tiktok_video(url):
    api_url = f"https://api.douyin.wtf/api/tiktok/info?url={url}"
    try:
        response = requests.get(api_url, timeout=15)
        data = response.json()
        video_url = data.get('video_data', {}).get('nwm_video_url_HQ') or data.get('video_data', {}).get('nwm_video_url')
        return video_url
    except Exception as e:
        print(f"Ошибка API: {e}")
        return None

@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def handle_tiktok(message):
    msg = bot.reply_to(message, "⏳ Пытаюсь достать видео из TikTok...")
    
    # Берем только первое слово (ссылку), чтобы не было ошибок из-за лишнего текста
    raw_url = message.text.split()[0] if ' ' in message.text else message.text
    video_url = get_tiktok_video(raw_url)
    
    if video_url:
        try:
            bot.send_video(message.chat.id, video_url)
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Ошибка отправки: {e}", message.chat.id, msg.message_id)
    else:
        bot.edit_message_text("😔 Не удалось скачать. Проверь, что ссылка рабочая!", message.chat.id, msg.message_id)

# --- 3. ОБМАНКА ДЛЯ RENDER ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_static_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_static_server, daemon=True).start()
    bot.remove_webhook()
    print("Бот запущен!", flush=True)
    bot.infinity_polling()
