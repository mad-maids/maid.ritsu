import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.filters.car_in_db import CarInDB
from tgbot.filters.is_private import IsPrivate
from tgbot.filters.search_car import SearchCar
from tgbot.filters.user_in_db import UserInDB
from tgbot.handlers import user_menu
from tgbot.handlers.admin import register_admin
from tgbot.handlers.discussion_room import discussion_handlers
from tgbot.handlers.error import error_handler
from tgbot.handlers.user_menu import user_menu_handlers
from tgbot.handlers.user_registration import user_registration_handlers
from tgbot.handlers.user_settings import user_settings_handlers
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.services.database import create_db_session

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))
    dp.setup_middleware(ThrottlingMiddleware())


def register_all_filters(dp):
    # dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(IsPrivate)
    dp.filters_factory.bind(UserInDB)
    dp.filters_factory.bind(CarInDB)
    dp.filters_factory.bind(SearchCar)


def register_all_handlers(dp):
    error_handler(dp)
    # register_admin(dp)
    user_registration_handlers(dp)
    user_menu_handlers(dp)
    user_settings_handlers(dp)
    discussion_handlers(dp)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("restart", "- Restart the bot"),
        types.BotCommand("help", "- Instructions"),
        types.BotCommand("finish", "- Finish the discussion")
    ])


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config
    bot['db'] = await create_db_session(config)

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)
    await set_default_commands(dp)
    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
