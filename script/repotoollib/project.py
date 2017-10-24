##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

class Project(object):
    def __init__(self, id, name, full_name, description, scm, is_private, is_archived, clone_links):
        self._id = id
        self._name = name
        self._full_name = full_name
        self._description = description
        self._scm = scm
        self._is_private = is_private
        self._is_archived = is_archived
        self._clone_links = clone_links

    @property
    def id(self): return self._id

    @property
    def name(self): return self._name

    @property
    def scm(self): return self._scm

