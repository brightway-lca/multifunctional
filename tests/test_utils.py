from multifunctional.utils import prepare_multifunctional_for_writing


def test_prepare_multifunctional_for_writing():
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
    assert prepare_multifunctional_for_writing(given) == expected
