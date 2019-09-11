""" command dispatcher. """

import logging
import ob
import string

from ob.utl import get_name

def dispatch(handler, event):
    if not event or not event.txt:
        return
    event.parse(event.txt)
    event.orig = event.orig or repr(handler)
    event._func = handler.get_cmd(event.chk)
    res = None
    if event._func:
        logging.debug("func %s" % get_name(event._func))
        res = event._func(event)
    event.show()
    event.ready()
    return res

dispatch.threaded = True
