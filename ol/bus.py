# OLIB - object library
#
#

import ol

class Bus(ol.Object):

    objs = []

    def __iter__(self):
        return iter(Bus.objs)

    def add(self, obj):
        Bus.objs.append(obj)

    def announce(self, txt, skip=None):
        for h in self.objs:
            if skip is not None and isinstance(h, skip):
                continue
            if "announce" in dir(h):
                h.announce(txt)

    def dispatch(self, event):
        for b in Bus.objs:
            if repr(b) == event.orig:
                b.dispatch(event)

    def by_orig(self, orig):
        for o in Bus.objs:
            if repr(o) == orig:
                return o

    def say(self, orig, channel, txt):
        for o in Bus.objs:
            if repr(o) == orig:
                o.say(channel, str(txt))

bus = Bus()
