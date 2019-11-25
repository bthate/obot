__version__ = 1

import ob
import socket
import time

from ob import Object, k
from ob.cls import Cfg
from ob.pst import Persist
from ob.utl import get_name

def __dir__():
    return ("UDP", "Cfg", "init") 

def init():
    server = UDP()
    server.start()
    return server

class Cfg(Cfg):

    def __init__(self):
        super().__init__()
        self.host = "localhost"
        self.port = 5500
        self.password = "boh"
        self.seed = "blablablablablaz" # needs to be 16 chars wide
        self.server = self.host
        self.owner = ""

class UDP(Persist):

    def __init__(self):
        super().__init__()
        self._stopped = False
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._sock.setblocking(1)
        self._starttime = time.time()
        self.cfg = Cfg()

    def output(self, txt, addr=None):
        try:
            (passwd, text) = txt.split(" ", 1)
        except ValueError:
            return
        text = text.replace("\00", "")
        if passwd == self.cfg.password:
            for b in k.fleet.bots:
                if "DCC" in get_name(b):
                    b.announce(text)

    def server(self, host="", port=""):
        if k.cfg.debug:
            return
        c = self.cfg
        try:
            self._sock.bind((host or c.host, port or c.port))
        except socket.gaierror as ex:
            logging.error("EBIND %s" % ex)
            return
        while not self._stopped:
            (txt, addr) = self._sock.recvfrom(64000)
            if self._stopped:
                break
            data = str(txt.rstrip(), "utf-8")
            if not data:
                break
            self.output(data, addr)

    def exit(self):
        self._stopped = True
        self._sock.settimeout(0.01)
        self._sock.sendto(bytes("bla", "utf-8"), (self.cfg.host, self.cfg.port))

    def start(self):
        self.cfg = k.db.last("obot.udp.Cfg") or Cfg()
        k.launch(self.server)
