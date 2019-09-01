README
######

OBOT is a IRC/XMPP bot you can use to display RSS feeds, uses a timestamped 
JSON file backend to provide persistence, makes it possible to program your
own module enabling your own commands, is in the Public Domain and contains
no copyright or LICENSE.

download
========

clone the source.

:: 

 > git clone https://github.com/bthate/obot
 > cd obot
 > sudo python3 setup.py install

another option is to download with pip3 and install globally.

::

 > sudo pip3 install obot --upgrade

you can also use the install --user option of setup.py to do a local install.

::

 > python3 setup.py install obot --user



shell
=====

starting obot without arguments starts a shell.

the basic bot has 3 commands:

1) cmds to show available commands.
2) load to load a module that adds commands.
3) unload to unload a module and remove commands.

typing load/unload without arguments gives possible options:

::

 bart@dell:~/obot$ ./bin/obot
 > cmds
 cmds|load|unload
 > load
 entry|cmds|db|tasks|show|loader|mbox|user|wisdom|rss
 > unload
 entry|cmds|db|tasks|show|loader|mbox|user|wisdom|rss

you can use the -m option to have modules loaded at starttime:

::

 bart@okdan:~$ obot -m entry,tasks
 > ps
 1    1s       Task(CLI.select)
 > log first entry to log
 ok 1
 > find log
 0 first entry to log

obot also provides the ob program that can be used as a command line shell program.

::

 bart@okdan:~$ ob v
 OBOT 7

standalone shell is provided by the obs program and standard daemonized version 
with the obd program.

modules
=======

possbile modules to load are:

::

 ob - save/load JSON files.
 bot - bot base class.
 clock - timer, repeater.
 cmds - show list of commands.
 command - parse string into command.
 db - object query.
 entry - log and todo commands.
 errors - basic OB exceptions.
 fleet - list of bots.
 handler - event callback dispatcher.
 kernel - runtime objects and boot code.
 loader - module loader.
 shell - shell functions.
 show - show runtime data.
 tasks - OB threads (tasks).
 term - terminal functions.
 times - file related utility.
 trace - traceback functions.
 types - OB types.
 user - user management.
 utils - file related utility.
 obot - object bot
 irc - IRC bot.
 mbox - email to object scanner.
 rss - rss feed fetcher.
 udp - udp to channel relay
 wisdom - wijsheid, wijs !
 xmpp - XMPP bot for obot.

rss
===

add url.

::

 > obot -m rss rss https://news.ycombinator.com/rss
 ok 1

you can use the find command to see what urls are registered:

::

 > obot -m db find rss rss
 0 https://news.ycombinator.com/rss

irc
===

the default bot just starts the shell, if you want to connect to IRC or XMPP
use the -p (prompt) option to provide connection arguments,  for IRC this is <server> <channel> <nick>>.

::

 > obot -m irc -p localhost \#obot obot


you can use the -b option to start the bot in the background and logfiles can be found in ~/.obot/logs.


users
=====

the default shell user is root@shell and gives access to all the commands that are available.
you can use the --owner option to set the owner of the bot to your own userhost.

if the bot joined the channel, it won't listen to you on default, you need to add the irc user to the bot.
the bot caches the userhosts needed to use in the meet command, so you can use the nickname instead of the full userhost.

::

 > meet bart
 ~bart@localhost added.


you can also use the full userhost as a argument to meet.

::

 > meet user@server
 user user@server created



programming
===========

if you want to add your own modules to the bot, you can put you .py files in a "mods" directory and use the -m option to point to that directory.

basic code is a function that gets an event as a argument.

::

 def command(event):
     << your code here >>

to give feedback to the user use the event.reply(txt) method.

:: 

 def command(event):
     event.reply("yooo %s" % event.origin)

to be able to handle the event it needs orig, origin and txt attributes set. 
the orig attribute is a string of the bot's repr, it is used to identify the bot to give the reply to.
one can use the bot's event method to create a basic event to use.

the event most important attributes are:

1) channel - the channel to display the response in.
2) orig - a repr() of the bot this event originated on
3) origin - a userhost of the user who created the event.
4) txt - the text the event is generated with. 

the event.parse() method takes a txt argument to parse the text into an
event.

::

 event = Event()
 event.parse("cmds")
 event.orig = repr(bot)
 event.origin = "root@shell"

have func coding ;]

ob
==

.. autosummary::
    :toctree: code
    :template: module.rst

    ob
    ob.clock
    ob.cmds
    ob.command
    ob.db
    ob.errors
    ob.fleet
    ob.handler
    ob.kernel
    ob.loader
    ob.shell
    ob.show
    ob.tasks
    ob.term
    ob.times
    ob.trace
    ob.types
    ob.user
    ob.utils

obot
====

.. autosummary::
    :toctree: code
    :template: module.rst

    obot
    obot.irc
    obot.mbox
    obot.rss
    obot.stats
    obot.udp
    obot.xmpp
    obot.wisdom

contact
=======

you can contact me on IRC/freenode/#dunkbots.

::

    | Bart Thate (bthate@dds.nl, thatebart@gmail.com)
    | botfather on #dunkbots irc.freenode.net
