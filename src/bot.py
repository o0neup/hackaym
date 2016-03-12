import logging

import re
import telebot
from telebot import types


# token = '185093347:AAHbhPcP3xPj7kiL3vpBUxM1lcxqmQR9WH8'
token = '175818011:AAGwDqLPSKmec0grwy_pweW30SdCg0f0zDI'
bot = telebot.TeleBot(token)

telebot.logger.setLevel(logging.INFO)
logger = telebot.logger


def parse_username(text):
    logger.info("Parse username in '{}'".format(text))
    if re.search("@\w+", text):
        return re.search("@\w+", text).group(0)
    return None


def parse_amount(text):
    logger.info("Parse amount in '{}'".format(text))
    try:
        return float(text)
    except ValueError:
        return None

command_dict = {
    "bill": [
        {
            "text": "for whom?",
            "parser": parse_username,
            "fallback_message": "Must be a username"
        }, {
            "text": "amount",
            "parser": parse_amount,
            "fallback_message": "Must be a float value"
        }, {
            "text": "describe it"
        }
    ]
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
    bot.send_message(message.chat.id, "@{}, {}".format(message.from_user.username, command_dict[
                     message.text.strip('/')][0]["text"]), reply_markup=types.ForceReply(selective=True))


@bot.message_handler(func=lambda message: True)
def save_user(message):
    logger.info(message)
    username = message.from_user.username
    logger.info("User id: '{}', username: '{}'".format(
        message.from_user.id, username))
    key = storage_key(message.from_user.id, message.chat.id)
    if key in storage:
        messages = storage[key]
        command = messages[0].strip('/').split('@')[0]

        question = command_dict[command][len(messages) - 1]
        next_question = None
        if len(messages) < len(command_dict[command]):
            next_question = command_dict[command][len(messages)]

        print messages, command, question
        logger.info("Message in storage with \nkey '{}',\nmessages: {}\nquestion: {}".format(
            key, messages, question))

        def save_and_send_next(text):
            write_to_storage(message.from_user.id,
                             message.chat.id, text)
            if next_question is not None:
                bot.send_message(message.chat.id, "@{}, {}".format(username, next_question[
                                 "text"]), reply_markup=types.ForceReply(selective=True))
            else:
                logger.info("Question sequence is over")
                bot.send_message(message.chat.id, "@{}, question sequence is over, answers are: {}".format(
                    username, messages[1:]))

        if "parser" in question:
            if question["parser"](message.text) is not None:
                parsed_message = question["parser"](message.text)
                logger.info("Parsed message: '{}'".format(parsed_message))
                save_and_send_next(parsed_message)
            else:
                bot.send_message(message.chat.id, "@{}, {}".format(
                    username, question["fallback_message"]))
                bot.send_message(message.chat.id, "@{}, {}".format(username, question[
                                 "text"]), reply_markup=types.ForceReply(selective=True))
        else:
            save_and_send_next(message.text)


storage = {}


def storage_key(user_id, chat_id):
    return "{},{}".format(user_id, chat_id)


def write_to_storage(user_id, chat_id, value):
    key = storage_key(user_id, chat_id)
    if key not in storage or (isinstance(value, str) and value.startswith('/')):
        storage[key] = []

    storage[key].append(value)


bot.polling()
