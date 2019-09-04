""" command dispatcher. """

def dispatch(handler, event):
    if not event.txt:
        return
    event.parse()
    event.orig = event.orig or repr(h)
    event._func = ob.get(handler.cmds, event.chk, None)
    res = None
    if event._func:
        res = event._func(e)
    event.show()
    return res
