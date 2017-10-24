from requests_oauthlib import OAuth2Session

from bulkcopylib.url_cache import UrlCache

_BITBUCKET_AUTH_URL = "https://bitbucket.org/site/oauth2/authorize"
_BITBUCKET_TOKEN_URL = "https://bitbucket.org/site/oauth2/access_token"

class _BitbucketUrlProvider(object):
    def __init__(self, api_key, api_secret):
        self._api_key = api_key
        self._api_secret = api_secret
        self._client = None

    def get(self, url):
        self._do_oauth_dance()
        response = self._client.get(url)
        response.raise_for_status()
        return response.content

    def _do_oauth_dance(self):
        if self._client is None:
            self._client = OAuth2Session(self._api_key)
            auth_url = self._client.authorization_url(_BITBUCKET_AUTH_URL)
            print("Please go here and authorize: {}".format(auth_url[0]))
            redirect_response = raw_input("Paste full redirect URL here: ")
            self._client.fetch_token(
                _BITBUCKET_TOKEN_URL,
                authorization_response=redirect_response,
                username=self._api_key,
                password=self._api_secret)

def make_bitbucket_url_cache(api_key, api_secret, cache_dir):
    url_provider = _BitbucketUrlProvider(api_key, api_secret)
    return UrlCache(cache_dir, url_provider=url_provider)
