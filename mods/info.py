""" runtime information. """

import os

def pid(event):
    event.reply(str(os.getpid()))
