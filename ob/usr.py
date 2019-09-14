""" user management. """

import ob
import logging
import threading
import time

from ob.db import Db
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
        for o in self.db.all("ob.usr.User", s):
            return o

    def get_user(self, origin):
        u = ob.get(Users.cache, origin, None)
        if u:
            return u
        s = {"user": origin}
        for o in self.db.find("ob.usr.User", s):
            ob.set(Users.cache, origin, o)
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
