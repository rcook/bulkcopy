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
        r = requests.get(
            make_url(_GITHUB_API_URL, "users", args.user, "repos"),
            auth=(self._user, self._api_token))
        r.raise_for_status()
        projects = map(_make_project, r.json())
        return projects
