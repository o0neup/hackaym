import logging

import telebot
from telebot import types


# token = '185093347:AAHbhPcP3xPj7kiL3vpBUxM1lcxqmQR9WH8'
token = '175818011:AAGwDqLPSKmec0grwy_pweW30SdCg0f0zDI'
bot = telebot.TeleBot(token)

telebot.logger.setLevel(logging.INFO)
logger = telebot.logger


command_dict = {
    "bill": ["for whom?", "amount", "describe it"]
}


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    logger.info(message)
    markup = types.ForceReply()
    bot.send_message(message.chat.id, "Hey!", reply_markup=markup)


@bot.message_handler(commands=['bill'])
def handle_bill(message):
    logger.info(message)
    write_to_storage(message.from_user.id, message.chat.id, message.text)


@bot.message_handler(func=lambda message: True)
def save_user(message):
    logger.info(message)
    logger.info("User id: '{}', username: '{}'".format(
        message.from_user.id, message.from_user.username))

    if get_key(message.from_user.id, message.chat.id) in storage:
        write_to_storage(message.from_user.id, message.chat.id, message.text)

storage = {}


def get_key(user_id, chat_id):
    return "{}{}".format(user_id, chat_id)


def write_to_storage(user_id, chat_id, text):
    key = get_key(user_id, chat_id)
    if key not in storage or text.startswith('/'):
        storage[key] = []

    storage[key].append(text)
    print storage


bot.polling()
