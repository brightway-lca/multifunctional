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
from .utils import prepare_multifunctional_for_writing


def multifunctional_dispatcher_method(
    db: "MultifunctionalDatabase", document: ActivityDataset
):
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

    # def datapackage(self):
    #     """Pick the right datapackage depending on settings"""
    #     if (aggregation_override.global_override is True) or (
    #         aggregation_override.local_overrides.get(self.name, None) is True
    #     ):
    #         fp = self.filepath_aggregated()
    #     elif (aggregation_override.global_override is False) or (
    #         aggregation_override.local_overrides.get(self.name, None) is False
    #     ):
    #         fp = self.filepath_processed()
    #     else:
    #         fp = (
    #             self.filepath_aggregated()
    #             if self.metadata.get("aggregation_use_in_calculation")
    #             else self.filepath_processed()
    #         )
    #     with ZipFS(fp) as zip_fs:
    #         return load_datapackage(zip_fs)

    # def filepath_aggregated(self):
    #     if not self.aggregation_datapackage_valid():
    #         MESSAGE = f"""Aggregated datapackage for database '{self.name}' is out of date.
    # It needs to be recalculated with:

    #     import bw_aggregated as bwa
    #     bwa.AggregatedDatabase("{self.name}").process_aggregated()

    # If you have mutual references in multiple aggregated databases, you can refresh all outdated
    # with:

    #     bwa.AggregatedDatabase.refresh_all()

    # """
    #         raise ObsoleteAggregatedDatapackage(MESSAGE)

    #     return self.dirpath_processed() / self.filename_aggregated()

    # def filename_aggregated(self):
    #     return clean_datapackage_name(self.filename + "aggregated.zip")

    # def refresh(self) -> None:
    #     """Easy to remember shortcut for humans."""
    #     self.process_aggregated()

    # def write(self, data, process=True, searchable=True) -> None:
    #     if not check_processes_in_data(data.values()):
    #         raise IncompatibleDatabase(
    #             "This data only has biosphere flows, and can't be aggregated."
    #         )

    #     super().write(data=data, process=process, searchable=searchable)

    #     if process:
    #         self.process_aggregated()

    # def process_aggregated(self, in_memory: bool = False) -> Datapackage:
    #     """Create structured arrays for the aggregated biosphere emissions, and for unitary production."""
    #     # Try to avoid race conditions - but no guarantee
    #     self.metadata["aggregation_calculation_timestamp"] = dt.now().isoformat()

    #     calculator = AggregationCalculator(self.name)
    #     calculator.calculate()

    #     dp = create_datapackage(
    #         fs=(
    #             None
    #             if in_memory
    #             else ZipFS(str(self.filepath_aggregated()), write=True)
    #         ),
    #         name=clean_datapackage_name(self.name),
    #         sum_intra_duplicates=True,
    #         sum_inter_duplicates=False,
    #     )
    #     self._add_inventory_geomapping_to_datapackage(dp=dp)

    #     dp.add_persistent_vector_from_iterator(
    #         matrix="biosphere_matrix",
    #         name=clean_datapackage_name(self.name + " biosphere matrix"),
    #         dict_iterator=calculator.biosphere_iterator,
    #     )
    #     dp.add_persistent_vector_from_iterator(
    #         matrix="technosphere_matrix",
    #         name=clean_datapackage_name(self.name + " technosphere matrix"),
    #         dict_iterator=calculator.technosphere_iterator,
    #     )
    #     if not in_memory:
    #         dp.finalize_serialization()
    #     return dp

    def write(self, data: dict, *args, **kwargs) -> None:
        data = prepare_multifunctional_for_writing(data)
        super().write(data, *args, **kwargs)
