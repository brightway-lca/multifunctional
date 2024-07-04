import math

import bw2calc as bc
import bw2data as bd


def test_lcia_scores(basic):
    basic.metadata["default_allocation"] = "price"
    flow = bd.get_node(code="a")
    m = bd.Method(("foo",))
    m.register()
    m.write([(flow.id, 5)])

    basic.process()
    filters = {
        "name": "process - 1",
        "reference product": "first product - 1",
    }
    fu, objs, _ = bd.prepare_lca_inputs(
        demand={bd.get_node(**filters): 1}, method=("foo",)
    )
    lca = bc.LCA(fu, data_objs=objs)
    lca.lci()
    lca.lcia()
    assert math.isclose(lca.score, 4 * 7 / (4 * 7 + 6 * 12) * 10 * 5 / 4, rel_tol=1e-5)

    filters = {
        "name": "process - 1",
        "reference product": "second product - 1",
    }
    fu, objs, _ = bd.prepare_lca_inputs(
        demand={bd.get_node(**filters): 1}, method=("foo",)
    )
    lca = bc.LCA(fu, data_objs=objs)
    lca.lci()
    lca.lcia()
    assert math.isclose(lca.score, 6 * 12 / (4 * 7 + 6 * 12) * 10 * 5 / 6, rel_tol=1e-5)
