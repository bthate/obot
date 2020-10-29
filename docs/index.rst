O B O T
#######

| Welcome to OBOT, the 24/7 channel daemon ! see https://pypi.org/project/obot/ - :ref:`source <source>`

OBOT is a pure python3 IRC chat bot that can run as a background daemon
for 24/7 a day presence in a IRC channel. It installs itself as a service so
you can get it restarted on reboot. You can use it to display RSS feeds, act as a
UDP to IRC gateway, program your own commands for it, have it log objects on
disk and search them and scan emails for correspondence analysis. OBOT uses
a JSON in file database with a versioned readonly storage. It reconstructs
objects based on type information in the path and uses a "dump OOP and use
OP" programming library where the methods are factored out into functions
that use the object as the first argument. 

OBOT is placed in the Public Domain and has no COPYRIGHT or LICENSE.

INSTALL
=======

installation is through pypi:

::

 $ sudo pip3 install obot

if the package doesn't update properly force a reinstall:

::

 $ sudo pip3 install obot --upgrade --force-reinstall

you can also run directly from the tarball, see https://pypi.org/project/obot/#files

OBJECT PROGRAMMING
==================

OBOT provides a "move all methods to functions" like this:

::

 obj.method(*args) -> method(obj, *args) 

 e.g.

 not:

 >>> from ob.obj import Object
 >>> o = Object()
 >>> o.set("key", "value")
 >>> o.key
 'value'

 but:

 >>> from ob.obj import Object, set
 >>> o = Object()
 >>> set(o, "key", "value")
 >>> o.key
 'value'

it's a way of programming with objects, replacing OOP. Not object-oriented programming, but object programming. If you are used to functional programming you'll like it (or not) ;]

USAGE
=====

OBOT has it's own CLI, you can run it by giving the obot command on the
prompt, it will return with no response:

:: 

 $ obot
 $ 

you can use obot <cmd> to run a command directly:

::

 $ obot cmd
 cfg,cmd,dne,dpl,edt,fnd,ftc,icfg,log,rem,rss,tdo,tsk,udp,ver

configuration is done with the icfg command:

::

 $ obot icfg
 channel=#obot nick=obot port=6667 server=localhost

you can use setters to edit fields in a configuration:

::

 $ obot icfg server=irc.freenode.net channel=\#dunkbots nick=obot
 channel=#dunkbots nick=botje port=6667 server=irc.freenode.net

start the irc bot with:

::

 $ obot mods=irc

RSS
===

OBOT provides with the use of feedparser the possibility to server rss
feeds in your channel. 

to add an url use the rss command with an url:

::

 $ obot rss https://github.com/bthate/obot/commits/master.atom
 ok 1

run the rss command to see what urls are registered:

::

 $ obot fnd rss
 0 https://github.com/bthate/obot/commits/master.atom

the ftc command can be used to poll the added feeds:

::

 $ obot ftc
 fetched 0

adding rss to mods= will load the rss modules and start it's poller.

::

 $ obot mods=rss


UDP
===

OBOT also has the possibility to serve as a UDP to IRC relay where you
can send UDP packages to the bot and have txt displayed on the channel.

use the obot program to send text via the bot to the channel on the irc server:

::

 $ tail -f /var/log/syslog | obot udp

to send the tail output to the IRC channel

you can use python3 code to send a UDP packet to obot, it's unencrypted
txt send to the bot and display on the joined channels.

to send a udp packet to okbot in python3:

::

 import socket

 def toudp(host=localhost, port=5500, txt=""):
     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     sock.sendto(bytes(txt.strip(), "utf-8"), host, port)

MODULES
=======

OBOT has the following modules:

::

    ob                  - object library
    ob.all              - all modules
    ob.bus              - announce
    ob.cfg              - config
    ob.csl              - console
    ob.dbs              - databases
    ob.dft              - default
    ob.evt              - event
    ob.hdl              - handler
    ob.int              - introspection
    ob.krn              - kernel
    ob.ldr              - loader
    ob.obj              - objects
    ob.prs              - parser
    ob.tms              - times
    ob.trm              - terminal
    ob.tsk              - tasks
    ob.utl              - utilities

OBOT had the following modules:

::

    obot.irc		- internet relay chat
    obot.rss		- rss fetcher
    obot.udp		- udp to irc relay

OMOD has the following modules available:

::

   omod.cmd	- command
   omod.edt	- edit
   omod.ent	- enter log and todo items
   omod.fnd	- find typed objects


SERVICE
=======

if you want to run the bot 24/7 you can install OBOT as a service for
the systemd daemon. You can do this by copying the following into
the /etc/systemd/system/obotd.service file:

::


 [Unit]
 Description=24/7 channel daemon
 After=network-online.target
 Wants=network-online.target

 [Service]
 User=obotd
 Group=obotd
 ExecStart=/usr/local/bin/obotd

 [Install]
 WantedBy=multi-user.target

create a homedir for obotd:

::

 $ mkdir /var/lib/obotd
 $ mkdir /var/lib/obotd/omod

add the obotd user to the system (as root):

::

 $ groupadd obotd
 $ chown -R obotd:obotd /var/lib/obotd
 $ useradd obotd -g obotd -d /home/obot

configure obot to connect to irc:

::

 $ obotd icfg server=irc.freenode.net channel=#obot nick=obot

copy modules over to obot's work directory:

::

 $ cp -Ra mymod/*.py /var/lib/obotd/omod

make sure permissions are set properly:

::

 $ chown -R obotd:obotd /var/lib/obotd
 $ chown -R obotd:obotd /var/lib/obotd
 $ chmod -R 700 /var/lib/obotd/
 $ chmod -R 400 /var/lib/obotd/omod/*.py

add the obotd service with:

::

 $ systemctl enable obotd
 $ systemctl daemon-reload

then restart the obotd service.

::

 $ service obotd stop
 $ service obotd start

if you don't want obotd to startup at boot, remove the service file:

::

 $ rm /etc/systemd/system/obotd.service

CONTACT
=======

contact me on IRC/freenode/#dunkbots or email me at bthate@dds.nl

| Bart Thate (bthate@dds.nl, thatebart@gmail.com)
| botfather on #dunkbots irc.freenode.net

.. toctree::
    :hidden:

    source

