import urllib
import urlparse

from pyprelude.util import unpack_args

def make_url(*args, **kwargs):
    base_url = "/".join(map(lambda x: x.strip("/"), unpack_args(*args)))
    parts = list(urlparse.urlparse(base_url + "/"))
    parts[4] = urllib.urlencode(kwargs)
    return urlparse.urlunparse(parts)