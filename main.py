"""
Главный файл запуска бота.
"""
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from config import BOT_TOKEN, ALLOWED_USERS
from handlers.commands import router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def check_access(user_id: int) -> bool:
    """Проверка доступа пользователя."""
    return not ALLOWED_USERS or user_id in ALLOWED_USERS


async def main():
    """Основная функция запуска бота."""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не найден! Проверьте файл .env")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация роутера
    dp.include_router(router)

    logger.info("✅ Бот запущен...")
    logger.info(f"👥 Разрешённые пользователи: {ALLOWED_USERS or 'Все'}")

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    finally:
        await bot.session.close()
        logger.info("👋 Сессия бота закрыта")


if __name__ == "__main__":
    asyncio.run(main())
