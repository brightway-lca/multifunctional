# multifunctional

[![PyPI](https://img.shields.io/pypi/v/multifunctional.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/multifunctional.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/multifunctional)][pypi status]
[![License](https://img.shields.io/pypi/l/multifunctional)][license]

[![Read the documentation at https://multifunctional.readthedocs.io/](https://img.shields.io/readthedocs/multifunctional/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/brightway-lca/multifunctional/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/brightway-lca/multifunctional/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/multifunctional/
[read the docs]: https://multifunctional.readthedocs.io/
[tests]: https://github.com/brightway-lca/multifunctional/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/brightway-lca/multifunctional
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

Handling multifunctional activities in the Brightway LCA software framework.

## Installation

You can install _multifunctional_ via [pip] from [PyPI]:

```console
$ pip install multifunctional
```

It is also available on `anaconda` using `mamba` or `conda` at the `cmutel` channel:

```console
mamba install -c conda-forge -c cmutel multifunctional
```

## Usage

Multifunctional activities can lead to linear algebra problems which don't have exactly one solution. Therefore, we commonly need to apply a handling function to either partition such activities, or otherwise manipulate their data such that they allow for the creation of a non-singular, square technosphere matrix.

This library is designed around the following workflow:

1. A multifunctional process is created and saved to the database by a user. A multifunctional process is any process with multiple functional flows, either outputs (e.g. products) and/or input (e.g. wastes).
1. The user provides a handling function of this process, such as substitution, allocation, etc.
1. When this database is processed, this library will apply the handling function, and create a square matrix for the database.

More functionality is planned; see [limitations](#limitations).

## How does it work?

1. LCA distinguishes processes and products. brightway introduces a new classification at the product level where products are either defined as goods or wastes.
   This classification is consistently maintained within a project, meaning that the same product cannot be classified as a good in one process and as a waste in another process.
   Or in other words, all intermediate flows of the same product carry the same classification (good OR waste).
1. brightway determines functional flows based on the good/waste classification of the flows of a process.
   Functional flows are defined as process outputs that are goods and process inputs that are wastes.

1. Adding a functional flow exchange will automatically create a new `product` node in the supply chain graph (if necessary).
1. Multi-functional processes are handled by handler functions. Handler functions are mapped in `multifunctional.handler_mapping`. This library provides a default set of handling functions (see below); users may also add custom handlers.
1. When the database is processed, the handler functions are executed, and if necessary, virtual activities are created. The processed array will create a square matrix.

## What does the user need to do?

1. Users specify products to be either goods or wastes when creating them the first time (this can be changed later, but may lead to changes in multiple processes): ``product['waste'] = False``.
1. Users need to specify which allocation method is to be used to resolve multi-functionality (e.g. economic allocation or substitution) and users need to provide the required data (e.g. prices or substitute product) so that multi-functionality can be resolved by one of the handlers.
Users give multifunctional activities a handler function label: ``activity_instance['handler'] = 'some_handler_function_label'``. Handler function labels are strings.

## Limitations

* This library current only works with the default SQlite backend

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [BSD 3 Clause license][License],
_multifunctional_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://multifunctional.readthedocs.io/en/latest/usage.html
[License]: https://github.com/brightway-lca/multifunctional/blob/main/LICENSE
[Contributor Guide]: https://github.com/brightway-lca/multifunctional/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/brightway-lca/multifunctional/issues


## Building the Documentation

You can build the documentation locally by installing the documentation Conda environment:

```bash
conda env create -f docs/environment.yml
```

activating the environment

```bash
conda activate sphinx_multifunctional
```

and [running the build command](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#sphinx-build):

```bash
sphinx-build docs _build/html --builder=html --jobs=auto --write-all; open _build/html/index.html
```
