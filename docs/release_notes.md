# Release notes

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This project uses [*towncrier*](https://towncrier.readthedocs.io/) and the changes for the upcoming release can be found in [the `news` directory](https://github.com/fedora-infra/fasjson/tree/develop/news/).

<!-- towncrier release notes start -->

## v1.7.0

Released on 2025-11-14.

### Features

- Support presence match in the search endpoint. For example, use `ircnick=*` to get users who have defined an IRC nick. (#presence-match)
- Add the possibility to search users by GitLab usernames (#645)
- Make `rssurl` and `website` multivalued fields (#719)
- Add a multivalued `group` search term for users, to select only those in the specified groups
- Allow searching for RSS URLs and websites

### Bug Fixes

- Fixup `get_user_groups()` after 6698d1c8

### Development Improvements

- Move the tests out of the main python package (#734)
- Make the Vagrant VM use Tinystage instead of its own instance of FreeIPA
- Switch to ruff instead of flake8+isort+bandit+pyupgrade

### Other Changes

- Note that the `email__exact` search term is deprecated since email searches are never substring-based, so just use the `email` term (#6698d1c)

### Contributors

Many thanks to the contributors of bug reports, pull requests, and pull request
reviews for this release:

- Aurélien Bompard
- Pedro Moura
- Ryan Lerch

## v1.6.0

Released on 2023-09-21.
This is a feature release that adds the `rssurl` field.

### Features

- Add the rssurl field (#558).

### Bug Fixes

- Don't crash when a user has no groups (#399).
- Don't crash when group is a sponsor of a group (#444).

### Contributors

Many thanks to the contributors of bug reports, pull requests, and pull request
reviews for this release:

- Aurélien Bompard
- Lenka Segura
- Pedro Moura


## v1.5.0

Released on 2022-08-29.
This is a feature release that adds `rhbzemail` field searching.

### Features

- Allow search by rhbzemail field (#370).

### Contributors

Many thanks to the contributors of bug reports, pull requests, and pull request
reviews for this release:

- Aurélien Bompard
- Michal Konečný


## v1.4.0

Released on 2022-06-30.
This is a feature release that adds exact value search and GitHub username
search.

### Features

- Allow searching for the exact value (#266).
- Add a way to search users with GitHub usernames (#348).

The `creation_before` search term has been renamed to `creation__before`
for coherence. This is technically a backwards incompatible change, but the
term has only been added a few days ago and not advertised, so I'm fairly
confident noone uses it yet.


## v1.3.0

This is a feature release that adds user search terms.

### Features

- Add the `human_name` and `creation_before` search terms for users (#343).

### Development Improvements

- Upgrade the Vagrant VM to F36 (#343).

### Contributors

Many thanks to the contributors of bug reports, pull requests, and pull request
reviews for this release:

- Aurélien Bompard
- Stephen Coady


## v1.2.1

Released on 2022-05-16.

### Development Improvements

- Allow users to set bugzilla email using fasRHBZEmail attribute (#288).
- Update dependencies
- Drop support for Python < 3.9

### Contributors

Many thanks to the contributors of bug reports, pull requests, and pull request
reviews for this release:

- Aurélien Bompard
- Pedro Moura
- Stephen Coady


## v1.2.0

Released on 2021-11-05.

### Features

- Add some more user fields: `github_username`, `gitlab_username`,
  `website`, and `pronouns` (#213).

### Bug Fixes

- Respect user's privacy setting on the search endpoint (#257).


## v1.1.0

This is a feature release.

### Features

- Field mask support: request more or less object attributes with a HTTP header
  (#144).
- Expose users' SSH keys (#186).

### Bug Fixes

- Display indirect groups as well (#188).

### Contributors

Many thanks to the contributors of bug reports, pull requests, and pull request
reviews for this release:

- Aurélien Bompard


## v1.0.0

This is a the first stable release, as deployed in production in the Fedora
infrastructure on March 24th 2021.

### Contributors

Many thanks to the contributors of bug reports, pull requests, and pull request
reviews for this release:

- Aurélien Bompard
- Stephen Coady
