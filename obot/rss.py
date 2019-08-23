""" rss to channel. """

import datetime
import io
import logging
import feedparser
import ob
import obot
import os
import random
import re
import urllib

from ob import Cfg, Object, launch, last
from ob.clock import Repeater
from ob.times import to_time
from ob.utils import get_url, strip_html, unescape

from ob.kernel import k

def __dir__():
    return ("Cfg", "Feed", "Fetcher", "Rss", "Seen", "delete" ,"fetch", "init", "rss")

def init():
    fetcher = Fetcher()
    fetcher.start()
    return fetcher

class Cfg(Cfg):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_list = ["title", "description", "link"]
        self.dosave = False

class Feed(Object):

    pass

class Seen(Object):

    def __init__(self):
        super().__init__()
        self.urls = []

class Fetcher(Object):


    def __init__(self):
        super().__init__()
        self.cfg = Cfg()
        self.seen = Seen()
        self._thrs = []

    def display(self, o):
        result = ""
        if "display_list" in dir(o):
            dl = o.display_list
        else:
            dl = self.cfg.display_list
        for key in dl:
            data = o._get(key, None)
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
            feed.update(o)
            feed.update(obj)
            u = urllib.parse.urlparse(feed.link)
            url = "%s://%s/%s" % (u.scheme, u.netloc, u.path)
            if url in self.seen.urls:
                continue
            self.seen.urls.append(url)
            counter += 1
            objs.append(feed)
            if self.cfg.dosave and "updated" in dir(feed):
                date = file_time(to_time(feed.updated))
                feed.save(stime=date)
        self.seen.save()
        for o in objs:
            k.fleet.announce(self.display(o))
        return counter

    def join(self):
        for thr in self._thrs:
            thr.join()

    def run(self):
        for o in k.db.all("obot.rss.Rss"):
            self._thrs.append(launch(self.fetch, o))
        return self._thrs

    def start(self, repeat=True):
        last(self.cfg)
        last(self.seen)
        if repeat:
            repeater = Repeater(600, self.run)
            repeater.start()
            return repeater

    def stop(self):
        self.seen.save()

class Rss(Object):

    def __init__(self):
        super().__init__()
        self.rss = ""

def get_feed(url):
    result = ""
    try:
        result = get_url(url).data
    except urllib.error.HTTPError as ex:
        logging.error("%s: %s" % (url, ex))
        yield None
    result = feedparser.parse(result)
    if "entries" in result:
        for entry in result["entries"]:
            yield entry

def file_time(timestamp):
    return str(datetime.datetime.fromtimestamp(timestamp)).replace(" ", os.sep) + "." + str(random.randint(111111, 999999))

def delete(event):
    """ delete matching rss objects. """
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

def fetch(event):
    """ fetch registered feeds. """
    fetcher = Fetcher()
    fetcher.start(repeat=False)
    res = fetcher.run()
    event.reply("fetched %s" % ",".join([str(x.join()) for x in res]))

def rss(event):
    """ use to add a rss feed or get a overview of registered rss feeds. """
    if not event.rest or "http" not in event.rest:
        nr = 0
        for o in k.db.find("obot.rss.Rss", {"rss": ""}):
            event.reply("%s %s" % (nr, o.rss))
        return
    o = Rss()
    o.rss = event.rest
    o.save()
    event.reply("ok 1")
