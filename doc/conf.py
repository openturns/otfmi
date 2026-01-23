import sys
import os
import subprocess

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = "otfmi"
copyright = "2017-2026 EDF-Phimeca"
author = "Sylvain Girard"

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath("../"))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx_gallery.gen_gallery",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx.ext.imgmath"
]

# paths to example scripts and generated doc by sphinx
sphinx_gallery_conf = {
    "examples_dirs": [
        "../doc_example",
    ],

    "gallery_dirs": [
        "auto_example",
    ],
    # only python files beginning by xxx will be executed
    "filename_pattern": "/ex_",
    "example_extensions": {".py"},
    "show_signature": False,
    "download_all_examples": False,
}

# -- Options for internationalization ----------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-internationalization

language = "en"

#

autodoc_default_options = {"members": None, "inherited-members": None}

intersphinx_mapping = {
    "openturns": ("http://openturns.github.io/openturns/latest", None)
}
autosummary_generate = True

numpydoc_show_class_members = True
numpydoc_class_members_toctree = False

# -- Options for imgmath ----------------------------------------
imgmath_latex_preamble = r"\usepackage{{{0}math_notations}}".format(
    os.path.dirname(__file__) + os.sep
)
imgmath_use_preview = True
if (
    subprocess.call(
        "dvisvgm -V", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    == 0
):
    imgmath_image_format = "svg"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = {'.rst': 'restructuredtext'}

# The master toctree document.
master_doc = "index"


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []


# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "friendly"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = "OTFMI"
html_theme = "breeze"
# html_sidebars = {
#     '**': [
#         # 'about.html',
#         'navigation.html',
#         'relations.html',
#         'searchbox.html',
#         'donate.html',
#     ]
# }

html_theme_options = {"sidebar_secondary": ["sidebar-toc.html"]}
html_show_sourcelink = False

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = "_static/Icon.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["custom_download_button.css", "hide_links.css"]
html_js_files = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = "%b %d, %Y"

# Output file base name for HTML help builder.
htmlhelp_basename = "otfmidoc"

version = os.environ.get("READTHEDOCS_VERSION", "latest")

html_context = {
    "github_user": "openturns",
    "github_repo": "otfmi",
    "github_version": "main",
    "doc_path": "docs",
    "current_version": version,
#    "version_switcher": "https://raw.githubusercontent.com/aksiome/breeze/refs/heads/main/docs/_static/switcher.json",
    "languages": [
        ("English", f"/en/{version}/%s/", "en"),
    ],
}

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    "papersize": "a4paper",
    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
    # Latex figure (float) alignment
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "otfmidoc.tex", "otfmi Documentation", "Sylvain Girard", "manual"),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "otfmidoc", "otfmi Documentation", [author], 1)]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "otfmidoc",
        "otfmi Documentation",
        author,
        "otfmi",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# https://github.com/openturns/otfmi

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False
