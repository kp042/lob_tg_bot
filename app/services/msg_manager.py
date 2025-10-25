import os
import logging
import asyncio
from aiogram import Bot
from aiogram.types import FSInputFile
from core.config import config
from core.app_context import app_context

# load bot
# bot = Bot(token=config.tg_bot.token)


async def send_image(chat_id, image_filename, msg):    
    if not os.path.exists(image_filename):
        logging.error(f"File {filename} not found!")
        await send_msg(chat_id, "Ошибка: изображение не сгенерировано.")
        return
    try:
        # image_path = os.path.join(tgbot_dir, image_filename)
        # photo = FSInputFile(image_path)
        photo = FSInputFile(image_filename)
        await app_context.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=msg,
            request_timeout=30  # Увеличиваем таймаут
        )        
    except Exception as e:
        logging.error(f"Send image error: {e}")
        await asyncio.sleep(5)
        await app_context.bot.send_photo(chat_id=chat_id, photo=photo, caption=msg)
    finally:
        os.remove(image_filename)


async def send_msg(chat_id, msg):
    try:
        await app_context.bot.send_message(
            chat_id=chat_id,
            text=str(msg),
            request_timeout=15
        )
    except Exception as e:
        logging.error(f"Send message error: {e}")
        await asyncio.sleep(3)
        await app_context.bot.send_message(chat_id=chat_id, text=str(msg))