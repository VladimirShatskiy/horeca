from telebot.types import Message
from loguru import logger
from keyboards import inline
from loader import bot
from config_data.config import TYPE_ORDER, CUR, lock


@logger.catch
@bot.message_handler(commands=['type'])
def bot_type(message: Message):

    data = (message.from_user.id,)
    with lock:
        CUR.execute("SELECT active, access_level FROM users JOIN access_level \n"
                    "        ON users.user_type = access_level.type_id WHERE telegram_id = ?", data)

    data = CUR.fetchall()[0]

    if data[1] == "client":
        bot.send_message(message.from_user.id, "У Вас нет доступа к данной функции")
        return
    elif data[0] == 2:
        bot.send_message(message.from_user.id, "Ваш доступ заблокирован\n"
                                               "Просьба обратиться к администратору")
        return
    else:
        bot.send_message(message.from_user.id, 'Просьба выбрать действие по заказ наряду',
                         reply_markup=inline.order_type.keyboard(TYPE_ORDER))

