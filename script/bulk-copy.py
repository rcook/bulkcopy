#!/usr/bin/env python
##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from __future__ import print_function
import configargparse
import json
import os
import re

from pyprelude.file_system import make_path
from pysimplevcs.git_util import git_clone

from bulkcopylib.bitbucket import make_bitbucket_url_cache
from bulkcopylib.gitlab import GitLab, make_gitlab_url_cache
from bulkcopylib.util import make_url

_BITBUCKET_API_URL = "https://api.bitbucket.org/2.0"

class _RepoFilter(object):
    def __init__(self, regexp):
        self._re = re.compile(regexp)

    def is_match(self, repo):
        return self._re.match(repo["name"]) is not None

def _gitlab_example(cache_dir, gitlab_api_token, user):
    cache = make_gitlab_url_cache(cache_dir)
    g = GitLab(cache, gitlab_api_token, user)
    #g.create_project("newly-created-project")
    for project in g.user_projects():
        name = project["name"]
        is_archived = project["archived"] == "True"
        git_url = project["ssh_url_to_repo"]
        visibility = project["visibility"]
        print("{}:".format(name))
        print("  archived: {}".format(is_archived))
        print("  URL: {}".format(git_url))
        print("  visibility: {}".format(visibility))

def _main_inner(args):
    _gitlab_example(args.cache_dir, args.gitlab_api_token, args.user)
    exit(1)
    cache = make_bitbucket_url_cache(args.bitbucket_api_key, args.bitbucket_api_secret, args.cache_dir)

    repo_filter = _RepoFilter(args.filter)

    repos = []
    next_url = make_url(_BITBUCKET_API_URL, "repositories", args.user)
    while next_url is not None:
        repos_obj = json.loads(cache.get(next_url))
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

def _main():
    parser = configargparse.ArgumentParser()
    parser.add_argument("--cache-dir", "-c", default=make_path(os.path.expanduser("~/.bulkcopy")))
    parser.add_argument("--user", "-u", default=os.environ.get("USERNAME"))
    parser.add_argument("--bitbucket-api-key", "-k", env_var="BITBUCKET_API_KEY", required=True)
    parser.add_argument("--bitbucket-api-secret", "-s", env_var="BITBUCKET_API_SECRET", required=True)
    parser.add_argument("--gitlab-api-token", "-t", env_var="GITLAB_API_TOKEN", required=True)
    parser.add_argument("--filter", "-f", required=True)
    args = parser.parse_args()
    _main_inner(args)

if __name__ == "__main__":
    _main()
