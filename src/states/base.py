# coding: utf-8


class Node(object):
    def __init__(self, msgfunc=None, keyfunc=None, edges=None):
        self.msgfunc = msgfunc
        self.keyfunc = keyfunc
        self.edges = edges

    def next_node(self, message):
        if self.keyfunc is not None:
            return self.edges[self.keyfunc(message)]

    def next_message(self, message):
        if self.msgfunc is not None:
            return self.msgfunc(message)
