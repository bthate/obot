""" command dispatcher. """

import logging
import ob
import string

from ob.err import ENOTXT
from ob.utl import get_name

def dispatch(handler, event):
    try:
        event.parse()
    except ENOTXT:
        event.ready()
        return
    event._func = handler.get_cmd(event.chk)
    event.orig = event.orig or repr(handler)
    if event._func:
        event._func(event)
        event.show()
    event.ready()
