from typing import Optional

from bw2data.backends.proxies import Activity
from bw2data.backends.schema import ActivityDataset

from .node_classes import (
    MaybeMultifunctionalProcess,
    ReadOnlyProcessWithReferenceProduct,
)


def multifunctional_node_dispatcher(node_obj: Optional[ActivityDataset] = None) -> Activity:
    """Dispatch the correct node class depending on node_obj attributes."""
    if node_obj and node_obj.type == "readonly_process":
        return ReadOnlyProcessWithReferenceProduct(document=node_obj)
    else:
        return MaybeMultifunctionalProcess(document=node_obj)
