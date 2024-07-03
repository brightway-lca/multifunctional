import bw2data as bd


def test_basic_allocation(basic):
    basic.metadata["default_allocation"] = "price"
    process = bd.get_node(code="1")
    process.allocate()
    for ds in basic:
        print(ds)
    assert False
