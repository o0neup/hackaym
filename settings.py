# coding: utf-8
"""
created by artemkorkhov at 2016/03/11
"""

import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_URL = "https://mrxmoscow.com"


PSQL = "postgres://hackaym:hackamakaka@localhost:5432/ym"

APP_NAME = "ymhacka"

REDIRECT_TO = "oauth_code"

TELEGRAM = {
    "token": "171350837:AAHZCrB8sr8naeAo_2G4761PTqwvx22cBZg",
    "api_uri": "https://api.telegram.org/bot{}/{}",
    "callback_uri": "https://mrxmoscow.com/aaa"
}


YM_SCOPE = ["account-info", "operation-details", "payment-p2p"]
try:
    from settings_local import *
except ImportError:
    pass
