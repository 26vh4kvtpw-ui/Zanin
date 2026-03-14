import telebot
import requests
import os
import threading
import time
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

def download_file(url, filename):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk: f.write(chunk)
        return True
    return False

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Бот готов! Теперь видео будут в оригинальном качестве без лагов звука.")

@bot.message_handler(func=lambda m: 'tiktok.com' in m.text.lower())
def handle_docs(message):
    if not is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id, f"❌ Сначала подпишись на {CHANNEL_ID}")
        return

    status_msg = bot.reply_to(message, "⏳ Скачиваю оригинал без потери качества...")
    link = message.text.split()[0]
    
    try:
        # Получаем ссылку на HD
        api = f"https://www.tikwm.com/api/?url={link}&hd=1"
        data = requests.get(api).json()
        video_url = data['data'].get('hdplay') or data['data'].get('play')
        
        if video_url:
            if not video_url.startswith('http'): video_url = "https://www.tikwm.com" + video_url
            
            # СКАЧИВАЕМ ФАЙЛ НА ДИСК (чтобы звук не отставал)
            file_path = f"video_{message.chat.id}.mp4"
            if download_file(video_url, file_path):
                with open(file_path, 'rb') as video:
                    bot.send_video(message.chat.id, video, caption="HD качество 🔥 @ZanimEdits")
                os.remove(file_path) # Удаляем файл после отправки
                bot.delete_message(message.chat.id, status_msg.message_id)
            else:
                bot.edit_message_text("❌ Ошибка при загрузке файла.", message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ Не удалось найти видео.", message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка: {e}", message.chat.id, status_msg.message_id)

# Сервер для Render
class S(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

def run():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), S).serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
