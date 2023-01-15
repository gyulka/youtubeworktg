from collections import defaultdict
import random
import sqlite3
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

import config


def db_init():
    return sqlite3.connect('db.db')


def get_admin():
    return 500242036


bot = Bot(token=config.Token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_msg(message: types.Message):
    id = message.from_user.id
    con = db_init()
    if con.execute('select id from users where id=?', (id,)).fetchone() is None:
        con.execute('insert into users(id) values(?)', (id,))
        con.commit()
        await message.answer('вы успешно подали заявку на регистрацию')
        await bot.send_message(get_admin(),'вам подали заявку')
    else:
        x, isreg = con.execute('select id,registered from users where id=?', (id,)).fetchone()
        await message.answer('вы уже зарегестрированы' if isreg else 'дождитесь подтверждения регистрации')


if __name__ == '__main__':
    executor.start_polling(dp)
