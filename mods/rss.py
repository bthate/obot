"""
     rss feed fetcher.

     to fetch all feeds from the commandline use:

         ./bin/ob -m rss fetch

"""

__version__ = 1

import datetime
import io
import logging
import ob
import obot
import os
import random
import re
import time
import urllib

try:
    import feedparser
except ModuleNotFoundError:
    feedparser = None
    
from ob import Object, k, last
from ob.clk import Repeater
from ob.cls import Cfg
from ob.cls import Default
from ob.pst import Persist
from ob.tms import day, to_time
from ob.utl import get_url, strip_html, unescape

def __dir__():
    return ("Cfg", "Feed", "Fetcher", "Rss", "Seen", "delete" ,"display", "feed", "fetch", "init", "rss")

def init():
    fetcher.start()
    return fetcher

class Cfg(Cfg):

    def __init__(self):
        super().__init__()
        self.display_list = ["title", "link"]
        self.dosave = True

class Feed(Default):

    pass

class Rss(Persist):

    def __init__(self):
        super().__init__()
        self.rss = ""

class Seen(Persist):

    def __init__(self):
        super().__init__()
        self.urls = []

class Fetcher(Persist):

    def __init__(self):
        super().__init__()
        self.cfg = Cfg()
        self.seen = Seen()
        self._thrs = []

    def display(self, o):
        result = ""
        try:
            dl = o.display_list
        except AttributeError:
            pass
        if not dl:
            dl = self.cfg.display_list
        for key in dl:
            data = ob.get(o, key, None)
            if data:
                data = data.replace("\n", " ")
                data = strip_html(data.rstrip())
                data = unescape(data)
                result += data.rstrip()
                result += " - "
        return result[:-2].rstrip()

    def fetch(self, obj):
        counter = 0
        objs = []
        if not obj.rss:
            return 0
        for o in reversed(list(get_feed(obj.rss))):
            if not o:
                continue
            feed = Feed()
            ob.update(feed, o)
            ob.update(feed, obj)
            u = urllib.parse.urlparse(feed.link)
            url = "%s://%s/%s" % (u.scheme, u.netloc, u.path)
            if url in self.seen.urls:
                continue
            self.seen.urls.append(url)
            counter += 1
            objs.append(feed)
            if self.cfg.dosave:
                try:
                    date = file_time(to_time(feed.published))
                except:
                    date = False
                if date:
                    feed.save(stime=date)
                else:
                    feed.save()
        self.seen.save()
        for o in objs:
            k.fleet.announce(self.display(o))
        return counter

    def join(self):
        for thr in self._thrs:
            thr.join()

    def run(self):
        res = []
        thrs = []
        for o in k.db.all("obot.rss.Rss"):
            thrs.append(k.launch(self.fetch, o))
        for thr in thrs:
            res.append(thr.join())
        return res

    def start(self, repeat=True):
        last(self.cfg)
        last(self.seen)
        if repeat:
            repeater = Repeater(600, self.run)
            repeater.start()
            return repeater

    def stop(self):
        self.seen.save()

fetcher = Fetcher()

def get_feed(url):
    result = ""
    if k.cfg.debug:
        return [Object(), Object()]
    try:
        result = get_url(url).data
    except urllib.error.HTTPError as ex:
        logging.error("%s: %s" % (url, ex))
        yield None
    if feedparser:
        result = feedparser.parse(result)
        if "entries" in result:
            for entry in result["entries"]:
                yield entry

def file_time(timestamp):
    return str(datetime.datetime.fromtimestamp(timestamp)).replace(" ", os.sep) + "." + str(random.randint(111111, 999999))

def delete(event):
    if not event.args:
        event.reply("delete <match>")
        return
    selector = {"rss": event.args[0]}
    nr = 0
    for rss in k.db.find("obot.rss.Rss", selector):
        nr += 1
        rss._deleted = True
        rss.save()
    event.reply("ok %s" % nr)

def display(event):
    if len(event.args) < 2:
        event.reply("display <feed> key1,key2,etc.")
        return
    nr = 0
    setter = {"display_list": event.args[1]}
    for o in k.db.find("obot.rss.Rss", {"rss": event.args[0]}):
        nr += 1
        ob.edit(o, setter)
        o.save()
    event.reply("ok %s" % nr)

def feed(event):
    match = ""
    if event.args:
        match = event.args[0]
    nr = 0
    diff = time.time() - to_time(day())
    res = list(k.db.find("obot.rss.Feed", {"link": match}, delta=-diff))
    for o in res:
        if match:
            event.reply("%s %s - %s - %s - %s" % (nr, o.title, o.summary, o.updated or o.published or "nodate", o.link))
        nr += 1
    if nr:
        return
    res = list(k.db.find("obot.rss.Feed", {"title": match}, delta=-diff))
    for o in res:
        if match:
            event.reply("%s %s - %s - %s" % (nr, o.title, o.summary, o.link))
        nr += 1
    res = list(k.db.find("obot.rss.Feed", {"summary": match}, delta=-diff))
    for o in res:
        if match:
            event.reply("%s %s - %s - %s" % (nr, o.title, o.summary, o.link))
        nr += 1
    if not nr:
        event.reply("no results found")
 
def fetch(event):
    res = fetcher.run()
    event.reply("fetched %s" % ",".join([str(x) for x in res]))

def rss(event):
    if not event.rest or "http" not in event.rest:
        nr = 0
        res = list(k.db.find("obot.rss.Rss", {"rss": ""}))
        if res:
            for o in res:
                event.reply("%s %s" % (nr, o.rss))
                nr += 1
        else:
            event.reply("rss <url>")
        return
    o = Rss()
    o.rss = event.rest
    o.save()
    event.reply("ok 1")
