""" command dispatcher. """

import logging
import ob
import string

from ob.utl import get_name

def dispatch(handler, event):
    if not event or not event.txt:
        event.ready()
        return
    event._func = handler.get_cmd(event.txt.split()[0])
    event.orig = event.orig or repr(handler)
    if event._func:
        event._func(event)
        event.show()
    event.ready()
