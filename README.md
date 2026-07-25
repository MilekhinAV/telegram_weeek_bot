# 🤖 Telegram → Weeek Bot

Бот для автоматического создания задач в системе **Weeek** из любых сообщений в групповом чате Telegram.  
Каждое новое сообщение превращается в задачу через публичный API Weeek.

---

## ✨ Возможности
- Реагирует на **любые сообщения** в указанном групповом чате (любой участник, бот или человек).
- Поддержка текста, медиа и вложений:
  - `title` задачи формируется из текста/подписи либо описания содержимого.
  - `description` содержит полный текст + метаинформацию (тип контента, отправитель, дата).
- Автоматическая установка срока задачи на **следующий календарный день**.
- Обработка ошибок Weeek API с ретраями.
- Логирование действий в консоль.
- Контейнеризация (Dockerfile + docker-compose).

---

## 🛠 Требования
- Linux-сервер с Docker и Docker Compose v2.
- Токен Telegram-бота.
- API-ключ Weeek.

---

## ⚙️ Установка и настройка

### 1. Клонировать репозиторий
```bash
git clone https://github.com/your-org/weeek-voice-bot.git
cd weeek-voice-bot
````

### 2. Создать `.env`

Скопируйте пример и заполните значения:

```bash
cat > .env <<'EOF'
# Telegram
TELEGRAM_BOT_TOKEN=123456:your_token_here

# Weeek API
WEEEK_API_KEY=<-------add your token here ---------->
WEEEK_BASE_URL=https://api.weeek.net/public/v1
WEEEK_TASKS_ENDPOINT=/tm/tasks

# Поля задачи
WEEEK_USER_ID=<-------add your user ID here ---------->
WEEEK_PROJECT_ID=<-------add your project ID here ---------->
WEEEK_BOARD_COLUMN_ID=<-------add your collumn ID here ---------->

# Разрешенные ID чатов (через запятую), если нужно привязать к конкретной группе
ALLOWED_CHAT_IDS=-10093794273940

# Прочее
SERVER_TZ=Europe/Moscow
TITLE_MAX_LEN=255
LOG_LEVEL=INFO
EOF
```

> Узнать `chat_id` можно, добавив бота в группу и вызвав:
> `curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates"`

### 3. Запуск

```bash
sudo apt-get update
sudo apt-get install docker-compose-plugin
sudo docker compose build
sudo docker compose up -d
```

### 4. Проверка

Логи:

```bash
docker compose logs -f
```

Если бот работает правильно, при любом сообщении в группе он ответит:

* `✅ Задача успешно создана в Weeek`
* или `❌ Не удалось создать задачу...` при ошибке.

---

## 🚀 Деплой на сервере Linux (чек-лист)

1. Установить Docker и Compose:

   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose-plugin
   ```

2. Склонировать репозиторий:

   ```bash
   git clone https://github.com/your-org/weeek-voice-bot.git
   cd weeek-voice-bot
   ```

3. Создать `.env` с токенами.

4. Запустить:

   ```bash
   docker compose up -d
   ```

5. Проверить:

   ```bash
   docker compose ps
   docker compose logs -f
   ```

6. При необходимости обновить:

   ```bash
   git pull
   docker compose build
   docker compose up -d
   ```

---

## 🔧 Управление

* **Остановить:**

  ```bash
  docker compose down
  ```

* **Перезапустить:**

  ```bash
  docker compose restart
  ```

* **Логи:**

  ```bash
  docker compose logs -f
  ```

---

## ❓ FAQ и типовые ошибки

### 1. Ошибка:

```
TelegramConflictError: Conflict: terminated by other getUpdates request
```

**Причина:** одновременно работает несколько экземпляров бота, либо у бота настроен webhook.
**Решение:**

* Завершить все процессы/контейнеры с ботом:

  ```bash
  docker compose down --remove-orphans
  docker ps -q --filter "ancestor=weeek-voice-bot:latest" | xargs -r docker stop
  ```
* Проверить нет ли локального Python-процесса:

  ```bash
  pgrep -af "python.*main.py" | xargs -r kill
  ```
* Сбросить webhook:

  ```bash
  curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/deleteWebhook?drop_pending_updates=true"
  ```

---

### 2. Ошибка:

```
Error response from daemon: pull access denied for weeek-voice-bot
```

**Причина:** `docker compose` пытается скачать образ из реестра, но образ не опубликован.
**Решение:**

* Собрать локально:

  ```bash
  docker compose build
  docker compose up -d
  ```

---

### 3. Ошибка:

```
TELEGRAM_BOT_TOKEN is not set
```

**Причина:** не задана переменная окружения в `.env`.
**Решение:** открыть `.env` и заполнить `TELEGRAM_BOT_TOKEN`.

---

### 4. Ошибка:

```
❌ Не удалось создать задачу. Проверьте настройки или обратитесь к администратору.
```

**Причина:** ошибка API Weeek (неверный ключ, ID проекта/доски или временная недоступность).
**Решение:** проверить:

* корректность `WEEEK_API_KEY`;
* `WEEEK_USER_ID`, `WEEEK_PROJECT_ID`, `WEEEK_BOARD_COLUMN_ID`;
* сетевое подключение сервера.

---

### 5. Бот не реагирует в группе

* Убедитесь, что **privacy mode** отключён у бота через BotFather (`/setprivacy → Disable`).
* Проверьте, что `ALLOWED_CHAT_IDS` в `.env` совпадает с ID вашей группы.
* Посмотрите логи:

  ```bash
  docker compose logs -f
  ```

---

## 📂 Структура проекта

```
.
├── Dockerfile
├── docker-compose.yml
├── main.py
└── requirements.txt
```

---

## 📜 Лицензия

MIT (или укажите свою)
