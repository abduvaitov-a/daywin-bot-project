from datetime import datetime
from database.db import cursor, conn


async def send_morning_notification(bot):
    cursor.execute("SELECT user_id FROM notifications")
    users = cursor.fetchall()

    for user in users:
        user_id = user[0]
        try:
            await bot.send_message(
                user_id,
                "☀️ Доброе утро!\n\n"
                "Сегодня отличный день чтобы стать лучше 🚀"
            )
        except Exception as e:
            print(e)


async def send_evening_notification(bot):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    cursor.execute("""
        SELECT id, user_id, habit_name, total_days, start_date
        FROM habits
        WHERE status = 'active'
    """)
    habits = cursor.fetchall()

    for habit in habits:
        habit_id, user_id, habit_name, total_days, start_date = habit
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            today = datetime.now()
            passed_days = (today - start).days

            if passed_days >= total_days:
                cursor.execute(
                    "UPDATE habits SET status = 'completed' WHERE id = ?",
                    (habit_id,)
                )
                conn.commit()
                await bot.send_message(
                    user_id,
                    f"🏆 Достижение получено!\n\n🔥 {habit_name}"
                )
                continue

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Выполнил", callback_data=f"success_{habit_id}")],
                    [InlineKeyboardButton(text="❌ Не выполнил", callback_data=f"fail_{habit_id}")]
                ]
            )

            await bot.send_message(
                user_id,
                f"🌙 Вечерний отчёт DAYWIN\n\n🔥 {habit_name}\n\nТы выполнил привычку сегодня?",
                reply_markup=keyboard
            )
        except Exception as e:
            print(e)