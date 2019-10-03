""" list of bots. """

import logging
import ob

from ob.pst import Persist
from ob.utl import get_name

def __dir__():
    return ("Fleet",)

class Fleet(Persist):

    def __init__(self):
        super().__init__()
        self.bots = []

    def __iter__(self):
        return iter(self.bots)

    def add(self, bot):
        if bot not in self.bots:
            logging.warning("add %s" % get_name(bot))
            self.bots.append(bot)
        return self

    def announce(self, txt):
        for b in self.bots:
            b.announce(str(txt))
        else:
            ob.k.raw(txt)

    def echo(self, bid, channel, txt, mtype="chat"):
        b = self.get_bot(bid)
        b.say(channel, txt, mtype)

    def get_bot(self, bid):
        res = None
        for b in self.bots:
            if str(bid) in repr(b):
                res = b
                break
        return res

    def match(self, m):
        res = None
        for b in self.bots:
            if m.lower() in repr(b):
                res = b
                break
        return res

    def remove(self, bot):
        self.bots.remove(bot)
