README
######

| OBOT is a IRC/XMPP bot you can use to display RSS feeds.
| OBOT uses a timestamped JSON file backend to provide persistence.
| OBOT makes it possible to program your own module enabling your own commands.
| OBOT is in the Public Domain and contains no copyright or LICENSE.

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

the default bot starts the IRC bot, you can disable this with the -x bot.irc option.
use server (-s), channel (-c) and nick (-n) options to connect to an IRC network

::

    > obot -m irc -p localhost -c \#obot -n obot


you can use the -b option to start the bot in the background and logfiles can be found in ~/.obot/logs.


users
=====

if the bot joined the channel, it won't listen to you on default, you need to add the irc user to the bot.
the bot caches the userhosts needed to use in the meet command, so you can use the nickname instead of the full userhost.

::

    > meet bart
    ~bart@localhost added.


you can also use the full userhost as a argument to meet.

::

    > meet user@server
    user user@server created


the default shell user is root@shell and gives access to all the commands that are available.
you can use the --owner option to set the owner of the bot to your own userhost.

cli
===

obot also provides the ob program that can be used as a command line shell program.

::

    bart@okdan:~$ ob v
    RSSBOT 12

stand alone shell is provided by the obs program and standard daemonized
version with the obd program.

::

shell
=====

starting RSSBOT without arguments starts a shell.

::

    bart@okdan:~$ obot -m entry
    > ps
    1    1s       Task(CLI.select)
    > log first entry to log
    ok 1
    > find log
    0 first entry to log

commands
========

available commands as of may 2019 are:

::

    cfg                      # show configuraton files.
    cmds                     # show list of commands.
    ed                       # show running threads.
    find                     # present a list of objects based on prompt input.
    fleet                    # show bots in the fleet.
    kill                     # kill a task.
    load                     # load a module
    log                      # log some text.
    meet                     # introduce a user.
    ps                       # show running tasks.
    rm                       # remove an object from the store.
    todo                     # enter something todo.
    undel                    # undelete an object.
    version                  # show version.

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

contact
=======

you can contact me on IRC/freenode/#dunkbots.

::

    | Bart Thate (bthate@dds.nl, thatebart@gmail.com)
    | botfather on #dunkbots irc.freenode.net
