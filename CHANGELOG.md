# Changelog

Changes in a project.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2022-12-16

### Added

- Added comparing resources using their ID
- Added default values for fields in Task
- Objects are refreshed after creating or updating
- Added `refresh` method to reload objects
- Added helper methods for client and resources to handle sub-objects
- Added support for subtasks

- [dev] Added CodeQL check to the CI
- [dev] Added pre-commit hooks to check formatting
- [dev] Added optional functional tests to validate library against real server
- [dev] Added sorting methods using `ssort`
- [dev] Added experimental strict typing

### Changed

- Redesigned way how fields of resources are defined
- Declared only minimal direct dependencies for the library, CI configured to run tests
  against minimal and newest dependencies.
- Fields like creation date are now read-only.
- The task's body supports now both types
- Fields missed previously are added

### Removed

- Removed support for Python older than 3.9

### Fixed

- Fixed listing task lists due to wrong API responses on simple request

### Known issue

- Example file may be outdated, use `tests/functional/test_crud.py` as reference
- Documentation is outdated, use tests as reference
- Type hints for fields may create confusions

## [0.0.4]

### Added

- Basic docs with library interface reference

### Changed

- Switching to the new ToDo API

### Removed

- `Attachment`, `Sensitivity` as not supported by the new API

## [0.0.3] - 2020-06-20

### Added

- Mark Task as complete
- Create TaskList and Task
- List attachments in task
- Filtering TaskList on when listed
- Simple support for filtering operators

### Fixed

- Support URLs with or without `/` at the begin or end

## [0.0.2] - 2020-05-02

### Added

- `WebBrowserProvider` can display custom messages
- Support deleting Task and TaskList
- Support updating Task and TaskList
- Converting resource to dict

### Changed

- Resources have explicitly init methods
- Package metadata updated

### Fixed

- Converting dates when aren't present in data dict
- Type annotations
- Package readme in PyPI

## [0.0.1] - 2020-05-21

### Added

- Login manually with personal MS Account
- Read task's lists
- Read task
- Initial Readme, Contributing and code-style tools
- Package building
- CI automation
