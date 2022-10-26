[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![Documentation Status](https://readthedocs.org/projects/holden/badge/?version=latest)](http://holden.readthedocs.io/?badge=latest)

<p align="center">
<img src="https://media.giphy.com/media/3ornjRyce6SukW8INi/giphy.gif" />
</p>

This package is named after the Roci's captain in The Expanse, James Holden, who was adept at furling his brow and recognizing connections. In a similar vein, holden offers users easy-to-use composite data structures without the overhead or complexity of larger graph packages. The included graphs are built for basic workflow design or analysis of conditional relationships. They are not meant for big data network analysis or similar large-scale projects (although nothing prevents you from using them in that manner). Rather, the goal of holden is to provide lightweight, turnkey, extensible graphs without all of the stuff you don't need in packages like [networkx](https://github.com/networkx/networkx) or [airflow](https://github.com/apache/airflow).

## Simple

The basic building blocks provided are:
* Graph: the base class for all graph data structures
* Edge: an optional edge class which can be treated as a drop-in tuple replacement or extended for greater functionality
* Node: an optional vertex class which provides universal hashability and some other convenient functions
* Forms: a dictionary that automatically stores all direct Graph subclasses to allow flexible subtype checking of and transformation between graph subtypes using the 'classify' and 'transform' methods

Out of the box, Graph has several subtypes with varying internal storage formats:
* Adjacency: an adjacency list using a dict(Hashable, set(Hashable)) structure
* Matrix: an adjacency matrix that uses a list[list[Hashable]] for mapping edges and a separate list[str] attribute that corresponds to the list of lists matrix
* Edges: an edge list structure that uses a list[tuple[Hashable, Hashable]] format
  
You can use holden without any regard to what is going on inside the graph. The methods and properties are the same regardless of which internal format is used. But the different forms are provided in case you want to utilize the advantages of each form or avoid certain drawbacks. Unless you want to design a different graph form, you should design subclasses to inherit from one of the
included types and add mixins to expand functionality.

## Flexible

 Various traits can be added to graphs, nodes, and edges as mixins including:
* Weighted edges (Weighted)
* Abilty to create a graph from or convert any graph to any recognized form (Fungible)
* Directed graphs (Directed)
* Automatically names objects if a name is not passed (Labeled)
* Ability to store nodes internally for easy reuse separate from the graph structure (Storage)

holden provides transformation methods between all of the internal storage forms as well as functions to convert graphs into a set of paths (Parallel) or a single path (Serial). The transformation methods can be used as class properties or with functions using an easy-to-understand naming convention (e.g., adjacency_to_edges or edges_to_parallel).

holden's framework supports a wide range of coding styles. You can create complex multiple inheritance structures with mixins galore or simpler, compositional objects. Even though the data structures are necessarily object-oriented, all of the tools to modify them are also available as functions, for those who prefer a more functional approaching to programming.

## Contributing

The project is also highly documented so that users and developers and make holden work with their projects. It is designed for Python coders at all levels. Beginners should be able to follow the readable code and internal documentation to understand how it works. More advanced users should find complex and tricky problems addressed through efficient code.

I hope you find holden useful and feel free to contribute, leave suggestions, or report bugs.

<p align="center">
<img src="https://media.giphy.com/media/3oKIPwyf0EBAGnAkWk/giphy.gif" />
</p>
