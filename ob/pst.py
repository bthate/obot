""" save/load JSON files. """

import datetime
import json
import logging
import ob
import os
import uuid

from ob.err import EEMPTY, ENOFILE
from ob.utl import cdir, locked
from ob.typ import get_cls

class Persist(ob.Object):

    """ JSON object persistence. """

    def load(self, path):
        """ load this object from disk. """
        assert path
        assert ob.workdir
        logging.debug("load %s" % path)
        lpath = os.path.join(ob.workdir, "store", path)
        if not lpath:
            cdir(lpath)
        if not os.path.exists(lpath):
            assert ENOFILE(path)
        with open(lpath, "r") as ofile:
            val = json.load(ofile, object_hook=ob.hooked)
            if not val:
                raise EEMPTY(path)
            ob.update(self, val)
        self.__path__ = path
        return self

    def save(self, path="", stime=None, timed=False):
        """ save(path="", stime=None, timed=False, strict=False)
        
            save this object to disk.
        """
        assert ob.workdir
        from ob.typ import get_type
        self.__type__ = get_type(self)
        if not path:
            try:
                path = self.__path__
            except AttributeError:
                pass
        if not path or stime:
            if not stime:
                stime = str(datetime.datetime.now()).replace(" ", os.sep)
            path = os.path.join(self.__type__, stime)
        logging.debug("save %s" % path)
        opath = os.path.join(ob.workdir, "store", path)
        cdir(opath)
        with open(opath, "w") as file:
            json.dump(self, file, default=ob.default, indent=4, sort_keys=True)
        return path
