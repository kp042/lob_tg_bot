import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from handlers import user, lob
from lexicon.lexicon import LEXICON_MENU
from core.config import config
from core.app_context import app_context
from services.api_client import APIClient


logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command=command, description=description)
        for command, description in LEXICON_MENU.items()
    ]
    await bot.set_my_commands(main_menu_commands)


async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=config.TG_BOT_TOKEN)    
    dp = Dispatcher()

    # Initialize API client
    api_client = APIClient(
        base_url=config.API_BASE,
        username=config.API_USER,
        password=config.API_PASS
    )
    
    # Store in app context
    app_context.bot = bot
    app_context.api_client = api_client

    # Set main menu
    await set_main_menu(bot)

    # Register routers
    dp.include_router(user.router)
    dp.include_router(lob.router)

    try:
        # Skip accumulated updates and start polling
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Starting LOB TG BOT")
        await dp.start_polling(bot)
    except Exception as e:
        logging.exception("Bot stopped with error")
    finally:
        # Cleanup
        await api_client.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
