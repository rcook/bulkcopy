# repotool by Richard Cook

[![View on PyPI](https://img.shields.io/pypi/v/repotool.svg)](https://pypi.python.org/pypi/repotool)

Python wrappers around GitHub, GitLab and Bitbucket REST APIs

## Clone repository

```
git clone https://github.com/rcook/repotool.git
```

## Set up Python virtual environment

```
script/virtualenv
```

## Dev-install main script into virtual environment

```
script\env pip install -e .
```

This will allow edits to the scripts to be picked up automatically

## Run main script in virtual environment

```
script/env repotool --version
```

## Build package

```
script/env python setup.py build
```

## Test package

```
script/env python setup.py test
```

## Upload package

```
script/env python setup.py sdist upload
```

## Install package into global site packages

```
python setup.py install --record files.txt
```

Note that this calls the `python` global Python instead of the Python in the project's virtual environment.

## Notes

Various package properties are defined in `repotool/__init__py`:

* `__project_name__`
* `__version__`
* `__description__`

When publishing a new build of the package, ensure that `__version__` is incremented as appropriate.

## User-level installation

```
pip install --user repotool
```

This will perform a user-level installation of the package. The scripts will be placed at:

* Windows: `%APPDATA%\Python\Scripts`
* Linux/macOS: `$HOME/.local/bin`

## Global installation

```
pip install repotool
```

This will perform a global installation of the package and should add the script to `PATH`.

## Licence

Released under [MIT License][licence]

[licence]: LICENSE
