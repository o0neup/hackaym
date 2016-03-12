# coding: utf-8
"""
created by artemkorkhov at 2016/03/12
"""


import logging

import requests

from flask import Flask, request, redirect, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from yandex_money.api import Wallet

from src.model.service import ModelService
from settings import YM_SCOPE, YM_CLIENT_ID, BASE_URL, REDIRECT_TO, PSQL


engine = create_engine(PSQL)
session = sessionmaker(bind=engine)()

app = Flask(__name__)
app.config.from_object('settings')

app.logger.setLevel(logging.INFO)
r = requests.get(app.config["TELEGRAM"]["api_uri"].format(app.config["TELEGRAM"][
                 "token"], "setWebhook"), {"url": app.config["TELEGRAM"]["callback_uri"]})
print r.status_code

mem_storage = {}


def get_auth_url(user_id, code_redirect_uri=REDIRECT_TO):
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
    ym_redirect_url = "{}/{}".format(BASE_URL, REDIRECT_TO)
    token = Wallet.get_access_token(client_id=YM_CLIENT_ID, code=code,
                                    redirect_uri=ym_redirect_url)
    account_info = Wallet(access_token=token['access_token']).account_info()

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
    return render_template("confirm.html")


@app.route("/auth_failed")
def auth_failed():
    return render_template("failed.html")


@app.route('/aaa', methods=["POST"])
def handle():
    app.logger.info(request.json)

    if "message" in request.json:
        message = request.json["message"]
        if message["chat"]["type"] == "private" and "text" in message:
            handle_private_message(message)
        elif message["chat"]["type"] == "group" and "text" in message:
            handle_group_message(message)
    else:
        return
    return "Ok"


def handle_private_message(message):
    return "Ok"


def handle_group_message(message):
    if message["text"].startswith("/bill"):
        mem_storage[message["from"]["username"]] = []
        r = requests.post(app.config["TELEGRAM"]["api_uri"].format(app.config["TELEGRAM"]["token"], "sendMessage"),
                      data={"chat_id": message["chat"]["id"], "text": u"Привет, @{}".format(message["from"]["username"]), "reply_to_message_id": message[
                          "message_id"], "reply_markup": '{"force_reply": true, "selective": true}'}
                      )
    return


if __name__ == "__main__":
    print get_auth_url(10000)
