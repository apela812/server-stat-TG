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
    get_all_running_processes,
)
from keyboards.main_kb import get_main_keyboard, get_inline_keyboard, get_back_keyboard, get_processes_keyboard

router = Router()


def check_user_access(user_id: int) -> bool:
    """Проверка доступа пользователя."""
    return not ALLOWED_USERS or user_id in ALLOWED_USERS


def format_cpu_stats(cpu: dict) -> str:
    """Форматирование статистики CPU."""
    status_emoji = "🟢" if cpu["percent"] < 50 else "🟡" if cpu["percent"] < 80 else "🔴"

    return (
        f"{status_emoji} Статистика CPU\n\n"
        f"📊 Загрузка: {cpu['percent']}%\n"
        f"⚡ Частота: {cpu['freq_current']} MHz (макс. {cpu['freq_max']} MHz)\n"
        f"🔹 Ядра: {cpu['cores_physical']} физических, {cpu['cores_logical']} логических"
    )


def format_ram_stats(ram: dict) -> str:
    """Форматирование статистики RAM."""
    status_emoji = "🟢" if ram["percent"] < 50 else "🟡" if ram["percent"] < 80 else "🔴"

    return (
        f"{status_emoji} Статистика RAM\n\n"
        f"📊 Загрузка: {ram['percent']}%\n"
        f"💾 Всего: {ram['total']:.2f} GB\n"
        f"✅ Свободно: {ram['available']:.2f} GB\n"
        f"🔸 Использовано: {ram['used']:.2f} GB"
    )


def format_disk_stats(disks: list) -> str:
    """Форматирование статистики дисков."""
    text = "💿 Статистика дисков\n\n"

    for disk in disks:
        status_emoji = "🟢" if disk["percent"] < 50 else "🟡" if disk["percent"] < 80 else "🔴"
        text += (
            f"{status_emoji} {disk['mountpoint']} ({disk['device']})\n"
            f"   Тип: {disk['fstype']}\n"
            f"   Всего: {disk['total']:.2f} GB\n"
            f"   Свободно: {disk['free']:.2f} GB\n"
            f"   Загрузка: {disk['percent']}%\n\n"
        )

    return text.strip()


def format_network_stats(network: dict) -> str:
    """Форматирование статистики сети."""
    return (
        "🌐 Статистика сети\n\n"
        f"📤 Отправлено: {network['bytes_sent']:.2f} MB\n"
        f"📥 Получено: {network['bytes_recv']:.2f} MB\n"
        f"📦 Пакетов отправлено: {network['packets_sent']:,}\n"
        f"📦 Пакетов получено: {network['packets_recv']:,}\n\n"
        f"Интерфейсы:\n"
        + "\n".join(f"  • {ip}" for ip in network["ip_addresses"][:5])
    )


def format_system_info(sys_info: dict) -> str:
    """Форматирование информации о системе."""
    temp_text = f"🌡️ Температура: {sys_info['temperature']}°C\n" if sys_info["temperature"] else ""

    return (
        "⚙️ Информация о системе\n\n"
        f"🖥️ Платформа: {sys_info['platform']}\n"
        f"📛 Хост: {sys_info['hostname']}\n"
        f"⏱️ Время работы: {sys_info['uptime']}\n"
        f"{temp_text}"
        f"🔹 Ядер CPU: {sys_info['cpu_count']}"
    )


def format_running_processes(processes: list, sort_by: str = "memory") -> str:
    """Форматирование списка запущенных процессов."""
    if not processes:
        return "📋 Нет запущенных процессов"

    sort_label = "Памяти" if sort_by == "memory" else "CPU"
    text = f"📋 Топ процессов по использованию {sort_label}\n\n"
    
    for i, proc in enumerate(processes, 1):
        pid = proc.get("pid", "N/A")
        name = proc.get("name", "Unknown")[:30]  # Ограничиваем длину имени
        cpu = proc.get("cpu_percent", 0) or 0
        memory = proc.get("memory_percent", 0) or 0
        
        text += f"{i}. <code>{name}</code>\n"
        text += f"   PID: {pid}\n"
        text += f"   CPU: {cpu:.1f}% | RAM: {memory:.1f}%\n\n"
    
    return text


def format_general_status(cpu: dict, ram: dict, sys_info: dict) -> str:
    """Форматирование общего статуса."""
    cpu_status = "🟢" if cpu["percent"] < 50 else "🟡" if cpu["percent"] < 80 else "🔴"
    ram_status = "🟢" if ram["percent"] < 50 else "🟡" if ram["percent"] < 80 else "🔴"

    return (
        f"📊 Общий статус сервера\n\n"
        f"📛 {sys_info['hostname']}\n"
        f"⏱️ Аптайм: {sys_info['uptime']}\n\n"
        f"{cpu_status} CPU: {cpu['percent']}%\n"
        f"{ram_status} RAM: {ram['percent']}%\n\n"
        f"⚡ Частота CPU: {cpu['freq_current']} MHz\n"
        f"💾 RAM: {ram['used']:.2f} / {ram['total']:.2f} GB"
    )


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start."""
    if not check_user_access(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этому боту.")
        return

    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
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
        "ℹ️ Доступные команды:\n\n"
        "/start - Запустить бота\n"
        "/status - Общий статус сервера\n"
        "/cpu - Статистика процессора\n"
        "/ram - Статистика оперативной памяти\n"
        "/disk - Статистика дисков\n"
        "/network - Статистика сети\n"
        "/system - Информация о системе\n"
        "/processes - Список запущенных процессов\n"
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


@router.message(Command("processes"))
async def cmd_processes(message: types.Message):
    """Обработчик команды /processes - список запущенных процессов."""
    if not check_user_access(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этому боту.")
        return

    processes = get_all_running_processes(sort_by="memory", limit=15)
    await message.answer(
        format_running_processes(processes, sort_by="memory"),
        reply_markup=get_processes_keyboard(),
        parse_mode="HTML"
    )


@router.message(F.text == "📋 Процессы")
async def msg_processes(message: types.Message):
    """Обработчик кнопки «Процессы»."""
    if not check_user_access(message.from_user.id):
        return

    processes = get_all_running_processes(sort_by="memory", limit=15)
    await message.answer(
        format_running_processes(processes, sort_by="memory"),
        reply_markup=get_processes_keyboard(),
        parse_mode="HTML"
    )


@router.message(F.text == "🔄 Обновить")
async def msg_refresh(message: types.Message):
    """Обработчик кнопки «Обновить»."""
    if not check_user_access(message.from_user.id):
        return

    cpu = get_cpu_stats()
    ram = get_ram_stats()
    sys_info = get_system_info()

    await message.answer(
        f"🔄 Данные обновлены\n\n" + format_general_status(cpu, ram, sys_info),
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
        f"🔄 Данные обновлены\n\n" + format_general_status(cpu, ram, sys_info),
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


@router.callback_query(F.data == "processes_memory")
async def cb_processes_memory(callback: types.CallbackQuery):
    """Обработчик кнопки «По памяти» для процессов."""
    processes = get_all_running_processes(sort_by="memory", limit=15)
    await callback.message.edit_text(
        format_running_processes(processes, sort_by="memory"),
        reply_markup=get_processes_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "processes_cpu")
async def cb_processes_cpu(callback: types.CallbackQuery):
    """Обработчик кнопки «По CPU» для процессов."""
    processes = get_all_running_processes(sort_by="cpu", limit=15)
    await callback.message.edit_text(
        format_running_processes(processes, sort_by="cpu"),
        reply_markup=get_processes_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "processes_refresh")
async def cb_processes_refresh(callback: types.CallbackQuery):
    """Обработчик кнопки «Обновить» для процессов."""
    processes = get_all_running_processes(sort_by="memory", limit=15)
    await callback.message.edit_text(
        "🔄 Данные обновлены\n\n" + format_running_processes(processes, sort_by="memory"),
        reply_markup=get_processes_keyboard(),
        parse_mode="HTML"
    )
