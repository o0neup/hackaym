# coding: utf-8


def default_fallback(message):
    return "Something wro"


class Node(object):

    def __init__(self, msgfunc=None, keyfunc=None, checkfunc=None, edges=None):
        self.msgfunc = msgfunc
        self.keyfunc = keyfunc
        self.checkfunc = checkfunc
        self.edges = edges
        self.storage = {}

    def next_node(self, message):
        self.storage[message.from_user.id] = message
        if self.keyfunc is not None:
            return self.edges[self.keyfunc(message)]

    def next_message(self, message):
        if self.msgfunc is not None:
            return self.msgfunc(message)

    def next_check(self, message):
        if self.checkfunc is not None:
            return self.checkfunc(message)
