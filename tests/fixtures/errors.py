DATA = {
    ("errors", "a"): {
        "name": "product a",
        "unit": "kg",
        "type": "product",
        "properties": {
            "price": 7.7,
        },
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
    ("errors", "c"): {
        "name": "product c",
        "unit": "kg",
        "type": "product",
        "properties": {
            "price": 7,
            "mass": 8,
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
            {
                "functional": True,
                "type": "production",
                "input": ("errors", "c"),
                "amount": 4,
            },
            {
                "functional": True,
                "type": "production",
                "desired_code": "first one here",
                "name": "first product - 1",
                "unit": "kg",
                "amount": 4,
                "properties": {
                    "price": 7,
                    "mass": True,
                },
            },
            {
                "functional": True,
                "type": "production",
                "desired_code": "second one here",
                "name": "second product - 2",
                "unit": "kg",
                "amount": 4,
                "properties": {
                    "price": 7,
                },
            },
            {
                "type": "biosphere",
                "amount": 12,
                "input": ("errors", "2"),
            },
        ],
    },
    ("errors", "2"): {
        "name": "flow",
        "unit": "kg",
        "type": "emission",
        "categories": ("air",),
    },
    ("errors", "3"): {
        "name": "process - 1",
        "type": "multifunctional",
        "exchanges": [
            {
                "functional": True,
                "type": "production",
                "input": ("errors", "c"),
                "amount": 4,
            },
            {
                "functional": True,
                "type": "production",
                "desired_code": "first one here",
                "name": "first product - 1.1",
                "unit": "kg",
                "amount": 4,
                "properties": {
                    "price": 7,
                    "mass": 9,
                },
            },
            {
                "type": "biosphere",
                "amount": 12,
                "input": ("errors", "2"),
            },
        ],
    },
}
