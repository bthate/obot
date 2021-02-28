OBOT
####

Welcome to OBOT, write your own commands ! see https://pypi.org/project/obot/

OBOT is a pure python3 IRC chat bot that can run as a background daemon
for 24/7 a day presence in a IRC channel. You can use it to display RSS feeds,
have it act as a UDP to IRC gateway, program your own commands for it, log 
objects on disk and search them.

OBOT is placed in the Public Domain, no COPYRIGHT, no LICENSE.

INSTALL
=======

installation is through pypi:

::

 $ sudo pip3 install obot

USAGE
=====

OBOT has it's own CLI, you can run it by giving the obot command on the
prompt, by default it will return with no response:

:: 

 $ obot
 $ 

you can use obot <cmd> to run a command directly:

::

 $ obot cmd
 cfg,cmd

basic bot configuration is done with the cfg command:

::

 $ obot cfg
 wd=/home/bart/.obot version=36

irc configuration is done with the icfg command:

::

 $ obot icfg server=irc.freenode.net channel=\#dunkbots nick=obot
 ok

for starting a command shell use the -c option:

::

 $ obot -c
 > 

start the irc bot with:

::

 $ obot -c mods=irc 
 > 

RSS
===

OBOT provides with the use of feedparser the possibility to server rss
feeds in your channel. OBOT doesn't depend on other packages so you need
to install feedparser first:

::

 $ sudo apt install python3-feedparser

to add an url use the rss command with an url:

::

 $ obot rss https://github.com/bthate/obot/commits/master.atom
 ok

run the fnd command to see what urls are registered:

::

 $ obot fnd rss
 0 https://github.com/bthate/obot/commits/master.atom

the ftc command can be used to poll the added feeds:

::

 $ obot ftc
 fetched 20

adding rss to mods= will load the rss module and start it's poller.

::

 $ obot -c mods=irc,rss
 >

UDP
===

OBOT also has the possibility to serve as a UDP to IRC relay where you
can send UDP packages to the bot and have txt displayed on the channel.
To enable this start obot with the udp module loaded:

::

 $ obot -c mods=irc,udp

use the obudp program to send text via the bot to the channel on the irc server:

::

 $ tail -f /var/log/syslog | obudp

to send the tail output to the IRC channel.

you can use python3 code to send a UDP packet to OBOT, it's unencrypted
txt send to the bot and display on the joined channels.

::

 import socket

 def toudp(host=localhost, port=5500, txt=""):
     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     sock.sendto(bytes(txt.strip(), "utf-8"), host, port)

SERVICE
=======

if you want to run the bot 24/7 you can install OBOT as a service for
the systemd daemon. You can do this by copying the following into
the /etc/systemd/system/obot.service file:

::

 [Unit]
 Description=OBOT - 24/7 channel daemon
 After=multi-user.target

 [Service]
 StandardOutput=journal+console
 StandardError=journal+console
 SyslogIdentifier=obot
 DynamicUser=True
 StateDirectory=obot
 CacheDirectory=obot
 ExecStart=/usr/local/bin/obotd
 CapabilityBoundingSet=CAP_NET_RAW

 [Install]
 WantedBy=multi-user.target

enable the obot service with:

::

 $ sudo systemctl enable obot
 $ sudo systemctl daemon-reload

then start the obot service.

::

 $ sudo systemctl start obot

if you don't want OB to startup at boot, remove the service file:

::

 $ sudo rm /etc/systemd/system/obot.service

CONTACT
=======

"hf"

contact me on IRC/freenode/#dunkbots or email me at bthate@dds.nl

| Bart Thate (bthate@dds.nl, thatebart@gmail.com)
| botfather on #dunkbots irc.freenode.net
