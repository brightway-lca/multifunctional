__all__ = (
    "__version__",
    "allocation_strategies",
    "MaybeMultifunctionalProcess",
    "MultifunctionalDatabase",
    "ReadOnlyProcessWithReferenceProduct",
    "property_allocation",
    "allocation_before_writing",
    "generic_allocation",
)

__version__ = "0.4.3"

# Follows guidance from https://loguru.readthedocs.io/en/stable/resources/recipes.html#configuring-loguru-to-be-used-by-a-library-or-an-application
# For development or to get more detail on what is really happening, re-enable with:
# logger.enable("multifunctional")
from loguru import logger

logger.disable("multifunctional")

from bw2data import labels
from bw2data.subclass_mapping import DATABASE_BACKEND_MAPPING, NODE_PROCESS_CLASS_MAPPING

from .allocation import allocation_strategies, generic_allocation, property_allocation
from .database import MultifunctionalDatabase
from .node_classes import MaybeMultifunctionalProcess, ReadOnlyProcessWithReferenceProduct
from .node_dispatch import multifunctional_node_dispatcher
from .utils import allocation_before_writing

DATABASE_BACKEND_MAPPING["multifunctional"] = MultifunctionalDatabase
NODE_PROCESS_CLASS_MAPPING["multifunctional"] = multifunctional_node_dispatcher


if "readonly_process" not in labels.process_node_types:
    labels.process_node_types.append("readonly_process")
