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
