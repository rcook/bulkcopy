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
    def __init__(self, config_dir, user, api_token):
        self._user = user
        self._api_token = api_token

    @property
    def provider_name(self): return "GitHub"

    def user_projects(self):
        projects = []

        url = make_url(_GITHUB_API_URL, "users", self._user, "repos")
        while True:
            r = self._do_request("get", url)
            projects.extend(map(lambda o: _make_project(self, o), r.json()))
            next_link = r.links.get("next")
            if next_link is None: break
            url = next_link["url"]

        return projects

    def project(self, project_name):
        r = self._do_request(
            "get",
            _GITHUB_API_URL,
            "repos",
            self._user,
            project_name)
        return _make_project(self, r.json())

    def delete_project(self, project, confirmation_token=False):
        if not confirmation_token:
            raise RuntimeError("Dangerous operation disallowed")

        if self != project.provider:
            raise RuntimeError("Project does not belong to this provider")

        self._do_request(
            "delete",
            _GITHUB_API_URL,
            "repos",
            self._user,
            project.name)

    def _do_request(self, method, *args, **kwargs):
        url = make_url(*args, **kwargs)
        r = requests.request(method, url, auth=(self._user, self._api_token))
        r.raise_for_status()
        return r
