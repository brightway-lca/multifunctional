import bw2data as bd


def test_allocation_with_product_as_process_node(basic):
    # Allocation a second time will pull attributes from the product node
    basic.metadata["default_allocation"] = "price"
    basic.process()
    node = bd.get_node(
        **{
            "name": "process - 1",
            "reference product": "first product - 1",
        }
    )
    node.parent.allocate(products_as_process=True)
    node = bd.get_node(id=node.id)
    assert node["name"] == "first product - 1"


def test_allocation_with_product_as_process_database(basic):
    # Allocation a second time will pull attributes from the product node
    basic.metadata["default_allocation"] = "price"
    basic.process()
    node = bd.get_node(
        **{
            "name": "process - 1",
            "reference product": "first product - 1",
        }
    )
    basic.metadata["simapro_project"] = "1.2.3"
    basic.process()

    node = bd.get_node(id=node.id)
    assert node["name"] == "first product - 1"
