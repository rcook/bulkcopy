#!/usr/bin/env python
##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from __future__ import print_function
import configargparse
import itertools
import os
import re

from pyprelude.file_system import make_path

from repotoollib.bitbucket import Bitbucket
from repotoollib.github import GitHub
from repotoollib.gitlab import GitLab

def _filter_projects(filter_expr, projects):
    if filter_expr is None:
        return projects
    else:
        regex = re.compile(filter_expr)
        return filter(lambda p: p.scm == "git" and regex.match(p.name) is not None, projects)

def _dump_all(projects):
    for project in projects:
        print("{} [{}] {}".format(project.name, project.id, project.clone_link("ssh")))

def _dump_similar(projects):
    groups = itertools.groupby(projects, lambda p: p.name)
    for key, group_iter in groups:
        group = list(group_iter)
        if len(group) > 1:
            print("{}:".format(key))
            for project in group:
                print("{} [{}] {}".format(project.name, project.id, project.clone_link("ssh")))

def _main_inner(args):
    services = [
        Bitbucket(args.config_dir, args.user, args.bitbucket_api_key, args.bitbucket_api_secret),
        GitLab(args.config_dir, args.user, args.gitlab_api_token),
        GitHub(args.config_dir, args.user, args.github_api_token)
    ]

    all_projects = []
    for service in services:
        all_projects.extend(service.user_projects())

    projects = sorted(_filter_projects(args.project_filter_expr, all_projects), key=lambda p: p.name)
    #_dump_all(projects)
    _dump_similar(projects)

def _main():
    default_config_dir = make_path(os.path.expanduser("~/.repotool"))
    default_config_path = make_path(default_config_dir, "config.yaml")
    parser = configargparse.ArgumentParser(default_config_files=[default_config_path])
    parser.add_argument("--config-dir", "-c", default=default_config_dir)
    parser.add_argument("--user", "-u", default=os.environ.get("USERNAME"))
    parser.add_argument("--bitbucket-api-key", "-k", env_var="BITBUCKET_API_KEY", required=True, is_config_file=True)
    parser.add_argument("--bitbucket-api-secret", "-s", env_var="BITBUCKET_API_SECRET", required=True, is_config_file=True)
    parser.add_argument("--gitlab-api-token", "-t", env_var="GITLAB_API_TOKEN", required=True, is_config_file=True)
    parser.add_argument("--github-api-token", "-g", env_var="GITHUB_API_TOKEN", required=True, is_config_file=True)
    parser.add_argument("--filter", "-f", dest="project_filter_expr", default=None)
    args = parser.parse_args()
    _main_inner(args)

if __name__ == "__main__":
    _main()
