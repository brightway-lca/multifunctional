import bw2data as bd
from loguru import logger

from multifunctional.utils import (
    add_exchange_input_if_missing,
    label_multifunctional_nodes,
    product_as_process_name,
    update_datasets_from_allocation_results,
)


def test_add_exchange_input_if_missing(caplog):
    logger.enable("multifunctional")

    given = {
        ("db", "code"): {
            "exchanges": [
                {"functional": False},
                {},
                {"functional": True, "input": ("db", "other")},
                {"functional": True, "input": ("db", "foo"), "code": "bar"},
                {"functional": True, "code": "foo"},
                {"functional": True, "code": "foo", "database": "something"},
                {"functional": True},
            ]
        },
        ("db", "more"): {
            "database": "me",
            "exchanges": [
                {"functional": True, "code": "foo"},
            ],
        },
    }
    expected = {
        ("db", "code"): {
            "exchanges": [
                {"functional": False},
                {},
                {"functional": True, "input": ("db", "other")},
                {"functional": True, "input": ("db", "foo"), "code": "foo"},
                {
                    "functional": True,
                    "input": ("db", "code"),
                    "mf_artificial_code": True,
                    "code": "foo",
                },
                {
                    "functional": True,
                    "input": ("db", "code"),
                    "mf_artificial_code": True,
                    "code": "foo",
                    "database": "something",
                },
                {
                    "functional": True,
                    "input": ("db", "code"),
                    "mf_artificial_code": True,
                },
            ]
        },
        ("db", "more"): {
            "database": "me",
            "exchanges": [
                {
                    "functional": True,
                    "code": "foo",
                    "input": ("db", "more"),
                    "mf_artificial_code": True,
                },
            ],
        },
    }
    assert add_exchange_input_if_missing(given) == expected
    assert "given 'code' is 'bar' but 'input' code is 'foo'" in caplog.text


def test_label_multifunctional_nodes():
    given = {
        1: {"exchanges": [{"functional": True}, {"functional": False}]},
        2: {},
        3: {"exchanges": [{"functional": True}, {"functional": True}, {}]},
    }
    expected = {
        1: {"exchanges": [{"functional": True}, {"functional": False}]},
        2: {},
        3: {
            "exchanges": [{"functional": True}, {"functional": True}, {}],
            "type": "multifunctional",
        },
    }
    assert label_multifunctional_nodes(given) == expected


def test_product_as_process_name():
    given = [
        {"exchanges": [{"functional": True}, {"functional": True}]},
        {"exchanges": [{"functional": True}]},
        {"exchanges": [{"functional": True, "name": "night train"}]},
        {"exchanges": []},
    ]
    expected = [
        {"exchanges": [{"functional": True}, {"functional": True}]},
        {"exchanges": [{"functional": True}]},
        {"name": "night train", "exchanges": [{"functional": True, "name": "night train"}]},
        {"exchanges": []},
    ]
    product_as_process_name(given)
    assert given == expected


def test_update_datasets_from_allocation_results(basic):
    basic.metadata["default_allocation"] = "price"
    basic.process()

    ds = bd.get_node(code="my favorite code")
    mf = ds.parent

    assert ds
    assert mf
