import bw2data as bd

from multifunctional.allocation import generic_allocation
from multifunctional.node_classes import (
    MaybeMultifunctionalProcess,
    ReadOnlyProcessWithReferenceProduct,
)


def check_products_allocation_results(factor_1, factor_2, database):
    nodes = sorted(
        database, key=lambda x: (x["name"], x.get("reference product", ""), x["type"])
    )

    assert isinstance(nodes[0], MaybeMultifunctionalProcess)
    assert nodes[0]["name"] == "first product"
    assert nodes[0]["type"] == "product"
    assert not list(nodes[0].exchanges())

    assert isinstance(nodes[1], MaybeMultifunctionalProcess)
    assert nodes[1]["name"] == "flow - a"
    assert not list(nodes[1].exchanges())
    assert len(nodes) == 5

    assert isinstance(nodes[2], MaybeMultifunctionalProcess)
    assert nodes[2].multifunctional
    assert "reference product" not in nodes[2]
    assert "mf_parent_key" not in nodes[2]
    expected = {
        "name": "process - 1",
        "type": "multifunctional",
    }
    for key, value in expected.items():
        assert nodes[2][key] == value

    assert isinstance(nodes[3], ReadOnlyProcessWithReferenceProduct)
    expected = {
        "name": "process - 1",
        "reference product": "first product",
        "unit": "kg",
        "mf_parent_key": nodes[2].key,
        "type": "readonly_process",
    }
    for key, value in expected.items():
        assert nodes[3][key] == value

    expected = {
        "input": ("product_properties", "product"),
        "output": nodes[3].key,
        "amount": 4,
        "type": "production",
        "functional": True,
    }
    production = list(nodes[3].production())
    assert len(production) == 1
    for key, value in expected.items():
        assert production[0][key] == value

    expected = {
        "input": nodes[1].key,
        "output": nodes[3].key,
        "amount": factor_1,
        "type": "biosphere",
    }
    biosphere = list(nodes[3].biosphere())
    assert len(biosphere) == 1
    for key, value in expected.items():
        assert biosphere[0][key] == value

    assert not biosphere[0].get("functional")

    assert isinstance(nodes[4], ReadOnlyProcessWithReferenceProduct)
    expected = {
        "name": "process - 1",
        "reference product": "second product - 1",
        "unit": "megajoule",
        "mf_parent_key": nodes[2].key,
        "type": "readonly_process",
    }
    for key, value in expected.items():
        assert nodes[4][key] == value

    expected = {
        "input": nodes[4].key,
        "output": nodes[4].key,
        "amount": 6,
        "type": "production",
        "functional": True,
    }
    production = list(nodes[4].production())
    assert len(production) == 1
    for key, value in expected.items():
        assert production[0][key] == value

    expected = {
        "input": nodes[1].key,
        "output": nodes[4].key,
        "amount": factor_2,
        "type": "biosphere",
    }
    biosphere = list(nodes[4].biosphere())
    assert len(biosphere) == 1
    for key, value in expected.items():
        assert biosphere[0][key] == value

    assert not biosphere[0].get("functional")


def test_without_allocation(product_properties):
    nodes = sorted(
        product_properties,
        key=lambda x: (x["name"], x.get("reference product", ""), x["type"]),
    )

    assert len(nodes) == 3

    assert isinstance(nodes[0], MaybeMultifunctionalProcess)
    assert nodes[0]["name"] == "first product"
    assert nodes[0]["type"] == "product"
    assert not list(nodes[0].exchanges())

    assert isinstance(nodes[1], MaybeMultifunctionalProcess)
    assert nodes[1]["name"] == "flow - a"
    assert not list(nodes[1].exchanges())

    assert isinstance(nodes[2], MaybeMultifunctionalProcess)
    assert nodes[2].multifunctional
    assert "reference product" not in nodes[2]
    assert "mf_parent_key" not in nodes[2]
    expected = {
        "name": "process - 1",
        "type": "multifunctional",
    }
    for key, value in expected.items():
        assert nodes[2][key] == value


def test_price_allocation(product_properties):
    product_properties.metadata["default_allocation"] = "price"
    bd.get_node(code="1").allocate()
    check_products_allocation_results(
        4 * 7 / (4 * 7 + 6 * 12) * 10,
        6 * 12 / (4 * 7 + 6 * 12) * 10,
        product_properties,
    )


def test_mass_allocation(product_properties):
    product_properties.metadata["default_allocation"] = "mass"
    bd.get_node(code="1").allocate()
    check_products_allocation_results(
        4 * 6 / (4 * 6 + 6 * 4) * 10, 6 * 4 / (4 * 6 + 6 * 4) * 10, product_properties
    )


def test_equal_allocation(product_properties):
    product_properties.metadata["default_allocation"] = "mass"
    bd.get_node(code="1").allocate()
    check_products_allocation_results(5, 5, product_properties)


def test_allocation_uses_existing(product_properties):
    product_properties.metadata["default_allocation"] = "price"
    bd.get_node(code="1").allocate()
    product_properties.metadata["default_allocation"] = "equal"
    bd.get_node(code="1").allocate()
    check_products_allocation_results(5, 5, product_properties)


def test_allocation_already_allocated(product_properties):
    product_properties.metadata["default_allocation"] = "price"
    bd.get_node(code="1").allocate()
    node = sorted(
        product_properties, key=lambda x: (x["name"], x.get("reference product", ""))
    )[3]

    assert generic_allocation(node, None) == []


def test_allocation_not_multifunctional(product_properties):
    assert generic_allocation(bd.get_node(code="a"), None) == []
