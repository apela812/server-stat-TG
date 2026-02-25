"""
Конфигурация бота.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Разрешённые пользователи (список ID)
ALLOWED_USERS_RAW = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS = [
    int(user_id.strip())
    for user_id in ALLOWED_USERS_RAW.split(",")
    if user_id.strip().isdigit()
]

# Пути проекта
BASE_DIR = Path(__file__).resolve().parent.parent
