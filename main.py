import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- НАСТРОЙКИ ---
TOKEN = '7746320533:AAES6Psnh9SVYYGGrlmN5ij0KHkJb4OX9Kg'
bot = telebot.TeleBot(TOKEN)

# --- ФУНКЦИЯ СКАТЫВАНИЯ ---
def get_video_url(url):
    # Очищаем входящую ссылку от лишнего мусора
    url = url.strip().split('?')[0]
    
    # Список API сервисов для скачивания
    apis = [
        f"https://www.tikwm.com/api/?url={url}",
        f"https://api.tiklydown.eu.org/api/download?url={url}",
        f"https://api.douyin.wtf/api/tiktok/info?url={url}"
    ]
    
    for api in apis:
        try:
            r = requests.get(api, timeout=10)
            if r.status_code == 200:
                data = r.json()
                video_link = None
                
                # Логика извлечения ссылки зависит от API
                if 'tikwm.com' in api:
                    video_link = data.get('data', {}).get('play')
                    if video_link and not video_link.startswith('http'):
                        video_link = "https://www.tikwm.com" + video_link
                elif 'tiklydown' in api:
                    video_link = data.get('video', {}).get('noWatermark')
                else:
                    video_link = data.get('video_data', {}).get('nwm_video_url_HQ')
                
                if video_link:
                    # КЛЮЧЕВОЙ МОМЕНТ: Удаляем порты :443 и :80, чтобы Telegram не выдавал ошибку 400
                    return video_link.replace(':443', '').replace(':80', '')
        except Exception as e:
            print(f"Ошибка при обращении к {api}: {e}")
            continue
    return None

# --- ОБРАБОТЧИКИ КОМАНД ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Пришли мне ссылку на TikTok, и я пришлю тебе видео без водяного знака! 🚀")

@bot.message_handler(func=lambda m: 'tiktok.com' in m.text.lower())
def handle_tiktok(message):
    wait_msg = bot.reply_to(message, "⏳ Начинаю скачивание, подожди немного...")
    
    # Вытаскиваем только саму ссылку из сообщения
    words = message.text.split()
    link_to_download = next((word for word in words if "tiktok.com" in word), None)
    
    if not link_to_download:
        bot.edit_message_text("Не вижу ссылки в сообщении!", message.chat.id, wait_msg.message_id)
        return

    final_url = get_video_url(link_to_download)
    
    if final_url:
        try:
            bot.send_video(message.chat.id, final_url)
            bot.delete_message(message.chat.id, wait_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Ошибка Telegram: {e}", message.chat.id, wait_msg.message_id)
    else:
        bot.edit_message_text("😔 Не удалось получить видео. Попробуй другую ссылку или позже.", message.chat.id, wait_msg.message_id)

# --- ТЕХНИЧЕСКАЯ ЧАСТЬ ДЛЯ RENDER ---
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Live!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), WebServer)
    server.serve_forever()

if name == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    bot.remove_webhook()
    print("DONE! Бот запущен и готов к работе.", flush=True)
    bot.infinity_polling()
