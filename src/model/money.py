# coding: utf-8
"""
created by artemkorkhov at 2016/03/13
"""

import logging
import time

from sqlalchemy.orm.exc import NoResultFound
from yandex_money.api import Wallet

from src.core import session
from src.model.models import User
from src.model.service import ModelService

from settings import APP_NAME


logger = logging.getLogger(__name__)


RESULT_CODES = {
    "success": "success",
    "refused": "refused",
    "hold_for_pickup": "hold_for_pickup",
    "illegal_params": "illegal_params",
    "illegal_param_to": "illegal_param_to",
    "illegal_param_amount": "illegal_param_amount",
    "payee_not_found": "payee_not_found",
    "authorization_reject": "authorization_reject",
}


class MoneyService(object):
    """ Basic YM service class. Instances have access to YM ops of one user
    """
    # TODO cache among one session?
    # TODO handle limits? https://money.yandex.ru/doc.xml?id=524834&lang=ru USER TYPE
    BALANCE_ENOUGH = "ENOUGH"
    BALANCE_MAYBE_ENOUGH = "MAYBE"
    BALANCE_NOT_ENOUGH = "NOT_ENOUGH"

    DEFAULT_REQUEST_PAYMENT = {
        "pattern_id": "p2p",
        "to": None,
        "amount_due": None,
        "comment": None,  # Is useful - payment description
        "message": None,  # Is useful - payment description
        "label": None,  # todo could be useful
        "codepro": False,
    }

    DEFAULT_PROCESS_PAYMENT = {
        "request_id": None,
        "money_source": None,  # todo careful - need to be able to choose
        "csc": None,  # todo if money_source is card - need to ask for csc
    }

    MAX_RETRIES = 3

    def __init__(self, user_id, comission=0.005, testmode=False, test_result="success"):
        self.service = ModelService(session)
        self.comission = comission
        try:
            self.user = self.service.session.query(User).filter(User.id == user_id).one()
        except NoResultFound:
            raise NoResultFound("No such user in system! Cannot be served; try to create user")
        self.wallet = Wallet(access_token=self.user.auth_token)

        self.process_retries = 1
        self.testmode = testmode
        self.test_result = test_result

    def _has_enough(self, required):
        """ Checks whether user has enough money to make a transfer.
        User can have one of three options:
        - has enough money on the acc at time of request. Status: "enough"
        - doesn't have enough money, but have linked bank cards, so payment is still possible to
        be processed. Status: "maybe"
        - doesn't have enough money and bank accs linked. Status: "not enough"
        :param required:
        :return str:
        """
        info = self.wallet.account_info()
        if info["balance"] < (required * (1 + self.comission)):
            if not info["cards_linked"]:
                return self.BALANCE_NOT_ENOUGH
            else:
                return self.BALANCE_MAYBE_ENOUGH
        else:
            return self.BALANCE_ENOUGH

    def issue_payment(self, to, amount, comment=None, label=APP_NAME):
        """ Issues payment of specified amount money from wallet holder to given user (to_id)
        :param to:
        :param amount:
        :param comment:
        :param label:
        :return:
        """
        # todo make default comment?
        self.process_retries = 1
        if not isinstance(to, self.__class__):
            raise TypeError("You must provide valid receiver! Must be {}, but given: {}".format(
                self.__class__, type(to)
            ))

        requests_opts = self.DEFAULT_REQUEST_PAYMENT.copy()
        requests_opts.update({
            "to": to.user.account_id,
            "amount_due": amount,
            "comment": comment or "",
            "message": comment or "",
            "label": label
        })
        if self.testmode:
            requests_opts.update({
                "test_payment": True,
                "test_result": self.test_result
            })
        try:
            request = self.wallet.request_payment(options=requests_opts)
        except Exception as e:
            raise e  # TODO handle this shit
        if request["status"] == "success":
            if not (request.get("wallet", {}).get("allowed") and not
                    request.get("cards", {}).get("allowed")):
                logger.error("Request is succeeded, but there are no allowed payment methods.")
                return None, request  # TODO ask for additional permissions
            else:
                return True, request
        else:
            return False, request

    def process_payment(self, payment_id, source, csc=None):
        """ Processes issued payment with given payment source.
        :param payment_id:
        :param source:
        :param csc:
        :return:
        """
        process_opts = self.DEFAULT_PROCESS_PAYMENT.copy()
        if source == "wallet":
            process_opts.update({
                "request_id": payment_id,
                "money_source": source
            })
        elif source == "card":
            if not csc or (isinstance(csc, basestring) and not csc.isdigit()):
                raise ValueError("CSC must be a valid 3-digits integer! Given: {}".format(csc))
            process_opts.update({
                "request_id": payment_id,
                "money_source": source,
                "csc": csc
            })
        if self.testmode:
            process_opts.update({
                "test_payment": True,
                "test_result": self.test_result
            })
        try:
            payment = self.wallet.process_payment(options=process_opts)
        except Exception as e:
            raise e  # TODO handle this
        if payment["status"] == "success":
            return True, payment
        elif payment["status"] == "in_progress" and self.process_retries > self.MAX_RETRIES:
            time.sleep(payment.get("next_retry", 0) * 1000)
            self.process_retries += 1
            return self.process_payment(payment_id, source, csc)
        else:
            return False, payment

    def phone_payment(self):
        # todo can be useful really. But not first priority :)
        raise NotImplementedError
