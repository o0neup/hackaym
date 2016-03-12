# coding: utf-8
"""
created by artemkorkhov at 2016/03/11
"""

import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


BOT_TOKEN = "**SECRET**"


try:
    from settings_local import *
except ImportError:
    pass