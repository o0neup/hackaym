# coding: utf-8
"""
created by artemkorkhov at 2016/03/12
"""


import logging

import requests

from flask import Flask, request


app = Flask(__name__)
app.config.from_object('settings')

app.logger.setLevel(logging.INFO)
r = requests.get(app.config["TELEGRAM"]["api_uri"].format(app.config["TELEGRAM"][
                 "token"], "setWebhook"), {"url": app.config["TELEGRAM"]["callback_uri"]})
print r.status_code


@app.route('/aaa', methods=["POST"])
def handle():
    app.logger.info(request.json)

    if "message" in request.json:
        message = request.json["message"]
        if message["chat"]["type"] == "private":
            handle_private_message(message)
        elif message["chat"]["type"] == "group":
            handle_group_message(message)
    else:
        return
    return "Ok"


def handle_private_message(message):
    pass

def handle_group_message(message):
    pass
