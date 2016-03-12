from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String, Integer, Float, Enum, DateTime, Boolean, Time, Interval
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, backref
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'u'
    __table_args__ = {'schema': 'hackaym'}

    id = Column("id", Integer, primary_key=True)
    auth_token = Column("auth_token", String)
    account_id = Column("account_id", String)

class Chat(Base):
    __tablename__ = 'chat'
    __table_args__ = {'schema': 'hackaym'}

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)

class Transaction(Base):
    __tablename__ = 'transaction'
    __table_args__ = {'schema': 'hackaym'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    from_acc_id = Column("from_acc_id", Integer, ForeignKey(User.id))
    to_acc_id = Column("to_acc_id", Integer, ForeignKey(User.id))

    amount = Column("amount", Float)
    chat_id = Column("chat_id", Integer, ForeignKey(Chat.id))

    date = Column("date", DateTime)
    description = Column("description", String)

    chat = relationship(Chat)
    from_acc = relationship(User, foreign_keys=from_acc_id)
    to_acc = relationship(User, foreign_keys=to_acc_id)

if __name__ == '__main__':
    from sqlalchemy import create_engine
    from sqlalchemy import *
    sa_engine = create_engine("postgres://localhost:5432/")

    Base.metadata.create_all(sa_engine)


