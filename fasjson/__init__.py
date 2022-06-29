try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version


# Set the version
try:
    __version__ = version("fasjson")
except PackageNotFoundError:
    import os

    import toml

    pyproject = toml.load(
        os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
    )
    __version__ = pyproject["tool"]["poetry"]["version"]
