##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from __future__ import print_function
import os
import yaml

from pyprelude.file_system import make_path
from requests_oauthlib import OAuth2Session

from repotoollib.project import Project
from repotoollib.util import make_url

_BITBUCKET_AUTH_URL = "https://bitbucket.org/site/oauth2/authorize"
_BITBUCKET_TOKEN_URL = "https://bitbucket.org/site/oauth2/access_token"
_BITBUCKET_API_URL = "https://api.bitbucket.org/2.0"

def _make_project(provider, project_obj):
    clone_links = { x["name"]: x["href"] for x in project_obj["links"]["clone"] }
    return Project(
        provider,
        project_obj["uuid"],
        project_obj["name"],
        project_obj["full_name"],
        project_obj["description"],
        project_obj["scm"],
        project_obj["is_private"],
        False,
        clone_links)

class Bitbucket(object):
    def __init__(self, config_dir, user, api_key, api_secret):
        self._cached_token_path = make_path(config_dir, "bitbucket.token.yaml")
        self._user = user
        self._api_key = api_key
        self._api_secret = api_secret
        self._client = None

    @property
    def provider_name(self): return "Bitbucket"

    def user_projects(self):
        projects = []
        url = make_url(_BITBUCKET_API_URL, "repositories", self._user)
        while url is not None:
            projects_obj = self._get(url)
            projects.extend(map(lambda o: _make_project(self, o), projects_obj["values"]))
            url = projects_obj.get("next")

        return projects

    def delete_project(self, name_or_id):
        self._delete(_BITBUCKET_API_URL, "repositories", self._user, name_or_id)

    def _get(self, *args, **kwargs):
        url = make_url(*args, **kwargs)
        self._do_oauth_dance()
        r = self._client.get(url)
        r.raise_for_status()
        return r.json()

    def _delete(self, *args, **kwargs):
        url = make_url(*args, **kwargs)
        self._do_oauth_dance()
        r = self._client.delete(url)
        r.raise_for_status()

    def _do_oauth_dance(self):
        if self._client is None:
            def _update_token(token):
                self._save_token(token)

            token = self._load_token()
            self._client = OAuth2Session(
                self._api_key,
                token=token,
                auto_refresh_url=_BITBUCKET_TOKEN_URL,
                auto_refresh_kwargs={ "client_id": self._api_key, "client_secret": self._api_secret },
                token_updater=_update_token)

            if token is None:
                auth_url = self._client.authorization_url(_BITBUCKET_AUTH_URL)
                print("Please go here and authorize: {}".format(auth_url[0]))
                redirect_response = raw_input("Paste full redirect URL here: ")
                token = self._client.fetch_token(
                    _BITBUCKET_TOKEN_URL,
                    authorization_response=redirect_response,
                    username=self._api_key,
                    password=self._api_secret)
                self._save_token(token)

    def _load_token(self):
        if os.path.isfile(self._cached_token_path):
            with open(self._cached_token_path, "rt") as f:
                return yaml.load(f)
        else:
            return None

    def _save_token(self, token):
        parent_dir = os.path.dirname(self._cached_token_path)
        if not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)
        with open(self._cached_token_path, "wt") as f:
            yaml.dump(token, f, default_flow_style=False)
