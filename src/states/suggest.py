# coding=utf-8
import telebot
from telebot import types
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from src.model.service import ModelService
from base import Node
from src.helpers import optimal_settleup

engine = create_engine("postgres://localhost:5432/")
Session = sessionmaker(bind=engine)
session = Session()
service = ModelService(session)

def render_suggest(suggest_list):
    if len(suggest_list) > 0:
        return {
            "text": "\n".join(["{} -> {}: {} руб.".format(x,y,z) for x,y,z in suggest_list])
        }
    else:
        return {
            "text": "Можете переебаться бесплатно"
        }

def render_buttons(text, buttons_list):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, selective=True)
    for btn in buttons_list:
        markup.add(btn)
    return {
        "text": text,
        "reply_markup": markup
    }

privateSuggestState2 = Node(
    msgfunc=lambda x: render_suggest(optimal_settleup(service.total_balance(chat_name=x.text).items()))
)

privateSuggestState = Node(
    msgfunc=lambda x: render_buttons("@{} Choose chat".format(x.from_user.username), service.user_chat_names(x.from_user.username)),
    keyfunc=lambda x: True,
    edges={True: privateSuggestState2}
)


publicSuggestState = Node(
    msgfunc=lambda x: render_suggest(optimal_settleup(service.total_balance(chat_id=x.chat.id).items())),
)

rootSuggestState = Node(
    msgfunc=None,
    keyfunc=lambda x: x.chat.id > 0,
    edges = {True: privateSuggestState,
            False: publicSuggestState}
)

