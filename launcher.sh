#!/bin/bash

# 🤖 Server Monitor Bot - Universal Launcher & Manager
# Полный функционал управления ботом + управление пользователями

set -e

# ═══════════════════════════════════════════════════════════════════
# ЦВЕТА И ПЕРЕМЕННЫЕ
# ═══════════════════════════════════════════════════════════════════

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

PYTHON_CMD="python3"
PIP_CMD="pip3"
ENV_FILE=".env"
USERS_FILE=".users.db"
DB_FILE=".bot_data.db"
VENV_DIR="venv"
LOG_DIR="logs"
BOT_PID_FILE=".bot.pid"
BOT_LOG_FILE="$LOG_DIR/bot.log"

# ═══════════════════════════════════════════════════════════════════
# ФУНКЦИИ ВЫВОДА
# ═══════════════════════════════════════════════════════════════════

print_header() {
    echo -e "\n${BOLD}${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║   🤖 Server Monitor Bot - Universal Launcher              ║"
    echo "║   Инициализация и управление ботом                        ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_main_menu() {
    echo -e "\n${BOLD}${BLUE}📋 Главное меню:${NC}"
    echo "  1. ⚙️  Управление конфигурацией"
    echo "  2. 👥 Управление пользователями"
    echo "  3. 🔧 Управление окружением"
    echo "  4. 📊 Состояние системы"
    echo "  5. 🚀 Запустить бота"
    echo "  6. 🌙 Запустить бота в фоне"
    echo "  7. ⏹️  Остановить бота"
    echo "  8. ❌ Выход"
}

print_config_menu() {
    echo -e "\n${BOLD}${BLUE}⚙️  Управление конфигурацией:${NC}"
    echo "  1. 🔑 Изменить токен бота"
    echo "  2. 📱 Добавить администратора по Telegram ID"
    echo "  3. 📝 Редактировать .env файл"
    echo "  4. 🔍 Просмотреть текущую конфигурацию"
    echo "  5. 🔄 Сбросить конфигурацию"
    echo "  6. ◀️  Назад в главное меню"
}

print_users_menu() {
    echo -e "\n${BOLD}${BLUE}👥 Управление пользователями:${NC}"
    echo "  1. ➕ Добавить пользователя"
    echo "  2. ➖ Удалить пользователя"
    echo "  3. 📋 Показать всех пользователей"
    echo "  4. ✏️  Редактировать подпись пользователя"
    echo "  5. 🔍 Поиск пользователя по ID"
    echo "  6. ◀️  Назад в главное меню"
}

print_env_menu() {
    echo -e "\n${BOLD}${BLUE}🔧 Управление окружением:${NC}"
    echo "  1. 📦 Проверить Python"
    echo "  2. 📦 Проверить pip"
    echo "  3. 📦 Установить зависимости"
    echo "  4. 📦 Обновить зависимости"
    echo "  5. 🐍 Создать виртуальное окружение"
    echo "  6. 🐍 Активировать виртуальное окружение"
    echo "  7. ◀️  Назад в главное меню"
}

print_status_menu() {
    echo -e "\n${BOLD}${BLUE}📊 Состояние системы:${NC}"
    echo "  1. 🔍 Проверить конфигурацию"
    echo "  2. 👥 Показать всех пользователей"
    echo "  3. 📦 Показать установленные пакеты"
    echo "  4. 🐍 Версия Python"
    echo "  5. 🔄 Статус бота"
    echo "  6. ◀️  Назад в главное меню"
}

print_separator() {
    echo -e "\n${BOLD}${MAGENTA}═══════════════════════════════════════════════════════════${NC}\n"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# ═══════════════════════════════════════════════════════════════════
# ФУНКЦИИ РАБОТЫ С ENV
# ═══════════════════════════════════════════════════════════════════

init_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        cat > "$ENV_FILE" << 'EOF'
# Server Monitor Bot Configuration
BOT_TOKEN=your_token_here
ALLOWED_USERS=123456789
DATABASE_PATH=data/bot.db
LOG_LEVEL=INFO
EOF
        success "Файл .env создан"
    fi
}

get_env_value() {
    grep "^$1=" "$ENV_FILE" 2>/dev/null | cut -d= -f2- || echo ""
}

set_env_value() {
    local key=$1
    local value=$2
    
    if [ ! -f "$ENV_FILE" ]; then
        init_env_file
    fi
    
    if grep -q "^$key=" "$ENV_FILE"; then
        sed -i "s|^$key=.*|$key=$value|" "$ENV_FILE"
    else
        echo "$key=$value" >> "$ENV_FILE"
    fi
}

view_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        warning "Файл $ENV_FILE не найден"
        return
    fi
    
    echo -e "${BOLD}${CYAN}📄 Содержание $ENV_FILE:${NC}\n"
    cat "$ENV_FILE" | grep -v "^#" | grep -v "^$" | sed 's/BOT_TOKEN=.*/BOT_TOKEN=***HIDDEN***/g'
}

# ═══════════════════════════════════════════════════════════════════
# УПРАВЛЕНИЕ КОНФИГУРАЦИЕЙ
# ═══════════════════════════════════════════════════════════════════

change_bot_token() {
    init_env_file
    
    echo -e "\n${CYAN}Введите новый токен бота (оставьте пусто для отмены):${NC}"
    read -r new_token
    
    if [ -z "$new_token" ]; then
        warning "Операция отменена"
        return
    fi
    
    if ! [[ "$new_token" =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
        error "Неверный формат токена"
        return
    fi
    
    set_env_value "BOT_TOKEN" "$new_token"
    success "Токен успешно изменён"
}

add_admin_user() {
    init_env_file
    
    echo -e "\n${CYAN}Введите Telegram ID администратора:${NC}"
    read -r user_id
    
    if [ -z "$user_id" ]; then
        warning "Операция отменена"
        return
    fi
    
    if ! [[ "$user_id" =~ ^[0-9]+$ ]]; then
        error "ID должен быть числом"
        return
    fi
    
    echo -e "\n${CYAN}Введите имя/подпись для этого пользователя:${NC}"
    read -r user_name
    
    if [ -z "$user_name" ]; then
        user_name="User_$user_id"
    fi
    
    # Получить текущих пользователей
    current_users=$(get_env_value "ALLOWED_USERS")
    
    # Проверить, не добавлен ли уже
    if [[ "$current_users" == *"$user_id"* ]]; then
        warning "Пользователь с ID $user_id уже в списке"
        return
    fi
    
    # Добавить нового пользователя
    if [ -z "$current_users" ] || [ "$current_users" = "123456789" ]; then
        new_users="$user_id"
    else
        new_users="$current_users,$user_id"
    fi
    
    set_env_value "ALLOWED_USERS" "$new_users"
    
    # Сохранить подпись в файл пользователей
    if [ ! -f "$USERS_FILE" ]; then
        touch "$USERS_FILE"
    fi
    echo "$user_id|$user_name" >> "$USERS_FILE"
    
    success "Администратор добавлен"
    info "ID: $user_id"
    info "Подпись: $user_name"
}

edit_env_file() {
    init_env_file
    local editor="${EDITOR:-nano}"
    $editor "$ENV_FILE"
    success "Файл сохранён"
}

reset_config() {
    echo -e "\n${YELLOW}⚠️  Вы уверены, что хотите сбросить конфигурацию? (y/n)${NC}"
    read -r confirm
    
    if [ "$confirm" != "y" ]; then
        warning "Операция отменена"
        return
    fi
    
    rm -f "$ENV_FILE" "$USERS_FILE"
    init_env_file
    success "Конфигурация сброшена"
}

# ═══════════════════════════════════════════════════════════════════
# УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ
# ═══════════════════════════════════════════════════════════════════

get_user_name() {
    local user_id=$1
    grep "^$user_id|" "$USERS_FILE" 2>/dev/null | cut -d'|' -f2 || echo "Unknown"
}

add_user() {
    echo -e "\n${CYAN}Введите Telegram ID пользователя:${NC}"
    read -r user_id
    
    if [ -z "$user_id" ]; then
        warning "Операция отменена"
        return
    fi
    
    if ! [[ "$user_id" =~ ^[0-9]+$ ]]; then
        error "ID должен быть числом"
        return
    fi
    
    echo -e "\n${CYAN}Введите подпись/имя для пользователя:${NC}"
    read -r user_name
    
    if [ -z "$user_name" ]; then
        user_name="User_$user_id"
    fi
    
    if [ ! -f "$USERS_FILE" ]; then
        touch "$USERS_FILE"
    fi
    
    # Проверить, существует ли уже
    if grep -q "^$user_id|" "$USERS_FILE" 2>/dev/null; then
        warning "Пользователь с ID $user_id уже существует"
        return
    fi
    
    echo "$user_id|$user_name" >> "$USERS_FILE"
    success "Пользователь добавлен"
    info "ID: $user_id | Подпись: $user_name"
}

remove_user() {
    echo -e "\n${CYAN}Введите Telegram ID пользователя для удаления:${NC}"
    read -r user_id
    
    if [ -z "$user_id" ]; then
        warning "Операция отменена"
        return
    fi
    
    if [ ! -f "$USERS_FILE" ]; then
        error "Файл пользователей не найден"
        return
    fi
    
    if ! grep -q "^$user_id|" "$USERS_FILE"; then
        error "Пользователь с ID $user_id не найден"
        return
    fi
    
    sed -i "/^$user_id|/d" "$USERS_FILE"
    success "Пользователь удален"
}

show_users() {
    if [ ! -f "$USERS_FILE" ] || [ ! -s "$USERS_FILE" ]; then
        warning "Список пользователей пуст"
        return
    fi
    
    echo -e "\n${BOLD}${CYAN}👥 Список пользователей:${NC}\n"
    echo -e "${BOLD}ID${NC}              | ${BOLD}Подпись${NC}"
    echo "─────────────────┼──────────────────────"
    
    while IFS='|' read -r id name; do
        printf "%-17s | %s\n" "$id" "$name"
    done < "$USERS_FILE"
    
    echo ""
}

edit_user_signature() {
    echo -e "\n${CYAN}Введите Telegram ID пользователя:${NC}"
    read -r user_id
    
    if [ -z "$user_id" ]; then
        warning "Операция отменена"
        return
    fi
    
    if [ ! -f "$USERS_FILE" ] || ! grep -q "^$user_id|" "$USERS_FILE"; then
        error "Пользователь не найден"
        return
    fi
    
    current_name=$(get_user_name "$user_id")
    echo -e "\n${CYAN}Текущая подпись: ${YELLOW}$current_name${NC}"
    echo -e "${CYAN}Введите новую подпись:${NC}"
    read -r new_name
    
    if [ -z "$new_name" ]; then
        warning "Операция отменена"
        return
    fi
    
    sed -i "s|^$user_id|.*|$user_id|$new_name|" "$USERS_FILE"
    success "Подпись обновлена"
}

search_user() {
    echo -e "\n${CYAN}Введите Telegram ID для поиска:${NC}"
    read -r user_id
    
    if [ -z "$user_id" ]; then
        warning "Операция отменена"
        return
    fi
    
    if [ ! -f "$USERS_FILE" ]; then
        error "Файл пользователей не найден"
        return
    fi
    
    result=$(grep "^$user_id|" "$USERS_FILE" 2>/dev/null || true)
    
    if [ -z "$result" ]; then
        warning "Пользователь с ID $user_id не найден"
        return
    fi
    
    echo -e "\n${BOLD}${CYAN}🔍 Результат поиска:${NC}"
    echo "$result" | while IFS='|' read -r id name; do
        info "ID: $id | Подпись: $name"
    done
}

# ═══════════════════════════════════════════════════════════════════
# УПРАВЛЕНИЕ ОКРУЖЕНИЕМ (из setup.sh)
# ═══════════════════════════════════════════════════════════════════

check_python() {
    echo -e "\n${CYAN}🐍 Проверка Python...${NC}\n"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        success "$PYTHON_VERSION"
    else
        error "Python3 не найден! Установите Python 3.9+"
        return 1
    fi
}

check_pip() {
    echo -e "\n${CYAN}📦 Проверка pip...${NC}\n"
    
    if command -v pip3 &> /dev/null; then
        PIP_VERSION=$(pip3 --version)
        success "$PIP_VERSION"
    else
        error "pip3 не найден!"
        return 1
    fi
}

install_dependencies() {
    echo -e "\n${CYAN}📦 Установка зависимостей...${NC}"
    
    if [ ! -f "requirements.txt" ]; then
        error "Файл requirements.txt не найден"
        return
    fi
    
    if [ ! -d "$VENV_DIR" ]; then
        warning "Виртуальное окружение не найдено, создаю..."
        create_venv
    fi
    
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt
    success "Зависимости установлены"
}

update_dependencies() {
    echo -e "\n${CYAN}📦 Обновление зависимостей...${NC}"
    
    if [ ! -d "$VENV_DIR" ]; then
        error "Виртуальное окружение не найдено"
        return
    fi
    
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install --upgrade -r requirements.txt
    success "Зависимости обновлены"
}

create_venv() {
    if [ -d "$VENV_DIR" ]; then
        warning "Виртуальное окружение уже существует"
        return
    fi
    
    echo -e "\n${CYAN}🐍 Создание виртуального окружения...${NC}"
    python3 -m venv "$VENV_DIR"
    success "Виртуальное окружение создано"
}

activate_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        error "Виртуальное окружение не найдено"
        return
    fi
    
    echo -e "\n${CYAN}🐍 Активация виртуального окружения...${NC}"
    source "$VENV_DIR/bin/activate"
    success "Виртуальное окружение активировано"
}

# ═══════════════════════════════════════════════════════════════════
# ИНФОРМАЦИЯ О СОСТОЯНИИ
# ═══════════════════════════════════════════════════════════════════

show_config() {
    echo -e "\n${BOLD}${CYAN}⚙️  Текущая конфигурация:${NC}\n"
    view_env_file
}

show_all_packages() {
    if [ ! -d "$VENV_DIR" ]; then
        error "Виртуальное окружение не активировано"
        return
    fi
    
    echo -e "\n${BOLD}${CYAN}📦 Установленные пакеты:${NC}\n"
    source "$VENV_DIR/bin/activate"
    pip list
}

show_python_version() {
    echo -e "\n${CYAN}🐍 Версия Python:${NC}\n"
    python3 --version
    echo ""
    python3 -c "import sys; print(f'Путь: {sys.executable}')"
}

# ═══════════════════════════════════════════════════════════════════
# ЗАПУСК БОТА
# ═══════════════════════════════════════════════════════════════════

run_bot() {
    init_env_file
    
    # Проверить обязательные переменные
    bot_token=$(get_env_value "BOT_TOKEN")
    
    if [ -z "$bot_token" ] || [ "$bot_token" = "your_token_here" ]; then
        error "BOT_TOKEN не установлен в .env файле"
        info "Используйте опцию '⚙️  Управление конфигурацией'"
        return
    fi
    
    if [ ! -d "$VENV_DIR" ]; then
        warning "Виртуальное окружение не найдено, создаю..."
        create_venv
        install_dependencies
    fi
    
    echo -e "\n${GREEN}🚀 Запуск бота...${NC}\n"
    source "$VENV_DIR/bin/activate"
    python main.py
}

run_bot_background() {
    init_env_file
    
    # Проверить обязательные переменные
    bot_token=$(get_env_value "BOT_TOKEN")
    
    if [ -z "$bot_token" ] || [ "$bot_token" = "your_token_here" ]; then
        error "BOT_TOKEN не установлен в .env файле"
        info "Используйте опцию '⚙️  Управление конфигурацией'"
        return
    fi
    
    # Проверить, не запущен ли уже бот
    if [ -f "$BOT_PID_FILE" ]; then
        stored_pid=$(cat "$BOT_PID_FILE")
        if ps -p "$stored_pid" > /dev/null 2>&1; then
            warning "Бот уже запущен (PID: $stored_pid)"
            return
        else
            # Удалить старый PID файл
            rm -f "$BOT_PID_FILE"
        fi
    fi
    
    if [ ! -d "$VENV_DIR" ]; then
        warning "Виртуальное окружение не найдено, создаю..."
        create_venv
        install_dependencies
    fi
    
    # Создать директорию для логов если её нет
    mkdir -p "$LOG_DIR"
    
    echo -e "\n${GREEN}🌙 Запуск бота в фоне...${NC}"
    
    # Запустить бота в фоне
    source "$VENV_DIR/bin/activate"
    nohup python main.py > "$BOT_LOG_FILE" 2>&1 &
    BOT_PID=$!
    
    # Сохранить PID
    echo "$BOT_PID" > "$BOT_PID_FILE"
    
    sleep 2
    
    # Проверить, запустился ли процесс
    if ps -p "$BOT_PID" > /dev/null 2>&1; then
        success "Бот успешно запущен в фоне"
        info "PID: $BOT_PID"
        info "Логи: $BOT_LOG_FILE"
        info "Для просмотра логов: tail -f $BOT_LOG_FILE"
        info "Для остановки: ./launcher.sh --stop"
    else
        error "Ошибка запуска бота"
        error "Логи:"
        cat "$BOT_LOG_FILE"
        rm -f "$BOT_PID_FILE"
    fi
}

stop_bot() {
    if [ ! -f "$BOT_PID_FILE" ]; then
        warning "Файл PID не найден, бот не запущен или был запущен другим способом"
        return
    fi
    
    bot_pid=$(cat "$BOT_PID_FILE")
    
    if ! ps -p "$bot_pid" > /dev/null 2>&1; then
        warning "Процесс с PID $bot_pid не найден"
        rm -f "$BOT_PID_FILE"
        return
    fi
    
    echo -e "\n${YELLOW}⏹️  Остановка бота (PID: $bot_pid)...${NC}"
    
    # Попытка мягкой остановки
    kill -TERM "$bot_pid" 2>/dev/null || true
    
    # Ждём 5 секунд
    for i in {1..5}; do
        if ! ps -p "$bot_pid" > /dev/null 2>&1; then
            success "Бот остановлен"
            rm -f "$BOT_PID_FILE"
            return
        fi
        sleep 1
    done
    
    # Если не остановился, принудительно завершаем
    warning "Принудительная остановка..."
    kill -KILL "$bot_pid" 2>/dev/null || true
    sleep 1
    
    if ps -p "$bot_pid" > /dev/null 2>&1; then
        error "Не удалось остановить бота"
    else
        success "Бот остановлен"
        rm -f "$BOT_PID_FILE"
    fi
}

show_bot_status() {
    if [ ! -f "$BOT_PID_FILE" ]; then
        info "Бот не запущен (файл PID не найден)"
        return
    fi
    
    bot_pid=$(cat "$BOT_PID_FILE")
    
    echo -e "\n${BOLD}${CYAN}🔄 Статус бота:${NC}\n"
    
    if ps -p "$bot_pid" > /dev/null 2>&1; then
        success "Бот запущен"
        info "PID: $bot_pid"
        info "Процесс:"
        ps -p "$bot_pid" --format pid,cmd,etime
    else
        warning "Процесс не найден (PID: $bot_pid)"
        info "Файл PID устаревает, удаляю..."
        rm -f "$BOT_PID_FILE"
    fi
    
    if [ -f "$BOT_LOG_FILE" ]; then
        echo -e "\n${CYAN}📄 Последние строки логов:${NC}\n"
        tail -20 "$BOT_LOG_FILE"
    fi
}

# ═══════════════════════════════════════════════════════════════════
# ГЛАВНОЕ МЕНЮ
# ═══════════════════════════════════════════════════════════════════

config_menu_handler() {
    while true; do
        print_config_menu
        echo -e "\n${CYAN}Выберите опцию:${NC}"
        read -r choice
        
        case $choice in
            1) change_bot_token ;;
            2) add_admin_user ;;
            3) edit_env_file ;;
            4) show_config ;;
            5) reset_config ;;
            6) break ;;
            *) error "Неверный выбор" ;;
        esac
    done
}

users_menu_handler() {
    while true; do
        print_users_menu
        echo -e "\n${CYAN}Выберите опцию:${NC}"
        read -r choice
        
        case $choice in
            1) add_user ;;
            2) remove_user ;;
            3) show_users ;;
            4) edit_user_signature ;;
            5) search_user ;;
            6) break ;;
            *) error "Неверный выбор" ;;
        esac
    done
}

env_menu_handler() {
    while true; do
        print_env_menu
        echo -e "\n${CYAN}Выберите опцию:${NC}"
        read -r choice
        
        case $choice in
            1) check_python ;;
            2) check_pip ;;
            3) install_dependencies ;;
            4) update_dependencies ;;
            5) create_venv ;;
            6) activate_venv ;;
            7) break ;;
            *) error "Неверный выбор" ;;
        esac
    done
}

status_menu_handler() {
    while true; do
        print_status_menu
        echo -e "\n${CYAN}Выберите опцию:${NC}"
        read -r choice
        
        case $choice in
            1) show_config ;;
            2) show_users ;;
            3) show_all_packages ;;
            4) show_python_version ;;
            5) show_bot_status ;;
            6) break ;;
            *) error "Неверный выбор" ;;
        esac
    done
}

main_menu() {
    while true; do
        print_header
        print_main_menu
        echo -e "\n${CYAN}Выберите опцию:${NC}"
        read -r choice
        
        case $choice in
            1) config_menu_handler ;;
            2) users_menu_handler ;;
            3) env_menu_handler ;;
            4) status_menu_handler ;;
            5) run_bot ;;
            6) run_bot_background ;;
            7) stop_bot ;;
            8) 
                echo -e "\n${GREEN}До свидания! 👋${NC}\n"
                exit 0
                ;;
            *)
                error "Неверный выбор"
                ;;
        esac
        
        print_separator
    done
}

# ═══════════════════════════════════════════════════════════════════
# ТОЧКА ВХОДА
# ═══════════════════════════════════════════════════════════════════

# Проверить аргументы командной строки
if [ $# -gt 0 ]; then
    case "$1" in
        --help|-h)
            echo -e "${BOLD}${CYAN}Server Monitor Bot - Launcher${NC}\n"
            echo "Использование: ./launcher.sh [опция]"
            echo ""
            echo "Опции:"
            echo "  --help, -h       Показать эту справку"
            echo "  --setup          Инициализировать всё с нуля"
            echo "  --run            Запустить бота напрямую"
            echo "  --start          Запустить бота в фоне"
            echo "  --stop           Остановить фоновый процесс бота"
            echo "  --status         Показать статус бота"
            echo "  --logs           Показать логи бота"
            echo "  --config         Открыть меню конфигурации"
            echo "  --users          Открыть меню пользователей"
            echo "  (пусто)          Открыть интерактивное меню"
            echo ""
            ;;
        --setup)
            init_env_file
            create_venv
            install_dependencies
            success "Инициализация завершена!"
            ;;
        --run)
            run_bot
            ;;
        --start)
            run_bot_background
            ;;
        --stop)
            stop_bot
            ;;
        --status)
            show_bot_status
            ;;
        --logs)
            if [ -f "$BOT_LOG_FILE" ]; then
                tail -f "$BOT_LOG_FILE"
            else
                error "Файл логов не найден: $BOT_LOG_FILE"
            fi
            ;;
        --config)
            config_menu_handler
            ;;
        --users)
            users_menu_handler
            ;;
        *)
            error "Неизвестная опция: $1"
            echo "Используйте --help для справки"
            ;;
    esac
else
    # Интерактивное меню по умолчанию
    main_menu
fi
