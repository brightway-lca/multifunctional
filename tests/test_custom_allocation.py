import logging
from typing import Callable

from bw2data import get_node, projects
from bw2data.tests import bw2test

from multifunctional import (
    add_custom_property_allocation_to_project,
    allocation_strategies,
    check_property_for_allocation,
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
