# 🖥️ Создание БД WordFlow в терминале на удалённом сервере

> Инструкция для случая, когда вы **уже подключились по SSH** к серверу и работаете в его терминале напрямую.

---

## 📋 Что нужно знать заранее

- Имя пользователя на сервере (обычно `root` или ваш логин с `sudo`)
- Пароль суперпользователя PostgreSQL (часто совпадает с системным `postgres`)

---

## 🚀 Пошаговая инструкция

### Шаг 1. Подключиться к серверу по SSH

На **вашем локальном компьютере**:

```bash
ssh username@your-server-ip
```

Пример:
```bash
ssh root@185.22.33.44
```

Дальше все команды выполняются **уже на сервере**.

---

### Шаг 2. Проверить, что PostgreSQL установлен и запущен

```bash
sudo systemctl status postgresql
```

Ожидается увидеть:
```
● postgresql.service - PostgreSQL RDBMS
     Active: active (exited)
```

**Если не активен:**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Если не установлен (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
```

**Проверить версию:**
```bash
psql --version
```

---

### Шаг 3. Войти в psql под суперпользователем

```bash
sudo -u postgres psql
```

После этого приглашение изменится на:
```
postgres=#
```

> 💡 Вы теперь внутри интерактивной консоли PostgreSQL. Все дальнейшие команды — это SQL.

---

### Шаг 4. Создать базу данных

Внутри `psql` выполните:

```sql
CREATE DATABASE wordflow
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;
```

Ожидается ответ:
```
CREATE DATABASE
```

**Проверить, что БД создана:**
```sql
\l
```

В списке должна появиться строка с `wordflow`.

---

### Шаг 5. Создать пользователя приложения

```sql
CREATE ROLE wordflow_user WITH
    LOGIN
    PASSWORD 'ПридумайтеНадёжныйПароль123!'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE;
```

Ожидается:
```
CREATE ROLE
```

> ⚠️ **Замените** `ПридумайтеНадёжныйПароль123!` на свой пароль.
>
> Сгенерировать случайный пароль можно в **другом терминале**:
> ```bash
> openssl rand -base64 24
> ```

**Проверить, что пользователь создан:**
```sql
\du
```

В списке должна быть строка `wordflow_user`.

---

### Шаг 6. Выдать права

```sql
-- Переключиться на новую БД
\c wordflow
```

Ожидается:
```
You are now connected to database "wordflow" as user "postgres".
```

Выдать права на схему:
```sql
GRANT ALL ON SCHEMA public TO wordflow_user;
GRANT ALL ON SCHEMA public TO postgres;
```

Ожидается дважды:
```
GRANT
```

(Опционально) Сделать `wordflow_user` владельцем БД:
```sql
ALTER DATABASE wordflow OWNER TO wordflow_user;
```

Ожидается:
```
ALTER DATABASE
```

---

### Шаг 7. Проверить подключение под новым пользователем

Не выходя из `psql`, проверим, что новый пользователь может подключиться.

**Сначала задайте пароль для локального подключения** (иногда требуется):
```sql
ALTER USER wordflow_user PASSWORD 'ПридумайтеНадёжныйПароль123!';
```

**Выйти из psql:**
```sql
\q
```

Теперь вы снова в обычном терминале сервера. Попробуйте подключиться под новым пользователем:

```bash
psql -U wordflow_user -d wordflow -h 127.0.0.1
```

Введите пароль, когда попросит.

Ожидается приглашение:
```
wordflow=>
```

**Проверить текущее подключение:**
```sql
SELECT current_user, current_database();
```

Ожидается:
```
 current_user  | current_database
---------------+------------------
 wordflow_user | wordflow
```

**Выйти:**
```sql
\q
```

---

### Шаг 8. Настроить удалённые подключения (если нужно подключаться с локальной машины)

> ⚠️ Этот шаг нужен, только если backend будет запускаться **не на этом же сервере**, а на вашей локальной машине. Если backend тоже на сервере — **пропустите этот шаг**.

#### 8.1. Отредактировать `postgresql.conf`

Найти файл (обычно один из путей):
```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
# или
sudo nano /etc/postgresql/16/main/postgresql.conf
```

Найти строку `#listen_addresses = 'localhost'` и заменить на:
```
listen_addresses = '*'
```

#### 8.2. Отредактировать `pg_hba.conf`

```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

В конец файла добавить:
```
# Разрешить подключения к wordflow с любого IP (по паролю)
host    wordflow    wordflow_user    0.0.0.0/0    scram-sha-256
```

> 🔒 **Безопаснее** указать конкретный IP:
> ```
> host  wordflow  wordflow_user  185.22.33.44/32  scram-sha-256
> ```

#### 8.3. Открыть порт в firewall

**UFW:**
```bash
sudo ufw allow 5432/tcp
sudo ufw reload
```

**iptables:**
```bash
sudo iptables -A INPUT -p tcp --dport 5432 -j ACCEPT
```

**Если сервер в облаке** — откройте порт 5432 в панели управления (Security Group / Firewall).

#### 8.4. Перезапустить PostgreSQL

```bash
sudo systemctl restart postgresql
```

#### 8.5. Проверить с локальной машины

На **вашем локальном компьютере**:
```bash
psql -h your-server-ip -U wordflow_user -d wordflow
```

Если подключились — всё работает. Выйти: `\q`

---

### Шаг 9. Настроить `backend/.env` на машине с backend

Откройте файл `backend/.env` (на машине, где будет запускаться backend) и укажите:

```env
DATABASE_URL=postgresql+asyncpg://wordflow_user:ПридумайтеНадёжныйПароль123!@your-server-ip:5432/wordflow
```

**Формат:**
```
postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>
```

> Если пароль содержит спецсимволы (`@`, `:`, `/`), закодируйте их:
> - `@` → `%40`
> - `:` → `%3A`
> - `/` → `%2F`

---

### Шаг 10. Применить миграции

На машине с backend:

```bash
cd backend
source venv/bin/activate   # Windows: venv\Scripts\activate
alembic upgrade head
```

**Проверить, что таблицы созданы** (на сервере):
```bash
sudo -u postgres psql -d wordflow -c "\dt"
```

Должны появиться таблицы:
```
 events
 dictionaries
 lesson_exercise_words
 lesson_exercises
 lessons
 learning_profiles
 llm_calls
 refresh_tokens
 user_words
 users
 words
```

---

## ✅ Быстрая шпаргалка (скопируйте и вставьте)

Всё сразу, одной сессией:

```bash
# 1. Войти в psql
sudo -u postgres psql

# 2. Внутри psql выполнить:
CREATE DATABASE wordflow WITH OWNER = postgres ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' TEMPLATE = template0;

CREATE ROLE wordflow_user WITH LOGIN PASSWORD 'YourStrongPassword123!' NOSUPERUSER NOCREATEDB NOCREATEROLE;

\c wordflow

GRANT ALL ON SCHEMA public TO wordflow_user;
GRANT ALL ON SCHEMA public TO postgres;

ALTER DATABASE wordflow OWNER TO wordflow_user;

\q

# 3. Проверить подключение
psql -U wordflow_user -d wordflow -h 127.0.0.1
# (введите пароль)
\q
```

---

## 🆘 Частые проблемы

### ❌ `sudo: unknown user: postgres`
PostgreSQL не установлен или пользователь `postgres` отсутствует.
```bash
sudo apt install postgresql -y
```

### ❌ `psql: command not found`
Клиент psql не в PATH. Установите:
```bash
sudo apt install postgresql-client -y
```

### ❌ `ERROR: locale "en_US.UTF-8" not found`
Локаль не установлена. Посмотрите доступные:
```bash
locale -a
```
И создайте БД с другой локалью:
```sql
CREATE DATABASE wordflow WITH ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C' TEMPLATE = template0;
```

Или установите локаль:
```bash
sudo locale-gen en_US.UTF-8
sudo systemctl restart postgresql
```

### ❌ `FATAL: role "postgres" does not exist`
Пользователь `postgres` не создан. Создайте:
```bash
sudo -u postgres createuser --superuser $USER
```

### ❌ `could not connect to server: Connection refused` (при удалённом подключении)
- Проверьте `listen_addresses` в `postgresql.conf`
- Проверьте `pg_hba.conf`
- Проверьте firewall
- Перезапустите: `sudo systemctl restart postgresql`

### ❌ `password authentication failed`
Неверный пароль. Сбросьте:
```bash
sudo -u postgres psql
ALTER USER wordflow_user PASSWORD 'NewPassword123!';
\q
```

---

## 📝 Полезные команды

| Действие | Команда |
|----------|---------|
| Войти в psql под postgres | `sudo -u postgres psql` |
| Список БД | `\l` |
| Список пользователей | `\du` |
| Подключиться к БД | `\c wordflow` |
| Список таблиц | `\dt` |
| Размер БД | `SELECT pg_size_pretty(pg_database_size('wordflow'));` |
| Выйти | `\q` |
| Удалить БД (осторожно!) | `DROP DATABASE wordflow;` |
| Удалить пользователя | `DROP ROLE wordflow_user;` |

---

## ✅ Чек-лист

- [ ] SSH-подключение к серверу работает
- [ ] PostgreSQL установлен и запущен (`systemctl status postgresql`)
- [ ] БД `wordflow` создана (`\l` показывает её)
- [ ] Пользователь `wordflow_user` создан (`\du` показывает его)
- [ ] Права выданы (`GRANT ALL ON SCHEMA public`)
- [ ] Локальное подключение под `wordflow_user` работает
- [ ] (Если нужно) Удалённое подключение работает
- [ ] `DATABASE_URL` в `backend/.env` настроен
- [ ] Миграции применены (`alembic upgrade head`)
- [ ] Таблицы созданы (`\dt` показывает 11 таблиц)

---

**Готово!** 🎉 Теперь можно запускать backend:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

Откройте http://localhost:8000/docs — API работает с реальной БД.
