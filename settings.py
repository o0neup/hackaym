# coding: utf-8
"""
created by artemkorkhov at 2016/03/11
"""

import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


BOT_TOKEN = "**SECRET**"


TELEGRAM = {
    "token": "185093347:AAHbhPcP3xPj7kiL3vpBUxM1lcxqmQR9WH8",
    "api_uri": "https://api.telegram.org/bot{}/{}",
    "callback_uri": "https://mrxmoscow.com:5000/aaa"
}


try:
    from settings_local import *
except ImportError:
    pass
