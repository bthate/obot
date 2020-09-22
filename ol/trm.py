# OLIB - object library
#
#

import atexit
import sys
import termios

resume = {}

def execute(main):
    termsave()
    try:
        main()
    except KeyboardInterrupt:
        print("")
    except PermissionError:
        print("you need root permissions.")
    finally:
        termreset()

def termsetup(fd):
    return termios.tcgetattr(fd)

def termreset():
    if "old" in resume:
        termios.tcsetattr(resume["fd"], termios.TCSADRAIN, resume["old"])

def termsave():
    try:
        resume["fd"] = sys.stdin.fileno()
        resume["old"] = termsetup(sys.stdin.fileno())
        atexit.register(termreset)
    except termios.error:
        pass
