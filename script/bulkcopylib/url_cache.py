import os
import urllib
import urllib2

from pyprelude.file_system import make_path

from bulkcopylib.util import make_url

def _encode_url(url):
    return urllib.quote_plus(url)

class SimpleUrlProvider(object):
    def __init__(self):
        pass

    def get(self, *args, **kwargs):
        data = kwargs.pop("_data", None)
        return self._do_request("GET", make_url(*args, **kwargs), data=data)

    def post(self, *args, **kwargs):
        data = kwargs.pop("_data", None)
        return self._do_request("POST", make_url(*args, **kwargs), data=data)

    def delete(self, *args, **kwargs):
        data = kwargs.pop("_data", None)
        return self._do_request("DELETE", make_url(*args, **kwargs), data=data)

    def _do_request(self, method, url, data=None):
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        encoded_data = None if data is None else urllib.urlencode(data)
        request = urllib2.Request(url, data=encoded_data)
        request.get_method = lambda: method
        connection = opener.open(request)
        return connection.read()

class UrlCache(object):
    def __init__(self, cache_path, provider=SimpleUrlProvider()):
        self._provider = provider
        self._cache_path = cache_path
        if not os.path.isdir(self._cache_path):
            os.makedirs(self._cache_path)

    @property
    def provider(self): return self._provider

    def get(self, *args, **kwargs):
        url = make_url(*args, **kwargs)
        path = make_path(self._cache_path, _encode_url(url))
        if os.path.isfile(path):
            with open(path, "rb") as f:
                return f.read()
        else:
            s = self._provider.get(url)
            with open(path, "wb") as f:
                f.write(s)
            return s
