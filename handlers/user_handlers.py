from datetime import datetime
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import cursor, conn

router = Router()

class HabitState(StatesGroup):
    waiting_for_habit_name = State()
    waiting_for_custom_days = State()
    waiting_for_morning_time = State()
    waiting_for_evening_time = State()

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить привычку", callback_data="create_habit")],
            [InlineKeyboardButton(text="📋 Мои привычки", callback_data="my_habits")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="statistics")],
            [InlineKeyboardButton(text="🏆 Достижения", callback_data="achievements")],
            [InlineKeyboardButton(text="🔔 Уведомления", callback_data="notifications")],
        ]
    )

def back_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]
    )

@router.message(CommandStart())
async def start(message: Message):
    cursor.execute("SELECT * FROM notifications WHERE user_id = ?", (message.from_user.id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO notifications (user_id) VALUES (?)", (message.from_user.id,))
        conn.commit()

    await message.answer(
        "🔥 DAYWIN 🔥\n\nТвой ежедневный трекер привычек\n\nНачни становиться лучше уже сегодня 🚀",
        reply_markup=main_menu()
    )

@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.answer("🏠 Главное меню DAYWIN", reply_markup=main_menu())

@router.callback_query(F.data == "notifications")
async def notifications_menu(callback: CallbackQuery):
    cursor.execute("SELECT morning_time, evening_time FROM notifications WHERE user_id = ?", (callback.from_user.id,))
    morning_time, evening_time = cursor.fetchone()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="☀️ Изменить утреннее", callback_data="change_morning")],
            [InlineKeyboardButton(text="🌙 Изменить вечернее", callback_data="change_evening")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]
    )

    await callback.message.answer(
        f"🔔 Настройки уведомлений\n\n☀️ Утреннее: {morning_time}\n🌙 Вечернее: {evening_time}",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "change_morning")
async def change_morning(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("☀️ Введи время утреннего уведомления\n\nПример: 08:00", reply_markup=back_menu())
    await state.set_state(HabitState.waiting_for_morning_time)

@router.message(HabitState.waiting_for_morning_time)
async def save_morning_time(message: Message, state: FSMContext):
    time_text = message.text.strip()
    try:
        datetime.strptime(time_text, "%H:%M")
    except ValueError:
        await message.answer("❌ Неправильный формат времени\n\nПример: 08:00")
        return

    cursor.execute("UPDATE notifications SET morning_time = ? WHERE user_id = ?", (time_text, message.from_user.id))
    conn.commit()
    await message.answer(f"✅ Утреннее уведомление установлено на {time_text}", reply_markup=back_menu())
    await state.clear()

@router.callback_query(F.data == "change_evening")
async def change_evening(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🌙 Введи время вечернего уведомления\n\nПример: 22:00", reply_markup=back_menu())
    await state.set_state(HabitState.waiting_for_evening_time)

@router.message(HabitState.waiting_for_evening_time)
async def save_evening_time(message: Message, state: FSMContext):
    time_text = message.text.strip()
    try:
        datetime.strptime(time_text, "%H:%M")
    except ValueError:
        await message.answer("❌ Неправильный формат времени\n\nПример: 22:00")
        return

    cursor.execute("UPDATE notifications SET evening_time = ? WHERE user_id = ?", (time_text, message.from_user.id))
    conn.commit()
    await message.answer(f"✅ Вечернее уведомление установлено на {time_text}", reply_markup=back_menu())
    await state.clear()

@router.callback_query(F.data == "create_habit")
async def create_habit(callback: CallbackQuery, state: FSMContext):
    cursor.execute("SELECT COUNT(*) FROM habits WHERE user_id = ? AND status = 'active'", (callback.from_user.id,))
    if cursor.fetchone()[0] >= 5:
        await callback.message.answer("❌ Максимум 5 привычек")
        return

    await callback.message.answer(
        "✍️ Введи привычку\n\nНапример:\n💧 Пить воду\n🏋️ Тренировки\n📚 Читать книги",
        reply_markup=back_menu()
    )
    await state.set_state(HabitState.waiting_for_habit_name)

@router.message(HabitState.waiting_for_habit_name)
async def get_habit_name(message: Message, state: FSMContext):
    await state.update_data(habit_name=message.text)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 1 месяц", callback_data="habit_31")],
            [InlineKeyboardButton(text="📆 3 месяца", callback_data="habit_93")],
            [InlineKeyboardButton(text="🗓 6 месяцев", callback_data="habit_186")],
            [InlineKeyboardButton(text="✍️ Ввести вручную", callback_data="custom_days")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]
    )
    await message.answer("⏳ Выбери срок привычки", reply_markup=keyboard)

@router.callback_query(F.data == "custom_days")
async def custom_days(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📅 Введи количество дней", reply_markup=back_menu())
    await state.set_state(HabitState.waiting_for_custom_days)

@router.message(HabitState.waiting_for_custom_days)
async def get_custom_days(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введи число")
        return

    total_days = int(message.text)
    data = await state.get_data()
    habit_name = data.get("habit_name")
    start_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "INSERT INTO habits (user_id, habit_name, total_days, start_date) VALUES (?, ?, ?, ?)",
        (message.from_user.id, habit_name, total_days, start_date)
    )
    conn.commit()

    await message.answer(f"✅ Привычка успешно создана\n\n🔥 {habit_name}\n⏳ {total_days} дней", reply_markup=back_menu())
    await state.clear()

@router.callback_query(F.data.startswith("habit_"))
async def save_habit(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    habit_name = data.get("habit_name")
    total_days = int(callback.data.split("_")[1])
    start_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "INSERT INTO habits (user_id, habit_name, total_days, start_date) VALUES (?, ?, ?, ?)",
        (callback.from_user.id, habit_name, total_days, start_date)
    )
    conn.commit()

    await callback.message.answer(f"✅ Привычка успешно создана\n\n🔥 {habit_name}\n⏳ {total_days} дней", reply_markup=back_menu())
    await state.clear()

@router.callback_query(F.data == "my_habits")
async def my_habits(callback: CallbackQuery):
    cursor.execute(
        "SELECT id, habit_name, total_days, start_date, success_days, failed_days FROM habits WHERE user_id = ? AND status = 'active'",
        (callback.from_user.id,)
    )
    habits = cursor.fetchall()

    if not habits:
        await callback.message.answer("📭 У тебя пока нет привычек", reply_markup=back_menu())
        return

    text = "📋 Твои привычки\n"
    for habit in habits:
        habit_id, habit_name, total_days, start_date, success_days, failed_days = habit
        start = datetime.strptime(start_date, "%Y-%m-%d")
        passed_days = min((datetime.now() - start).days, total_days)
        remaining_days = total_days - passed_days
        total_checks = success_days + failed_days
        success_percent = 0 if total_checks == 0 else int((success_days / total_checks) * 100)

        text += f"\n🔥 {habit_name}\n📊 Успешность: {success_percent}%\n⏳ Осталось: {remaining_days} дней\n"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Удалить привычку", callback_data="delete_habit_menu")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]
    )
    await callback.message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data == "achievements")
async def achievements(callback: CallbackQuery):
    cursor.execute("SELECT habit_name FROM habits WHERE user_id = ? AND status = 'completed'", (callback.from_user.id,))
    habits = cursor.fetchall()

    if not habits:
        await callback.message.answer("🏆 Пока нет достижений", reply_markup=back_menu())
        return

    text = "🏆 Твои достижения\n"
    for habit in habits:
        text += f"\n✅ {habit[0]} — завершено\n"

    await callback.message.answer(text, reply_markup=back_menu())

@router.callback_query(F.data == "delete_habit_menu")
async def delete_habit_menu(callback: CallbackQuery):
    cursor.execute("SELECT id, habit_name FROM habits WHERE user_id = ? AND status = 'active'", (callback.from_user.id,))
    habits = cursor.fetchall()

    if not habits:
        await callback.message.answer("📭 Нет привычек для удаления", reply_markup=back_menu())
        return

    keyboard_buttons = [[InlineKeyboardButton(text=f"🗑 {h[1]}", callback_data=f"delete_{h[0]}")] for h in habits]
    keyboard_buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])

    await callback.message.answer("🗑 Выбери привычку для удаления", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons))

@router.callback_query(F.data.startswith("delete_"))
async def delete_habit(callback: CallbackQuery):
    if callback.data == "delete_habit_menu":
        return
    habit_id = int(callback.data.split("_")[1])
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()
    await callback.message.edit_text("🗑 Привычка удалена", reply_markup=back_menu())

@router.callback_query(F.data == "statistics")
async def statistics(callback: CallbackQuery):
    cursor.execute(
        "SELECT habit_name, total_days, start_date, success_days, failed_days FROM habits WHERE user_id = ? AND status = 'active'",
        (callback.from_user.id,)
    )
    habits = cursor.fetchall()

    if not habits:
        await callback.message.answer("📭 У тебя пока нет привычек", reply_markup=back_menu())
        return

    text = "📊 Статистика DAYWIN\n"
    for habit in habits:
        habit_name, total_days, start_date, success_days, failed_days = habit
        start = datetime.strptime(start_date, "%Y-%m-%d")
        passed_days = min((datetime.now() - start).days, total_days)
        remaining_days = total_days - passed_days
        total = success_days + failed_days
        percent = 0 if total == 0 else int((success_days / total) * 100)

        text += f"\n🔥 {habit_name}\n\n✅ Выполнено: {success_days}\n❌ Пропусков: {failed_days}\n📈 Успешность: {percent}%\n⏳ Осталось: {remaining_days} дней\n"

    await callback.message.answer(text, reply_markup=back_menu())

@router.callback_query(F.data.startswith("success_"))
async def success_day(callback: CallbackQuery):
    habit_id = int(callback.data.split("_")[1])
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT success_days, last_check_date FROM habits WHERE id = ?", (habit_id,))
    success_days, last_check = cursor.fetchone()

    if last_check == today:
        await callback.answer("⚠️ Сегодня уже отмечено", show_alert=True)
        return

    success_days += 1
    cursor.execute("UPDATE habits SET success_days = ?, last_check_date = ? WHERE id = ?", (success_days, today, habit_id))
    conn.commit()
    await callback.message.edit_text("✅ Отлично! День засчитан 🔥")

@router.callback_query(F.data.startswith("fail_"))
async def failed_day(callback: CallbackQuery):
    habit_id = int(callback.data.split("_")[1])
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT failed_days, last_check_date FROM habits WHERE id = ?", (habit_id,))
    failed_days, last_check = cursor.fetchone()

    if last_check == today:
        await callback.answer("⚠️ Сегодня уже отмечено", show_alert=True)
        return

    failed_days += 1
    cursor.execute("UPDATE habits SET failed_days = ?, last_check_date = ? WHERE id = ?", (failed_days, today, habit_id))
    conn.commit()
    await callback.message.edit_text("💪 Не сдавайся! Завтра получится лучше")