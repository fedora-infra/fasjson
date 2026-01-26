from importlib.metadata import PackageNotFoundError, version

# Set the version
try:
    __version__ = version("fasjson")
except PackageNotFoundError:
    import os

    import tomllib

    with open(
        os.path.join(os.path.dirname(__file__), "..", "pyproject.toml"), "rb"
    ) as pyproject_fh:
        pyproject = tomllib.load(pyproject_fh)
    __version__ = pyproject["project"]["version"]
