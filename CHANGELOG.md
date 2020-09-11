# Changelog

Changes in a project.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
