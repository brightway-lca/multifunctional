"""Fixtures for bw_simapro_csv"""

from copy import deepcopy

import pytest
from bw2data.tests import bw2test
from fixtures.basic import DATA as BASIC_DATA
from fixtures.internal_linking import DATA as INTERNAL_LINKING_DATA
from fixtures.products import DATA as PRODUCT_DATA

from multifunctional import allocation_before_writing


@pytest.fixture
def basic_data():
    return deepcopy(BASIC_DATA)


@pytest.fixture
@bw2test
def basic():
    from multifunctional import MultifunctionalDatabase

    db = MultifunctionalDatabase("basic")
    db.write(deepcopy(BASIC_DATA), process=False)
    db.metadata["dirty"] = True
    return db


@pytest.fixture
@bw2test
def products():
    from multifunctional import MultifunctionalDatabase

    db = MultifunctionalDatabase("products")
    db.write(deepcopy(PRODUCT_DATA), process=False)
    db.metadata["dirty"] = True
    return db


@pytest.fixture
@bw2test
def internal():
    from multifunctional import MultifunctionalDatabase

    db = MultifunctionalDatabase("internal")
    db.register(default_allocation="price")
    db.write(
        allocation_before_writing(deepcopy(INTERNAL_LINKING_DATA), "price"),
        process=False,
    )
    db.process(allocate=False)
    return db
