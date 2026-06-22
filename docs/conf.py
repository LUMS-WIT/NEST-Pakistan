project = "NEST-Pakistan"
author = "Arfa Yaseen, Muhammad Awais"
copyright = "2025, Arfa Yaseen, Muhammad Awais"
release = "0.1.0"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "tasklist",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {
    "navigation_depth": 3,
    "titles_only": False,
}

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
