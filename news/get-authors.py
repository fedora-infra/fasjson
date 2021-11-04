#!/usr/bin/env python3

"""

This script browses through git commit history (starting at latest tag), collects all authors of
commits and creates fragment for `towncrier`_ tool.

It's meant to be run during the release process, before generating the release notes.

Example::

    $ python get_authors.py

.. _towncrier: https://github.com/hawkowl/towncrier/

Authors:
    Aurelien Bompard
    Michal Konecny
"""

import os
import sys
from subprocess import check_output


EXCLUDE = ["dependabot[bot]", "dependabot-preview[bot]", "Weblate (bot)"]

try:
    target = sys.argv[1].strip()
except IndexError:
    target = "HEAD"

last_tag = check_output(
    "git tag | sort -n | tail -n 1", shell=True, universal_newlines=True
)
authors = {}
log_range = last_tag.strip() + ".." + target
output = check_output(
    ["git", "log", log_range, "--format=%ae\t%an"], universal_newlines=True
)
for line in output.splitlines():
    email, fullname = line.split("\t")
    email = email.split("@")[0].replace(".", "")
    if email in authors:
        continue
    authors[email] = fullname

for nick, fullname in authors.items():
    if fullname in EXCLUDE:
        continue
    filename = "{}.author".format(nick)
    if os.path.exists(filename):
        continue
    print(f"Adding author {fullname} ({nick})")
    with open(filename, "w") as f:
        f.write(fullname)
        f.write("\n")
