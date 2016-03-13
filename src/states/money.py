# coding: utf-8
"""
created by artemkorkhov at 2016/03/13
"""

from src.states.base import Node
from src.core import session
from src.model.service import ModelService


service = ModelService(session)


def render_invitation(users):
    """ Renders invitation to instantiate chat with bot
    :param users:
    :return:
    """
    known_users = set(service.get_known_users())
    _users = ', '.join(["@{}".format(u) for u in users if u not in known_users])
    return {
        "text": ("К сожалению, у {} не создан чат со мной, и мы не можем воспользоваться "
                 "клёвым функционалом Яндекс.Денег :( Создайте, пожалуйста, приватные чаты "
                 "со мной").format(_users)
    }


AskForRegister = Node(
    msgfunc=lambda x: render_invitation(service.user_chat_names(x.from_user.id)),
    keyfunc=None,
)
