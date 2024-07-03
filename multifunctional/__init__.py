__all__ = (
    "__version__",
    "economic_allocation",
    "equal_allocation",
    "handler_mapping",
)

__version__ = "0.1.DEV"

from .handlers import economic_allocation, equal_allocation


handler_mapping = {
    "economic": economic_allocation,
    "equal": equal_allocation,
}
