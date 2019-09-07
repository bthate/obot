""" IRC bot for OBOT. """

__version__ = 1

import ob
import logging
import os
import socket
import ssl
import sys
import textwrap
import time
import threading

from ob import Object, launch, last 
from ob.dispatch import dispatch
from ob.errors import EINIT
from ob.handler import Event
from ob.kernel import k
from ob.trace import get_exception
from ob.utils import locked

from obot import Bot

def __dir__():
    return ('Bot', 'Cfg', 'DCC', 'DEvent', 'IEvent', 'IRC', 'init', "cb_log", "errored", "noticed", "privmsged")

def init():
    """ initialise irc bot. """
    bot = IRC()
    last(bot.cfg)
    if k.cfg.prompting or not bot.cfg.server:
        try:
            server, channel, nick = k.cfg.args
            bot.cfg.server = server
            bot.cfg.channel = channel
            bot.cfg.nick = nick
            bot.cfg.save()
        except ValueError:
            sys.stdout.write("%s -m irc <server> <channel> <nick>" % k.cfg.name)
            sys.stdout.flush()
            raise EINIT
    bot.start()
    return bot

class Cfg(ob.Cfg):

    """ IRC configuration file. """

    def __init__(self):
        super().__init__()
        self.blocking = True
        self.channel = ""
        self.nick = ""
        self.port = 6667
        self.prompt = True
        self.realname = "ob"
        self.server = ""
        self.sleep = 5
        self.verbose = True
        self.username = "ob"

class Event(Event):

    """ IRC event. """

    def __init__(self):
        super().__init__()
        self.arguments = []
        self.cc = ""
        self.channel = ""
        self.command = ""
        self.nick = ""
        self.target = ""

class DEvent(Event):

    """ DCC event. """

    def __init__(self):
        super().__init__()
        self._sock = None
        self._fsock = None
        self.channel = ""

    def raw(self, txt):
        self._fsock.write(txt.rstrip() + "\n") 
        self._fsock.flush()

    def reply(self, txt):
        self.raw(txt)

class TextWrap(textwrap.TextWrapper):

    """ textwrapper (default 500 chars). """

    def __init__(self):
        super().__init__()
        self.drop_whitespace = False
        self.fix_sentence_endings = True
        self.replace_whitespace = True
        self.tabsize = 4
        self.width = 500

class IRC(Bot):

    """ IRC bot. """

    def __init__(self):
        super().__init__()
        self._buffer = []
        self._connected = threading.Event()
        self._sock = None
        self._fsock = None
        self._threaded = False
        self.cc = "!"
        self.cfg = Cfg()
        self.channels = []
        self.state = Object()
        self.state.error = ""
        self.state.last = 0
        self.state.lastline = ""
        self.state.nrconnect = 0
        self.state.nrsend = 0
        self.state.pongcheck = False
        self.state.resume = None
        self.register(errored)
        self.register(noticed)
        self.register(privmsged)
        if self.cfg.channel and self.cfg.channel not in self.channels:
            self.channels.append(self.cfg.channel)

    def _connect(self):
        """ raw connect code. """
        oldsock = None
        if k.cfg.resume:
            fd = None
            s = {"server": server}
            b = k.db.last("obot.irc.IRC", s)
            if b:
                try:
                    fd = int(b.state["resume"])
                except TypeError:
                    pass
            if fd:
                logging.warning("resume %s" % fd)
                if self.cfg.ipv6:
                    oldsock = socket.fromfd(fd , socket.AF_INET6, socket.SOCK_STREAM)
                else:
                    oldsock = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
        if not oldsock:
            if self.cfg.ipv6:
                oldsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            else:
                oldsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        oldsock.setblocking(int(self.cfg.blocking or 1))
        oldsock.settimeout(60.0)
        if not k.cfg.resume:
            oldsock.connect((self.cfg.server, int(self.cfg.port or 6667)))
        oldsock.setblocking(int(self.cfg.blocking or 1))
        oldsock.settimeout(700.0)
        if self.cfg.ssl:
            self._sock = ssl.wrap_socket(oldsock)
        else:
            self._sock = oldsock
        self._fsock = self._sock.makefile("r")
        self.state.resume = self._sock.fileno()
        os.set_inheritable(self.state.resume, os.O_RDWR)
        self._connected.set()
        return True

    def _parsing(self, txt):
        """ parse incoming text into an event. """
        rawstr = str(txt)
        rawstr = rawstr.replace("\u0001", "")
        rawstr = rawstr.replace("\001", "")
        o = Event()
        o.orig = repr(self)
        o.txt = rawstr
        o.cc = self.cc
        o.command = ""
        o.arguments = []
        arguments = rawstr.split()
        if arguments:
            o.origin = arguments[0]
        else:
            o.origin = self.cfg.server
        if o.origin.startswith(":"):
            o.origin = o.origin[1:]
            if len(arguments) > 1:
                o.command = arguments[1]
            if len(arguments) > 2:
                txtlist = []
                adding = False
                for arg in arguments[2:]:
                    if arg.startswith(":"):
                        adding = True
                        txtlist.append(arg[1:])
                        continue
                    if adding:
                        txtlist.append(arg)
                    else:
                        o.arguments.append(arg)
                    o.txt = " ".join(txtlist)
        else:
            o.chk = o.command = o.origin
            o.origin = self.cfg.server
        try:
            o.nick, o.origin = o.origin.split("!")
        except ValueError:
            o.nick = ""
        if o.arguments:
            o.target = o.arguments[-1]
        else:
            o.target = ""
        if o.target.startswith("#"):
            o.channel = o.target
        else:
            o.channel = o.nick
        if not o.txt:
            if rawstr[0] == ":":
                rawstr = rawstr[1:]
            o.txt = rawstr.split(":", 1)[-1]
        if not o.txt and len(arguments) == 1:
            o.txt = arguments[1]
        o.args = o.txt.split()
        o.rest = " ".join(o.args)
        o.chk = o.command
        return o

    def _some(self, use_ssl=False, encoding="utf-8"):
        """ poll (blocking) for some input on socket. """
        if use_ssl:
            inbytes = self._sock.read()
        else:
            inbytes = self._sock.recv(512)
        txt = str(inbytes, encoding)
        if txt == "":
            raise ConnectionResetError
        logging.debug(txt.rstrip())
        self.state.lastline += txt
        splitted = self.state.lastline.split("\r\n")
        for s in splitted[:-1]:
            self._buffer.append(s)
        self.state.lastline = splitted[-1]

    def announce(self, txt):
        """ announce txt on all joined channels. """
        for channel in self.channels:
            self.say(channel, txt)

    def command(self, cmd, *args):
        """ send command to server. """
        if not args:
            self.raw(cmd)
            return
        if len(args) == 1:
            self.raw("%s %s" % (cmd.upper(), args[0]))
            return
        if len(args) == 2:
            self.raw("%s %s :%s" % (cmd.upper(), args[0], " ".join(args[1:])))
            return
        if len(args) >= 3:
            self.raw("%s %s %s :%s" % (cmd.upper(), args[0], args[1], " ".join(args[2:])))
            return

    def connect(self):
        """ connect till connected. """
        nr = 0
        while 1:
            self.state.nrconnect += 1
            if self._connect():
                break
            time.sleep(nr * 3.0)
            nr += 1
        if not k.cfg.resume:
            self.logon(self.cfg.server, self.cfg.nick)

    def poll(self):
        """ return (blocking) event from irc server. """
        self._connected.wait()
        if not self._buffer:
            try:
                self._some()
            except (ConnectionResetError, socket.timeout):
                e = Event()
                e._error = get_exception()
                e.chk = "ERROR"
                return e
        e = self._parsing(self._buffer.pop(0))
        cmd = e.command
        if cmd == "001":
            if "servermodes" in dir(self.cfg):
                self.raw("MODE %s %s" % (self.cfg.nick, self.cfg.servermodes))
            self.joinall()
        elif cmd == "PING":
            self.state.pongcheck = True
            self.command("PONG", e.txt)
        elif cmd == "PONG":
            self.state.pongcheck = False
        elif cmd == "433":
            nick = e.target + "_"
            self.cfg.nick = nick
            self.raw("NICK %s" % self.cfg.nick or "ob", True)
        elif cmd == "ERROR":
            self.state.error = e
        return e

    def joinall(self):
        """ join all channels. """
        for channel in self.channels:
            self.command("JOIN", channel)

    def logon(self, server, nick):
        """ perform logon on the irc server. """
        if k.cfg.resume:
            return
        self._connected.wait()
        self.raw("NICK %s" % nick, True)
        self.raw("USER %s %s %s :%s" % (self.cfg.username or "ob", server, server, self.cfg.realname or "ob"), True)

    @locked
    def raw(self, txt, direct=False):
        """ send txt on the socket. """
        txt = txt.rstrip()
        logging.debug(txt)
        if self._stopped:
            return
        if not txt.endswith("\r\n"):
            txt += "\r\n"
        txt = txt[:512]
        txt = bytes(txt, "utf-8")
        if not direct:
            if (time.time() - self.state.last) < 3.0:
                time.sleep(1.0 * (self.state.nrsend % 10))
        self.state.last = time.time()
        self.state.nrsend += 1
        self._sock.send(txt)

    def say(self, channel, txt, mtype="chat"):
        """ wrap text before output to server. """
        wrapper = TextWrap()
        for line in txt.split("\n"):
            for t in wrapper.wrap(line):
                self.command("PRIVMSG", channel, t)

    def start(self):
        """ start irc bot. """
        if self.cfg.channel:
            self.channels.append(self.cfg.channel)
        self.connect()
        super().start()
        
class DCC(Bot):

    """ DCC bot. """

    def __init__(self):
        super().__init__()
        self._connected = threading.Event()
        self._sock = None
        self._fsock = None
        self.encoding = "utf-8"
        self.origin = ""
        self.register(dispatch)

    def raw(self, txt):
        """ raw socket output. """
        self._fsock.write(txt.rstrip())
        self._fsock.write("\n")
        self._fsock.flush()

    def announce(self, txt):
        """ announce to client. """
        self.raw(txt)

    def connect(self, event):
        """ connect to dcc client. """
        arguments = event.txt.split()
        addr = arguments[3]
        port = arguments[4]
        port = int(port)
        if ':' in addr:
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((addr, port))
        s.send(bytes('Welcome to %s %s !!\n' % (k.cfg.name.upper(), event.nick), "utf-8"))
        s.setblocking(True)
        os.set_inheritable(s.fileno(), os.O_RDWR)
        self._sock = s
        self._fsock = self._sock.makefile("rw")
        self.origin = event.origin
        self._connected.set()
        super().start()

    def poll(self):
        """ return event from dcc socket. """
        self._connected.wait()
        e = DEvent()
        e.txt = self._fsock.readline()
        e._sock = self._sock
        e._fsock = self._fsock
        e.channel = self.origin
        e.orig = repr(self)
        e.origin = self.origin or "root@dcc"
        return e

    def say(self, channel, txt, type="chat"):
        """ echo to DCC client. """
        self.raw(txt)

def errored(handler, event):
    """ error handler. """
    if event.chk != "ERROR":
        return
    handler.state.error = event
    handler._connected.clear()
    time.sleep(handler.state.nrconnect * handler.cfg.sleep)
    handler.connect()

def noticed(handler, event):
    """ notice handler. """
    if event.chk != "NOTICE":
        return
    if event.txt.startswith("VERSION"):
        txt = "\001VERSION %s %s - %s\001" % (k.cfg.name, __version__, k.cfg.description)
        handler.command("NOTICE", event.channel, txt)

def privmsged(handler, event):
    """ privmsg handler. """
    if event.chk != "PRIVMSG":
        return
    if event.origin != k.cfg.owner:
        k.users.userhosts.set(event.nick, event.origin)
    if event.txt.startswith("DCC CHAT"):
        try:
            dcc = DCC()
            dcc.walk("ob")
            dcc.encoding = "utf-8"
            launch(dcc.connect, event)
            return
        except ConnectionRefusedError:
            return
    if event.txt and event.txt[0] == handler.cc:
        if not k.users.allowed(event.origin, "USER"):
            return
        event.parse(event.txt[1:])
        k.put(event)
