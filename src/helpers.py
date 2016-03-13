__author__ = 'ffuuugor'
import itertools
import sys

def optimal_settleup(balances):
    """

    :param balances: [(uid, balance)]
    :return: [(from_uid, to_uid, amount)]
    """

    positive_balances = filter(lambda x: x[1] > 0, balances)
    negative_balances = filter(lambda x: x[1] < 0, balances)

    min_transacations = None
    min_length = sys.maxint
    for negative_perm in itertools.permutations(negative_balances):
        for positive_perm in itertools.permutations(positive_balances):
            positive_perm = list(positive_perm)

            transactions = []
            curr_positive_idx = 0

            for ntuple in negative_perm:
                curr_balance = ntuple[1]

                while curr_balance < 0:
                    if curr_balance + positive_perm[curr_positive_idx][1] < 0:
                        amount = positive_perm[curr_positive_idx][1]
                        to_user = positive_perm[curr_positive_idx][0]
                        curr_balance += positive_perm[curr_positive_idx][1]
                        curr_positive_idx += 1
                    else:
                        amount = -curr_balance
                        to_user = positive_perm[curr_positive_idx][0]
                        positive_perm[curr_positive_idx] = (positive_perm[curr_positive_idx][0],
                                                            positive_perm[curr_positive_idx][1] + curr_balance)
                        curr_balance = 0

                    transactions.append((ntuple[0], to_user, amount))

            if len(transactions) < min_length:
                min_length = len(transactions)
                min_transacations = transactions

    return min_transacations

# balances = {
#     "Anton": -201,
#     "Artem": -150,
#     "Ololosha": 0,
#     "Igor": 50,
#     "Alex": 300,
#     "Terebonka": 1
# }
#
# print optimal_settleup(balances.items())



