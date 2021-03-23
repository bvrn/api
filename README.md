# BVRN API

An API for various operation around music associations.
Used and developed for [Blasmusikverband Rhein-Neckar e.V.](https://www.bvrn.de/)

## Local development

### Dependency management

Python dependencies are managed via [Poetry](https://python-poetry.org/).

### Code quality

Various `git` [pre-commit](https://pre-commit.com/) hooks are in place to ensure code quality:

* Generic formatting and consistency checking.
* Sort Python imports via [`isort`](https://pycqa.github.io/isort/).
* Format Python code via [`black`](https://black.readthedocs.io/en/stable/).
