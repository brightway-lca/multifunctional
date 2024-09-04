import bw2data as bd


def test_allocation_labels_applied_price(basic):
    n = bd.get_node(code="1")
    assert "mf_strategy_label" not in n

    basic.metadata["default_allocation"] = "price"
    basic.process()

    n = bd.get_node(code="1")

    for exc in n.production():
        if exc["name"] == "first product - 1":
            assert exc["mf_allocation_factor"] == 0.28
        elif exc["name"] == "second product - 2":
            assert exc["mf_allocation_factor"] == 0.72
    assert n["mf_strategy_label"] == "property allocation by 'price'"


def test_allocation_labels_applied_manual(basic):
    n = bd.get_node(code="1")
    assert "mf_strategy_label" not in n

    basic.metadata["default_allocation"] = "manual_allocation"
    basic.process()

    n = bd.get_node(code="1")

    for exc in n.production():
        if exc["name"] == "first product - 1":
            assert exc["mf_allocation_factor"] == 0.2
        elif exc["name"] == "second product - 2":
            assert exc["mf_allocation_factor"] == 0.8
    assert n["mf_strategy_label"] == "property allocation by 'manual_allocation'"


def test_allocation_labels_applied_equal(basic):
    n = bd.get_node(code="1")
    assert "mf_strategy_label" not in n

    basic.metadata["default_allocation"] = "equal"
    basic.process()

    n = bd.get_node(code="1")

    for exc in n.production():
        if exc["name"] == "first product - 1":
            assert exc["mf_allocation_factor"] == 0.5
        elif exc["name"] == "second product - 2":
            assert exc["mf_allocation_factor"] == 0.5
    assert n["mf_strategy_label"] == "equal_allocation"
