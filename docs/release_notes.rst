=============
Release notes
=============

.. towncrier release notes start

v1.2.0
======

Released on 2021-11-05.

Features
^^^^^^^^

* Field mask support: request more or less object attributes with a HTTP header
  (:issue:`144`).
* Expose users' SSH keys (:issue:`186`).
* Add some more user fields: ``github_username``, ``gitlab_username``,
  ``website``, and ``pronouns`` (:issue:`213`).

Bug Fixes
^^^^^^^^^

* Display indirect groups as well (:issue:`188`).
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
