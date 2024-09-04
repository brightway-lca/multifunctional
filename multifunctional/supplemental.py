import bw2data as bd


def add_product_node_properties_to_exchange(obj: dict) -> dict:
    """Add properties from products to the exchange to make them available during allocation."""
    this = (obj["database"], obj["code"])
    for exc in filter(
        lambda x: x.get("functional") and "input" in x, obj.get("exchanges", [])
    ):
        if exc.get("type") == "production":
            # Keep as separate because it should eventually be an output, not an input...
            other = exc["input"]
        elif exc.get("type") == "technosphere":
            other = exc["input"]
        else:
            other = None

        if other is None or this == other:
            continue

        if not exc.get("properties"):
            exc["properties"] = {}

        exc["__mf__properties_from_product"] = set()

        try:
            other = bd.get_node(database=other[0], code=other[1])
        except bd.errors.UnknownObject:
            continue
        for k, v in other.get("properties", {}).items():
            if k not in exc["properties"]:
                exc["__mf__properties_from_product"].add(k)
                exc["properties"][k] = v

    return obj
