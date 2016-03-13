# coding: utf-8
"""
created by artemkorkhov at 2016/03/12
"""

import logging

from flask import redirect, render_template, request
from flask.blueprints import Blueprint

from sqlalchemy.exc import IntegrityError

from yandex_money.api import Wallet

from src.core import session
from src.bot import bot
from src.model.service import ModelService
from settings import YM_CLIENT_ID, BASE_URL, REDIRECT_TO


logger = logging.getLogger(__name__)

auth = Blueprint("auth", import_name=__name__)


@auth.route("/oauth_code")
def oauth_confirm():
    code = request.args.get("code")
    user_id = request.args.get("user_id")
    if not code:
        raise ValueError("The code is missing, and it's sucks :(")
    ym_redirect_url = "{}/{}".format(BASE_URL, REDIRECT_TO)
    token = Wallet.get_access_token(client_id=YM_CLIENT_ID, code=code,
                                    redirect_uri=ym_redirect_url)
    account_info = Wallet(access_token=token['access_token']).account_info()

    service = ModelService(session)
    try:
        service.add_wallet(username=user_id, auth_token=token['access_token'],
                           account_id=int(account_info["account"]))
    except IntegrityError:
        return redirect("{}/auth_confirmed?user_id={}".format(BASE_URL, user_id))
    except Exception as e:  # TODO handle exceptions with invalid user_id!
        logger.exception(e)
        return redirect("{}/auth_failed?user_id={}&error={}".format(BASE_URL, user_id, e))
    return redirect("{}/auth_confirmed?user_id={}".format(BASE_URL, user_id))


@auth.route("/auth_confirmed")
def auth_confirmed():
    user_id = request.args.get("user_id")

    if user_id:
        service = ModelService(session)
        chat_id = service.user_chat(username=user_id)
        bot.send_message(chat_id=chat_id, text="Счет Яндекс.Денег успешно добавлен")
    return render_template("confirm.html")


@auth.route("/auth_failed")
def auth_failed():
    user_id = request.args.get("user_id")
    error = request.args.get("error")
    logger.exception(error)

    if user_id:
        service = ModelService(session)
        chat_id = service.user_chat(username=user_id)
        bot.send_message(chat_id=chat_id,
                         text="При авторизации в Яндекс.Деньгах возникла ошибка :(")
    return render_template("failed.html")
