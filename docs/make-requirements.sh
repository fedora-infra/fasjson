#!/bin/sh

set -e

here=`dirname $0`
output="${here}/requirements.txt"

set -x

poetry export -f requirements.txt --without-hashes -o "${output}"

# Remove some modules because ReadTheDocs does not install C-based modules
for exclude in gssapi python-ldap requests-kerberos pykerberos winkerberos; do
    sed -i -e "/^${exclude}==/d" "${output}"
done

# Add toml to parse the version in conf.py
echo toml >> "${output}"
