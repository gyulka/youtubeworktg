import logging
from collections import defaultdict
import random
import sqlite3
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import filters
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, ReplyKeyboardMarkup

import config

logging.basicConfig(filename='log.txt',
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


def db_init():
    return sqlite3.connect('db.db')


bot = Bot(token=config.Token)
dp = Dispatcher(bot)

# ----------------consts
SETQIWI = 3
SETBTC = 4
SETETH = 5
SENDURL = 6

# keyboards
menu_profile_button = InlineKeyboardButton(text='профиль', callback_data='menu_profile')
main_menu_button = InlineKeyboardButton(text='назад', callback_data='menu_main')
with_button = InlineKeyboardButton(text='выплата', callback_data='menu_with')
with_qiwi_button = InlineKeyboardButton(text='заказать выплату qiwi', callback_data='menu_with_qiwi')
with_btc_button = InlineKeyboardButton(text='заказать выплату btc', callback_data='menu_with_btc')
with_eth_button = InlineKeyboardButton(text='заказать выплату eth', callback_data='menu_with_eth')
menu_send_button = InlineKeyboardButton(text='отправить', callback_data='menu_send')
menu_set_qiwi = InlineKeyboardButton(text='привязать qiwi', callback_data='menu_set_qiwi')
menu_set_btc = InlineKeyboardButton(text='привязать btc', callback_data='menu_set_btc')
menu_set_eth = InlineKeyboardButton(text='привязать eth', callback_data='menu_set_eth')
# -------------------main menu keyboard
inline_menu_main = InlineKeyboardMarkup()
inline_menu_main.add(menu_profile_button)
inline_menu_main.add(menu_send_button)
inline_menu_main.add(with_button)
# -------------------profile menu keyboard
inline_menu_profile = InlineKeyboardMarkup()
inline_menu_profile.add(menu_set_qiwi)
inline_menu_profile.add(menu_set_btc)
inline_menu_profile.add(menu_set_eth)
inline_menu_profile.add(main_menu_button)

replykeyoard = ReplyKeyboardMarkup()
replykeyoard.add('/menu')


def isregistered(id):
    con = db_init()
    if con.execute('select id,balance from users where id=?', (id,)).fetchone() is None:
        return False
    return True


def get_menu(id):
    con = db_init()
    x = con.execute('select menu from users where id=?', (id,)).fetchone()[0]
    return x


def get_balance(id):
    con = db_init()
    x = con.execute('select balance from users where id=?', (id,)).fetchone()[0]
    return x


def get_btc(id):
    con = db_init()
    x = con.execute('select btc from users where id=?', (id,)).fetchone()[0]
    return x


def get_qiwi(id):
    con = db_init()
    x = con.execute('select qiwi from users where id=?', (id,)).fetchone()[0]
    return x


def get_eth(id):
    con = db_init()
    x = con.execute('select eth from users where id=?', (id,)).fetchone()[0]
    return x


def get_admin_status(id):
    con = db_init()
    x = con.execute('select admin from users where id=?', (id,)).fetchone()[0]
    return x


def set_qiwi(id, value):
    con = db_init()
    x = con.execute('update users set qiwi=? where id=?', (value, id)).fetchone()
    con.commit()


def set_btc(id, value):
    con = db_init()
    x = con.execute('update users set btc=? where id=?', (value, id)).fetchone()
    con.commit()


def set_eth(id, value):
    con = db_init()
    x = con.execute('update users set eth=? where id=?', (value, id)).fetchone()
    con.commit()


def reg_member(id, username):
    con = db_init()
    try:
        con.execute('insert into users(id,username) values(?,?)', (id, username))
        con.commit()
    except Exception as error:
        logging.error(str(error))
    con.commit()


def add_salary(id):
    con = db_init()
    try:
        balance = get_balance(id)
        con.execute('update users set balance=? where id=?', (balance + config.salary, id))
        con.commit()
    except Exception as error:
        logging.error(str(error))
    con.commit()


def set_menu(id, value):
    con = db_init()
    try:
        con.execute('update users set menu=? where id=?', (value, id))
    except Exception as error:
        logging.error(str(error))
    con.commit()


def get_accept(id):
    if get_admin_status(id) < 0:
        return False
    return True


def set_admin_status(id, value):
    con = db_init()
    try:
        con.execute('update users set admin=? where id=?', (value, id))
        con.commit()
    except Exception as error:
        logging.error(str(error))


def get_admin_list(status=1):
    con = db_init()
    ans = []

    for j in con.execute('select id from users where admin>=?', (status,)).fetchall():
        ans.append(j[0])
    return ans


def get_member_list(status=1):
    con = db_init()
    ans = []

    for j in con.execute('select id from users where admin=0', ).fetchall():
        ans.append(j[0])
    return ans


def set_video_viewed(video_id):
    con = db_init()
    con.execute('update videos set isviewed=true where id=?', (video_id,))
    con.commit()


def get_tg_id_by_video(video_id):
    con = db_init()
    return con.execute('select tg_id from videos where id=?', (video_id,)).fetchone()[0]


def get_video_viewed(video_id):
    con = db_init()
    return con.execute('select isviewed from videos where id=?', (video_id,)).fetchone()[0]


def insert_video(video_id, tg_id):
    con = db_init()
    con.execute('insert into videos( id, tg_id) values(?,?)', (video_id, tg_id))
    con.commit()


def set_balance(id, value):
    con = db_init()
    try:
        con.execute('update users set balance=? where id=?', (value, id))
        con.commit()
    except Exception as error:
        logging.error(str(error))


def get_tg_id_by_with(with_id):
    con = db_init()
    return con.execute('select tg_id from withdraws where id=?', (with_id,)).fetchone()[0]


def get_sum_with(with_id):
    con = db_init()
    return con.execute('select summ from withdraws where id=?', (with_id,)).fetchone()[0]


def get_chat_id():
    con = db_init()
    return con.execute('select chat_id from config where id=1').fetchone()[0]


def change_chat(value):
    con = db_init()
    con.execute('update config set chat_id=? where id=1', (value,))
    con.commit()


def generate_post(user: types.user, url):
    id = url.split('/')[-1]
    id = id.split('v=')[-1]
    ans = f'''Пользователь @{user.username} отправил на модерацию видео
Видео: {id}
URL: {url}'''
    return ans, id


def get_username(id):
    con = db_init()
    return con.execute('select username from users where id=?', (id,)).fetchone()[0]


def insert_with(summ, tg_id):
    con = db_init()
    con.execute('insert into withdraws(tg_id,summ) values(?,?)', (tg_id, summ))
    con.commit()
    return \
        con.execute('select id from withdraws where summ=? and not isviewed and tg_id=?', (summ, tg_id)).fetchall()[-1][
            0]


def generate_menu():
    return '''Добро пожаловать в бота с оплатой за залив видео на Youtube

Информация тут будет обновлена, а пока что напишите @araaraara2021

Ваша оплата за каждый загруженный видеоролик: 30 RUB'''


def generate_profile(id):
    return f'''Id: {id}
Статус: {"воркер" if get_admin_status(id) == 0 else "админи" if get_admin_status(id) == 1 else "гл. админ"}
Баланс: {get_balance(id)}
Qiwi: {get_qiwi(id)}
BTC: {get_btc(id)}
ETH: {get_eth(id)}'''


@dp.message_handler(commands=['start'])
async def start_msg(message: types.Message):
    id = message.from_user.id

    if not isregistered(id) or get_admin_status(id) < -1:
        if not isregistered(id):
            reg_member(id, message.from_user.username)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Отклонить', callback_data=f'reg_deny_{id}'))
        keyboard.add(InlineKeyboardButton(text='Подтвердить', callback_data=f'reg_accept_{id}'))
        for i in get_admin_list():
            await bot.send_message(i, f'Заявка на регистрацию\nНик:{message.from_user.username}', reply_markup=keyboard)
        await message.answer('Заявка успешно принята на рассмотрение')
    elif get_admin_status(id) > -1:
        await message.answer('Вы уже зарегестрированы')
    else:
        await message.answer('Дождитесь рассмотрения заявки')


@dp.message_handler(commands=['menu'])
async def menu_msg(message: types.Message):
    id = message.from_user.id
    if not get_accept(id):
        await message.answer('отсутствует доступ')
        return
    await message.answer(generate_menu(), reply_markup=inline_menu_main)


@dp.callback_query_handler(text=['menu_profile'])
async def callback_profile(callback: types.callback_query):
    id = callback.from_user.id
    await callback.message.edit_text(generate_profile(id), reply_markup=inline_menu_profile)


@dp.callback_query_handler(text=['menu_set_qiwi'])
async def callback_set_qiwi(callback: types.callback_query):
    id = callback.from_user.id
    set_menu(id, SETQIWI)
    await callback.message.edit_text('введите кошелёк', reply_markup=None)


@dp.callback_query_handler(text=['menu_set_btc'])
async def callback_set_btc(callback: types.callback_query):
    id = callback.from_user.id
    set_menu(id, SETBTC)
    await callback.message.edit_text('введите кошелёк', reply_markup=None)


@dp.callback_query_handler(text=['menu_set_eth'])
async def callback_set_btc(callback: types.callback_query):
    id = callback.from_user.id
    set_menu(id, SETETH)
    await callback.message.edit_text('введите кошелёк', reply_markup=None)


@dp.callback_query_handler(text=['menu_set_qiwi'])
async def callback_set_qiwi(callback: types.callback_query):
    id = callback.from_user.id
    set_menu(id, SETQIWI)
    await callback.message.edit_text('введите кошелёк', reply_markup=None)


@dp.callback_query_handler(text=['menu_main'])
async def callback_menu(callback: types.callback_query):
    id = callback.from_user.id
    await callback.message.edit_text(generate_menu(), reply_markup=inline_menu_main)


@dp.callback_query_handler(text=['menu_send'])
async def callback_menu(callback: types.callback_query):
    id = callback.from_user.id
    set_menu(id, SENDURL)
    await callback.message.edit_text('Отправьте ссылку на видео', reply_markup=None)


@dp.callback_query_handler(filters.Text(startswith=['video_accept_']))
async def callback_accept_video(callback: types.callback_query):
    video_id = callback.data.split('_')[-1]
    if not get_video_viewed(video_id):
        text = f'/seo all https://www.youtube.com/watch?v={video_id}, 60, 100, l'
        await bot.send_message(get_chat_id(), text)
        add_salary(get_tg_id_by_video(video_id))
        set_video_viewed(video_id)

        await callback.message.edit_text(f'Вы одобрили видео {video_id}', reply_markup=None)
    else:
        await callback.message.edit_text(f'Видео уже было просмотрено другим администратором', reply_markup=None)


@dp.callback_query_handler(filters.Text(startswith=['video_deny_']))
async def callback_deny_video(callback: types.callback_query):
    video_id = callback.data.split('_')[-1]
    if not get_video_viewed(video_id):
        set_video_viewed(video_id)
        await callback.message.edit_text(f'Вы отклонили видео {video_id}', reply_markup=None)
    else:
        await callback.message.edit_text(f'Видео уже было просмотрено другим администратором', reply_markup=None)


@dp.callback_query_handler(filters.Text(startswith=['video_refresh_']))
async def callback_deny_video(callback: types.callback_query):
    video_id = callback.data.split('_')[-1]
    if not get_video_viewed(video_id):
        await bot.send_message(callback.from_user.id, 'вы первый кто просмотрел данное видео')
    else:
        await callback.message.edit_text(f'Видео уже было просмотрено другим администратором', reply_markup=None)


@dp.callback_query_handler(filters.Text(startswith=['with_deny_']))
async def callback_deny_with(callback: types.callback_query):
    with_id = callback.data.split('_')[-1]
    set_balance(get_tg_id_by_with(with_id)
                , get_sum_with(with_id))
    await callback.message.edit_text('вы отклонили выплату', reply_markup=None)


@dp.callback_query_handler(filters.Text(startswith=['with_accept_']))
async def callback_accept_with(callback: types.callback_query):
    with_id = callback.data.split('_')[-1]
    await callback.message.edit_text('вы подтвердили выплату', reply_markup=None)


@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    id = message.from_user.id
    if get_admin_status(id) != 2:
        await message.answer('Не достаточно прав')
        return
    await message.answer('/admin_list показывает список администраторов\n/member_list показывает список воркеров')


@dp.message_handler(commands=['admin_list'])
async def admin_panel(message: types.Message):
    id = message.from_user.id
    if get_admin_status(id) != 2:
        await message.answer('Не достаточно прав')
        return
    for i in get_admin_list():
        if i != id:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text='Упразнить', callback_data=f'admin_demote_{i}'))
            await message.answer(f'@{get_username(i)}', reply_markup=keyboard)


@dp.message_handler(commands=['member_list'])
async def admin_panel(message: types.Message):
    id = message.from_user.id
    if get_admin_status(id) != 2:
        await message.answer('Не достаточно прав')
        return
    for i in get_member_list():
        if i != id:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text='повысить', callback_data=f'admin_promote_{i}'))
            await message.answer(f'@{get_username(i)}', reply_markup=keyboard)


@dp.callback_query_handler(filters.Text(startswith=['admin_promote_']))
async def callback_accept_reg(callback: types.callback_query):
    id = callback.data.split('_')[-1]

    set_admin_status(id, 1)
    await bot.send_message(int(id), 'Ваc повысили до фдмина', reply_markup=replykeyoard)
    await callback.message.edit_text('успешно', reply_markup=None)


@dp.callback_query_handler(filters.Text(startswith=['admin_demote_']))
async def callback_accept_reg(callback: types.callback_query):
    id = callback.data.split('_')[-1]

    set_admin_status(id, 0)
    await bot.send_message(int(id), 'Ваc понизили до воркера', reply_markup=replykeyoard)
    await callback.message.edit_text('успешно', reply_markup=None)


@dp.callback_query_handler(filters.Text(startswith=['reg_accept_']))
async def callback_accept_reg(callback: types.callback_query):
    id = callback.data.split('_')[-1]

    set_admin_status(id, 0)
    await bot.send_message(int(id), 'Вам одобрили регистрацию', reply_markup=replykeyoard)
    await callback.message.edit_text('Вы подтвердили регистрацию', reply_markup=None)


@dp.callback_query_handler(filters.Text(startswith=['reg_deny_']))
async def callback_deny_reg(callback: types.callback_query):
    id = callback.from_user.id
    set_admin_status(id, -2)
    await callback.message.remove('вы отклонили регистрацию', reply_markup=None)


@dp.callback_query_handler(filters.Text(startswith=['menu_with_']))
async def callback_deny_reg(callback: types.callback_query):
    id = callback.from_user.id
    type = callback.data.split('_')[-1]
    keyboard = InlineKeyboardMarkup()
    keyboard.add(main_menu_button)
    await callback.message.edit_text('Успешно', reply_markup=keyboard)
    with_id = insert_with(get_balance(id), id)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Отклонить', callback_data=f'with_deny_{with_id}'))
    keyboard.add(InlineKeyboardButton(text='Одобрить', callback_data=f'with_accept_{with_id}'))

    for i in get_admin_list(2):
        await bot.send_message(i,
                               f'запрос вывода от @{callback.from_user.username}\n{type}: {eval(f"get_{type}({id})")}\n{get_balance(id)}р',
                               reply_markup=keyboard)
    set_balance(id, 0)


@dp.callback_query_handler(filters.Text(startswith=['change_chat_']))
async def callback_change_chat(callback: types.callback_query):
    chat_id = callback.data.split('_')[-1]
    change_chat(chat_id)
    await callback.message.edit_text('успешно', reply_markup=None)


@dp.callback_query_handler(filters.Text(startswith=['menu_with']))
async def callback_with_try(callback: types.callback_query):
    id = callback.from_user.id
    keyboard = InlineKeyboardMarkup()
    flag = False
    if get_qiwi(id) is not None:
        flag = True
        keyboard.add(InlineKeyboardButton(text='qiwi', callback_data='menu_with_qiwi'))
    if get_btc(id) is not None:
        flag = True
        keyboard.add(InlineKeyboardButton(text='btc', callback_data='menu_with_btc'))
    if get_eth(id) is not None:
        flag = True
        keyboard.add(InlineKeyboardButton(text='eth', callback_data='menu_with_eth'))
    keyboard.add(main_menu_button)
    await callback.message.edit_text('выберите вариант' if flag else 'привяжите способ выплаты', reply_markup=keyboard)


@dp.message_handler()
async def message_handler(message: types.Message):
    id = message.from_user.id
    menu = get_menu(id)
    if menu == SETQIWI:
        set_qiwi(id, message.text)
        set_menu(id, 0)
        await message.answer('Успешно')
        await message.answer(generate_menu(), reply_markup=inline_menu_main)

    if menu == SETBTC:
        set_btc(id, message.text)
        set_menu(id, 0)
        await message.answer('Успешно')
        await message.answer(generate_menu(), reply_markup=inline_menu_main)

    if menu == SETETH:
        set_eth(id, message.text)
        set_menu(id, 0)
        await message.answer('Успешно')
        await message.answer(generate_menu(), reply_markup=inline_menu_main)

    if menu == SENDURL:
        mess, video_id = generate_post(message.from_user, message.text)
        insert_video(video_id, id)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Отклонить', callback_data=f'video_deny_{video_id}'))
        keyboard.add(InlineKeyboardButton(text='Одобрить', callback_data=f'video_accept_{video_id}'))
        keyboard.add(InlineKeyboardButton(text='Оновить', callback_data=f'video_refresh_{video_id}'))

        for i in get_admin_list():
            await bot.send_message(i, mess, reply_markup=keyboard)


@dp.my_chat_member_handler()
async def event_handler(event: types.ChatMemberUpdated):
    keyboard = InlineKeyboardMarkup()
    keyboard.add((InlineKeyboardButton(text='Да', callback_data=f'change_chat_{event.chat.id}')))
    keyboard.add(InlineKeyboardButton(text='Нет', callback_data='no_changes'))
    for i in get_admin_list(2):
        await bot.send_message(i, f'заменить канал на {event.chat.title}', reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp)
