# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## 0.2.0
    * Updated to the latest `snickerdoodle` `cookiecutter` template: `uv` and `hatchling` replace `pdm`, and the GitHub Actions, `pre-commit`, `ruff`, `mypy`, `codecov`, `dependabot`, and `mkdocs` settings were updated
    * Only Python 3.11 and later are supported
    * Completed `Edges` and `Matrix` (`add`, `delete`, `connect`, `disconnect`, `merge`, and `subset` now work for every form)
    * Completed every transformer between the `adjacency`, `edges`, `matrix`, `parallel`, and `serial` forms and every `report` and `traverse` function
    * Completed `Serial` and `Parallel` and made them `Directed`, `Fungible`, and `Exportable`
    * Added the `Storage` trait that the README described
    * Added `holden.get_base` and made `holden.set_base` change the classes that `Forms` uses
    * `isinstance` now recognizes raw structures for the registered forms (for example, `isinstance({"a": {"b"}, "b": set()}, holden.Adjacency)`)
    * `Directed` now works with every form of graph, and `System` is also `Exportable`
    * `Labeled` nodes are hashed and compared by name (a `name` class attribute sets the default name)
    * `Node` subclasses now keep the hash and equality methods of mixins that precede `Node`
    * Exports are deterministic, include nodes without edges, quote identifiers that `dot` and `mermaid` cannot read, and use the names of labeled nodes; `to_dot` output now ends with a newline
    * Fixed `Adjacency` creating nodes when they were looked up or tested with `in`. The default `contents` is now a plain `dict`
    * Fixed `Forms.transform`, `Graph.disconnect`, `Composite.subset`, `Composite.delete`, `Parallel.walk`, `System.walk`, `Serial.walk`, `_windowify`, `is_composite`, `Edge` indexing, `Weighted`, `to_mermaid` settings, and `add_transformer`
    * `walk_serial`, `walk_parallel`, and `Serial.walk`/`Parallel.walk` now return a list of paths, like `System.walk`
    * `Directed` operators (`+` and `+=`) return the modified graph instead of `None`
    * Added type information and complete documentation to all of the code, and added a tutorial, recipes, and an advanced user guide
    * Added unit tests for all of the code and for the examples in the documentation

## 0.1.9
    * Cleaned up documentation from docstrings
    * Added mermaid.js exporter

## 0.1.8
    * Transitioned to `snickerdoodle` `cookiecutter` template
    * Removed extra dependencies
    * Updated class names from `bunches` package
