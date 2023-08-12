from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import requests
import asyncio
import aiohttp
from aiohttp import ClientSession
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

USER_ID = os.environ['USER_ID']
API_TOKEN = os.environ['API_TOKEN']
#url = 'http://app:8001/process_image'
#API_URL = 'http://api-serv.ru:8001/'
API_URL = 'http://app:8001/'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


async def register_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="♻️ Начало работы с ботом"),
        types.BotCommand(command="/help", description="💡 Получить справку по командам"),
        types.BotCommand(command="/date", description="📆 Получить текущую дату"),
        types.BotCommand(command="/power", description="🪩 Возведение в степень (используйте аргументы)"),
    ]
    await bot.set_my_commands(commands)


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def process_image(message: types.Message):
    # Получение файла изображения
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    # Загрузка изображения
    image_data = await bot.download_file(file_path)

    # Отправка изображения на сервер
    url = API_URL + 'process_image'
    response = requests.post(url, files={"image": ("input_image.png", image_data, "image/png")})

    if response.status_code == 200:
        # Получение обработанного изображения и отправка его обратно пользователю
        output_image_data = BytesIO(response.content)
        output_image_data.seek(0)
        await message.reply_photo(photo=output_image_data, caption="Обработанное изображение")


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    text = "Привет! Я бот для обработки изображений. Отправьте мне фотографию, и я верну вам обработанное изображение."
#    await message.reply(text, parse_mode=ParseMode.MARKDOWN)
    keyboard = create_inline_keyboard()
    await message.reply(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)


@dp.message_handler(commands=['date'])
async def get_date(message: types.Message):
    async with ClientSession() as session:
        url = API_URL + 'date'
        headers = {'accept': 'application/json'}

        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                date_data = await response.json()
                await message.reply(f"Date data: {date_data}")
            else:
                await message.reply("Ошибка при получении данных о дате.")


@dp.message_handler(commands=['power'])
async def get_power(message: types.Message):
    # Разбор аргументов команды
    args = message.get_args().split()
    if len(args) != 2:
        await message.reply("Введите два значения переменных после команды /power. Например: /power 10 20")
        return

    param1, param2 = args

    # Проверка, что аргументы являются числами
    try:
        float(param1)
        float(param2)
    except ValueError:
        await message.reply("Оба значения должны быть числами. Например: /power 10 20")
        return

    # Запрос к серверу с передачей параметров
    async with aiohttp.ClientSession() as session:
        url = API_URL + f'power?x={param1}&y={param2}'
        async with session.get(url) as response:
            if response.status == 200:
                power_data = await response.json()
                await message.reply(f"{param1}^{param2}: {power_data}")
            else:
                await message.reply("Ошибка при обработке возведения в степень.")

def create_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    # Добавление кнопок в инлайн-клавиатуру
    keyboard.add(InlineKeyboardButton("📆 Получить дату", callback_data="get_date"))
    keyboard.add(InlineKeyboardButton("🪩 Возведение в степень", callback_data="get_power"))
    return keyboard


@dp.callback_query_handler(lambda c: c.data == 'get_date')
async def get_date_callback(callback_query: types.CallbackQuery):
    async with aiohttp.ClientSession() as session:
        url = API_URL + 'date'
        async with session.get(url) as response:
            if response.status == 200:
                date_data = await response.json()
                await bot.answer_callback_query(callback_query.id, f"Текущая дата: {date_data['date']}")
            else:
                await bot.answer_callback_query(callback_query.id, "Ошибка при получении даты.")

@dp.callback_query_handler(lambda c: c.data == 'get_power')
async def get_power_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, "Пожалуйста, используйте команду /power с двумя аргументами, например: /power 10 20")


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    help_text = """
*Доступные команды бота:*

/start - Начало работы с ботом
/help - Получить справку по командам
/date - Получить текущую дату
/power _arg1_ _arg2_ - Возведение в степень (используйте аргументы)

🖼 Отправьте мне фотографию, и я верну вам обработанное изображение.

🪩 Для получения возведения в степень используйте команду /power с двумя аргументами, например: /power 25 3
"""

    await message.reply(help_text, parse_mode=ParseMode.MARKDOWN)


async def main():
    await register_commands(bot)

    while True:
        try:
            await bot.send_message(chat_id=USER_ID, text="Бот запущен")
            await dp.start_polling()
        except Exception as e:
            logging.exception("Ошибка во время выполнения бота")
            await bot.send_message(chat_id=USER_ID, text="Бот остановлен")
            await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(main())
