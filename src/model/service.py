# coding: utf-8

from models import User, Transaction, Chat, as_dict
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
import logging
import datetime
from sqlalchemy import or_
from collections import defaultdict
from sqlalchemy.orm.exc import NoResultFound


__author__ = 'ffuuugor'

logger = logging.getLogger(__name__)


class ModelService(object):

    def __init__(self, session):
        self.session = session

    def _ensure_user(self, username):
        try:
            self.session.query(User).filter(User.id == username).one()
        except NoResultFound:
            self.create_user(username)

    def _ensure_chat(self, chat_id):
        try:
            self.session.query(Chat).filter(Chat.id == chat_id).one()
        except NoResultFound:
            self.create_chat(chat_id)

    def chat_id(self, chat_name):
        chat = self.session.query(Chat).filter(Chat.name == chat_name).one()
        return chat.id

    def create_user(self, username, auth_token=None, account_id=None):
        user = User(id=username, auth_token=auth_token, account_id=account_id)
        self.session.add(user)
        self.session.commit()

    def add_wallet(self, username, auth_token=None, account_id=None):
        self._ensure_user(username)

        user = self.session.query(User).filter(User.id == username).one()

        if user.auth_token is not None or user.account_id is not None:
            logger.warning("User already has valid wallet. Overriding")

        user.auth_token = auth_token
        user.account_id = account_id
        self.session.add(user)
        self.session.commit()

    def create_chat(self, chat_id, name=None):
        chat = Chat(id=chat_id, name=name)
        self.session.add(chat)
        self.session.commit()

    def update_chat(self, chat_id, name):
        chat = self.session.query(Chat).filter(Chat.id == chat_id).one()
        chat.name = name
        self.session.add(chat)
        self.session.commit()

    def create_transaction(self, from_username, to_username, chat_id, amount, date=None, description=None):
        self._ensure_user(from_username)
        self._ensure_user(to_username)
        self._ensure_chat(chat_id)

        if date is None:
            date = datetime.datetime.now()

        transaction = Transaction(from_acc_id=from_username, to_acc_id=to_username, chat_id=chat_id,
                                  amount=amount, date=date, description=description)
        self.session.add(transaction)
        self.session.commit()

    def user_chat_names(self, username):
        self._ensure_user(username)
        chats = self.session.query(Transaction, Chat)\
            .filter(Transaction.chat_id == Chat.id)\
            .filter(or_(Transaction.from_acc_id == username, Transaction.to_acc_id == username)).distinct(Chat.name).all()

        return [chat[1].name for chat in chats]


    def list_transactions(self, username=None, chat_id=None, limit=10):
        if username is None and chat_id is None:
            raise ValueError("At least one of the following should not be null: username, chat_id")

        query = self.session.query(Transaction, Chat).filter(Transaction.chat_id == Chat.id).order_by(Transaction.date.desc())

        if username is not None:
            query = query.filter(or_(Transaction.from_acc_id == username, Transaction.to_acc_id == username))

        if chat_id is not None:
            query = query.filter(Transaction.chat_id == chat_id)

        result = query.limit(limit).all()
        return [as_dict(x, columns=["name", "description", "date", "from_acc_id", "to_acc_id"]) for x in result]

    def total_balance(self, username=None, chat_id=None, chat_name=None):
        if username is None and chat_id is None and chat_name is None:
            raise ValueError("At least one of the following should not be null: username, chat_id")

        if chat_name is not None:
            chat_id = self.session.query(Chat).filter(Chat.name == chat_name).one().id

        query = self.session.query(Transaction)

        if username is not None:
            query = query.filter(or_(Transaction.from_acc_id == username, Transaction.to_acc_id == username))

        if chat_id is not None:
            query = query.filter(Transaction.chat_id == chat_id)

        accountable_transactions = query.all()
        if username is None:
            users = set([x.from_acc_id for x in accountable_transactions])\
                    | set([x.to_acc_id for x in accountable_transactions])
        else:
            users = {username}

        balances = defaultdict(int)
        for transaction in accountable_transactions:
            balances[transaction.from_acc_id] -= transaction.amount
            balances[transaction.to_acc_id] += transaction.amount

        # user_object = self.session.query(User).filter(User.id.in_(users)).all()
        # names = {u.id: u.name}

        return {key: val for key, val in balances.iteritems() if key in users}


if __name__ == '__main__':
    engine = create_engine("postgres://localhost:5432/ym")
    Session = sessionmaker(bind=engine)

    session = Session()

    service = ModelService(session)
    # service.create_chat(-147219024,"Trump")
    service.create_transaction(82493396, 112, -147219024, 350)
    # print service.total_balance(chat_id=101)
