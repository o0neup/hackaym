# coding=utf-8
from telebot import types

from src.model.service import ModelService
from src.states.base import Node

from src.core import session

service = ModelService(session)

def render_buttons(text, buttons_list):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, selective=True)
    for btn in buttons_list:
        markup.add(btn)
    return {
        "text": text,
        "reply_markup": markup
    }

def candidates(chat_id=None, chart_name=None, user_id=None):
    return set(service.total_balance(chat_id=chat_id, chat_name=chart_name).keys()) - {user_id}

chooseRecipientState2 = Node(
    msgfunc=lambda x: render_buttons("@{} Кому вы хотите отдать деньги?".format(x.from_user.username),
                                     candidates(chart_name=privateTransferState.storage[x.from_user.username].text,
                                                user_id=x.from_user.username)),
    keyfunc=lambda x: True,
    edges={True: chooseAmountState2}
)

privateTransferState = Node(
    msgfunc=lambda x: render_buttons("@{} Выберите чат".format(x.from_user.username), service.user_chat_names(x.from_user.username)),
    keyfunc=lambda x: True,
    edges={True: chooseRecipientState2}
)

publicTransferState = Node(
    msgfunc=lambda x: "Для перевода через Яндекс.Деньги напишите, пожалуста, мне в личку. Тут я стесняюсь",
)

rootTransferState = Node(
    msgfunc=None,
    keyfunc=lambda x: x.chat.id > 0,
    edges={True: privateTransferState,
           False: publicTransferState}
)

