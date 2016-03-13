# coding=utf-8
import telebot
from telebot import types
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from src.model.service import ModelService
from base import Node
from src.helpers import optimal_settleup
import re

engine = create_engine("postgres://localhost:5432/")
Session = sessionmaker(bind=engine)
session = Session()
service = ModelService(session)

def render_buttons(text, buttons_list):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for btn in buttons_list:
        markup.add(str(btn))
    return {
        "text": text,
        "reply_markup": markup
    }

def render_suggest_buttons(message, chat_id):
    settleup_scheme = optimal_settleup(service.total_balance(chat_id=chat_id).items())
    buttons = ["{} -> {}: {} руб.".format(*x) for x in settleup_scheme]
    buttons.append("Другой вариант")

    return render_buttons("Мы предлагаем следующие варианты погашения долгов", buttons)

def shortSettle(message, chat_id):
    match = re.match("(.*) -> (.*): (.*) руб.", message.text.encode("utf-8"))
    from_name = match.group(1)
    to_name = match.group(2)
    amount = int(float(match.group(3)))
    service.create_transaction(from_name, to_name, chat_id, -amount, description="Ручной settle up")

    return {
        "text": "Информация успешно записана. Надеюсь, вы не соврали ;)"
    }

def longSettle(message):
    from_user_id = message.from_user.id
    to_user_id = int(chooseRecipientState.storage[from_user_id].text)
    amount = int(chooseAmountState.storage[from_user_id].text)
    service.create_transaction(from_user_id, to_user_id, message.chat.id, -amount, description="Ручной settle up")

    return {
        "text": "Информация успешно записана. Надеюсь, вы не соврали ;)"
    }

def longSettle2(message):
    from_user_id = message.from_user.id
    to_user_id = int(chooseRecipientState.storage[from_user_id].text)
    amount = int(chooseAmountState.storage[from_user_id].text)
    service.create_transaction(from_user_id, to_user_id,
                               service.chat_id(privateSettleupState.storage[message.from_user.id].text),
                               -amount, description="Ручной settle up")

    return {
        "text": "Информация успешно записана. Надеюсь, вы не соврали ;)"
    }

def candidates(chat_id=None, chart_name=None, user_id=None):
    return set(service.total_balance(chat_id=chat_id, chat_name=chart_name).keys()) - {user_id}

firstDoneState = Node(
    msgfunc=lambda x: shortSettle(x, x.chat.id)
)

firstDoneState2 = Node(
    msgfunc=lambda x: shortSettle(x, service.chat_id(privateSettleupState.storage[x.from_user.id].text))
)

secondDoneState = Node(
    msgfunc=longSettle
)

secondDoneState2 = Node(
    msgfunc=longSettle2
)

chooseAmountState = Node(
    msgfunc=lambda x: {"text":"Введите сумму", "reply_markup": types.ForceReply()},
    keyfunc=lambda x: True,
    edges={True: secondDoneState}
)

chooseAmountState2 = Node(
    msgfunc=lambda x: {"text":"Введите сумму", "reply_markup": types.ForceReply()},
    keyfunc=lambda x: True,
    edges={True: secondDoneState2}
)

chooseRecipientState = Node(
    msgfunc=lambda x: render_buttons("Кому вы хотите отдать деньги?", candidates(chat_id=x.chat.id, user_id=x.from_user.id)),
    keyfunc=lambda x: True,
    edges={True: chooseAmountState}
)

chooseRecipientState2 = Node(
    msgfunc=lambda x: render_buttons("Кому вы хотите отдать деньги?",
                                     candidates(chart_name=privateSettleupState.storage[x.from_user.id].text,
                                                user_id=x.from_user.id)),
    keyfunc=lambda x: True,
    edges={True: chooseAmountState2}
)

suggestedNochatState = Node(
    msgfunc=lambda x:render_suggest_buttons(x, service.chat_id(privateSettleupState.storage[x.from_user.id].text)),
    keyfunc=lambda x: x.text == "Другой вариант".decode("utf-8"),
    edges={
        True: chooseRecipientState2,
        False: firstDoneState2
    }
)

privateSettleupState = Node(
    msgfunc=lambda x: render_buttons("Choose chat", service.user_chat_names(x.from_user.id)),
    keyfunc=lambda x: True,
    edges={True: suggestedNochatState}
)

publicSettleupState = Node(
    msgfunc=lambda x:render_suggest_buttons(x, x.chat.id),
    keyfunc=lambda x: x.text == "Другой вариант".decode("utf-8"),
    edges={
        True: chooseRecipientState,
        False: firstDoneState
    }
)

rootSettleupState = Node(
    keyfunc=lambda x: x.chat.id > 0,
    edges = {True: privateSettleupState,
            False: publicSettleupState})
