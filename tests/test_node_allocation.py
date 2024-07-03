import bw2data as bd
import pytest


def test_basic_allocation(basic):
    process = bd.get_node(code="1")
    with pytest.raises(ValueError):
        process.allocate()


def test_basic_allocation_wrong_database_default(basic):
    basic.metadata["default_allocation"] = "foo"
    process = bd.get_node(code="1")
    with pytest.raises(KeyError):
        process.allocate()


def test_basic_allocation_wrong_process_default(basic):
    process = bd.get_node(code="1")
    process["default_allocation"] = "foo"
    with pytest.raises(KeyError):
        process.allocate()
