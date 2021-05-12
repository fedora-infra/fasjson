#!/bin/sh

set -e

here=$(realpath $(dirname $0))
output="${here}/requirements.txt"
excluded="gssapi python-ldap requests-kerberos pykerberos winkerberos flask-mod-auth-gssapi"

set -x

poetry export -f requirements.txt --without-hashes -o "${output}"

# Remove some modules because ReadTheDocs does not install C-based modules
for exclude in ${excluded}; do
    sed -i -e "/^${exclude}==/d" "${output}"
done

# Add toml to parse the version in conf.py
echo toml >> "${output}"
# Add Sphinx dependencies
echo -e "sphinx\nsphinxcontrib-napoleon\nsphinxcontrib-openapi" >> "${output}"
