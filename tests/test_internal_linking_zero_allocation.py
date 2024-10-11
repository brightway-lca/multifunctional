from multifunctional.allocation import allocation_strategies


def test_allocation_sets_code_for_zero_allocation_products_in_multifunctional_process():
    given = {
        "exchanges": [
            {
                "name": "🍫",
                "unit": "kg",
                "amount": 1,
                "type": "technosphere",
            },
            {
                "name": "🐑",
                "unit": "kg",
                "waste_type": "not defined",
                "amount": 1.0,
                "allocation": 100.0,
                "type": "production",
                "desired_code": "sheep",
                "functional": True,
                "properties": {"manual_allocation": 100.0},
            },
            {
                "name": "🐣",
                "unit": "kg",
                "desired_code": "cluck",
                "amount": 0.1,
                "allocation": 0.0,
                "type": "production",
                "functional": True,
                "properties": {"manual_allocation": 0.0},
            },
        ],
        "type": "multifunctional",
        "name": "(unknown)",
        "location": None,
        "code": "chicken",
        "database": "db",
    }
    expected = [
        {
            "exchanges": [
                {
                    "name": "🍫",
                    "unit": "kg",
                    "amount": 1,
                    "type": "technosphere",
                },
                {
                    "name": "🐑",
                    "mf_allocation_factor": 1.0,
                    "unit": "kg",
                    "waste_type": "not defined",
                    "amount": 1.0,
                    "allocation": 100.0,
                    "type": "production",
                    "desired_code": "sheep",
                    "functional": True,
                    "properties": {"manual_allocation": 100.0},
                    "input": ("db", "sheep"),
                    "mf_allocated": True,
                    "mf_allocated_process_code": "sheep",
                    "mf_manual_input_product": False,
                },
                {
                    "name": "🐣",
                    "mf_allocation_factor": 0.0,
                    "desired_code": "cluck",
                    "unit": "kg",
                    "amount": 0.1,
                    "allocation": 0.0,
                    "type": "production",
                    "functional": True,
                    "properties": {"manual_allocation": 0.0},
                    "input": ("db", "cluck"),
                    "mf_allocated": True,
                    "mf_allocated_process_code": "cluck",
                    "mf_manual_input_product": False,
                },
            ],
            "type": "multifunctional",
            "mf_strategy_label": "property allocation by 'manual_allocation'",
            "name": "(unknown)",
            "location": None,
            "code": "chicken",
            "database": "db",
        },
        {
            "exchanges": [
                {
                    "name": "🐑",
                    "unit": "kg",
                    "waste_type": "not defined",
                    "amount": 1.0,
                    "allocation": 100.0,
                    "type": "production",
                    "desired_code": "sheep",
                    "functional": True,
                    "properties": {"manual_allocation": 100.0},
                    "input": ("db", "sheep"),
                },
                {
                    "name": "🍫",
                    "unit": "kg",
                    "amount": 1.0,
                    "loc": 1.0,
                    "type": "technosphere",
                },
            ],
            "type": "readonly_process",
            "reference product": "🐑",
            "name": "(unknown)",
            "unit": "kg",
            "production amount": 1.0,
            "mf_strategy_label": "property allocation by 'manual_allocation'",
            "mf_parent_key": ("db", "chicken"),
            "location": None,
            "code": "sheep",
            "database": "db",
        },
        {
            "exchanges": [
                {
                    "name": "🐣",
                    "unit": "kg",
                    "amount": 0.1,
                    "allocation": 0.0,
                    "desired_code": "cluck",
                    "type": "production",
                    "functional": True,
                    "properties": {"manual_allocation": 0.0},
                    "input": ("db", "cluck"),
                },
                {
                    "name": "🍫",
                    "unit": "kg",
                    "amount": 0.0,
                    "loc": 0.0,
                    "uncertainty type": 0,
                    "type": "technosphere",
                },
            ],
            "type": "readonly_process",
            "reference product": "🐣",
            "name": "(unknown)",
            "unit": "kg",
            "production amount": 0.1,
            "mf_strategy_label": "property allocation by 'manual_allocation'",
            "mf_parent_key": ("db", "chicken"),
            "location": None,
            "code": "cluck",
            "database": "db",
        },
    ]
    assert allocation_strategies["manual_allocation"](given) == expected
