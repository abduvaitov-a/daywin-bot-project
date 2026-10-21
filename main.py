import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.config import BOT_TOKEN
from database.db import create_tables
from handlers.user_handlers import router
from services.scheduler import send_morning_notification, send_evening_notification


async def main():
    create_tables()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    scheduler = AsyncIOScheduler()

    dp.include_router(router)

    print("🔥 DAYWIN STARTED 🔥")

    await bot.set_my_commands([BotCommand(command="start", description="🔥 DAYWIN")])

    scheduler.add_job(send_morning_notification, "cron", hour=8, minute=0, args=[bot])
    scheduler.add_job(send_evening_notification, "cron", hour=22, minute=0, args=[bot])
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())