"""
Модуль клавиатур для бота.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура с командами."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Общий статус"),
                KeyboardButton(text="🔥 CPU"),
            ],
            [
                KeyboardButton(text="💾 RAM"),
                KeyboardButton(text="💿 Диски"),
            ],
            [
                KeyboardButton(text="🌐 Сеть"),
                KeyboardButton(text="⚙️ Система"),
            ],
            [
                KeyboardButton(text="📋 Процессы"),
                KeyboardButton(text="🔄 Обновить"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
    return keyboard


def get_inline_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-клавиатура для быстрых действий."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Общий статус", callback_data="status_general"),
                InlineKeyboardButton(text="🔥 CPU", callback_data="status_cpu"),
            ],
            [
                InlineKeyboardButton(text="💾 RAM", callback_data="status_ram"),
                InlineKeyboardButton(text="💿 Диски", callback_data="status_disk"),
            ],
            [
                InlineKeyboardButton(text="🌐 Сеть", callback_data="status_network"),
                InlineKeyboardButton(text="⚙️ Система", callback_data="status_system"),
            ],
            [
                InlineKeyboardButton(text="📋 Процессы", callback_data="processes_memory"),
            ],
            [
                InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh"),
            ],
        ]
    )
    return keyboard


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой «Назад»."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="↩️ Назад в меню", callback_data="back_menu")],
        ]
    )
    return keyboard


def get_processes_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для управления процессами."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔥 По CPU", callback_data="processes_cpu"),
                InlineKeyboardButton(text="💾 По памяти", callback_data="processes_memory"),
            ],
            [InlineKeyboardButton(text="🔄 Обновить", callback_data="processes_refresh")],
            [InlineKeyboardButton(text="↩️ Назад в меню", callback_data="back_menu")],
        ]
    )
    return keyboard
