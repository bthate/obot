""" logging callback. """

from ob import k

def init():
    k.register(log_handler)

def log_handler(handler, event):
    if event.dolog:
        event.save()
