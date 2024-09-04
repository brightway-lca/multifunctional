import bw2data as bd
from bw2data.tests import bw2test

from multifunctional.supplemental import add_product_node_properties_to_exchange


@bw2test
def test_not_overwrite_properties():
    bd.Database("foo").write(
        {("foo", "1"): {"properties": {"first": True, "second": False}}}
    )
    data = {
        "database": "foo",
        "code": "2",
        "exchanges": [
            {
                "input": ("foo", "1"),
                "functional": True,
                "type": "production",
                "properties": {"first": 7},
            }
        ],
    }
    expected = {
        "database": "foo",
        "code": "2",
        "exchanges": [
            {
                "input": ("foo", "1"),
                "functional": True,
                "type": "production",
                "__mf__properties_from_product": {"second"},
                "properties": {"first": 7, "second": False},
            }
        ],
    }
    assert add_product_node_properties_to_exchange(data) == expected


@bw2test
def test_update_properties_production():
    bd.Database("foo").write(
        {("foo", "1"): {"properties": {"first": True, "second": False}}}
    )
    data = {
        "database": "foo",
        "code": "2",
        "exchanges": [
            {
                "input": ("foo", "1"),
                "functional": True,
                "type": "production",
            }
        ],
    }
    expected = {
        "database": "foo",
        "code": "2",
        "exchanges": [
            {
                "input": ("foo", "1"),
                "functional": True,
                "__mf__properties_from_product": {"first", "second"},
                "type": "production",
                "properties": {"first": True, "second": False},
            }
        ],
    }
    assert add_product_node_properties_to_exchange(data) == expected


@bw2test
def test_update_properties_technosphere():
    bd.Database("foo").write(
        {("foo", "1"): {"properties": {"first": True, "second": False}}}
    )
    data = {
        "database": "foo",
        "code": "2",
        "exchanges": [
            {
                "input": ("foo", "1"),
                "functional": True,
                "type": "technosphere",
            }
        ],
    }
    expected = {
        "database": "foo",
        "code": "2",
        "exchanges": [
            {
                "input": ("foo", "1"),
                "functional": True,
                "type": "technosphere",
                "__mf__properties_from_product": {"first", "second"},
                "properties": {"first": True, "second": False},
            }
        ],
    }
    assert add_product_node_properties_to_exchange(data) == expected


@bw2test
def test_not_update_properties_other():
    bd.Database("foo").write(
        {("foo", "1"): {"properties": {"first": True, "second": False}}}
    )
    data = {
        "database": "foo",
        "code": "2",
        "exchanges": [
            {
                "input": ("foo", "1"),
                "functional": True,
                "type": "w00t",
            }
        ],
    }
    expected = {
        "database": "foo",
        "code": "2",
        "exchanges": [
            {
                "input": ("foo", "1"),
                "functional": True,
                "type": "w00t",
            }
        ],
    }
    assert add_product_node_properties_to_exchange(data) == expected


@bw2test
def test_skip_exc_without_input():
    bd.Database("foo").write(
        {("foo", "1"): {"properties": {"first": True, "second": False}}}
    )
    data = {
        "database": "foo",
        "code": "2",
        "exchanges": [
            {
                "functional": True,
                "type": "production",
            }
        ],
    }
    expected = {
        "database": "foo",
        "code": "2",
        "exchanges": [
            {
                "functional": True,
                "type": "production",
            }
        ],
    }
    assert add_product_node_properties_to_exchange(data) == expected


def test_get_properties_different_database():
    bd.Database("bar").write(
        {("bar", "1"): {"properties": {"first": True, "second": False}}}
    )
    data = {
        "database": "foo",
        "code": "2",
        "exchanges": [
            {
                "input": ("bar", "1"),
                "functional": True,
                "type": "production",
                "properties": {"first": 7},
            }
        ],
    }
    expected = {
        "database": "foo",
        "code": "2",
        "exchanges": [
            {
                "input": ("bar", "1"),
                "functional": True,
                "type": "production",
                "__mf__properties_from_product": {"second"},
                "properties": {"first": 7, "second": False},
            }
        ],
    }
    assert add_product_node_properties_to_exchange(data) == expected
