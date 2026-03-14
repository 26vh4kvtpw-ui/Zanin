import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = '7746320533:AAHsQngCsZW-VyhQoU7akrZHsO8CY2Tl1-o'
bot = telebot.TeleBot(TOKEN)

# Функция для получения прямой ссылки на видео TikTok
def get_tiktok_video(url):
    api_url = f"https://api.tiklydown.eu.org/api/download?url={url}"
    try:
        response = requests.get(api_url).json()
        # Берем ссылку на видео без водяного знака
        return response['video']['noWatermark']
    except:
        return None

@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def handle_tiktok(message):
    msg = bot.reply_to(message, "Скачиваю видео, подожди...")
    video_url = get_tiktok_video(message.text)
    
    if video_url:
        bot.send_video(message.chat.id, video_url)
        bot.delete_message(message.chat.id, msg.message_id)
    else:
        bot.edit_message_text("Не удалось скачать видео. Проверь ссылку!", message.chat.id, msg.message_id)

# Обманка для Render
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
    print("Бот-скачиватель запущен!", flush=True)
    bot.infinity_polling()
