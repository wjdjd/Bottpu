import os
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile
import yt_dlp

# --- ENG MUHIM JOYI ---
# Tokenni shu yerga yozing. Bo'sh joylar qolmasin!
BOT_TOKEN = "8218779955:AAEknXgba_N355QFgINCiAQ6Kf53zFziMg8"
# ----------------------

dp = Dispatcher()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def download_video(url, message: types.Message):
    msg = await message.answer("🔍 Qidirilmoqda...")
    
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    # Cookies fayl borligini tekshirish
    cookie_file = 'cookies.txt' if os.path.exists('cookies.txt') else None

        ydl_opts = {
        'format': 'best[ext=mp4]',  # O'ZGARTIRILDI
        'outtmpl': f"downloads/{message.message_id}.mp4",
        'cookiefile': cookie_file,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 ... (davomi o\'sha)',
    }

    try:
        await msg.edit_text("⬇️ Yuklanmoqda...")
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)

        await msg.edit_text("📤 Yuborilmoqda...")
        video = FSInputFile(filename)
        await message.answer_video(video, caption="✅ @BotNomi")
        await msg.delete()
        
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await msg.edit_text(f"❌ Xatolik: {e}")
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

@dp.message(F.text)
async def run_bot(message: types.Message):
    if message.text == "/start":
        await message.answer("Salom! Link yuboring.")
    elif "http" in message.text:
        await download_video(message.text, message)
    else:
        await message.answer("Iltimos, havola yuboring.")

async def main():
    print("Bot ishga tushmoqda...")
    # Token tekshiruvi yo'q, to'g'ridan-to'g'ri ulaymiz
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

