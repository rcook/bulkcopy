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

from repotool import __description__, __project_name__, __version__
from repotool.bitbucket import Bitbucket
from repotool.github import GitHub
from repotool.gitlab import GitLab

_PROJECT_KEY_FUNC = lambda p: (p.name, p.scm)
_PROVIDER_KEY_FUNC = lambda p: p.name
_PROVIDER_CLASSES = {
    "bitbucket": Bitbucket,
    "github": GitHub,
    "gitlab": GitLab
}

def _read_config(config_path):
    if os.path.isfile(config_path):
        with open(config_path, "rt") as f:
            return yaml.load(f)
    else:
        config_obj = {}
        provider_config_obj = []
        config_obj["providers"] = provider_config_obj

        for provider_type_name in sorted(_PROVIDER_CLASSES.keys()):
            cls = _PROVIDER_CLASSES[provider_type_name]
            provider_config_obj.append(cls.make_sample_config())

        with open(config_path, "wt") as f:
            f.write(yaml.dump(config_obj))

        return config_obj

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
    if args.provider_names is not None:
        providers = []
        for provider_name in set(args.provider_names):
            providers.append(provider_map[provider_name])
    else:
        providers = provider_map.values()

    providers = sorted(providers, key=_PROVIDER_KEY_FUNC)

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

def _do_create(args, provider_map):
    provider = provider_map.get(args.provider_name)
    provider.create_project(args.project_name, is_private=True)
    print("Project {} created.".format(args.project_name))

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
    providers = sorted(provider_map.values(), key=_PROVIDER_KEY_FUNC)

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

    config_obj = _read_config(default_config_path)

    provider_map = {}
    for provider_config_obj in config_obj.get("providers", []):
        name = provider_config_obj["name"]
        type = provider_config_obj["type"]
        cls = _PROVIDER_CLASSES[type]
        provider_map[name] = cls.parse_config(default_config_dir, default_user, provider_config_obj)

    parser = argparse.ArgumentParser(description="Repository tool")
    parser.add_argument("--version", action="version", version="{} version {}".format(__project_name__, __version__))

    subparsers = parser.add_subparsers(help="subcommand help")

    list_parser = subparsers.add_parser("list", help="List projects")
    list_parser.set_defaults(func=_do_list)
    list_parser.add_argument(
        "--filter",
        "-f",
        dest="project_filter_expr",
        default=None)
    list_parser.add_argument(
        "--provider",
        "-p",
        nargs="+",
        dest="provider_names",
        default=None,
        choices=sorted(provider_map.keys()))
    list_parser.add_argument(
        "--include-archived",
        "-a",
        dest="include_archived",
        action="store_true",
        default=False)

    info_parser = subparsers.add_parser("info", help="Show information about project")
    info_parser.set_defaults(func=_do_info)
    info_parser.add_argument(
        "provider_name",
        metavar="PROVIDERNAME",
        help="Name of project provider")
    info_parser.add_argument(
        "project_name",
        metavar="PROJECTNAME",
        help="Project name")

    create_parser = subparsers.add_parser("create", help="Create project")
    create_parser.set_defaults(func=_do_create)
    create_parser.add_argument(
        "provider_name",
        metavar="PROVIDERNAME",
        help="Name of project provider")
    create_parser.add_argument(
        "project_name",
        metavar="PROJECTNAME",
        help="Project name")

    delete_parser = subparsers.add_parser("delete", help="Delete project")
    delete_parser.set_defaults(func=_do_delete)
    delete_parser.add_argument(
        "provider_name",
        metavar="PROVIDERNAME",
        help="Name of project provider")
    delete_parser.add_argument(
        "project_name",
        metavar="PROJECTNAME",
        help="Project name")

    archive_parser = subparsers.add_parser("archive", help="Archive project")
    archive_parser.set_defaults(func=_do_archive)
    archive_parser.add_argument(
        "provider_name",
        metavar="PROVIDERNAME",
        help="Name of project provider")
    archive_parser.add_argument(
        "project_name",
        metavar="PROJECTNAME",
        help="Project name")

    dupes_parser = subparsers.add_parser("dupes", help="Show possible duplicate projects")
    dupes_parser.set_defaults(func=_do_dupes)

    args = parser.parse_args()
    args.func(args, provider_map)

if __name__ == "__main__":
    _main()
