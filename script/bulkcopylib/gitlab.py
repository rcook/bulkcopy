import json
import urllib

from bulkcopylib.url_cache import UrlCache

_GITLAB_API_URL = "https://gitlab.com/api/v4"

class GitLab(object):
    def __init__(self, cache, api_token, user):
        self._cache = cache
        self._api_token = api_token
        self._user = user

    def create_project(self, name, visibility="private"):
        self._cache.provider.post(_GITLAB_API_URL, "projects", private_token=self._api_token, _data={
            "name": name,
            "visibility": visibility
        })

    def delete_project(self, name):
        full_name = urllib.quote_plus("{}/{}".format(self._user, name))
        self._cache.provider.delete(_GITLAB_API_URL, "projects", full_name, _data={ "private_token": self._api_token })

    def user_projects(self):
        return json.loads(self._cache.provider.get(_GITLAB_API_URL, "users", self._user, "projects", private_token=self._api_token))

def make_gitlab_url_cache(cache_dir):
    return UrlCache(cache_dir)
