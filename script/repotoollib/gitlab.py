##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

import requests
import urllib

from repotoollib.owner import Owner
from repotoollib.project import Project
from repotoollib.util import make_url

_GITLAB_API_URL = "https://gitlab.com/api/v4"

def _make_project(provider, project_obj):
    clone_links = {
        "https": project_obj["http_url_to_repo"],
        "ssh": project_obj["ssh_url_to_repo"]
    }

    owner_obj = project_obj.get("owner")
    owner = None if owner_obj is None else provider._get_owner(owner_obj)

    source_obj = project_obj.get("forked_from_project")
    source = None if source_obj is None else _make_project(provider, source_obj)

    visibility_str = project_obj.get("visibility")
    is_private = False if visibility_str is None else visibility_str == "private"

    return Project(
        provider,
        source,
        owner,
        int(project_obj["id"]),
        project_obj["name"],
        project_obj["name_with_namespace"],
        project_obj["description"],
        "git",
        is_private,
        project_obj.get("archived", False),
        clone_links)

class GitLab(object):
    @staticmethod
    def make_sample_config():
        return {
            "name": "gitlab",
            "type": "gitlab",
            "user": "user",
            "api-token": "api-token"
        }

    @staticmethod
    def parse_config(config_dir, default_user, obj):
        name = obj["name"]
        user = obj.get("user", default_user)
        api_token = obj["api-token"]
        return GitLab(name, config_dir, user, api_token)

    def __init__(self, name, config_dir, user, api_token):
        self._name = name
        self._user = user
        self._api_token = api_token
        self._owners = {}

    @property
    def name(self): return self._name

    @property
    def provider_name(self): return "GitLab"

    def get_project(self, project_name):
        r = self._do_request("get", "projects", self._encode_project_name(project_name), private_token=self._api_token)
        return _make_project(self, r.json())

    def get_projects(self, include_archived=False):
        query = {
            "private_token": self._api_token,
            "per_page": 300
        }

        if include_archived:
            query["archived"] = True

        projects = []
        while True:
            r = self._do_request("get", "users", self._user, "projects", query)
            projects.extend(map(lambda o: _make_project(self, o), r.json()))
            page_id = r.headers.get("X-Next-Page")
            if page_id is None or len(page_id) == 0: break
            query["page"] = page_id

        return projects

    def create_project(self, project_name, visibility="private"):
        url = make_url(_GITLAB_API_URL, "projects", private_token=self._api_token)
        r = requests.post(url, data={ "name": project_name, "visibility": visibility })
        r.raise_for_status()

    def delete_project(self, project, confirmation_token=False):
        if not confirmation_token:
            raise RuntimeError("Dangerous operation disallowed")

        if self != project.provider:
            raise RuntimeError("Project does not belong to this provider")

        url = make_url(_GITLAB_API_URL, "projects", self._encode_project_name(project.name))
        r = requests.delete(url, data={ "private_token": self._api_token })
        r.raise_for_status()

    def archive_project(self, project, confirmation_token=False):
        if not confirmation_token:
            raise RuntimeError("Dangerous operation disallowed")

        if self != project.provider:
            raise RuntimeError("Project does not belong to this provider")

        url = make_url(_GITLAB_API_URL, "projects", self._encode_project_name(project.name), "archive")
        r = requests.post(url, data={ "private_token": self._api_token })
        r.raise_for_status()

    def _encode_project_name(self, project_name):
        return urllib.quote_plus("{}/{}".format(self._user, project_name))

    def _do_request(self, method, *args, **kwargs):
        url = make_url(*[_GITLAB_API_URL] + list(args), **kwargs)
        return self._do_request_raw(method, url)

    def _do_request_raw(self, method, url):
        r = requests.request(method, url)
        r.raise_for_status()
        return r

    def _get_owner(self, owner_obj):
        id = owner_obj["id"]
        owner = self._owners.get(id)
        if owner is not None:
            return owner

        owner = Owner(
            "user",
            id,
            owner_obj["username"])
        self._owners[id] = owner
        return owner
