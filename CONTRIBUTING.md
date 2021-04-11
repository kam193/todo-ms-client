# Contributing

|                      |                                                                                   |
| -------------------- | --------------------------------------------------------------------------------- |
| **Issue tracker**    | Github issues and Github Project or repository page                               |
| **Branching model**  | Current version is always on `master`. Create new branch from and new PR to them. |
| **Release model**    | Bump version and create Github Release with tag `vx.x.x`                          |
| **Pull requests**    | CI checks passed and maintainer's approval are required to merge.                 |
| **Changelog**        | Keep CHANGELOG.md up-to-date. Review it before release.                           |
| **Style guide**      | We use `flake8`, `black` and obligatory `isort`.                                  |
| **Pip requirements** | We use [pip-tools](https://github.com/jazzband/pip-tools) to manage requirements  |
| **Python**           | Supported Python is 3.7+                                                          |

## Running tests locally

`tox` is configured to run unit tests as well as code style checks. Install `tox`:

    pip install tox

An then run one of the following tox environments: `py37` (tests on Python 3.7), `py38` (Python 3.8) or `lint` (style checks).
For example:

    tox -e py37

## Building docs

Docs are generated using Sphinx. You can build it using tox:

    tox -e docs

## Pre-commi hook

Keeping code style is supported by pre-commit hooks. It's recommended to use them.
To configure, install requirements from `requirements-dev.txt` and run:

    pre-commit install
