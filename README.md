# Telegram → Weeek Bot

Telegram-бот автоматически создаёт задачи в Weeek из сообщений группового чата.

Бот обрабатывает сообщения от любых участников чата: пользователей и других Telegram-ботов. Поддерживаются текстовые сообщения, голосовые сообщения, фотографии, документы, видео, аудиозаписи, стикеры и другие распространённые типы контента.

## Возможности

* Создание задачи в Weeek из каждого сообщения в Telegram-группе.
* Обработка сообщений от людей и Telegram-ботов.
* Поддержка текста, подписи к медиа, документов, фото, видео, аудио и голосовых сообщений.
* Автоматическое назначение срока на следующий календарный день.
* Ограничение работы конкретными Telegram-чатами.
* Защита от циклической обработки собственных ответов бота.
* Повторные попытки обращения к Weeek API при ошибках.
* Логирование полученных сообщений и ответов API.
* Запуск через Docker Compose.
* Автоматический перезапуск контейнера после сбоя или перезагрузки сервера.
* Ротация Docker-логов.

## Логика работы

1. Участник отправляет сообщение в Telegram-группу.
2. Бот получает сообщение через Telegram long polling.
3. Бот проверяет:

   * сообщение получено из группы или супергруппы;
   * идентификатор группы разрешён в `ALLOWED_CHAT_IDS`;
   * сообщение не было отправлено самим ботом;
   * сообщение содержит поддерживаемый тип данных.
4. Бот формирует название и описание задачи.
5. Бот отправляет POST-запрос в Weeek API.
6. При успешном создании задачи бот отвечает:

```text
✅ Задача успешно создана в Weeek
```

При ошибке:

```text
❌ Не удалось создать задачу. Проверьте настройки или обратитесь к администратору.
```

## Формирование задачи Weeek

Для текстового сообщения:

* `title` — текст Telegram-сообщения;
* `description` — полный текст Telegram-сообщения.

Для сообщения с подписью:

* `title` — подпись к вложению;
* `description` — полная подпись.

Для сообщения без текста бот формирует описание типа содержимого. Например:

```text
Message from username: Document: report.pdf
```

Дата выполнения задачи устанавливается на следующий календарный день в часовом поясе, указанном в `SERVER_TZ`.

Используемый endpoint по умолчанию:

```text
https://api.weeek.net/public/v1/tm/tasks
```

## Структура проекта

```text
.
├── Dockerfile
├── docker-compose.yml
├── main.py
└── requirements.txt
```

На сервере дополнительно создаётся файл:

```text
.env
```

Файл `.env` не должен публиковаться в GitHub.

## Требования

Для работы проекта необходимы:

* Ubuntu Server;
* Docker Engine;
* Docker Compose Plugin;
* токен Telegram-бота;
* API-ключ Weeek;
* идентификатор пользователя Weeek;
* идентификатор проекта Weeek;
* идентификатор колонки доски Weeek;
* идентификатор Telegram-группы.

## Подготовка Telegram-бота

Создайте Telegram-бота через BotFather и сохраните его токен.

Добавьте бота в нужную Telegram-группу.

Чтобы бот видел все сообщения участников группы, отключите Privacy Mode:

```text
BotFather → /setprivacy → выбрать бота → Disable
```

После изменения Privacy Mode рекомендуется удалить бота из группы и добавить его заново.

## Установка Docker на Ubuntu

Не смешивайте пакет `docker.io` из стандартного репозитория Ubuntu с пакетами `docker-ce` и `containerd.io` из официального репозитория Docker.

При смешивании пакетов может появиться ошибка:

```text
containerd.io : Conflicts: containerd
```

### Удаление конфликтующих пакетов

```bash
sudo apt-get remove -y \
  docker.io \
  docker-compose \
  docker-compose-v2 \
  podman-docker \
  containerd \
  runc
```

Удаление этих пакетов не удаляет автоматически Docker-образы и контейнеры из `/var/lib/docker`.

### Установка необходимых пакетов

```bash
sudo apt-get update

sudo apt-get install -y \
  ca-certificates \
  curl
```

### Добавление ключа официального репозитория Docker

```bash
sudo install -m 0755 -d /etc/apt/keyrings

sudo curl -fsSL \
  https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc

sudo chmod a+r /etc/apt/keyrings/docker.asc
```

### Добавление репозитория Docker

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### Установка Docker Engine и Docker Compose

```bash
sudo apt-get update

sudo apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

### Запуск и включение автозапуска Docker

```bash
sudo systemctl enable --now docker
```

Проверка:

```bash
docker --version
docker compose version
sudo systemctl is-active docker
sudo systemctl is-enabled docker
```

Ожидаемый статус Docker:

```text
active
enabled
```

## Работа с Docker без sudo

Добавьте текущего пользователя в группу `docker`:

```bash
sudo usermod -aG docker "$USER"
```

Примените новую группу без перезагрузки:

```bash
newgrp docker
```

Проверьте доступ:

```bash
docker ps
```

Добавление пользователя в группу `docker` предоставляет ему привилегии, сопоставимые с административными на сервере.

## Настройка Docker Compose

Файл `docker-compose.yml` должен содержать локальную сборку через `build`.

Используйте следующую конфигурацию:

```yaml
services:
  weeek-voice-bot:
    build:
      context: .
      dockerfile: Dockerfile
    image: weeek-voice-bot:latest
    restart: always

    env_file:
      - .env

    environment:
      TZ: Europe/Moscow

    healthcheck:
      test: ["CMD", "python", "-c", "import socket; print('ok')"]
      interval: 30s
      timeout: 10s
      retries: 5

    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

Параметр:

```yaml
build:
  context: .
```

указывает Docker Compose собирать образ локально из `Dockerfile`.

Без `build` Docker Compose попытается скачать образ `weeek-voice-bot:latest` из Docker Hub и выдаст ошибку:

```text
pull access denied for weeek-voice-bot
```

## Создание файла `.env`

Перейдите в каталог проекта:

```bash
cd ~/weeek_bot/weeek_bot
```

Создайте файл:

```bash
touch .env
chmod 600 .env
nano .env
```

Добавьте настройки:

```dotenv
TELEGRAM_BOT_TOKEN=
WEEEK_API_KEY=

WEEEK_BASE_URL=https://api.weeek.net/public/v1
WEEEK_TASKS_ENDPOINT=/tm/tasks

WEEEK_USER_ID=0044a107-6f54-4a5e-b2e2-859896283c63
WEEEK_PROJECT_ID=2
WEEEK_BOARD_COLUMN_ID=4

ALLOWED_CHAT_IDS=

SERVER_TZ=Europe/Moscow
TITLE_MAX_LEN=255
LOG_LEVEL=INFO
```

Заполните пустые значения:

```dotenv
TELEGRAM_BOT_TOKEN=
WEEEK_API_KEY=
ALLOWED_CHAT_IDS=
```

актуальными данными вашей среды.

Для нескольких Telegram-групп укажите идентификаторы через запятую без пробелов:

```dotenv
ALLOWED_CHAT_IDS=-1001111111111,-1002222222222
```

Если `ALLOWED_CHAT_IDS` оставить пустым, бот сможет обрабатывать сообщения во всех группах, куда он добавлен.

Это не рекомендуется для рабочего сервера.

## Защита секретов

Добавьте `.env` в `.gitignore`:

```bash
printf ".env\n__pycache__/\n*.pyc\n" >> .gitignore
```

Проверьте:

```bash
cat .gitignore
```

API-ключ Weeek и токен Telegram-бота нельзя:

* сохранять в `main.py`;
* добавлять в `Dockerfile`;
* публиковать в GitHub;
* вставлять в README;
* передавать в открытых чатах;
* сохранять в Docker-образе.

Если API-ключ или Telegram-токен уже был опубликован, его необходимо отозвать и создать новый.

## Проверка конфигурации

Перед сборкой проверьте итоговую конфигурацию Compose:

```bash
cd ~/weeek_bot/weeek_bot
docker compose config
```

Команда должна завершиться без ошибок.

Вывод может содержать значения переменных окружения. Не публикуйте полный вывод, если в нём отображаются секреты.

## Сборка Docker-образа

Перейдите в каталог, где находятся `Dockerfile` и `docker-compose.yml`:

```bash
cd ~/weeek_bot/weeek_bot
```

Остановите предыдущую версию проекта:

```bash
docker compose down --remove-orphans
```

Соберите образ:

```bash
docker compose build --no-cache
```

Проверьте наличие локального образа:

```bash
docker images | grep weeek-voice-bot
```

Ожидаемый результат:

```text
weeek-voice-bot   latest
```

## Запуск бота

Запустите контейнер в фоновом режиме:

```bash
docker compose up -d
```

Параметр `-d` означает detached mode. Контейнер продолжает работать после выхода из SSH-сессии.

Проверьте состояние:

```bash
docker compose ps
```

Посмотрите последние логи:

```bash
docker compose logs --tail=100
```

Следите за логами в реальном времени:

```bash
docker compose logs -f
```

Для выхода из просмотра логов нажмите:

```text
Ctrl+C
```

Это остановит только просмотр логов. Контейнер продолжит работать.

Проверить это можно командой:

```bash
docker compose ps
```

## Проверка работы

1. Добавьте Telegram-бота в группу.
2. Отключите Privacy Mode.
3. Укажите ID группы в `ALLOWED_CHAT_IDS`.
4. Отправьте в группу текстовое сообщение.
5. Проверьте ответ Telegram-бота.
6. Проверьте появление задачи в Weeek.
7. Проверьте логи:

```bash
docker compose logs --tail=100
```

При успешной обработке в логах появятся сообщения, похожие на:

```text
Received message from username in chat -100...
Processing message
Task created in Weeek
Sent reply to user
```

## Управление контейнером

### Состояние

```bash
docker compose ps
```

### Запуск

```bash
docker compose up -d
```

### Остановка контейнера без удаления

```bash
docker compose stop
```

### Запуск остановленного контейнера

```bash
docker compose start
```

### Перезапуск

```bash
docker compose restart
```

### Остановка и удаление контейнера

```bash
docker compose down
```

### Последние 100 строк логов

```bash
docker compose logs --tail=100
```

### Логи в реальном времени

```bash
docker compose logs -f
```

### Состояние Docker Engine

```bash
sudo systemctl status docker --no-pager
```

## Обновление проекта

После изменения `main.py`, `Dockerfile` или `requirements.txt` необходимо пересобрать образ.

```bash
cd ~/weeek_bot/weeek_bot

docker compose down

docker compose build --no-cache

docker compose up -d

docker compose ps

docker compose logs --tail=100
```

Команда `docker compose restart` не пересобирает образ и не применяет изменения из `main.py`, если код копируется внутрь образа на этапе сборки.

## Обновление проекта из GitHub

После получения изменений:

```bash
cd ~/weeek_bot/weeek_bot

git pull

docker compose down

docker compose build --no-cache

docker compose up -d

docker compose ps
```

## Автоматический запуск после перезагрузки

В `docker-compose.yml` используется:

```yaml
restart: always
```

Это означает, что Docker автоматически запустит контейнер:

* после падения процесса;
* после перезапуска Docker Engine;
* после перезагрузки сервера.

Docker Engine также должен быть включён в автозапуск:

```bash
sudo systemctl enable docker
```

Проверка:

```bash
sudo systemctl is-enabled docker
docker inspect weeek-voice-bot-1 --format '{{.HostConfig.RestartPolicy.Name}}'
```

Название контейнера может отличаться. Точное имя можно получить:

```bash
docker compose ps
```

## Почему не используется `docker compose pull`

Команда:

```bash
docker compose pull
```

загружает образ из Docker Registry.

В текущей конфигурации образ создаётся непосредственно на сервере из локального `Dockerfile`, поэтому используется:

```bash
docker compose build
docker compose up -d
```

Команду `docker compose pull` следует использовать только после публикации образа в Docker Hub, GitHub Container Registry или другом Docker Registry.

## Типовые ошибки

### Cannot connect to the Docker daemon

Ошибка:

```text
Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
Is the docker daemon running?
```

Причина: Docker Engine не запущен или текущий пользователь не имеет доступа к Docker socket.

Проверьте Docker:

```bash
sudo systemctl status docker --no-pager
```

Запустите и включите автозапуск:

```bash
sudo systemctl enable --now docker
```

Проверьте:

```bash
docker ps
```

При ошибке доступа добавьте пользователя в группу `docker`:

```bash
sudo usermod -aG docker "$USER"
newgrp docker
```

### pull access denied for weeek-voice-bot

Ошибка:

```text
pull access denied for weeek-voice-bot, repository does not exist
```

Причина: в `docker-compose.yml` указан параметр `image`, но отсутствует локальная сборка `build`.

Проверьте, что конфигурация содержит:

```yaml
build:
  context: .
  dockerfile: Dockerfile
```

Затем выполните:

```bash
docker compose build --no-cache
docker compose up -d
```

Не выполняйте `docker compose pull`, если образ не опубликован в Registry.

### containerd.io conflicts with containerd

Ошибка:

```text
containerd.io : Conflicts: containerd
```

Причина: одновременно используются пакеты из репозитория Ubuntu и официального репозитория Docker.

Удалите конфликтующие пакеты:

```bash
sudo apt-get remove -y \
  docker.io \
  docker-compose \
  docker-compose-v2 \
  podman-docker \
  containerd \
  runc
```

Установите официальный набор Docker:

```bash
sudo apt-get update

sudo apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

### TelegramConflictError

Ошибка:

```text
TelegramConflictError: Conflict: terminated by other getUpdates request
```

Причина: один Telegram-токен одновременно используется несколькими экземплярами бота.

Telegram long polling допускает только один активный процесс с одним токеном.

Посмотрите Docker-контейнеры:

```bash
docker ps -a | grep -i weeek
```

Посмотрите все Compose-проекты:

```bash
docker compose ls
```

Остановите текущий Compose-проект:

```bash
docker compose down --remove-orphans
```

Найдите локальные Python-процессы:

```bash
pgrep -af "python.*main.py"
```

При наличии лишнего процесса завершите его:

```bash
pkill -f "python.*main.py"
```

Проверьте systemd-сервисы:

```bash
systemctl list-units --type=service | grep -i weeek
```

После остановки лишних экземпляров запустите одну копию:

```bash
docker compose up -d
docker compose logs --tail=100
```

Если ранее использовался webhook, удалите его через Telegram Bot API, а затем снова запустите long polling.

### TELEGRAM_BOT_TOKEN is not set

Ошибка:

```text
TELEGRAM_BOT_TOKEN is not set
```

Причина: отсутствует файл `.env`, в нём нет переменной или Compose не подключает файл.

Проверьте:

```bash
cd ~/weeek_bot/weeek_bot
ls -la .env
grep '^TELEGRAM_BOT_TOKEN=' .env
```

Проверьте `docker-compose.yml`:

```yaml
env_file:
  - .env
```

Пересоздайте контейнер:

```bash
docker compose down
docker compose up -d --build
```

### WEEEK_API_KEY is not set

Ошибка:

```text
WEEEK_API_KEY is not set
```

Проверьте наличие значения:

```bash
grep '^WEEEK_API_KEY=' .env
```

После исправления:

```bash
docker compose up -d --build
```

### Бот не реагирует на сообщения

Проверьте Privacy Mode через BotFather:

```text
/setprivacy → выбрать бота → Disable
```

Проверьте ID группы:

```bash
grep '^ALLOWED_CHAT_IDS=' .env
```

Посмотрите логи:

```bash
docker compose logs --tail=200
```

Если сообщение отклонено фильтром, в логах будет:

```text
Message rejected by should_process
```

Возможные причины:

* сообщение отправлено не в группе;
* Telegram-группа отсутствует в `ALLOWED_CHAT_IDS`;
* сообщение отправлено самим ботом;
* тип сообщения не входит в список поддерживаемых.

### Бот получает сообщения, но задача не создаётся

Посмотрите ответ Weeek API:

```bash
docker compose logs --tail=200 | grep -E "Weeek API error|Weeek API exception"
```

Проверьте:

```dotenv
WEEEK_API_KEY=
WEEEK_BASE_URL=https://api.weeek.net/public/v1
WEEEK_TASKS_ENDPOINT=/tm/tasks
WEEEK_USER_ID=0044a107-6f54-4a5e-b2e2-859896283c63
WEEEK_PROJECT_ID=2
WEEEK_BOARD_COLUMN_ID=4
```

Возможные причины:

* недействительный API-ключ;
* неправильный endpoint;
* пользователь Weeek не существует;
* проект или колонка недоступны;
* API-ключ не имеет нужных прав;
* сервер не имеет доступа в интернет;
* Weeek API временно недоступен.

Проверка сетевого доступа:

```bash
curl -I https://api.weeek.net
```

### Неверная дата задачи

Проверьте настройки:

```bash
grep -E '^(SERVER_TZ|WEEEK_TASKS_ENDPOINT)=' .env
```

Рекомендуемое значение:

```dotenv
SERVER_TZ=Europe/Moscow
```

Проверьте время внутри контейнера:

```bash
docker compose exec weeek-voice-bot date
```

### Контейнер постоянно перезапускается

Посмотрите состояние:

```bash
docker compose ps
```

Посмотрите логи:

```bash
docker compose logs --tail=200
```

Посмотрите причину завершения:

```bash
docker inspect weeek-voice-bot-1 \
  --format 'Status={{.State.Status}} ExitCode={{.State.ExitCode}} Error={{.State.Error}}'
```

Уточните фактическое имя контейнера через:

```bash
docker compose ps
```

### Изменения в main.py не применились

Причина: код находится внутри Docker-образа, а контейнер был только перезапущен.

Выполните пересборку:

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Просмотр логов завершён через Ctrl+C

Команда:

```bash
docker compose logs -f
```

работает в интерактивном режиме.

Нажатие `Ctrl+C` останавливает только просмотр логов и не останавливает контейнер.

Проверка:

```bash
docker compose ps
```

## Полная последовательность первого запуска

```bash
cd ~/weeek_bot/weeek_bot

sudo systemctl enable --now docker

docker compose config

docker compose down --remove-orphans

docker compose build --no-cache

docker compose up -d

docker compose ps

docker compose logs --tail=100
```

## Полная последовательность обновления

```bash
cd ~/weeek_bot/weeek_bot

git pull

docker compose down

docker compose build --no-cache

docker compose up -d

docker compose ps

docker compose logs --tail=100
```

## Безопасность

Рекомендуется:

* обязательно ограничить `ALLOWED_CHAT_IDS`;
* хранить `.env` с правами `600`;
* не запускать несколько экземпляров с одним Telegram-токеном;
* регулярно обновлять Docker Engine и базовый Python-образ;
* не публиковать ответы Weeek API, если они содержат чувствительные данные;
* отозвать ранее опубликованные ключи и токены;
* выполнять резервное копирование `.env` в защищённое хранилище;
* не включать `.env` в Docker-образ;
* ограничить доступ к серверу по SSH-ключам.

## Лицензия

Укажите лицензию проекта отдельным файлом `LICENSE`, если репозиторий планируется распространять публично.
