from requests_oauthlib import OAuth2Session

from bulkcopylib.url_cache import UrlCache

_BITBUCKET_AUTH_URL = "https://bitbucket.org/site/oauth2/authorize"
_BITBUCKET_TOKEN_URL = "https://bitbucket.org/site/oauth2/access_token"

class _BitbucketUrlProvider(object):
    def __init__(self, bitbucket_key, bitbucket_secret):
        self._bitbucket_key = bitbucket_key
        self._bitbucket_secret = bitbucket_secret
        self._bitbucket = None

    def get(self, url):
        self._do_oauth_dance()
        response = self._bitbucket.get(url)
        response.raise_for_status()
        return response.content

    def _do_oauth_dance(self):
        if self._bitbucket is None:
            self._bitbucket = OAuth2Session(self._bitbucket_key)
            auth_url = self._bitbucket.authorization_url(_BITBUCKET_AUTH_URL)
            print("Please go here and authorize: {}".format(auth_url[0]))
            redirect_response = raw_input("Paste full redirect URL here: ")
            self._bitbucket.fetch_token(
                _BITBUCKET_TOKEN_URL,
                authorization_response=redirect_response,
                username=self._bitbucket_key,
                password=self._bitbucket_secret)

def make_bitbucket_url_cache(bitbucket_key, bitbucket_secret, cache_dir):
    url_provider = _BitbucketUrlProvider(bitbucket_key, bitbucket_secret)
    return UrlCache(url_provider, cache_dir)
