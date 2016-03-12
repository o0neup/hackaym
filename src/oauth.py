# coding: utf-8
"""
created by artemkorkhov at 2016/03/12
"""

from flask import request, redirect, render_template

from yandex_money.api import Wallet

from src.app import app, session
from src.model.models import User
from src.model.service import ModelService
from settings import YM_SCOPE, YM_CLIENT_ID, BASE_URL, REDIRECT_TO


def get_auth_url(user_id, code_redirect_uri=REDIRECT_TO["CODE"]):
    """
    :param user_id:
    :param code_redirect_uri:
    :return:
    """
    redirect_url = "{}/{}?user_id={}".format(BASE_URL, code_redirect_uri, user_id)
    return Wallet.build_obtain_token_url(client_id=YM_CLIENT_ID, redirect_uri=redirect_url,
                                         scope=YM_SCOPE)


@app.route("/oauth_code")
def oauth_confirm():
    code = request.args.get("code")
    user_id = request.args.get("user_id")
    if not code:
        raise ValueError("The code is missing, and it's sucks :(")
    ym_redirect_url = "{}/{}".format(BASE_URL, REDIRECT_TO["TOKEN"])
    token = Wallet.get_access_token(client_id=YM_CLIENT_ID, code=code,
                                    redirect_uri=ym_redirect_url)
    account_info = Wallet(access_token=token).account_info()

    service = ModelService(session)
    try:
        service.create_user(uid=user_id, auth_token=token,
                            account_id=int(account_info["account"]))
    except Exception as e:  # TODO handle exceptions with invalid user_id!
        print "Ololo, cannot save user"
        raise e  # TODO handle general exception with redirect
    else:
        redirect("/auth_confirmed")


@app.route("/auth_confirmed")
def auth_confirmed():
    render_template()


if __name__ == '__main__':
    print get_auth_url(user_id=10000)

