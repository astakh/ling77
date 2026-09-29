#!/bin/bash
# ============================================================
# WordFlow: Скрипт быстрой инициализации проекта
# ============================================================

set -e

echo "🚀 WordFlow: Инициализация проекта..."
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 не найден. Установите Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python:${NC} $PYTHON_VERSION"

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js не найден. Установите Node.js 18+${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js:${NC} $NODE_VERSION"

# Проверка npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm не найден${NC}"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ npm:${NC} $NPM_VERSION"

echo ""
echo "📦 Установка зависимостей..."
echo ""

# Frontend
echo -e "${YELLOW}→ Установка frontend зависимостей...${NC}"
npm install
echo -e "${GREEN}✓ Frontend зависимости установлены${NC}"
echo ""

# Backend
echo -e "${YELLOW}→ Создание виртуального окружения...${NC}"
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Виртуальное окружение создано${NC}"
else
    echo -e "${GREEN}✓ Виртуальное окружение уже существует${NC}"
fi

echo ""
echo -e "${YELLOW}→ Активация виртуального окружения...${NC}"
source venv/bin/activate

echo -e "${YELLOW}→ Установка backend зависимостей...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Backend зависимости установлены${NC}"

cd ..

echo ""
echo "⚙️  Настройка конфигурации..."
echo ""

# Backend .env
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}→ Создание backend/.env...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✓ backend/.env создан${NC}"
    echo -e "${YELLOW}  ⚠️  Отредактируйте backend/.env и укажите:${NC}"
    echo -e "${YELLOW}     - DATABASE_URL (ваш удалённый PostgreSQL)${NC}"
    echo -e "${YELLOW}     - SECRET_KEY (openssl rand -hex 32)${NC}"
    echo -e "${YELLOW}     - GIGACHAT credentials${NC}"
else
    echo -e "${GREEN}✓ backend/.env уже существует${NC}"
fi

# Frontend .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}→ Создание .env для frontend...${NC}"
    echo "VITE_API_URL=http://localhost:8000" > .env
    echo -e "${GREEN}✓ .env создан${NC}"
else
    echo -e "${GREEN}✓ .env уже существует${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Инициализация завершена!${NC}"
echo ""
echo -e "${YELLOW}Следующие шаги:${NC}"
echo ""
echo "1. Отредактируйте backend/.env:"
echo "   - Укажите DATABASE_URL для вашего PostgreSQL"
echo "   - Сгенерируйте SECRET_KEY: openssl rand -hex 32"
echo "   - Добавьте GigaChat credentials"
echo ""
echo "2. Создайте базу данных на удалённом сервере:"
echo "   psql -h your-server -U postgres -f backend/scripts/create_database.sql"
echo ""
echo "3. Запустите миграции:"
echo "   cd backend && source venv/bin/activate && alembic upgrade head"
echo ""
echo "4. Запустите проект:"
echo "   - Backend: cd backend && uvicorn main:app --reload"
echo "   - Frontend: npm run dev"
echo ""
echo "   Или используйте VSCode: F5 → Full Stack"
echo ""
echo "5. Откройте http://localhost:5173"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
