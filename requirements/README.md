# Requirements files

For the sake of reproducibility, the development-related requirements are managed using
pip-tools. The main library requirements are simple requirements.txt file, defining only
the direct dependencies.

## Versioning direct dependencies

For direct dependencies, the minimum version is specified in the requirements.txt file.
During CI build, the tests are run against the minimum, the latest and pinned (dev)
versions. Tox commands:

-   `tox -e py39` - run tests against the pinned dependencies
-   `tox -e minimum` - run tests against the minimum dependencies
-   `tox -e latest` - run tests against the latest dependencies

The test, docs and dev-only dependencies are not intentionally tested against different
versions. For the main dependencies, we want to ensure that the library is still working.
