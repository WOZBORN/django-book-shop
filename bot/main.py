import asyncio
import logging
import sqlite3
import os

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

TOKEN = os.getenv("BOT_TOKEN")

# Инициализация диспетчера
dp = Dispatcher()

# Путь к базе данных (скорректируй путь в зависимости от расположения)
DB_PATH = "../bookshop/db.sqlite3"

def get_order_status(order_key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Выполняем запрос для получения информации о заказе
        cursor.execute("""
            SELECT o.status, GROUP_CONCAT(b.title || ' x ' || oi.quantity, ', ') AS items
            FROM main_order o
            JOIN main_orderitem oi ON o.id = oi.order_id
            JOIN main_book b ON oi.book_id = b.id
            WHERE o.order_key = ?
        """, (order_key,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            return {"status": result[0], "items": result[1]}
        return None
    except sqlite3.Error as e:
        conn.close()
        logging.error(f"Database error: {e}")
        return None

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Этот обработчик отвечает на команду /start
    """
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}!\n\n"
        "Отправь мне ключ заказа, чтобы я сообщил статус и содержимое."
    )


@dp.message()
async def order_status_handler(message: Message) -> None:
    """
    Обработчик сообщений: проверяет ключ заказа и возвращает статус и содержимое.
    """
    order_key = message.text.strip()
    order_data = get_order_status(order_key)

    if order_data:
        await message.answer(
            f"Статус заказа: {html.bold(order_data['status'])}\n"
            f"Содержимое заказа: {html.code(order_data['items'])}"
        )
    else:
        await message.answer(
            "Не удалось найти заказ с таким ключом. Проверьте ключ и попробуйте снова."
        )


async def main() -> None:
    # Инициализация бота
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
