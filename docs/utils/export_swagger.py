#! /usr/bin/env python

# this is a script we run in tox when generating the docs.
# it saves a copy of the openapi / swagger spec so we can use
# it in sphinx with the sphinxcontrib-openapi plugin

import os
import json

from fasjson.web.app import create_app

directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
app = create_app()

app.testing = True
app.config["FASJSON_IPA_CONFIG_PATH"] = f"{directory}/utils/ipa.default.conf"
app.config["FASJSON_IPA_CA_CERT_PATH"] = f"{directory}/utils/ipa.ca.crt"
app.config["TESTING"] = True

client = app.test_client()

page = client.get("/specs/v1.json")
f = open(f"{directory}/_api/api_v1.json", "w")
f.write(json.dumps(page.get_json(), indent=4))
f.close()

# if we go to v2, we will need to generate it here something like this

# page = client.get("/specs/v2.json")
# f = open(f"{directory}/_api/api_v2.json", "w")
# f.write(json.dumps(page.get_json(), indent=4))
# f.close()
