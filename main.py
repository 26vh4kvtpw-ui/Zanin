import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# ТОКЕН, который ты получил у @BotFather
API_TOKEN = '7746320533:AAH2wr3tBIfvM9BUqGgS5XlSm65A6gW7EDw'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для получения прямой ссылки на видео без водяного знака
def get_tiktok_video(url):
    api_url = f"https://www.tikwm.com/api/?url={url}"
    response = requests.get(api_url).json()
    if response.get('data'):
        # Возвращаем ссылку на видео высокого качества (hdplay или play)
        return response['data'].get('hdplay') or response['data'].get('play')
    return None

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Пришли мне ссылку на видео из TikTok, и я скачаю его без водяного знака. 😎")

@dp.message(F.text.contains("tiktok.com"))
async def handle_tiktok(message: types.Message):
    wait_msg = await message.answer("⏳ Обрабатываю видео, подожди немного...")
    
    video_url = get_tiktok_video(message.text)
    
    if video_url:
        await bot.send_video(message.chat.id, video=video_url, caption="Готово! Держи видео без знака.")
        await wait_msg.delete()
    else:
        await wait_msg.edit_text("❌ Не удалось скачать видео. Проверь ссылку.")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
