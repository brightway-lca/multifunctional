from bw2data import databases
from bw2data.backends import SQLiteBackend
from bw2data.backends.schema import ActivityDataset
from bw_processing import (
    Datapackage,
    clean_datapackage_name,
    create_datapackage,
    load_datapackage,
    safe_filename,
)

from .node_dispatch import multifunctional_node_dispatcher
from .utils import add_exchange_input_if_missing, label_multifunctional_nodes


def multifunctional_dispatcher_method(db: "MultifunctionalDatabase", document: ActivityDataset):
    return multifunctional_node_dispatcher(document)


class MultifunctionalDatabase(SQLiteBackend):
    """A database which includes multifunctional processes (i.e. processes which have more than one
    functional input and/or output edge). Such multifunctional processes normally break square
    matrix construction, so need to be resolved in some way.

    We support three options:

    * Mark the process as `"skip_allocation"=True`. You have manually constructed the database so
        that is produces a valid technosphere matrix, by e.g. having two multifunctional processes
        with the same two functional edge products.
    * Using substitution, so that a functional edge corresponds to the same functional edge in
        another process, e.g. combined heat and power produces two functional products, but the
        heat product is also produced by another process, so the amount of that other process would
        be decreased.
    * Using allocation, and splitting a multifunctional process in multiple read-only single output
        unit processes. The strategy used for allocation can be changed dynamically to investigate
        the impact of different allocation approaches.

    This class uses custom `Node` classes for multifunctional processes and read-only single-output
    unit processes.

    Stores default allocation strategies per database in the `Database` metadata dictionary:

    * `default_allocation`: str. Reference to function in `multifunctional.allocation_strategies`.

    Each database has one default allocation, but individual processes can also have specific
    default allocation strategies in `MultifunctionalProcess['default_allocation']`.

    Allocation strategies need to reference a process `property`. See the README.

    """

    backend = "multifunctional"
    node_class = multifunctional_dispatcher_method

    def write(self, data: dict, *args, **kwargs) -> None:
        data = label_multifunctional_nodes(add_exchange_input_if_missing(data))
        super().write(data, *args, **kwargs)

    def process(self, csv: bool = False, allocate: bool = True) -> None:
        if allocate:
            for node in filter(lambda x: x.multifunctional, self):
                node.allocate()
        super().process(csv=csv)
