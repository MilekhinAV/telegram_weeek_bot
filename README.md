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

To install Docker Compose on an Ubuntu VPS, the modern and recommended approach is to install it as a Docker CLI plugin (docker compose) directly from the official Docker repository. [1, 2] 
Here is the complete step-by-step guide to setting up both Docker and Docker Compose.
------------------------------
## Step 1: Update and Install Prerequisites
First, connect to your VPS via SSH. Update your local package index and install the tools required to secure your data and download Docker over HTTPS: [3, 4, 5, 6] 

sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg

## Step 2: Add Docker's Official GPG Key
Download Docker’s official GPG key to verify package signatures before installation: [3, 7, 8] 

sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

## Step 3: Add the Repository to Apt Sources
Add the stable repository for your specific version of Ubuntu to your system package lists: [1, 6, 7] 

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

## Step 4: Install Docker and Docker Compose
Refresh your package indexes once more to include the newly added repository. Then, install the complete Docker suite, including the Docker Compose plugin: [6, 7, 9, 10, 11] 

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

## Step 5: Verify the Installation
Confirm that both Docker and the Docker Compose plugin are properly installed and active on your system: [3, 12, 13, 14, 15] 

sudo docker --version
docker compose version

(Note: Modern Docker Compose v2 is run as docker compose without a hyphen). [1, 16] 
------------------------------
## Step 6: Run Docker Without Sudo (Optional)
By default, Docker commands require sudo permissions. To avoid typing sudo every time, add your current user to the docker user group: [1, 6, 17, 18] 

sudo usermod -aG docker $USER

Important: Log out of your VPS terminal session and log back in to apply this permission change. [17, 18] 
If you want to spin up your first application stack, let me know what kind of app you want to host (e.g., WordPress, Nginx, a Node.js API, or a database), and I can generate a custom docker-compose.yml file for you. [5, 13, 17, 19, 20] 


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
