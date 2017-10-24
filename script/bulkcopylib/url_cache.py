import os
import urllib
import urllib2

from pyprelude.file_system import make_path

def _encode_url(url):
    return urllib.quote_plus(url)

class SimpleUrlProvider(object):
    def __init__(self):
        pass

    def get(self, url):
        u = None
        try:
            u = urllib2.urlopen(url)
            return u.read()
        finally:
            if u:
                u.close()

class UrlCache(object):
    def __init__(self, cache_path, url_provider=SimpleUrlProvider()):
        self._url_provider = url_provider
        self._cache_path = cache_path
        if not os.path.isdir(self._cache_path):
            os.makedirs(self._cache_path)

    def get(self, url, bypass_cache=False):
        path = make_path(self._cache_path, _encode_url(url))
        if not bypass_cache and os.path.isfile(path):
            with open(path, "rb") as f:
                return f.read()
        else:
            s = self._url_provider.get(url)
            with open(path, "wb") as f:
                f.write(s)
            return s
