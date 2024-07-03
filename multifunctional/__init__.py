__all__ = (
    "__version__",
    "economic_allocation",
    "equal_allocation",
    "handler_mapping",
)

from .version import version as __version__

from .handlers import economic_allocation, equal_allocation


handler_mapping = {
    "economic": economic_allocation,
    "equal": equal_allocation,
}
