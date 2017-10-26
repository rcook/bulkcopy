##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

import requests
import urllib

from repotoollib.project import Project
from repotoollib.util import make_url

_GITHUB_API_URL = "https://api.github.com"

def _make_project(provider, project_obj):
    clone_links = {
        "https": project_obj["html_url"],
        "ssh": project_obj["ssh_url"]
    }
    return Project(
        provider,
        int(project_obj["id"]),
        project_obj["name"],
        project_obj["full_name"],
        project_obj["description"],
        "git",
        project_obj["private"],
        project_obj["archived"],
        clone_links)

class GitHub(object):
    @staticmethod
    def make_sample_config():
        return {
            "name": "github",
            "type": "github",
            "user": "user",
            "api-token": "api-token"
        }

    @staticmethod
    def parse_config(config_dir, default_user, obj):
        name = obj["name"]
        user = obj.get("user", default_user)
        api_token = obj["api-token"]
        return GitHub(name, config_dir, user, api_token)

    def __init__(self, name, config_dir, user, api_token):
        self._name = name
        self._user = user
        self._api_token = api_token

    @property
    def name(self): return self._name

    @property
    def provider_name(self): return "GitHub"

    def get_project(self, project_name):
        r = self._do_request("get", "repos", self._user, project_name)
        return _make_project(self, r.json())

    def get_projects(self, include_archived=False):
        projects = []

        url = make_url(_GITHUB_API_URL, "users", self._user, "repos")
        while True:
            r = self._do_request_raw("get", url)
            projects.extend(map(lambda o: _make_project(self, o), r.json()))
            next_link = r.links.get("next")
            if next_link is None: break
            url = next_link["url"]

        return projects

    def delete_project(self, project, confirmation_token=False):
        if not confirmation_token:
            raise RuntimeError("Dangerous operation disallowed")

        if self != project.provider:
            raise RuntimeError("Project does not belong to this provider")

        self._do_request("delete", "repos", self._user, project.name)

    def _do_request(self, method, *args, **kwargs):
        url = make_url(*[_GITHUB_API_URL] + list(args), **kwargs)
        return self._do_request_raw(method, url)

    def _do_request_raw(self, method, url):
        r = requests.request(method, url, auth=(self._user, self._api_token))
        r.raise_for_status()
        return r
