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

from repotoollib.bitbucket import Bitbucket
from repotoollib.gitlab import GitLab

def _gitlab_example(config_dir, gitlab_api_token, user):
    cache = make_gitlab_url_cache(config_dir)
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

def _filter_projects(filter_expr, projects):
    if filter_expr is None:
        return projects
    else:
        regex = re.compile(filter_expr)
        return filter(lambda p: p.scm == "git" and regex.match(p.name) is not None, projects)

def _main_inner(args):
    """
    service = Bitbucket(
        args.config_dir,
        args.user,
        args.bitbucket_api_key,
        args.bitbucket_api_secret)
    """
    service = GitLab(
        args.config_dir,
        args.user,
        args.gitlab_api_token)

    projects = _filter_projects(args.project_filter_expr, service.user_projects())
    for project in sorted(projects, key=lambda x: x.name):
        print("{}:".format(project.name))
        print("  {}".format(project.id))
        print("  {}".format(project.scm))

    #gitlab_cache = make_gitlab_url_cache(args.config_dir)
    #gitlab = GitLab(gitlab_cache, args.gitlab_api_token, args.user)

    #for project_name in project_names:
    #    gitlab.archive_project(project_name)
    #    print("Archived {}".format(project_name))

    """
    cache = make_bitbucket_url_cache(args.bitbucket_api_key, args.bitbucket_api_secret, args.config_dir)
    client = cache.provider.client

    for project_name in project_names:
        url = make_url(_BITBUCKET_API_URL, "repositories", args.user, project_name)
        r = client.delete(url)
        r.raise_for_status()
        #r.content
        print("Deleted {}".format(project_name))
    """


    """
    #gitlab_cache = make_gitlab_url_cache(args.config_dir)
    #gitlab = GitLab(gitlab_cache, args.gitlab_api_token, args.user)
    #_gitlab_example(args.config_dir, args.gitlab_api_token, args.user)
    #exit(1)
    cache = make_bitbucket_url_cache(args.bitbucket_api_key, args.bitbucket_api_secret, args.config_dir)

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
        local_dir = make_path(args.config_dir, "_repos", repo_name)
        if os.path.isdir(local_dir):
            print("Repo \"{}\" already mirrored".format(repo_name))
        else:
            print("Mirroring \"{}\"".format(repo_name))
            parent_dir = os.path.dirname(local_dir)
            if not os.path.isdir(parent_dir):
                os.makedirs(parent_dir)
            git_url = "git@bitbucket.org:{}/{}.git".format(args.user, repo_name)
            git_clone("--mirror", git_url, local_dir)
    """

    """
    projects = []
    page_id = None
    while True:
        query = {
            "private_token": args.gitlab_api_token,
            "per_page": 300
        }
        if page_id is not None:
            query["page"] = page_id

        url = make_url(
            "https://gitlab.com/api/v4",
            "users",
            args.user,
            "projects",
            query)
        print(url)
        r = requests.get(url)

        projects_obj = r.json()
        for project in projects_obj:
            project_name = project["name"]
            if project_name.startswith("fast-export-") or project_name.startswith("backup-"):
                projects.append(project)

        page_id = r.headers.get("X-Next-Page")
        if page_id is None or len(page_id) == 0:
            break

    with open("projects.txt", "wt") as f:
        for project in projects:
            f.write(project["name"] + "\n")

    print(len(projects))
    exit(0)

    projects_obj = gitlab.user_projects()
    print(len(projects_obj))
    exit(0)
    for project in projects_obj:
        project_name = project["name"]
        if project_name.startswith("fast-export-") or project_name.startswith("backup-"):
            print(project_name)
    """

def _main():
    parser = configargparse.ArgumentParser()
    parser.add_argument("--config-dir", "-c", default=make_path(os.path.expanduser("~/.repotool")))
    parser.add_argument("--user", "-u", default=os.environ.get("USERNAME"))
    parser.add_argument("--bitbucket-api-key", "-k", env_var="BITBUCKET_API_KEY", required=True)
    parser.add_argument("--bitbucket-api-secret", "-s", env_var="BITBUCKET_API_SECRET", required=True)
    parser.add_argument("--gitlab-api-token", "-t", env_var="GITLAB_API_TOKEN", required=True)
    parser.add_argument("--filter", "-f", dest="project_filter_expr", default=None)
    args = parser.parse_args()
    _main_inner(args)

if __name__ == "__main__":
    _main()
