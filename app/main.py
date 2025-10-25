import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from handlers import user, lob
from lexicon.lexicon import LEXICON_MENU
from config.config import config

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in LEXICON_MENU.items()
    ]
    await bot.set_my_commands(main_menu_commands)


async def main():    
    # initialize bot and dispatcher
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    # dp.message.middleware(AccessMiddleware())

    # main menu
    await set_main_menu(bot)

    # register routers
    dp.include_router(user.router)
    dp.include_router(lob.router)

    # skip the accumulated updates and launch polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)    
    logging.info("Starting LOB TG BOT")


if __name__ == "__main__":
    asyncio.run(main())


