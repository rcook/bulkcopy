##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from repotool.table import Table

class Project(object):
    def __init__(self, provider, source, owner, id, name, full_name, description, scm, is_private, is_archived, clone_links):
        self._source = source
        self._provider = provider
        self._owner = owner
        self._id = id
        self._name = name
        self._full_name = full_name
        self._description = description
        self._scm = scm
        self._is_private = is_private
        self._is_archived = is_archived
        self._clone_links = clone_links

    def __repr__(self):
        return "{} ({}) {} ({})".format(
            self._name,
            self._id,
            self._clone_links.get("ssh", "(unknown URL)"),
            self._owner)

    @property
    def provider(self): return self._provider

    @property
    def source(self): return self._source

    @property
    def owner(self): return self._owner

    @property
    def id(self): return self._id

    @property
    def name(self): return self._name

    @property
    def full_name(self): return self._full_name

    @property
    def description(self): return self._description

    @property
    def scm(self): return self._scm

    @property
    def is_private(self): return self._is_private

    @property
    def is_archived(self): return self._is_archived

    def clone_link(self, key): return self._clone_links[key]

    def clone_link_keys(self): return self._clone_links.keys()

    def make_table(self):
        table = Table()
        table.add_row("Owner", self._owner)
        table.add_row("ID", self._id)
        table.add_row("Name", self._name)
        table.add_row("Full name", self._full_name)
        table.add_row("Description", self._description)
        table.add_row("SCM", self._scm)
        table.add_row("Private", self._is_private)
        table.add_row("Archived", self._is_archived)
        clone_link_str = ", ".join(["{}: {}".format(k, self._clone_links[k]) for k in self._clone_links])
        table.add_row("Clone links", clone_link_str)
        table.add_row("Provider", self._provider.provider_name)
        if self._source:
            table.add_row("Source", self._source.full_name)
        return table

    def delete(self, confirmation_token=True):
        if not confirmation_token:
            raise RuntimeError("Dangerous operation disallowed")

        self._provider.delete_project(self, confirmation_token=confirmation_token)

    def archive(self, confirmation_token=True):
        if not confirmation_token:
            raise RuntimeError("Dangerous operation disallowed")

        self._provider.archive_project(self, confirmation_token=confirmation_token)
