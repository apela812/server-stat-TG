"""
Обработчики команд и сообщений бота.
"""
from aiogram import Router, F, types
from aiogram.filters import Command

from config import ALLOWED_USERS
from utils.stats import (
    get_cpu_stats,
    get_ram_stats,
    get_disk_stats,
    get_network_stats,
    get_system_info,
    get_top_processes,
)
from keyboards.main_kb import get_main_keyboard, get_inline_keyboard, get_back_keyboard

router = Router()


def check_user_access(user_id: int) -> bool:
    """Проверка доступа пользователя."""
    return not ALLOWED_USERS or user_id in ALLOWED_USERS


def format_cpu_stats(cpu: dict) -> str:
    """Форматирование статистики CPU."""
    status_emoji = "🟢" if cpu["percent"] < 50 else "🟡" if cpu["percent"] < 80 else "🔴"

    return (
        f"{status_emoji} <b>Статистика CPU</b>\n\n"
        f"📊 Загрузка: <b>{cpu['percent']}%</b>\n"
        f"⚡ Частота: <b>{cpu['freq_current']} MHz</b> (макс. {cpu['freq_max']} MHz)\n"
        f"🔹 Ядра: <b>{cpu['cores_physical']}</b> физических, <b>{cpu['cores_logical']}</b> логических"
    )


def format_ram_stats(ram: dict) -> str:
    """Форматирование статистики RAM."""
    status_emoji = "🟢" if ram["percent"] < 50 else "🟡" if ram["percent"] < 80 else "🔴"

    return (
        f"{status_emoji} <b>Статистика RAM</b>\n\n"
        f"📊 Загрузка: <b>{ram['percent']}%</b>\n"
        f"💾 Всего: <b>{ram['total']:.2f} GB</b>\n"
        f"✅ Свободно: <b>{ram['available']:.2f} GB</b>\n"
        f"🔸 Использовано: <b>{ram['used']:.2f} GB</b>"
    )


def format_disk_stats(disks: list) -> str:
    """Форматирование статистики дисков."""
    text = "💿 <b>Статистика дисков</b>\n\n"

    for disk in disks:
        status_emoji = "🟢" if disk["percent"] < 50 else "🟡" if disk["percent"] < 80 else "🔴"
        text += (
            f"{status_emoji} <b>{disk['mountpoint']}</b> ({disk['device']})\n"
            f"   Тип: {disk['fstype']}\n"
            f"   Всего: <b>{disk['total']:.2f} GB</b>\n"
            f"   Свободно: <b>{disk['free']:.2f} GB</b>\n"
            f"   Загрузка: <b>{disk['percent']}%</b>\n\n"
        )

    return text.strip()


def format_network_stats(network: dict) -> str:
    """Форматирование статистики сети."""
    return (
        "🌐 <b>Статистика сети</b>\n\n"
        f"📤 Отправлено: <b>{network['bytes_sent']:.2f} MB</b>\n"
        f"📥 Получено: <b>{network['bytes_recv']:.2f} MB</b>\n"
        f"📦 Пакетов отправлено: <b>{network['packets_sent']:,}</b>\n"
        f"📦 Пакетов получено: <b>{network['packets_recv']:,}</b>\n\n"
        f"<b>Интерфейсы:</b>\n"
        + "\n".join(f"  • {ip}" for ip in network["ip_addresses"][:5])
    )


def format_system_info(sys_info: dict) -> str:
    """Форматирование информации о системе."""
    temp_text = f"🌡️ Температура: <b>{sys_info['temperature']}°C</b>\n" if sys_info["temperature"] else ""

    return (
        "⚙️ <b>Информация о системе</b>\n\n"
        f"🖥️ Платформа: <b>{sys_info['platform']}</b>\n"
        f"📛 Хост: <b>{sys_info['hostname']}</b>\n"
        f"⏱️ Время работы: <b>{sys_info['uptime']}</b>\n"
        f"{temp_text}"
        f"🔹 Ядер CPU: <b>{sys_info['cpu_count']}</b>"
    )


def format_general_status(cpu: dict, ram: dict, sys_info: dict) -> str:
    """Форматирование общего статуса."""
    cpu_status = "🟢" if cpu["percent"] < 50 else "🟡" if cpu["percent"] < 80 else "🔴"
    ram_status = "🟢" if ram["percent"] < 50 else "🟡" if ram["percent"] < 80 else "🔴"

    return (
        f"📊 <b>Общий статус сервера</b>\n\n"
        f"📛 <b>{sys_info['hostname']}</b>\n"
        f"⏱️ Аптайм: <b>{sys_info['uptime']}</b>\n\n"
        f"{cpu_status} <b>CPU:</b> {cpu['percent']}%\n"
        f"{ram_status} <b>RAM:</b> {ram['percent']}%\n\n"
        f"⚡ Частота CPU: <b>{cpu['freq_current']} MHz</b>\n"
        f"💾 RAM: <b>{ram['used']:.2f} / {ram['total']:.2f} GB</b>"
    )


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start."""
    if not check_user_access(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этому боту.")
        return

    await message.answer(
        f"👋 <b>Привет, {message.from_user.first_name}!</b>\n\n"
        "Я бот для мониторинга вашего сервера.\n"
        "Выберите команду в меню ниже:",
        reply_markup=get_main_keyboard(),
    )


@router.message(Command("status"))
async def cmd_status(message: types.Message):
    """Обработчик команды /status - общий статус."""
    if not check_user_access(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этому боту.")
        return

    cpu = get_cpu_stats()
    ram = get_ram_stats()
    sys_info = get_system_info()

    await message.answer(
        format_general_status(cpu, ram, sys_info),
        reply_markup=get_inline_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help."""
    if not check_user_access(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этому боту.")
        return

    help_text = (
        "ℹ️ <b>Доступные команды:</b>\n\n"
        "/start - Запустить бота\n"
        "/status - Общий статус сервера\n"
        "/cpu - Статистика процессора\n"
        "/ram - Статистика оперативной памяти\n"
        "/disk - Статистика дисков\n"
        "/network - Статистика сети\n"
        "/system - Информация о системе\n"
        "/help - Эта справка\n\n"
        "Также вы можете использовать кнопки в меню."
    )

    await message.answer(help_text)


@router.message(F.text == "📊 Общий статус")
async def msg_general_status(message: types.Message):
    """Обработчик кнопки «Общий статус»."""
    if not check_user_access(message.from_user.id):
        return

    cpu = get_cpu_stats()
    ram = get_ram_stats()
    sys_info = get_system_info()

    await message.answer(
        format_general_status(cpu, ram, sys_info),
        reply_markup=get_inline_keyboard(),
    )


@router.message(F.text == "🔥 CPU")
async def msg_cpu(message: types.Message):
    """Обработчик кнопки «CPU»."""
    if not check_user_access(message.from_user.id):
        return

    cpu = get_cpu_stats()
    await message.answer(format_cpu_stats(cpu), reply_markup=get_back_keyboard())


@router.message(F.text == "💾 RAM")
async def msg_ram(message: types.Message):
    """Обработчик кнопки «RAM»."""
    if not check_user_access(message.from_user.id):
        return

    ram = get_ram_stats()
    await message.answer(format_ram_stats(ram), reply_markup=get_back_keyboard())


@router.message(F.text == "💿 Диски")
async def msg_disk(message: types.Message):
    """Обработчик кнопки «Диски»."""
    if not check_user_access(message.from_user.id):
        return

    disks = get_disk_stats()
    await message.answer(format_disk_stats(disks), reply_markup=get_back_keyboard())


@router.message(F.text == "🌐 Сеть")
async def msg_network(message: types.Message):
    """Обработчик кнопки «Сеть»."""
    if not check_user_access(message.from_user.id):
        return

    network = get_network_stats()
    await message.answer(format_network_stats(network), reply_markup=get_back_keyboard())


@router.message(F.text == "⚙️ Система")
async def msg_system(message: types.Message):
    """Обработчик кнопки «Система»."""
    if not check_user_access(message.from_user.id):
        return

    sys_info = get_system_info()
    await message.answer(format_system_info(sys_info), reply_markup=get_back_keyboard())


@router.message(F.text == "🔄 Обновить")
async def msg_refresh(message: types.Message):
    """Обработчик кнопки «Обновить»."""
    if not check_user_access(message.from_user.id):
        return

    cpu = get_cpu_stats()
    ram = get_ram_stats()
    sys_info = get_system_info()

    await message.answer(
        f"🔄 <b>Данные обновлены</b>\n\n" + format_general_status(cpu, ram, sys_info),
        reply_markup=get_inline_keyboard(),
    )


@router.callback_query(F.data == "back_menu")
async def cb_back_menu(callback: types.CallbackQuery):
    """Обработчик кнопки «Назад в меню»."""
    await callback.message.edit_reply_markup(reply_markup=get_inline_keyboard())


@router.callback_query(F.data == "refresh")
async def cb_refresh(callback: types.CallbackQuery):
    """Обработчик кнопки «Обновить» (inline)."""
    cpu = get_cpu_stats()
    ram = get_ram_stats()
    sys_info = get_system_info()

    await callback.message.edit_text(
        f"🔄 <b>Данные обновлены</b>\n\n" + format_general_status(cpu, ram, sys_info),
        reply_markup=get_inline_keyboard(),
    )


@router.callback_query(F.data == "status_general")
async def cb_status_general(callback: types.CallbackQuery):
    """Обработчик кнопки «Общий статус» (inline)."""
    cpu = get_cpu_stats()
    ram = get_ram_stats()
    sys_info = get_system_info()

    await callback.message.edit_text(
        format_general_status(cpu, ram, sys_info),
        reply_markup=get_inline_keyboard(),
    )


@router.callback_query(F.data == "status_cpu")
async def cb_status_cpu(callback: types.CallbackQuery):
    """Обработчик кнопки «CPU» (inline)."""
    cpu = get_cpu_stats()
    await callback.message.edit_text(format_cpu_stats(cpu), reply_markup=get_back_keyboard())


@router.callback_query(F.data == "status_ram")
async def cb_status_ram(callback: types.CallbackQuery):
    """Обработчик кнопки «RAM» (inline)."""
    ram = get_ram_stats()
    await callback.message.edit_text(format_ram_stats(ram), reply_markup=get_back_keyboard())


@router.callback_query(F.data == "status_disk")
async def cb_status_disk(callback: types.CallbackQuery):
    """Обработчик кнопки «Диски» (inline)."""
    disks = get_disk_stats()
    await callback.message.edit_text(format_disk_stats(disks), reply_markup=get_back_keyboard())


@router.callback_query(F.data == "status_network")
async def cb_status_network(callback: types.CallbackQuery):
    """Обработчик кнопки «Сеть» (inline)."""
    network = get_network_stats()
    await callback.message.edit_text(format_network_stats(network), reply_markup=get_back_keyboard())


@router.callback_query(F.data == "status_system")
async def cb_status_system(callback: types.CallbackQuery):
    """Обработчик кнопки «Система» (inline)."""
    sys_info = get_system_info()
    await callback.message.edit_text(format_system_info(sys_info), reply_markup=get_back_keyboard())
