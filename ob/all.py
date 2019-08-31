""" import all sub modules. """

import ob
import ob.utils
import ob.user
import ob.fleet
import ob.db
import ob.loader
import ob.handler
import ob.kernel
import ob.command
import ob.cmds
import ob.errors
import ob.shell
import ob.tasks
import ob.term
import ob.trace
import ob.types
import ob.clock

def init():
    from ob.kernel import k
    for mn in __dir__():
        k.walk("ob.%s" % mn)

def __dir__():
    return ("clock",
            "cmds",
            "command",
            "db",
            "errors",
            "fleet",
            "handler",
            "kernel",
            "loader",
            "shell",
            "show",
            "tasks",
            "term",
            "times",
            "trace",
            "types",
            "user",
            "utils")
