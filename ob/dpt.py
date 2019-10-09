""" command dispatcher. """

import logging
import ob
import string

from ob.utl import get_name

def dispatch(handler, event):
    if not event or not event.txt:
        event.ready()
        return
    event.parse(event.txt)
    event.orig = event.orig or repr(handler)
    event._func = handler.get_cmd(event.chk)
    if event._func:
        event._func(event)
        event.show()
    event.ready()
