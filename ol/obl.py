# OLIB
#
#

"object list"

from ol.obj import Object

class Ol(Object):

    "object list"

    def append(self, key, value):
        "add to list at self[key]"
        if key not in self:
            self[key] = []
        if isinstance(value, type(list)):
            self[key].extend(value)
        else:
            if value not in self[key]:
                self[key].append(value)

    def update(self, d):
        "update from other object list"
        for k, v in d.items():
            self.append(k, v)
