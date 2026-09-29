-- ============================================================
-- WordFlow: Скрипт создания базы данных
-- Выполнить на удалённом PostgreSQL сервере под суперпользователем
-- ============================================================

-- 1. Создать базу данных
CREATE DATABASE wordflow
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- 2. Создать пользователя приложения (опционально, но рекомендуется)
-- Замените 'your_secure_password' на реальный пароль
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'wordflow_user') THEN
        CREATE ROLE wordflow_user WITH LOGIN PASSWORD 'your_secure_password';
    END IF;
END
$$;

-- 3. Выдать права
GRANT ALL PRIVILEGES ON DATABASE wordflow TO postgres;
GRANT ALL PRIVILEGES ON DATABASE wordflow TO wordflow_user;

-- 4. Подключиться к БД wordflow и выполнить:
\c wordflow

GRANT ALL ON SCHEMA public TO wordflow_user;
GRANT ALL ON SCHEMA public TO postgres;

-- 5. Расширения (опционально)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- Проверка
-- ============================================================
-- SELECT datname FROM pg_database WHERE datname = 'wordflow';
-- SELECT rolname FROM pg_roles WHERE rolname = 'wordflow_user';
