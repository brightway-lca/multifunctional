import bw2data as bd

import multifunctional as mf


def test_internal_linking_results_unchanged(internal):
    dog = bd.get_node(code="🐶")
    assert dog["type"] == "product"
    assert not list(dog.exchanges())

    cat = bd.get_node(code="😼")
    assert cat["type"] == "product"
    assert not list(cat.exchanges())

    flow = bd.get_node(code="a")
    assert flow["type"] == "emission"
    assert not list(flow.exchanges())


def test_internal_linking_results_mf_process_1(internal):
    p = bd.get_node(type="multifunctional", name="process - 1")
    assert p["location"] == "first"
    assert not p.get("unit")
    assert not p.get("reference product")

    assert len(list(p.exchanges())) == 3
    assert len(list(p.production())) == 2
    assert {exc["input"] for exc in p.production()} == {
        ("internal", "first - generated"),
        ("internal", "😼"),
    }


def test_internal_linking_results_mf_process_2(internal):
    p = bd.get_node(type="multifunctional", name="process - 2")
    assert p["location"] == "second"
    assert not p.get("unit")
    assert not p.get("reference product")

    assert len(list(p.exchanges())) == 4
    assert len(list(p.production())) == 2
    assert {exc["input"] for exc in p.production()} == {
        ("internal", "second - generated"),
        ("internal", "🐶"),
    }
    assert {exc["mf_manual_input_product"] for exc in p.production()} == {True, False}
    assert {exc["mf_allocated"] for exc in p.production()} == {True}
    assert {exc.get("mf_artificial_code") for exc in p.production()} == {None}


def test_internal_linking_allocated_dog(internal):
    # Allocation a second time will pull attributes from the product node
    internal.process()
    dog = bd.get_node(
        **{
            "name": "process - 2",
            "reference product": "woof",
        }
    )

    assert dog["location"] == "second"
    assert dog.get("unit") == "kg"
    assert dog["code"] != "2"

    assert len(list(dog.exchanges())) == 3
    assert len(list(dog.production())) == 1
    assert {exc["input"] for exc in dog.production()} == {
        ("internal", "🐶"),
    }
