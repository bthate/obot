""" user management. """

import logging
import threading
import time

from ob import Object
from ob.db import Db
from ob.errors import ENOUSER

def __dir__():
    return ("User", "Users", "meet")

class User(Object):

    def __init__(self):
        super().__init__()
        self.user = ""
        self.perms = []

class Users(Object):

    cache = Object()
    db = Db()
    userhosts = Object()

    def allowed(self, origin, perm):
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
        for o in self.db.all("ob.user.User", s):
            return o

    def get_user(self, origin):
        u = Users.cache._get(origin, None)
        if u:
            return u
        s = {"user": origin}
        for o in self.db.find("ob.user.User", s):
            setattr(Users.cache, origin, o)
            return o

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
        setattr(Users.cache, origin, user)
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
    from ob.kernel import k
    origin = k.users.userhosts._get(origin, origin)
    u = k.users.meet(origin, perms)
    event.reply("added %s" % u.user)
