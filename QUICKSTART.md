# ⚡ Быстрый старт WordFlow

## 🎯 Для запуска в VSCode

### 1️⃣ Автоматическая инициализация

**Linux/Mac:**
```bash
chmod +x init.sh
./init.sh
```

**Windows:**
```bash
init.bat
```

### 2️⃣ Настроить подключение к БД

Отредактируйте `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://wordflow_user:password@your-server-ip:5432/wordflow
SECRET_KEY=ваш-секретный-ключ-64-символа
GIGACHAT_CLIENT_ID=your-client-id
GIGACHAT_CLIENT_SECRET=your-client-secret
```

### 3️⃣ Создать БД на удалённом сервере

```bash
psql -h your-server-ip -U postgres -f backend/scripts/create_database.sql
```

Или выполните SQL вручную:
```sql
CREATE DATABASE wordflow WITH OWNER = postgres ENCODING = 'UTF8';
```

### 4️⃣ Запустить миграции

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
alembic upgrade head
```

### 5️⃣ Запустить проект

**Вариант A — VSCode (рекомендуется):**
- Нажмите `F5`
- Выберите **"Full Stack"**
- Готово! ✓

**Вариант B — Терминал:**

Терминал 1 (Backend):
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

Терминал 2 (Frontend):
```bash
npm run dev
```

### 6️⃣ Открыть приложение

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs

---

## 📁 Что добавлено для VSCode

✅ `.vscode/settings.json` — настройки редактора  
✅ `.vscode/launch.json` — конфигурации отладки (F5)  
✅ `.vscode/tasks.json` — автоматизированные задачи  
✅ `.vscode/extensions.json` — рекомендуемые расширения  
✅ `init.sh` / `init.bat` — скрипты инициализации  
✅ `SETUP.md` — подробная инструкция  
✅ `backend/scripts/create_database.sql` — SQL для создания БД  

---

## 🔧 Полезные команды VSCode

| Действие | Команда |
|----------|---------|
| Запустить всё | `F5` → Full Stack |
| Только backend | `F5` → Backend: FastAPI |
| Только frontend | `F5` → Frontend: Vite Dev |
| Задачи | `Ctrl+Shift+P` → Tasks |
| Терминал | `` Ctrl+` `` |

---

## 🆘 Если что-то не работает

1. **БД не подключается** → проверьте firewall и `pg_hba.conf`
2. **Миграции не работают** → `alembic upgrade head`
3. **Порт занят** → `lsof -i :8000` и убейте процесс
4. **CORS ошибка** → проверьте `CORS_ORIGINS` в `.env`

Подробности: см. `SETUP.md`

---

**Готово!** 🎉 Откройте http://localhost:5173
