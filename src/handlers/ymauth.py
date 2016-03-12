# coding: utf-8
"""
created by artemkorkhov at 2016/03/12
"""

import logging

from flask import redirect, render_template, request
from flask.blueprints import Blueprint

from sqlalchemy.exc import IntegrityError

from yandex_money.api import Wallet

from src.app import session
from src.model.service import ModelService
from settings import YM_SCOPE, YM_CLIENT_ID, BASE_URL, REDIRECT_TO


logger = logging.getLogger(__name__)

BP_NAME = "auth"
auth = Blueprint("auth", import_name=__name__)


def get_auth_url(user_id, code_redirect_uri=REDIRECT_TO):
    """
    :param user_id:
    :param code_redirect_uri:
    :return:
    """
    redirect_url = "{}/{}/{}?user_id={}".format(BASE_URL, BP_NAME, code_redirect_uri, user_id)
    return Wallet.build_obtain_token_url(client_id=YM_CLIENT_ID, redirect_uri=redirect_url,
                                         scope=YM_SCOPE)


@auth.route("/oauth_code")
def oauth_confirm():
    code = request.args.get("code")
    user_id = request.args.get("user_id")
    if not code:
        raise ValueError("The code is missing, and it's sucks :(")
    ym_redirect_url = "{}/{}/{}".format(BASE_URL, BP_NAME, REDIRECT_TO)
    token = Wallet.get_access_token(client_id=YM_CLIENT_ID, code=code,
                                    redirect_uri=ym_redirect_url)
    account_info = Wallet(access_token=token['access_token']).account_info()

    service = ModelService(session)
    try:
        service.create_user(uid=user_id, auth_token=token['access_token'],
                            account_id=int(account_info["account"]))
    except IntegrityError:
        return redirect("{}/{}/auth_confirmed".format(BASE_URL, BP_NAME))
    except Exception as e:  # TODO handle exceptions with invalid user_id!
        logger.exception(e)
        return redirect("{}/{}/auth_failed".format(BASE_URL, BP_NAME))  # maybe parse error details into template
    return redirect("{}/{}/auth_confirmed".format(BASE_URL, BP_NAME))


@auth.route("/auth_confirmed")
def auth_confirmed():
    return render_template("confirm.html")


@auth.route("/auth_failed")
def auth_failed():
    return render_template("failed.html")