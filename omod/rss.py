# OLIB - object library
#
#

import datetime
import html.parser
import ol
import os
import random
import re
import time
import urllib

from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

debug = False

try:
    import feedparser
    gotparser = True
except ModuleNotFoundError:
    gotparser = False

debug = False

timestrings = [
    "%a, %d %b %Y %H:%M:%S %z",
    "%d %b %Y %H:%M:%S %z",
    "%d %b %Y %H:%M:%S",
    "%a, %d %b %Y %H:%M:%S",
    "%d %b %a %H:%M:%S %Y %Z",
    "%d %b %a %H:%M:%S %Y %z",
    "%a %d %b %H:%M:%S %Y %z",
    "%a %b %d %H:%M:%S %Y",
    "%d %b %Y %H:%M:%S",
    "%a %b %d %H:%M:%S %Y",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dt%H:%M:%S+00:00",
    "%a, %d %b %Y %H:%M:%S +0000",
    "%d %b %Y %H:%M:%S +0000",
    "%d, %b %Y %H:%M:%S +0000"
]


def init(krn):
    f = Fetcher()
    f.start()
    return f

class Cfg(ol.Cfg):

    def __init__(self):
        super().__init__()
        self.dosave = True

class Feed(ol.Default):

    pass

class Rss(ol.Object):

    def __init__(self):
        super().__init__()
        self.rss = ""

class Seen(ol.Object):

    def __init__(self):
        super().__init__()
        self.urls = []

class Fetcher(ol.Object):

    cfg = ol.Cfg()
    seen = Seen()

    def __init__(self):
        super().__init__()
        self._thrs = []

    def display(self, o):
        result = ""
        dl = []
        try:
            dl = o.display_list.split(",")
        except AttributeError:
            pass
        if not dl:
            dl = self.cfg.display_list.split(",")
        if not dl or not dl[0]:
            dl = ["title", "link"]
        for key in dl:
            if not key:
                continue
            data = ol.get(o, key, None)
            if key == "link" and self.cfg.tinyurl:
                datatmp = get_tinyurl(data)
                if datatmp:
                    data = datatmp[0]
            if data:
                data = data.replace("\n", " ")
                data = strip_html(data.rstrip())
                data = unescape(data)
                result += data.rstrip()
                result += " - "
        return result[:-2].rstrip()

    def fetch(self, rssobj):
        counter = 0
        objs = []
        if not rssobj.rss:
            return 0
        for o in reversed(list(get_feed(rssobj.rss))):
            if not o:
                continue
            f = Feed()
            ol.update(f, rssobj)
            ol.update(f, o)
            u = urllib.parse.urlparse(f.link)
            if u.path and not u.path == "/":
                url = "%s://%s/%s" % (u.scheme, u.netloc, u.path)
            else:
                url = f.link
            if url in Fetcher.seen.urls:
                continue
            Fetcher.seen.urls.append(url)
            counter += 1
            objs.append(f)
            if self.cfg.dosave:
                ol.save(f)
        if objs:
            ol.save(Fetcher.seen)
        for o in objs:
            txt = self.display(o)
            for bot in ol.bus.bus:
                bot.announce(txt)
        return counter

    def run(self):
        thrs = []
        for o in ol.dbs.all("omod.rss.Rss"):
            thrs.append(ol.tsk.launch(self.fetch, o))
        return thrs

    def start(self, repeat=True):
        ol.dbs.last(Fetcher.cfg)
        ol.dbs.last(Fetcher.seen)
        if repeat:
            repeater = Repeater(300.0, self.run)
            repeater.start()

    def stop(self):
        ol.save(self.seen)

fetcher = Fetcher()

def get_feed(url):
    if debug:
        return [ol.Object(), ol.Object()]
    try:
        result = get_url(url)
    except (HTTPError, URLError):
        return [Object(), Object()]
    if gotparser:
        result = feedparser.parse(result.data)
        if "entries" in result:
            for entry in result["entries"]:
                yield entry
    else:
        print("feedparser is missing")
        return [Object(), Object()]

def file_time(timestamp):
    s = str(datetime.datetime.fromtimestamp(timestamp))
    return s.replace(" ", os.sep) + "." + str(random.randint(111111, 999999))

def get_tinyurl(url):
    postarray = [
        ('submit', 'submit'),
        ('url', url),
        ]
    postdata = urlencode(postarray, quote_via=quote_plus)
    req = Request('http://tinyurl.com/create.php', data=bytes(postdata, "UTF-8"))
    req.add_header('User-agent', useragent())
    for txt in urlopen(req).readlines():
        line = txt.decode("UTF-8").strip()
        i = re.search('data-clipboard-text="(.*?)"', line, re.M)
        if i:
            return i.groups()
    return []

def get_url(url):
    url = urllib.parse.urlunparse(urllib.parse.urlparse(url))
    req = urllib.request.Request(url)
    req.add_header('User-agent', useragent())
    response = urllib.request.urlopen(req)
    response.data = response.read()
    return response

def strip_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def to_time(daystr):
    daystr = daystr.strip()
    if "," in daystr:
        daystr = " ".join(daystr.split(None)[1:7])
    elif "(" in daystr:
        daystr = " ".join(daystr.split(None)[:-1])
    else:
        try:
            d, h = daystr.split("T")
            h = h[:7]
            daystr = " ".join([d, h])
        except (ValueError, IndexError):
            pass
    res = 0
    for tstring in timestrings:
        try:
            res = time.mktime(time.strptime(daystr, tstring))
            break
        except ValueError:
            try:
                res = time.mktime(time.strptime(" ".join(daystr.split()[:-1]), tstring))
            except ValueError:
                pass
        if res:
            break
    return res

def unescape(text):
    txt = re.sub(r"\s+", " ", text)
    return html.parser.HTMLParser().unescape(txt)

def useragent():
    return 'Mozilla/5.0 (X11; Linux x86_64) OLIB +http://github.com/bthate/olib)'

def rm(event):
    if not event.args:
        return
    selector = {"rss": event.args[0]}
    nr = 0
    got = []
    for o in find("omod.rss.Rss", selector):
        nr += 1
        o._deleted = True
        got.append(o)
    for o in got:
        save(o)
    event.reply("ok")

def dpl(event):
    if len(event.args) < 2:
        return
    setter = {"display_list": event.args[1]}
    for o in ol.dbs.find("omod.rss.Rss", {"rss": event.args[0]}):
        ol.edit(o, setter)
        ol.save(o)
    event.reply("ok")

def fed(event):
    if not event.args:
        return
    match = event.args[0]
    nr = 0
    res = list(find("omod.rss.Feed", {"link": match}))
    for o in res:
        if match:
            event.reply("%s %s - %s - %s" % (nr,
                                                  o.title,
                                                  o.summary,
                                                  o.link))
        nr += 1
    if nr:
        return
    res = list(ol.dbs.find("omod.rss.Feed", {"title": match}))
    for o in res:
        if match:
            event.reply("%s %s - %s - %s" % (nr, o.title, o.summary, o.link))
        nr += 1
    res = list(ol.dbs.find("omod.rss.Feed", {"summary": match}))
    for o in res:
        if match:
            event.reply("%s %s - %s - %s" % (nr, o.title, o.summary, o.link))
        nr += 1

def ftc(event):
    res = []
    thrs = []
    fetchr = Fetcher()
    fetchr.start(False)
    thrs = fetchr.run()
    for thr in thrs:
        res.append(thr.join() or 0)
    if res:
        event.reply("fetched %s" % ",".join([str(x) for x in res]))
        return

def rss(event):
    if not event.args:
        return
    url = event.args[0]
    res = list(ol.dbs.find("omod.rss.Rss", {"rss": url}))
    if res:
        return
    o = Rss()
    o.rss = event.args[0]
    ol.save(o)
    event.reply("ok")
