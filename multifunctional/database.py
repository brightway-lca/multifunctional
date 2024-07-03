# # -*- coding: utf-8 -*-
# from . import sqlite3_lci_db
from bw2data import mapping, geomapping, config
# from ...errors import UntypedExchange, InvalidExchange, UnknownObject, WrongDatabase
# from ...project import writable_project
# from ...search import IndexManager, Searcher
# from ...utils import as_uncertainty_dict
# from ..base import LCIBackend
# from ..utils import check_exchange
# from .proxies import Activity
from bw2data.backends.peewee.utils import (
    dict_as_activitydataset,
    dict_as_exchangedataset,
    retupleize_geo_strings,
)
from bw2data.backends.peewee.schema import ActivityDataset, ExchangeDataset
from bw_processing import clean_datapackage_name, create_datapackage
import datetime
import itertools
from bw2data.backends.peewee.database import SQLiteBackend


class MultifunctionalDatabase(SQLiteBackend):
    def process(self):
        """Create structured arrays for the technosphere and biosphere matrices.

        Uses ``bw_processing`` for array creation and metadata serialization.

        Also creates a ``geomapping`` array, linking activities to locations. Used for regionalized calculations.

        Use a raw SQLite3 cursor instead of Peewee for a ~2 times speed advantage.

        """
        # Try to avoid race conditions - but no guarantee
        self.metadata["processed"] = datetime.datetime.now().isoformat()

        # Get number of exchanges and processes to set
        # initial Numpy array size (still have to include)
        # implicit production exchanges
        dependents = set()

        # Create geomapping array, from dataset interger ids to locations
        inv_mapping_qs = ActivityDataset.select(
            ActivityDataset.location, ActivityDataset.code
        ).where(
            ActivityDataset.database == self.name, ActivityDataset.type == "process"
        )

        dp = create_datapackage(
            dirpath=self.dirpath_processed(),
            name=self.filename_processed(),
            compress=True,
            overwrite=True,
            duplicates="sum",
        )
        dp.add_persistent_vector_from_iterator(
            nrows=inv_mapping_qs.count(),
            dict_iterator=(
                {
                    "row": mapping[(self.name, row["code"])],
                    "col": geomapping[
                        retupleize_geo_strings(row["location"])
                        or config.global_location
                    ],
                    "amount": 1,
                }
                for row in inv_mapping_qs.dicts()
            ),
            matrix_label="inv_geomapping_matrix",
            name=clean_datapackage_name(self.name + " inventory geomapping matrix"),
        )

        BIOSPHERE_SQL = """SELECT data, input_database, input_code, output_database, output_code
                FROM exchangedataset
                WHERE output_database = ?
                AND type = 'biosphere'
        """
        dp.add_persistent_vector_from_iterator(
            dict_iterator=self.exchange_data_iterator(BIOSPHERE_SQL, dependents),
            matrix_label="biosphere_matrix",
            name=clean_datapackage_name(self.name + " biosphere matrix"),
        )

        # Figure out when the production exchanges are implicit
        implicit_production = (
            {"row": mapping[(self.name, x[0])], "amount": 1}
            # Get all codes
            for x in ActivityDataset.select(ActivityDataset.code)
            .where(
                # Get correct database name
                ActivityDataset.database == self.name,
                # Only consider `process` type activities
                ActivityDataset.type << ("process", None),
                # But exclude activities that already have production exchanges
                ~(
                    ActivityDataset.code
                    << ExchangeDataset.select(
                        # Get codes to exclude
                        ExchangeDataset.output_code
                    ).where(
                        ExchangeDataset.output_database == self.name,
                        ExchangeDataset.type << ("production", "generic production"),
                    )
                ),
            )
            .tuples()
        )

        TECHNOSPHERE_POSITIVE_SQL = """SELECT data, input_database, input_code, output_database, output_code
                FROM exchangedataset
                WHERE output_database = ?
                AND type IN ('production', 'substitution', 'generic production')
        """
        TECHNOSPHERE_NEGATIVE_SQL = """SELECT data, input_database, input_code, output_database, output_code
                FROM exchangedataset
                WHERE output_database = ?
                AND type IN ('technosphere', 'generic consumption')
        """

        dp.add_persistent_vector_from_iterator(
            dict_iterator=itertools.chain(
                self.exchange_data_iterator(
                    TECHNOSPHERE_NEGATIVE_SQL, dependents, flip=True
                ),
                self.exchange_data_iterator(TECHNOSPHERE_POSITIVE_SQL, dependents),
                implicit_production,
            ),
            matrix_label="technosphere_matrix",
            name=clean_datapackage_name(self.name + " technosphere matrix"),
        )
        dp.finalize_serialization()

        self.metadata["depends"] = sorted(dependents)
        self.metadata["dirty"] = False
        self._metadata.flush()
