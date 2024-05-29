__all__ = (
    "__version__",
    "convert_multifunctional_activity",
    "economic_allocation",
    "equal_allocation",
    "handler_mapping",
)

__version__ = "0.1.DEV"

from .utils import convert_multifunctional_activity
from .handlers import economic_allocation, equal_allocation


handler_mapping = {
    "economic": economic_allocation,
    "equal": equal_allocation,
}
