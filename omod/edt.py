# OBOT - 24/7 channel daemon
#
#

"edit objects"

from ol.dbs import lasttype
from ol.krn import get_kernel
from ol.obj import get, save
from ol.ofn import edit
from ol.utl import get_cls, list_files

def edt(event):
    "edit objects"
    if not event.args:
        import ol.krn
        assert ol.krn.wd
        f = list_files(ol.krn.wd)
        if f:
            event.reply(f)
        return
    k = get_kernel()
    cn = get(k.names, event.args[0], [event.args[0]])
    if len(cn) > 1:
        event.reply(cn)
        return
    cn = cn[0]
    try:
        l = lasttype(cn)
    except IndexError:
        return
    if not l:
        try:
            c = get_cls(cn)
            l = c()
            event.reply("created %s" % cn)
        except ol.ENOCLASS:
            event.reply(list_files(wd))
            return
    if not event.prs.sets:
        event.reply(l)
        return
    edit(l, event.prs.sets)
    save(l)
    event.reply("ok")
