from telebot import types

from src.model.service import ModelService
from src.states.base import Node

from src.core import session

service = ModelService(session)


def render_balance(balance_dict):
    return {
        "text": "\n".join(["{}: {}".format(x,y) for x,y in balance_dict.items()])
    }


def render_buttons(text, buttons_list):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for btn in buttons_list:
        markup.add(btn)
    return {
        "text": text,
        "reply_markup": markup
    }

privateInfoState2 = Node(
    msgfunc=lambda x: render_balance(service.total_balance(chat_name=x.text))
)

privateInfoState = Node(
    msgfunc=lambda x: render_buttons("Choose chat", service.user_chat_names(x.from_user.id)),
    keyfunc=lambda x: True,
    edges={True: privateInfoState2}
)

publicInfoState = Node(
    msgfunc=lambda x: render_balance(service.total_balance(chat_id=x.chat.id)),
)

rootInfoState = Node(
    msgfunc=None,
    keyfunc=lambda x: x.chat.id > 0,
    edges={True: privateInfoState,
           False: publicInfoState}
)

