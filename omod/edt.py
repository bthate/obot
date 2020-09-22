# OLIB - object library
#
#

import ol

def edt(event):
    if not event.args:
        f = ol.utl.list_files(ol.wd)
        if f:
            event.reply(f)
        return
    cn = event.args[0]
    if "." not in cn:
        shorts = ol.utl.find_shorts("omod")
        if shorts:
            cn = ol.get(shorts, cn, cn)
    try:
        l = ol.dbs.lasttype(cn)
    except IndexError:
        return
    if not l:
        try:
            c = ol.get_cls(cn)
            l = c()
            event.reply("created %s" % cn)
        except ENOCLASS:
            event.reply(ol.utl.list_files(ol.wd))
            return
    if len(event.args) == 1:
        event.reply(l)
        return
    ol.edit(l, event.sets)
    ol.save(l)
    event.reply("ok")
