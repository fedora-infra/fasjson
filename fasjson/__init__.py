# Set the version
try:
    import importlib.metadata

    __version__ = importlib.metadata.version("fasjson")
except ImportError:
    import pkg_resources

    __version__ = pkg_resources.get_distribution("fasjson").version
