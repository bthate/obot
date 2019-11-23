""" operator commands. """

import logging
import ob
import obot
import os
import time
import threading

from ob import Object, k
from ob.utl import get_name
from ob.dbs import Db
from ob.err import ENOUSER
from ob.pst import Persist

def __dir__():
    return ("User", "Users")

class User(Persist):

    def __init__(self):
        super().__init__()
        self.user = ""
        self.perms = []

class Users(Persist):

    cache = Persist()
    db = Db()
    userhosts = Persist()

    def allowed(self, origin, perm):
        if ob.k.cfg.nousers:
            return True
        perm = perm.upper()
        user = self.get_user(origin)
        if user:
            if perm in user.perms:
                return True
        txt = "denied %s %s" % (origin, perm)
        logging.error(txt)
        return False

    def delete(self, origin, perm):
        for user in self.get_users(origin):
            try:
                user.perms.remove(perm)
                user.save()
                return True
            except ValueError:
                pass

    def get_users(self, origin=""):
        s = {"user": origin}
        return self.db.all("obot.usr.User", s)

    def get_user(self, origin):
        u =  list(self.get_users())
        if u:
            return u[-1]
 
    def meet(self, origin, perms=None):
        if not perms:
            perms = []
        user = self.get_user(origin)
        if not user:
            user = User()
        user.user = origin
        user.perms = perms + ["USER", ]
        if perms:
            user.perms.extend(perms)
        user.save(timed=True)
        return user

    def oper(self, origin):
        user = User()
        user.user = origin
        user.perms = ["OPER", "USER"]
        ob.set(Users.cache, origin, user)
        return user

    def perm(self, origin, permission):
        user = self.get_user(origin)
        if not user:
            raise ENOUSER(origin)
        if permission.upper() not in user.perms:
            user.perms.append(permission.upper())
            user.save()
        return user

def meet(event):
    if not event.args:
        event.reply("meet origin [permissions]")
        return
    try:
        origin, *perms = event.args[:]
    except ValueError:
        event.reply("|".join(sorted(k.users.userhosts)))
        return
    origin = ob.get(k.users.userhosts, origin, origin)
    u = k.users.meet(origin, perms)
    event.reply("added %s" % u.user)
