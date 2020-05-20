#! /usr/bin/env python

# this is a script we run in tox when generating the docs.
# it saves a copy of the openapi / swagger spec so we can use
# it in sphinx with the sphinxcontrib-openapi plugin

import os
import json
from importlib import import_module

from fasjson.web.app import create_app


directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "_api")


def _generate_spec(api_version):
    api_module = import_module(f"fasjson.web.apis.v{api_version}")
    output_path = os.path.join(directory, f"api_v{api_version}.json")
    with open(output_path, "w") as f:
        f.write(json.dumps(api_module.api.__schema__))


if __name__ == "__main__":
    app = create_app({"TESTING": True})
    with app.test_request_context():
        _generate_spec(1)
