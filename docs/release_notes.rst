=============
Release notes
=============

.. towncrier release notes start

v1.5.0
======

Released on 2022-08-29.
This is a feature release that adds rhbzemail field searching.

Features
^^^^^^^^

* Allow search by rhbzemail field (:issue:`370`).

Contributors
^^^^^^^^^^^^

Many thanks to the contributors of bug reports, pull requests, and pull request
reviews for this release:

* Aurélien Bompard
* Michal Konečný


v1.4.0
======

Released on 2022-06-30.
This is a feature release that adds exact value search and GitHub username
search.


Features
^^^^^^^^

* Allow searching for the exact value (:issue:`266`).
* Add a way to search users with GitHub usernames (:issue:`348`).

The ``creation_before`` search term has been renamed to ``creation__before``
for coherence. This is technically a backwards incompatible change, but the
term has only been added a few days ago and not advertised, so I'm fairly
confident noone uses it yet.


v1.3.0
======

This is a feature release that adds user search terms.

Features
^^^^^^^^

* Add the ``human_name`` and ``creation_before`` search terms for users
  (:pr:`343`).

Development Improvements
^^^^^^^^^^^^^^^^^^^^^^^^

* Upgrade the Vagrant VM to F36 (:pr:`343`).

Contributors
^^^^^^^^^^^^

Many thanks to the contributors of bug reports, pull requests, and pull request
reviews for this release:

* Aurélien Bompard
* Stephen Coady


v1.2.1
======

Released on 2022-05-16.

Development Improvements
^^^^^^^^^^^^^^^^^^^^^^^^

* Allow users to set bugzilla email using fasRHBZEmail attribute
  (:issue:`288`).
* Update dependencies
* Drop support for Python < 3.9

Contributors
^^^^^^^^^^^^

Many thanks to the contributors of bug reports, pull requests, and pull request
reviews for this release:

* Aurélien Bompard
* Pedro Moura
* Stephen Coady


v1.2.0
======

Released on 2021-11-05.

Features
^^^^^^^^

* Add some more user fields: ``github_username``, ``gitlab_username``,
  ``website``, and ``pronouns`` (:issue:`213`).

Bug Fixes
^^^^^^^^^

* Respect user's privacy setting on the search endpoint (:issue:`257`).


v1.1.0
======
This is a feature release.


Features
^^^^^^^^

* Field mask support: request more or less object attributes with a HTTP header
  (:issue:`144`).
* Expose users' SSH keys (:issue:`186`).

Bug Fixes
^^^^^^^^^

* Display indirect groups as well (:issue:`188`).

Contributors
^^^^^^^^^^^^

Many thanks to the contributors of bug reports, pull requests, and pull request
reviews for this release:

* Aurélien Bompard


v1.0.0
======

This is a the first stable release, as deployed in production in the Fedora infrastructure
on March 24th 2021.


Contributors
^^^^^^^^^^^^

Many thanks to the contributors of bug reports, pull requests, and pull request
reviews for this release:

* Aurélien Bompard
* Stephen Coady
