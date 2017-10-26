#!/usr/bin/env python
##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from __future__ import print_function
import argparse
import getpass
import itertools
import os
import re
import yaml

from pyprelude.file_system import make_path

from repotoollib.bitbucket import Bitbucket
from repotoollib.github import GitHub
from repotoollib.gitlab import GitLab

_PROJECT_KEY_FUNC = lambda p: (p.name, p.scm)
_PROVIDER_KEY_FUNC = lambda p: p.name
_PROVIDER_CLASSES = {
    "bitbucket": Bitbucket,
    "github": GitHub,
    "gitlab": GitLab
}

def _filter_projects(filter_expr, projects):
    if filter_expr is None:
        return projects
    else:
        regex = re.compile(filter_expr)
        return filter(lambda p: regex.match(p.name) is not None, projects)

def _show_providers(providers):
    print("Providers: {}".format("(none)" if len(providers) == 0 else ", ".join(
        map(lambda p: "{} ({})".format(p.name, p.provider_name), providers))))

def _get_projects(providers, include_archived=False):
    all_projects = []
    for provider in providers:
        all_projects.extend(provider.get_projects(include_archived=include_archived))

    projects = sorted(all_projects, key=_PROJECT_KEY_FUNC)
    return projects

def _sorted_providers(provider_map):
    return sorted(provider_map.values(), key=_PROVIDER_KEY_FUNC)

def _confirm_operation(project, op):
    table = project.make_table()
    print()
    print("PROJECT INFORMATION\n")
    table.show()
    print()
    result = raw_input("Do you really want to {} project \"{}\" from {}? [Enter \"YES\" to confirm] ".format(
        op,
        project.name,
        project.provider.provider_name))
    if result != "YES":
        return False

    result = raw_input("Really? [Enter \"REALLY\" to confirm] ")
    if result != "REALLY":
        return False

    return True

def _do_list(args, provider_map):
    if args.provider_name:
        providers = [provider_map[args.provider_name]]
    else:
        providers = _sorted_providers(provider_map)

    _show_providers(providers)

    all_projects = _get_projects(providers, include_archived=args.include_archived)
    projects = _filter_projects(args.project_filter_expr, all_projects)
    for project in projects:
        print("{} [{}] {}".format(project.name, project.id, project.clone_link("ssh")))

    print("Total: {} projects".format(len(projects)))

def _do_info(args, provider_map):
    provider = provider_map.get(args.provider_name)
    project = provider.get_project(args.project_name)
    table = project.make_table()
    print()
    print("PROJECT INFORMATION\n")
    table.show()
    print()

def _do_delete(args, provider_map):
    provider = provider_map.get(args.provider_name)
    project = provider.get_project(args.project_name)

    confirmation_token = _confirm_operation(project, "delete")
    if not confirmation_token:
        print("Aborted.")
        return

    project.delete(confirmation_token=confirmation_token)
    print("Project {} deleted.".format(project.name))

def _do_archive(args, provider_map):
    provider = provider_map.get(args.provider_name)
    project = provider.get_project(args.project_name)

    confirmation_token = _confirm_operation(project, "archive")
    if not confirmation_token:
        print("Aborted.")
        return

    project.archive(confirmation_token=confirmation_token)
    print("Project {} archived.".format(project.name))

def _do_dupes(args, provider_map):
    providers = _sorted_providers(provider_map)

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

def _main():
    default_config_dir = make_path(os.path.expanduser("~/.repotool"))
    default_config_path = make_path(default_config_dir, "config.yaml")
    default_user = getpass.getuser()

    with open(default_config_path, "rt") as f:
        config_obj = yaml.load(f)

    provider_map = {}
    for provider_config_obj in config_obj.get("providers", []):
        name = provider_config_obj["name"]
        type = provider_config_obj["type"]
        cls = _PROVIDER_CLASSES[type]
        provider_map[name] = cls.parse_config(default_config_dir, default_user, provider_config_obj)

    parser = argparse.ArgumentParser(description="Repository tool")

    subparsers = parser.add_subparsers(help="subcommand help")

    list_parser = subparsers.add_parser("list", help="List projects")
    list_parser.set_defaults(func=_do_list)
    list_parser.add_argument("--filter", "-f", dest="project_filter_expr", default=None)
    list_parser.add_argument(
        "--provider",
        "-p",
        dest="provider_name",
        default=None,
        choices=sorted(provider_map.keys()))
    list_parser.add_argument("--include-archived", "-a", dest="include_archived", action="store_true", default=False)

    info_parser = subparsers.add_parser("info", help="Show information about project")
    info_parser.set_defaults(func=_do_info)
    info_parser.add_argument("provider_name", help="Name of project provider")
    info_parser.add_argument("project_name", help="Project name")

    delete_parser = subparsers.add_parser("delete", help="Delete project")
    delete_parser.set_defaults(func=_do_delete)
    delete_parser.add_argument("provider_name", help="Name of project provider")
    delete_parser.add_argument("project_name", help="Project name")

    archive_parser = subparsers.add_parser("archive", help="Archive project")
    archive_parser.set_defaults(func=_do_archive)
    archive_parser.add_argument("provider_name", help="Name of project provider")
    archive_parser.add_argument("project_name", help="Project name")

    dupes_parser = subparsers.add_parser("dupes", help="Show possible duplicate projects")
    dupes_parser.set_defaults(func=_do_dupes)

    args = parser.parse_args()
    args.func(args, provider_map)

if __name__ == "__main__":
    _main()
