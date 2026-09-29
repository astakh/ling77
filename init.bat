@echo off
REM ============================================================
REM WordFlow: Скрипт быстрой инициализации проекта (Windows)
REM ============================================================

echo 🚀 WordFlow: Инициализация проекта...
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден. Установите Python 3.11+
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python: %PYTHON_VERSION%

REM Проверка Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js не найден. Установите Node.js 18+
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✓ Node.js: %NODE_VERSION%

REM Проверка npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm не найден
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo ✓ npm: %NPM_VERSION%

echo.
echo 📦 Установка зависимостей...
echo.

REM Frontend
echo → Установка frontend зависимостей...
call npm install
echo ✓ Frontend зависимости установлены
echo.

REM Backend
echo → Создание виртуального окружения...
cd backend

if not exist "venv" (
    python -m venv venv
    echo ✓ Виртуальное окружение создано
) else (
    echo ✓ Виртуальное окружение уже существует
)

echo.
echo → Активация виртуального окружения...
call venv\Scripts\activate.bat

echo → Установка backend зависимостей...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ✓ Backend зависимости установлены

cd ..

echo.
echo ⚙️  Настройка конфигурации...
echo.

REM Backend .env
if not exist "backend\.env" (
    echo → Создание backend\.env...
    copy backend\.env.example backend\.env
    echo ✓ backend\.env создан
    echo   ⚠️  Отредактируйте backend\.env и укажите:
    echo      - DATABASE_URL (ваш удалённый PostgreSQL)
    echo      - SECRET_KEY
    echo      - GIGACHAT credentials
) else (
    echo ✓ backend\.env уже существует
)

REM Frontend .env
if not exist ".env" (
    echo → Создание .env для frontend...
    echo VITE_API_URL=http://localhost:8000 > .env
    echo ✓ .env создан
) else (
    echo ✓ .env уже существует
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ✅ Инициализация завершена!
echo.
echo Следующие шаги:
echo.
echo 1. Отредактируйте backend\.env:
echo    - Укажите DATABASE_URL для вашего PostgreSQL
echo    - Сгенерируйте SECRET_KEY
echo    - Добавьте GigaChat credentials
echo.
echo 2. Создайте базу данных на удалённом сервере:
echo    psql -h your-server -U postgres -f backend\scripts\create_database.sql
echo.
echo 3. Запустите миграции:
echo    cd backend ^&^& venv\Scripts\activate ^&^& alembic upgrade head
echo.
echo 4. Запустите проект:
echo    - Backend: cd backend ^&^& uvicorn main:app --reload
echo    - Frontend: npm run dev
echo.
echo    Или используйте VSCode: F5 → Full Stack
echo.
echo 5. Откройте http://localhost:5173
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pause
