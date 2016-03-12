__author__ = 'ffuuugor'
from models import User, Transaction, Chat, as_dict
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
import logging
import datetime
from sqlalchemy import or_
from collections import defaultdict

logger = logging.getLogger(__name__)


class ModelService(object):

    def __init__(self, session):
        self.session = session

    def create_user(self, uid, auth_token=None, account_id=None):
        user = User(id=uid, auth_token=auth_token, account_id=account_id)
        self.session.add(user)
        self.session.commit()

    def add_wallet(self, uid, auth_token=None, account_id=None):
        user = self.session.query(User).filter(User.id == uid).one()

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

    def create_transaction(self, from_uid, to_uid, chat_id, amount, date=None, description=None):
        if date is None:
            date = datetime.datetime.now()

        transaction = Transaction(from_acc_id=from_uid, to_acc_id=to_uid, chat_id=chat_id,
                                  amount=amount, date=date, description=description)
        self.session.add(transaction)
        self.session.commit()

    def list_transactions(self, uid=None, chat_id=None, limit=10):
        if uid is None and chat_id is None:
            raise ValueError("At least one of the following should not be null: uid, chat_id")

        query = self.session.query(Transaction, Chat).filter(Transaction.chat_id == Chat.id).order_by(Transaction.date.desc())

        if uid is not None:
            query = query.filter(or_(Transaction.from_acc_id == uid, Transaction.to_acc_id == uid))

        if chat_id is not None:
            query = query.filter(Transaction.chat_id == chat_id)

        result = query.limit(limit).all()
        return [as_dict(x, columns=["name", "description", "date", "from_acc_id", "to_acc_id"]) for x in result]

    def total_balance(self, uid=None, chat_id=None):
        if uid is None and chat_id is None:
            raise ValueError("At least one of the following should not be null: uid, chat_id")

        query = self.session.query(Transaction)

        if uid is not None:
            query = query.filter(or_(Transaction.from_acc_id == uid, Transaction.to_acc_id == uid))

        if chat_id is not None:
            query = query.filter(Transaction.chat_id == chat_id)

        accountable_transactions = query.all()
        if uid is None:
            users = set([x.from_acc_id for x in accountable_transactions])\
                    | set([x.to_acc_id for x in accountable_transactions])
        else:
            users = {uid}

        balances = defaultdict(int)
        for transaction in accountable_transactions:
            balances[transaction.from_acc_id] -= transaction.amount
            balances[transaction.to_acc_id] += transaction.amount

        return {key: val for key, val in balances.iteritems() if key in users }


if __name__ == '__main__':
    engine = create_engine("postgres://localhost:5432/")
    Session = sessionmaker(bind=engine)

    # create a Session
    session = Session()

    service = ModelService(session)
    print service.total_balance(chat_id=110)
