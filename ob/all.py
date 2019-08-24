""" import all sub modules. """

import ob
import ob.utils
import ob.user
import ob.fleet
import ob.db
import ob.entry
import ob.loader
import ob.handler
import ob.kernel
import ob.bot
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
        k.walk(mn)

def __dir__():
    return ("bot",
            "clock",
            "cmds",
            "command",
            "db",
            "entry",
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
