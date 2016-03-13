# -*- coding: utf-8 -*-
import logging
import traceback

import telebot
from telebot import types

import re
from src.core import session
from src.model.service import ModelService
from src.states.history import rootHistoryState
from src.states.info import rootInfoState
from src.states.money import render_invitation
from src.states.settleup import rootSettleupState
from src.states.suggest import rootSuggestState


service = ModelService(session)


# token = '185093347:AAHbhPcP3xPj7kiL3vpBUxM1lcxqmQR9WH8'
# token = '175818011:AAGwDqLPSKmec0grwy_pweW30SdCg0f0zDI'
token = '217392807:AAGQiwgNtOTln6KHp-Z9f_X7cLqaeeC2MlY'

# token = '184775317:AAEOyy9Ex2AE5ER5r5FOLClhcmquDLQdMds'  # artyomka_token
bot = telebot.TeleBot(token)

telebot.logger.setLevel(logging.INFO)
logger = telebot.logger
logging.basicConfig(level=logging.INFO)


def parse_single_username(message):
    logger.info("Parse single username in '{}'".format(message.text))
    username = None
    if message.text.strip() == "я":
        username = message.from_user.username
    else:
        result = re.findall("@\w+", message.text)
        if len(result) == 1:
            username = result[0]

    return username

def parse_username(message):
    text = message.text
    logger.info("Parse username in '{}'".format(text))
    result = re.findall("@\w+", text)
    if len(result) > 0:
        return result
    return None


def parse_amount(message):
    text = message.text
    logger.info("Parse amount in '{}'".format(text))
    try:
        return float(text)
    except ValueError:
        return None

command_dict = {
    "bill": [{
        "text": "Кто платил?",
        "parser": parse_single_username,
        "fall_back_message": "Это должен быть один username пользователя"
    },
        {
            "text": "За кого платили?",
            "parser": parse_username,
            "fallback_message": "Должно быть один или несколько username"
    }, {
            "text": "amount",
            "parser": parse_amount,
            "fallback_message": "Это должно быть число"
    }, {
            "text": "Опишите операцию"
    }
    ]
}

user_states = {}


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.from_user.username in user_states:
        del user_states[message.from_user.username]
    logging.info(message)
    markup = types.ForceReply()
    bot.send_message(message.chat.id, "Hey!", reply_markup=markup)


@bot.message_handler(commands=['bill'])
def handle_bill(message):
    if message.from_user.username in user_states:
        del user_states[message.from_user.username]

    logger.info(message)
    write_to_storage(message.from_user.username, message.text)
    bot.send_message(message.chat.id, "@{}, {}".format(message.from_user.username, command_dict[
                     message.text.strip('/')][0]["text"]), reply_markup=types.ForceReply(selective=True))

    invitation = render_invitation(
        service.user_chat_names(message.from_user.username))
    if invitation is not None:
        bot.send_message(message.chat.id, **invitation)


@bot.message_handler(commands=['info'])
def handle_info(message):
    user_states[message.from_user.username] = rootInfoState
    handle_state(message)


@bot.message_handler(commands=['suggest'])
def handle_info(message):
    user_states[message.from_user.username] = rootSuggestState
    handle_state(message)


@bot.message_handler(commands=['settleup'])
def handle_info(message):
    user_states[message.from_user.username] = rootSettleupState
    handle_state(message)


@bot.message_handler(commands=['history'])
def handle_info(message):
    user_states[message.from_user.username] = rootHistoryState
    handle_state(message)


@bot.message_handler(func=lambda message: message.from_user.username is not None)
def handle_state(message):
    try:
        if message.from_user.username not in user_states:
            return handle_message(message)

        state = user_states[message.from_user.username].next_node(message)
        errmsg = state.next_check(message)
        if errmsg is None:
            bot.send_message(message.chat.id, **state.next_message(message))
            user_states[message.from_user.username] = state
        else:
            bot.send_message(message.chat.id, text=errmsg)
    except:
        traceback.print_exc()


def handle_message(message):
    logger.info(message)
    username = message.from_user.username

    if message.chat.title is not None:
        service._ensure_chat(message.chat.id, message.chat.title)
        service._ensure_user(username)
    else:
        service._ensure_chat(message.chat.id, message.chat.username)
        service._ensure_user(username, message.chat.id)
        service.update_user(username, message.chat.id)

    logger.info("User id: '{}', username: '{}'".format(
        message.from_user.id, username))
    key = message.from_user.username
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
                # bot.send_message(message.chat.id, "@{}, question sequence is over, answers are: {}".format(
                #     username, messages[1:]))
                total_amount = int(messages[3])
                payer = messages[1]
                for_users = messages[2]
                description = messages[3]
                for user in for_users:
                    service.create_transaction(payer, user, message.chat.id,
                                               amount=int(total_amount / len(for_users)), description=description)

        if "parser" in question:
            if question["parser"](message) is not None:
                parsed_message = question["parser"](message)
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


def write_to_storage(username, value):
    key = username
    if key not in storage or (isinstance(value, str) and value.startswith('/')):
        storage[key] = []

    storage[key].append(value)


bot.polling()
