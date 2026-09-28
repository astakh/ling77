# 🗄️ Инструкция: Создание базы данных на удалённом PostgreSQL сервере

## 📋 Что понадобится

- **IP/хост** удалённого сервера
- **Логин/пароль** пользователя с правами создания БД (обычно `postgres`)
- **Порт PostgreSQL** (по умолчанию `5432`)
- **Клиент psql** (установлен на Linux/Mac, для Windows — через installer PostgreSQL или отдельно)

---

## 🔌 Шаг 1. Подключение к серверу

### Вариант A. Через SSH (если есть shell-доступ)

```bash
ssh user@your-server-ip
```

Далее все команды выполняются **на удалённом сервере**.

### Вариант B. Удалённо через psql с локальной машины

```bash
psql -h your-server-ip -U postgres -p 5432
```

Введите пароль при запросе.

### Вариант C. Через pgAdmin / DBeaver / TablePlus

Подключитесь к серверу через GUI-клиент, используя:
- Host: `your-server-ip`
- Port: `5432`
- Username: `postgres`
- Password: ваш пароль

Далее можно выполнять SQL-запросы через встроенный редактор.

---

## 🏗️ Шаг 2. Создание базы данных

### Способ 1. Через psql (рекомендуется)

Подключитесь к серверу:

```bash
psql -h your-server-ip -U postgres
```

Выполните SQL:

```sql
-- 1. Создать базу данных
CREATE DATABASE wordflow
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0
    CONNECTION LIMIT = -1;

-- 2. Проверить, что БД создана
\l
```

Должны увидеть `wordflow` в списке баз данных.

> **Важно:** `TEMPLATE = template0` нужен, если на сервере в `template1` уже есть объекты — это гарантирует чистую БД.

### Способ 2. Одной командой из локальной машины

```bash
createdb -h your-server-ip -U postgres -E UTF8 --locale=en_US.UTF-8 wordflow
```

### Способ 3. Через готовый SQL-файл

```bash
psql -h your-server-ip -U postgres -f backend/scripts/create_database.sql
```

---

## 👤 Шаг 3. Создание пользователя приложения

**Рекомендуется** создать отдельного пользователя для приложения (не использовать `postgres`).

```sql
-- Создать пользователя с паролем
CREATE ROLE wordflow_user WITH
    LOGIN
    PASSWORD 'YourStrongPasswordHere123!'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE;

-- Проверить
\du
```

> ⚠️ **Замените** `YourStrongPasswordHere123!` на надёжный пароль. Сгенерировать можно командой:
> ```bash
> openssl rand -base64 24
> ```

---

## 🔐 Шаг 4. Выдача прав

```sql
-- Подключиться к новой БД
\c wordflow

-- Выдать права на схему public
GRANT ALL ON SCHEMA public TO wordflow_user;
GRANT ALL ON SCHEMA public TO postgres;

-- (Опционально) Сделать wordflow_user владельцем БД
ALTER DATABASE wordflow OWNER TO wordflow_user;
```

Если используете `postgres` как владельца — этот шаг можно пропустить.

---

## ✅ Шаг 5. Проверка подключения

### Проверка с локальной машины под новым пользователем

```bash
psql -h your-server-ip -U wordflow_user -d wordflow
```

Введите пароль. Если подключились — всё работает.

Выполните тестовый запрос:

```sql
SELECT current_user, current_database(), version();
```

Ожидается что-то вроде:

```
 current_user  | current_database | version
---------------+------------------+---------------------------------
 wordflow_user | wordflow         | PostgreSQL 14.x on ...
```

Выйти: `\q`

---

## 🌐 Шаг 6. Настройка удалённого доступа (если не подключается)

Если psql выдаёт `could not connect` или `timeout`, проверьте:

### 6.1. `postgresql.conf` (на сервере)

```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
```

Найдите и раскомментируйте/измените:

```
listen_addresses = '*'
port = 5432
```

### 6.2. `pg_hba.conf` (на сервере)

```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

Добавьте в конец файла строку, разрешающую подключения с вашего IP:

```
# TYPE  DATABASE  USER        ADDRESS          METHOD
host    wordflow  wordflow_user  0.0.0.0/0    scram-sha-256
```

> 🔒 **Безопасность:** вместо `0.0.0.0/0` (все IP) укажите конкретный IP вашего компьютера:
> ```
> host  wordflow  wordflow_user  185.22.33.44/32  scram-sha-256
> ```

### 6.3. Firewall

**На сервере (UFW):**
```bash
sudo ufw allow from YOUR_IP to any port 5432
```

**На сервере (iptables):**
```bash
sudo iptables -A INPUT -p tcp -s YOUR_IP --dport 5432 -j ACCEPT
```

**Если сервер в облаке (AWS/GCP/Yandex/Selectel):**
Откройте порт `5432` в Security Group / Firewall Rules.

### 6.4. Перезапуск PostgreSQL

```bash
sudo systemctl restart postgresql
```

---

## 🧪 Шаг 7. Финальная проверка

С локальной машины:

```bash
# 1. Проверить доступность порта
nc -zv your-server-ip 5432
# Ожидается: Connection to ... port 5432 [tcp/*] succeeded!

# 2. Подключиться
psql -h your-server-ip -U wordflow_user -d wordflow

# 3. Внутри psql
\conninfo
# Ожидается: You are connected to database "wordflow" as user "wordflow_user" on host "..."
```

---

## 🔧 Шаг 8. Настройка `backend/.env`

После создания БД укажите строку подключения в `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://wordflow_user:YourStrongPasswordHere123!@your-server-ip:5432/wordflow
```

**Формат URL:**
```
postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>
```

Если пароль содержит спецсимволы (`@`, `:`, `/`), закодируйте их URL-encode:
- `@` → `%40`
- `:` → `%3A`
- `/` → `%2F`

Пример:
```env
DATABASE_URL=postgresql+asyncpg://wordflow_user:pass%40word@185.22.33.44:5432/wordflow
```

---

## 🚀 Шаг 9. Применение миграций

После настройки `.env`:

```bash
cd backend
source venv/bin/activate   # Windows: venv\Scripts\activate
alembic upgrade head
```

Проверьте, что таблицы созданы:

```bash
psql -h your-server-ip -U wordflow_user -d wordflow -c "\dt"
```

Должны появиться таблицы:
```
┌──────────────────────┐
│ users                │
│ learning_profiles    │
│ dictionaries         │
│ words                │
│ user_words           │
│ lessons              │
│ lesson_exercises     │
│ lesson_exercise_words│
│ refresh_tokens       │
│ llm_calls            │
│ events               │
└──────────────────────┘
```

---

## 🆘 Решение частых проблем

### ❌ `FATAL: database "wordflow" does not exist`
БД не создана. Вернитесь к **Шагу 2**.

### ❌ `FATAL: password authentication failed for user "wordflow_user"`
Неверный пароль или пользователь не создан. Проверьте **Шаг 3**.

### ❌ `could not connect to server: Connection refused`
- PostgreSQL не запущен: `sudo systemctl status postgresql`
- Firewall блокирует: проверьте **Шаг 6.3**
- `listen_addresses` не настроен: проверьте **Шаг 6.1**

### ❌ `FATAL: no pg_hba.conf entry for host "..."`
Ваш IP не разрешён. Добавьте запись в `pg_hba.conf` (**Шаг 6.2**) и перезапустите PostgreSQL.

### ❌ `invalid locale name: "en_US.UTF-8"`
Локаль не установлена на сервере. Используйте доступную:
```bash
locale -a  # посмотреть доступные локали
```
И создайте БД с другой локалью:
```sql
CREATE DATABASE wordflow WITH ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C' TEMPLATE = template0;
```

### ❌ `permission denied for schema public`
Не выданы права. Выполните **Шаг 4**.

### ❌ `connection to server at "...", port 5432 failed: Operation timed out`
Проблема с сетью:
- Проверьте IP и порт
- Проверьте firewall на сервере
- Проверьте Security Group в облаке
- Попробуйте `telnet your-server-ip 5432` или `nc -zv your-server-ip 5432`

---

## 📝 Шпаргалка команд

| Действие | Команда |
|----------|---------|
| Подключиться | `psql -h HOST -U USER -d wordflow` |
| Список БД | `\l` |
| Список пользователей | `\du` |
| Список таблиц | `\dt` |
| Подключиться к БД | `\c wordflow` |
| Выйти | `\q` |
| Размер БД | `SELECT pg_size_pretty(pg_database_size('wordflow'));` |

---

## ✅ Чек-лист готовности

- [ ] PostgreSQL запущен на удалённом сервере
- [ ] БД `wordflow` создана
- [ ] Пользователь `wordflow_user` создан (или используется `postgres`)
- [ ] Права на схему `public` выданы
- [ ] Порт 5432 открыт в firewall
- [ ] `pg_hba.conf` разрешает подключения с вашего IP
- [ ] Подключение с локальной машины работает
- [ ] `DATABASE_URL` в `backend/.env` настроен
- [ ] Миграции применены (`alembic upgrade head`)
- [ ] Таблицы созданы (проверка через `\dt`)

**После выполнения всех пунктов можно запускать backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

И открыть http://localhost:8000/docs — API должно работать с реальной БД. 🎉
