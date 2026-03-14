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
    bot.reply_to(message, "🚀 Теперь использую новый метод загрузки. Кидай ссылку!")

@bot.message_handler(func=lambda m: 'tiktok.com' in m.text.lower())
def handle_video(message):
    if not is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id, f"❌ Подпишись на {CHANNEL_ID}")
        return

    msg = bot.reply_to(message, "📥 Загружаю оригинал через новый сервер...")
    link = message.text.split()[0]
    
    try:
        # Используем другое API (TiklyDown)
        api = f"https://api.tiklydown.eu.org/api/download?url={link}"
        res = requests.get(api).json()
        
        # Берем ссылку на видео без водяного знака
        video_url = res.get('video', {}).get('noWatermark')
        
        if video_url:
            file_path = f"video_{message.chat.id}.mp4"
            r = requests.get(video_url)
            with open(file_path, 'wb') as f:
                f.write(r.content)
            
            # ОТПРАВЛЯЕМ КАК ДОКУМЕНТ (чтобы Telegram не трогал звук)
            with open(file_path, 'rb') as video:
                bot.send_document(message.chat.id, video, caption="HD Оригинал (без обработки) 🔥")
            
            os.remove(file_path)
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ Сервер не смог достать это видео.", message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка: {e}", message.chat.id, msg.message_id)

class S(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

def run():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), S).serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
