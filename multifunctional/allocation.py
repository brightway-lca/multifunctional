from copy import deepcopy
from functools import partial
from typing import Callable, List
from uuid import uuid4

from bw2io.utils import rescale_exchange
from loguru import logger

from .node_classes import (
    MaybeMultifunctionalProcess,
    ReadOnlyProcessWithReferenceProduct,
)


def generic_allocation(act: MaybeMultifunctionalProcess, func: Callable) -> List[dict]:
    """Allocation by single allocation factor generated by `func`.

    Allocation amount is edge amount times function(edge_data, act) divided by sum of all edge
    amounts times function(edge_data, act).

    Skips functional edges with zero allocation values."""
    if isinstance(act, ReadOnlyProcessWithReferenceProduct):
        return []
    elif not act.has_multiple_functional_edges:
        return []

    total = 0
    for exc in act.functional_edges():
        total += func(exc._data, act)

    new_processes = []
    for exc in act.functional_edges():
        factor = func(exc._data, act) / total
        if not factor:
            continue

        logger.debug(
            "Using allocation factor {f} for functional edge {e} on activity {a}",
            f=factor,
            e=repr(exc),
            a=repr(act),
        )

        try:
            new_code = exc["allocated_product_code"]
        except KeyError:
            new_code = uuid4().hex
            exc["allocated_product_code"] = new_code
            exc.save()
            logger.debug(
                "Creating new product code {c} for functional edge {e} on activity {a}",
                c=new_code,
                e=repr(exc),
                a=repr(act),
            )

        new_process = deepcopy(act._data)
        new_process["multifunctional_parent_id"] = act.id
        new_process["code"] = new_code
        new_process["type"] = "readonly_process"
        new_process["reference product"] = exc["name"]
        new_process["unit"] = exc["unit"]
        new_functional_exchange = deepcopy(exc._data)
        new_functional_exchange["input"] = (act["database"], new_code)
        new_process["exchanges"] = [new_functional_exchange]

        for exc in act.nonfunctional_edges():
            new_process["exchanges"].append(
                rescale_exchange(deepcopy(exc._data), factor)
            )

        new_processes.append(new_process)

    return new_processes


def get_allocation_factor_from_property(
    edge_data: dict, node: MaybeMultifunctionalProcess, property_label: str
) -> float:
    if "properties" not in edge_data:
        raise KeyError(
            f"Edge {edge_data} from process {node} (id {node.id}) doesn't have properties"
        )
    try:
        return edge_data["amount"] * edge_data["properties"][property_label]
    except KeyError as err:
        raise KeyError(
            f"Edge {edge_data} from process {node} (id {node.id}) missing property {property_label}"
        ) from err


def property_allocation(property_label: str) -> Callable:
    return partial(
        generic_allocation,
        func=partial(get_allocation_factor_from_property, property_label=property_label),
    )


allocation_strategies = {
    "price": property_allocation("price"),
    "manual": property_allocation("manual"),
    "mass": property_allocation("mass"),
    "equal": partial(generic_allocation, func=lambda x, y: 1.0),
}
