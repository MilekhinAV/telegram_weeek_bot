import asyncio
import logging
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatType
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# --------------------- загрузка окружения ---------------------
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
WEEEK_API_KEY = os.getenv("WEEEK_API_KEY", "").strip()
WEEEK_BASE_URL = os.getenv("WEEEK_BASE_URL", "https://api.weeek.net/public/v1").rstrip("/")
WEEEK_TASKS_ENDPOINT = os.getenv("WEEEK_TASKS_ENDPOINT", "/tm/tasks")

# Фиксированные поля из ТЗ
WEEEK_USER_ID = os.getenv("WEEEK_USER_ID", "0044a107-6f54-4a5e-b2e2-859896283c63")
WEEEK_PROJECT_ID = int(os.getenv("WEEEK_PROJECT_ID", "2"))
WEEEK_BOARD_COLUMN_ID = int(os.getenv("WEEEK_BOARD_COLUMN_ID", "4"))

# Ограничение по чатам (опционально). Если пусто — обрабатываем все групповые чаты.
ALLOWED_CHAT_IDS = {int(x) for x in os.getenv("ALLOWED_CHAT_IDS", "").split(",") if x.strip().lstrip("-").isdigit()}

# Таймзона для вычисления даты следующего дня
SERVER_TZ = os.getenv("SERVER_TZ", "UTC")

# Сообщения в чат
MSG_OK = "✅ Задача успешно создана в Weeek"
MSG_FAIL = "❌ Не удалось создать задачу. Проверьте настройки или обратитесь к администратору."

# Лимит заголовка
TITLE_MAX_LEN = int(os.getenv("TITLE_MAX_LEN", "255"))

# --------------------- базовые проверки ---------------------
if not TELEGRAM_BOT_TOKEN:
    raise SystemExit("TELEGRAM_BOT_TOKEN is not set")
if not WEEEK_API_KEY:
    raise SystemExit("WEEEK_API_KEY is not set")

# --------------------- логирование ---------------------
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO"),
)
logger = logging.getLogger("weeek-bot")

dp = Dispatcher()
MY_BOT_ID = None  # будет заполнен в main()

# --------------------- утилиты ---------------------
def next_day_str(tz_name: str) -> str:
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)
    nd = now + timedelta(days=1)
    return nd.strftime("%d.%m.%Y")


def truncate_title(s: str, limit: int = TITLE_MAX_LEN) -> str:
    s = s.strip().replace("\n", " ")
    if len(s) <= limit:
        return s
    return s[: limit - 1].rstrip() + "…"


def content_to_text(message: Message) -> tuple[str, str]:
    """
    Возвращает (title_source, full_description) на основе любого сообщения.
    1) Если есть text/caption — используем его.
    2) Иначе формируем человекочитаемое описание по типу контента.
    """
    sender = (message.from_user.username or message.from_user.full_name or "Unknown").strip()

    if message.text:
        txt = message.text.strip()
        title_src = txt
        desc = txt
        return title_src, desc

    if message.caption:
        cap = message.caption.strip()
        title_src = cap
        desc = cap
        return title_src, desc

    # Медиа/прочие типы
    if message.voice:
        d = f"Voice message ({message.voice.duration}s)"
    elif message.video_note:
        d = f"Video note ({message.video_note.duration}s)"
    elif message.audio:
        d = f"Audio ({message.audio.duration}s) — {message.audio.file_name or 'unnamed'}"
    elif message.document:
        d = f"Document: {message.document.file_name or 'unnamed'}"
    elif message.photo:
        d = "Photo"
    elif message.video:
        d = f"Video ({message.video.duration}s)"
    elif message.animation:
        d = "Animation (GIF)"
    elif message.sticker:
        d = "Sticker"
    else:
        d = "Unknown content"

    # Структурируем описание
    title_src = f"Message from {sender}: {d}"
    details = [
        f"From: {sender}",
        f"Type: {d}",
        f"Chat: {message.chat.title or 'Unknown'}",
        f"Time: {message.date}",
    ]
    desc = "\n".join(details)
    return title_src, desc


def build_payload(title_src: str, description: str) -> dict:
    day = next_day_str(SERVER_TZ)
    return {
        "title": truncate_title(title_src, TITLE_MAX_LEN),
        "description": description.strip(),
        "day": day,
        "parentId": None,
        "userId": WEEEK_USER_ID,
        "locations": [
            {"projectId": WEEEK_PROJECT_ID, "boardColumnId": WEEEK_BOARD_COLUMN_ID}
        ],
        "type": "action",
        "priority": 0,
    }


async def create_weeek_task(title_src: str, description: str) -> bool:
    url = f"{WEEEK_BASE_URL}{WEEEK_TASKS_ENDPOINT}"
    headers = {
        "Authorization": f"Bearer {WEEEK_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = build_payload(title_src, description)
    timeouts = httpx.Timeout(connect=10.0, read=20.0, write=20.0, pool=10.0)

    for attempt in range(1, 4):
        try:
            async with httpx.AsyncClient(timeout=timeouts) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if 200 <= resp.status_code < 300:
                    logger.info("Task created in Weeek. Status=%s Body=%s", resp.status_code, resp.text)
                    return True
                else:
                    logger.warning("Weeek API error. Attempt=%s Status=%s Body=%s", attempt, resp.status_code, resp.text)
        except Exception as e:
            logger.error("Weeek API exception on attempt %s: %r", attempt, e)
        await asyncio.sleep(1.5 * attempt)

    return False


def should_process(message: Message) -> bool:
    # Только группы/супергруппы
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return False

    # Если указан белый список чатов — проверяем
    if ALLOWED_CHAT_IDS and message.chat.id not in ALLOWED_CHAT_IDS:
        return False

    # Игнорируем собственные сообщения бота (чтобы не зациклиться)
    if message.from_user and MY_BOT_ID and message.from_user.id == MY_BOT_ID:
        return False

    # Хотим иметь хоть какое-то содержимое (текст/подпись или медиа)
    has_any = any([
        bool(message.text),
        bool(message.caption),
        bool(message.voice),
        bool(message.video_note),
        bool(message.audio),
        bool(message.document),
        bool(message.photo),
        bool(message.video),
        bool(message.animation),
        bool(message.sticker),
    ])
    return has_any


# --------------------- Telegram handlers ---------------------
@dp.message()
async def handle_any_message(message: Message):
    logger.info("🔍 Received message from %s in chat %s", 
                message.from_user.username if message.from_user else "unknown", 
                message.chat.id)
    
    if not should_process(message):
        logger.info("❌ Message rejected by should_process")
        return

    title_src, desc = content_to_text(message)
    logger.info("✅ Processing message: %s", title_src[:50])

    ok = await create_weeek_task(title_src, desc)
    try:
        await message.reply(MSG_OK if ok else MSG_FAIL, allow_sending_without_reply=True)
        logger.info("📤 Sent reply to user")
    except Exception as e:
        logger.error("Failed to send reply to chat: %r", e)


async def main():
    global MY_BOT_ID

    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=None))
    logger.info("Bot starting...")

    # Узнаём собственный ID бота (нужно, чтобы не обрабатывать свои ответы)
    try:
        me = await bot.get_me()
        MY_BOT_ID = me.id
        logger.info("Bot info: @%s (id=%s)", me.username, me.id)
        logger.info("Bot can join groups: %s; can_read_all_group_messages: %s", me.can_join_groups, me.can_read_all_group_messages)
    except Exception as e:
        logger.error("Failed to get bot info: %r", e)

    await dp.start_polling(bot, allowed_updates=["message"])


if __name__ == "__main__":
    try:
        import uvloop  # type: ignore
        uvloop.install()
    except Exception:
        pass

    asyncio.run(main())
