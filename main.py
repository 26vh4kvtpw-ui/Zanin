import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = '7746320533:AAHsQngCsZW-VyhQoU7akrZHsO8CY2Tl1-o'
bot = telebot.TeleBot(TOKEN)

def get_tiktok_video(url):
    # Очищаем ссылку от лишнего мусора, если он есть
    clean_url = url.split('?')[0]
    api_url = f"https://api.tiklydown.eu.org/api/download?url={clean_url}"
    
    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        # Проверяем, есть ли видео в ответе
        if 'video' in data and 'noWatermark' in data['video']:
            return data['video']['noWatermark']
        else:
            print(f"API ответил, но видео нет: {data}") # Увидишь в логах Render
            return None
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")
        return None


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
