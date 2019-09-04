""" command dispatcher. """

import ob

def dispatch(handler, event):
    if not event.txt:
        return
    event.parse()
    event.orig = event.orig or repr(handler)
    event._func = ob.get(handler.cmds, event.chk, None)
    res = None
    if event._func:
        res = event._func(event)
    event.show()
    return res
