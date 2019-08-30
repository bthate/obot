""" list of bots. """

import logging

from ob import Object
from ob.utils import get_name

def __dir__():
    return ("Fleet",)

class Fleet(Object):

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

    def echo(self, bid, channel, txt, mtype="chat"):
        b = self.get_bot(bid)
        if b._outputed:
            b._outqueue.put_nowait((bid, channel, txt, mtype))
        else:
            b.say(bid, channel, txt, mtype)

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
