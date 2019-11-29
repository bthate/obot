from setuptools import setup

setup(
    name='obot',
    version='17',
    url='https://bitbucket.org/bthate/obot',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="Framework to program bots.",
    long_description="""OBOT is a IRC bot you can use to display RSS feeds, 
makes it possible to program your own module enabling your own commands, 
is in the Public Domain and contains no copyright or LICENSE.

download with pip3 and install globally.

 > sudo pip3 install obot --upgrade

clone the source:

 > git clone https://github.com/bthate/obot
 > cd obot
 > sudo python3 setup.py install

you can also use the install --user option of setup.py to do a local install.

 > python3 setup.py install obot --user

the default bot just starts the shell, if you want to connect to IRC use the -p (prompt) option to provide connection arguments
for IRC this is <server> <channel> <nick>>:

 > obot -m irc -p localhost \#obot obot


you can use the -b option to start the bot in the background and logfiles can be found in ~/.obot/logs.

obot contains the following modules:

 obot      - object bot framework.
 obot.edit - edit objects.
 obot.log  - log callback. 
 obot.irc  - irc bot.
 obot.mbox - mbox email.
 obot.rss  - feed to channel.
 obot.show - show runtime information.
 obot.udp  - udp to channel.
 obot.user - user management.

add url:

 > obot -m rss rss https://news.ycombinator.com/rss
 ok 1

you can use the find command to see what urls are registered:

 > obot -m db find rss rss
 0 https://news.ycombinator.com/rss

using udp to relay text into a channel, start the bot with -m udp and use
the obudp program to send text to the UDP to channel server:

 > tail -f ~/.obot/logs/ob.log | ./bin/obudp 

the default shell user is root@shell and gives access to all the commands that are available.
you can use the --owner option to set the owner of the bot to your own userhost.

if the bot joined the channel, it won't listen to you on default, you need to add the irc user to the bot.
the bot caches the userhosts needed to use in the meet command, so you can use the nickname instead of the full userhost:

 > meet bart
 ~bart@localhost added.

you can also use the full userhost as a argument to meet:

 > meet user@server
 user user@server created


if you want to add your own modules to the bot, you can put you .py files in a "mods" directory and use the -m option to point to that directory.

basic code is a function that gets an event as a argument:

 def command(event):
     << your code here >>

to give feedback to the user use the event.reply(txt) method:

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

the event.parse() method takes a txt argument to parse the text into an event:

 event = Event()
 event.parse("cmds")
 event.orig = repr(bot)
 event.origin = "root@shell"


have fun coding ;]


you can contact me on IRC/freenode/#dunkbots.

| Bart Thate (bthate@dds.nl, thatebart@gmail.com)
| botfather on #dunkbots irc.freenode.net
    
    
    """,
    long_description_content_type="text/markdown",
    license='Public Domain',
    zip_safe=True,
    install_requires=["ob"],
    packages=["obot"],
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: Public Domain',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 'Topic :: Utilities'
                ]
)
