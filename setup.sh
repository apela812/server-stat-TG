#!/bin/bash

# =============================================================================
# Script: setup.sh
# Description: Автоматическая настройка и запуск Server Monitor Bot
# =============================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Без цвета

# Логотип
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║         🤖 Server Monitor Bot - Setup Script              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Проверка наличия Python
echo -e "\n${YELLOW}[1/5] Проверка Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Найдено: ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}✗ Python3 не найден! Установите Python 3.9+${NC}"
    exit 1
fi

# Проверка наличия pip
echo -e "\n${YELLOW}[2/5] Проверка pip...${NC}"
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo -e "${GREEN}✓ Найдено: ${PIP_VERSION}${NC}"
else
    echo -e "${RED}✗ pip3 не найден! Установите pip${NC}"
    exit 1
fi

# Создание виртуального окружения
echo -e "\n${YELLOW}[3/5] Создание виртуального окружения...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ venv уже существует, пропускаем создание${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Виртуальное окружение создано${NC}"
fi

# Активация виртуального окружения
echo -e "\n${YELLOW}[4/5] Установка зависимостей...${NC}"
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓ Зависимости установлены${NC}"

# Настройка .env
echo -e "\n${YELLOW}[5/5] Настройка переменных окружения...${NC}"
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠ Файл .env уже существует${NC}"
    read -p "Хотите перезаписать? (y/n): " overwrite
    if [ "$overwrite" = "y" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env создан из шаблона${NC}"
    else
        echo -e "${YELLOW}⊗ Пропущено${NC}"
    fi
else
    cp .env.example .env
    echo -e "${GREEN}✓ .env создан из шаблона${NC}"
fi

# Инструкция по получению токена
echo -e "\n${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              📋 Следующие шаги                            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${YELLOW}1️⃣  Получите токен бота:${NC}"
echo -e "   📱 Откройте @BotFather в Telegram"
echo -e "   📝 Отправьте команду /newbot"
echo -e "   💾 Сохраните полученный токен"

echo -e "\n${YELLOW}2️⃣  Узнайте свой Telegram ID:${NC}"
echo -e "   📱 Откройте @userinfobot в Telegram"
echo -e "   📋 Скопируйте ваш ID (число)"

echo -e "\n${YELLOW}3️⃣  Отредактируйте файл .env:${NC}"
echo -e "   nano .env"
echo -e "   "
echo -e "   Вставьте ваши данные:"
echo -e "   ${GREEN}BOT_TOKEN=ваш_токен_от_botfather${NC}"
echo -e "   ${GREEN}ALLOWED_USERS=ваш_id${NC}"

echo -e "\n${YELLOW}4️⃣  Запустите бота:${NC}"
echo -e "   ${GREEN}python main.py${NC}"

echo -e "\n${GREEN}✅ Настройка завершена!${NC}"
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Предложение запустить бота
read -p "Хотите запустить бота сейчас? (y/n): " run_now
if [ "$run_now" = "y" ]; then
    echo -e "\n${GREEN}🚀 Запуск бота...${NC}"
    python main.py
fi
