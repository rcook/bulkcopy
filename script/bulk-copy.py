#!/usr/bin/env python
##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from __future__ import print_function
import argparse
import json
import os
import re

from pyprelude.file_system import make_path
from pysimplevcs.git_util import git_clone

from bulkcopylib.bitbucket import make_bitbucket_url_cache
from bulkcopylib.util import make_url

_BITBUCKET_API_URL = "https://api.bitbucket.org/2.0"

class _RepoFilter(object):
    def __init__(self, regexp):
        self._re = re.compile(regexp)

    def is_match(self, repo):
        return self._re.match(repo["name"]) is not None

def _main(args):
    cache = make_bitbucket_url_cache(args.bitbucket_key, args.bitbucket_secret, args.cache_dir)

    repo_filter = _RepoFilter(args.filter)

    repos = []
    next_url = make_url(_BITBUCKET_API_URL, "repositories", args.user)
    while next_url is not None:
        repos_obj = json.loads(cache.fetch(next_url))
        unfiltered_repos = repos_obj["values"]
        repos.extend(filter(lambda x: x["scm"] == "git" and repo_filter.is_match(x), unfiltered_repos))
        next_url = repos_obj.get("next")

    for repo in repos:
        repo_name = repo["name"]
        local_dir = make_path(args.cache_dir, "_repos", repo_name)
        if os.path.isdir(local_dir):
            print("Repo \"{}\" already mirrored".format(repo_name))
        else:
            print("Mirroring \"{}\"".format(repo_name))
            parent_dir = os.path.dirname(local_dir)
            if not os.path.isdir(parent_dir):
                os.makedirs(parent_dir)
            git_url = "git@bitbucket.org:{}/{}.git".format(args.user, repo_name)
            git_clone("--mirror", git_url, local_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", "-c", default=make_path(os.path.expanduser("~/.bulkcopy")))
    parser.add_argument("--user", "-u", default=os.environ.get("USERNAME"))
    parser.add_argument("--bitbucket-key", "-k", default=os.environ.get("BITBUCKET_API_KEY"))
    parser.add_argument("--bitbucket-secret", "-s", default=os.environ.get("BITBUCKET_API_SECRET"))
    parser.add_argument("--filter", "-f", required=True)
    args = parser.parse_args()
    _main(args)