# coding: utf-8
"""
created by artemkorkhov at 2016/03/12
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import PSQL


engine = create_engine(PSQL)
session = sessionmaker(bind=engine)()
