__all__ = (
    "__version__",
    "convert_multifunctional_activity",
    "economic_allocation",
    "equal_allocation",
    "handler_mapping",
)

from .version import version as __version__

from .utils import convert_multifunctional_activity
from .handlers import economic_allocation, equal_allocation


handler_mapping = {
    "economic": economic_allocation,
    "equal": equal_allocation,
}
