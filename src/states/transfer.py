# coding=utf-8
from telebot import types

from src.model.service import ModelService
from src.states.base import Node
from src.helpers import optimal_settleup
from src.model.money import MoneyService
import re

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

def render_suggest_buttons(message, chat_id):
    settleup_scheme = optimal_settleup(service.total_balance(chat_id=chat_id).items())
    settleup_scheme = filter(lambda x: service.has_wallet(x[0]) and service.has_wallet(x[1]), settleup_scheme)

    buttons = ["{} -> {}: {} руб.".format(*x) for x in settleup_scheme]
    # buttons.append("Другой вариант")

    return render_buttons("@{} Мы предлагаем следующие варианты погашения долгов"
                          .format(message.from_user.username), buttons)

def candidates(chat_id=None, chart_name=None, user_id=None):
    users = set(service.total_balance(chat_id=chat_id, chat_name=chart_name).keys()) - {user_id}
    return filter(lambda x: service.has_wallet(x), users)

def handleMoney(message):
    match = re.match("(.*) -> (.*): (.*) руб.", message.text.encode("utf-8"))
    from_name = match.group(1)
    to_name = match.group(2)
    amount = int(float(match.group(3)))

    moneyServiceFrom = MoneyService(from_name)
    moneyServiceTo = MoneyService(to_name)

    if not moneyServiceFrom._has_enough(amount):
        return {"text":"Зарабатывать сначала научись, потом долги отдавай"}

    flag, request = moneyServiceFrom.issue_payment(moneyServiceTo, amount)

    if not flag:
        return {"text":"И немедленно выпил"}

    #TODO ТЕМА СОБЕРИСЬ

cvcConfirmState = Node(
    msgfunc=lambda x: None#TODO здесь надо cvc послать дальше
)

firstMoneyState = Node(
    msgfunc=handleMoney,
    keyfunc=True,
    edges={True:cvcConfirmState}
)

suggestedNochatState = Node(
    msgfunc=lambda x:render_suggest_buttons(x, service.chat_id(privateTransferState.storage[x.from_user.username].text)),
    keyfunc=True,
    edges={
        True: firstMoneyState
    }
)

privateTransferState = Node(
    msgfunc=lambda x: render_buttons("@{} Выберите чат".format(x.from_user.username), service.user_chat_names(x.from_user.username)),
    keyfunc=lambda x: True,
    edges={True: suggestedNochatState}
)

publicTransferState = Node(
    msgfunc=lambda x: {"text": "Для перевода через Яндекс.Деньги напишите, пожалуста, мне в личку. Тут я стесняюсь"},
)

poorTransferStare = Node (
    msgfunc=lambda x: {"text": "Напишите мне и мы добавим ваш Яндекс.Кошелек к вашему аккаунту, а то у вас пока нет"}
)

rootTransferState = Node(
    msgfunc=None,
    keyfunc=lambda x: (x.chat.id > 0, service.has_wallet(x.from_user.username)),
    edges={(True, True): privateTransferState,
           (False, False): publicTransferState,
        (True,False): poorTransferStare,
        (False,False): poorTransferStare}
)

