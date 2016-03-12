# coding: utf-8
"""
created by artemkorkhov at 2016/03/12
"""

from flask import request

from yandex_money.api import Wallet

from src.app import app, session
from src.model.models import User
from settings import YM_SCOPE, YM_CLIENT_ID, BASE_URL, REDIRECT_TO


def get_auth_url(code_redirect_uri=REDIRECT_TO["CODE"]):
    """
    :param code_redirect_uri:
    :return:
    """
    redirect_url = "{}/{}".format(BASE_URL, code_redirect_uri)
    return Wallet.build_obtain_token_url(client_id=YM_CLIENT_ID, redirect_uri=redirect_url,
                                         scope=YM_SCOPE)


@app.route("/oauth_code")
def oauth_confirm():
    code = request.args.get("code")
    if not code:
        raise ValueError("The code is missing, and it's sucks :(")
    redirect_url = "{}/{}".format(BASE_URL, REDIRECT_TO["TOKEN"])
    token = Wallet.get_access_token(client_id=YM_CLIENT_ID, code=code,
                                    redirect_uri=redirect_url)
    raise NotImplementedError