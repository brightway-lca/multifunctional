__all__ = (
    "__version__",
    "allocation_strategies",
    "MaybeMultifunctionalProcess",
    "MultifunctionalDatabase",
    "MultifunctionalProcess",
    "ReadOnlyProcessWithReferenceProduct",
)

__version__ = "0.1.DEV"

from bw2data import labels
from bw2data.subclass_mapping import (
    DATABASE_BACKEND_MAPPING,
    NODE_PROCESS_CLASS_MAPPING,
)

from .database import MultifunctionalDatabase
from .allocation import allocation_strategies
from .node_classes import (
    MaybeMultifunctionalProcess,
    MultifunctionalProcess,
    ReadOnlyProcessWithReferenceProduct,
)
from .node_dispatch import multifunctional_node_dispatcher

DATABASE_BACKEND_MAPPING["multifunctional"] = MultifunctionalDatabase
NODE_PROCESS_CLASS_MAPPING["multifunctional"] = multifunctional_node_dispatcher


if "readonly_process" not in labels.process_node_types:
    labels.process_node_types.append("readonly_process")
