# coding: utf-8
"""
created by artemkorkhov at 2016/03/11
"""

import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_URL = "https://mrxmoscow.com"


REDIRECT_TO = {
    "CODE": "oauth_code",
    "TOKEN": "oauth_token"
}


TELEGRAM = {
    "token": "185093347:AAHbhPcP3xPj7kiL3vpBUxM1lcxqmQR9WH8",
    "api_uri": "https://api.telegram.org/bot{}/{}",
    "callback_uri": "https://mrxmoscow.com/aaa"
}


YM_SCOPE = ["account-info", "operation-details", "payment-p2p", "payment-shop"]


try:
    from settings_local import *
except ImportError:
    pass
