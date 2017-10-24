import json
import urllib

from bulkcopylib.url_cache import UrlCache

_GITLAB_API_URL = "https://gitlab.com/api/v4"

def _encode_project_name_or_id(user, name_or_id):
    if isinstance(name_or_id, int):
        return str(name_or_id)
    else:
        return urllib.quote_plus("{}/{}".format(user, name_or_id))

class GitLab(object):
    def __init__(self, cache, api_token, user):
        self._cache = cache
        self._api_token = api_token
        self._user = user

    def user_projects(self):
        return json.loads(self._cache.provider.get(_GITLAB_API_URL, "users", self._user, "projects", private_token=self._api_token))

    def create_project(self, name, visibility="private"):
        self._cache.provider.post(_GITLAB_API_URL, "projects", private_token=self._api_token, _data={
            "name": name,
            "visibility": visibility
        })

    def delete_project(self, name_or_id):
        self._cache.provider.delete(
            _GITLAB_API_URL,
            "projects",
            _encode_project_name_or_id(self._user, name_or_id),
            _data={ "private_token": self._api_token })

    def archive_project(self, name_or_id):
        self._cache.provider.post(
            _GITLAB_API_URL,
            "projects",
            _encode_project_name_or_id(self._user, name_or_id),
            "archive",
            _data={ "private_token": self._api_token })

def make_gitlab_url_cache(cache_dir):
    return UrlCache(cache_dir)
