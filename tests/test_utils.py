from multifunctional.utils import add_exchange_input_if_missing


def test_add_exchange_input_if_missing_no_code():
    given = {
        "foo": {
            "exchanges": [
                {"functional": True},
                {},
                {"functional": True, "input": "bar"},
            ]
        }
    }
    expected = {
        "foo": {
            "exchanges": [
                {"functional": True, "input": "foo"},
                {},
                {"functional": True, "input": "bar"},
            ]
        }
    }
    assert add_exchange_input_if_missing(given) == expected


def test_add_exchange_input_if_missing_code_present():
    given = {
        "foo": {
            "database": "1",
            "exchanges": [
                {"functional": True, "code": "2"},
                {},
                {"functional": True, "input": "bar"},
            ]
        }
    }
    expected = {
        "foo": {
            "database": "1",
            "exchanges": [
                {"functional": True, "code": "2", "input": ("1", "2")},
                {},
                {"functional": True, "input": "bar"},
            ]
        }
    }
    assert add_exchange_input_if_missing(given) == expected
