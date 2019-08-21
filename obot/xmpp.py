""" XMPP bot for OBOT. """

__version__ = 1

import _thread
import getpass
import logging
import ob
import ssl
import sys
import threading

from ob import Cfg, Object
from ob.bot import Bot
from ob.errors import EINIT
from ob.handler import Event
from ob.kernel import k

def __dir__():
    return ("XMPP", "XEvent", "Cfg", "stripped")

def init():
    xmpp = XMPP()
    ob.last(xmpp.cfg)
    if xmpp.cfg.user:
        logging.warning("using %s" % xmpp.cfg.user)
    dosave = False
    if k.cfg.prompting or not xmpp.cfg.user:
        xmpp.cfg.user = input("user: ")
        dosave = True
    elif k.cfg.argparse or k.cfg.args:
        if k.cfg.args:
            xmpp.cfg.user = k.cfg.args[0]
            dosave = True
        else:
            raise EINIT
    if not xmpp.cfg.user:
        raise EINIT
    if not xmpp.cfg.password:
        xmpp.cfg.password = getpass.getpass()
    if not xmpp.cfg.password:
        raise EINIT
    if dosave:
        xmpp.cfg.save()
    if not xmpp.cfg.user:
        sys.stdout.write("%s <jid>" % k.cfg.name)
        sys.stdout.flush()
        raise EINIT
    xmpp.start()
    return xmpp

try:
    import sleekxmpp
except ImportError:
    pass

class Cfg(Cfg):

    def __init__(self):
        super().__init__()
        self.channel = ""
        self.ipv6 = False
        self.nick = ""
        self.noresolver = True
        self.password = ""
        self.server = ""
        self.user = ""

class XEvent(Event):

    def __init__(self):
        super().__init__()
        self.cc = ""
        self.channel = ""
        self.element = ""
        self.jid = ""
        self.nick = ""
        self.server = ""
        self.mtype = ""
        self.txt = ""

class XMPP(Bot):

    def __init__(self):
        super().__init__()
        self._connected = threading.Event()
        self._threaded = True
        self.cc = ""
        self.cfg = Cfg()
        self.channels = []
        self.client = None
        self.jid = None
        self.rooms = []
        self.state = Object()

    def _connect(self, user, pw):
        self._makeclient(user, pw)
        if self.cfg.noresolver:
            self.client.configure_dns(None)
        self.client.connect(use_tls=True)
        self._connected.set()
        
    def _makeclient(self, jid, password):
        self.client = sleekxmpp.clientxmpp.ClientXMPP(jid,
                                                      password,
                                                      plugin_config={},
                                                      plugin_whitelist=[],
                                                      escape_quotes=False,
                                                      sasl_mech=None)
        self.client._error = Object()
        self.client.register_plugin(u'xep_0045')
        self.client.add_event_handler('errored', self.handling)
        self.client.add_event_handler('failed_auth', self.handling)
        self.client.add_event_handler("message", self.messaged)
        self.client.add_event_handler("iq", self.handling)
        self.client.add_event_handler('presence', self.presenced)
        self.client.add_event_handler('presence_dnd', self.presenced)
        self.client.add_event_handler('presence_xa', self.presenced)
        self.client.add_event_handler('presence_available', self.presenced)
        self.client.add_event_handler('presence_chat', self.presenced)
        self.client.add_event_handler('presence_away', self.presenced)
        self.client.add_event_handler('presence_unavailable', self.presenced)
        self.client.add_event_handler('presence_subscribe', self.presenced)
        self.client.add_event_handler('presence_subscribed', self.presenced)
        self.client.add_event_handler('presence_unsubscribe', self.presenced)
        self.client.add_event_handler('presence_unsubscribed', self.presenced)
        self.client.add_event_handler("session_bind", self.session_bind)
        self.client.add_event_handler("session_start", self.session_start)
        self.client.add_event_handler("ssl_invalid_cert", self.handling)
        #self.client.add_event_handler("ssl_cert", self.handler)
        self.client.exception = self.handling
        self.client.reconnect_max_attempts = 3
        self.client.ssl_version = ssl.PROTOCOL_SSLv23
        self.client.use_ipv6 = self.cfg.ipv6

    def _say(self, channel, txt, mtype="chat"):
        try:
            sleekxmpp.jid.JID(channel)
        except sleekxmpp.jid.InvalidJID:
            return
        if self.cfg.user in channel:
            return
        if channel in self.rooms:
            mtype = "groupchat"
        if mtype == "groupchat":
            channel = stripped(channel)
        self.client.send_message(channel, str(txt), mtype)

    def sleek(self):
        self.client.process(block=True)

    def announce(self, txt):
        for channel in self.channels:
            self.say(channel, txt, "chat")
        for room in self.rooms:
            self.say(channel, txt, "groupchat")

    def connect(self, user="", password=""):
        self._connect(user, password)
        return True

    def handling(self, data):
        print(data)

    def do_join(self):
        c = self.cfg
        if c.room not in self.rooms:
            self.rooms.append(c.room)
        self._connected.wait()
        self.client.plugin['xep_0045'].joinMUC(c.room,
                                               c.nick,
                                               wait=True)

    def fileno(self):
        return self.client.filesocket.fileno()

    def messaged(self, data):
        if '<delay xmlns="urn:xmpp:delay"' in str(data):
            return
        origin = str(data["from"])
        if data["type"] == "groupchat":
            if not k.users.allowed(origin, "USER"):
                return
        txt = data["body"]
        m = XEvent()
        m.parse(txt)
        m.txt = txt
        m.jid = origin
        m.orig = repr(self)
        m.origin = origin
        m.mtype = data["type"]
        if m.mtype == "error":
            loggin.error("error %s" % m.error)
            return
        m.nick = m.origin.split("/")[-1]
        m.user = m.jid = stripped(m.origin)
        m.channel = stripped(m.origin)
        if self.cfg.user == m.user:
            return
        if m.origin not in self.channels:
            self.channels.append(m.origin)
        k.put(m)

    def pinged(self, event):
        print(event)

    def presenced(self, data):
        o = XEvent()
        o.mtype = data["type"]
        o.orig = repr(self)
        o.cc = ""
        o.origin = str(data["from"])
        o.jid = o.origin
        o.nick = o.origin.split("/")[-1]
        o.server = self.cfg.server
        o.room = stripped(o.origin)
        if "txt" not in o:
            o.txt = ""
        o.element = "presence"
        if self.cfg.user in o.origin:
            return
        if o.mtype == 'subscribe':
            pres = XEvent({'to': o.origin, 'type': 'subscribed'})
            self.client.send_presence(pres)
            pres = XEvent({'to': o.origin, 'type': 'subscribe'})
            self.client.send_presence(pres)
            self.channels.append(o.origin)
        elif o.mtype == "unsubscribe":
            if o.origin in self.channels:
                self.channels.remove(o.origin)
            return
        elif o.mtype == "available":
            if o.origin not in self.channels:
                self.channels.append(o.origin)
        elif o.mtype == "unavailable":
            if o.origin in self.channels:
                self.channels.remove(o.origin)

    def say(self, channel, txt, mtype=None):
        self._say(channel, txt, mtype)

    def session_bind(self, data):
        self.jid = str(data)

    def session_start(self, data):
        try:
            self.client.send_presence()
            self.client.get_roster()
        except sleekxmpp.exceptions.IqTimeout:
            self.reconnect()

    def stop(self):
        if "client" in self and self.client:
            self.client.disconnect()
        super().stop()

    def start(self):
        super().start()
        ok = self.connect(self.cfg.user, self.cfg.password)
        if ok:
            if self.cfg.channel:
                self.join()
        ob.launch(self.output)
        ob.launch(self.sleek)
        return self

def stripped(jid):
    try:
        return str(jid).split("/")[0]
    except (IndexError, ValueError):
        return str(jid)
