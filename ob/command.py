""" parse string into command. """

import logging
import ob

def __dir__():
    return ("Command", "Token", "aliases")

aliases = {
           "c": "cmds",
           "f": "find",
           "l": "log",
           "ps": "show tasks",
           "t": "todo",
           "u": "show uptime",
           "v": "show version"
           }

from ob.errors import ENOTXT
from ob.times import to_day

class Token(ob.Default):

    """ represent a single word in a sentence. """

    def __init__(self):
        super().__init__()
        self.down = None
        self.index = None
        self.option = ""
        self.up = None

    def parse(self, nr, word):
        """ parse the n'th word. """
        if nr == 0:
            if word.startswith("!"):
                word = word[1:]
            if word:
                self.chk = word
            return
        if word.startswith("-"):
            try:
                self.down = int(word[1:])
            except ValueError:
                pass
            self.option += word[1:]
            return
        try:
            self.index = int(word)
            self.arg = word
            return
        except ValueError:
            pass
        if nr == 1:
            self.match = ob.handler.names.get(word, word)
            logging.warn("match %s" % self.match)
            self.arg = word
            return
        if "http" in word:
            self.value = word
            self.arg = word
            return
        if word.startswith("+"):
            try:
                self.up = int(word[1:])
                return
            except ValueError:
                pass
        if "==" in word:
            if word.endswith("-"):
                self.ignore = word[:-1]
                word = self.ignore
            self.selector, self.value = word.split("==")
            self.dkey = self.selector
        elif "=" in word:
            self.setter, self.value = word.split("=")
            self.dkey = self.setter
        else:
            self.arg = word
            self.dkey = word
            self.value = word
        if nr == 2 and not self.selector and not self.setter:
            self.selector = word
            self.value = None

class Command(ob.Default):

    """ A line of txt parsed into a command. """

    def __init__(self):
        super().__init__()
        self._error = None
        self._func = None
        self._thrs = []
        self.args = []
        self.batch = False
        self.delta = 0
        self.dkeys = []
        self.index = None
        self.match = None
        self.orig = None
        self.result = []
        self.selector = {}
        self.setter = {}
        self.time = 0

    def _aliased(self, txt):
        """ return aliased version of txt. """
        spl = txt.split()
        if spl and spl[0] in aliases:
            cmd = spl[0]
            v = aliases.get(cmd, None)
            if v:
                spl[0] = cmd.replace(cmd, v)
        txt2 = " ".join(spl)
        return txt2 or txt

    def _tokens(self):
        """ return a list of tokens. """
        words = self.txt.split()
        tokens = []
        nr = -1
        for word in words:
            nr += 1
            token = Token()
            token.parse(nr, word)
            tokens.append(token)
        return tokens

    def parse(self, txt, options=""):
        """ parse txt into a command. """
        if not txt:
            txt = self.txt 
        if not txt:
            raise ENOTXT
        txt = txt.replace("\u0001", "")
        txt = txt.replace("\001", "")
        if txt and self.cc == txt[0]:
            txt = txt[1:]
        self.txt = self._aliased(txt)
        if not self.txt:
            self.txt = txt
        nr = -1
        self.cfrom = ob.trace.get_from()
        self.args = []
        self.dkeys = []
        self.options = options or self.options or ""
        prev = ""
        for token in self._tokens():
            nr += 1
            if token.chk:
                self.chk = token.chk
            if token.match:
                self.match = token.match
            if token.index:
                self.index = token.index
                self.args.append(token.arg)
            if token.option:
                self.options += "," + token.option
            if prev == "-o":
                prev = ""
                self.options += "," + token.value
            if token.down:
                prev = token.down
            if token.ignore:
                self.ignore = token.ignore
                continue
            elif token.dkey:
                self.dkeys.append(token.dkey)
            if token.selector:
                self.selector[token.selector] = token.value
            if token.setter:
                self.setter[token.setter] = token.value
            if token.up:
                self.delta = parse_date(token.up)
            elif token.down:
                self.delta = parse_date(token.down)
            if token.arg:
                self.args.append(token.arg)
        for opt in self.options.split(","):
            try:
                self.index = int(opt)
                break
            except ValueError:
                pass
            continue
        self.rest = " ".join(self.args)
        self.time = to_day(self.rest)
