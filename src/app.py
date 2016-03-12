# coding: utf-8
"""
created by artemkorkhov at 2016/03/12
"""


import logging

import requests

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine("postgres://localhost:5432/")
session = sessionmaker(bind=engine)()

app = Flask(__name__)
app.config.from_object('settings')

app.logger.setLevel(logging.INFO)
r = requests.get(app.config["TELEGRAM"]["api_uri"].format(app.config["TELEGRAM"][
                 "token"], "setWebhook"), {"url": app.config["TELEGRAM"]["callback_uri"]})
print r.status_code


@app.route('/aaa', methods=["POST"])
def handle():
    app.logger.info(request.json)
    print request.json()
    return "Ok"
