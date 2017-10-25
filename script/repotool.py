#!/usr/bin/env python
##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from __future__ import print_function
import configargparse
import getpass
import itertools
import os
import re

from pyprelude.file_system import make_path

from repotoollib.bitbucket import Bitbucket
from repotoollib.github import GitHub
from repotoollib.gitlab import GitLab

_PROJECT_KEY_FUNC = lambda p: (p.name, p.scm)

def _filter_projects(filter_expr, projects):
    if filter_expr is None:
        return projects
    else:
        regex = re.compile(filter_expr)
        return filter(lambda p: regex.match(p.name) is not None, projects)

def _get_project_providers(args):
    providers = []

    if args.bitbucket_api_key is not None and args.bitbucket_api_secret is not None:
        providers.append(Bitbucket(args.config_dir, args.user, args.bitbucket_api_key, args.bitbucket_api_secret))

    if args.gitlab_api_token is not None:
        providers.append(GitLab(args.config_dir, args.user, args.gitlab_api_token))

    if args.github_api_token:
        providers.append(GitHub(args.config_dir, args.user, args.github_api_token))

    return providers

def _show_providers(providers):
    print("Providers: {}".format("(none)" if len(providers) == 0 else ", ".join(map(lambda p: p.provider_name, providers))))

def _get_projects(providers):
    all_projects = []
    for provider in providers:
        all_projects.extend(provider.get_projects())

    projects = sorted(all_projects, key=_PROJECT_KEY_FUNC)
    return projects

def _do_list(args):
    providers = _get_project_providers(args)
    _show_providers(providers)

    all_projects = _get_projects(providers)
    projects = _filter_projects(args.project_filter_expr, all_projects)
    for project in projects:
        print("{} [{}] {}".format(project.name, project.id, project.clone_link("ssh")))

    print("Total: {} projects".format(len(projects)))

def _do_dupes(args):
    providers = _get_project_providers(args)
    _show_providers(providers)

    projects = _get_projects(providers)

    groups = itertools.groupby(projects, _PROJECT_KEY_FUNC)
    group_count = 0
    for key, group_iter in groups:
        group = list(group_iter)
        if len(group) > 1:
            group_count += 1
            project_name, _ = key
            print("{}:".format(project_name))
            for project in group:
                print("  {} [{}] {}".format(project.provider.provider_name, project.id, project.clone_link("ssh")))

    print("Total: {} groups of possibly duplicate projects".format(group_count))

def _do_info(args):
    providers = _get_project_providers(args)
    provider_map = { p.provider_name: p for p in providers }

    provider = provider_map.get(args.provider_name)
    project = provider.get_project(args.project_name)

    table = project.make_table()
    print()
    print("PROJECT INFORMATION\n")
    table.show()
    print()

def _confirm_delete(project):
    table = project.make_table()
    print()
    print("PROJECT INFORMATION\n")
    table.show()
    print()
    result = raw_input("Do you really want to delete project \"{}\" from {}? [Enter \"YES\" to confirm] ".format(project.name, project.provider.provider_name))
    if result != "YES":
        return False

    result = raw_input("Really? [Enter \"REALLY\" to confirm] ")
    if result != "REALLY":
        return False

    return True

def _do_delete(args):
    providers = _get_project_providers(args)
    provider_map = { p.provider_name: p for p in providers }

    provider = provider_map.get(args.provider_name)
    project = provider.get_project(args.project_name)

    confirmation_token = _confirm_delete(project)
    if not confirmation_token:
        print("Aborted.")
        return

    project.delete(confirmation_token=confirmation_token)
    print("Project {} deleted.".format(project.name))

def _main():
    default_config_dir = make_path(os.path.expanduser("~/.repotool"))
    default_config_path = make_path(default_config_dir, "config.yaml")
    parser = configargparse.ArgumentParser(default_config_files=[default_config_path])
    parser.add_argument("--config-dir", "-c", default=default_config_dir)
    parser.add_argument("--user", "-u", default=getpass.getuser())
    parser.add_argument("--bitbucket-api-key", "-k", env_var="BITBUCKET_API_KEY", required=False, is_config_file=True)
    parser.add_argument("--bitbucket-api-secret", "-s", env_var="BITBUCKET_API_SECRET", required=False, is_config_file=True)
    parser.add_argument("--gitlab-api-token", "-t", env_var="GITLAB_API_TOKEN", required=False, is_config_file=True)
    parser.add_argument("--github-api-token", "-g", env_var="GITHUB_API_TOKEN", required=False, is_config_file=True)

    subparsers = parser.add_subparsers(help="subcommand help")

    list_parser = subparsers.add_parser("list", help="List projects")
    list_parser.set_defaults(func=_do_list)
    list_parser.add_argument("--filter", "-f", dest="project_filter_expr", default=None)

    dupes_parser = subparsers.add_parser("dupes", help="Show possible duplicate projects")
    dupes_parser.set_defaults(func=_do_dupes)

    info_parser = subparsers.add_parser("info", help="Show information about project")
    info_parser.set_defaults(func=_do_info)
    info_parser.add_argument("provider_name", help="Name of project provider")
    info_parser.add_argument("project_name", help="Project name")

    delete_parser = subparsers.add_parser("delete", help="Delete project")
    delete_parser.set_defaults(func=_do_delete)
    delete_parser.add_argument("provider_name", help="Name of project provider")
    delete_parser.add_argument("project_name", help="Project name")

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    _main()
