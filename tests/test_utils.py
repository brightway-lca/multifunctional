from multifunctional.utils import add_exchange_input_if_missing


def test_add_exchange_input_if_missing_no_code():
    given = {
        ("db", "code"): {
            "exchanges": [
                {"functional": True},
                {"functional": False},
                {},
                {"functional": True, "input": ("db", "other")},
            ]
        }
    }
    expected = {
        ("db", "code"): {
            "exchanges": [
                {"functional": True, "input": ("db", "code"), "code": "code", 'mf_artificial_code': True},
                {"functional": False},
                {},
                {"functional": True, "input": ("db", "other"), "code": "other"},
            ]
        }
    }
    assert add_exchange_input_if_missing(given) == expected


def test_add_exchange_input_if_missing_code_present():
    given = {
        ("db", "code"): {
            "database": "1",
            "exchanges": [
                {"functional": True, "code": "2"},
                {},
                {"functional": True, "input": ("db", "other")},
            ]
        }
    }
    expected = {
        ("db", "code"): {
            "database": "1",
            "exchanges": [
                {"functional": True, "code": "2", "input": ("1", "2")},
                {},
                {"functional": True, "input": ("db", "other"), "code": "other"},
            ]
        }
    }
    assert add_exchange_input_if_missing(given) == expected
