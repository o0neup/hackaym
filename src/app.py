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


def handle():
    app.logger.info(request.json)
    print request.json
    return "Ok"

if __name__ == "__main__":
    app.run()
