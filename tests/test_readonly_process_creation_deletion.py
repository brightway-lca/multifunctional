import bw2data as bd
from bw2data.tests import bw2test

from multifunctional import MultifunctionalDatabase
from multifunctional.allocation import generic_allocation
from multifunctional.node_classes import (
    MaybeMultifunctionalProcess,
    ReadOnlyProcessWithReferenceProduct,
)


def test_allocation_creates_readonly_nodes(products):
    assert len(products) == 3

    products.metadata["default_allocation"] = "price"
    bd.get_node(code="1").allocate()
    assert len(products) == 5

    assert sorted([ds["type"] for ds in products]) == [
        "emission",
        "multifunctional",
        "product",
        "readonly_process",
        "readonly_process",
    ]


def test_node_save_skips_allocation(products):
    assert len(products) == 3

    products.metadata["default_allocation"] = "price"
    bd.get_node(code="1").save()
    assert len(products) == 3


def test_marking_exchange_as_nonfunctional(products):
    assert len(products) == 3

    products.metadata["default_allocation"] = "price"
    bd.get_node(code="1").allocate()
    assert bd.get_node(code="1")["type"] == "multifunctional"
    assert len(products) == 5

    exc = list(bd.get_node(code="1").production())[0]
    assert exc["functional"]
    exc["functional"] = False
    exc.save()
    bd.get_node(code="1").allocate()
    assert bd.get_node(code="1")["type"] in ("process", "processwithreferenceproduct")
    assert len(products) == 3


def test_change_functional_state_multiple_times(products):
    assert len(products) == 3

    products.metadata["default_allocation"] = "price"
    bd.get_node(code="1").allocate()
    assert bd.get_node(code="1")["mf_was_once_allocated"]
    assert bd.get_node(code="1")["type"] == "multifunctional"
    assert len(products) == 5

    exc = list(bd.get_node(code="1").production())[0]
    assert exc["functional"]
    exc["functional"] = False
    exc.save()
    bd.get_node(code="1").allocate()
    assert bd.get_node(code="1")["mf_was_once_allocated"]
    assert bd.get_node(code="1")["type"] in ("process", "processwithreferenceproduct")
    assert len(products) == 3

    exc = list(bd.get_node(code="1").production())[0]
    exc["functional"] = True
    exc.save()
    bd.get_node(code="1").allocate()
    assert bd.get_node(code="1")["type"] == "multifunctional"
    assert len(products) == 5

    exc = list(bd.get_node(code="1").production())[0]
    exc["functional"] = False
    exc.save()
    bd.get_node(code="1").allocate()
    assert bd.get_node(code="1")["type"] in ("process", "processwithreferenceproduct")
    assert len(products) == 3

    exc = list(bd.get_node(code="1").production())[0]
    exc["functional"] = True
    exc.save()
    bd.get_node(code="1").allocate()
    assert bd.get_node(code="1")["type"] == "multifunctional"
    assert len(products) == 5


def test_change_multifunctional_reduce_num_still_multifunctional(many_products):
    assert len(many_products) == 5

    many_products.metadata["default_allocation"] = "price"
    bd.get_node(code="1").allocate()
    assert bd.get_node(code="1")["mf_was_once_allocated"]
    assert bd.get_node(code="1")["type"] == "multifunctional"
    assert len(many_products) == 8

    exc = [exc for exc in bd.get_node(code="1").exchanges() if exc.input["code"] == "p1"][0]
    assert exc["functional"]
    exc["functional"] = False
    exc.save()
    bd.get_node(code="1").allocate()
    assert bd.get_node(code="1")["mf_was_once_allocated"]
    assert bd.get_node(code="1")["type"] == "multifunctional"
    assert len(many_products) == 7

    exc = [exc for exc in bd.get_node(code="1").exchanges() if exc.input["code"] == "p1"][0]
    exc["functional"] = True
    exc.save()
    bd.get_node(code="1").allocate()
    assert bd.get_node(code="1")["type"] == "multifunctional"
    assert len(many_products) == 8

    exc = [exc for exc in bd.get_node(code="1").exchanges() if exc.input["code"] == "p1"][0]
    exc["functional"] = False
    exc.save()
    bd.get_node(code="1").allocate()
    assert bd.get_node(code="1")["type"] == "multifunctional"
    assert len(many_products) == 7

    exc = [exc for exc in bd.get_node(code="1").exchanges() if exc.input["code"] == "p1"][0]
    exc["functional"] = True
    exc.save()
    bd.get_node(code="1").allocate()
    assert bd.get_node(code="1")["type"] == "multifunctional"
    assert len(many_products) == 8
