from copy import deepcopy

import pytest
from bw2data.tests import bw2test
from fixtures.basic import DATA as BASIC_DATA
from fixtures.errors import DATA as ERRORS_DATA
from fixtures.internal_linking import DATA as INTERNAL_LINKING_DATA
from fixtures.product_properties import DATA as PP_DATA
from fixtures.products import DATA as PRODUCT_DATA
from fixtures.many_products import DATA as MANY_PRODUCTS_DATA

from multifunctional import MultifunctionalDatabase, allocation_before_writing


@pytest.fixture
def basic_data():
    return deepcopy(BASIC_DATA)


@pytest.fixture
@bw2test
def basic():
    db = MultifunctionalDatabase("basic")
    db.write(deepcopy(BASIC_DATA), process=False)
    db.metadata["dirty"] = True
    return db


@pytest.fixture
@bw2test
def products():
    db = MultifunctionalDatabase("products")
    db.write(deepcopy(PRODUCT_DATA), process=False)
    db.metadata["dirty"] = True
    return db


@pytest.fixture
@bw2test
def many_products():
    db = MultifunctionalDatabase("products")
    db.write(deepcopy(MANY_PRODUCTS_DATA), process=False)
    db.metadata["dirty"] = True
    return db


@pytest.fixture
@bw2test
def errors():
    db = MultifunctionalDatabase("errors")
    db.register(default_allocation="price")
    db.write(deepcopy(ERRORS_DATA))
    return db


@pytest.fixture
@bw2test
def product_properties():
    db = MultifunctionalDatabase("product_properties")
    db.write(deepcopy(PP_DATA), process=False)
    db.metadata["dirty"] = True
    return db


@pytest.fixture
@bw2test
def internal():
    db = MultifunctionalDatabase("internal")
    db.register(default_allocation="price")
    db.write(
        allocation_before_writing(deepcopy(INTERNAL_LINKING_DATA), "price"),
        process=False,
    )
    db.process(allocate=False)
    return db
