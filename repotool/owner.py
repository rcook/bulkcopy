##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from repotool.table import Table

class Owner(object):
    def __init__(self, type, id, user_name):
        self._type = type
        self._id = id
        self._user_name = user_name

    def __repr__(self):
        return "{} ({}:{})".format(self._user_name, self._id, self._type)

    @property
    def type(self): return self._type

    @property
    def id(self): return self._id

    @property
    def user_name(self): return self._user_name
