##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

import os
import subprocess
import sys
import urllib
import urlparse

from pyprelude.util import unpack_args

def make_url(*args, **kwargs):
    """
    >>> make_url("https://host/api", "users", "user-name", "projects", token="api_token")
    'https://host/api/users/user-name/projects?token=api_token'
    >>> make_url("https://host/api", "users", "user-name", "projects/", token="api_token")
    'https://host/api/users/user-name/projects/?token=api_token'
    >>> make_url("https://host/api", "users", "user-name", "projects", "/", token="api_token")
    'https://host/api/users/user-name/projects/?token=api_token'
    >>> make_url("https://host/api", "users", "user-name", "projects", [("token", "api_token"), ("aaa", "bbb")])
    'https://host/api/users/user-name/projects?token=api_token&aaa=bbb'
    >>> make_url("https://host/api", "users", "user-name", "projects/", [("token", "api_token"), ("aaa", "bbb")])
    'https://host/api/users/user-name/projects/?token=api_token&aaa=bbb'
    >>> make_url("https://host/api", "users", "user-name", "projects", [("token", "api_token"), ("aaa", "bbb")], other="value")
    'https://host/api/users/user-name/projects?token=api_token&aaa=bbb&other=value'
    >>> make_url("https://host/api", "users", "user-name", "projects/", [("token", "api_token"), ("aaa", "bbb")], other="value")
    'https://host/api/users/user-name/projects/?token=api_token&aaa=bbb&other=value'
    >>> make_url("https://host/api")
    'https://host/api'
    >>> make_url("https://host/api/")
    'https://host/api/'
    >>> make_url("https://host/api", "users", "user-name", "projects")
    'https://host/api/users/user-name/projects'
    >>> make_url("https://host/api", "users", "user-name", "projects/")
    'https://host/api/users/user-name/projects/'
    >>> make_url("https://host/api", "users", "user-name", "projects", 12345)
    'https://host/api/users/user-name/projects/12345'
    >>> make_url("https://host/api", "users", "user-name", "projects", 12345, "/")
    'https://host/api/users/user-name/projects/12345/'
    """
    if len(args) == 1 and len(kwargs) == 0:
        # Return a single string unaltered
        return args[0]

    temp_args = unpack_args(*args)
    temp_arg_count = len(temp_args)

    # Handle list of tuples as last of array arguments
    if temp_arg_count > 1 and isinstance(temp_args[-1], list):
        path_fragments = temp_args[0 : -1]
        query_string = urllib.urlencode(temp_args[-1] + kwargs.items())
    elif temp_arg_count > 1 and isinstance(temp_args[-1], dict):
        path_fragments = temp_args[0 : -1]
        query_string = urllib.urlencode(temp_args[-1].items() + kwargs.items())
    else:
        path_fragments = temp_args
        query_string = urllib.urlencode(kwargs)

    path_fragments = map(str, path_fragments)
    has_trailing_slash = path_fragments[-1].endswith("/")
    path_fragments = filter(lambda f: len(f) > 0, map(lambda f: f.strip("/"), path_fragments))
    base_url = "/".join(path_fragments)

    if has_trailing_slash:
        base_url += "/"

    parts = list(urlparse.urlparse(base_url))
    parts[4] = query_string
    return urlparse.urlunparse(parts)

# https://stackoverflow.com/questions/4216985/call-to-operating-system-to-open-url
def open_browser(url):
    if sys.platform == "win32":
        os.startfile(url)
        return True
    elif sys.platform == "darwin":
        subprocess.Popen(["open", url])
        return True
    else:
        try:
            subprocess.Popen(["xdg-open", url])
            return True
        except OSError:
            return False

if __name__ == "__main__":
    import doctest
    doctest.testmod()
