#!/usr/bin/env python
##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from __future__ import print_function
import argparse
import json
import os

from pyprelude.file_system import make_path

from bulkcopylib.bitbucket import make_bitbucket_url_cache
from bulkcopylib.util import make_url

_BITBUCKET_API_URL = "https://api.bitbucket.org/2.0"

def _main(args):
    cache = make_bitbucket_url_cache(args.bitbucket_key, args.bitbucket_secret, args.cache_dir)

    x = []
    next_url = make_url(_BITBUCKET_API_URL, "repositories", args.user)
    while next_url is not None:
        repos_data = cache.fetch(next_url)
        repos = json.loads(repos_data)
        values = repos["values"]
        x.extend(values)
        next_url = repos.get("next")

    print(len(x))

    #for key, value in repos.iteritems():
    #    print("{}={}".format(key, value))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", "-c", default=make_path(os.path.expanduser("~/.bulkcopy")))
    parser.add_argument("--user", "-u", default=os.environ.get("USERNAME"))
    parser.add_argument("--bitbucket-key", "-k", default=os.environ.get("BITBUCKET_API_KEY"))
    parser.add_argument("--bitbucket-secret", "-s", default=os.environ.get("BITBUCKET_API_SECRET"))
    args = parser.parse_args()
    _main(args)