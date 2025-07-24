# Configuration file for the Sphinx documentation builder. This file only contains a
# selection of the most common options. For a full list see the documentation:
# http://www.sphinx-doc.org/en/master/config.
# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory, add
# these directories to sys.path here. If the directory is relative to the documentation
# root, use os.path.abspath to make it absolute, like shown here.
import pathlib
import sys
from datetime import datetime

sys.path.insert(0, str(pathlib.Path("../src").resolve()))

# -- Project information -----------------------------------------------------

project = "GETTSIM"
copyright = f"2019-{datetime.today().year}, GETTSIM team"  # noqa: A001, DTZ002
author = "GETTSIM team"
release = "0.7.0"
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be extensions coming
# with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "nbsphinx",
    "sphinx_automodapi.automodapi",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "myst_parser",
]

# The master toctree document.
master_doc = "index"

# Add any paths that contain templates here, relative to this directory.

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "restructuredtext",
    ".md": "markdown",
}

# List of patterns, relative to source directory, that match files and directories to
# ignore when looking for source files. This pattern also affects html_static_path and
# html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Extensions configuration ------------------------------------------------

add_module_names = False

autodoc_default_options = {
    "members": True,
    "private-members": True,
    "special-members": True,
    "undoc-members": True,
}
autodoc_mock_imports = [
    "networkx",
    "numpy",
    "numpy_groupies",
    "numba",
    "weave",
    "pandas",
    "pygments",
    "pytest",
    "yaml",
]

extlinks = {
    "ghuser": ("https://github.com/%s", "@%s"),
    "gh": (
        "https://github.com/ttsim-dev/gettsim/pull/%s",
        "#%s",
    ),
}

intersphinx_mapping = {
    "numpy": ("https://docs.scipy.org/doc/numpy", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "python": ("https://docs.python.org/", None),
}

myst_heading_anchors = 3

numpydoc_show_class_members = False

todo_include_todos = True
todo_emit_warnings = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for a list of
# builtin themes.
html_theme = "pydata_sphinx_theme"
html_logo = "_static/images/gettsim_logo.svg"

html_theme_options = {
    "github_url": "https://github.com/ttsim-dev/gettsim",
}

# Add any paths that contain custom static files (such as style sheets) here, relative
# to this directory. They are copied after the builtin static files, so a file named
# "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = ["css/custom.css"]

html_sidebars = {
    "**": [
        "relations.html",  # needs 'show_related': True theme option to display
        "searchbox.html",
    ],
}

# Napoleon settings
napoleon_use_rtype = False
