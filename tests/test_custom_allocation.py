import logging
from typing import Callable

from bw2data import get_node, projects
from bw2data.tests import bw2test

from multifunctional import (
    add_custom_property_allocation_to_project,
    allocation_strategies,
    check_property_for_allocation,
    check_property_for_process_allocation,
    list_available_properties,
    MultifunctionalDatabase,
)
from multifunctional.custom_allocation import (
    DEFAULT_ALLOCATIONS,
    MessageType,
)


@bw2test
def test_allocation_strategies_changing_project():
    assert set(allocation_strategies) == DEFAULT_ALLOCATIONS

    projects.set_current("other")
    add_custom_property_allocation_to_project("whatever")
    assert "whatever" in allocation_strategies
    assert isinstance(allocation_strategies["whatever"], Callable)

    projects.set_current("default")
    assert "whatever" not in allocation_strategies
    assert set(allocation_strategies) == DEFAULT_ALLOCATIONS

    projects.set_current("other")
    assert "whatever" in allocation_strategies
    assert isinstance(allocation_strategies["whatever"], Callable)


def test_check_property_for_allocation_success(basic):
    basic.metadata["default_allocation"] = "price"
    basic.process()
    assert check_property_for_allocation("basic", "price")


def test_check_property_for_allocation_failure(errors):
    result = check_property_for_allocation("errors", "mass")
    expected = {
        (
            logging.WARNING,
            MessageType.MISSING_PRODUCT_PROPERTY,
            get_node(code="a").id,
            get_node(code="1").id,
        ),
        (
            logging.CRITICAL,
            MessageType.NONNUMERIC_PRODUCT_PROPERTY,
            get_node(code="b").id,
            get_node(code="1").id,
        ),
        (
            logging.CRITICAL,
            MessageType.NONNUMERIC_EDGE_PROPERTY,
            get_node(code="first one here").id,
            get_node(code="1").id,
        ),
        (
            logging.WARNING,
            MessageType.MISSING_EDGE_PROPERTY,
            get_node(code="second one here").id,
            get_node(code="1").id,
        ),
    }
    assert len(result) == 4
    for err in result:
        assert (err.level, err.message_type, err.product_id, err.process_id) in expected


def test_check_process_property_for_allocation_failure(errors):
    msg_list = []
    check_property_for_process_allocation(get_node(code="1"), "mass", msg_list)
    expected = {
        (
            logging.WARNING,
            MessageType.MISSING_PRODUCT_PROPERTY,
            get_node(code="a").id,
            get_node(code="1").id,
        ),
        (
            logging.CRITICAL,
            MessageType.NONNUMERIC_PRODUCT_PROPERTY,
            get_node(code="b").id,
            get_node(code="1").id,
        ),
        (
            logging.CRITICAL,
            MessageType.NONNUMERIC_EDGE_PROPERTY,
            get_node(code="first one here").id,
            get_node(code="1").id,
        ),
        (
            logging.WARNING,
            MessageType.MISSING_EDGE_PROPERTY,
            get_node(code="second one here").id,
            get_node(code="1").id,
        ),
    }
    assert len(msg_list) == 4
    for err in msg_list:
        assert (err.level, err.message_type, err.product_id, err.process_id) in expected


def test_check_process_property_for_allocation_failure_process_type(errors):
    msg_list = []
    result = check_property_for_process_allocation(get_node(code="a"), "mass", msg_list)
    assert result is True
    assert not msg_list


@bw2test
def test_check_property_for_allocation_failure_boolean():
    DATA = {
        ("errors", "a"): {
            "name": "product a",
            "unit": "kg",
            "type": "product",
            "properties": {"price": 7.7, "mass": 1},
        },
        ("errors", "b"): {
            "name": "product b",
            "unit": "kg",
            "type": "product",
            "properties": {
                "price": 8.1,
                "mass": True,
            },
        },
        ("errors", "1"): {
            "name": "process - 1",
            "type": "multifunctional",
            "exchanges": [
                {
                    "functional": True,
                    "type": "production",
                    "input": ("errors", "a"),
                    "amount": 4,
                },
                {
                    "functional": True,
                    "type": "production",
                    "input": ("errors", "b"),
                    "amount": 4,
                },
            ],
        },
    }
    db = MultifunctionalDatabase("errors")
    db.register(default_allocation="price")
    db.write(DATA)

    result = check_property_for_allocation("errors", "mass")
    print(result)
    expected = (
        logging.CRITICAL,
        MessageType.NONNUMERIC_PRODUCT_PROPERTY,
        get_node(code="b").id,
        get_node(code="1").id,
    )
    assert len(result) == 1
    assert (
        result[0].level,
        result[0].message_type,
        result[0].product_id,
        result[0].process_id,
    ) == expected


def test_list_available_properties_basic(basic):
    basic.metadata["default_allocation"] = "price"
    basic.process()
    expected = [
        ("price", MessageType.ALL_VALID),
        ("mass", MessageType.ALL_VALID),
        ("manual_allocation", MessageType.ALL_VALID),
    ]
    for obj in list_available_properties("basic"):
        assert obj in expected


def test_list_available_properties_errors(errors):
    expected = [
        ("price", MessageType.ALL_VALID),
        ("mass", MessageType.NONNUMERIC_PROPERTY),
    ]
    for obj in list_available_properties("errors"):
        assert obj in expected


def test_list_available_properties_for_process_basic(basic):
    basic.metadata["default_allocation"] = "price"
    basic.process()
    expected = [
        ("price", MessageType.ALL_VALID),
        ("mass", MessageType.ALL_VALID),
        ("manual_allocation", MessageType.ALL_VALID),
    ]
    for obj in list_available_properties("basic", get_node(code="1")):
        assert obj in expected


def test_list_available_properties_for_process_errors(errors):
    expected_1 = [
        ("price", MessageType.ALL_VALID),
        ("mass", MessageType.NONNUMERIC_PROPERTY),
    ]
    for obj in list_available_properties("errors", get_node(code="1")):
        assert obj in expected_1
    expected_3 = [
        ("price", MessageType.ALL_VALID),
        ("mass", MessageType.ALL_VALID),
    ]
    for obj in list_available_properties("errors", get_node(code="3")):
        assert obj in expected_3
