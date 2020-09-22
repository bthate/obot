# OLIB - object library
#
#

import datetime
import ol
import os
import threading
import time

class Timer(ol.Object):

    def __init__(self, sleep, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.sleep = sleep
        self.args = args
        self.name = kwargs.get("name", "")
        self.kwargs = kwargs
        self.state = ol.Object()
        self.timer = None

    def run(self, *args, **kwargs):
        self.state.latest = time.time()
        ol.tsk.launch(self.func, *self.args, **self.kwargs)

    def start(self):
        if not self.name:
            self.name = ol.get_name(self.func)
        timer = threading.Timer(self.sleep, self.run, self.args, self.kwargs)
        timer.setName(self.name)
        timer.setDaemon(True)
        timer.sleep = self.sleep
        timer.state = self.state
        timer.state.starttime = time.time()
        timer.state.latest = time.time()
        timer.func = self.func
        timer.start()
        self.timer = timer
        return timer

    def stop(self):
        if self.timer:
            self.timer.cancel()

class Repeater(Timer):

    def run(self, *args, **kwargs):
        thr = ol.tsk.launch(self.start, **kwargs)
        super().run(*args, **kwargs)
        return thr


year_formats = [
    "%b %H:%M",
    "%b %H:%M:%S",
    "%a %H:%M %Y",
    "%a %H:%M",
    "%a %H:%M:%S",
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d-%m",
    "%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    "%d-%m %H:%M:%S",
    "%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%d-%m-%Y %H:%M",
    "%d-%m %H:%M",
    "%m-%d %H:%M",
    "%H:%M:%S",
    "%H:%M"
]

def day():
    return str(datetime.datetime.today()).split()[0]

def days(path):
    return elapsed(time.time() - fntime(path))

def elapsed(seconds, short=True):
    txt = ""
    nsec = float(seconds)
    year = 365*24*60*60
    week = 7*24*60*60
    nday = 24*60*60
    hour = 60*60
    minute = 60
    years = int(nsec/year)
    nsec -= years*year
    weeks = int(nsec/week)
    nsec -= weeks*week
    nrdays = int(nsec/nday)
    nsec -= nrdays*nday
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    sec = nsec - minutes*minute
    if years:
        txt += "%sy" % years
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += "%sd" % nrdays
    if years and short and txt:
        return txt
    if hours:
        txt += "%sh" % hours
    if nrdays and short and txt:
        return txt
    if minutes:
        txt += "%sm" % minutes
    if hours and short and txt:
        return txt
    if sec == 0:
        txt += "0s"
    #elif sec < 1 or not short:
    #    txt += "%.3fs" % sec
    else:
        txt += "%ss" % int(sec)
    txt = txt.strip()
    return txt

def fntime(daystr):
    daystr = daystr.replace("_", ":")
    datestr = " ".join(daystr.split(os.sep)[-2:])
    try:
        datestr, rest = datestr.rsplit(".", 1)
    except ValueError:
        rest = ""
    try:
        t = time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))
        if rest:
            t += float("." + rest)
    except ValueError:
        t = 0
    return t

def get_time(daystr):
    for f in year_formats:
        try:
            t = time.mktime(time.strptime(daystr, f))
            return t
        except ValueError:
            pass

def parse_time(daystr):
    if not any([c.isdigit() for c in daystr]):
        return 0
    valstr = ""
    val = 0
    total = 0
    for c in daystr:
        try:
            vv = int(valstr)
        except ValueError:
            vv = 0
        if c == "y":
            val = vv * 3600*24*365
        if c == "w":
            val = vv * 3600*24*7
        elif c == "d":
            val = vv * 3600*24
        elif c == "h":
            val = vv * 3600
        elif c == "m":
            val = vv * 60
        else:
            valstr += c
        total += val
    return total

def today():
    return datetime.datetime.today().timestamp()

def to_day(daystring):
    line = ""
    daystr = str(daystring)
    for word in daystr.split():
        if "-" in word:
            line += word + " "
        elif ":" in word:
            line += word
    if "-" not in line:
        line = day() + " " + line
    try:
        return get_time(line.strip())
    except ValueError:
        pass
