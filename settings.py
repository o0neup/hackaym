# coding: utf-8
"""
created by artemkorkhov at 2016/03/11
"""

import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_URL = "https://mrxmoscow.com"


PSQL = "postgres://hackaym:hackamakaka@localhost:5432/ym"

REDIRECT_TO = "oauth_code"

TELEGRAM = {
    "token": "185093347:AAHbhPcP3xPj7kiL3vpBUxM1lcxqmQR9WH8",
    "api_uri": "https://api.telegram.org/bot{}/{}",
    "callback_uri": "https://mrxmoscow.com/aaa"
}


YM_SCOPE = ["account-info", "operation-details", "payment-p2p"]


try:
    from settings_local import *
except ImportError:
    pass
