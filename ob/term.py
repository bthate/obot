""" terminal functions. """

import atexit
import sys
import termios

resume = {}

def __dir__():
    return ("reset", "save")

def reset():
    if "old" in resume:
        termios.tcsetattr(resume["fd"], termios.TCSADRAIN, resume["old"])

def save():
    resume["fd"] = sys.stdin.fileno()
    resume["old"] = setup(sys.stdin.fileno())
    atexit.register(reset)

def setup(fd):
    old = termios.tcgetattr(fd)
    return old
