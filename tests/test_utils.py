from multifunctional.utils import add_exchange_input_if_missing


def test_add_exchange_input_if_missing(caplog):
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
                {"functional": True, "input": ("db", "other"), "code": "other"},
                {"functional": True, "input": ("db", "foo"), "code": "foo"},
                {"functional": True, "input": ("db", "foo"), "code": "foo"},
                {
                    "functional": True,
                    "input": ("something", "foo"),
                    "code": "foo",
                    "database": "something",
                },
                {
                    "functional": True,
                    "input": ("db", "code"),
                    "code": "code",
                    "mf_artificial_code": True,
                },
            ]
        },
        ("db", "more"): {
            "database": "me",
            "exchanges": [
                {"functional": True, "code": "foo", "input": ("db", "foo")},
            ],
        },
    }
    assert add_exchange_input_if_missing(given) == expected
    print(caplog.text)
    assert "given 'code' is 'bar' but 'input' code is 'foo'" in caplog.text
