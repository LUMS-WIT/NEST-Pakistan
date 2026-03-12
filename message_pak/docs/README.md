# Building the Documentation

This directory contains the Sphinx-based documentation for NEST-Pakistan.

## Prerequisites

Install the required documentation dependencies:

```bash
pip install -r ../requirement.txt
```

Or install just the documentation packages:

```bash
pip install sphinx sphinx-rtd-theme myst-parser sphinx-copybutton
```

## Building the Documentation

### HTML (Recommended)

To build the HTML documentation:

```bash
cd docs
make html
```

Or on Windows:

```bash
cd docs
make.bat html
```

The built documentation will be available in `docs/_build/html/index.html`.

### Other Formats

You can also build other formats:

- **PDF (LaTeX)**: `make latexpdf`
- **EPUB**: `make epub`
- **Single HTML**: `make singlehtml`

## Viewing the Documentation

After building, open `_build/html/index.html` in your web browser to view the documentation.

## Documentation Structure

- `index.rst` - Main documentation entry point
- `conf.py` - Sphinx configuration file
- `*.md` - Source markdown files (automatically converted by myst-parser)
- `*.rst` - ReStructuredText wrapper files for markdown content
- `include/` - Additional resources (images, diagrams, etc.)
- `_build/` - Generated documentation (not tracked in git)

## Adding New Documentation

1. Create a new `.md` file in this directory
2. Add it to the `toctree` in `index.rst`
3. Rebuild the documentation

## Continuous Integration

For automated documentation builds, consider setting up:
- Read the Docs (readthedocs.org)
- GitHub Actions
- GitLab CI/CD

