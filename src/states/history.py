# coding=utf-8
import telebot
from telebot import types
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from src.model.service import ModelService
from base import Node
from src.core import session

service = ModelService(session)

def render_transactions(transactions):
    return {
        "text": "\n".join(["|".join(x.values()) for x in transactions])
    }

privateHistoryState = Node(
    msgfunc=lambda x: render_transactions(service.list_transactions(x.from_user.username))
)


publicHistoryState = Node(
    msgfunc=lambda x: render_transactions(service.list_transactions(chat_id=x.chat.id))
)

rootHistoryState = Node(
    msgfunc=None,
    keyfunc=lambda x: x.chat.id > 0,
    edges = {True: privateHistoryState,
            False: publicHistoryState}
)
