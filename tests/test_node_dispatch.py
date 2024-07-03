import bw2data as bd

import multifunctional as mf


def test_basic_setup(basic):
    flow = bd.get_node(code="a")
    assert isinstance(basic, mf.MultifunctionalDatabase)
    assert isinstance(flow, mf.MaybeMultifunctionalProcess)

    process = bd.get_node(code="1")
    assert isinstance(process, mf.MultifunctionalProcess)
