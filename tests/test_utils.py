from loguru import logger

from multifunctional.utils import add_exchange_input_if_missing, label_multifunctional_nodes


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
