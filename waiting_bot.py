# -*- coding: utf-8 -*-
import ast
import json
import logging
import sys
import time
from datetime import datetime, timedelta

import telebot
from telebot.apihelper import ApiException

import texts
from config import BotSettings, DBSettings
from getters import DBGetter, YClientsGetter

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(filename='debug.log', level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S %p")

bot = telebot.TeleBot(BotSettings.TOKEN)
async_bot = telebot.AsyncTeleBot(BotSettings.TOKEN)
types = telebot.types

yclient_api = YClientsGetter()


def check_current_user_password(user_id):
    current_password = DBGetter(DBSettings.HOST).get("SELECT password FROM current_password")[0][0]
    try:
        logged_in_password = DBGetter(DBSettings.HOST).get("SELECT logged_password FROM authorized_users "
                                                           "WHERE user_id = %s" % user_id)[0][0]
    except IndexError:
        logged_in_password = current_password

    if logged_in_password == current_password:
        return "ok"
    else:
        return "changed"


def process_changed_password(message):
    user_id = message.chat.id
    bot.send_chat_action(chat_id=user_id, action="typing")
    password = message.text
    current_password = DBGetter(DBSettings.HOST).get("SELECT password FROM current_password")[0][0]
    if password == current_password:
        DBGetter(DBSettings.HOST).insert("UPDATE authorized_users SET logged_password ='%s' "
                                         "WHERE user_id = %s" % (password, user_id))
        main_menu_buttons(message, text=texts.PASSWORD_CORRECT)
    else:
        msg = bot.send_message(chat_id=user_id, text=texts.PASSWORD_INCORRECT)
        bot.register_next_step_handler(msg, process_changed_password)


def main_menu_buttons(message, text):
    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(texts.ADD_TO_WAITING_LIST)
    bot.send_message(chat_id=user_id, text=text, reply_markup=markup)


@bot.message_handler(commands=["start"])
def greeting_menu(message):
    user_id = message.chat.id
    first_name = message.chat.first_name
    bot.send_chat_action(chat_id=user_id, action="typing")
    user_auth = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM authorized_users "
                                              "WHERE user_id = %s" % user_id)[0][0]
    # new user
    if user_auth == 0:
        msg = bot.send_message(user_id, text=texts.GREETING % first_name)
        bot.register_next_step_handler(msg, process_password)

    # old user
    else:
        if check_current_user_password(user_id) == "ok":
            main_menu_buttons(message, text=texts.WHAT_DO_WE_DO)

        else:
            msg = bot.send_message(chat_id=user_id, text=texts.PASSWORD_WAS_CHANGED)
            bot.register_next_step_handler(msg, process_changed_password)


def process_password(message):
    user_id = message.chat.id
    bot.send_chat_action(chat_id=user_id, action="typing")
    password = message.text
    current_password = DBGetter(DBSettings.HOST).get("SELECT password FROM current_password")[0][0]
    if password == current_password:
        DBGetter(DBSettings.HOST).insert("INSERT INTO authorized_users (user_id, logged_password) "
                                         "VALUES (%s, '%s')" % (user_id, password))
        main_menu_buttons(message, text=texts.AUTHORIZED)

    else:
        msg = bot.send_message(chat_id=user_id, text=texts.PASSWORD_INCORRECT)
        bot.register_next_step_handler(msg, process_password)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts.ADD_TO_WAITING_LIST)
def add_to_waiting_list(message):
    user_id = message.chat.id
    bot.send_chat_action(chat_id=user_id, action="typing")
    msg = bot.send_message(chat_id=user_id, text=texts.TYPE_PHONE)
    bot.register_next_step_handler(msg, process_phone)


def process_phone(message):
    client_phone = message.text
    client = yclient_api.get_clients(phone=client_phone)
    print json.dumps(client)
    print json.dumps(yclient_api.get_clients())

while True:

    try:

        bot.polling(none_stop=True)

    # ConnectionError and ReadTimeout because of possible timeout of the requests library

    # TypeError for moviepy errors

    # maybe there are others, therefore Exception

    except Exception as e:
        logging.error(e)
        time.sleep(5)
