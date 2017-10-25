##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

import requests
import urllib

from repotoollib.project import Project
from repotoollib.util import make_url

_GITHUB_API_URL = "https://api.github.com"

def _make_project(project_obj):
    clone_links = {
        "https": project_obj["html_url"],
        "ssh": project_obj["ssh_url"]
    }
    return Project(
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

    def user_projects(self):
        projects = []

        url = make_url(_GITHUB_API_URL, "users", self._user, "repos")
        while True:
            r = requests.get(
                url,
                auth=(self._user, self._api_token))
            r.raise_for_status()

            projects.extend(map(_make_project, r.json()))
            next_link = r.links.get("next")
            if next_link is None: break
            url = next_link["url"]

        return projects
