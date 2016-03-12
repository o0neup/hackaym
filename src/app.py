# coding: utf-8
"""
created by artemkorkhov at 2016/03/12
"""


import logging

import requests

from flask import Flask, request

from src.handlers.ymauth import auth


logger = logging.getLogger(__name__)

app = Flask(__name__)
app.register_blueprint(auth)
app.config.from_object('settings')

app.logger.setLevel(logging.INFO)
r = requests.get(app.config["TELEGRAM"]["api_uri"].format(app.config["TELEGRAM"][
                 "token"], "setWebhook"), {"url": app.config["TELEGRAM"]["callback_uri"]})
print r.status_code

mem_storage = {}


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
        return r.json()
