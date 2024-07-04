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

Multifunctional activities can lead to linear algebra problems which don't have exactly one solution. Therefore, we commonly need to apply a handling function to either partition such activities, or otherwise manipulate their data such that they allow for the creation of a square and non-singular technosphere matrix.

This library is designed around the following workflow:

1. Multifunctional process(es) are created and saved in a `MultifunctionalDatabase`. A multifunctional process is any process with multiple functional edges, either outputs (e.g. products) and/or input (e.g. wastes). Each functional edge must be labelled `functional=True`.
2. The user specifies an allocation strategy for the database:

```python
database_obj.metadata['default_allocation'] = 'price'
database_obj.metadata.flush()
```

3. LCA calculations can be done as normal. See `dev/basic_example.ipynb` for a simple example.

### Substitution

You don't need to use library for substitution, that already works natively in Brightway. Just produce a product which another process also produces (i.e. has the same database name and code), and the production amount of the other process will be reduced as needed to meet the functional unit demand.

### Built-in allocation functions

`multifunctional` includes the following built-in property-based allocation functions:

* `price`: Does economic allocation based on the property "price" in each functional edge.
* `mass`: Does economic allocation based on the property "mass" in each functional edge.
* `manual`: Does economic allocation based on the property "manual" in each functional edge.

Property-based allocation assumes that each functional edge has a `properties` dictionary, and this dictionary has the relevant key with a corresponding numeric value. For example, for `price` allocation, each functional edge needs to have `'properties' = {'price': some_number}`.

The allocation strategy `equal` is also included, though mostly for testing purposes. This divides impacts equally across each functional edge.

### Custom property-based allocation functions

To create new property-based allocation functions, add an entry to `allocation_strategies` using the function `property_allocation`:

```python
import multifunctional as mf
mf.allocation_strategies['foo'] = property_allocation('bar')
```

Additions to `allocation_strategies` are not persisted, so need to be repeated in each Python interpreter.

### Custom single-factor allocation functions

To create custom allocation functions which apply a single allocation factor to all nonfunctional inputs and outputs, pass a function to `multifunctional.allocation.generic_allocation`. This function needs to accept the following input arguments:

* edge_data (dict): Data on functional edge
* node: An instance of `multifunctional.MaybeMultifunctionalProcess`

The custom function should return a number.

The custom function needs to be curried and added to `allocation_strategies`. You can follow this example:

```python
import multifunctional as mf
from functools import partial

def allocation_factor(edge_data: dict, node: mf.MaybeMultifunctionalProcess) -> float:
   """Nonsensical allocation factor generation"""
   if edge_data.get("unit") == "kg":
      return 1.2
   elif "silly" in node["name"]:
      return 4.2
   else:
      return 7

mf.allocation_strategies['silly'] = partial(mf.generic_allocation, func=allocation_factor)
```

### Other custom allocation functions

To have complete control over allocation, add your own function to `allocation_strategies`. This function should take an input of `multifunctional.MultifunctionalProcess`, and return a list of dictionaries. These dictionaries can follow the [normal `ProcessWithReferenceProduct` data schema](https://github.com/brightway-lca/bw_interface_schemas/blob/5fb1d40587aec2a4bb2248505550fc883a91c355/bw_interface_schemas/lci.py#L83), but the new node datasets need to also include the following:

* `multifunctional_parent_id`: Integer database id of the source multifunctional process
* `type`: Should always be "readonly_process"

Furthermore, the code of the allocated processes (`allocated_product_code`) must be written to each functional edge (and that edge saved so this data is persisted). See the code in `multifunctional.allocation.generic_allocation` for an example.

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
