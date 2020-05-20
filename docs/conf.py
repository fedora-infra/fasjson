# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import fasjson  # NOQA


# -- Project information -----------------------------------------------------

project = "fasjson"
copyright = "2020, Red Hat, Inc"
author = "Fedora Infrastructure"

# The short X.Y version
version = ".".join(fasjson.__version__.split(".")[:2])

# The full version, including alpha/beta/rc tags
release = fasjson.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinxcontrib.openapi",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Explcitely set the master doc
# https://github.com/readthedocs/readthedocs.org/issues/2569
master_doc = "index"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"


# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "github_user": "fedora-infra",
    "github_repo": "fasjson",
    "page_width": "1040px",
    "show_related": True,
    "sidebar_collapse": True,
    "caption_font_size": "140%",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

extlinks = {
    "commit": ("https://github.com/fedora-infra/fasjson/commit/%s", ""),
    "issue": ("https://github.com/fedora-infra/fasjson/issues/%s", "#"),
    "pr": ("https://github.com/fedora-infra/fasjson/pull/%s", "PR#"),
}
