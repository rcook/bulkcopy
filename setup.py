#!/usr/bin/env python
##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

import os
import re

from setuptools import setup

_PROJECT_NAME = "repotool"

def _read_properties(project_name):
    init_path = os.path.abspath(os.path.join(project_name, "__init__.py"))
    regex = re.compile("^\\s*__(?P<key>.*)__\\s*=\\s*\"(?P<value>.*)\"\\s*$")
    with open(init_path, "rt") as f:
        props = {}
        for line in f.readlines():
            m = regex.match(line)
            if m is not None:
                props[m.group("key")] = m.group("value")

    return props

_PROPERTIES = _read_properties(_PROJECT_NAME)
project_name = _PROPERTIES["project_name"]
version = _PROPERTIES["version"]
description = _PROPERTIES["description"]

setup(
    name=project_name,
    version=version,
    description=description,
    setup_requires=["setuptools-markdown"],
    long_description_markdown_filename="README.md",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
    ],
    url="https://github.com/rcook/repotool",
    author="Richard Cook",
    author_email="rcook@rcook.org",
    license="MIT",
    packages=[project_name],
    install_requires=[
        "pyprelude",
        "pysimplevcs",
        "pyyaml",
        "requests_oauthlib"
    ],
    entry_points={
        "console_scripts": [
            "{0} = {0}.__main__:_main".format(project_name)
        ]
    },
    include_package_data=True,
    test_suite="{}.tests.suite".format(project_name),
    zip_safe=False)
