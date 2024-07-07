DATA = {
    ("basic", "a"): {
        "name": "flow - a",
        "code": "a",
        "unit": "kg",
        "type": "emission",
        "categories": ("air",),
    },
    ("basic", "1"): {
        "name": "process - 1",
        "code": "1",
        "location": "first",
        "type": "multifunctional",
        "exchanges": [
            {
                "functional": True,
                "type": "production",
                "desired_code": "my favorite code",
                "name": "first product - 1",
                "unit": "kg",
                "amount": 4,
                "properties": {
                    "price": 7,
                    "mass": 6,
                    "manual": 2,
                },
            },
            {
                "functional": True,
                "type": "production",
                "name": "second product - 1",
                "unit": "megajoule",
                "amount": 6,
                "properties": {
                    "price": 12,
                    "mass": 4,
                    "manual": 8,
                },
            },
            {
                "type": "biosphere",
                "name": "flow - a",
                "amount": 10,
                "input": ("basic", "a"),
            },
        ],
    },
}
