##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

import requests
import urllib

from repotoollib.project import Project
from repotoollib.util import make_url

_GITLAB_API_URL = "https://gitlab.com/api/v4"

def _encode_project_name_or_id(user, name_or_id):
    if isinstance(name_or_id, int):
        return str(name_or_id)
    else:
        return urllib.quote_plus("{}/{}".format(user, name_or_id))

def _make_project(project_obj):
    clone_links = {
        "https": project_obj["http_url_to_repo"],
        "ssh": project_obj["ssh_url_to_repo"]
    }
    return Project(
        int(project_obj["id"]),
        project_obj["name"],
        project_obj["name_with_namespace"],
        project_obj["description"],
        "git",
        project_obj["visibility"] == "private",
        project_obj["archived"],
        clone_links)

class GitLab(object):
    def __init__(self, config_dir, user, api_token):
        self._user = user
        self._api_token = api_token

    def user_projects(self):
        query = {
            "private_token": self._api_token,
            "per_page": 300
        }

        projects = []
        while True:
            url = make_url(
                _GITLAB_API_URL,
                "users",
                self._user,
                "projects",
                query)
            r = requests.get(url)
            r.raise_for_status()

            projects.extend(map(_make_project, r.json()))

            page_id = r.headers.get("X-Next-Page")
            if page_id is None or len(page_id) == 0: break
            query["page"] = page_id

        return projects

    def create_project(self, name, visibility="private"):
        url = make_url(
            _GITLAB_API_URL,
            "projects",
            private_token=self._api_token)
        r = requests.post(url, data={ "name": name, "visibility": visibility })
        r.raise_for_status()

    def delete_project(self, name_or_id):
        url = make_url(
            _GITLAB_API_URL,
            "projects",
            _encode_project_name_or_id(self._user, name_or_id))
        r = requests.delete(url, data={ "private_token": self._api_token })
        r.raise_for_status()

    def archive_project(self, name_or_id):
        url = make_url(
            _GITLAB_API_URL,
            "projects",
            _encode_project_name_or_id(self._user, name_or_id),
            "archive")
        r = requests.post(url, data={ "private_token": self._api_token })
        r.raise_for_status()
