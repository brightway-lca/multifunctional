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
