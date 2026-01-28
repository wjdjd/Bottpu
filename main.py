import os
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
import yt_dlp

# --- SOZLAMALAR ---
# Railway Variables dan tokenni oladi.
# Agar token topilmasa, dastur to'xtaydi.
BOT_TOKEN = os.getenv("8218779955:AAEknXgba_N355QFgINCiAQ6Kf53zFziMg8")

dp = Dispatcher()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# --- INDIKATORLAR ---
STATUS = {
    "search": "🔍 Qidirilmoqda...",
    "download": "⬇️ Yuklab olinmoqda... (Serverga)",
    "upload": "📤 Sizga yuborilmoqda...",
    "error": "❌ Xatolik!"
}

async def download_video(url, message: types.Message):
    msg = await message.answer(STATUS["search"])
    
    # Papka borligini tekshirish
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    # Cookies faylni tekshirish
    cookie_file = 'cookies.txt'
    if not os.path.exists(cookie_file):
        logging.warning("Cookies fayli topilmadi! Bot cookiesiz ishlaydi.")
        cookie_file = None

    # Fayl nomi (ID orqali)
    filename = f"downloads/{message.message_id}.mp4"

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': filename,
        'cookiefile': cookie_file,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        # FFmpeg joylashuvi (Railwayda avtomatik topiladi)
        'merge_output_format': 'mp4',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    try:
        await msg.edit_text(STATUS["download"])
        
        loop = asyncio.get_event_loop()
        # Videoni yuklash jarayoni
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            title = info.get('title', 'Video')
            
            # Agar fayl nomi o'zgargan bo'lsa, aniqlaymiz
            if not os.path.exists(filename):
                filename = ydl.prepare_filename(info)

        # Telegramga jo'natish
        await msg.edit_text(STATUS["upload"])
        
        video_file = FSInputFile(filename)
        caption = f"🎥 <b>{title}</b>\n\n🤖 Bot orqali yuklandi"
        
        await message.answer_video(video=video_file, caption=caption, parse_mode="HTML")
        await msg.delete()

    except Exception as e:
        # Xatolikni logga chiqarish (Siz Railwayda ko'rishingiz uchun)
        logging.error(f"Xatolik yuz berdi: {e}")
        await msg.edit_text(f"{STATUS['error']}\n\nSabab: {str(e)[:100]}")
    
    finally:
        # Serverni tozalash
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Salom! Menga Instagram, TikTok yoki YouTube linkini tashlang.")

@dp.message(F.text)
async def link_handler(message: types.Message):
    url = message.text
    if "http" in url:
        await download_video(url, message)
    else:
        await message.answer("Iltimos, havola (link) yuboring.")

async def main():
    if not BOT_TOKEN:
        print("DIQQAT: BOT_TOKEN Railway Variables bo'limiga kiritilmagan!")
        return
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
