""" basic OB exceptions. """

class EBLOCKING(Exception):

    """ operation is blocking. """

class ECLASS(Exception):

    """ missing class. """

class EEMPTY(Exception):

    """ read object is empty. """

class EJSON(Exception):

    """ ill formated JSON. """

class ENOFILE(Exception):

    """ file doesn't exist. """

class ENOFUNCTION(Exception):

    """ could not fetch handler. """

class ENOMODULE(Exception):

    """ not module could be found. """

class ENOTFOUND(Exception):

    """ item is not found. """

class ENOTIMPLEMENTED(Exception):

    """ base function is not overriden. """

class ENOTXT(Exception):

    """ event has no text set. """

class ENOUSER(Exception):

    """ user is not found. """

class ENOTYPE(Exception):

    """ type is not recognised. """

class EOWNER(Exception):

    """ owner permissions are needed. """

class ETYPE(Exception):

    """ type is not knowen """

class EINIT(Exception):

    """ interrupt during initialisation. """
