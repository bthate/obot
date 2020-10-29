# OLIB
#
#

"default values"

from ol.obj import Object

class Default(Object):

    "uses default values"

    def __getattr__(self, k):
        if k not in self:
            return ""
        return self.__dict__[k]